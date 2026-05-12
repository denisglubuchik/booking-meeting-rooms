import { computed, ref } from "vue";
import { toTypedSchema } from "@vee-validate/zod";
import { useForm } from "vee-validate";
import { useRouter } from "vue-router";
import { z } from "zod";
import { humanizeApiError, register } from "../../shared/api";
import { useAuthStore } from "./store";

export function useRegister() {
  const router = useRouter();
  const auth = useAuthStore();
  const loading = ref(false);
  const error = ref("");
  const success = ref("");

  const schema = toTypedSchema(
    z.object({
      full_name: z.string().trim().min(2, "Введите корректное полное имя."),
      email: z.string().email("Введите корректный email."),
      password: z.string().min(6, "Пароль должен быть не короче 6 символов."),
    }),
  );

  const { defineField, errors, handleSubmit } = useForm({
    validationSchema: schema,
    initialValues: {
      full_name: "",
      email: "",
      password: "",
    },
  });

  const [fullName] = defineField("full_name");
  const [email] = defineField("email");
  const [password] = defineField("password");

  const firstError = computed(() => errors.value.full_name || errors.value.email || errors.value.password || "");

  const onSubmit = handleSubmit(async (values) => {
    loading.value = true;
    error.value = "";
    success.value = "";
    try {
      const normalizedEmail = values.email.trim();
      await register({
        full_name: values.full_name.trim(),
        email: normalizedEmail,
        password: values.password,
      });
      await auth.loginWithPassword(normalizedEmail, values.password);
      await router.push("/");
    } catch (err) {
      error.value = humanizeApiError(err);
    } finally {
      loading.value = false;
    }
  });

  return { fullName, email, password, firstError, loading, error, success, onSubmit };
}
