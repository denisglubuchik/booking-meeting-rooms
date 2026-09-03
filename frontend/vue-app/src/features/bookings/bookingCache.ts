import type { InfiniteData, QueryClient } from "@tanstack/vue-query";
import { queryKeys } from "../../shared/api";
import type { Booking, BookingDetails, Room } from "../../shared/types/api";

type BookingCommandResult = {
  booking: Booking;
  room?: Room;
  includeInMyBookings: boolean;
};

type BookingCommandResults = Record<string, BookingCommandResult>;

function replaceBooking(items: Booking[], booking: Booking) {
  return items.map((item) => (item.id === booking.id ? booking : item));
}

function isNewerThan(booking: Booking, other: Booking) {
  return new Date(booking.updated_at).getTime() > new Date(other.updated_at).getTime();
}

function rememberBookingCommandResult(
  queryClient: QueryClient,
  booking: Booking,
  room?: Room,
  includeInMyBookings = false,
) {
  queryClient.setQueryData<BookingCommandResults>(queryKeys.bookingCommandResults, (current) => {
    const previous = current?.[booking.id];
    return {
      ...current,
      [booking.id]: {
        booking,
        room,
        includeInMyBookings: includeInMyBookings || previous?.includeInMyBookings || false,
      },
    };
  });
}

export function getBookingCommandResult(queryClient: QueryClient, bookingId: string) {
  return queryClient.getQueryData<BookingCommandResults>(queryKeys.bookingCommandResults)?.[bookingId];
}

export function mergeMyBookingsWithCommandResults(
  queryClient: QueryClient,
  bookings: Booking[],
  includeMissing: boolean,
) {
  const commandResults = queryClient.getQueryData<BookingCommandResults>(queryKeys.bookingCommandResults);
  if (!commandResults) return bookings;

  const merged = [...bookings];
  for (const { booking, includeInMyBookings } of Object.values(commandResults)) {
    const index = merged.findIndex((item) => item.id === booking.id);
    if (index >= 0) {
      if (isNewerThan(booking, merged[index])) merged[index] = booking;
    } else if (includeMissing && includeInMyBookings) {
      merged.push(booking);
    }
  }

  return merged.sort(
    (left, right) => new Date(right.start_time).getTime() - new Date(left.start_time).getTime(),
  );
}

export function updateBookingFromCommand(
  queryClient: QueryClient,
  booking: Booking,
  room?: Room,
  includeInMyBookings = false,
) {
  rememberBookingCommandResult(queryClient, booking, room, includeInMyBookings);

  queryClient.setQueriesData<InfiniteData<Booking[], number>>(
    { queryKey: queryKeys.myBookings },
    (current) =>
      current
        ? {
            ...current,
            pages: current.pages.map((page) => replaceBooking(page, booking)),
          }
        : current,
  );

  queryClient.setQueriesData<Booking[]>(
    { queryKey: ["admin-bookings"] },
    (current) => (current ? replaceBooking(current, booking) : current),
  );

  queryClient.setQueryData<BookingDetails>(
    queryKeys.bookingDetails(booking.id),
    (current) =>
      current
        ? {
            ...current,
            booking,
            room: room ?? current.room,
          }
        : current,
  );
}

export function addCreatedBookingToMyBookings(
  queryClient: QueryClient,
  booking: Booking,
) {
  rememberBookingCommandResult(queryClient, booking, undefined, true);

  queryClient.setQueryData<InfiniteData<Booking[], number>>(queryKeys.myBookingsDefault(), (current) => {
    if (!current) return current;

    if (current.pages.some((page) => page.some((item) => item.id === booking.id))) {
      return {
        ...current,
        pages: current.pages.map((page) => replaceBooking(page, booking)),
      };
    }

    const [firstPage = [], ...remainingPages] = current.pages;
    return {
      ...current,
      pages: [[booking, ...firstPage], ...remainingPages],
    };
  });
}
