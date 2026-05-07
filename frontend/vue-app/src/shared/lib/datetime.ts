import dayjs from "dayjs";

export function formatDateRu(value: string) {
  return dayjs(value).format("DD.MM.YYYY");
}

export function formatTimeRu(value: string) {
  return dayjs(value).format("HH:mm");
}

export function formatDateTimeRu(value: string) {
  return dayjs(value).format("DD.MM.YYYY HH:mm");
}

export function isSameDay(left: string, right: Date) {
  return dayjs(left).isSame(dayjs(right), "day");
}
