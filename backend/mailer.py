"""Confirmation email to the client + alert email to the owner.

Providers:
* smtp   — Gmail (App Password), Outlook, Zoho, SendGrid SMTP, Brevo… (default)
* resend — https://resend.com API key
If nothing is configured, emails are printed to the server log instead, so you
can test the whole flow locally before setting up a provider.
"""
from __future__ import annotations

import base64
import logging
import smtplib
import ssl
from datetime import datetime, timedelta
from email.message import EmailMessage
from email.utils import formataddr, make_msgid, parseaddr
from html import escape
from zoneinfo import ZoneInfo

from . import config

log = logging.getLogger(__name__)

# Brand palette: blue #003594 · yellow #FFB81C · white · navy #1B2A56 · gold #CDB87F (+ tints)
NAVY, BLUE, YELLOW, GOLD, MUTED, BORDER, CREAM = "#1b2a56", "#003594", "#ffb81c", "#cdb87f", "#5f6a89", "#e8e9ef", "#f5f0e5"


# ---------------------------------------------------------------- helpers
def meeting_start(date: str, time_str: str) -> datetime:
    """'2026-10-24' + '11:30 AM' → aware datetime in the business timezone."""
    naive = datetime.strptime(f"{date} {time_str}", "%Y-%m-%d %I:%M %p")
    return naive.replace(tzinfo=ZoneInfo(config.TIMEZONE))


def pretty_when(date: str, time_str: str) -> str:
    start = meeting_start(date, time_str)
    return f"{start.strftime('%A, %B')} {start.day}, {start.year} at {time_str} ({config.TIMEZONE_LABEL})"


def build_ics(b: dict) -> str:
    start = meeting_start(b["date"], b["time"]).astimezone(ZoneInfo("UTC"))
    end = start + timedelta(minutes=config.MEETING_LENGTH_MIN)
    fmt = "%Y%m%dT%H%M%SZ"

    def esc_ics(s: str) -> str:
        return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")

    organizer = config.OWNER_EMAIL or parseaddr(config.EMAIL_FROM)[1]
    lines = [
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Meir Web Development//Booking//EN",
        "CALSCALE:GREGORIAN", "METHOD:PUBLISH", "BEGIN:VEVENT",
        f"UID:{b['booking_id']}@meir",
        f"DTSTAMP:{datetime.now(ZoneInfo('UTC')).strftime(fmt)}",
        f"DTSTART:{start.strftime(fmt)}", f"DTEND:{end.strftime(fmt)}",
        f"SUMMARY:{esc_ics('Free consultation — ' + config.BUSINESS_NAME)}",
        f"DESCRIPTION:{esc_ics('Service: ' + b['service'] + chr(10) + 'Booking reference: ' + b['booking_id'] + chr(10) + 'A Google Meet, Zoom or WhatsApp call link will be emailed before the call.')}",
        "LOCATION:Google Meet / Zoom / WhatsApp (link to follow)",
    ]
    if organizer:
        lines.append(f"ORGANIZER;CN={esc_ics(config.BUSINESS_NAME)}:mailto:{organizer}")
    lines += ["STATUS:CONFIRMED", "BEGIN:VALARM", "TRIGGER:-PT30M", "ACTION:DISPLAY",
              "DESCRIPTION:Consultation in 30 minutes", "END:VALARM", "END:VEVENT", "END:VCALENDAR"]
    return "\r\n".join(lines) + "\r\n"


def _shell(title: str, body_html: str) -> str:
    return f"""<!doctype html><html><body style="margin:0;background:{CREAM};font-family:Arial,Helvetica,sans-serif;color:{NAVY}">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{CREAM};padding:32px 12px"><tr><td align="center">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;background:#fff;border:1px solid {BORDER};border-radius:16px;overflow:hidden">
<tr><td style="background:{BLUE};padding:24px 32px"><span style="font-size:22px;font-weight:700;color:#fff">meir</span><span style="font-size:22px;font-weight:700;color:{YELLOW}"> /</span>
<div style="font-family:'Courier New',monospace;font-size:12px;color:#c9d6f2;margin-top:4px">{escape(title)}</div></td></tr>
<tr><td style="height:4px;background:{GOLD};font-size:0;line-height:0">&nbsp;</td></tr>
<tr><td style="padding:32px">{body_html}</td></tr>
<tr><td style="padding:20px 32px;border-top:1px solid {BORDER};font-size:12px;color:{MUTED}">{escape(config.BUSINESS_NAME)} · Mon–Sat 8:00 AM – 8:00 PM (PHT)</td></tr>
</table></td></tr></table></body></html>"""


