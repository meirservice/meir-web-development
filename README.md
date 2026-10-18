# Meir Web Development Services — website + booking backend

A responsive agency website built from the Meir Figma design, with a **Python (Flask)** backend that:

1. saves every consultation booking as a new row in **Google Sheets**,
2. emails the client an **instant confirmation** (with a calendar invite `.ics`),
3. emails **you** an alert with all the details (hit *Reply* to answer the client directly),
4. makes every date + time **bookable only once** — taken slots show as "Booked" on the calendar, fully booked days are crossed out, and the page re-checks availability every 20 seconds while it's open.

Pages: **`/`** (home) and **`/consultation`** (the booking page — every "Book" button on the home page links here, and pricing/service buttons pre-fill the service and budget).

It runs out of the box: until you add Google and email credentials, bookings are saved to `data/bookings.csv` and emails are printed in the terminal, so you can test everything first.

```
meir/
├── app.py                 # Flask app: routes, validation, booking flow
├── backend/
│   ├── config.py          # all settings (read from .env)
│   ├── storage.py         # Google Sheets (or CSV fallback) + one-booking-per-slot lock
│   └── mailer.py          # client + owner emails, .ics invite (SMTP or Resend)
├── static/
│   ├── index.html         # home page
│   ├── consultation.html  # booking page (/consultation)
│   ├── css/styles.css     # styles (tokens from Figma)
│   ├── js/main.js         # services, calendar, form, FAQ, case studies
│   └── img/               # put the 3 case-study images here (see step 6)
├── requirements.txt
├── .env.example           # copy to .env
├── render.yaml / Procfile # deployment
└── data/                  # local CSV fallback
```

---

## 1. Run it locally (5 minutes)

You need **Python 3.10+**.

```bash
cd meir
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # Windows: copy .env.example .env
python app.py
```

Open **http://localhost:5000** and click **Book Consultation** (or go straight to **http://localhost:5000/consultation**), pick a date and time, and submit the form. You'll see the booking in `data/bookings.csv` and both emails printed in the terminal.

Check what's connected any time at **http://localhost:5000/healthz** — it shows `storage` (`local_csv` or `google_sheets`) and `email` (`console`, `smtp` or `resend`).

---

## 2. Connect Google Sheets

The backend logs in to Google as a **service account** (a robot Google user) and writes to a sheet you share with it.

