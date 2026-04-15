import { buildSeatName, SEAT_ROWS } from "../utils/seats";

function SeatButton({ seat, status, onClick }) {
  const variants = {
    available:
      "border-emerald-200 bg-emerald-50 text-emerald-800 hover:-translate-y-0.5 hover:border-emerald-300 hover:bg-emerald-100",
    selected:
      "border-blue-300 bg-blue-600 text-white hover:-translate-y-0.5 hover:bg-blue-700",
    booked:
      "cursor-not-allowed border-rose-200 bg-rose-100 text-rose-500 opacity-70"
  };

  return (
    <button
      type="button"
      onClick={() => onClick(seat)}
      disabled={status === "booked"}
      className={`h-12 rounded-2xl border text-sm font-bold shadow-sm transition ${variants[status]}`}
      aria-label={`Seat ${seat}`}
    >
      {seat}
    </button>
  );
}

export function SeatLayout({ bookedSeats, selectedSeats, onToggleSeat }) {
  const bookedSeatSet = new Set(bookedSeats);
  const selectedSeatSet = new Set(selectedSeats);

  return (
    <div className="rounded-[26px] border border-slate-200 bg-slate-50/80 p-4 sm:p-5">
      <div className="mb-4 flex items-center justify-between rounded-2xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white">
        <span>Front Entry</span>
        <span className="rounded-full bg-white/15 px-3 py-1 text-xs">Driver</span>
      </div>

      <div className="space-y-3">
        {SEAT_ROWS.map((row) => {
          const rowSeats = ["A", "B", "C", "D"].map((column) => buildSeatName(column, row));

          return (
            <div
              key={row}
              className="grid grid-cols-[minmax(0,1fr)_minmax(0,1fr)_42px_minmax(0,1fr)_minmax(0,1fr)] items-center gap-2"
            >
              {rowSeats.slice(0, 2).map((seat) => {
                const status = bookedSeatSet.has(seat)
                  ? "booked"
                  : selectedSeatSet.has(seat)
                    ? "selected"
                    : "available";

                return <SeatButton key={seat} seat={seat} status={status} onClick={onToggleSeat} />;
              })}

              <div className="text-center text-xs font-bold uppercase tracking-[0.25em] text-slate-400">{row}</div>

              {rowSeats.slice(2).map((seat) => {
                const status = bookedSeatSet.has(seat)
                  ? "booked"
                  : selectedSeatSet.has(seat)
                    ? "selected"
                    : "available";

                return <SeatButton key={seat} seat={seat} status={status} onClick={onToggleSeat} />;
              })}
            </div>
          );
        })}
      </div>
    </div>
  );
}
