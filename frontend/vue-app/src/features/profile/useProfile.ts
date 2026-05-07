import { computed, watchEffect } from "vue";
import { toTypedSchema } from "@vee-validate/zod";
import { useMutation, useQuery } from "@tanstack/vue-query";
import { useForm } from "vee-validate";
import { z } from "zod";
import { me, updateMe, humanizeApiError } from "../../shared/api";
import { useAuthStore } from "../auth/store";
import { useToast } from "../ui/toast";

export function useProfile() {
  const auth = useAuthStore();
  const toast = useToast();

  const schema = toTypedSchema(
    z.object({
      full_name: z.string().trim().min(2, "Введите корректное полное имя."),
      email: z.string().email("Введите корректный email."),
    }),
  );

  const { defineField, errors, handleSubmit, setValues } = useForm({
    validationSchema: schema,
    initialValues: {
      full_name: "",
      email: "",
    },
  });

  const [fullName] = defineField("full_name");
  const [email] = defineField("email");

  const meQuery = useQuery({
    queryKey: ["profile-me"],
    queryFn: () => me(),
  });

  const user = computed(() => meQuery.data.value ?? null);
  const isLoading = computed(() => meQuery.isLoading.value || meQuery.isFetching.value);
  const errorText = computed(() =>
    meQuery.error.value ? humanizeApiError(meQuery.error.value) : "",
  );
  const firstError = computed(() => errors.value.full_name || errors.value.email || "");

  watchEffect(() => {
    if (!user.value) return;
    setValues({ full_name: user.value.full_name, email: user.value.email });
  });

  const userRoleLabel = computed(() => (user.value?.role === "admin" ? "админ" : "сотрудник"));

  const updateMutation = useMutation({
    mutationFn: (values: { full_name: string; email: string }) =>
      updateMe({
        full_name: values.full_name.trim(),
        email: values.email.trim(),
      }),
    onSuccess: (updated) => {
      auth.applyUser(updated);
      meQuery.refetch();
      toast.success("Профиль обновлен.");
    },
    onError: (err) => {
      toast.error(humanizeApiError(err));
    },
  });

  const onSubmit = handleSubmit((values) => {
    updateMutation.mutate(values);
  });

  return {
    user,
    isLoading,
    errorText,
    userRoleLabel,
    fullName,
    email,
    firstError,
    updateMutation,
    onSubmit,
  };
}
