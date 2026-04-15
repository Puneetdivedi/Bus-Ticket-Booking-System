import { startTransition, useDeferredValue, useEffect, useState } from "react";
import {
  createBooking,
  downloadBookingsCsv,
  fetchBoardingSequence,
  fetchBookings,
  fetchSeatMap,
  getApiErrorMessage,
  updateBoardingStatus,
  updateBooking
} from "./api/client";
import { BoardingSequencePanel } from "./components/BoardingSequencePanel";
import { BookingForm } from "./components/BookingForm";
import { BookingTable } from "./components/BookingTable";
import { ConfirmationModal } from "./components/ConfirmationModal";
import { formatTravelDate } from "./utils/format";
import { getTodayDateString, isPastDate, sortSeats } from "./utils/seats";

const initialDate = getTodayDateString();

function buildEmptyFormState(travelDate = initialDate) {
  return {
    travelDate,
    mobileNumber: "",
    selectedSeats: []
  };
}

export default function App() {
  const [formState, setFormState] = useState(buildEmptyFormState());
  const [listFilter, setListFilter] = useState({
    travelDate: initialDate,
    mobileSearch: ""
  });
  const [editingBooking, setEditingBooking] = useState(null);
  const [bookedSeats, setBookedSeats] = useState([]);
  const [bookingMetrics, setBookingMetrics] = useState({
    total_bookings: 0,
    total_passengers: 0,
    bookings: []
  });
  const [boardingSequence, setBoardingSequence] = useState([]);
  const [estimatedBoardingTime, setEstimatedBoardingTime] = useState(0);
  const [pageError, setPageError] = useState("");
  const [formError, setFormError] = useState("");
  const [isSeatMapLoading, setIsSeatMapLoading] = useState(false);
  const [isDashboardLoading, setIsDashboardLoading] = useState(true);
  const [isFormSubmitting, setIsFormSubmitting] = useState(false);
  const [togglingBookingId, setTogglingBookingId] = useState("");
  const [confirmationState, setConfirmationState] = useState({
    booking: null,
    mode: "create"
  });

  const deferredMobileSearch = useDeferredValue(listFilter.mobileSearch);

  async function loadSeatMap(travelDate) {
    setIsSeatMapLoading(true);

    try {
      const data = await fetchSeatMap(travelDate);
      setBookedSeats(data.booked_seats);
    } catch (error) {
      setPageError(getApiErrorMessage(error));
    } finally {
      setIsSeatMapLoading(false);
    }
  }

  async function loadDashboard(travelDate, mobileSearch) {
    setIsDashboardLoading(true);

    try {
      const [bookingsResponse, sequenceResponse] = await Promise.all([
        fetchBookings(travelDate, mobileSearch),
        fetchBoardingSequence(travelDate)
      ]);

      setBookingMetrics(bookingsResponse);
      setBoardingSequence(sequenceResponse.bookings);
      setEstimatedBoardingTime(sequenceResponse.estimated_total_time_seconds);
      setPageError("");
    } catch (error) {
      setPageError(getApiErrorMessage(error));
    } finally {
      setIsDashboardLoading(false);
    }
  }

  useEffect(() => {
    loadSeatMap(formState.travelDate);
  }, [formState.travelDate]);

  useEffect(() => {
    loadDashboard(listFilter.travelDate, deferredMobileSearch);
  }, [listFilter.travelDate, deferredMobileSearch]);

  useEffect(() => {
    const seatsReservedByOthers = bookedSeats.filter((seat) => {
      const isEditableSeat =
        editingBooking &&
        editingBooking.travel_date === formState.travelDate &&
        editingBooking.seats.includes(seat);

      return !isEditableSeat;
    });

    setFormState((currentState) => {
      const nextSeats = currentState.selectedSeats.filter((seat) => !seatsReservedByOthers.includes(seat));

      if (nextSeats.length === currentState.selectedSeats.length) {
        return currentState;
      }

      return { ...currentState, selectedSeats: nextSeats };
    });
  }, [bookedSeats, editingBooking, formState.travelDate]);

  function resetForm(nextTravelDate = formState.travelDate) {
    setEditingBooking(null);
    setFormError("");
    setFormState(buildEmptyFormState(nextTravelDate));
  }

  function handleFieldChange(field, value) {
    setFormError("");
    setPageError("");
    setFormState((currentState) => ({
      ...currentState,
      [field]: value
    }));
  }

  function handleSeatToggle(seat) {
    setFormError("");

    const seatsReservedByOthers = bookedSeats.filter((bookedSeat) => {
      const isEditableSeat =
        editingBooking &&
        editingBooking.travel_date === formState.travelDate &&
        editingBooking.seats.includes(bookedSeat);

      return !isEditableSeat;
    });

    if (seatsReservedByOthers.includes(seat)) {
      return;
    }

    setFormState((currentState) => {
      if (currentState.selectedSeats.includes(seat)) {
        return {
          ...currentState,
          selectedSeats: currentState.selectedSeats.filter((selectedSeat) => selectedSeat !== seat)
        };
      }

      if (currentState.selectedSeats.length >= 6) {
        setFormError("A single booking cannot contain more than 6 seats.");
        return currentState;
      }

      return {
        ...currentState,
        selectedSeats: sortSeats([...currentState.selectedSeats, seat])
      };
    });
  }

  function validateForm() {
    if (!formState.travelDate || isPastDate(formState.travelDate)) {
      return "Please choose today or a future travel date.";
    }

    if (!/^\d{10}$/.test(formState.mobileNumber)) {
      return "Mobile number must contain exactly 10 digits.";
    }

    if (!formState.selectedSeats.length) {
      return "Select at least one seat before saving the booking.";
    }

    return "";
  }

  async function handleSubmitBooking() {
    const validationMessage = validateForm();
    if (validationMessage) {
      setFormError(validationMessage);
      return;
    }

    setIsFormSubmitting(true);
    setFormError("");
    setPageError("");

    const payload = {
      travel_date: formState.travelDate,
      mobile_number: formState.mobileNumber,
      seats: formState.selectedSeats
    };

    try {
      const savedBooking = editingBooking
        ? await updateBooking(editingBooking.booking_id, payload)
        : await createBooking(payload);

      setConfirmationState({
        booking: savedBooking,
        mode: editingBooking ? "update" : "create"
      });

      await Promise.all([
        loadSeatMap(formState.travelDate),
        loadDashboard(listFilter.travelDate, deferredMobileSearch)
      ]);

      resetForm(savedBooking.travel_date);
    } catch (error) {
      setFormError(getApiErrorMessage(error));
    } finally {
      setIsFormSubmitting(false);
    }
  }

  function handleEdit(booking) {
    startTransition(() => {
      setEditingBooking(booking);
      setFormState({
        travelDate: booking.travel_date,
        mobileNumber: booking.mobile_number,
        selectedSeats: booking.seats
      });
      setFormError("");
      setPageError("");
    });

    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function handleToggleBoarding(booking) {
    setTogglingBookingId(booking.booking_id);
    setPageError("");

    try {
      await updateBoardingStatus(booking.booking_id, !booking.is_boarded);
      await loadDashboard(listFilter.travelDate, deferredMobileSearch);
    } catch (error) {
      setPageError(getApiErrorMessage(error));
    } finally {
      setTogglingBookingId("");
    }
  }

  async function handleExportCsv() {
    try {
      const blob = await downloadBookingsCsv(listFilter.travelDate);
      const url = window.URL.createObjectURL(new Blob([blob]));
      const link = document.createElement("a");
      link.href = url;
      link.download = `bookings-${listFilter.travelDate}.csv`;
      link.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      setPageError(getApiErrorMessage(error));
    }
  }

  const seatsReservedByOthers = bookedSeats.filter((seat) => {
    const isEditableSeat =
      editingBooking && editingBooking.travel_date === formState.travelDate && editingBooking.seats.includes(seat);

    return !isEditableSeat;
  });

  return (
    <>
      <div className="min-h-screen bg-dots bg-[length:18px_18px]">
        <div className="mx-auto flex min-h-screen w-full max-w-7xl flex-col px-4 py-6 sm:px-6 lg:px-8">
          <header className="overflow-hidden rounded-[34px] bg-slate-900 px-6 py-8 text-white shadow-panel sm:px-8 lg:px-10">
            <div className="grid gap-6 lg:grid-cols-[1.6fr_0.8fr] lg:items-end">
              <div>
                <div className="inline-flex rounded-full bg-white/10 px-4 py-1 text-xs font-bold uppercase tracking-[0.24em] text-slate-200">
                  Bus Conductor Console
                </div>
                <h1 className="mt-4 max-w-3xl font-['Trebuchet_MS'] text-4xl font-bold leading-tight sm:text-5xl">
                  Bus Ticket Booking System with live seat control and optimal boarding order
                </h1>
                <p className="mt-4 max-w-2xl text-sm leading-6 text-slate-300 sm:text-base">
                  Manage bookings, prevent conflicts, and board passengers in the fastest possible row sequence from a
                  single responsive dashboard.
                </p>
              </div>

              <div className="grid gap-4 sm:grid-cols-3 lg:grid-cols-1">
                <div className="rounded-[26px] bg-white/10 p-5 backdrop-blur">
                  <div className="text-xs uppercase tracking-[0.2em] text-slate-300">Travel date</div>
                  <div className="mt-2 text-2xl font-bold">{formatTravelDate(listFilter.travelDate)}</div>
                </div>
                <div className="rounded-[26px] bg-white/10 p-5 backdrop-blur">
                  <div className="text-xs uppercase tracking-[0.2em] text-slate-300">Bookings</div>
                  <div className="mt-2 text-2xl font-bold">{bookingMetrics.total_bookings}</div>
                </div>
                <div className="rounded-[26px] bg-white/10 p-5 backdrop-blur">
                  <div className="text-xs uppercase tracking-[0.2em] text-slate-300">Passengers</div>
                  <div className="mt-2 text-2xl font-bold">{bookingMetrics.total_passengers}</div>
                </div>
              </div>
            </div>
          </header>

          {pageError ? (
            <div className="mt-6 rounded-[24px] border border-rose-200 bg-rose-50 px-5 py-4 text-sm font-medium text-rose-700">
              {pageError}
            </div>
          ) : null}

          <main className="mt-6 grid gap-6">
            <BookingForm
              formState={formState}
              reservedSeats={seatsReservedByOthers}
              editingBooking={editingBooking}
              isSeatMapLoading={isSeatMapLoading}
              formError={formError}
              onSeatToggle={handleSeatToggle}
              onFieldChange={handleFieldChange}
              onReset={() => resetForm(formState.travelDate)}
              onSubmit={handleSubmitBooking}
              isSubmitting={isFormSubmitting}
            />

            <section className="panel-surface p-5 sm:p-7">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
                <div>
                  <h2 className="font-['Trebuchet_MS'] text-2xl font-bold text-slate-900">
                    Daily operations filter
                  </h2>
                  <p className="mt-2 text-sm text-slate-600">
                    Filter the booking table by travel date and optionally search passengers by mobile number.
                  </p>
                </div>

                <div className="grid gap-4 md:grid-cols-3">
                  <div>
                    <label className="field-label" htmlFor="filterDate">
                      Travel Date
                    </label>
                    <input
                      id="filterDate"
                      type="date"
                      value={listFilter.travelDate}
                      onChange={(event) =>
                        setListFilter((currentState) => ({
                          ...currentState,
                          travelDate: event.target.value
                        }))
                      }
                      className="field-input"
                    />
                  </div>

                  <div>
                    <label className="field-label" htmlFor="mobileSearch">
                      Search Mobile
                    </label>
                    <input
                      id="mobileSearch"
                      type="search"
                      value={listFilter.mobileSearch}
                      onChange={(event) =>
                        setListFilter((currentState) => ({
                          ...currentState,
                          mobileSearch: event.target.value.replace(/\D/g, "").slice(0, 10)
                        }))
                      }
                      className="field-input"
                      placeholder="Optional mobile number"
                    />
                  </div>

                  <div className="flex items-end">
                    <button
                      type="button"
                      onClick={handleExportCsv}
                      className="w-full rounded-2xl bg-teal-700 px-5 py-3 text-sm font-semibold text-white transition hover:bg-teal-800"
                    >
                      Export CSV
                    </button>
                  </div>
                </div>
              </div>
            </section>

            <BoardingSequencePanel
              sequence={boardingSequence}
              estimatedTime={estimatedBoardingTime}
              isLoading={isDashboardLoading}
            />

            <BookingTable
              bookings={bookingMetrics.bookings}
              filterDate={listFilter.travelDate}
              isLoading={isDashboardLoading}
              togglingId={togglingBookingId}
              onToggleBoarding={handleToggleBoarding}
              onEdit={handleEdit}
            />
          </main>
        </div>
      </div>

      <ConfirmationModal
        booking={confirmationState.booking}
        mode={confirmationState.mode}
        onClose={() => setConfirmationState({ booking: null, mode: "create" })}
      />
    </>
  );
}
