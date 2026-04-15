export function BoardingSequencePanel({ sequence, estimatedTime, isLoading }) {
  return (
    <section className="panel-surface p-5 sm:p-7">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <div className="inline-flex rounded-full bg-blue-100 px-3 py-1 text-xs font-bold uppercase tracking-[0.2em] text-blue-700">
            Boarding Algorithm
          </div>
          <h2 className="mt-3 font-['Trebuchet_MS'] text-3xl font-bold text-slate-900">
            Optimal far-to-near boarding sequence
          </h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
            Each booking is ranked by its farthest seat row. Higher row numbers board first so no group needs to cross
            a settling passenger.
          </p>
        </div>

        <div className="rounded-[24px] bg-slate-900 px-5 py-4 text-white">
          <div className="text-xs uppercase tracking-[0.2em] text-slate-300">Estimated completion</div>
          <div className="mt-1 text-3xl font-bold">{estimatedTime}s</div>
        </div>
      </div>

      {isLoading ? (
        <div className="mt-6 rounded-3xl bg-slate-50 p-6 text-sm text-slate-500">Calculating the best sequence...</div>
      ) : sequence.length ? (
        <div className="mt-6 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {sequence.map((booking) => (
            <article
              key={booking.booking_id}
              className={`rounded-[26px] border p-5 transition ${
                booking.is_boarded
                  ? "border-emerald-200 bg-emerald-50"
                  : "border-slate-200 bg-gradient-to-br from-white to-slate-50"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="rounded-full bg-slate-900 px-3 py-1 text-xs font-bold text-white">
                  #{booking.sequence_number}
                </span>
                <span className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                  Max row {booking.max_row}
                </span>
              </div>

              <div className="mt-4 text-sm font-semibold text-slate-900">{booking.booking_id}</div>

              <div className="mt-4 flex flex-wrap gap-2">
                {booking.seats.map((seat) => (
                  <span key={seat} className="pill">
                    {seat}
                  </span>
                ))}
              </div>

              <div className="mt-4 text-sm text-slate-600">{booking.mobile_number}</div>
            </article>
          ))}
        </div>
      ) : (
        <div className="mt-6 rounded-[26px] border border-dashed border-slate-200 bg-slate-50 px-5 py-8 text-sm text-slate-500">
          No bookings are available for this date yet. Create a booking to generate the boarding order.
        </div>
      )}
    </section>
  );
}
