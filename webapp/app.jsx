const { useEffect, useMemo, useState } = React;

const api = axios.create({
  baseURL: window.location.origin,
  headers: {
    "Content-Type": "application/json",
  },
});

const SEAT_COLUMNS = ["A", "B", "C", "D"];
const SEAT_ROWS = Array.from({ length: 15 }, (_, index) => index + 1);
const URL_PARAMS = new URLSearchParams(window.location.search);
const QUERY_DATE = /^\d{4}-\d{2}-\d{2}$/.test(URL_PARAMS.get("date") || "") ? URL_PARAMS.get("date") : null;
const DEMO_MODE = URL_PARAMS.get("demo") === "1" || window.location.protocol === "file:";
const DEMO_TRAVEL_DATE = "2026-04-20";
const DEMO_BOOKINGS = [
  {
    booking_id: "9fcbc544-a525-4310-bf21-8679f85a911d",
    travel_date: DEMO_TRAVEL_DATE,
    mobile_number: "9999988888",
    seats: ["A14", "A15"],
    passenger_count: 2,
    is_boarded: true,
    can_edit: true,
    max_row: 15,
    sequence_number: 1,
  },
  {
    booking_id: "d8e4cc1b-c79f-453f-b994-aa03f52ea115",
    travel_date: DEMO_TRAVEL_DATE,
    mobile_number: "9876543210",
    seats: ["A1", "B1"],
    passenger_count: 2,
    is_boarded: false,
    can_edit: true,
    max_row: 1,
    sequence_number: 2,
  },
];
const DEMO_SEQUENCE = DEMO_BOOKINGS.map((booking) => ({
  sequence_number: booking.sequence_number,
  booking_id: booking.booking_id,
  mobile_number: booking.mobile_number,
  seats: booking.seats,
  max_row: booking.max_row,
  is_boarded: booking.is_boarded,
}));

function getTodayDateString() {
  const now = new Date();
  const offset = now.getTimezoneOffset() * 60_000;
  return new Date(now.getTime() - offset).toISOString().slice(0, 10);
}

function sortSeats(seats) {
  return [...seats].sort((left, right) => {
    const leftRow = Number.parseInt(left.slice(1), 10);
    const rightRow = Number.parseInt(right.slice(1), 10);
    if (leftRow === rightRow) {
      return left.localeCompare(right);
    }
    return leftRow - rightRow;
  });
}

