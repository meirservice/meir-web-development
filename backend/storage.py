"""Where bookings are saved — and the guarantee that a time slot can only be booked once.

* Google Sheets — when GOOGLE_SHEET_ID and service-account credentials are set.
* Local CSV (data/bookings.csv) — automatic fallback while Google isn't set up yet.

How double-booking is prevented
-------------------------------
1. A cross-process file lock (data/.booking.lock) wraps "check slot → save row",
   so two requests — even on different gunicorn workers — can't both pass the check.
2. Inside the lock the check reads the sheet fresh (never the cache).
3. Google Sheets only: after saving, the sheet is read again. If another booking for
   the same date + time exists (e.g. a second server instance, or a row someone typed
   in by hand), the earliest one wins and the later row is removed again.
A slot frees up when its Status is set to "Cancelled".
"""
from __future__ import annotations

import csv
import json
import logging
import os
import threading
import time
from pathlib import Path

from filelock import FileLock

from . import config

log = logging.getLogger(__name__)

HEADERS = [
    "Submitted At",
    "Booking ID",
    "Status",
    "Full Name",
    "Email",
    "Phone / Discord",
    "Service",
    "Budget",
    "Preferred Date",
    "Preferred Time",
    "Business Timezone",
    "Client Timezone",
    "Project Details",
]
SUBMITTED_COL = HEADERS.index("Submitted At")
ID_COL = HEADERS.index("Booking ID")
STATUS_COL = HEADERS.index("Status")
DATE_COL = HEADERS.index("Preferred Date")
TIME_COL = HEADERS.index("Preferred Time")
CANCELLED = {"cancelled", "canceled"}

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CSV_PATH = DATA_DIR / "bookings.csv"
LOCK_PATH = DATA_DIR / ".booking.lock"

_thread_lock = threading.Lock()  # guards the gspread client + cache inside one process
_ws = None
_cache = {"at": 0.0, "rows": []}
CACHE_SECONDS = 10  # for the public availability endpoints only — bookings always read fresh


class SlotTaken(Exception):
    """Raised when the requested date + time is already booked."""


def _norm_time(t: str) -> str:
    """'09:30 am' → '9:30 AM' so hand-typed sheet rows still match."""
    t = " ".join(t.strip().upper().split())
    return t[1:] if t.startswith("0") else t


def _row(b: dict) -> list[str]:
    return [
        b["submitted_at"], b["booking_id"], "New", b["name"], b["email"], b["phone"],
        b["service"], b["budget"], b["date"], b["time"], config.TIMEZONE,
        b["client_timezone"], b["details"],
    ]


def _active(r: list[str]) -> bool:
    status = r[STATUS_COL].strip().lower() if len(r) > STATUS_COL else ""
    return len(r) > TIME_COL and status not in CANCELLED


# ---------------------------------------------------------------- Google Sheets
def sheets_enabled() -> bool:
    if not config.GOOGLE_SHEET_ID:
        return False
    return bool(config.GOOGLE_SERVICE_ACCOUNT_JSON) or os.path.exists(config.GOOGLE_SERVICE_ACCOUNT_FILE)


def _worksheet():
    """Open (and lazily create) the Bookings tab, making sure the header row exists."""
    global _ws
    if _ws is not None:
        return _ws
    import gspread  # imported lazily so the app still starts without Google set up

    if config.GOOGLE_SERVICE_ACCOUNT_JSON:
        client = gspread.service_account_from_dict(json.loads(config.GOOGLE_SERVICE_ACCOUNT_JSON))
    else:
        client = gspread.service_account(filename=config.GOOGLE_SERVICE_ACCOUNT_FILE)

    sheet = client.open_by_key(config.GOOGLE_SHEET_ID)
    try:
        ws = sheet.worksheet(config.GOOGLE_SHEET_TAB)
    except gspread.WorksheetNotFound:
        ws = sheet.add_worksheet(title=config.GOOGLE_SHEET_TAB, rows=1000, cols=len(HEADERS))

    first = ws.row_values(1)
    if not first:
        ws.update([HEADERS], "A1")
        ws.format("A1:M1", {"textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
                            "backgroundColor": {"red": 0, "green": 0.208, "blue": 0.58}})
        ws.freeze(rows=1)
    elif first != HEADERS:
        log.warning("Row 1 of tab %r doesn't match the expected headers — appending anyway.", config.GOOGLE_SHEET_TAB)
    _ws = ws
    return ws


