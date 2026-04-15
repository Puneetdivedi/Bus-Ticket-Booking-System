CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id VARCHAR(36) NOT NULL UNIQUE,
    travel_date DATE NOT NULL,
    mobile_number VARCHAR(10) NOT NULL,
    is_boarded BOOLEAN NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_bookings_booking_id ON bookings (booking_id);
CREATE INDEX IF NOT EXISTS ix_bookings_travel_date ON bookings (travel_date);
CREATE INDEX IF NOT EXISTS ix_bookings_mobile_number ON bookings (mobile_number);

CREATE TABLE IF NOT EXISTS booking_seats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id VARCHAR(36) NOT NULL,
    travel_date DATE NOT NULL,
    seat_number VARCHAR(4) NOT NULL,
    CONSTRAINT fk_booking_seats_booking
        FOREIGN KEY (booking_id)
        REFERENCES bookings (booking_id)
        ON DELETE CASCADE,
    CONSTRAINT uq_booking_seat_per_day UNIQUE (travel_date, seat_number)
);

CREATE INDEX IF NOT EXISTS ix_booking_seats_booking_id ON booking_seats (booking_id);
CREATE INDEX IF NOT EXISTS ix_booking_seats_travel_date ON booking_seats (travel_date);
