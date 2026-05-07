import { defineStore } from "pinia";
import type { Role, User } from "../../shared/types/api";
import { login, me, setApiToken } from "../../shared/api";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    isAuthenticated: Boolean(localStorage.getItem("booking_token")),
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
        const user = await me();
        this.applyUser(user);
      } catch {
        this.logout();
      }
    },
    applyUser(user: User) {
      this.isAuthenticated = true;
      this.role = user.role;
      this.fullName = user.full_name;
      this.email = user.email;
    },
    async loginWithPassword(email: string, password: string) {
      this.loading = true;
      this.error = "";
      try {
        const auth = await login(email, password);
        setApiToken(auth.access_token);
        const user = await me();
        this.applyUser(user);
      } catch (err) {
        this.error = err instanceof Error ? err.message : "Ошибка входа";
        throw err;
      } finally {
        this.loading = false;
      }
    },
    logout() {
      setApiToken("");
      this.isAuthenticated = false;
      this.role = "employee";
      this.fullName = "";
      this.email = "";
    },
  },
});
