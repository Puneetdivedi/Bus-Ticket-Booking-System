export function formatTravelDate(value) {
  if (!value) {
    return "N/A";
  }

  return new Intl.DateTimeFormat("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric"
  }).format(new Date(`${value}T00:00:00`));
}

export function shortenBookingId(bookingId) {
  return `${bookingId.slice(0, 8)}...`;
}
