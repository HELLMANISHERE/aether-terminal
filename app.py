import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from supabase import create_client, Client

# =========================================================
# 1. PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="⚡ Aether Terminal",
    page_icon="🎛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# 2. SUPABASE CLIENT INITIALIZATION
# =========================================================
# Requires SUPABASE_URL and SUPABASE_KEY in .streamlit/secrets.toml
# (or the Streamlit Cloud Secrets manager).
#
# Expected schema — create these tables in the Supabase SQL editor
# if they don't already exist:
#
#   create table profiles (
#       username text primary key,
#       available_cash numeric not null default 100000.0
#   );
#
#   create table transactions (
#       id bigint generated always as identity primary key,
#       username text not null,
#       ticker text not null,
#       trade_type text not null,          -- 'BUY' or 'SELL'
#       quantity numeric not null,
#       execution_price numeric not null,
#       total_value numeric not null,
#       created_at timestamptz not null default now()
#   );
#
# This app assumes a single hardcoded user, 'default_trader'. Multi-user
# support would require swapping this constant for real auth (e.g. Supabase
# Auth + st.session_state for the logged-in identity).
USERNAME = "default_trader"
STARTING_CASH = 100000.0

@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase = init_supabase()
    DB_AVAILABLE = True
except Exception as e:
    DB_AVAILABLE = False
    st.error(
        "⚠️ Could not connect to Supabase. Check that SUPABASE_URL and "
        "SUPABASE_KEY are set correctly in your Streamlit secrets."
    )
    st.exception(e)
    st.stop()


