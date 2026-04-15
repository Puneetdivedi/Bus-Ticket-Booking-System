export const TOTAL_ROWS = 15;
export const SEAT_COLUMNS = ["A", "B", "C", "D"];
export const SEAT_ROWS = Array.from({ length: TOTAL_ROWS }, (_, index) => index + 1);

export function buildSeatName(column, row) {
  return `${column}${row}`;
}

export function sortSeats(seats) {
  return [...seats].sort((left, right) => {
    const leftRow = Number.parseInt(left.slice(1), 10);
    const rightRow = Number.parseInt(right.slice(1), 10);

    if (leftRow === rightRow) {
      return left.localeCompare(right);
    }

    return leftRow - rightRow;
  });
}

export function getTodayDateString() {
  const now = new Date();
  const timezoneOffset = now.getTimezoneOffset() * 60_000;
  return new Date(now.getTime() - timezoneOffset).toISOString().slice(0, 10);
}

export function isPastDate(value) {
  return value < getTodayDateString();
}