def _details_table(b: dict, include_contact: bool) -> str:
    rows = [("Reference", b["booking_id"]), ("When", pretty_when(b["date"], b["time"])), ("Service", b["service"])]
    if b["budget"]:
        rows.append(("Budget", b["budget"]))
    if include_contact:
        rows = [("Name", b["name"]), ("Email", b["email"]), ("Phone / Discord", b["phone"] or "—"),
                ("Client timezone", b["client_timezone"] or "—")] + rows
    cells = "".join(
        f'<tr><td style="padding:10px 0;border-bottom:1px solid {BORDER};color:{MUTED};font-size:13px;width:140px;vertical-align:top">{escape(k)}</td>'
        f'<td style="padding:10px 0;border-bottom:1px solid {BORDER};font-size:14px">{escape(v)}</td></tr>'
        for k, v in rows
    )
    return f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:20px 0">{cells}</table>'


def _details_box(b: dict) -> str:
    return (f'<div style="background:{CREAM};border-radius:12px;padding:16px;font-size:14px;line-height:1.6;white-space:pre-wrap">'
            f'{escape(b["details"])}</div>')


# ---------------------------------------------------------------- message builders
def client_email(b: dict) -> dict:
    first = b["name"].split()[0]
    when = pretty_when(b["date"], b["time"])
    html = _shell("booking confirmed", f"""
<h1 style="font-size:24px;margin:0 0 12px">You're booked, {escape(first)}!</h1>
<p style="font-size:15px;line-height:1.6;margin:0">Thanks for booking a free 30-minute consultation with {escape(config.BUSINESS_NAME)}.
We'll send your Google Meet, Zoom or WhatsApp call link before the call.</p>
{_details_table(b, include_contact=False)}
<p style="font-size:13px;color:{MUTED};margin:0 0 8px">What you told us:</p>{_details_box(b)}
<p style="font-size:15px;line-height:1.6;margin:24px 0 0"><b>Before the call</b>, it helps to gather any examples of websites you like, your logo or brand colours, and the content you already have.</p>
<p style="font-size:15px;line-height:1.6;margin:16px 0 0"><b>No payment is needed now.</b> After the call we'll send you a written quote, and only if you decide to proceed will we email the payment details (PayPal, Wise, or GCash / RCBC / MariBank / BDO via QR code).</p>
<p style="font-size:15px;line-height:1.6;margin:16px 0 0">Need to reschedule? Just reply to this email or message us on WhatsApp at +63 976 132 9770.</p>
<p style="font-size:15px;margin:24px 0 0">Talk soon,<br><b>{escape(config.BUSINESS_NAME)}</b></p>""")
    text = (f"Hi {first},\n\nYou're booked! Thanks for scheduling a free 30-minute consultation with {config.BUSINESS_NAME}.\n\n"
            f"Reference: {b['booking_id']}\nWhen: {when}\nService: {b['service']}\n"
            + (f"Budget: {b['budget']}\n" if b["budget"] else "")
            + f"\nWe'll send your Google Meet, Zoom or WhatsApp call link before the call.\n"
              f"No payment is needed now. After the call we'll send a written quote, and only if you decide to proceed will we email the payment details.\n"
              f"Need to reschedule? Reply to this email or message us on WhatsApp at +63 976 132 9770.\n\n"
              f"Talk soon,\n{config.BUSINESS_NAME}\n")
    return {
        "to": b["email"],
        "subject": f"Your consultation is confirmed — {when}",
        "html": html, "text": text,
        "reply_to": config.EMAIL_REPLY_TO,
        "attachment": ("consultation.ics", build_ics(b), "text/calendar"),
    }


