"""Settings, loaded from environment variables (.env in local development)."""
import os

from dotenv import load_dotenv

load_dotenv()


def _bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


# ---------- Business ----------
BUSINESS_NAME = os.getenv("BUSINESS_NAME", "Meir Web Development Services")
OWNER_EMAIL = os.getenv("OWNER_EMAIL", "meirwebdevelopment@gmail.com")  # where new-booking alerts go
SITE_URL = os.getenv("SITE_URL", "https://meirwebdevelopment.com")
TIMEZONE = os.getenv("BUSINESS_TIMEZONE", "Asia/Manila")
TIMEZONE_LABEL = os.getenv("BUSINESS_TIMEZONE_LABEL", "Philippine Time, UTC+8")
MEETING_LENGTH_MIN = int(os.getenv("MEETING_LENGTH_MIN", "30"))
BOOKING_WINDOW_DAYS = int(os.getenv("BOOKING_WINDOW_DAYS", "60"))
OPEN_HOUR = int(os.getenv("OPEN_HOUR", "8"))     # 8:00 AM
CLOSE_HOUR = int(os.getenv("CLOSE_HOUR", "20"))  # 8:00 PM
CLOSED_WEEKDAYS = [int(d) for d in os.getenv("CLOSED_WEEKDAYS", "6").split(",") if d.strip()]  # Mon=0 … Sun=6; default: closed Sundays

TIME_SLOTS = [s.strip() for s in os.getenv(
    "TIME_SLOTS", "8:00 AM,9:30 AM,11:00 AM,1:00 PM,2:30 PM,4:00 PM,5:30 PM,7:00 PM"
).split(",") if s.strip()]

# Must match the service names on the website (static/js/main.js)
SERVICES = [
    "Custom Web Design & UI/UX Prototyping",
    "Full-Stack Website & Web App Development",
    "E-Commerce Store Development & Integration",
    "Website Redesign, Maintenance & Performance Optimization",
    "Search Engine Optimization (SEO) & Analytics Setup",
    "Full Package (Design to Launch)",
]

BUDGETS = ["", "Under $500", "$500 – $1,000", "$1,000 – $1,500", "$1,500+"]

# ---------- Google Sheets ----------
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "")
GOOGLE_SHEET_TAB = os.getenv("GOOGLE_SHEET_TAB", "Bookings")
# Either paste the whole service-account JSON into one env var (best for Render)…
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")
# …or point to the downloaded key file (easiest locally)
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "service-account.json")

# ---------- Email ----------
# EMAIL_PROVIDER = "smtp" (Gmail, Outlook, SendGrid SMTP, Brevo…) or "resend"
EMAIL_PROVIDER = os.getenv("EMAIL_PROVIDER", "smtp").lower()
EMAIL_FROM = os.getenv("EMAIL_FROM", "")  # e.g. "Meir Web Development <you@gmail.com>"
EMAIL_REPLY_TO = os.getenv("EMAIL_REPLY_TO", OWNER_EMAIL)

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")  # Gmail: a 16-character App Password
SMTP_USE_SSL = _bool("SMTP_USE_SSL", SMTP_PORT == 465)

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")

# ---------- App ----------
DEBUG = _bool("FLASK_DEBUG", False)
RATE_LIMIT_PER_HOUR = int(os.getenv("RATE_LIMIT_PER_HOUR", "5"))
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()]
