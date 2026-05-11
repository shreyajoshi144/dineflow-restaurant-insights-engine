"""
Dineflow — Streamlit Frontend
Run: streamlit run app.py
FastAPI backend must be running on http://localhost:8000
"""

import os
import streamlit as st
import requests
from datetime import datetime, date, time

API_BASE = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")

# ── Colour palette ────────────────────────────────────────────────────────────
PRIMARY   = "#E38BA0"
SECONDARY = "#F6C1CC"
ACCENT    = "#D97C8E"
SOFT      = "#FBE4EA"
CARD      = "#FFFFFF"
BG        = "#FFF7F9"
TEXT      = "#4E3B3F"
ADMIN_CLR = "#7C4DFF"   # purple accent for admin UI

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dineflow",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {{
    --primary:   {PRIMARY};
    --secondary: {SECONDARY};
    --accent:    {ACCENT};
    --soft:      {SOFT};
    --card:      {CARD};
    --bg:        {BG};
    --text:      {TEXT};
}}

html, body, [class*="css"] {{ font-family: 'DM Sans', sans-serif; color: {TEXT}; }}
.stApp {{ background-color: {BG}; }}
p, span, div, label, h1, h2, h3, h4, h5, h6, li, td, th {{ color: {TEXT}; }}

input, textarea {{
    color: {TEXT} !important; background-color: #ffffff !important;
    border-radius: 8px !important; border: 1px solid {SECONDARY} !important;
    font-family: 'DM Sans', sans-serif !important;
}}
input::placeholder, textarea::placeholder {{ color: #b08a90 !important; opacity: 1 !important; }}
input:focus, textarea:focus {{
    border-color: {PRIMARY} !important;
    box-shadow: 0 0 0 2px rgba(227,139,160,0.18) !important;
    color: {TEXT} !important;
}}
[data-testid="stTextInput"] input {{ color: {TEXT} !important; }}
[data-testid="stTextInput"] label, [data-testid="stTextInput"] p {{ color: {TEXT} !important; }}
[data-testid="stDateInput"] input {{ color: {TEXT} !important; }}
[data-testid="stSelectbox"] label, [data-testid="stSelectbox"] p, [data-testid="stSelectbox"] span {{ color: {TEXT} !important; }}
[data-testid="stSelectbox"] > div > div {{ color: {TEXT} !important; border-radius: 8px !important; border: 1px solid {SECONDARY} !important; }}

[data-testid="stSidebar"] {{ background-color: {PRIMARY} !important; }}
[data-testid="stSidebar"] * {{ color: #FFFAF2 !important; }}
[data-testid="stSidebar"] .stButton > button {{
    background: transparent !important; color: #FFFAF2 !important;
    border: 1px solid rgba(255,255,255,0.25) !important; border-radius: 8px !important;
    width: 100%; text-align: left; padding: 10px 16px; margin-bottom: 4px;
    font-family: 'DM Sans', sans-serif; font-weight: 500; font-size: 14px; transition: background 0.2s;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    background: rgba(255,255,255,0.15) !important; border-color: rgba(255,255,255,0.5) !important;
}}

.stButton > button {{
    background-color: {PRIMARY} !important; color: #FFFAF2 !important;
    border: none !important; border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif; font-weight: 500; padding: 10px 20px; transition: opacity 0.2s;
}}
.stButton > button:hover {{ opacity: 0.88; }}
button[kind="secondary"] {{ background-color: {SOFT} !important; color: {TEXT} !important; }}

.stTabs [data-baseweb="tab-list"] {{ background-color: {CARD}; border-radius: 10px; padding: 4px; gap: 4px; }}
.stTabs [data-baseweb="tab"] {{ background: transparent; border-radius: 8px; color: {TEXT}; font-family: 'DM Sans', sans-serif; font-weight: 500; }}
.stTabs [aria-selected="true"] {{ background-color: {PRIMARY} !important; color: #FFFAF2 !important; }}

[data-testid="metric-container"] {{ background: {CARD}; border-radius: 12px; padding: 16px; border: 1px solid {SECONDARY}; }}
[data-testid="metric-container"] * {{ color: {TEXT} !important; }}

hr {{ border-color: {SECONDARY} !important; opacity: 0.4; }}
[data-testid="stAlert"] {{ border-radius: 10px !important; }}
::-webkit-scrollbar {{ width: 6px; }}
::-webkit-scrollbar-track {{ background: {BG}; }}
::-webkit-scrollbar-thumb {{ background: {SECONDARY}; border-radius: 3px; }}
[data-testid="stVegaLiteChart"] {{ border-radius: 12px; overflow: hidden; }}
[data-testid="stExpander"] summary p, [data-testid="stExpander"] p {{ color: {TEXT} !important; }}
[data-testid="stCaptionContainer"] p {{ color: {TEXT} !important; opacity: 0.7; }}
.stMarkdown p, .stMarkdown span {{ color: {TEXT}; }}
[data-baseweb="calendar"] * {{ color: {TEXT} !important; }}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# COMPONENT HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def card(content_html: str, padding: str = "24px 28px") -> None:
    st.markdown(f"""
    <div style="background:{CARD};border:1px solid {SECONDARY};border-radius:14px;
                padding:{padding};margin-bottom:16px;">{content_html}</div>
    """, unsafe_allow_html=True)


def section_title(emoji: str, title: str, subtitle: str = "") -> None:
    sub_html = f'<p style="margin:4px 0 0;font-size:14px;color:{TEXT};opacity:0.65;font-weight:400">{subtitle}</p>' if subtitle else ""
    st.markdown(f"""
    <div style="margin-bottom:24px;">
        <h2 style="font-family:'Cormorant Garamond',serif;font-size:28px;font-weight:700;
                   color:{TEXT};margin:0;letter-spacing:-0.3px;">{emoji} {title}</h2>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


def tag(label: str, color: str = PRIMARY, text_color: str = "#FFFAF2") -> str:
    return (
        f'<span style="background:{color};color:{text_color};border-radius:20px;'
        f'padding:3px 12px;font-size:11px;font-weight:600;letter-spacing:0.5px;'
        f'text-transform:uppercase;font-family:\'DM Sans\',sans-serif;">{label}</span>'
    )


def divider() -> None:
    st.markdown(
        f'<hr style="border:none;border-top:1px solid {SECONDARY};opacity:0.35;margin:24px 0;">',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# API HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def auth_headers() -> dict:
    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}


def api_post(endpoint: str, payload: dict, use_auth: bool = False):
    headers = {"Content-Type": "application/json"}
    if use_auth:
        headers.update(auth_headers())
    try:
        return requests.post(f"{API_BASE}{endpoint}", json=payload, headers=headers, timeout=10)
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend. Is FastAPI running on port 8000?")
        return None


def api_get(endpoint: str, params: dict = None, use_auth: bool = False):
    headers = auth_headers() if use_auth else {}
    try:
        return requests.get(f"{API_BASE}{endpoint}", params=params, headers=headers, timeout=10)
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend. Is FastAPI running on port 8000?")
        return None


def api_delete(endpoint: str, use_auth: bool = True):
    headers = auth_headers() if use_auth else {}
    try:
        return requests.delete(f"{API_BASE}{endpoint}", headers=headers, timeout=10)
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend.")
        return None


def safe_json(r) -> dict:
    try:
        return r.json()
    except Exception:
        return {"detail": r.text}


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INIT
# ══════════════════════════════════════════════════════════════════════════════

DEFAULTS = {
    "token":                  None,
    "user_email":             None,
    "user_role":              None,   # "user" | "admin"
    "page":                   "Home",
    "availability_result":    None,
    "selected_booking_time":  None,
    "admin_bk_page":          1,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:8px 0 28px;text-align:center;">
            <div style="font-family:'Cormorant Garamond',serif;font-size:30px;font-weight:700;
                        color:#FFFAF2;letter-spacing:1px;">🍽️ Dineflow</div>
            <div style="font-size:11px;color:rgba(255,255,255,0.6);letter-spacing:2px;
                        text-transform:uppercase;margin-top:2px;">Restaurant & Bar</div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.token:
            email_short = st.session_state.user_email.split("@")[0].capitalize()
            role_badge  = "🛡️ Admin" if st.session_state.user_role == "admin" else "👤 Guest"
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.12);border-radius:10px;
                        padding:10px 14px;margin-bottom:20px;font-size:13px;">
                {role_badge} <b>{email_short}</b>
                <span style="opacity:0.6;font-size:11px;display:block;margin-top:2px;">
                    {st.session_state.user_email}
                </span>
            </div>
            """, unsafe_allow_html=True)

            nav_items = [
                ("🏠", "Home"),
                ("📅", "Book Table"),
                ("🍴", "Menu"),
                ("📊", "Analytics"),
            ]
            # Admin-only nav item
            if st.session_state.user_role == "admin":
                nav_items.append(("🛡️", "Admin Panel"))

            for icon, label in nav_items:
                if st.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True):
                    st.session_state.page                = label
                    st.session_state.availability_result = None
                    st.rerun()

            st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
            st.markdown("---")

            with st.expander("🌱 Seed Demo Data"):
                st.markdown(
                    "<p style='font-size:12px;opacity:0.8;'>Populate DB with 5 users, 10 tables, 100 bookings.</p>",
                    unsafe_allow_html=True,
                )
                if st.button("▶ Run Seed", use_container_width=True):
                    r = api_post("/seed-data", {})
                    if r and r.status_code == 200:
                        d = r.json()
                        st.success(f"✅ {d['users']} users · {d['tables']} tables · {d['bookings']} bookings")
                        st.caption("Admin: alice@dineflow.com / password123")
                    elif r:
                        st.error(r.text)

            st.markdown("<div style='margin-top:auto;padding-top:24px;'></div>", unsafe_allow_html=True)
            if st.button("🚪  Logout", use_container_width=True):
                for k in ["token", "user_email", "user_role", "availability_result", "selected_booking_time"]:
                    st.session_state[k] = None
                st.session_state.page = "Home"
                st.rerun()

        else:
            st.markdown("""
            <p style='font-size:13px;opacity:0.75;text-align:center;margin-top:8px;color:#FFFAF2;'>
                Sign in to reserve your table
            </p>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: AUTH
# ══════════════════════════════════════════════════════════════════════════════

def page_auth() -> None:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {PRIMARY} 0%, {ACCENT} 100%);
                border-radius: 20px; padding: 56px 40px; text-align: center; margin-bottom: 36px;">
        <div style="font-size:48px;margin-bottom:12px;">🍽️</div>
        <h1 style="font-family:'Cormorant Garamond',serif;color:#FFFAF2;font-size:44px;
                   font-weight:700;margin:0 0 10px;letter-spacing:-0.5px;">Welcome to Dineflow</h1>
        <p style="color:rgba(255,250,242,0.85);font-size:16px;max-width:420px;margin:0 auto;font-weight:300;">
            Reserve your perfect table, explore our menu, and track your dining journey.
        </p>
    </div>
    """, unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 1.4, 1])
    with mid:
        tab_login, tab_signup = st.tabs(["Sign In", "Create Account"])

        with tab_login:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            email    = st.text_input("Email address", key="li_email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", key="li_pass")
            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

            if st.button("Sign In →", use_container_width=True, type="primary"):
                if not email or not password:
                    st.warning("Please fill in both fields.")
                else:
                    r = api_post("/login", {"email": email, "password": password})
                    if r and r.status_code == 200:
                        data = r.json()
                        st.session_state.token      = data["access_token"]
                        st.session_state.user_email = email
                        st.session_state.user_role  = data.get("role", "user")
                        st.session_state.page       = "Home"
                        st.success("✅ Signed in!")
                        st.rerun()
                    elif r:
                        st.error(safe_json(r).get("detail", "Sign-in failed."))

            st.markdown(f"""
            <p style='text-align:center;margin-top:14px;font-size:12px;color:{PRIMARY};'>
                Demo: alice@dineflow.com / password123 (admin)
            </p>""", unsafe_allow_html=True)

        with tab_signup:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            new_email = st.text_input("Email address", key="su_email", placeholder="you@example.com")
            new_pass  = st.text_input("Password", type="password", key="su_pass")
            conf_pass = st.text_input("Confirm Password", type="password", key="su_conf")
            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

            if st.button("Create Account →", use_container_width=True, type="primary"):
                if not new_email or not new_pass:
                    st.warning("Please fill in all fields.")
                elif new_pass != conf_pass:
                    st.error("Passwords do not match.")
                else:
                    r = api_post("/signup", {"email": new_email, "password": new_pass})
                    if r and r.status_code == 201:
                        st.success("✅ Account created! Sign in now.")
                    elif r:
                        st.error(safe_json(r).get("detail", "Signup failed."))


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: HOME
# ══════════════════════════════════════════════════════════════════════════════

def page_home() -> None:
    st.markdown(f"""
    <div style="background: linear-gradient(120deg, {PRIMARY} 0%, {ACCENT} 100%);
                border-radius: 20px; padding: 52px 48px; margin-bottom: 32px;
                display: flex; align-items: center; justify-content: space-between;">
        <div>
            <div style="font-family:'Cormorant Garamond',serif;font-size:42px;font-weight:700;
                        color:#FFFAF2;line-height:1.15;margin-bottom:12px;">
                Reserve Your<br>Perfect Evening
            </div>
            <p style="color:rgba(255,250,242,0.88);font-size:15px;max-width:380px;
                      font-weight:300;margin-bottom:24px;">
                Seasonal menus, handcrafted cocktails, and unforgettable moments — all one click away.
            </p>
            <span style="background:#FFFAF2;color:{PRIMARY};border-radius:8px;
                         padding:10px 24px;font-weight:600;font-size:14px;">Book a Table →</span>
        </div>
        <div style="font-size:96px;opacity:0.22;user-select:none;">🍽️</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:{SOFT};border:1px solid {ACCENT};border-radius:14px;padding:16px 24px;
                display:flex;align-items:center;gap:16px;margin-bottom:28px;">
        <div style="font-size:28px;">🎁</div>
        <div>
            <span style="font-weight:600;color:{TEXT};font-size:14px;">
                This Weekend — Chef's Tasting Menu
            </span>
            <span style="font-size:13px;color:{TEXT};opacity:0.65;display:block;margin-top:2px;">
                5-course seasonal tasting experience · Available Fri–Sun · Reserve by Thursday
            </span>
        </div>
        <div style="margin-left:auto;">{tag("Limited Seats", ACCENT, "#FFFAF2")}</div>
    </div>
    """, unsafe_allow_html=True)

    section_title("⚡", "Quick Actions")
    c1, c2, c3 = st.columns(3)

    with c1:
        card(f"""
        <div style="text-align:center;padding:8px 0;">
            <div style="font-size:36px;margin-bottom:12px;">📅</div>
            <div style="font-family:'Cormorant Garamond',serif;font-size:20px;
                        font-weight:700;color:{TEXT};margin-bottom:6px;">Book a Table</div>
            <div style="font-size:13px;color:{TEXT};opacity:0.65;line-height:1.5;">
                Check real-time availability and reserve your spot instantly.
            </div>
        </div>
        """)
        if st.button("Reserve Now", key="qa_book", use_container_width=True):
            st.session_state.page = "Book Table"
            st.rerun()

    with c2:
        card(f"""
        <div style="text-align:center;padding:8px 0;">
            <div style="font-size:36px;margin-bottom:12px;">🍴</div>
            <div style="font-family:'Cormorant Garamond',serif;font-size:20px;
                        font-weight:700;color:{TEXT};margin-bottom:6px;">View Menu</div>
            <div style="font-size:13px;color:{TEXT};opacity:0.65;line-height:1.5;">
                Explore our seasonal dishes, specials, and handcrafted drinks.
            </div>
        </div>
        """)
        if st.button("See Menu", key="qa_menu", use_container_width=True):
            st.session_state.page = "Menu"
            st.rerun()

    with c3:
        card(f"""
        <div style="text-align:center;padding:8px 0;">
            <div style="font-size:36px;margin-bottom:12px;">📋</div>
            <div style="font-family:'Cormorant Garamond',serif;font-size:20px;
                        font-weight:700;color:{TEXT};margin-bottom:6px;">My Bookings</div>
            <div style="font-size:13px;color:{TEXT};opacity:0.65;line-height:1.5;">
                View and manage all your upcoming reservations.
            </div>
        </div>
        """)
        if st.button("View Bookings", key="qa_bk", use_container_width=True):
            st.session_state.page = "Book Table"
            st.rerun()

    divider()

    c1, c2, c3, c4 = st.columns(4)
    items = [
        ("🕐", "Hours",        "Mon–Fri 12–23\nSat–Sun 11–23"),
        ("📍", "Location",     "42 Elm Street\nIndore, MP"),
        ("📞", "Reservations", "+91 98765 43210"),
        ("🍷", "Dress Code",   "Smart Casual"),
    ]
    for col, (icon, label, value) in zip([c1, c2, c3, c4], items):
        with col:
            card(f"""
            <div style="text-align:center;">
                <div style="font-size:24px;">{icon}</div>
                <div style="font-size:11px;font-weight:600;letter-spacing:1px;
                            text-transform:uppercase;color:{PRIMARY};margin:6px 0 4px;">{label}</div>
                <div style="font-size:13px;color:{TEXT};white-space:pre-line;line-height:1.5;">{value}</div>
            </div>
            """, padding="16px 12px")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: BOOK TABLE
# ══════════════════════════════════════════════════════════════════════════════

def page_book() -> None:
    section_title("📅", "Book a Table", "Check availability and reserve your spot")

    left, right = st.columns([1.1, 1], gap="large")

    with left:
        card(f"""
        <div style="font-family:'Cormorant Garamond',serif;font-size:20px;
                    font-weight:700;color:{TEXT};margin-bottom:4px;">📋 Reservation Details</div>
        <p style="font-size:13px;color:{TEXT};opacity:0.65;margin:0;">
            Choose a date and time to see available tables. Each slot lasts 2 hours.
        </p>
        """, padding="20px 24px 8px")

        selected_date  = st.date_input("Date", value=date.today(), key="bk_date")
        selected_hour  = st.selectbox(
            "Time Slot", options=list(range(10, 24)), index=8,
            format_func=lambda h: f"{h:02d}:00", key="bk_hour",
        )
        booking_dt     = datetime.combine(selected_date, time(hour=selected_hour))
        booking_dt_iso = booking_dt.isoformat()

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔍 Check Availability", use_container_width=True, type="primary"):
                r = api_get("/availability", params={"time": booking_dt_iso})
                if r and r.status_code == 200:
                    st.session_state.availability_result   = r.json()
                    st.session_state.selected_booking_time = booking_dt_iso

        if st.session_state.availability_result:
            result = st.session_state.availability_result
            tables = result.get("available_tables", [])
            divider()

            if tables:
                st.markdown(f"""
                <div style="background:#e8f5e9;border:1px solid #a5d6a7;border-radius:10px;
                            padding:12px 18px;margin-bottom:16px;font-size:14px;
                            color:#1b5e20;font-weight:500;">
                    ✅ {len(tables)} table(s) available for {booking_dt.strftime('%A, %b %d at %H:%M')}
                </div>
                """, unsafe_allow_html=True)

                for t in tables:
                    cap      = t["capacity"]
                    pax_icon = "👤" * min(cap, 4) + ("+" if cap > 4 else "")
                    card(f"""
                    <div style="display:flex;align-items:center;justify-content:space-between;">
                        <div>
                            <div style="font-weight:600;font-size:15px;color:{TEXT};">Table {t['id']}</div>
                            <div style="font-size:12px;color:{TEXT};opacity:0.6;margin-top:2px;">
                                {pax_icon} · Seats up to {cap} guests
                            </div>
                        </div>
                        {tag("Available", "#d4edda", "#155724")}
                    </div>
                    """, padding="14px 20px")

                table_ids    = [t["id"] for t in tables]
                chosen_table = st.selectbox(
                    "Select a Table", options=table_ids, key="chosen_tbl",
                    format_func=lambda tid: f"Table {tid}",
                )
                with c2:
                    if st.button("✅ Book Table", use_container_width=True, type="primary"):
                        rb = api_post(
                            "/book",
                            {"table_id": chosen_table, "booking_time": booking_dt_iso},
                            use_auth=True,
                        )
                        if rb and rb.status_code == 201:
                            st.balloons()
                            st.success(
                                f"🎉 Table {chosen_table} reserved for "
                                f"{booking_dt.strftime('%A, %b %d at %H:%M')}!"
                            )
                            st.session_state.availability_result = None
                        elif rb:
                            detail = safe_json(rb).get("detail", "Booking failed.")
                            if rb.status_code == 429:
                                st.error(f"⚠️ {detail}")
                            else:
                                st.error(f"❌ {detail}")
                                sr = api_get("/suggestions", params={"time": booking_dt_iso})
                                if sr and sr.status_code == 200:
                                    suggs = sr.json().get("suggestions", [])
                                    if suggs:
                                        st.markdown(f"""
                                        <div style="font-size:13px;font-weight:600;
                                                    color:{PRIMARY};margin:12px 0 8px;">
                                            💡 Try these nearby slots:
                                        </div>
                                        """, unsafe_allow_html=True)
                                        for s in suggs[:3]:
                                            st_fmt   = datetime.fromisoformat(s["time"]).strftime("%b %d · %H:%M")
                                            tbl_list = ", ".join(f"#{tid}" for tid in s["available_tables"][:3])
                                            card(f"""
                                            <div style="font-size:13px;color:{TEXT};">
                                                <b>{st_fmt}</b> — Tables: {tbl_list}
                                            </div>
                                            """, padding="10px 16px")

            else:
                st.markdown(f"""
                <div style="background:#fff3e0;border:1px solid #ffcc80;border-radius:10px;
                            padding:12px 18px;margin-bottom:16px;font-size:14px;
                            color:#e65100;font-weight:500;">
                    ⚠️ Slot fully booked — showing nearby suggestions
                </div>
                """, unsafe_allow_html=True)
                sr = api_get("/suggestions", params={"time": booking_dt_iso})
                if sr and sr.status_code == 200:
                    suggs = sr.json().get("suggestions", [])
                    if suggs:
                        st.markdown(
                            f"<p style='font-size:13px;font-weight:600;color:{TEXT};'>💡 Available nearby:</p>",
                            unsafe_allow_html=True,
                        )
                        for s in suggs[:3]:
                            st_fmt   = datetime.fromisoformat(s["time"]).strftime("%A, %b %d at %H:%M")
                            tbl_list = ", ".join(f"#{tid}" for tid in s["available_tables"][:3])
                            card(f"""
                            <div style="font-size:13px;color:{TEXT};">
                                <b style="color:{PRIMARY};">{st_fmt}</b>
                                <span style="opacity:0.65;"> · Tables: {tbl_list}</span>
                            </div>
                            """, padding="12px 18px")
                    else:
                        st.warning("No nearby slots available. Try a different date.")

    with right:
        st.markdown(f"""
        <div style="font-family:'Cormorant Garamond',serif;font-size:22px;
                    font-weight:700;color:{TEXT};margin-bottom:16px;">📋 My Reservations</div>
        """, unsafe_allow_html=True)

        rb = api_get("/bookings", use_auth=True)
        if rb and rb.status_code == 200:
            my_bookings = rb.json()
            if my_bookings:
                for b in my_bookings:   # already sorted desc by API
                    btime      = datetime.fromisoformat(b["booking_time"])
                    bstatus    = b.get("status", "active")
                    is_future  = btime > datetime.now()

                    if bstatus == "cancelled":
                        status_tag = tag("Cancelled", "#f8d7da", "#721c24")
                    elif is_future:
                        status_tag = tag("Upcoming", "#d4edda", "#155724")
                    else:
                        status_tag = tag("Past", "#f0e8ea", TEXT)

                    card(f"""
                    <div style="display:flex;align-items:flex-start;
                                justify-content:space-between;gap:8px;">
                        <div>
                            <div style="font-weight:600;font-size:15px;color:{TEXT};">
                                Table {b['table_id']}
                            </div>
                            <div style="font-size:12px;color:{TEXT};opacity:0.6;margin-top:3px;">
                                📅 {btime.strftime('%A, %b %d %Y')}
                            </div>
                            <div style="font-size:12px;color:{TEXT};opacity:0.6;margin-top:1px;">
                                🕐 {btime.strftime('%H:%M')}
                            </div>
                        </div>
                        {status_tag}
                    </div>
                    """, padding="14px 18px")
            else:
                card(f"""
                <div style="text-align:center;padding:24px 0;">
                    <div style="font-size:32px;margin-bottom:10px;">🗓️</div>
                    <div style="font-size:14px;color:{TEXT};opacity:0.65;">No reservations yet.</div>
                    <div style="font-size:13px;color:{TEXT};opacity:0.45;margin-top:4px;">
                        Book your first table on the left!
                    </div>
                </div>
                """)
        elif rb and rb.status_code == 401:
            st.warning("Session expired. Please log in again.")
            st.session_state.token = None
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: MENU
# ══════════════════════════════════════════════════════════════════════════════

MENU = {
    "Starters": [
        ("Mushroom Bruschetta",       "Toasted sourdough · wild mushrooms · truffle oil",      "₹280", "🍄"),
        ("Burrata & Heirloom Tomato", "Creamy burrata · basil oil · flaky sea salt",            "₹340", "🧀"),
        ("Soup of the Day",           "Chef's seasonal creation — ask your server",             "₹220", "🥣"),
        ("Crispy Calamari",           "Lemon aioli · smoked paprika · fresh herbs",             "₹320", "🦑"),
    ],
    "Mains": [
        ("Pan Seared Salmon",         "Lemon butter · capers · wilted spinach · new potatoes", "₹680", "🐟"),
        ("Herb Roasted Chicken",      "Free-range · rosemary jus · seasonal vegetables",       "₹580", "🍗"),
        ("Wild Mushroom Risotto",     "Arborio · parmesan · truffle oil · micro herbs",         "₹520", "🍚"),
        ("Grilled Tenderloin",        "200g · chimichurri · roasted garlic mash",               "₹880", "🥩"),
    ],
    "Desserts": [
        ("Crème Brûlée",              "Classic vanilla · caramelised sugar crust",              "₹240", "🍮"),
        ("Dark Chocolate Fondant",    "Warm centre · vanilla bean ice cream",                   "₹280", "🍫"),
        ("Seasonal Fruit Tart",       "Buttery pastry · crème pâtissière · fresh fruit",        "₹260", "🥧"),
    ],
    "Drinks": [
        ("House Sangria",             "Red wine · brandy · seasonal fruit",                     "₹320", "🍷"),
        ("Classic Negroni",           "Gin · Campari · sweet vermouth",                         "₹380", "🍸"),
        ("Fresh Lime Soda",           "Still or sparkling · mint · sugar or salt rim",          "₹120", "🍋"),
        ("Artisan Coffee",            "Single origin · filter / espresso / cold brew",          "₹160", "☕"),
    ],
}

def page_menu() -> None:
    section_title("🍴", "Our Menu", "Seasonal ingredients, crafted with care")

    for category, items in MENU.items():
        st.markdown(f"""
        <div style="font-family:'Cormorant Garamond',serif;font-size:22px;font-weight:700;
                    color:{TEXT};border-left:4px solid {PRIMARY};padding-left:14px;margin:24px 0 14px;">
            {category}
        </div>
        """, unsafe_allow_html=True)

        cols = st.columns(2)
        for idx, (name, desc, price, icon) in enumerate(items):
            with cols[idx % 2]:
                card(f"""
                <div style="display:flex;gap:14px;align-items:flex-start;">
                    <div style="font-size:28px;line-height:1;margin-top:2px;">{icon}</div>
                    <div style="flex:1;">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div style="font-weight:600;font-size:15px;color:{TEXT};">{name}</div>
                            <div style="font-weight:700;font-size:15px;color:{PRIMARY};
                                        white-space:nowrap;margin-left:12px;">{price}</div>
                        </div>
                        <div style="font-size:12px;color:{TEXT};opacity:0.6;
                                    margin-top:4px;line-height:1.5;">{desc}</div>
                    </div>
                </div>
                """, padding="16px 20px")
        divider()

    st.markdown(f"""
    <div style="background:{SOFT};border-radius:12px;padding:16px 24px;font-size:13px;
                color:{TEXT};opacity:0.75;text-align:center;border:1px solid {ACCENT};">
        🌿 All dishes use seasonal, locally sourced ingredients where possible.
        Please inform your server of any allergies.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════

def page_analytics() -> None:
    section_title("📊", "Insights", "Booking patterns and peak hours")

    rp = api_get("/analytics/peak-hours")
    rd = api_get("/analytics/distribution")

    peak_data = rp.json().get("peak_hours", []) if rp and rp.status_code == 200 else []
    dist_data = rd.json().get("distribution", []) if rd and rd.status_code == 200 else []

    total_bookings = sum(d["count"] for d in dist_data) if dist_data else 0
    peak_hour_val  = f"{peak_data[0]['hour']:02d}:00" if peak_data else "—"
    active_days    = len(dist_data)
    avg_per_day    = round(total_bookings / active_days, 1) if active_days else 0

    c1, c2, c3, c4 = st.columns(4)
    for col, (label, value, sub) in zip(
        [c1, c2, c3, c4],
        [
            ("Total Reservations",     str(total_bookings), "lifetime bookings"),
            ("Peak Dining Hour",       peak_hour_val,       "highest demand slot"),
            ("Active Service Days",    str(active_days),    "days with bookings"),
            ("Avg Daily Reservations", str(avg_per_day),    "average per day"),
        ],
    ):
        with col:
            st.metric(label=label, value=value, help=sub)

    divider()

    left, right = st.columns([1, 1.2], gap="large")

    with left:
        st.markdown(f"""
        <div style="font-family:'Cormorant Garamond',serif;font-size:20px;
                    font-weight:700;color:{TEXT};margin-bottom:16px;">🕐 Peak Booking Hours</div>
        """, unsafe_allow_html=True)

        if peak_data:
            top_count = peak_data[0]["count"]
            for i, item in enumerate(peak_data):
                medal    = ["🥇", "🥈", "🥉"][i] if i < 3 else "  "
                fill_pct = int((item["count"] / top_count) * 100)
                card(f"""
                <div style="display:flex;align-items:center;gap:14px;">
                    <div style="font-size:20px;">{medal}</div>
                    <div style="flex:1;">
                        <div style="display:flex;justify-content:space-between;
                                    font-size:14px;font-weight:600;color:{TEXT};margin-bottom:6px;">
                            <span>{item['hour']:02d}:00 — {item['hour']+1:02d}:00</span>
                            <span style="color:{PRIMARY};">{item['count']} bookings</span>
                        </div>
                        <div style="background:{SECONDARY};border-radius:4px;height:8px;">
                            <div style="background:{PRIMARY};border-radius:4px;
                                        height:8px;width:{fill_pct}%;"></div>
                        </div>
                    </div>
                </div>
                """, padding="14px 18px")
        else:
            card(f"<div style='text-align:center;padding:20px 0;color:{TEXT};opacity:0.5;font-size:14px;'>No data yet — seed the database first.</div>")

    with right:
        st.markdown(f"""
        <div style="font-family:'Cormorant Garamond',serif;font-size:20px;
                    font-weight:700;color:{TEXT};margin-bottom:16px;">📅 Bookings by Date</div>
        """, unsafe_allow_html=True)

        if dist_data:
            chart_data = {d["date"]: d["count"] for d in dist_data}
            st.bar_chart(chart_data, color=PRIMARY)
            divider()
            st.markdown(f"<div style='font-size:13px;font-weight:600;color:{TEXT};margin-bottom:10px;'>Recent Dates</div>",
                        unsafe_allow_html=True)
            max_count = max(d["count"] for d in dist_data)
            for item in dist_data[-6:]:
                pct = int((item["count"] / max_count) * 100)
                card(f"""
                <div style="display:flex;align-items:center;justify-content:space-between;font-size:13px;">
                    <span style="color:{TEXT};font-weight:500;">{item['date']}</span>
                    <div style="display:flex;align-items:center;gap:10px;">
                        <div style="background:{SECONDARY};border-radius:3px;height:6px;width:80px;">
                            <div style="background:{ACCENT};border-radius:3px;height:6px;width:{pct}%;"></div>
                        </div>
                        <span style="color:{PRIMARY};font-weight:700;min-width:24px;text-align:right;">
                            {item['count']}
                        </span>
                    </div>
                </div>
                """, padding="10px 18px")
        else:
            card(f"<div style='text-align:center;padding:20px 0;color:{TEXT};opacity:0.5;font-size:14px;'>No data yet — seed the database first.</div>")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ADMIN PANEL
# ══════════════════════════════════════════════════════════════════════════════

def page_admin() -> None:
    st.markdown(f"""
    <div style="background:linear-gradient(120deg,{ADMIN_CLR} 0%,#512DA8 100%);
                border-radius:16px;padding:28px 36px;margin-bottom:28px;">
        <div style="font-family:'Cormorant Garamond',serif;font-size:32px;font-weight:700;
                    color:#FFFAF2;margin-bottom:4px;">🛡️ Admin Panel</div>
        <div style="font-size:13px;color:rgba(255,255,255,0.75);">
            Full system overview — users, bookings, and analytics
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_users, tab_bookings, tab_analytics = st.tabs(["👥 Users", "📋 All Bookings", "📈 Analytics"])

    # ── Tab 1: Users ──────────────────────────────────────────────────────────
    with tab_users:
        r = api_get("/admin/users", use_auth=True)
        if r is None:
            return
        if r.status_code == 403:
            st.error("Access denied.")
            return
        users = r.json().get("users", [])

        st.markdown(f"<div style='font-size:13px;color:{TEXT};opacity:0.6;margin-bottom:16px;'>"
                    f"{len(users)} registered users</div>", unsafe_allow_html=True)

        for u in users:
            role_tag = tag("Admin", ADMIN_CLR, "#fff") if u["role"] == "admin" else tag("User", SECONDARY, TEXT)
            card(f"""
            <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;">
                <div>
                    <div style="font-weight:600;font-size:14px;color:{TEXT};">{u['email']}</div>
                    <div style="font-size:12px;color:{TEXT};opacity:0.5;margin-top:2px;">ID #{u['id']}</div>
                </div>
                <div style="display:flex;align-items:center;gap:12px;">
                    <span style="font-size:13px;color:{TEXT};opacity:0.7;">
                        {u['active_bookings']} active bookings
                    </span>
                    {role_tag}
                </div>
            </div>
            """, padding="14px 20px")

    # ── Tab 2: All Bookings ───────────────────────────────────────────────────
    with tab_bookings:
        st.markdown("**Filters**")
        fc1, fc2, fc3 = st.columns([1, 1, 1])
        with fc1:
            filter_date = st.text_input("Date (YYYY-MM-DD)", key="adm_date", placeholder="e.g. 2026-05-10")
        with fc2:
            filter_uid  = st.text_input("User ID", key="adm_uid", placeholder="e.g. 2")
        with fc3:
            page_size   = st.selectbox("Per page", [10, 20, 50], index=1, key="adm_ps")

        # Pagination state
        if "admin_bk_page" not in st.session_state:
            st.session_state.admin_bk_page = 1

        params = {"page": st.session_state.admin_bk_page, "limit": page_size}
        if filter_date.strip():
            params["date"]    = filter_date.strip()
        if filter_uid.strip().isdigit():
            params["user_id"] = int(filter_uid.strip())

        r = api_get("/admin/bookings", params=params, use_auth=True)
        if r and r.status_code == 200:
            data      = r.json()
            total     = data["total"]
            bookings  = data["bookings"]
            cur_page  = data["page"]
            total_pgs = max(1, -(-total // page_size))   # ceil division

            st.markdown(f"<div style='font-size:13px;color:{TEXT};opacity:0.6;margin-bottom:12px;'>"
                        f"{total} bookings found · Page {cur_page} of {total_pgs}</div>",
                        unsafe_allow_html=True)

            for b in bookings:
                btime    = datetime.fromisoformat(b["booking_time"])
                bstatus  = b["status"]
                s_tag    = (tag("Active", "#d4edda", "#155724")
                            if bstatus == "active"
                            else tag("Cancelled", "#f8d7da", "#721c24"))

                col_info, col_btn = st.columns([5, 1])
                with col_info:
                    card(f"""
                    <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;">
                        <div>
                            <div style="font-weight:600;font-size:14px;color:{TEXT};">
                                Booking #{b['id']} · Table {b['table_id']}
                            </div>
                            <div style="font-size:12px;color:{TEXT};opacity:0.55;margin-top:3px;">
                                👤 {b['user_email']} (ID {b['user_id']}) ·
                                📅 {btime.strftime('%d %b %Y %H:%M')}
                            </div>
                        </div>
                        {s_tag}
                    </div>
                    """, padding="12px 18px")
                with col_btn:
                    if bstatus == "active":
                        st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
                        if st.button("Cancel", key=f"cancel_{b['id']}"):
                            dr = api_delete(f"/admin/booking/{b['id']}")
                            if dr and dr.status_code == 200:
                                st.success(f"Booking #{b['id']} cancelled.")
                                st.rerun()
                            elif dr:
                                st.error(safe_json(dr).get("detail", "Error"))

            # Pagination controls
            p1, p2, p3 = st.columns([1, 2, 1])
            with p1:
                if cur_page > 1:
                    if st.button("← Prev", use_container_width=True):
                        st.session_state.admin_bk_page = cur_page - 1
                        st.rerun()
            with p3:
                if cur_page < total_pgs:
                    if st.button("Next →", use_container_width=True):
                        st.session_state.admin_bk_page = cur_page + 1
                        st.rerun()
        elif r:
            st.error(safe_json(r).get("detail", "Failed to load bookings."))

    # ── Tab 3: Admin Analytics ────────────────────────────────────────────────
    with tab_analytics:
        section_title("📈", "System Analytics", "Real-time operational data")

        # Cancellation rate metrics
        rc = api_get("/admin/cancellation-rate", use_auth=True)
        if rc and rc.status_code == 200:
            cd = rc.json()
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Bookings",     cd["total_bookings"])
            m2.metric("Active",             cd["active_bookings"])
            m3.metric("Cancelled",          cd["cancelled_bookings"])
            m4.metric("Cancellation Rate",  f"{cd['cancellation_rate_pct']}%")
            divider()

        ac1, ac2 = st.columns(2)

        with ac1:
            # Most booked tables
            rt = api_get("/admin/most-booked-tables", use_auth=True)
            if rt and rt.status_code == 200:
                tables_data = rt.json().get("most_booked_tables", [])
                st.markdown(f"""
                <div style="font-family:'Cormorant Garamond',serif;font-size:18px;font-weight:700;
                            color:{TEXT};margin-bottom:12px;">🪑 Most Booked Tables</div>
                """, unsafe_allow_html=True)
                if tables_data:
                    max_c = tables_data[0]["count"] or 1
                    for t in tables_data:
                        pct = int(t["count"] / max_c * 100)
                        card(f"""
                        <div style="display:flex;align-items:center;justify-content:space-between;
                                    font-size:13px;color:{TEXT};">
                            <span><b>Table {t['table_id']}</b>
                                <span style="opacity:0.55;"> · {t['capacity']} seats</span>
                            </span>
                            <div style="display:flex;align-items:center;gap:8px;">
                                <div style="background:{SECONDARY};border-radius:3px;height:6px;width:80px;">
                                    <div style="background:{ADMIN_CLR};border-radius:3px;
                                                height:6px;width:{pct}%;"></div>
                                </div>
                                <span style="color:{ADMIN_CLR};font-weight:700;">{t['count']}</span>
                            </div>
                        </div>
                        """, padding="10px 16px")

            # Top users
            ru = api_get("/admin/top-users", use_auth=True)
            if ru and ru.status_code == 200:
                top_users = ru.json().get("top_users", [])
                st.markdown(f"""
                <div style="font-family:'Cormorant Garamond',serif;font-size:18px;font-weight:700;
                            color:{TEXT};margin:20px 0 12px;">👑 Top Users</div>
                """, unsafe_allow_html=True)
                for i, u in enumerate(top_users[:5]):
                    medal = ["🥇", "🥈", "🥉", "4.", "5."][i] if i < 5 else str(i + 1) + "."
                    card(f"""
                    <div style="display:flex;align-items:center;justify-content:space-between;
                                font-size:13px;color:{TEXT};">
                        <span>{medal} <b>{u['email']}</b></span>
                        <span style="color:{ADMIN_CLR};font-weight:700;">{u['count']} bookings</span>
                    </div>
                    """, padding="10px 16px")

        with ac2:
            # Hourly load chart
            rh = api_get("/admin/hourly-load", use_auth=True)
            if rh and rh.status_code == 200:
                hourly = rh.json().get("hourly_load", [])
                st.markdown(f"""
                <div style="font-family:'Cormorant Garamond',serif;font-size:18px;font-weight:700;
                            color:{TEXT};margin-bottom:12px;">🕐 Hourly Load</div>
                """, unsafe_allow_html=True)
                if hourly:
                    chart = {f"{h['hour']:02d}:00": h["count"] for h in hourly}
                    st.bar_chart(chart, color=ADMIN_CLR)
                else:
                    st.caption("No data yet.")

            # Table utilization
            rtu = api_get("/admin/table-utilization", use_auth=True)
            if rtu and rtu.status_code == 200:
                util = rtu.json().get("table_utilization", [])
                st.markdown(f"""
                <div style="font-family:'Cormorant Garamond',serif;font-size:18px;font-weight:700;
                            color:{TEXT};margin:20px 0 12px;">📊 Table Utilisation</div>
                """, unsafe_allow_html=True)
                if util:
                    max_u = max(t["booking_count"] for t in util) or 1
                    for t in util:
                        pct = int(t["booking_count"] / max_u * 100)
                        card(f"""
                        <div style="display:flex;align-items:center;justify-content:space-between;
                                    font-size:13px;color:{TEXT};">
                            <span>
                                <b>Table {t['table_id']}</b>
                                <span style="opacity:0.55;"> · {t['capacity']} seats</span>
                            </span>
                            <div style="display:flex;align-items:center;gap:8px;">
                                <div style="background:{SECONDARY};border-radius:3px;height:6px;width:80px;">
                                    <div style="background:{ACCENT};border-radius:3px;
                                                height:6px;width:{pct}%;"></div>
                                </div>
                                <span style="color:{ACCENT};font-weight:700;">{t['booking_count']}</span>
                            </div>
                        </div>
                        """, padding="10px 16px")


# ══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════════

render_sidebar()

if not st.session_state.token:
    page_auth()
else:
    page = st.session_state.page
    if page == "Home":
        page_home()
    elif page == "Book Table":
        page_book()
    elif page == "Menu":
        page_menu()
    elif page == "Analytics":
        page_analytics()
    elif page == "Admin Panel":
        if st.session_state.user_role == "admin":
            page_admin()
        else:
            st.error("🚫 Admin access required.")
            st.session_state.page = "Home"
            st.rerun()
