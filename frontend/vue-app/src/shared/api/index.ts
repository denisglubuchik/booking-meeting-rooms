export { ApiError, humanizeApiError, setApiToken } from "./client";

export { login, register, me, updateMe } from "./auth";
export {
  getOffices,
  getOfficeById,
  createOffice,
  updateOffice,
  activateOffice,
  deactivateOffice,
  setOfficeImage,
  deleteOfficeImage,
} from "./offices";
export {
  getRooms,
  getRoomsByOffice,
  getRoomById,
  createRoom,
  updateRoom,
  activateRoom,
  deactivateRoom,
  setRoomImage,
  deleteRoomImage,
} from "./rooms";
export {
  getAvailableRooms,
  getRoomBookings,
  getMyBookings,
  getAllBookings,
  createBooking,
  cancelBooking,
  rescheduleBooking,
  changeBookingRoom,
} from "./bookings";
export { getUsers, activateUser, deactivateUser, promoteToAdmin, demoteToEmployee } from "./users";
export { queryKeys } from "./queryKeys";
