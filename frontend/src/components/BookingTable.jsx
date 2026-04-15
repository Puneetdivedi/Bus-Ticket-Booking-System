import { formatTravelDate, shortenBookingId } from "../utils/format";

function PhoneIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4 fill-current" aria-hidden="true">
      <path d="M6.6 10.8a15.3 15.3 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.24c1.08.36 2.23.54 3.42.54a1 1 0 0 1 1 1V21a1 1 0 0 1-1 1C10.4 22 2 13.6 2 3a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.18.18 2.34.54 3.42a1 1 0 0 1-.24 1l-2.2 2.38Z" />
    </svg>
  );
}

export function BookingTable({ bookings, filterDate, isLoading, togglingId, onToggleBoarding, onEdit }) {
  return (
    <section className="panel-surface p-5 sm:p-7">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <div className="inline-flex rounded-full bg-coral/15 px-3 py-1 text-xs font-bold uppercase tracking-[0.2em] text-coral">
            Screen 2
          </div>
          <h2 className="mt-3 font-['Trebuchet_MS'] text-3xl font-bold text-slate-900">
            Booking list and boarding control
          </h2>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Sequence order is highlighted from farthest row to nearest row for {formatTravelDate(filterDate)}.
          </p>
        </div>
      </div>

      <div className="mt-6 overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
          <thead>
            <tr className="text-xs uppercase tracking-[0.18em] text-slate-400">
              <th className="pb-3 pr-4 font-semibold">Seq</th>
              <th className="pb-3 pr-4 font-semibold">Booking ID</th>
              <th className="pb-3 pr-4 font-semibold">Seats</th>
              <th className="pb-3 pr-4 font-semibold">Mobile</th>
              <th className="pb-3 pr-4 font-semibold">Boarding</th>
              <th className="pb-3 pr-0 font-semibold">Edit</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {isLoading ? (
              <tr>
                <td colSpan="6" className="py-10 text-center text-slate-500">
                  Loading bookings...
                </td>
              </tr>
            ) : bookings.length ? (
              bookings.map((booking) => (
                <tr key={booking.booking_id} className={booking.is_boarded ? "bg-emerald-50/60" : "bg-white"}>
                  <td className="py-4 pr-4 align-top">
                    <span className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-slate-900 text-xs font-bold text-white">
                      {booking.sequence_number}
                    </span>
                  </td>
                  <td className="py-4 pr-4 align-top">
                    <div className="font-semibold text-slate-900" title={booking.booking_id}>
                      {shortenBookingId(booking.booking_id)}
                    </div>
                    <div className="mt-1 text-xs text-slate-500">Row priority {booking.max_row}</div>
                  </td>
                  <td className="py-4 pr-4 align-top">
                    <div className="flex flex-wrap gap-2">
                      {booking.seats.map((seat) => (
                        <span key={seat} className="pill">
                          {seat}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="py-4 pr-4 align-top">
                    <a
                      href={`tel:${booking.mobile_number}`}
                      className="inline-flex items-center gap-2 rounded-full border border-slate-200 px-3 py-2 font-semibold text-slate-700 transition hover:border-teal-200 hover:bg-teal-50 hover:text-teal-700"
                    >
                      <PhoneIcon />
                      {booking.mobile_number}
                    </a>
                  </td>
                  <td className="py-4 pr-4 align-top">
                    <button
                      type="button"
                      onClick={() => onToggleBoarding(booking)}
                      disabled={togglingId === booking.booking_id}
                      className={`rounded-2xl px-4 py-2 font-semibold transition ${
                        booking.is_boarded
                          ? "bg-emerald-100 text-emerald-700 hover:bg-emerald-200"
                          : "bg-slate-900 text-white hover:bg-slate-800"
                      } disabled:cursor-not-allowed disabled:opacity-60`}
                    >
                      {togglingId === booking.booking_id
                        ? "Updating..."
                        : booking.is_boarded
                          ? "Boarded"
                          : "Mark Boarded"}
                    </button>
                  </td>
                  <td className="py-4 pr-0 align-top">
                    <button
                      type="button"
                      disabled={!booking.can_edit}
                      onClick={() => onEdit(booking)}
                      className="rounded-2xl border border-slate-300 px-4 py-2 font-semibold text-slate-700 transition hover:border-slate-400 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      {booking.can_edit ? "Edit" : "Locked"}
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6" className="py-10 text-center text-slate-500">
                  No bookings found for the selected filters.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
