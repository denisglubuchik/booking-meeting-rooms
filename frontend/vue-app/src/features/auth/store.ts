import { defineStore } from "pinia";
import type { Role, User } from "../../shared/types/api";
import { clearAuthTokens, login, logout, me, setAuthTokens } from "../../shared/api";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    isAuthenticated: Boolean(localStorage.getItem("booking_token")),
    id: "",
    role: "employee" as Role,
    fullName: "",
    email: "",
    loading: false,
    error: "",
  }),
  actions: {
    async hydrate() {
      if (!this.isAuthenticated) return;
      try {
        const user = await me(true);
        this.applyUser(user);
      } catch {
        this.logout();
      }
    },
    applyUser(user: User) {
      this.isAuthenticated = true;
      this.id = user.id;
      this.role = user.role;
      this.fullName = user.full_name;
      this.email = user.email;
    },
    async loginWithPassword(email: string, password: string) {
      this.loading = true;
      this.error = "";
      try {
        const auth = await login(email, password);
        setAuthTokens(auth.access_token);
        const user = await me(true);
        this.applyUser(user);
      } catch (err) {
        this.error = err instanceof Error ? err.message : "Ошибка входа";
        throw err;
      } finally {
        this.loading = false;
      }
    },
    logout() {
      void logout().catch(() => undefined);
      clearAuthTokens();
      this.isAuthenticated = false;
      this.id = "";
      this.role = "employee";
      this.fullName = "";
      this.email = "";
    },
  },
});