# ---------------------------------------------------------------- reading
def _read_rows_fresh() -> list[list[str]]:
    with _thread_lock:
        if sheets_enabled():
            rows = _worksheet().get_all_values()[1:]
        elif CSV_PATH.exists():
            with CSV_PATH.open(newline="", encoding="utf-8") as f:
                rows = list(csv.reader(f))[1:]
        else:
            rows = []
        _cache.update(at=time.time(), rows=rows)
    return rows


def _read_rows_cached() -> list[list[str]]:
    if time.time() - _cache["at"] < CACHE_SECONDS:
        return _cache["rows"]
    return _read_rows_fresh()


def _taken_in(rows: list[list[str]], date: str) -> list[str]:
    return sorted({_norm_time(r[TIME_COL]) for r in rows if _active(r) and r[DATE_COL].strip() == date})


# ---------------------------------------------------------------- public API
def backend_name() -> str:
    return "google_sheets" if sheets_enabled() else "local_csv"


def taken_slots(date: str, fresh: bool = False) -> list[str]:
    """Times already booked on one date (YYYY-MM-DD)."""
    rows = _read_rows_fresh() if fresh else _read_rows_cached()
    return _taken_in(rows, date)


def taken_by_date(month: str) -> dict[str, list[str]]:
    """{'2026-10-24': ['9:30 AM', ...], ...} for every date in a month (YYYY-MM)."""
    out: dict[str, set] = {}
    for r in _read_rows_cached():
        if _active(r) and r[DATE_COL].startswith(month + "-"):
            out.setdefault(r[DATE_COL].strip(), set()).add(_norm_time(r[TIME_COL]))
    return {d: sorted(t) for d, t in out.items()}


def book_slot(booking: dict) -> None:
    """Atomically claim booking['date'] + booking['time'] and save the row.

    Raises SlotTaken if the slot is already booked. Raises other exceptions if
    the storage itself fails (the caller decides what to do then).
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    slot = _norm_time(booking["time"])

    with FileLock(str(LOCK_PATH), timeout=30):
        # 1) Fresh check — inside the lock, so nobody can slip in between check and save
        if slot in _taken_in(_read_rows_fresh(), booking["date"]):
            raise SlotTaken()

        # 2) Save
        row = _row(booking)
        with _thread_lock:
            if sheets_enabled():
                # RAW = stored exactly as typed, so visitor text can never run as a formula.
                _worksheet().append_row(row, value_input_option="RAW", insert_data_option="INSERT_ROWS")
            else:
                new = not CSV_PATH.exists()
                with CSV_PATH.open("a", newline="", encoding="utf-8") as f:
                    w = csv.writer(f)
                    if new:
                        w.writerow(HEADERS)
                    w.writerow(row)

        # 3) Google Sheets: verify we really own the slot (covers multiple server instances)
        if sheets_enabled():
            rows = _read_rows_fresh()
            rivals = [r for r in rows if _active(r) and r[DATE_COL].strip() == booking["date"]
                      and _norm_time(r[TIME_COL]) == slot]
            winner = min(rivals, key=lambda r: (r[SUBMITTED_COL], r[ID_COL]), default=None)
            if winner is not None and winner[ID_COL] != booking["booking_id"]:
                _remove_row(booking["booking_id"])
                raise SlotTaken()
        else:
            _cache["rows"] = _cache["rows"] + [row]


def _remove_row(booking_id: str) -> None:
    """Delete the row we just appended (lost a race for the slot)."""
    with _thread_lock:
        ws = _worksheet()
        cell = ws.find(booking_id, in_column=ID_COL + 1)
        if cell:
            ws.delete_rows(cell.row)
            log.info("Removed duplicate booking row %s (slot already taken)", booking_id)
        _cache["at"] = 0.0
