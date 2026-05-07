export const queryKeys = {
  officesLookup: ["offices-lookup"] as const,
  roomsLookup: ["rooms-lookup"] as const,
  usersLookup: ["users-lookup"] as const,
  bookingDetails: (bookingId: string) => ["booking-details", bookingId] as const,
  userLookup: (query: string) => ["users-lookup", query] as const,
  adminOffices: (filters: Record<string, unknown>) => ["admin-offices", filters] as const,
  adminRooms: (filters: Record<string, unknown>) => ["admin-rooms", filters] as const,
  adminBookings: (filters: Record<string, unknown>) => ["admin-bookings", filters] as const,
  adminUsers: (filters: Record<string, unknown>) => ["admin-users", filters] as const,
};
