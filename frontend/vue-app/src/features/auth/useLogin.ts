import { computed } from "vue";
import { toTypedSchema } from "@vee-validate/zod";
import { useForm } from "vee-validate";
import { useRouter } from "vue-router";
import { z } from "zod";
import { useAuthStore } from "./store";

export function useLogin() {
  const router = useRouter();
  const auth = useAuthStore();

  const schema = toTypedSchema(
    z.object({
      email: z.string().email("Введите корректный email."),
      password: z.string().min(1, "Введите пароль."),
    }),
  );

  const { defineField, errors, handleSubmit } = useForm({
    validationSchema: schema,
    initialValues: {
      email: "",
      password: "",
    },
  });

  const [email] = defineField("email");
  const [password] = defineField("password");
  const firstError = computed(() => errors.value.email || errors.value.password || "");

  const onSubmit = handleSubmit(async (values) => {
    try {
      await auth.loginWithPassword(values.email, values.password);
      await router.push("/");
    } catch {
      // handled in store
    }
  });

  return { auth, email, password, firstError, onSubmit };
}
