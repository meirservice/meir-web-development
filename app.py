"""Meir Web Development Services — Flask backend.

Serves the website and handles consultation bookings:
  1. validates the form,
  2. appends a row to Google Sheets (or data/bookings.csv until Sheets is set up),
  3. emails the client a confirmation (+ calendar invite) and alerts the owner.

Run locally:   python app.py            → http://localhost:5000
Production:    gunicorn app:app
"""
from __future__ import annotations

import logging
import re
import secrets
import threading
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from flask import Flask, jsonify, request, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix

from backend import config, mailer, storage

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("meir")

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)  # real client IP behind Render/Railway proxies
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024  # bookings are tiny; reject anything large

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]{2,}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
LIMITS = {"name": 100, "email": 150, "phone": 60, "details": 3000, "client_timezone": 64}

_hits: dict[str, deque] = defaultdict(deque)
_hits_lock = threading.Lock()


# ---------------------------------------------------------------- helpers
def now_biz() -> datetime:
    return datetime.now(ZoneInfo(config.TIMEZONE))


def rate_limited(ip: str) -> bool:
    window = 3600
    t = time.time()
    with _hits_lock:
        q = _hits[ip]
        while q and t - q[0] > window:
            q.popleft()
        if len(q) >= config.RATE_LIMIT_PER_HOUR:
            return True
        q.append(t)
        return False


def clean(value, limit: int) -> str:
    return str(value or "").replace("\r\n", "\n").strip()[:limit]


def validate(data: dict) -> tuple[dict, dict]:
    b = {
        "name": clean(data.get("name"), LIMITS["name"]),
        "email": clean(data.get("email"), LIMITS["email"]).lower(),
        "phone": clean(data.get("phone"), LIMITS["phone"]),
        "service": clean(data.get("service"), 120),
        "budget": clean(data.get("budget"), 40),
        "date": clean(data.get("date"), 10),
        "time": clean(data.get("time"), 10),
        "details": clean(data.get("details"), LIMITS["details"]),
        "client_timezone": clean(data.get("client_timezone"), LIMITS["client_timezone"]),
    }
    errors: dict[str, str] = {}

    if len(b["name"]) < 2:
        errors["name"] = "Please enter your full name."
    if not EMAIL_RE.match(b["email"]):
        errors["email"] = "Please enter a valid email address."
    if b["service"] not in config.SERVICES:
        errors["service"] = "Please choose a service from the list."
    if b["budget"] not in config.BUDGETS:
        b["budget"] = ""
    if len(b["details"]) < 10:
        errors["details"] = "Tell us a little about your project (at least 10 characters)."

    # Date & time: real date, inside the booking window, open day, valid slot, not in the past
    if not DATE_RE.match(b["date"]) or b["time"] not in config.TIME_SLOTS:
        errors["date"] = "Please pick a date and time on the calendar."
    else:
        try:
            start = mailer.meeting_start(b["date"], b["time"])
            today = now_biz().date()
            if start.weekday() in config.CLOSED_WEEKDAYS:
                errors["date"] = "We're closed that day — please pick another date."
            elif start < now_biz() + timedelta(hours=1):
                errors["date"] = "That time has already passed — please pick a later slot."
            elif start.date() > today + timedelta(days=config.BOOKING_WINDOW_DAYS):
                errors["date"] = f"Bookings open up to {config.BOOKING_WINDOW_DAYS} days ahead."
        except ValueError:
            errors["date"] = "Please pick a valid date."
    return b, errors


def new_booking_id() -> str:
    return f"MEIR-{now_biz():%y%m%d}-{secrets.token_hex(2).upper()}"


# ---------------------------------------------------------------- routes
@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/consultation")
def consultation():
    return send_from_directory(app.static_folder, "consultation.html")


@app.get("/healthz")
def health():
    return jsonify(ok=True, storage=storage.backend_name(), email=mailer.provider())


@app.get("/api/config")
def api_config():
    return jsonify(
        services=config.SERVICES,
        time_slots=config.TIME_SLOTS,
        timezone=config.TIMEZONE,
        timezone_label=config.TIMEZONE_LABEL,
        closed_weekdays=config.CLOSED_WEEKDAYS,
        booking_window_days=config.BOOKING_WINDOW_DAYS,
        open_hour=config.OPEN_HOUR,
        close_hour=config.CLOSE_HOUR,
    )


