# --- Imports (must be at the very top) ---
import streamlit as st
import time
import pandas as pd
import json
import os
import yfinance as yf
import requests
from datetime import datetime as dt

# --- Dark Mode & Focus Mode Toggles ---
sidebar_col1, sidebar_col2 = st.sidebar.columns([1,1])
with sidebar_col1:
    dark_mode = st.checkbox("🌙 Dark Mode", value=False, help="Switch to a dark color scheme for low-light environments.", key="dark_mode_checkbox")
with sidebar_col2:
    focus_mode = st.checkbox("🛏️ Focus Mode", value=False, help="Hide non-essential UI for distraction-free monitoring.", key="focus_mode_checkbox")

if dark_mode:
    st.markdown(
        """
        <style>
        html, body, .stApp, .stApp::before {
            background: #000 !important;
            background-color: #000 !important;
            color: #f1f1f1 !important;
            background-image: none !important;
            animation: none !important;
        }
        .stApp::before {
            content: '';
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: #000 !important;
            z-index: 0;
            pointer-events: none;
        }
        .st-emotion-cache-18ni7ap, .st-emotion-cache-1v0mbdj, .st-emotion-cache-1kyxreq {
            background: rgba(30,30,30,0.92) !important;
            color: #f1f1f1 !important;
        }
        .stMarkdown, .stTextInput, .stButton, .stRadio, .stInfo, .stSelectbox, .stSlider, .stNumberInput {
            color: #f1f1f1 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# --- Focus Mode: Hide non-essential UI ---
def focus_hide_block():
    st.markdown(
        """
        <style>
        .focus-hide, .legend-hide, .helper-hide, .summary-hide, .filters-hide {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

if focus_mode:
    focus_hide_block()

# --- Minimalist Helper Information Boxes below Total Events ---


# --- Legend ---
if not focus_mode:
        st.markdown("""
        <div class='legend-hide' style='margin:0.5em 0 1em 0; padding:0.7em 1em; background:rgba(255,255,255,0.7); border-radius:10px; font-size:0.98em; max-width:900px;'>
            <b>Legend:</b>
            <span style='margin-right:1em;'><span style='color:#2ecc40;'>▲</span>/<span style='color:#d7263d;'>▼</span>: Price up/down</span>
            <span style='margin-right:1em;'>🐢/🐇: Ticker speed slow/fast</span>
            <span style='margin-right:1em;'><span style='color:#d7263d;'>Critical</span>, <span style='color:#f49d37;'>High</span>, <span style='color:#3f88c5;'>Medium</span>, <span style='color:#43aa8b;'>Low</span>: Severity</span>
            <span style='margin-right:1em;'>Black box: Market closed</span>
            <span style='margin-right:1em;'>📝: Watchlist</span>
            <span style='margin-right:1em;'>ℹ️: Info</span>
            <span style='margin-right:1em;'>⚠️: Warning</span>
        </div>
        """, unsafe_allow_html=True)

import streamlit as st
import pandas as pd
import json
import os
import yfinance as yf





st.set_page_config(page_title="Global Risk Monitor", layout="wide")

# --- Auto-refresh every minute ---
st_autorefresh = st.experimental_rerun if hasattr(st, 'experimental_rerun') else None
if st_autorefresh:
    st_autorefresh_interval = 60  # seconds
    st.markdown("<meta http-equiv='refresh' content='60'>", unsafe_allow_html=True)

# --- Accessibility: Keyboard Navigation Hints & ARIA Labels ---
st.markdown(
        """
        <style>
        /* Visually hidden class for screen readers */
        .sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); border: 0; }
        </style>
        <div class="sr-only" aria-live="polite">
            Use Tab/Shift+Tab to navigate. Press Enter/Space to activate buttons and controls. All controls are accessible by keyboard.
        </div>
        """,
        unsafe_allow_html=True
)
st.markdown(
    """
    <style>
    body, .stApp {
        background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%) !important;
        min-height: 100vh;
        background-size: 400% 400%!important;
        animation: gradientBGmove 30s ease-in-out infinite;
    }
    @keyframes gradientBGmove {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    .stApp {
        background-attachment: fixed !important;
    }
    /* Optional: soften Streamlit main block background for contrast */
    .st-emotion-cache-18ni7ap, .st-emotion-cache-1v0mbdj, .st-emotion-cache-1kyxreq {
        background: rgba(255,255,255,0.85) !important;
        border-radius: 16px !important;
        box-shadow: 0 2px 16px #0001 !important;
        transition: background 0.7s, box-shadow 0.7s, border-radius 0.7s, opacity 0.7s;
        opacity: 0;
        animation: fadeInBlock 1.2s forwards;
    }
    @keyframes fadeInBlock {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    /* Fade in for ticker price boxes */
    .ticker-fade {
        opacity: 0;
        animation: fadeInBlock 1.2s forwards;
        transition: background 0.7s, color 0.7s;
    }
        @media (max-width: 900px) {
            .stApp, body {
                font-size: 0.98em !important;
            }
            .st-emotion-cache-18ni7ap, .st-emotion-cache-1v0mbdj, .st-emotion-cache-1kyxreq {
                padding: 0.5em !important;
                margin: 0.2em !important;
                border-radius: 8px !important;
                max-width: 100vw !important;
                box-shadow: 0 1px 6px #0002 !important;
                background: rgba(255,255,255,0.95) !important;
                overflow-x: auto !important;
                word-break: break-word !important;
            }
        }
        @media (max-width: 600px) {
            .stApp, body {
                font-size: 0.93em !important;
            }
            .st-emotion-cache-18ni7ap, .st-emotion-cache-1v0mbdj, .st-emotion-cache-1kyxreq {
                padding: 0.2em !important;
                margin: 0.1em !important;
                border-radius: 4px !important;
                max-width: 100vw !important;
                box-shadow: 0 1px 3px #0001 !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
)

# --- Data Ingestion with Manual Refresh ---
@st.cache_data(show_spinner=False)
def load_events():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "events.json")
    with open(path) as f:
        data = json.load(f)
    return pd.DataFrame(data["events"]), data.get("last_updated", "N/A")

@st.cache_data(show_spinner=False)
def load_severity_rules():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "severity_rules.json")
    with open(path) as f:
        return json.load(f)

# Manual refresh button and timestamp
# Only show the timestamp (hide Refresh Data button)

events_df, _ = load_events()
rules = load_severity_rules()

# --- Event Scoring (simple keyword-based, can be improved) ---
def score_event(row, rules):
    score = rules.get("default_score", 1)
    text = (row.get("title", "") + " " + row.get("description", "")).lower()
    for level, keywords in rules["keywords"].items():
        for kw in keywords:
            if kw in text:
                if level == "critical":
                    return 40
                elif level == "high":
                    return 30
                elif level == "medium":
                    return 20
                elif level == "low":
                    return 10
    return score

events_df["computed_score"] = events_df.apply(lambda row: score_event(row, rules), axis=1)

# --- Severity Grouping ---
def get_severity_label(score):
    if score >= 40:
        return "CRITICAL"
    elif score >= 30:
        return "HIGH"
    elif score >= 20:
        return "MEDIUM"
    else:
        return "LOW"

events_df["severity_label"] = events_df["computed_score"].apply(get_severity_label)


# --- Ticker Banner ---


# --- Critical Alerts Scrolling News Ticker with Speed Controls ---
import streamlit as st
from datetime import datetime, timedelta

st.session_state['ticker_window_hours'] = 2


# --- Ticker Speed Calculation (marquee: scrollamount=1 is slowest, higher is faster) ---
def calc_ticker_speed(display_value):
    min_scroll = 1   # slowest
    max_scroll = 20  # fastest
    min_v = 0
    max_v = 100
    ratio = max(0, min(1, (display_value - min_v) / (max_v - min_v)))
    scrollamount = int(min_scroll + ratio * (max_scroll - min_scroll))
    return scrollamount



# Lock to 0 (100% slower than 80) on every load
if 'ticker_display_value' not in st.session_state:
    st.session_state['ticker_display_value'] = 0
if 'ticker_speed' not in st.session_state:
    st.session_state['ticker_speed'] = calc_ticker_speed(st.session_state['ticker_display_value'])




def slower_ticker():
    # Decrease display value, recalc speed
    st.session_state['ticker_display_value'] = max(0, st.session_state['ticker_display_value'] - 10)
    st.session_state['ticker_speed'] = calc_ticker_speed(st.session_state['ticker_display_value'])

def faster_ticker():
    # Increase display value, recalc speed
    st.session_state['ticker_display_value'] = min(100, st.session_state['ticker_display_value'] + 10)
    st.session_state['ticker_speed'] = calc_ticker_speed(st.session_state['ticker_display_value'])

def reset_ticker_speed():
    st.session_state['ticker_display_value'] = 0
    st.session_state['ticker_speed'] = calc_ticker_speed(0)

now = datetime.utcnow()
window_hours = st.session_state['ticker_window_hours']
scroll_speed = st.session_state['ticker_speed']
critical_recent = events_df[(events_df["severity_label"] == "CRITICAL") & (pd.to_datetime(events_df["published"], errors='coerce') > now - timedelta(hours=window_hours))]

with st.container():
    st.markdown("<div style='margin-bottom:0.5em;'></div>", unsafe_allow_html=True)
    def speed_emoji(val):
        if val <= 10:
            return '🐢'
        elif val <= 40:
            return '🚶'
        elif val <= 70:
            return '🏃'
        else:
            return '🐇'


        st.markdown("""
        <div id='ticker' class='ticker' role='region' aria-label='Critical alerts ticker'
            style='background:#e0e0e0;border-radius:10px;padding:1vw 1vw 0.5vw 1vw;max-width:520px;margin:auto;box-shadow:0 2px 12px #0002;'>
        """, unsafe_allow_html=True)
    if not critical_recent.empty:
        # Helper functions for icon/category assignment
        def is_airline_disaster(text):
            return any(word in text for word in ["plane crash", "airline crash", "air disaster", "air crash", "aviation accident"])
        def is_natural_disaster(text):
            return any(word in text for word in ["earthquake", "hurricane", "tornado", "flood", "tsunami", "wildfire", "volcano", "landslide"])
        def is_war(text):
            return any(word in text for word in ["war", "invasion", "military conflict", "battle", "airstrike", "missile", "shelling"])
        def is_terrorism(text):
            return any(word in text for word in ["terrorist", "terrorism", "bombing", "suicide attack", "car bomb", "explosion"])
        def is_active_shooter(text):
            return any(word in text for word in ["active shooter", "mass shooting", "gunman", "school shooting"])
        def is_mass_casualty(text, min_casualties=10):
            import re
            match = re.search(r"(\d+) (dead|killed|casualties|injured|wounded)", text)
            return match and int(match.group(1)) >= min_casualties
        def is_stock_swing(text, min_points=50):
            import re
            match = re.search(r"(stock|market|index|shares|price).{0,20}([+-]?\d+\.?\d*)", text)
            if match:
                try:
                    val = float(match.group(2))
                    return abs(val) >= min_points
                except:
                    return False
            return False

        ticker_items = []
        for _, row in critical_recent.iterrows():
            label = row.get('ticker_label')
            category = row.get('ticker_category')
            url = row.get('url')
            title = row.get('title', '')
            description = row.get('description', '')
            text = f"{title} {description}".lower()
            if not label or not category:
                if is_airline_disaster(text):
                    label = f"✈️ {title}"
                    category = 'airline_disaster'
                elif is_natural_disaster(text):
                    label = f"🌪️ {title}"
                    category = 'natural_disaster'
                elif is_war(text):
                    label = f"🪖 {title}"
                    category = 'war'
                elif is_terrorism(text):
                    label = f"💥 {title}"
                    category = 'terrorism'
                elif is_active_shooter(text):
                    label = f"🚨 {title}"
                    category = 'active_shooter'
                elif is_mass_casualty(text, 10):
                    label = f"🚑 {title}"
                    category = 'mass_casualty'
                elif is_stock_swing(text, 50):
                    label = f"📈 {title}"
                    category = 'stock_swing'
                else:
                    label = title
                    category = 'critical'
            # Optionally, make label a link if url exists
            if url:
                item = f"<a href='{url}' target='_blank' style='color:inherit;text-decoration:underline;'><b>{label}</b></a>"
            else:
                item = f"<b>{label}</b>"
            # Add published time for context
            item += f" <span style='color:#888;font-weight:400;'>({row['published']})</span>"
            ticker_items.append(item)
        st.markdown(f"""
        <div class='ticker-inner' style='overflow:hidden;white-space:nowrap;max-width:520px;width:100%;margin:auto;'>
            <marquee behavior='scroll' direction='left' scrollamount='{scroll_speed}' style='font-size:1.1em;color:#b71c1c;font-weight:600;'>
                {' | '.join(ticker_items)}
            </marquee>
        </div>
        """, unsafe_allow_html=True)
    else:
        import requests
        from datetime import datetime as dt
        nowStr = None
        try:
            resp = requests.get("http://worldtimeapi.org/api/timezone/America/Chicago", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                dt_cst = datetime.fromisoformat(data["datetime"][:-1])
                nowStr = dt_cst.strftime('%b %d, %Y %I:%M %p CST')
        except Exception:
            pass
        if not nowStr:
            nowStr = "Unable to fetch CST time. Please check your internet connection or try again later."
        msgs = [
            '🌟 Stay prepared; small actions save lives.',
            '🧭 Verify sources; act responsibly.',
            '🤝 Check in on your community.',
            '💡 Keep an emergency kit stocked.',
            '🫶 Breathe and focus; you’ve got this.'
        ]
def fetch_cst_last_updated():
    try:
        resp = requests.get("http://worldtimeapi.org/api/timezone/America/Chicago", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            dt_cst = datetime.fromisoformat(data["datetime"][:-1])
            return dt_cst.strftime('%b %d, %Y, %I:%M %p CST')
    except Exception:
        pass
    return "ERROR"

st.markdown(f"""
<div class='ticker-inner' style='overflow:hidden;white-space:nowrap;width:100%;'>
    <marquee behavior='scroll' direction='left' scrollamount='{scroll_speed}' style='font-size:1.1em;color:#888;font-weight:600;'>
        {' | '.join(msgs)}
    </marquee>
</div>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

    # Streamlit buttons for widen/reset and ticker speed
    # Removed extra Widen/Reset window buttons; all controls are now in the blue box above.



# --- Minimalist Speed Control and horizontally aligned Stock Price Ticker Boxes with symbol input
speed_col, *stock_cols = st.columns([1,1,1,1])
with speed_col:
    st.markdown("<div style='height:0.5em;'></div>", unsafe_allow_html=True)
    if st.button('🐢', key='slower_btn', help='Slow down ticker (left = slowest)'):
        slower_ticker()
    st.markdown("<div style='height:0.2em;'></div>", unsafe_allow_html=True)
    speed_label = f"Speed: <b style='font-size:1.1em'>{speed_emoji(st.session_state.get('ticker_display_value', 1))}</b>"
    st.markdown(f"<div style='text-align:center;font-size:1em;margin:0;'>{speed_label}</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:0.2em;'></div>", unsafe_allow_html=True)
    if st.button('🐇', key='faster_btn', help='Speed up ticker (right = fastest)'):
        faster_ticker()
    st.markdown("<div style='height:0.2em;'></div>", unsafe_allow_html=True)

# --- Live Stock Price Fetching for Ticker Inputs with Suggestions, Pre-population, Help, and Favorites ---
ticker_inputs = []
# Suggestions for ticker symbols
symbol_suggestions = [
    ("KO", "Coca-Cola"),
    ("AAPL", "Apple"),
    ("MSFT", "Microsoft"),
    ("TSLA", "Tesla"),
    ("T", "AT&T"),
    ("F", "Ford"),
    ("GOOGL", "Alphabet"),
    ("AMZN", "Amazon"),
    ("NVDA", "Nvidia")
]

# Small help text above ticker inputs (no star/favorite reference)
st.markdown("""
<div style='font-size:0.97em; color:#bbb; margin-bottom:0.2em;'>
    <b>Stock Ticker Watchlist:</b> Enter a valid stock symbol (e.g., <span style='color:#fff;background:#444;padding:0 0.2em;border-radius:3px;'>AAPL</span>, <span style='color:#fff;background:#444;padding:0 0.2em;border-radius:3px;'>KO</span>, <span style='color:#fff;background:#444;padding:0 0.2em;border-radius:3px;'>TSLA</span>).<br>
    The price and trend arrow update live. Market closed = black background. <br>
    <span style='color:#888;'>Examples: KO (Coca-Cola), AAPL (Apple), T (AT&amp;T), F (Ford), MSFT (Microsoft)</span>
</div>
""", unsafe_allow_html=True)

# --- Ticker symbol input and price display (no star/favorite) ---
for i, col in enumerate(stock_cols):
    with col:
        # Pre-populate first input with KO, others blank
        default_val = "KO" if i == 0 else ""
        # Suggestion text for each input
        suggestion = symbol_suggestions[i][0] + f" ({symbol_suggestions[i][1]})" if i < len(symbol_suggestions) else "Ticker Symbol"
        ticker_input = st.text_input(
            f"Symbol {i+1}",
            value=default_val,
            key=f"ticker_input_{i+1}",
            max_chars=8,
            help=f"Enter ticker symbol, e.g. {suggestion}."
        )
        symbol = ticker_input.strip().upper()
        price = None
        prev_close = None
        market_open = None
        error = None
        arrow = ''
        color = '#888'  # default gray
        box_bg = '#23272e'  # dark background
        text_color = '#222'  # default text color
        if symbol:
            try:
                ticker = yf.Ticker(symbol)
                # Try fast_info first
                price = ticker.fast_info["last_price"] if hasattr(ticker, "fast_info") and ticker.fast_info else None
                prev_close = ticker.fast_info["previous_close"] if hasattr(ticker, "fast_info") and ticker.fast_info else None
                market_open = ticker.fast_info.get("market_open") if hasattr(ticker, "fast_info") and ticker.fast_info else None
                # Fallback to info dict
                if price is None:
                    price = ticker.info.get("regularMarketPrice")
                if prev_close is None:
                    prev_close = ticker.info.get("previousClose")
                if market_open is None:
                    market_open = ticker.info.get("marketState", "").upper() == "REGULAR"
                # Determine up/down/unchanged
                if price is not None and prev_close is not None:
                    if price > prev_close:
                        arrow = '▲'
                        color = '#2ecc40'  # green
                    elif price < prev_close:
                        arrow = '▼'
                        color = '#d7263d'  # red
                    else:
                        arrow = '→'
                        color = '#888'  # unchanged
                elif price is not None:
                    arrow = ''
                    color = '#888'
                else:
                    error = "N/A"
                # Market open/closed formatting
                if market_open is not None and not market_open:
                    box_bg = '#111'  # black background
                    text_color = '#fff'
            except Exception:
                error = "N/A"
        display_price = f"${price:,.2f}" if price is not None else (error if error else "$---.--")
        # Pad ticker symbol to at least 3 chars for alignment, using invisible chars if needed
        display_symbol = symbol if symbol else f'TICKER{i+1}'
        if len(display_symbol) < 3:
            # Add invisible underscores to pad width
            pad = 3 - len(display_symbol)
            display_symbol += f"<span style='opacity:0;'>{'_'*pad}</span>"
        st.markdown(f"""
        <div class='ticker-fade' style='max-width:120px; margin:0.5em auto; border:1px solid #222; border-radius:8px; padding:0.5rem 1rem; background:{box_bg}; text-align:center;' aria-label='Stock price for {display_symbol}'>
            <b style='color:{text_color if box_bg=="#111" else '#fff'}; font-family:monospace; min-width:2.5em; display:inline-block;'>{display_symbol}</b>: <span style='color:{color if box_bg!="#111" else text_color};font-weight:600;'>{display_price} {arrow}</span>
        </div>
        """, unsafe_allow_html=True)
        ticker_inputs.append(ticker_input)

# --- Summary Bar ---
total_events = len(events_df)
critical_count = (events_df["severity_label"] == "CRITICAL").sum()
high_count = (events_df["severity_label"] == "HIGH").sum()
medium_count = (events_df["severity_label"] == "MEDIUM").sum()
low_count = (events_df["severity_label"] == "LOW").sum()


# --- Timezone Setup (must be before formatting functions) ---
import tzlocal
try:
    local_tz = tzlocal.get_localzone()
except Exception:
    local_tz = None


# Always use current UTC time for last_updated






last_updated_fmt = fetch_cst_last_updated()
st.markdown(f"""
<div style='background:#f8f9fa;border-radius:8px;padding:0.7em 1em;margin-bottom:1em;display:flex;gap:2em;align-items:center;'>
    <b>🗂️ {total_events} Total Events</b>
    <span style='color:#d7263d'><b>{critical_count} Critical</b></span>
    <span style='color:#f49d37'><b>{high_count} High</b></span>
    <span style='color:#3f88c5'><b>{medium_count} Medium</b></span>
    <span style='color:#43aa8b'><b>{low_count} Low</b></span>
</div>
""", unsafe_allow_html=True)


st.markdown("""
<div style='margin:0.5em 0 1em 0; padding:0.7em 1em; background:rgba(255,255,255,0.7); border-radius:10px; font-size:0.98em; max-width:900px;'>
    <b>Legend:</b>
    <span style='margin-right:1em;'><span style='color:#2ecc40;'>▲</span>/<span style='color:#d7263d;'>▼</span>: Price up/down</span>
    <span style='margin-right:1em;'>🐢/🐇: Ticker speed slow/fast</span>
    <span style='margin-right:1em;'><span style='color:#d7263d;'>Critical</span>, <span style='color:#f49d37;'>High</span>, <span style='color:#3f88c5;'>Medium</span>, <span style='color:#43aa8b;'>Low</span>: Severity</span>
    <span style='margin-right:1em;'>Black box: Market closed</span>
    <span style='margin-right:1em;'>📝: Watchlist</span>
    <span style='margin-right:1em;'>ℹ️: Info</span>
    <span style='margin-right:1em;'>⚠️: Warning</span>
</div>
""", unsafe_allow_html=True)
helper_col1, helper_col2, helper_col3 = st.columns(3)
# Helper info boxes removed for production cleanup


# --- Event Filter Buttons ---
st.markdown("""
<div class='filters' style='display:flex;gap:0.5em;margin-bottom:1.2em;'>
    <style>
    .filter-btn {padding:0.4em 1.1em;border-radius:5px;border:none;background:#f8f9fa;color:#333;font-weight:500;cursor:pointer;transition:background 0.2s;}
    .filter-btn.active {background:#3f88c5;color:#fff;}
    .filter-btn.critical {background:#d7263d;color:#fff;}
    .filter-btn.high {background:#f49d37;color:#fff;}
    .filter-btn.medium {background:#3f88c5;color:#fff;}
    .filter-btn.low {background:#43aa8b;color:#fff;}
    </style>
</div>
""", unsafe_allow_html=True)

filter_map = {
    "All Events": None,
    "Critical": "CRITICAL",
    "High": "HIGH",
    "Medium": "MEDIUM",
    "Low": "LOW"
}
filter_labels = list(filter_map.keys())
selected = st.radio(
    label="Filter events by severity:",
    options=filter_labels,
    index=0,
    horizontal=True,
    key="event_filter_radio"
)

def event_card(row):
    sev_color = {
        "CRITICAL": "#d7263d",
        "HIGH": "#f49d37",
        "MEDIUM": "#3f88c5",
        "LOW": "#43aa8b"
    }[row["severity_label"]]
    title = row["title"]
    url = row.get("url", "")
    if url and url.startswith("http"):
        title_md = f"<a href='{url}' target='_blank' rel='noopener noreferrer'>{url}</a>"
    else:
        title_md = title
    desc = row.get("description", "")
    source = row.get("source", "Unknown")
    score = row["computed_score"]
    label = row["severity_label"]
    # Format published date/time in user's local timezone
    # Prefer story_published if available
    ts = row.get("story_published_dt")
    if pd.notnull(ts):
        if local_tz is not None:
            ts_local = ts.tz_convert(local_tz) if ts.tzinfo else ts.tz_localize('UTC').tz_convert(local_tz)
            ts_str = ts_local.strftime("%b %d, %Y, %I:%M %p (%Z)")
        else:
            ts_str = ts.strftime("%b %d, %Y, %I:%M %p UTC")
    else:
        # Fallback to published_dt
        ts = row.get("published_dt")
        if pd.notnull(ts):
            if local_tz is not None:
                ts_local = ts.tz_convert(local_tz) if ts.tzinfo else ts.tz_localize('UTC').tz_convert(local_tz)
                ts_str = ts_local.strftime("%b %d, %Y, %I:%M %p (%Z)")
            else:
                ts_str = ts.strftime("%b %d, %Y, %I:%M %p UTC")
        else:
            ts_str = "Unknown time"
    return f"""
<div style='border-left:6px solid {sev_color};background:#fff;border-radius:6px;padding:1em 1.2em;margin-bottom:1.1em;box-shadow:0 1px 4px #0001;'>
    <div style='font-size:1.15rem;margin-bottom:0.15em;font-weight:600;'>{title_md}</div>
    <div style='font-size:0.98rem;color:#444;margin-bottom:0.25em;'>{desc}</div>
    <div style='font-size:0.93rem;color:#888;'>
        <b style='color:{sev_color}'>{label}</b> | 📰 {source} | <b>Score:</b> {score}
    </div>
    <div style='font-size:0.93rem;color:#888;margin-top:0.15em;'>🕒 <a href='{url}' target='_blank' rel='noopener noreferrer'>{ts_str}</a></div>
</div>
"""


# --- Filter to last 24 hours and sort by most recent ---
def parse_time(ts):
    import re
    try:
        # Remove unrecognized timezone abbreviations (e.g., 'EST', 'PST')
        if isinstance(ts, str):
            # Remove trailing timezone abbreviation if present
            ts_clean = re.sub(r"\s([A-Z]{2,4})$", "", ts)
        else:
            ts_clean = ts
        return pd.to_datetime(ts_clean, utc=True)
    except Exception:
        return pd.NaT

import tzlocal
from datetime import datetime, timedelta

# Get user's local timezone
try:
    local_tz = tzlocal.get_localzone()
except Exception:
    local_tz = None

now_utc = pd.Timestamp.utcnow()
events_df["published_dt"] = events_df["published"].apply(parse_time)
# Parse story_published if present
if "story_published" in events_df.columns:
    events_df["story_published_dt"] = events_df["story_published"].apply(parse_time)
else:
    events_df["story_published_dt"] = pd.NaT
recent_cutoff = now_utc - pd.Timedelta(hours=24)
# Use story_published_dt if available, else published_dt
events_df["display_dt"] = events_df["story_published_dt"].combine_first(events_df["published_dt"])
recent_df = events_df[events_df["display_dt"] >= recent_cutoff].copy()
recent_df = recent_df.sort_values("display_dt", ascending=False)

# Filter events by selected severity

# Sort order for severity
severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}

if filter_map[selected]:
    filtered_df = recent_df[recent_df["severity_label"] == filter_map[selected]]
    filtered_df = filtered_df.sort_values("display_dt", ascending=False)
else:
    # All Events: sort by severity, then by most recent
    filtered_df = recent_df.copy()
    filtered_df["severity_rank"] = filtered_df["severity_label"].map(severity_order)
    filtered_df = filtered_df.sort_values(["severity_rank", "display_dt"], ascending=[True, False])

if filtered_df.empty:
    st.info("No events found for this filter in the last 24 hours.")
else:
    for _, row in filtered_df.iterrows():
        # Format time/date stamp in user's local timezone
        ts = row.get("published_dt")
        if pd.notnull(ts):
            if local_tz is not None:
                ts_local = ts.tz_convert(local_tz) if ts.tzinfo else ts.tz_localize('UTC').tz_convert(local_tz)
                ts_str = ts_local.strftime("%b %d, %Y, %I:%M %p (%Z)")
            else:
                ts_str = ts.strftime("%b %d, %Y, %I:%M %p UTC")
        else:
            ts_str = "Unknown time"
        card_html = event_card(row)
        st.markdown(card_html, unsafe_allow_html=True)

# --- Footer ---
st.markdown("""
<hr style='margin-top:2em;margin-bottom:0.5em;'>
<div style='font-size:1.05rem;color:#888;'>
  Data sourced from multiple news feeds | Updates every hour<br>
  <span style='font-size:0.95em;'>Built with ❤️ for crisis awareness</span>
</div>
""", unsafe_allow_html=True)
