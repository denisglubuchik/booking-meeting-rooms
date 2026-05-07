import type { components } from "../api/schema";

export type Role = "employee" | "admin";
export type BookingStatus = components["schemas"]["BookingStatus"];

export type Office = components["schemas"]["OfficeResponse"];
export type Room = components["schemas"]["RoomResponse"];
export type Booking = components["schemas"]["BookingResponse"];
export type User = Omit<components["schemas"]["UserResponse"], "role"> & { role: Role };
