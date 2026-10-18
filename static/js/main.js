/* =========================================================
   Meir Web Development Services — front-end behaviour
   ========================================================= */
(() => {
  "use strict";

  // ---------- Content ----------
  // Service names must match SERVICES in backend/config.py — the booking API
  // only accepts these values. The dropdown is filled from /api/config, so the
  // backend stays the single source of truth.
  const SERVICES = [
    {
      name: "Custom Web Design & UI/UX Prototyping",
      icon: "layout",
      desc: "Wireframes, clickable prototypes and design systems built around how your customers actually use your site.",
      stack: ["Figma", "FigJam", "Design tokens", "WCAG 2.2"],
      deliverables: ["User flows & sitemap", "Wireframes + hi-fi mockups", "Interactive prototype", "Component library & style guide"],
      time: "1–2 weeks",
    },
    {
      name: "Full-Stack Website & Web App Development",
      icon: "code",
      desc: "Fast, responsive websites and custom web apps — from marketing sites with a CMS to dashboards with logins and databases.",
      stack: ["HTML/CSS/JS", "React / Next.js", "Python · Flask", "PostgreSQL", "REST APIs"],
      deliverables: ["Responsive multi-page build", "CMS or admin panel", "Auth, forms & integrations", "Repo access + deployment"],
      time: "2–6 weeks",
    },
    {
      name: "E-Commerce Store Development & Integration",
      icon: "cart",
      desc: "Online stores with product catalogues, cart, checkout and payments — on Shopify, WooCommerce or a custom stack.",
      stack: ["Shopify", "WooCommerce", "Stripe", "PayPal", "GCash / Maya"],
      deliverables: ["Store setup & theme", "Product import", "Payment & shipping config", "Order-flow testing"],
      time: "4–6 weeks",
    },
    {
      name: "Website Redesign, Maintenance & Performance Optimization",
      icon: "refresh",
      desc: "Modernise an existing site, keep it updated and secure, and make it load fast on every device.",
      stack: ["Lighthouse", "Core Web Vitals", "CDN & caching", "Uptime monitoring"],
      deliverables: ["UX & performance audit", "Redesign or refactor", "Monthly updates & backups", "Speed report before/after"],
      time: "1–4 weeks · monthly plans",
    },
    {
      name: "Search Engine Optimization (SEO) & Analytics Setup",
      icon: "trending",
      desc: "Get found on Google and understand what visitors do — technical SEO, on-page content and clean tracking.",
      stack: ["Google Search Console", "GA4", "Tag Manager", "Schema.org"],
      deliverables: ["Technical SEO audit & fixes", "Keyword & meta optimisation", "GA4 + conversion tracking", "Monthly insight report"],
      time: "1–2 weeks · ongoing",
    },
    {
      name: "Full Package (Design to Launch)",
      icon: "layers",
      wide: true,
      desc: "Complete collaboration from branding and UI/UX to development, launch, SEO setup and full documentation — one team, one timeline.",
      stack: ["Brand identity", "UI/UX", "Full-stack build", "SEO & analytics", "Hosting & domain"],
      deliverables: ["Logo & brand guide", "Designed + developed website", "Launch & analytics setup", "User manual + training session", "30 days of support"],
      time: "Custom",
    },
  ];

  const STEPS = [
    ["Discovery call", "Understand goals, audience, and budget.", "Day 1"],
    ["Research and planning", "Competitor review, sitemap, project scope.", "2–3 days"],
    ["Wireframes", "Layout structure for approval.", "3–5 days"],
    ["UI design", "High-fidelity visuals in the brand style.", "1–2 weeks"],
    ["Development", "Responsive build, testing on all devices.", "1–3 weeks"],
    ["Launch", "Deployment, domain setup, final checks.", "1–2 days"],
    ["Documentation and handover", "User guide, design files, credentials, training session.", "Handover"],
    ["Support", "30 days of free fixes after launch.", "30 days"],
  ];

  const CASES = {
    bloom: {
      title: "Bloom Café — Branding & Landing Page",
      intro: "A modern cafe in the heart of the city needed a digital presence that matched their high-end coffee experience.",
      challenge: "Create a brand identity that feels premium, modern, and approachable.",
      approach: "We focused on clean typography and a muted color palette with a pop of coral for highlights.",
      deliverables: "• Brand guide • Logo files • Landing page design • Development • Deployment",
      results: "A fast, mobile-first page designed to turn visitors into online orders and walk-in customers.",
      timeline: [["Day 1", "Discovery"], ["Day 3", "Wireframes"], ["Day 7", "Launch"]],
    },
    northline: {
      title: "Northline Apparel — E-commerce Store",
      intro: "A growing streetwear label was selling through social DMs and needed a proper store that could handle drops.",
      challenge: "Replace manual order-taking with a store that handles inventory, sizes and payments without slowing down on launch days.",
      approach: "A product-first layout with quick size selection, a two-step checkout and local payment options alongside cards.",
      deliverables: "• Store design • Product catalogue setup • Payment & shipping integration • Admin training • Documentation",
      results: "A store built to handle product drops and payments without manual order-taking.",
      timeline: [["Week 1", "Discovery & catalogue"], ["Week 3", "Store build"], ["Week 5", "Launch"]],
    },
    taskflow: {
      title: "TaskFlow App — Interface Design (UI/UX)",
      intro: "A productivity start-up needed a clear, focused interface for its task and analytics dashboard before development began.",
      challenge: "Present dense project data without overwhelming users on a small mobile screen.",
      approach: "We mapped the core flows, then designed a dark interface with strong hierarchy, glanceable charts and a reusable component library.",
      deliverables: "• User flows • Wireframes • Hi-fi mobile screens • Clickable prototype • Design system",
      results: "A reusable design system a development team can build from directly, with minimal back-and-forth.",
      timeline: [["Day 1", "Discovery"], ["Week 1", "Wireframes & flows"], ["Week 2", "Hi-fi + prototype"]],
    },
  };

  const FAQS = [
    ["How long does a project take?", "Projects range from 3–7 days for a logo to 4–6 weeks for an e-commerce store. I’ll confirm your scope and schedule during our discovery call."],
    ["How much does a website cost?", "Our packages start at $499 for a one-page starter website, $999 for a full business website, and $1,499 for an online store. You get a fixed quote after the free consultation, with no surprise fees."],
    ["What do I need to prepare before we start?", "Your goals, any existing logo or brand colours, examples of websites you like, and the content you already have (text, photos, product lists). Don’t worry if it’s incomplete — we’ll fill the gaps together."],
    ["Do you provide documentation after the project?", "Yes. Every project ends with a handover: a website user manual, source design files, code repository access, login credentials and a short training session."],
    ["Can you redesign my existing website?", "Absolutely. We start with a UX and performance audit, keep what works (and your SEO rankings), and rebuild what doesn’t."],
    ["Do you offer support after launch?", "Every project includes 30 days of free fixes after launch. After that, optional monthly maintenance plans cover updates, backups, security and small changes."],
    ["What payment methods do you accept?", "PayPal and Wise for international clients, plus GCash, RCBC, MariBank and BDO (QR code) for clients in the Philippines. Booking and the consultation are free. We only send payment details after you confirm you want to proceed, and projects are usually split 50% deposit and 50% before launch."],
    ["How can I contact you?", "Message us on WhatsApp at +63 976 132 9770, email meirwebdevelopment@gmail.com, or reach us on Facebook. We’re available Monday to Saturday, 8 AM to 8 PM Philippine time (UTC+8)."],
  ];

  const ICONS = {
    layout: '<rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/>',
    code: '<polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>',
    cart: '<circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>',
    refresh: '<polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>',
    trending: '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>',
    layers: '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>',
  };
  const icon = (name) =>
    `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONS[name] || ""}</svg>`;


  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const PAGE = document.body.dataset.page; // "home" | "consultation"

  // Defaults; overridden by /api/config
  let CONFIG = {
    services: SERVICES.map((s) => s.name),
    time_slots: ["8:00 AM", "9:30 AM", "11:00 AM", "1:00 PM", "2:30 PM", "4:00 PM", "5:30 PM", "7:00 PM"],
    timezone: "Asia/Manila",
    timezone_label: "Philippine Time, UTC+8",
    closed_weekdays: [6], // Python weekday numbers: Monday=0 … Sunday=6 (closed Sundays)
    booking_window_days: 60,
    open_hour: 8,
    close_hour: 20,
  };

  async function loadConfig() {
    try {
      const r = await fetch("/api/config", { cache: "no-store" });
      if (r.ok) CONFIG = { ...CONFIG, ...(await r.json()) };
    } catch { /* static preview: keep defaults */ }
  }

  // =========================================================
  // Shared: navigation + open/closed status
  // =========================================================
  function initNav() {
    const nav = $(".nav");
    const toggle = $(".nav__toggle");
    const links = $("#nav-links");
    const close = () => { links.classList.remove("is-open"); toggle.setAttribute("aria-expanded", "false"); };
    toggle.addEventListener("click", () => {
      const open = links.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(open));
    });
    links.addEventListener("click", (e) => { if (e.target.closest("a")) close(); });
    const onScroll = () => nav.classList.toggle("is-scrolled", window.scrollY > 8);
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();

    if (PAGE !== "home") return;
    const map = new Map($$('.nav__links a[href^="#"]:not(.btn)').map((a) => [a.getAttribute("href").slice(1), a]));
    const io = new IntersectionObserver(
      (entries) => entries.forEach((en) => {
        if (en.isIntersecting && map.has(en.target.id)) {
          map.forEach((a) => a.classList.remove("is-active"));
          map.get(en.target.id).classList.add("is-active");
        }
      }),
      { rootMargin: "-45% 0px -50% 0px" }
    );
    map.forEach((_, id) => { const s = document.getElementById(id); if (s) io.observe(s); });
  }

  function businessNow() {
    // {weekday (Mon=0), hour, minute, dateISO} in the business timezone
    const parts = Object.fromEntries(
      new Intl.DateTimeFormat("en-US", {
        timeZone: CONFIG.timezone, weekday: "short", year: "numeric", month: "2-digit", day: "2-digit",
        hour: "numeric", minute: "2-digit", hourCycle: "h23",
      }).formatToParts(new Date()).map((p) => [p.type, p.value])
    );
    return {
      weekday: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].indexOf(parts.weekday),
      hour: parseInt(parts.hour, 10),
      minute: parseInt(parts.minute, 10),
      dateISO: `${parts.year}-${parts.month}-${parts.day}`,
    };
  }

  function updateOpenStatus() {
    const { weekday, hour } = businessNow();
    const open = !CONFIG.closed_weekdays.includes(weekday) && hour >= CONFIG.open_hour && hour < CONFIG.close_hour;
    $$("[data-open-status]").forEach((el) => (el.textContent = open ? "Open now" : "Closed now"));
    $$("[data-open-badge]").forEach((el) => {
      el.textContent = open ? "OPEN NOW" : "CLOSED NOW";
      el.classList.toggle("is-closed", !open);
    });
  }

  // =========================================================
  // Home page
  // =========================================================
  function renderIcons() {
    $$("[data-icon]").forEach((el) => (el.innerHTML = icon(el.dataset.icon)));
  }

  const bookingLink = (service, budget) => {
    const q = new URLSearchParams();
    if (service) q.set("service", service);
    if (budget) q.set("budget", budget);
    return `/consultation${q.toString() ? "?" + q : ""}`;
  };

  function renderServices() {
    const grid = $("#services-grid");
    if (!grid) return;
    grid.innerHTML = SERVICES.map(
      (s, i) => `
      <article class="service${s.wide ? " service--wide" : ""}" id="service-${i}">
        <span class="icon-tile">${icon(s.icon)}</span>
        <div>
          <h3>${esc(s.name)}</h3>
          <p class="service__desc">${esc(s.desc)}</p>
        </div>
        <div class="service__more" id="service-more-${i}">
          <div><p class="service__label">Tech stack</p><div class="chips">${s.stack.map((t) => `<span class="chip">${esc(t)}</span>`).join("")}</div></div>
          <div><p class="service__label">Deliverables</p><ul class="service__list">${s.deliverables.map((d) => `<li>${esc(d)}</li>`).join("")}</ul></div>
          <a href="${bookingLink(s.name)}" class="btn btn--primary service__book">Book this service</a>
        </div>
        <div class="service__foot">
          <span class="mono${s.wide ? "" : " mono--blue"}">${esc(s.time)}</span>
          <button type="button" class="link-btn" aria-expanded="false" aria-controls="service-more-${i}">Learn more</button>
        </div>
      </article>`
    ).join("");

    grid.addEventListener("click", (e) => {
      const btn = e.target.closest(".link-btn");
      if (!btn) return;
      const card = btn.closest(".service");
      const open = card.classList.toggle("is-open");
      btn.setAttribute("aria-expanded", String(open));
      btn.textContent = open ? "Show less" : "Learn more";
    });
  }

  function renderTimeline() {
    const el = $("#timeline");
    if (!el) return;
    el.innerHTML = STEPS.map(
      ([title, text, tag], i) => `
      <li class="step">
        <div class="step__head"><span class="step__num">${String(i + 1).padStart(2, "0")}</span><h3>${esc(title)}</h3></div>
        <p>${esc(text)}</p>
        <span class="tag">${esc(tag)}</span>
      </li>`
    ).join("");
  }

  function renderCase(key) {
    const c = CASES[key];
    $("#case-study").innerHTML = `
      <h3>${esc(c.title)}</h3>
      <p class="case__intro">${esc(c.intro)}</p>
      <div class="case__grid">
        <div><h4>The challenge</h4><p>${esc(c.challenge)}</p></div>
        <div><h4>Deliverables</h4><p>${esc(c.deliverables)}</p></div>
        <div><h4>Our approach</h4><p>${esc(c.approach)}</p></div>
        <div><h4>Goal</h4><p>${esc(c.results)}</p></div>
        <div><h4>Process timeline</h4><div class="case__timeline">${c.timeline.map(([d, t]) => `<div><span>${esc(d)}</span> <span>${esc(t)}</span></div>`).join("")}</div></div>
      </div>`;
    $$("[data-case]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.case === key)));
  }

  function initWork() {
    if (!$("#case-study")) return;
    renderCase("bloom");
    $$("[data-case]").forEach((b) =>
      b.addEventListener("click", () => {
        renderCase(b.dataset.case);
        $("#case-study").scrollIntoView({ behavior: "smooth", block: "nearest" });
      })
    );
    // Load exported Figma images if present; otherwise keep the palette gradient
    $$("[data-img]").forEach((el) => {
      const img = new Image();
      img.onload = () => {
        el.style.setProperty("--img", `url("${el.dataset.img}")`);
        el.classList.add("has-img");
      };
      img.src = el.dataset.img;
    });
  }

  function renderFaqs() {
    const list = $("#faq-list");
    if (!list) return;
    const chevron = '<span class="faq__icon" aria-hidden="true"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg></span>';
    list.innerHTML = FAQS.map(
      ([q, a], i) => `
      <div class="faq${i === 0 ? " is-open" : ""}">
        <button type="button" class="faq__q" aria-expanded="${i === 0}" aria-controls="faq-${i}"><span>${esc(q)}</span>${chevron}</button>
        <div class="faq__a" id="faq-${i}" role="region"><div><p>${esc(a)}</p></div></div>
      </div>`
    ).join("");
    list.addEventListener("click", (e) => {
      const btn = e.target.closest(".faq__q");
      if (!btn) return;
      const item = btn.parentElement;
      const open = item.classList.toggle("is-open");
      btn.setAttribute("aria-expanded", String(open));
    });
  }

  // =========================================================
  // Consultation page — calendar, live availability, form
  // =========================================================
  const REFRESH_MS = 20_000; // re-check availability while the page is open
  const state = {
    viewYear: 0, viewMonth: 0,
    date: null, time: null,
    months: {},          // "YYYY-MM" → { taken: { "YYYY-MM-DD": ["9:30 AM", …] }, at }
  };
  const DOW = ["M", "T", "W", "T", "F", "S", "S"];
  const pad = (n) => String(n).padStart(2, "0");
  const iso = (y, m, d) => `${y}-${pad(m + 1)}-${pad(d)}`;
  const ymOf = (isoDate) => isoDate.slice(0, 7);
  const parseISO = (s) => { const [y, m, d] = s.split("-").map(Number); return new Date(y, m - 1, d); };
  const todayInBiz = () => parseISO(businessNow().dateISO);
  const fmtLong = (s) => parseISO(s).toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric", year: "numeric" });
  const fmtShort = (s) => parseISO(s).toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric", year: "numeric" });

  const slotMinutes = (slot) => {
    const [, h, m, ap] = slot.match(/(\d+):(\d+)\s*(AM|PM)/i);
    return ((parseInt(h, 10) % 12) + (ap.toUpperCase() === "PM" ? 12 : 0)) * 60 + parseInt(m, 10);
  };
  function slotIsPast(date, slot) {
    // Same rule as the server: at least 1 hour's notice, in the business timezone
    const now = businessNow();
    if (date < now.dateISO) return true;
    if (date > now.dateISO) return false;
    return slotMinutes(slot) < now.hour * 60 + now.minute + 60;
  }
  const takenFor = (date) => (state.months[ymOf(date)]?.taken?.[date]) || [];

  async function loadMonth(ym, force = false) {
    const cached = state.months[ym];
    if (cached && !force && Date.now() - cached.at < REFRESH_MS) return cached;
    try {
      const r = await fetch(`/api/availability?month=${ym}`, { cache: "no-store" });
      if (!r.ok) throw new Error();
      const data = await r.json();
      state.months[ym] = { taken: data.taken || {}, at: Date.now() };
    } catch {
      state.months[ym] = state.months[ym] || { taken: {}, at: 0 }; // offline: the server still validates on submit
    }
    return state.months[ym];
  }

  function dayState(date) {
    const taken = takenFor(date);
    const free = CONFIG.time_slots.filter((t) => !taken.includes(t) && !slotIsPast(date, t));
    return { full: free.length === 0, some: taken.length > 0 };
  }

  function renderCalendar() {
    const today = todayInBiz();
    const maxDate = new Date(today); maxDate.setDate(maxDate.getDate() + CONFIG.booking_window_days);
    const { viewYear: y, viewMonth: m } = state;
    const first = new Date(y, m, 1);
    const daysInMonth = new Date(y, m + 1, 0).getDate();
    const lead = (first.getDay() + 6) % 7; // Monday-first

    $("#cal-month").textContent = first.toLocaleDateString("en-US", { month: "long", year: "numeric" });
    $("#cal-prev").disabled = y === today.getFullYear() && m === today.getMonth();
    $("#cal-next").disabled = new Date(y, m + 1, 1) > maxDate;

    let html = DOW.map((d) => `<div class="calendar__dow" aria-hidden="true">${d}</div>`).join("");
    for (let i = 0; i < lead; i++) html += "<div></div>";
    for (let d = 1; d <= daysInMonth; d++) {
      const date = new Date(y, m, d);
      const id = iso(y, m, d);
      const pyWeekday = (date.getDay() + 6) % 7;
      const outOfRange = date < today || date > maxDate || CONFIG.closed_weekdays.includes(pyWeekday);
      const st = outOfRange ? { full: false, some: false } : dayState(id);
      const disabled = outOfRange || st.full;
      const cls = ["calendar__day",
        id === state.date ? "is-selected" : "",
        +date === +today ? "is-today" : "",
        !outOfRange && st.full ? "is-full" : "",
        !disabled && st.some ? "has-bookings" : ""].join(" ").trim();
      const label = `${fmtLong(id)}${st.full && !outOfRange ? " — fully booked" : outOfRange ? " — unavailable" : st.some ? " — some times booked" : ""}`;
      html += `<button type="button" class="${cls}" data-date="${id}" ${disabled ? "disabled" : ""} aria-label="${label}" aria-pressed="${id === state.date}" title="${st.full && !outOfRange ? "Fully booked" : ""}">${d}</button>`;
    }
    $("#cal-grid").innerHTML = html;
  }

  function renderSlots() {
    const wrap = $("#slots");
    if (!state.date) {
      $("#slots-date").textContent = "Pick a date first";
      wrap.innerHTML = '<p class="slots__empty">Select a date on the calendar to see available times.</p>';
      return;
    }
    $("#slots-date").textContent = fmtLong(state.date);
    const taken = takenFor(state.date);
    wrap.innerHTML = CONFIG.time_slots.map((t) => {
      const booked = taken.includes(t);
      const past = !booked && slotIsPast(state.date, t);
      const sel = t === state.time;
      const sub = booked ? "Booked" : past ? "Unavailable" : sel ? "Selected" : "Available";
      return `<button type="button" class="slot${sel ? " is-selected" : ""}${booked ? " is-booked" : ""}" role="radio"
        aria-checked="${sel}" data-time="${t}" ${booked || past ? "disabled" : ""}
        aria-label="${t}${booked ? ", already booked" : past ? ", unavailable" : ""}">${t}<small>${sub}</small></button>`;
    }).join("");
  }

  function notice(msg, type = "info") {
    const el = $("#slot-notice");
    if (!msg) { el.innerHTML = ""; return; }
    el.innerHTML = `<div class="notice${type === "error" ? " notice--error" : ""}" role="status">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
      <span>${esc(msg)}</span></div>`;
  }

  function syncSummary() {
    $("#date").value = state.date || "";
    $("#time").value = state.time || "";
    const set = (id, val, empty = "Not selected") => {
      const el = $(id);
      el.textContent = val || empty;
      el.classList.toggle("is-empty", !val);
    };
    set("#sum-date", state.date ? fmtLong(state.date) : "");
    set("#sum-time", state.time ? `${state.time} (${CONFIG.timezone_label})` : "");
    set("#sum-service", $("#service").value);
    $("#step-date").classList.toggle("is-done", !!state.date);
    $("#step-time").classList.toggle("is-done", !!state.time);
    if (state.date && state.time) clearError("date");
  }

  // Re-check availability; if someone else took the selected slot, tell the visitor
  async function refreshAvailability() {
    const yms = new Set([iso(state.viewYear, state.viewMonth, 1).slice(0, 7)]);
    if (state.date) yms.add(ymOf(state.date));
    await Promise.all([...yms].map((ym) => loadMonth(ym, true)));
    if (state.date && state.time && takenFor(state.date).includes(state.time)) {
      notice(`Sorry — someone just booked ${state.time} on ${fmtShort(state.date)}. Please choose another time.`, "error");
      state.time = null;
    }
    if (state.date && dayState(state.date).full) {
      notice(`${fmtShort(state.date)} is now fully booked. Please pick another date.`, "error");
      state.date = null; state.time = null;
    }
    renderCalendar(); renderSlots(); syncSummary();
  }

  // ---------- form helpers ----------
  const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  function setError(name, msg) {
    const p = $(`[data-error-for="${name}"]`);
    if (!p) return;
    p.textContent = msg;
    const field = p.closest(".field");
    if (field) {
      field.classList.add("has-error");
      const input = field.querySelector("input:not([type=hidden]), select, textarea");
      if (input) input.setAttribute("aria-invalid", "true");
    }
  }
  function clearError(name) {
    const p = $(`[data-error-for="${name}"]`);
    if (!p) return;
    p.textContent = "";
    const field = p.closest(".field");
    if (field) {
      field.classList.remove("has-error");
      const input = field.querySelector("[aria-invalid]");
      if (input) input.removeAttribute("aria-invalid");
    }
  }
  function validate(data) {
    const errors = {};
    if (!data.date || !data.time) errors.date = "Please pick a date and a time.";
    if (!data.name || data.name.trim().length < 2) errors.name = "Please enter your full name.";
    if (!EMAIL_RE.test(data.email || "")) errors.email = "Please enter a valid email address.";
    if (!data.service) errors.service = "Please choose a service.";
    if (!data.details || data.details.trim().length < 10) errors.details = "Tell us a little about your project (at least 10 characters).";
    return errors;
  }

  function fillServiceOptions() {
    const sel = $("#service");
    sel.innerHTML = '<option value="" disabled selected>Choose a service</option>' +
      CONFIG.services.map((s) => `<option>${esc(s)}</option>`).join("");
    // Preselect from links like /consultation?service=…&budget=…
    const q = new URLSearchParams(location.search);
    const svc = q.get("service"), budget = q.get("budget");
    if (svc && CONFIG.services.includes(svc)) sel.value = svc;
    if (budget && [...$("#budget").options].some((o) => o.value === budget || o.text === budget)) $("#budget").value = budget;
  }

  async function initBooking() {
    const form = $("#booking-form");
    const btn = $("#submit-btn");
    const status = $("#form-status");

    fillServiceOptions();
    $("#slots-tz span").textContent = `Times shown in ${CONFIG.timezone_label}`;
    const t = todayInBiz();
    state.viewYear = t.getFullYear();
    state.viewMonth = t.getMonth();
    renderCalendar();               // draw immediately…
    await loadMonth(iso(state.viewYear, state.viewMonth, 1).slice(0, 7));
    renderCalendar();               // …then again with bookings marked
    syncSummary();

    const goMonth = async (delta) => {
      state.viewMonth += delta;
      if (state.viewMonth < 0) { state.viewMonth = 11; state.viewYear--; }
      if (state.viewMonth > 11) { state.viewMonth = 0; state.viewYear++; }
      renderCalendar();
      await loadMonth(iso(state.viewYear, state.viewMonth, 1).slice(0, 7));
      renderCalendar();
    };
    $("#cal-prev").addEventListener("click", () => goMonth(-1));
    $("#cal-next").addEventListener("click", () => goMonth(1));

    $("#cal-grid").addEventListener("click", async (e) => {
      const b = e.target.closest("[data-date]");
      if (!b || b.disabled) return;
      state.date = b.dataset.date;
      state.time = null;
      notice("");
      renderCalendar(); renderSlots(); syncSummary();
      await loadMonth(ymOf(state.date), true); // freshest data for the chosen day
      renderCalendar(); renderSlots();
      if (window.matchMedia("(max-width: 1080px)").matches) $("#step-time").scrollIntoView({ behavior: "smooth", block: "start" });
    });

    $("#slots").addEventListener("click", (e) => {
      const b = e.target.closest("[data-time]");
      if (!b || b.disabled) return;
      state.time = b.dataset.time;
      notice("");
      renderSlots(); syncSummary();
    });

    $("#service").addEventListener("change", () => { clearError("service"); syncSummary(); });
    ["name", "email", "details"].forEach((n) => form.elements[n].addEventListener("input", () => clearError(n)));

    // Live availability: poll while visible, and re-check when the tab regains focus
    setInterval(() => { if (!document.hidden) refreshAvailability(); }, REFRESH_MS);
    document.addEventListener("visibilitychange", () => { if (!document.hidden) refreshAvailability(); });

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      status.textContent = "";
      const data = Object.fromEntries(new FormData(form).entries());
      data.client_timezone = Intl.DateTimeFormat().resolvedOptions().timeZone || "";

      ["name", "email", "service", "date", "details"].forEach(clearError);
      const errors = validate(data);
      if (Object.keys(errors).length) {
        Object.entries(errors).forEach(([k, v]) => setError(k, v));
        const firstKey = Object.keys(errors)[0];
        const el = firstKey === "date" ? (state.date ? $("#step-time") : $("#step-date")) : form.elements[firstKey];
        el.scrollIntoView({ behavior: "smooth", block: "center" });
        if (firstKey !== "date") el.focus({ preventScroll: true });
        return;
      }

      const setBusy = (busy) => {
        [btn, $("#summary-submit")].forEach((b) => { b.disabled = busy; });
        btn.classList.toggle("is-loading", busy);
        $(".btn__label", btn).textContent = busy ? "Booking…" : "Book my consultation";
      };
      setBusy(true);
      try {
        const res = await fetch("/api/book", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        });
        const out = await res.json().catch(() => ({}));
        if (res.status === 409) {
          // Someone else got this slot first — show it as booked and ask for another time
          await loadMonth(ymOf(data.date), true);
          state.time = null;
          if (dayState(data.date).full) state.date = null;
          renderCalendar(); renderSlots(); syncSummary();
          notice(out.message || "Sorry — that time was just booked. Please choose another.", "error");
          $("#step-time").scrollIntoView({ behavior: "smooth", block: "start" });
          return;
        }
        if (!res.ok || !out.ok) {
          if (out.errors) Object.entries(out.errors).forEach(([k, v]) => setError(k, v));
          throw new Error(out.message || "Something went wrong. Please try again or message us on WhatsApp.");
        }

        // Success
        const first = data.name.trim().split(/\s+/)[0];
        $("#success-text").textContent = out.email_sent
          ? `Thanks, ${first}! A confirmation with a calendar invite has been sent to ${data.email}.`
          : `Thanks, ${first}! Your consultation is booked — we’ll confirm by email shortly.`;
        const rows = [
          ["Date", fmtLong(data.date)], ["Time", `${data.time} (${CONFIG.timezone_label})`],
          ["Service", data.service], ["Reference", out.booking_id],
        ];
        $("#success-details").innerHTML = rows.map(([k, v]) => `<div><dt>${esc(k)}</dt><dd>${esc(v)}</dd></div>`).join("");
        $("#booking").hidden = true;
        $("#success").hidden = false;
        $("#success").focus();
        window.scrollTo({ top: 0, behavior: "smooth" });
        const ym = ymOf(data.date);
        const m = state.months[ym] || (state.months[ym] = { taken: {}, at: Date.now() });
        m.taken[data.date] = [...(m.taken[data.date] || []), data.time];
      } catch (err) {
        status.innerHTML = `<div class="notice notice--error"><span>${esc(err.message)}</span></div>`;
      } finally {
        setBusy(false);
      }
    });

    $("#book-another").addEventListener("click", () => {
      form.reset();
      fillServiceOptions();
      state.date = null; state.time = null;
      notice("");
      $("#success").hidden = true;
      $("#booking").hidden = false;
      refreshAvailability();
      $("#step-date").scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }

  // =========================================================
  // Boot
  // =========================================================
  document.addEventListener("DOMContentLoaded", async () => {
    $$("#year").forEach((el) => (el.textContent = new Date().getFullYear()));
    initNav();
    if (PAGE === "home") {
      renderIcons();
      renderServices();
      renderTimeline();
      initWork();
      renderFaqs();
    }
    await loadConfig();
    updateOpenStatus();
    setInterval(updateOpenStatus, 60_000);
    if (PAGE === "consultation") initBooking();
  });
})();