### 2a. Create the sheet
1. Go to [sheets.new](https://sheets.new) and name it e.g. **Meir — Consultations**.
2. Copy the sheet ID from the URL — the long part between `/d/` and `/edit`:
   `https://docs.google.com/spreadsheets/d/`**`1AbCdEf...xyz`**`/edit`

You don't need to add headers — the app creates a **Bookings** tab with a bold, frozen header row on the first booking.

### 2b. Create a service account
1. Open [console.cloud.google.com](https://console.cloud.google.com) → create a project (e.g. *meir-website*).
2. **APIs & Services → Library** → search **Google Sheets API** → **Enable**.
3. **APIs & Services → Credentials → Create credentials → Service account**. Give it a name (e.g. *meir-bookings*) → **Done** (no roles needed).
4. Click the new service account → **Keys → Add key → Create new key → JSON**. A `.json` file downloads.
5. Rename it to **`service-account.json`** and put it in the `meir/` folder next to `app.py`. (It's already in `.gitignore` — never commit it.)

### 2c. Share the sheet with the robot
Open the JSON file, copy the `client_email` (looks like `meir-bookings@meir-website.iam.gserviceaccount.com`), then in your sheet click **Share**, paste it, give **Editor** access, untick "Notify", and share.

### 2d. Add to `.env`
```env
GOOGLE_SHEET_ID=1AbCdEf...xyz
GOOGLE_SHEET_TAB=Bookings
GOOGLE_SERVICE_ACCOUNT_FILE=service-account.json
```
Restart `python app.py`. `/healthz` should now say `"storage": "google_sheets"`.

**Columns written:** Submitted At · Booking ID · Status · Full Name · Email · Phone / Discord · Service · Budget · Preferred Date · Preferred Time · Business Timezone · Client Timezone · Project Details

> **Tip — cancelling:** change a row's **Status** to `Cancelled` and that time slot becomes bookable again on the website (within ~30 seconds).

---

## 3. Connect email

### Option A — Gmail (free, easiest)
Gmail needs an **App Password** (your normal password won't work):

1. Turn on **2-Step Verification**: [myaccount.google.com/security](https://myaccount.google.com/security).
2. Create an app password: [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) → name it *Meir website* → copy the 16-character code.
3. In `.env`:
```env
OWNER_EMAIL=you@gmail.com
EMAIL_PROVIDER=smtp
EMAIL_FROM=Meir Web Development <you@gmail.com>
EMAIL_REPLY_TO=you@gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=you@gmail.com
SMTP_PASSWORD=abcdefghijklmnop
```
Gmail's free limit (~500 emails/day) is plenty for bookings.

### Option B — Resend (best once you have your own domain)
1. Sign up at [resend.com](https://resend.com), add and verify your domain (e.g. `meir.studio`).
2. Create an API key.
3. In `.env`:
```env
EMAIL_PROVIDER=resend
RESEND_API_KEY=re_xxxxxxxx
EMAIL_FROM=Meir Web Development <hello@meir.studio>
OWNER_EMAIL=you@gmail.com
```

### Option C — any other SMTP (SendGrid, Brevo, Outlook, Zoho…)
Use `EMAIL_PROVIDER=smtp` with that provider's host, port, user and password. For SendGrid: `SMTP_HOST=smtp.sendgrid.net`, `SMTP_USER=apikey`, `SMTP_PASSWORD=<your API key>`.

Restart, submit a test booking with your own email — you should get the confirmation, and `OWNER_EMAIL` gets the alert.

---

## 4. Deploy (Render — free tier)

The Flask app serves both the website and the API, so it's a single deploy.

1. Push the `meir/` folder to a **GitHub** repo (the `.gitignore` keeps `.env` and `service-account.json` out).
2. On [render.com](https://render.com): **New + → Blueprint** → choose the repo. It reads `render.yaml`.
   *(Or **New + → Web Service**: Build `pip install -r requirements.txt`, Start `gunicorn app:app --workers 2 --threads 4 --timeout 60`.)*
3. Fill in the environment variables Render asks for (same values as your `.env`). For Google, use **`GOOGLE_SERVICE_ACCOUNT_JSON`** instead of the file — paste the **entire contents** of `service-account.json` as the value.
4. Deploy, then open `https://your-app.onrender.com/healthz` to confirm `google_sheets` and `smtp`.
5. **Custom domain:** Render → your service → Settings → Custom Domains → add `meir.studio` and follow the DNS steps.

> The free Render plan sleeps after 15 minutes idle, so the first visit can take ~30 seconds. The $7/month plan stays awake.

**Other hosts:** [Railway](https://railway.app) and [Fly.io](https://fly.io) work the same way using the `Procfile`. PythonAnywhere also works (point the WSGI file at `app:app`).

---

## 5. Customise

| What | Where |
|---|---|
| Time slots, closed days, hours, booking window, timezone | `.env` (`TIME_SLOTS`, `CLOSED_WEEKDAYS`, `OPEN_HOUR`, `CLOSE_HOUR`, `BOOKING_WINDOW_DAYS`, `BUSINESS_TIMEZONE`) |
| Services in the dropdown | `SERVICES` in `backend/config.py` **and** the cards in `static/js/main.js` (names must match) |
| Service card text, tech stack, deliverables | `SERVICES` array in `static/js/main.js` |
| Process steps, case studies, FAQs | `STEPS`, `CASES`, `FAQS` in `static/js/main.js` |
| Prices, testimonials, contact details, socials | `static/index.html` |
| Colours & fonts | `:root` tokens at the top of `static/css/styles.css` — the five palette colours (`--blue #003594`, `--yellow #FFB81C`, `--white`, `--navy #1B2A56`, `--gold #CDB87F`) plus tints made from them |
| Booking page text | `static/consultation.html` |
| Email wording | `client_email()` / `owner_email()` in `backend/mailer.py` |

---

## 6. Case-study images

The three project images live in your Figma file. Export them and the site picks them up automatically (a matching gradient shows until then):

1. In Figma, select each image inside **Project Card / 1, 2, 3** → right panel **Export → PNG** (2×).
2. Save them as `static/img/bloom-cafe.png`, `static/img/northline.png`, `static/img/taskflow.png`.

---

## How a booking flows

```
/consultation ──POST /api/book──▶ Flask
                                  ├─ validate (fields, real date, open day, slot exists, ≥1h notice)
                                  ├─ 🔒 lock → fresh check slot is free → append row ──▶ Google Sheet (or CSV)
                                  │          → re-check sheet (earliest booking wins) → unlock
                                  │          └─ taken? → 409 "someone has just booked that time"
                                  ├─ owner alert email (background)
                                  └─ client confirmation email + .ics
         ◀── { ok, booking_id, email_sent } ──
```

### How "one booking per time slot" is guaranteed

1. **On the page** — booked times show as *Booked* and can't be clicked; days with no free times are crossed out. The page re-checks every 20 seconds and whenever the tab is reopened, so if someone else takes the time you were looking at, you're told straight away.
2. **On the server** — the check and the save happen inside a lock (`data/.booking.lock`), reading the sheet fresh each time, so two people pressing *Book* at the same instant can't both get the slot. The second person gets "Sorry — someone has just booked that time" and the time turns to *Booked*. (Tested: 30 simultaneous requests for one slot across 4 server workers → exactly 1 booking.)
3. **In Google Sheets** — after saving, the sheet is checked again. If a second row for the same date + time exists (another server instance, or a row typed in by hand), the earliest booking keeps the slot and the later row is removed.
4. **Cancelling** — set a row's **Status** to `Cancelled` and that slot opens up again on the website.

If the sheet can't be reached, the booking is **not** confirmed (so a slot is never promised twice); the visitor is asked to retry or WhatsApp you, and you still get an alert email with their details.

**Other protections:** server-side validation, a hidden honeypot field for bots, rate limiting (5 bookings/hour per IP by default), size limits, and sheet writes stored as plain text so nothing a visitor types can run as a spreadsheet formula.

## API

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/config` | services, time slots, timezone, closed days |
| GET | `/api/slots?date=YYYY-MM-DD` | times already booked that day |
| GET | `/api/availability?month=YYYY-MM` | booked times for every day in a month |
| POST | `/api/book` | create a booking (JSON: `name, email, phone, service, budget, date, time, details`) |
| GET | `/healthz` | which storage + email provider are active |

## Troubleshooting

- **`SpreadsheetNotFound` / 403 in the log** — the sheet isn't shared with the service account's `client_email`, or `GOOGLE_SHEET_ID` is wrong.
- **`Google Sheets API has not been used in project…`** — enable the Sheets API (step 2b-2) and wait a minute.
- **`SMTPAuthenticationError` (535)** — use a Gmail **App Password**, not your login password; 2-Step Verification must be on.
- **Emails land in spam** — normal at first with Gmail. Ask yourself to mark one "Not spam", or switch to Resend with your own verified domain.
- **Times look wrong** — slots are in `BUSINESS_TIMEZONE`; the client's own timezone is recorded in the sheet and the calendar invite converts automatically.