# =========================================================
# 3. DESIGN SYSTEM — APPLE x LINEAR x STRIPE (unchanged)
# =========================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background-color: #050508;
    }

    #MainMenu, footer, header[data-testid="stHeader"] {
        background-color: transparent;
    }
    div[data-testid="stDecoration"] {
        display: none;
    }
    div.block-container {
        padding-top: 2rem;
    }

    section[data-testid="stSidebar"] {
        background-color: #050508;
        border-right: 1px solid #14171D;
    }
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        color: #F5F6F8;
        letter-spacing: -0.2px;
    }

    div[data-testid="stMetric"] {
        background-color: #0D0E12;
        border: 1px solid #1F242E;
        border-radius: 12px;
        padding: 18px 20px 16px 20px;
    }
    div[data-testid="stMetricLabel"] {
        color: #6E7480;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    div[data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 25px;
    }
    div[data-testid="stMetricDelta"] {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
    }

    .hud-card {
        background-color: #0D0E12;
        border: 1px solid #1F242E;
        border-radius: 12px;
        padding: 18px 20px 16px 20px;
        transition: border-color 0.2s ease;
    }
    .hud-label {
        color: #6E7480;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    .hud-value {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 25px;
        margin-top: 5px;
    }
    .hud-sub {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        font-size: 13px;
        margin-top: 3px;
    }
    .glow-green {
        color: #00FFA3;
        text-shadow: 0 0 18px rgba(0, 255, 163, 0.35);
    }
    .glow-red {
        color: #FF3366;
        text-shadow: 0 0 18px rgba(255, 51, 102, 0.35);
    }

    h1 {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        letter-spacing: -1.2px;
        color: #F5F6F8;
    }
    h2, h3, h4 {
        font-family: 'Inter', sans-serif;
        color: #F5F6F8;
        font-weight: 700;
        letter-spacing: -0.3px;
    }

    button[data-baseweb="tab"] {
        font-size: 14.5px;
        font-weight: 600;
        color: #6E7480;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #5E8BFF;
    }
    div[data-baseweb="tab-highlight"] {
        background-color: #5E8BFF;
    }
    div[data-baseweb="tab-border"] {
        background-color: #14171D;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #1F242E;
        border-radius: 10px;
        overflow: hidden;
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input {
        background-color: #0D0E12;
        border: 1px solid #1F242E;
        color: #F5F6F8;
        font-family: 'JetBrains Mono', monospace;
    }

    div.order-panel button[kind="primary"] {
        background-color: #00FFA3 !important;
        color: #050508 !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 800 !important;
        font-size: 15px !important;
        padding: 13px 0 !important;
        letter-spacing: 0.3px;
    }
    div.order-panel button[kind="secondary"] {
        background-color: #FF3366 !important;
        color: #050508 !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 800 !important;
        font-size: 15px !important;
        padding: 13px 0 !important;
        letter-spacing: 0.3px;
    }

    .watchlist-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 2px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        border-bottom: 1px solid #14171D;
    }
    .watchlist-ticker {
        color: #F5F6F8;
        font-weight: 600;
    }
    .watchlist-price {
        color: #C2C6CE;
    }

    hr {
        border-color: #14171D;
    }

    [data-testid="stCaptionContainer"] {
        color: #6E7480 !important;
    }

    .sentiment-box {
        background-color: #0D0E12;
        border: 1px solid #1F242E;
        border-left: 3px solid #5E8BFF;
        border-radius: 10px;
        padding: 20px 22px;
        font-family: 'Inter', sans-serif;
        line-height: 1.6;
    }
    .sentiment-tag {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 12px;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        padding: 4px 10px;
        border-radius: 6px;
        display: inline-block;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("# ⚡ Aether Terminal")
st.caption("A hyper-minimalist financial command center · Live data · Supabase-backed persistence")

# =========================================================
# 4. SUPABASE DATA ACCESS LAYER
# =========================================================
# All reads/writes go through these functions. Nothing about portfolio,
# cash, or trade history lives in st.session_state anymore — Supabase is
# the single source of truth, queried fresh on every rerun.

def get_or_create_profile(username: str) -> float:
    """Fetch available_cash for a user. If no profile row exists yet
    (first-ever run), create one seeded with STARTING_CASH."""
    response = supabase.table("profiles").select("*").eq("username", username).execute()

    if response.data and len(response.data) > 0:
        return float(response.data[0]["available_cash"])

    # No profile yet — create one
    supabase.table("profiles").insert({
        "username": username,
        "available_cash": STARTING_CASH,
    }).execute()
    return STARTING_CASH


def update_cash_balance(username: str, new_cash: float):
    """Persist the user's updated cash balance back to the profiles table."""
    supabase.table("profiles").update({
        "available_cash": new_cash,
    }).eq("username", username).execute()


def fetch_transactions(username: str) -> pd.DataFrame:
    """Fetch the full transaction history for a user, oldest first."""
    response = (
        supabase.table("transactions")
        .select("*")
        .eq("username", username)
        .order("created_at", desc=False)
        .execute()
    )
    if not response.data:
        return pd.DataFrame(columns=[
            "id", "username", "ticker", "trade_type",
            "quantity", "execution_price", "total_value", "created_at"
        ])
    return pd.DataFrame(response.data)


def insert_transaction(username, ticker, trade_type, quantity, execution_price, total_value):
    """Write a single trade row to the transactions table."""
    supabase.table("transactions").insert({
        "username": username,
        "ticker": ticker,
        "trade_type": trade_type,
        "quantity": quantity,
        "execution_price": execution_price,
        "total_value": total_value,
    }).execute()


def reset_account(username: str):
    """Wipe all transactions and reset cash to STARTING_CASH for this user."""
    supabase.table("transactions").delete().eq("username", username).execute()
    supabase.table("profiles").update({
        "available_cash": STARTING_CASH,
    }).eq("username", username).execute()


def compute_holdings_from_transactions(tx_df: pd.DataFrame) -> dict:
    """Replay the full transaction log chronologically to derive net shares
    owned and weighted-average cost basis per ticker. This is the
    'transactions are the source of truth, portfolio is a derived view'
    pattern — there is no separately-stored portfolio table.

    Returns: { ticker: {"shares": float, "avg_cost": float} }
    """
    holdings = {}

    if tx_df.empty:
        return holdings

    for _, row in tx_df.iterrows():
        tkr = row["ticker"]
        qty = float(row["quantity"])
        price = float(row["execution_price"])
        trade_type = row["trade_type"]

        if tkr not in holdings:
            holdings[tkr] = {"shares": 0.0, "avg_cost": 0.0}

        position = holdings[tkr]

        if trade_type == "BUY":
            old_shares = position["shares"]
            old_avg_cost = position["avg_cost"]
            new_shares = old_shares + qty
            # Weighted average cost basis across all BUYs
            new_avg_cost = ((old_shares * old_avg_cost) + (qty * price)) / new_shares if new_shares > 0 else 0.0
            position["shares"] = new_shares
            position["avg_cost"] = new_avg_cost

        elif trade_type == "SELL":
            # Selling reduces share count but does NOT change avg_cost —
            # cost basis of remaining shares is unaffected by a sale.
            position["shares"] -= qty

    # Drop tickers fully closed out (0 or negative shares from a sell)
    holdings = {t: p for t, p in holdings.items() if p["shares"] > 1e-9}
    return holdings


def compute_realized_pnl(tx_df: pd.DataFrame) -> list:
    """Replay transactions chronologically to compute realized P&L for each
    SELL, using the running average cost basis at the moment of that sale.
    This mirrors compute_holdings_from_transactions but tracks P&L per SELL
    row, which is needed for Win Rate and Performance Insights."""
    running = {}  # ticker -> {"shares": float, "avg_cost": float}
    realized_trades = []

    if tx_df.empty:
        return realized_trades

    for _, row in tx_df.iterrows():
        tkr = row["ticker"]
        qty = float(row["quantity"])
        price = float(row["execution_price"])
        trade_type = row["trade_type"]

        if tkr not in running:
            running[tkr] = {"shares": 0.0, "avg_cost": 0.0}

        position = running[tkr]

        if trade_type == "BUY":
            old_shares = position["shares"]
            old_avg_cost = position["avg_cost"]
            new_shares = old_shares + qty
            new_avg_cost = ((old_shares * old_avg_cost) + (qty * price)) / new_shares if new_shares > 0 else 0.0
            position["shares"] = new_shares
            position["avg_cost"] = new_avg_cost

        elif trade_type == "SELL":
            cost_basis_per_share = position["avg_cost"]
            realized_dollar = (price - cost_basis_per_share) * qty
            realized_pct = ((price - cost_basis_per_share) / cost_basis_per_share * 100) if cost_basis_per_share > 0 else 0.0
            realized_trades.append({
                "Ticker": tkr,
                "Quantity": qty,
                "Execution Price": price,
                "Realized P&L ($)": realized_dollar,
                "Realized P&L (%)": realized_pct,
            })
            position["shares"] -= qty

    return realized_trades


def calculate_win_rate(realized_trades: list):
    if not realized_trades:
        return None, 0, 0
    wins = sum(1 for t in realized_trades if t["Realized P&L ($)"] > 0)
    total = len(realized_trades)
    return (wins / total * 100), wins, total


# =========================================================
# 5. MARKET DATA HELPERS (unchanged — yfinance, not DB-backed)
# =========================================================
@st.cache_data(ttl=60)
def fetch_history(ticker_symbol: str, period: str = "3mo", interval: str = "1d"):
    stock = yf.Ticker(ticker_symbol)
    return stock.history(period=period, interval=interval)


def get_current_price(ticker_symbol: str):
    try:
        hist = fetch_history(ticker_symbol, "3mo")
        if hist.empty:
            return None, hist
        return float(hist["Close"].iloc[-1]), hist
    except Exception:
        return None, pd.DataFrame()


@st.cache_data(ttl=60)
def get_macro_quote(ticker_symbol: str):
    try:
        hist = yf.Ticker(ticker_symbol).history(period="5d")
        if len(hist) < 2:
            return None, None
        last = float(hist["Close"].iloc[-1])
        prev = float(hist["Close"].iloc[-2])
        pct = (last - prev) / prev * 100
        return last, pct
    except Exception:
        return None, None


def get_live_prices_for_holdings(holdings: dict):
    prices = {}
    for tkr in holdings:
        price, _ = get_current_price(tkr)
        prices[tkr] = price if price is not None else 0.0
    return prices


def render_hud_card(label, value_str, sub_str=None, glow=None):
    glow_class = f"glow-{glow}" if glow else ""
    sub_html = f'<div class="hud-sub {glow_class}">{sub_str}</div>' if sub_str else ""
    st.markdown(
        f"""
        <div class="hud-card">
            <div class="hud-label">{label}</div>
            <div class="hud-value {glow_class}">{value_str}</div>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# 6. TRADE EXECUTION (writes to Supabase, no session_state)
# =========================================================
def execute_buy(username, tkr, qty, price, current_cash):
    if not price:
        st.error("Can't buy — invalid ticker price.")
        return False
    total_cost = price * qty
    if current_cash < total_cost:
        st.error("Not enough cash for this trade.")
        return False

    insert_transaction(username, tkr, "BUY", qty, price, total_cost)
    update_cash_balance(username, current_cash - total_cost)
    st.toast(f"Bought {qty} shares of {tkr} @ ${price:.2f}", icon="✅")
    return True


def execute_sell(username, tkr, qty, price, current_cash, holdings):
    if not price:
        st.error("Can't sell — invalid ticker price.")
        return False
    position = holdings.get(tkr)
    if not position or position["shares"] < qty:
        st.error("You don't own enough shares to sell.")
        return False

    total_return = price * qty
    insert_transaction(username, tkr, "SELL", qty, price, total_return)
    update_cash_balance(username, current_cash + total_return)
    st.toast(f"Sold {qty} shares of {tkr} @ ${price:.2f}", icon="💰")
    return True


# =========================================================
# 7. SESSION STATE — UI-ONLY STATE (not financial data)
# =========================================================
# Note: cash, holdings, and trade history are now fully DB-backed and are
# NOT stored here. The only thing kept in session_state is which ticker is
# currently selected in the chart panel — pure UI state, fine to lose on
# refresh, and irrelevant to data integrity.
if "active_ticker" not in st.session_state:
    st.session_state.active_ticker = "AAPL"


# =========================================================
# 8. SIDEBAR — GLOBAL LIQUIDITY TRACKER (macro-only, unchanged)
# =========================================================
with st.sidebar:
    st.markdown("## 🌐 Global Liquidity")
    st.caption("Live macro pulse")
    st.markdown("")

    macro_assets = [
        ("S&P 500", "^GSPC"),
        ("NASDAQ", "^IXIC"),
        ("BITCOIN", "BTC-USD"),
        ("ETHEREUM", "ETH-USD"),
    ]

    for label, sym in macro_assets:
        price, pct = get_macro_quote(sym)
        if price is not None:
            color = "#00FFA3" if pct >= 0 else "#FF3366"
            sign = "+" if pct >= 0 else ""
            st.markdown(
                f"""
                <div class="watchlist-row">
                    <span class="watchlist-ticker">{label}</span>
                    <span class="watchlist-price">{price:,.2f}
                        <span style="color:{color}; font-weight:700;">{sign}{pct:.2f}%</span>
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="watchlist-row"><span class="watchlist-ticker">{label}</span>'
                f'<span style="color:#6E7480;">N/A</span></div>',
                unsafe_allow_html=True,
            )

    st.markdown("---")
    st.caption(f"Aether Terminal · {USERNAME} · Supabase-backed")

    if st.button("♻️ Reset Account", use_container_width=True):
        reset_account(USERNAME)
        st.cache_data.clear()
        st.rerun()


# =========================================================
# 9. PULL LIVE STATE FROM SUPABASE (fresh every rerun)
# =========================================================
current_cash = get_or_create_profile(USERNAME)
tx_df = fetch_transactions(USERNAME)
holdings = compute_holdings_from_transactions(tx_df)
realized_trades = compute_realized_pnl(tx_df)

live_prices = get_live_prices_for_holdings(holdings)

holdings_value = 0.0
total_cost_basis = 0.0
portfolio_rows = []

for tkr, position in holdings.items():
    sh = position["shares"]
    avg_cost = position["avg_cost"]
    live_price = live_prices.get(tkr, 0.0)

    market_value = sh * live_price
    cost_basis = sh * avg_cost
    pnl_dollar = market_value - cost_basis
    pnl_pct = (pnl_dollar / cost_basis * 100) if cost_basis > 0 else 0.0

    holdings_value += market_value
    total_cost_basis += cost_basis

    portfolio_rows.append({
        "Ticker": tkr,
        "Shares": sh,
        "Average Cost": avg_cost,
        "Live Price": live_price,
        "Total Invested": cost_basis,
        "Market Value": market_value,
        "Live P&L ($)": pnl_dollar,
        "Live P&L (%)": pnl_pct,
    })

total_portfolio_value = current_cash + holdings_value
overall_pnl_dollar = total_portfolio_value - STARTING_CASH
overall_pnl_pct = (overall_pnl_dollar / STARTING_CASH * 100) if STARTING_CASH else 0.0

win_rate, win_count, closed_count = calculate_win_rate(realized_trades)


# =========================================================
# 10. HUD — 4 GLOWING WIDGETS
# =========================================================
h1, h2, h3, h4 = st.columns(4)

with h1:
    render_hud_card("TOTAL PORTFOLIO LIQUIDITY", f"${total_portfolio_value:,.2f}")

with h2:
    render_hud_card("AVAILABLE BUYING POWER", f"${current_cash:,.2f}")

with h3:
    glow = "green" if overall_pnl_dollar >= 0 else "red"
    sign = "+" if overall_pnl_dollar >= 0 else "-"
    render_hud_card(
        "NET OPEN RETURNS",
        f"{sign}${abs(overall_pnl_dollar):,.2f}",
        f"{sign}{abs(overall_pnl_pct):.2f}%",
        glow=glow,
    )

with h4:
    if win_rate is None:
        render_hud_card("WIN RATE & EFFICIENCY", "—", "No closed trades yet")
    else:
        glow = "green" if win_rate >= 50 else "red"
        render_hud_card(
            "WIN RATE & EFFICIENCY",
            f"{win_rate:.1f}%",
            f"{win_count} / {closed_count} closed",
            glow=glow,
        )

st.markdown("---")

# =========================================================
# 11. MAIN TERMINAL — CHART (3.2) + ORDER PANEL (0.8)
# =========================================================
chart_col, order_col = st.columns([3.2, 0.8])

with chart_col:
    ticker_input = st.text_input(
        "Symbol", value=st.session_state.active_ticker, label_visibility="collapsed",
        placeholder="Enter ticker — e.g. AAPL, TSLA, MSFT",
    ).upper().strip()
    st.session_state.active_ticker = ticker_input if ticker_input else st.session_state.active_ticker
    active_ticker = st.session_state.active_ticker

    current_price, historical_data = (None, pd.DataFrame())
    if active_ticker:
        current_price, historical_data = get_current_price(active_ticker)

    st.markdown(f"#### {active_ticker} · 3-Month Chart")

    if current_price and not historical_data.empty:
        hist = historical_data.copy()
        hist["EMA20"] = hist["Close"].ewm(span=20, adjust=False).mean()

        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            row_heights=[0.75, 0.25],
            vertical_spacing=0.03,
        )

        fig.add_trace(
            go.Candlestick(
                x=hist.index,
                open=hist["Open"],
                high=hist["High"],
                low=hist["Low"],
                close=hist["Close"],
                name=active_ticker,
                increasing_line_color="#00FFA3",
                decreasing_line_color="#FF3366",
                increasing_fillcolor="#00FFA3",
                decreasing_fillcolor="#FF3366",
            ),
            row=1, col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=hist.index, y=hist["EMA20"],
                line=dict(color="#5E8BFF", width=1.8),
                name="EMA 20",
            ),
            row=1, col=1,
        )

        volume_colors = [
            "#00FFA3" if c >= o else "#FF3366"
            for o, c in zip(hist["Open"], hist["Close"])
        ]
        fig.add_trace(
            go.Bar(
                x=hist.index, y=hist["Volume"],
                marker_color=volume_colors,
                name="Volume",
                showlegend=False,
            ),
            row=2, col=1,
        )

        fig.update_layout(
            height=560,
            template="plotly_dark",
            paper_bgcolor="#050508",
            plot_bgcolor="#050508",
            font=dict(family="JetBrains Mono, monospace", color="#C2C6CE"),
            xaxis_rangeslider_visible=False,
            margin=dict(l=10, r=10, t=20, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
        )
        fig.update_xaxes(gridcolor="#14171D", row=1, col=1)
        fig.update_xaxes(gridcolor="#14171D", row=2, col=1)
        fig.update_yaxes(gridcolor="#14171D", row=1, col=1, title_text="Price (USD)")
        fig.update_yaxes(gridcolor="#14171D", row=2, col=1, title_text="Volume")

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Enter a valid ticker above to load the chart.")

with order_col:
    st.markdown("#### Order")
    st.markdown('<div class="order-panel">', unsafe_allow_html=True)

    order_qty = st.number_input("Qty", min_value=1, value=5, step=1, key="order_qty", label_visibility="collapsed")

    if current_price:
        st.markdown(
            f"""
            <div class="hud-card" style="margin: 10px 0 14px 0;">
                <div class="hud-label">{active_ticker}</div>
                <div class="hud-value" style="font-size:19px;">${current_price:,.2f}</div>
                <div class="hud-sub" style="color:#6E7480; font-weight:500;">
                    Cost: ${current_price * order_qty:,.2f}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.error("Invalid ticker.")

    order_buy = st.button("BUY", use_container_width=True, type="primary", key="order_buy_btn")
    order_sell = st.button("SELL", use_container_width=True, type="secondary", key="order_sell_btn")

    st.markdown('</div>', unsafe_allow_html=True)

    # On any trade: write to Supabase, then rerun so every figure on the
    # page (HUD, holdings grid, ledger) re-reads fresh data from the DB.
    if order_buy:
        if execute_buy(USERNAME, active_ticker, order_qty, current_price, current_cash):
            st.rerun()
    if order_sell:
        if execute_sell(USERNAME, active_ticker, order_qty, current_price, current_cash, holdings):
            st.rerun()

st.markdown("---")

# =========================================================
# 12. ANALYTICAL GRID & LEDGER — TABS
# =========================================================
tab1, tab2, tab3 = st.tabs(["💼 Active Holdings Grid", "📜 Order Ledger", "🧠 AI Trader Sentiment"])

# ---------------------------------------------------------
# TAB 1 — ACTIVE HOLDINGS GRID (derived from transactions table)
# ---------------------------------------------------------
with tab1:
    st.markdown("#### Active Holdings")

    if portfolio_rows:
        df = pd.DataFrame(portfolio_rows)

        def style_pnl(row):
            color = "#00FFA3" if row["Live P&L ($)"] >= 0 else "#FF3366"
            return [f"color: {color}" if col in ("Live P&L ($)", "Live P&L (%)") else "" for col in row.index]

        styled = df.style.apply(style_pnl, axis=1).format({
            "Average Cost": "${:,.2f}",
            "Live Price": "${:,.2f}",
            "Total Invested": "${:,.2f}",
            "Market Value": "${:,.2f}",
            "Live P&L ($)": "${:,.2f}",
            "Live P&L (%)": "{:,.2f}%",
        })

        st.dataframe(styled, use_container_width=True, hide_index=True)

        st.markdown("")
        c1, c2 = st.columns(2)
        with c1:
            render_hud_card("TOTAL HOLDINGS VALUE", f"${holdings_value:,.2f}")
        with c2:
            unrealized = holdings_value - total_cost_basis
            unrealized_pct = (unrealized / total_cost_basis * 100) if total_cost_basis > 0 else 0.0
            glow = "green" if unrealized >= 0 else "red"
            sign = "+" if unrealized >= 0 else "-"
            render_hud_card(
                "UNREALIZED P&L",
                f"{sign}${abs(unrealized):,.2f}",
                f"{sign}{abs(unrealized_pct):.2f}%",
                glow=glow,
            )
    else:
        st.info("You don't own any stocks yet. Use the order panel to place your first trade.")

# ---------------------------------------------------------
# TAB 2 — ORDER LEDGER (raw transactions table, newest first)
# ---------------------------------------------------------
with tab2:
    st.markdown("#### Order Ledger")

    if not tx_df.empty:
        ledger_view = tx_df.sort_values("created_at", ascending=False)[
            ["created_at", "ticker", "trade_type", "quantity", "execution_price", "total_value"]
        ].rename(columns={
            "created_at": "Timestamp",
            "ticker": "Asset Ticker",
            "trade_type": "Action Type",
            "quantity": "Quantity",
            "execution_price": "Execution Price",
            "total_value": "Total Value",
        })

        st.dataframe(
            ledger_view,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Timestamp": st.column_config.TextColumn("Timestamp"),
                "Asset Ticker": st.column_config.TextColumn("Asset Ticker"),
                "Action Type": st.column_config.TextColumn("Action Type"),
                "Quantity": st.column_config.NumberColumn("Quantity", format="%d"),
                "Execution Price": st.column_config.NumberColumn("Execution Price", format="$%.2f"),
                "Total Value": st.column_config.NumberColumn("Total Value", format="$%.2f"),
            },
        )
        st.caption(f"Total trades executed: {len(tx_df)}")
    else:
        st.info("No trades recorded yet. Your transaction history will appear here once you start trading.")

# ---------------------------------------------------------
# TAB 3 — AI TRADER SENTIMENT (rules-based heuristic, not ML)
# ---------------------------------------------------------
with tab3:
    st.markdown("#### AI Market Recommendation")
    st.caption("A simple, transparent rules-based heuristic comparing live price to the 20-day EMA — not a machine learning model.")

    if current_price and not historical_data.empty:
        ema20_latest = hist["EMA20"].iloc[-1]
        spread_pct = (current_price - ema20_latest) / ema20_latest * 100

        if current_price > ema20_latest:
            tag_color = "#00FFA3"
            tag_text = "BULLISH MOMENTUM"
            message = (
                f"{active_ticker} is trading <strong>above</strong> its 20-day EMA "
                f"(${current_price:,.2f} vs ${ema20_latest:,.2f}, a spread of "
                f"<strong>+{spread_pct:.2f}%</strong>). This typically reflects short-term upward "
                f"momentum. Some traders watch for pullbacks toward the EMA as potential entry zones."
            )
        elif current_price < ema20_latest:
            tag_color = "#FF3366"
            tag_text = "BEARISH PRESSURE"
            message = (
                f"{active_ticker} is trading <strong>below</strong> its 20-day EMA "
                f"(${current_price:,.2f} vs ${ema20_latest:,.2f}, a spread of "
                f"<strong>{spread_pct:.2f}%</strong>). This typically reflects short-term downward "
                f"pressure. Some traders treat the EMA as resistance until price reclaims it."
            )
        else:
            tag_color = "#5E8BFF"
            tag_text = "NEUTRAL / AT EQUILIBRIUM"
            message = (
                f"{active_ticker} is trading almost exactly at its 20-day EMA "
                f"(${current_price:,.2f} vs ${ema20_latest:,.2f}). No clear directional bias from "
                f"this signal alone — wait for a decisive break in either direction."
            )

        st.markdown(
            f"""
            <div class="sentiment-box">
                <div class="sentiment-tag" style="background-color:{tag_color}22; color:{tag_color}; border:1px solid {tag_color}55;">
                    {tag_text}
                </div>
                <div style="color:#F5F6F8; font-size:15px;">{message}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("")
        st.caption(
            "⚠️ This is a single-indicator heuristic for illustrative purposes only — it is not "
            "financial advice and should never be the sole basis for a real trading decision."
        )
    else:
        st.info("Load a valid ticker in the chart panel to generate a sentiment reading.")