function formatTravelDate(value) {
  if (!value) {
    return "N/A";
  }

  return new Intl.DateTimeFormat("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(`${value}T00:00:00`));
}

function getApiErrorMessage(error) {
  if (typeof error?.response?.data?.detail === "string") {
    return error.response.data.detail;
  }

  if (Array.isArray(error?.response?.data?.detail)) {
    return error.response.data.detail.map((item) => item.msg).join(", ");
  }

  return error?.message || "Something went wrong while talking to the server.";
}

function SeatLegend() {
  return (
    <div className="legend-row">
      <span className="legend" style={{ background: "#dcfce7", color: "#166534" }}>
        <span className="dot" style={{ background: "#22c55e" }} />
        Available
      </span>
      <span className="legend" style={{ background: "#dbeafe", color: "#1d4ed8" }}>
        <span className="dot" style={{ background: "#2563eb" }} />
        Selected
      </span>
      <span className="legend" style={{ background: "#fee2e2", color: "#b91c1c" }}>
        <span className="dot" style={{ background: "#ef4444" }} />
        Booked
      </span>
    </div>
  );
}

function SeatLayout({ bookedSeats, selectedSeats, onToggleSeat }) {
  const bookedSet = new Set(bookedSeats);
  const selectedSet = new Set(selectedSeats);

  return (
    <div className="seat-shell">
      <div className="seat-header">
        <span>Front Entry</span>
        <span className="driver-chip">Driver</span>
      </div>

      <div className="seat-grid">
        {SEAT_ROWS.map((row) => {
          const rowSeats = SEAT_COLUMNS.map((column) => `${column}${row}`);
          return (
            <div key={row} className="seat-row">
              {rowSeats.slice(0, 2).map((seat) => {
                const status = bookedSet.has(seat)
                  ? "booked"
                  : selectedSet.has(seat)
                    ? "selected"
                    : "available";

                return (
                  <button
                    type="button"
                    key={seat}
                    className={`seat ${status}`}
                    onClick={() => onToggleSeat(seat)}
                    disabled={status === "booked"}
                  >
                    {seat}
                  </button>
                );
              })}

              <div className="row-num">{row}</div>

              {rowSeats.slice(2).map((seat) => {
                const status = bookedSet.has(seat)
                  ? "booked"
                  : selectedSet.has(seat)
                    ? "selected"
                    : "available";

                return (
                  <button
                    type="button"
                    key={seat}
                    className={`seat ${status}`}
                    onClick={() => onToggleSeat(seat)}
                    disabled={status === "booked"}
                  >
                    {seat}
                  </button>
                );
              })}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function ConfirmationModal({ state, onClose }) {
  if (!state.booking) {
    return null;
  }

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true">
      <div className="modal-panel">
        <div className="summary-chip">{state.mode === "update" ? "Booking updated" : "Booking confirmed"}</div>
        <h3 className="summary-title">Passenger details are locked in</h3>
        <p className="subtitle">Share the booking ID with the traveller before boarding begins.</p>

        <div className="detail-box">
          <div className="detail-item">
            <div className="detail-label">Booking ID</div>
            <div className="detail-value">{state.booking.booking_id}</div>
          </div>
          <div className="detail-item">
            <div className="detail-label">Travel Date</div>
            <div className="detail-value">{formatTravelDate(state.booking.travel_date)}</div>
          </div>
          <div className="detail-item">
            <div className="detail-label">Mobile Number</div>
            <div className="detail-value">{state.booking.mobile_number}</div>
          </div>
          <div className="detail-item">
            <div className="detail-label">Selected Seats</div>
            <div className="pill-row" style={{ marginTop: 10 }}>
              {state.booking.seats.map((seat) => (
                <span key={seat} className="pill">
                  {seat}
                </span>
              ))}
            </div>
          </div>
        </div>

        <div className="button-row">
          <button type="button" className="btn primary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

function BoardingPanel({ isLoading, sequence, estimatedTime }) {
  return (
    <section className="card">
      <div className="boarding-header">
        <div>
          <div className="section-badge blue">Boarding Algorithm</div>
          <h2 className="title">Optimal far-to-near boarding sequence</h2>
          <p className="subtitle">
            Each booking is ranked by its farthest seat row. Higher row numbers board first so no group needs to cross
            a settling passenger.
          </p>
        </div>

        <div className="est-box">
          <div className="metric-label">Estimated Completion</div>
          <div className="metric-value">{estimatedTime}s</div>
        </div>
      </div>

      {isLoading ? (
        <div className="loading-state">Calculating the best boarding sequence...</div>
      ) : sequence.length ? (
        <div className="boarding-grid">
          {sequence.map((booking) => (
            <article key={booking.booking_id} className={`boarding-card ${booking.is_boarded ? "boarded" : ""}`}>
              <div className="boarding-top">
                <span className="seq-pill">#{booking.sequence_number}</span>
                <span className="metric-label" style={{ color: "#6b7280", padding: 0 }}>
                  Max Row {booking.max_row}
                </span>
              </div>

              <div className="boarding-id">{booking.booking_id}</div>
              <div className="pill-row" style={{ marginTop: 14 }}>
                {booking.seats.map((seat) => (
                  <span key={seat} className="pill">
                    {seat}
                  </span>
                ))}
              </div>
              <div className="footer-note">
                {booking.mobile_number} · {booking.is_boarded ? "Boarded" : "Waiting"}
              </div>
            </article>
          ))}
        </div>
      ) : (
        <div className="empty-state">No bookings are available for this date yet.</div>
      )}
    </section>
  );
}

function BookingTable({ bookings, travelDate, isLoading, togglingId, onToggleBoarding, onEdit }) {
  return (
    <section className="card">
      <div className="card-header">
        <div>
          <div className="section-badge red">Screen 2</div>
          <h2 className="title">Booking list and boarding control</h2>
          <p className="subtitle">
            Sequence order is highlighted from farthest row to nearest row for {formatTravelDate(travelDate)}.
          </p>
        </div>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Seq</th>
              <th>Booking ID</th>
              <th>Seats</th>
              <th>Mobile</th>
              <th>Boarding</th>
              <th>Edit</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr>
                <td colSpan="6">
                  <div className="loading-state">Loading bookings...</div>
                </td>
              </tr>
            ) : bookings.length ? (
              bookings.map((booking) => (
                <tr key={booking.booking_id} className={booking.is_boarded ? "boarded-row" : ""}>
                  <td>
                    <span className="seq-circle">{booking.sequence_number}</span>
                  </td>
                  <td>
                    <div style={{ fontWeight: 800 }}>{booking.booking_id.slice(0, 8)}...</div>
                    <div className="footer-note" style={{ marginTop: 6 }}>
                      Row priority {booking.max_row}
                    </div>
                  </td>
                  <td>
                    <div className="pill-row">
                      {booking.seats.map((seat) => (
                        <span key={seat} className="pill">
                          {seat}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td>
                    <a href={`tel:${booking.mobile_number}`} className="phone-pill">
                      ☎ {booking.mobile_number}
                    </a>
                  </td>
                  <td>
                    <button
                      type="button"
                      className={`status-btn ${booking.is_boarded ? "boarded" : "pending"}`}
                      onClick={() => onToggleBoarding(booking)}
                      disabled={togglingId === booking.booking_id}
                    >
                      {togglingId === booking.booking_id
                        ? "Updating..."
                        : booking.is_boarded
                          ? "Boarded"
                          : "Mark Boarded"}
                    </button>
                  </td>
                  <td>
                    <button
                      type="button"
                      className="status-btn edit"
                      onClick={() => onEdit(booking)}
                      disabled={!booking.can_edit}
                    >
                      {booking.can_edit ? "Edit" : "Locked"}
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6">
                  <div className="empty-state">No bookings found for the selected filters.</div>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function App() {
  const initialDate = QUERY_DATE || getTodayDateString();
  const demoDate = DEMO_MODE ? QUERY_DATE || DEMO_TRAVEL_DATE : initialDate;
  const [formState, setFormState] = useState(
    DEMO_MODE
      ? {
          travelDate: demoDate,
          mobileNumber: DEMO_BOOKINGS[0].mobile_number,
          selectedSeats: DEMO_BOOKINGS[0].seats,
        }
      : {
          travelDate: demoDate,
          mobileNumber: "",
          selectedSeats: [],
        },
  );
  const [filters, setFilters] = useState({
    travelDate: demoDate,
    mobileSearch: "",
  });
  const [editingBooking, setEditingBooking] = useState(DEMO_MODE ? DEMO_BOOKINGS[0] : null);
  const [bookedSeats, setBookedSeats] = useState(
    DEMO_MODE ? sortSeats(DEMO_BOOKINGS.flatMap((booking) => booking.seats)) : [],
  );
  const [bookingList, setBookingList] = useState(
    DEMO_MODE
      ? {
          total_bookings: DEMO_BOOKINGS.length,
          total_passengers: DEMO_BOOKINGS.reduce((sum, booking) => sum + booking.passenger_count, 0),
          bookings: DEMO_BOOKINGS,
        }
      : {
          total_bookings: 0,
          total_passengers: 0,
          bookings: [],
        },
  );
  const [boardingSequence, setBoardingSequence] = useState(DEMO_MODE ? DEMO_SEQUENCE : []);
  const [estimatedTime, setEstimatedTime] = useState(DEMO_MODE ? 60 : 0);
  const [pageError, setPageError] = useState("");
  const [notice, setNotice] = useState("");
  const [formError, setFormError] = useState("");
  const [loadingSeatMap, setLoadingSeatMap] = useState(false);
  const [loadingDashboard, setLoadingDashboard] = useState(!DEMO_MODE);
  const [submitting, setSubmitting] = useState(false);
  const [togglingId, setTogglingId] = useState("");
  const [modalState, setModalState] = useState({
    booking: null,
    mode: "create",
  });

  const reservedSeats = useMemo(() => {
    return bookedSeats.filter((seat) => {
      const editableSeat =
        editingBooking &&
        editingBooking.travel_date === formState.travelDate &&
        editingBooking.seats.includes(seat);
      return !editableSeat;
    });
  }, [bookedSeats, editingBooking, formState.travelDate]);

  async function loadSeatMap(travelDate) {
    setLoadingSeatMap(true);
    try {
      const response = await api.get("/api/bookings/seat-map", {
        params: { travel_date: travelDate },
      });
      setBookedSeats(response.data.booked_seats);
    } catch (error) {
      setPageError(getApiErrorMessage(error));
    } finally {
      setLoadingSeatMap(false);
    }
  }

  async function loadDashboard(travelDate, mobileSearch) {
    setLoadingDashboard(true);
    try {
      const [bookingsResponse, sequenceResponse] = await Promise.all([
        api.get("/api/bookings", {
          params: {
            travel_date: travelDate,
            ...(mobileSearch ? { mobile_number: mobileSearch } : {}),
          },
        }),
        api.get("/api/bookings/boarding-sequence", {
          params: { travel_date: travelDate },
        }),
      ]);

      setBookingList(bookingsResponse.data);
      setBoardingSequence(sequenceResponse.data.bookings);
      setEstimatedTime(sequenceResponse.data.estimated_total_time_seconds);
      setPageError("");
    } catch (error) {
      setPageError(getApiErrorMessage(error));
    } finally {
      setLoadingDashboard(false);
    }
  }

  useEffect(() => {
    if (DEMO_MODE) {
      return;
    }
    loadSeatMap(formState.travelDate);
  }, [formState.travelDate]);

  useEffect(() => {
    if (DEMO_MODE) {
      return;
    }
    const handle = window.setTimeout(() => {
      loadDashboard(filters.travelDate, filters.mobileSearch);
    }, 180);
    return () => window.clearTimeout(handle);
  }, [filters.travelDate, filters.mobileSearch]);

  useEffect(() => {
    setFormState((current) => {
      const nextSeats = current.selectedSeats.filter((seat) => !reservedSeats.includes(seat));
      if (nextSeats.length === current.selectedSeats.length) {
        return current;
      }
      return { ...current, selectedSeats: nextSeats };
    });
  }, [reservedSeats]);

  function resetForm(nextTravelDate = formState.travelDate) {
    setEditingBooking(null);
    setFormError("");
    setFormState({
      travelDate: nextTravelDate,
      mobileNumber: "",
      selectedSeats: [],
    });
  }

  function handleSeatToggle(seat) {
    if (reservedSeats.includes(seat)) {
      return;
    }

    setFormError("");
    setFormState((current) => {
      if (current.selectedSeats.includes(seat)) {
        return {
          ...current,
          selectedSeats: current.selectedSeats.filter((selectedSeat) => selectedSeat !== seat),
        };
      }

      if (current.selectedSeats.length >= 6) {
        setFormError("A single booking cannot contain more than 6 seats.");
        return current;
      }

      return {
        ...current,
        selectedSeats: sortSeats([...current.selectedSeats, seat]),
      };
    });
  }

  function validateForm() {
    if (!formState.travelDate || formState.travelDate < getTodayDateString()) {
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

  async function handleSubmit(event) {
    event.preventDefault();

    if (DEMO_MODE) {
      setNotice("Demo mode is visual-only. Start the app from localhost:8000 to save real bookings.");
      return;
    }

    const validationMessage = validateForm();
    if (validationMessage) {
      setFormError(validationMessage);
      return;
    }

    setSubmitting(true);
    setPageError("");
    setNotice("");

    const payload = {
      travel_date: formState.travelDate,
      mobile_number: formState.mobileNumber,
      seats: formState.selectedSeats,
    };

    try {
      const response = editingBooking
        ? await api.put(`/api/bookings/${editingBooking.booking_id}`, payload)
        : await api.post("/api/bookings", payload);

      setModalState({
        booking: response.data,
        mode: editingBooking ? "update" : "create",
      });
      setNotice(editingBooking ? "Booking updated successfully." : "Booking created successfully.");
      setFilters((current) => ({ ...current, travelDate: response.data.travel_date }));
      await Promise.all([
        loadSeatMap(response.data.travel_date),
        loadDashboard(response.data.travel_date, filters.mobileSearch),
      ]);
      resetForm(response.data.travel_date);
    } catch (error) {
      setFormError(getApiErrorMessage(error));
    } finally {
      setSubmitting(false);
    }
  }

  function handleEdit(booking) {
    setEditingBooking(booking);
    setFormState({
      travelDate: booking.travel_date,
      mobileNumber: booking.mobile_number,
      selectedSeats: booking.seats,
    });
    setPageError("");
    setNotice("");
    setFormError("");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function handleToggleBoarding(booking) {
    if (DEMO_MODE) {
      setBookingList((current) => ({
        ...current,
        bookings: current.bookings.map((item) =>
          item.booking_id === booking.booking_id ? { ...item, is_boarded: !item.is_boarded } : item,
        ),
      }));
      setBoardingSequence((current) =>
        current.map((item) =>
          item.booking_id === booking.booking_id ? { ...item, is_boarded: !item.is_boarded } : item,
        ),
      );
      setNotice(`Demo mode toggled ${booking.booking_id.slice(0, 8)}...`);
      return;
    }

    setTogglingId(booking.booking_id);
    setPageError("");
    setNotice("");
    try {
      await api.patch(`/api/bookings/${booking.booking_id}/boarding`, {
        is_boarded: !booking.is_boarded,
      });
      setNotice(`Booking ${!booking.is_boarded ? "marked as boarded" : "moved back to waiting"}.`);
      await loadDashboard(filters.travelDate, filters.mobileSearch);
    } catch (error) {
      setPageError(getApiErrorMessage(error));
    } finally {
      setTogglingId("");
    }
  }

  function handleExportCsv() {
    if (DEMO_MODE) {
      setNotice("Demo mode does not export files. Run the app from localhost:8000 for live export.");
      return;
    }
    const url = `/api/bookings/export/csv?travel_date=${encodeURIComponent(filters.travelDate)}`;
    window.open(url, "_blank");
  }

  return (
    <>
      <div className="page">
        <section className="hero">
          <div>
            <div className="hero-badge">Bus Conductor Console</div>
            <h1>Bus Ticket Booking System with live seat control and optimal boarding order</h1>
            <p>
              Manage bookings, prevent seat conflicts, and board passengers from the farthest row to the nearest row
              from one responsive conductor dashboard.
            </p>
          </div>

          <div className="metric-grid">
            <div className="metric-card">
              <div className="metric-label">Travel Date</div>
              <div className="metric-value">{formatTravelDate(filters.travelDate)}</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Bookings</div>
              <div className="metric-value">{bookingList.total_bookings}</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Passengers</div>
              <div className="metric-value">{bookingList.total_passengers}</div>
            </div>
          </div>
        </section>

        <div className="stack">
          {pageError ? <div className="banner error">{pageError}</div> : null}
          {notice ? <div className="banner success">{notice}</div> : null}
          {DEMO_MODE ? (
            <div className="banner success">
              Demo mode is rendering the real React UI with sample data. Run <code>run_app.bat</code> or
              <code> run_app.ps1</code> to use the live backend at <code>http://127.0.0.1:8000</code>.
            </div>
          ) : null}

          <section className="card">
            <div className="card-header">
              <div>
                <div className="section-badge">Screen 1</div>
                <h2 className="title">Book or update a passenger block</h2>
                <p className="subtitle">
                  Select a valid travel date, capture the traveller&apos;s mobile number, and lock up to six seats in a
                  single booking.
                </p>
              </div>

              {editingBooking ? <div className="edit-chip">Editing booking {editingBooking.booking_id.slice(0, 8)}...</div> : null}
            </div>

            <div className="two-col">
              <div>
                <form onSubmit={handleSubmit}>
                  <div className="field-grid">
                    <div className="field">
                      <label htmlFor="travelDate">Travel Date</label>
                      <input
                        id="travelDate"
                        className="field-input"
                        type="date"
                        value={formState.travelDate}
                        onChange={(event) => {
                          setFormError("");
                          setFormState((current) => ({ ...current, travelDate: event.target.value }));
                        }}
                      />
                    </div>

                    <div className="field">
                      <label htmlFor="mobileNumber">Mobile Number</label>
                      <input
                        id="mobileNumber"
                        className="field-input"
                        type="tel"
                        inputMode="numeric"
                        maxLength="10"
                        value={formState.mobileNumber}
                        placeholder="Enter 10-digit number"
                        onChange={(event) => {
                          setFormError("");
                          setFormState((current) => ({
                            ...current,
                            mobileNumber: event.target.value.replace(/\D/g, "").slice(0, 10),
                          }));
                        }}
                      />
                    </div>
                  </div>

                  <div className="top-split">
                    <SeatLegend />
                    <div className="pill-row">
                      <span className="pill">{formState.selectedSeats.length} selected</span>
                      <span className="pill">Maximum 6 seats per mobile per day</span>
                      {loadingSeatMap ? <span className="pill">Refreshing seat map...</span> : null}
                    </div>
                  </div>

                  <SeatLayout
                    bookedSeats={reservedSeats}
                    selectedSeats={formState.selectedSeats}
                    onToggleSeat={handleSeatToggle}
                  />

                  <div className="pill-row" style={{ marginTop: 16 }}>
                    {formState.selectedSeats.length ? (
                      formState.selectedSeats.map((seat) => (
                        <button key={seat} type="button" className="pill chip-button" onClick={() => handleSeatToggle(seat)}>
                          {seat} ×
                        </button>
                      ))
                    ) : (
                      <span className="meta-text">Choose one or more seats to continue.</span>
                    )}
                  </div>

                  {formError ? (
                    <div className="banner error" style={{ marginTop: 18 }}>
                      {formError}
                    </div>
                  ) : null}

                  <div className="button-row">
                    <button type="submit" className="btn primary" disabled={submitting}>
                      {submitting ? "Saving..." : editingBooking ? "Update Booking" : "Confirm Booking"}
                    </button>
                    <button type="button" className="btn secondary" onClick={() => resetForm(formState.travelDate)}>
                      {editingBooking ? "Cancel Edit" : "Clear Selection"}
                    </button>
                  </div>
                </form>
              </div>

              <div className="summary-card">
                <div className="summary-chip">{editingBooking ? "Ready to update" : "Ready to confirm"}</div>
                <h3 className="summary-title">Booking confirmation panel</h3>
                <p className="subtitle">
                  Successful bookings show the generated booking ID, travel date, mobile number, and seat selection.
                </p>
                <div className="detail-box">
                  <div className="detail-item">
                    <div className="detail-label">Current Travel Date</div>
                    <div className="detail-value">{formatTravelDate(formState.travelDate)}</div>
                  </div>
                  <div className="detail-item">
                    <div className="detail-label">Mobile Number</div>
                    <div className="detail-value">{formState.mobileNumber || "Not entered yet"}</div>
                  </div>
                  <div className="detail-item">
                    <div className="detail-label">Selected Seats</div>
                    <div className="pill-row" style={{ marginTop: 10 }}>
                      {formState.selectedSeats.length ? (
                        formState.selectedSeats.map((seat) => (
                          <span key={seat} className="pill">
                            {seat}
                          </span>
                        ))
                      ) : (
                        <span className="meta-text">No seats selected yet.</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <section className="card">
            <div className="card-header">
              <div>
                <h2 className="title">Daily operations filter</h2>
                <p className="subtitle">
                  Filter the booking table by travel date and optionally search passengers by mobile number.
                </p>
              </div>
            </div>

            <div className="ops-grid">
              <div className="field">
                <label htmlFor="filterDate">Travel Date</label>
                <input
                  id="filterDate"
                  className="field-input"
                  type="date"
                  value={filters.travelDate}
                  onChange={(event) =>
                    setFilters((current) => ({
                      ...current,
                      travelDate: event.target.value,
                    }))
                  }
                />
              </div>

              <div className="field">
                <label htmlFor="mobileSearch">Search Mobile</label>
                <input
                  id="mobileSearch"
                  className="field-input"
                  type="search"
                  value={filters.mobileSearch}
                  placeholder="Optional mobile number"
                  onChange={(event) =>
                    setFilters((current) => ({
                      ...current,
                      mobileSearch: event.target.value.replace(/\D/g, "").slice(0, 10),
                    }))
                  }
                />
              </div>

              <button type="button" className="btn teal" onClick={handleExportCsv}>
                Export CSV
              </button>
            </div>
          </section>

          <BoardingPanel isLoading={loadingDashboard} sequence={boardingSequence} estimatedTime={estimatedTime} />

          <BookingTable
            bookings={bookingList.bookings}
            travelDate={filters.travelDate}
            isLoading={loadingDashboard}
            togglingId={togglingId}
            onToggleBoarding={handleToggleBoarding}
            onEdit={handleEdit}
          />
        </div>
      </div>

      <ConfirmationModal
        state={modalState}
        onClose={() => setModalState({ booking: null, mode: "create" })}
      />
    </>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
