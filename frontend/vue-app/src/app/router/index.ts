import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../../features/auth/store";
import DashboardPage from "../../pages/dashboard/index.vue";
import LoginPage from "../../pages/login/index.vue";
import RegisterPage from "../../pages/register/index.vue";
import OfficesPage from "../../pages/offices/index.vue";
import RoomsPage from "../../pages/rooms/index.vue";
import FindRoomPage from "../../pages/find-room/index.vue";
import RoomDetailsPage from "../../pages/room-details/index.vue";
import CreateBookingPage from "../../pages/create-booking/index.vue";
import BookingDetailsPage from "../../pages/booking-details/index.vue";
import MyBookingsPage from "../../pages/my-bookings/index.vue";
import ProfilePage from "../../pages/profile/index.vue";
import AdminOfficesPage from "../../pages/admin-offices/index.vue";
import AdminRoomsPage from "../../pages/admin-rooms/index.vue";
import AdminBookingsPage from "../../pages/admin-bookings/index.vue";
import AdminBookingHistoryPage from "../../pages/admin-booking-history/index.vue";
import AdminUsersPage from "../../pages/admin-users/index.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/login", component: LoginPage, meta: { public: true } },
    { path: "/register", component: RegisterPage, meta: { public: true } },
    { path: "/", component: DashboardPage },
    { path: "/offices", component: OfficesPage },
    { path: "/rooms", component: RoomsPage },
    { path: "/find-room", component: FindRoomPage },
    { path: "/rooms/:id", component: RoomDetailsPage },
    { path: "/bookings/new", component: CreateBookingPage },
    { path: "/bookings/:id", component: BookingDetailsPage },
    { path: "/my-bookings", component: MyBookingsPage },
    { path: "/profile", component: ProfilePage },
    { path: "/admin/offices", component: AdminOfficesPage, meta: { admin: true } },
    { path: "/admin/rooms", component: AdminRoomsPage, meta: { admin: true } },
    { path: "/admin/bookings", component: AdminBookingsPage, meta: { admin: true } },
    { path: "/admin/booking-history", component: AdminBookingHistoryPage, meta: { admin: true } },
    { path: "/admin/users", component: AdminUsersPage, meta: { admin: true } },
    {
      path: "/:pathMatch(.*)*",
      redirect: () => (useAuthStore().isAuthenticated ? "/" : "/login"),
    },
  ],
});

router.beforeEach((to) => {
  const auth = useAuthStore();
  if (!to.meta.public && !auth.isAuthenticated) return "/login";
  if (to.meta.public && auth.isAuthenticated) return "/";
  if (to.meta.admin && auth.role !== "admin") return "/";
  return true;
});

export default router;
