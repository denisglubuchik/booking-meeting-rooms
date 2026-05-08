import type { components } from "../api/schema";

export type Role = "employee" | "admin";
export type BookingStatus = components["schemas"]["BookingStatus"];

export type Office = components["schemas"]["OfficeResponse"];
export type Room = components["schemas"]["RoomResponse"];
export type Booking = components["schemas"]["BookingResponse"];
export type BookingDetails = components["schemas"]["BookingDetailsResponse"];
export type BookingParticipant = components["schemas"]["BookingParticipantResponse"];
export type BookingParticipantDetails = components["schemas"]["BookingParticipantDetailsResponse"];
export type UserLookup = components["schemas"]["UserLookupResponse"];
export type User = Omit<components["schemas"]["UserResponse"], "role"> & { role: Role };

export type OperationWarning = {
  code: string;
  severity: string;
  message: string;
};

export type AddBookingParticipantResult = {
  participant: BookingParticipant;
  warnings: OperationWarning[];
};