@app.get("/api/slots")
def api_slots():
    date = request.args.get("date", "")
    if not DATE_RE.match(date):
        return jsonify(ok=False, message="Use ?date=YYYY-MM-DD"), 400
    try:
        taken = storage.taken_slots(date)
    except Exception:  # noqa: BLE001
        log.exception("Could not read availability")
        return jsonify(ok=False, date=date, taken=[]), 503
    return jsonify(ok=True, date=date, taken=taken)


@app.get("/api/availability")
def api_availability():
    """Booked times for a whole month, so the calendar can grey out full days."""
    month = request.args.get("month", "")
    if not re.match(r"^\d{4}-\d{2}$", month):
        return jsonify(ok=False, message="Use ?month=YYYY-MM"), 400
    try:
        taken = storage.taken_by_date(month)
    except Exception:  # noqa: BLE001
        log.exception("Could not read availability")
        return jsonify(ok=False, month=month, taken={}), 503
    return jsonify(ok=True, month=month, taken=taken, slots=config.TIME_SLOTS)


@app.post("/api/book")
def api_book():
    data = request.get_json(silent=True) or request.form.to_dict()

    # Honeypot: bots fill the hidden "website" field. Pretend success, save nothing.
    if data.get("website"):
        log.info("Honeypot triggered from %s", request.remote_addr)
        return jsonify(ok=True, booking_id="MEIR-000000-0000", email_sent=True)

    if rate_limited(request.remote_addr or "unknown"):
        return jsonify(ok=False, message="Too many bookings from this connection. Please try again later or email us directly."), 429

    booking, errors = validate(data)
    if errors:
        return jsonify(ok=False, message="Please fix the highlighted fields.", errors=errors), 400

    booking["booking_id"] = new_booking_id()
    booking["submitted_at"] = now_biz().strftime("%Y-%m-%d %H:%M:%S")

    # 1) Claim the slot and save — atomic, so one date + time can only be booked once
    try:
        storage.book_slot(booking)
    except storage.SlotTaken:
        return jsonify(ok=False, code="slot_taken",
                       message="Sorry — someone has just booked that time. Please choose another slot.",
                       errors={"date": "That time is no longer available."}), 409
    except Exception:  # noqa: BLE001
        # Storage is down, so we can't guarantee the slot. Don't confirm it to the client,
        # but alert the owner so the lead isn't lost.
        log.exception("Saving booking %s failed", booking["booking_id"])
        threading.Thread(target=mailer.send, args=(mailer.owner_email(booking, "FAILED"),), daemon=True).start()
        return jsonify(ok=False, message="We couldn't complete your booking right now. Please try again in a minute, "
                                         "or message us on WhatsApp and we'll book you in."), 503

    # 2) Owner alert in the background (never slows down the visitor)
    threading.Thread(target=mailer.send, args=(mailer.owner_email(booking, storage.backend_name()),), daemon=True).start()

    # 3) Client confirmation
    email_sent = mailer.send(mailer.client_email(booking))

    log.info("Booking %s saved_to=%s client_email=%s", booking["booking_id"], storage.backend_name(), email_sent)
    return jsonify(ok=True, booking_id=booking["booking_id"], email_sent=email_sent)


@app.after_request
def headers(resp):
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    if request.path.startswith("/api/"):
        resp.headers["Cache-Control"] = "no-store"  # availability must never be cached
    origin = request.headers.get("Origin")
    if origin and origin in config.ALLOWED_ORIGINS:  # only needed if the front-end is hosted elsewhere
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        resp.headers["Vary"] = "Origin"
    return resp


@app.route("/api/book", methods=["OPTIONS"])
def book_preflight():
    return ("", 204)


if __name__ == "__main__":
    log.info("Storage: %s | Email: %s", storage.backend_name(), mailer.provider())
    app.run(host="0.0.0.0", port=int(__import__("os").getenv("PORT", "5000")), debug=config.DEBUG)
