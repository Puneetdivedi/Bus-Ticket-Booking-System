import { SeatLegend } from "./SeatLegend";
import { SeatLayout } from "./SeatLayout";

export function BookingForm({
  formState,
  reservedSeats,
  editingBooking,
  isSeatMapLoading,
  formError,
  onSeatToggle,
  onFieldChange,
  onReset,
  onSubmit,
  isSubmitting
}) {
  return (
    <section className="panel-surface p-5 sm:p-7">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <div className="inline-flex rounded-full bg-teal-100 px-3 py-1 text-xs font-bold uppercase tracking-[0.2em] text-teal-700">
            Screen 1
          </div>
          <h2 className="mt-3 font-['Trebuchet_MS'] text-3xl font-bold text-slate-900">
            Book or update a passenger block
          </h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
            Select a valid travel date, capture the traveller&apos;s 10-digit mobile number, and lock up to 6 seats in
            a single booking.
          </p>
        </div>

        {editingBooking ? (
          <div className="rounded-3xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
            Editing booking <span className="font-semibold">{editingBooking.booking_id.slice(0, 8)}...</span>
          </div>
        ) : null}
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2">
        <div>
          <label className="field-label" htmlFor="travelDate">
            Travel Date
          </label>
          <input
            id="travelDate"
            type="date"
            value={formState.travelDate}
            onChange={(event) => onFieldChange("travelDate", event.target.value)}
            className="field-input"
          />
        </div>

        <div>
          <label className="field-label" htmlFor="mobileNumber">
            Mobile Number
          </label>
          <input
            id="mobileNumber"
            type="tel"
            value={formState.mobileNumber}
            onChange={(event) => onFieldChange("mobileNumber", event.target.value.replace(/\D/g, "").slice(0, 10))}
            className="field-input"
            inputMode="numeric"
            placeholder="Enter 10-digit number"
          />
        </div>
      </div>

      <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <SeatLegend />
        <div className="flex flex-wrap items-center gap-2 text-xs font-semibold text-slate-500">
          <span className="pill">{formState.selectedSeats.length} selected</span>
          <span className="pill">Maximum 6 seats per mobile per day</span>
          {isSeatMapLoading ? <span className="pill">Refreshing seat map...</span> : null}
        </div>
      </div>

      <div className="mt-6">
        <SeatLayout bookedSeats={reservedSeats} selectedSeats={formState.selectedSeats} onToggleSeat={onSeatToggle} />
      </div>

      <div className="mt-5 flex flex-wrap gap-2">
        {formState.selectedSeats.length ? (
          formState.selectedSeats.map((seat) => (
            <button
              key={seat}
              type="button"
              onClick={() => onSeatToggle(seat)}
              className="rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-700 transition hover:bg-blue-200"
            >
              {seat} x
            </button>
          ))
        ) : (
          <span className="text-sm text-slate-500">Choose one or more seats to continue.</span>
        )}
      </div>

      {formError ? (
        <div className="mt-5 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700">
          {formError}
        </div>
      ) : null}

      <div className="mt-6 flex flex-col gap-3 sm:flex-row">
        <button
          type="button"
          onClick={onSubmit}
          disabled={isSubmitting}
          className="rounded-2xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isSubmitting ? "Saving..." : editingBooking ? "Update Booking" : "Confirm Booking"}
        </button>
        <button
          type="button"
          onClick={onReset}
          className="rounded-2xl border border-slate-300 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:border-slate-400 hover:bg-slate-50"
        >
          {editingBooking ? "Cancel Edit" : "Clear Selection"}
        </button>
      </div>
    </section>
  );
}