def owner_email(b: dict, saved_to: str) -> dict:
    when = pretty_when(b["date"], b["time"])
    sheet_link = (f'<p style="margin:16px 0 0"><a href="https://docs.google.com/spreadsheets/d/{escape(config.GOOGLE_SHEET_ID)}" '
                  f'style="color:{BLUE}">Open the bookings sheet →</a></p>') if saved_to == "google_sheets" else ""
    warn = ("" if saved_to != "FAILED" else
            f'<p style="background:#fdecea;color:#c62828;padding:12px;border-radius:8px;font-size:14px">⚠ This booking could NOT be saved, so the client was NOT confirmed — they were asked to try again. Please contact them and book them in manually.</p>')
    html = _shell("new consultation booked", f"""
{warn}<h1 style="font-size:22px;margin:0 0 4px">New booking: {escape(b['name'])}</h1>
<p style="font-size:15px;color:{MUTED};margin:0">{escape(when)}</p>
{_details_table(b, include_contact=True)}
<p style="font-size:13px;color:{MUTED};margin:0 0 8px">Project details:</p>{_details_box(b)}
<p style="margin:24px 0 0"><a href="mailto:{escape(b['email'])}?subject={escape('Re: your consultation ' + b['booking_id'])}"
style="display:inline-block;background:{YELLOW};color:{NAVY};text-decoration:none;font-weight:700;padding:12px 20px;border-radius:12px">Reply to {escape(b['name'].split()[0])}</a></p>
{sheet_link}""")
    text = (f"New consultation booked\n\nName: {b['name']}\nEmail: {b['email']}\nPhone/Discord: {b['phone'] or '-'}\n"
            f"When: {when}\nService: {b['service']}\nBudget: {b['budget'] or '-'}\nClient timezone: {b['client_timezone'] or '-'}\n"
            f"Reference: {b['booking_id']}\n\nProject details:\n{b['details']}\n")
    return {
        "to": config.OWNER_EMAIL,
        "subject": (f"⚠ Booking NOT saved — contact {b['name']} ({b['date']} {b['time']})" if saved_to == "FAILED"
                    else f"🗓 New consultation: {b['name']} — {b['service']} — {b['date']} {b['time']}"),
        "html": html, "text": text,
        "reply_to": b["email"],  # hitting Reply answers the client directly
        "attachment": ("consultation.ics", build_ics(b), "text/calendar"),
    }


# ---------------------------------------------------------------- transports
def provider() -> str:
    if config.EMAIL_PROVIDER == "resend" and config.RESEND_API_KEY and config.EMAIL_FROM:
        return "resend"
    if config.EMAIL_PROVIDER == "smtp" and config.SMTP_USER and config.SMTP_PASSWORD:
        return "smtp"
    return "console"


def _from_header() -> str:
    if config.EMAIL_FROM:
        return config.EMAIL_FROM
    return formataddr((config.BUSINESS_NAME, config.SMTP_USER))


def _send_smtp(msg: dict) -> None:
    em = EmailMessage()
    em["From"] = _from_header()
    em["To"] = msg["to"]
    em["Subject"] = msg["subject"]
    if msg.get("reply_to"):
        em["Reply-To"] = msg["reply_to"]
    em["Message-ID"] = make_msgid(domain=(parseaddr(_from_header())[1].split("@")[-1] or "meir.local"))
    em.set_content(msg["text"])
    em.add_alternative(msg["html"], subtype="html")
    if msg.get("attachment"):
        name, content, mime = msg["attachment"]
        maintype, subtype = mime.split("/")
        em.add_attachment(content.encode("utf-8"), maintype=maintype, subtype=subtype, filename=name)

    ctx = ssl.create_default_context()
    if config.SMTP_USE_SSL:
        with smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT, context=ctx, timeout=20) as s:
            s.login(config.SMTP_USER, config.SMTP_PASSWORD)
            s.send_message(em)
    else:
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=20) as s:
            s.starttls(context=ctx)
            s.login(config.SMTP_USER, config.SMTP_PASSWORD)
            s.send_message(em)


def _send_resend(msg: dict) -> None:
    import requests

    payload = {"from": config.EMAIL_FROM, "to": [msg["to"]], "subject": msg["subject"],
               "html": msg["html"], "text": msg["text"]}
    if msg.get("reply_to"):
        payload["reply_to"] = msg["reply_to"]
    if msg.get("attachment"):
        name, content, _ = msg["attachment"]
        payload["attachments"] = [{"filename": name, "content": base64.b64encode(content.encode()).decode()}]
    r = requests.post("https://api.resend.com/emails", json=payload,
                      headers={"Authorization": f"Bearer {config.RESEND_API_KEY}"}, timeout=20)
    if r.status_code >= 300:
        raise RuntimeError(f"Resend error {r.status_code}: {r.text[:300]}")


def send(msg: dict) -> bool:
    """Send one message. Returns True on success; never raises."""
    if not msg.get("to"):
        log.warning("Email skipped (no recipient): %s", msg["subject"])
        return False
    p = provider()
    try:
        if p == "smtp":
            _send_smtp(msg)
        elif p == "resend":
            _send_resend(msg)
        else:
            log.warning("\n──── EMAIL (no provider configured — printing instead) ────\nTo: %s\nSubject: %s\n\n%s────────────",
                        msg["to"], msg["subject"], msg["text"])
            return True  # treated as success in local dev so the flow can be tested
        log.info("Email sent via %s to %s", p, msg["to"])
        return True
    except Exception:  # noqa: BLE001 — log and carry on; a failed email must not lose the booking
        log.exception("Email to %s failed via %s", msg["to"], p)
        return False
