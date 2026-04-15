import { formatTravelDate } from "../utils/format";

export function ConfirmationModal({ booking, mode, onClose }) {
  if (!booking) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/45 px-4">
      <div className="w-full max-w-lg rounded-[30px] bg-white p-6 shadow-2xl sm:p-8">
        <div className="mb-5 inline-flex rounded-full bg-emerald-100 px-4 py-1 text-sm font-semibold text-emerald-700">
          {mode === "update" ? "Booking updated" : "Booking confirmed"}
        </div>

        <h2 className="font-['Trebuchet_MS'] text-2xl font-bold text-slate-900">
          Passenger details are locked in
        </h2>
        <p className="mt-2 text-sm text-slate-600">
          Share the booking ID with the traveller before boarding begins.
        </p>

        <div className="mt-6 grid gap-4 rounded-[24px] bg-slate-50 p-5 text-sm text-slate-700">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Booking ID</div>
            <div className="mt-1 break-all font-semibold text-slate-900">{booking.booking_id}</div>
          </div>
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Travel date</div>
            <div className="mt-1 font-semibold text-slate-900">{formatTravelDate(booking.travel_date)}</div>
          </div>
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Mobile number</div>
            <div className="mt-1 font-semibold text-slate-900">{booking.mobile_number}</div>
          </div>
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Selected seats</div>
            <div className="mt-2 flex flex-wrap gap-2">
              {booking.seats.map((seat) => (
                <span key={seat} className="pill">
                  {seat}
                </span>
              ))}
            </div>
          </div>
        </div>

        <button
          type="button"
          onClick={onClose}
          className="mt-6 w-full rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
        >
          Close
        </button>
      </div>
    </div>
  );
}
