export const en = {
  common: {
    unknownError: "Unknown error",
  },
  api: {
    fallback: {
      invalidFields: "Please check the filled fields.",
      unauthorized: "Session expired or invalid credentials.",
      forbidden: "You do not have permission for this action.",
      notFound: "Resource not found.",
      serverError: "Internal server error.",
      requestFailed: "Request failed ({status}).",
    },
    errors: {
      not_found: "Resource not found.",
      forbidden: "You do not have permission for this action.",
      bad_request: "Bad request.",
      invalid_credentials: "Invalid email or password.",
      booking_time_in_past: "Booking in the past is not allowed.",
      booking_horizon_exceeded: "Booking date is too far in the future.",
      room_unavailable: "Room is unavailable for selected time.",
      invalid_time_range: "Invalid time range.",
      invalid_booking_state: "Operation is not available for current booking status.",
      permission_denied: "You do not have permission for this action.",
      application_error: "Application error.",
      domain_error: "Business logic error.",
      "auth.missing_bearer_token": "Authorization is required.",
      "auth.invalid_access_token": "Session expired. Please sign in again.",
      "auth.user_deactivated": "User is deactivated.",
      "auth.admin_access_required": "Admin access is required.",
      "validation.request_invalid": "Please check the filled fields.",
    },
  },
} as const;
