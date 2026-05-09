const TIME_24H_REGEX = /^([01]\d|2[0-3]):([0-5]\d)$/;

export function isValidTime24h(value: string) {
  return TIME_24H_REGEX.test(value.trim());
}

