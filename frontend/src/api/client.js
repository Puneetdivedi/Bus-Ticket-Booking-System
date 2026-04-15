import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  headers: {
    "Content-Type": "application/json"
  }
});

export function getApiErrorMessage(error) {
  if (typeof error.response?.data?.detail === "string") {
    return error.response.data.detail;
  }

  if (Array.isArray(error.response?.data?.detail)) {
    return error.response.data.detail.map((item) => item.msg).join(", ");
  }

  return error.message || "Something went wrong while talking to the server.";
}

export async function fetchSeatMap(travelDate) {
  const { data } = await api.get("/api/bookings/seat-map", {
    params: { travel_date: travelDate }
  });
  return data;
}

export async function fetchBookings(travelDate, mobileNumber = "") {
  const { data } = await api.get("/api/bookings", {
    params: {
      travel_date: travelDate,
      ...(mobileNumber ? { mobile_number: mobileNumber } : {})
    }
  });
  return data;
}

export async function fetchBoardingSequence(travelDate) {
  const { data } = await api.get("/api/bookings/boarding-sequence", {
    params: { travel_date: travelDate }
  });
  return data;
}

export async function createBooking(payload) {
  const { data } = await api.post("/api/bookings", payload);
  return data;
}

export async function updateBooking(bookingId, payload) {
  const { data } = await api.put(`/api/bookings/${bookingId}`, payload);
  return data;
}

export async function updateBoardingStatus(bookingId, isBoarded) {
  const { data } = await api.patch(`/api/bookings/${bookingId}/boarding`, {
    is_boarded: isBoarded
  });
  return data;
}

export async function downloadBookingsCsv(travelDate) {
  const response = await api.get("/api/bookings/export/csv", {
    params: { travel_date: travelDate },
    responseType: "blob"
  });
  return response.data;
}
