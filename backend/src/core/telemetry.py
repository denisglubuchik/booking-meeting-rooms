from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

from opentelemetry import metrics, trace
from opentelemetry._logs import set_logger_provider  # noqa: PLC2701
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import (  # noqa: PLC2701
    OTLPLogExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.instrumentation.logging.handler import LoggingHandler
from opentelemetry.sdk._logs import LoggerProvider  # noqa: PLC2701
from opentelemetry.sdk._logs.export import (  # noqa: PLC2701
    BatchLogRecordProcessor,
    ConsoleLogRecordExporter,
    LogRecordExporter,
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    MetricExporter,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SpanExporter,
)

if TYPE_CHECKING:
    from core.config import TelemetryConfig

ExporterName = Literal["console", "otlp", "none"]


@dataclass(slots=True)
class TelemetryRuntime:
    service_name: str
    tracer_provider: TracerProvider | None = None
    meter_provider: MeterProvider | None = None
    logger_provider: LoggerProvider | None = None
    logging_handler: logging.Handler | None = None
    _shutdown: bool = field(default=False, init=False, repr=False)

    @property
    def enabled(self) -> bool:
        return any(
            provider is not None
            for provider in (
                self.tracer_provider,
                self.meter_provider,
                self.logger_provider,
            )
        )

    def force_flush(self, timeout_millis: int = 30_000) -> bool:
        deadline_ns = time.monotonic_ns() + timeout_millis * 1_000_000
        providers = (
            self.logger_provider,
            self.meter_provider,
            self.tracer_provider,
        )

        for provider in providers:
            if provider is None:
                continue
            remaining_millis = (
                deadline_ns - time.monotonic_ns()
            ) // 1_000_000
            if remaining_millis <= 0:
                return False
            if not provider.force_flush(timeout_millis=remaining_millis):
                return False
        return True

    def shutdown(self) -> None:
        if self._shutdown:
            return
        self._shutdown = True

        if self.logging_handler is not None:
            self.logging_handler.close()
        if self.logger_provider is not None:
            self.logger_provider.shutdown()
        if self.meter_provider is not None:
            self.meter_provider.shutdown()
        if self.tracer_provider is not None:
            self.tracer_provider.shutdown()


def setup_telemetry(
    *,
    service_name: str,
    service_version: str,
    config: TelemetryConfig,
) -> TelemetryRuntime:
    if config.OTEL_SDK_DISABLED or _all_exporters_disabled(config):
        return TelemetryRuntime(service_name=service_name)

    resource = Resource.create(
        {
            "service.name": service_name,
            "service.version": service_version,
        },
    )
    meter_provider = _setup_metrics(config, resource)
    tracer_provider = _setup_traces(config, resource)
    logger_provider, logging_handler = _setup_logs(config, resource)

    if meter_provider is not None:
        metrics.set_meter_provider(meter_provider)
    if tracer_provider is not None:
        trace.set_tracer_provider(tracer_provider)
    if logger_provider is not None:
        set_logger_provider(logger_provider)

    return TelemetryRuntime(
        service_name=service_name,
        tracer_provider=tracer_provider,
        meter_provider=meter_provider,
        logger_provider=logger_provider,
        logging_handler=logging_handler,
    )


def _all_exporters_disabled(config: TelemetryConfig) -> bool:
    return all(
        exporter == "none"
        for exporter in (
            config.OTEL_TRACES_EXPORTER,
            config.OTEL_METRICS_EXPORTER,
            config.OTEL_LOGS_EXPORTER,
        )
    )


def _setup_traces(
    config: TelemetryConfig,
    resource: Resource,
) -> TracerProvider | None:
    exporter = _make_span_exporter(config.OTEL_TRACES_EXPORTER)
    if exporter is None:
        return None

    provider = TracerProvider(resource=resource, shutdown_on_exit=False)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    return provider


def _setup_metrics(
    config: TelemetryConfig,
    resource: Resource,
) -> MeterProvider | None:
    exporter = _make_metric_exporter(config.OTEL_METRICS_EXPORTER)
    if exporter is None:
        return None

    reader = PeriodicExportingMetricReader(
        exporter,
        export_interval_millis=config.OTEL_METRIC_EXPORT_INTERVAL,
    )
    return MeterProvider(
        metric_readers=(reader,),
        resource=resource,
        shutdown_on_exit=False,
    )


def _setup_logs(
    config: TelemetryConfig,
    resource: Resource,
) -> tuple[LoggerProvider | None, logging.Handler | None]:
    exporter = _make_log_exporter(config.OTEL_LOGS_EXPORTER)
    if exporter is None:
        return None, None

    provider = LoggerProvider(resource=resource, shutdown_on_exit=False)
    provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
    handler = LoggingHandler(
        level=logging.NOTSET,
        logger_provider=provider,
    )
    return provider, handler


def _make_span_exporter(name: ExporterName) -> SpanExporter | None:
    if name == "console":
        return ConsoleSpanExporter()
    if name == "otlp":
        return OTLPSpanExporter()
    return None


def _make_metric_exporter(name: ExporterName) -> MetricExporter | None:
    if name == "console":
        return ConsoleMetricExporter()
    if name == "otlp":
        return OTLPMetricExporter()
    return None


def _make_log_exporter(name: ExporterName) -> LogRecordExporter | None:
    if name == "console":
        return ConsoleLogRecordExporter()
    if name == "otlp":
        return OTLPLogExporter()
    return None
