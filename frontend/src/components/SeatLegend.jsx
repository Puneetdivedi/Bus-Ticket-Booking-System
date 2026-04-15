const legendItems = [
  {
    label: "Available",
    tone: "bg-emerald-100 text-emerald-700 ring-emerald-200"
  },
  {
    label: "Selected",
    tone: "bg-blue-100 text-blue-700 ring-blue-200"
  },
  {
    label: "Booked",
    tone: "bg-rose-100 text-rose-700 ring-rose-200"
  }
];

export function SeatLegend() {
  return (
    <div className="flex flex-wrap gap-3">
      {legendItems.map((item) => (
        <span
          key={item.label}
          className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-semibold ring-1 ${item.tone}`}
        >
          <span className="h-2.5 w-2.5 rounded-full bg-current opacity-80" />
          {item.label}
        </span>
      ))}
    </div>
  );
}
