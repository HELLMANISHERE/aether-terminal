import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

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
# 2. DESIGN SYSTEM — APPLE x LINEAR x STRIPE
# =========================================================
# Tokens:
#   Background     : #050508  (pure deep slate-black)
#   Panel          : #0D0E12  (dark graphite card)
#   Border         : #1F242E  (razor-thin hairline)
#   Text Primary   : #F5F6F8
#   Text Secondary : #6E7480
#   Accent (focus) : #5E8BFF  (neon-blue — EMA line, active states)
#   Positive       : #00FFA3  (neon green)
#   Negative       : #FF3366  (neon crimson)
#   Data font      : 'JetBrains Mono' — all numbers
#   Display font   : 'Inter' — all labels/prose
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background-color: #050508;
    }

    /* ---- Remove Streamlit visual clutter ---- */
    #MainMenu, footer, header[data-testid="stHeader"] {
        background-color: transparent;
    }
    div[data-testid="stDecoration"] {
        display: none;
    }
    div.block-container {
        padding-top: 2rem;
    }

    /* ---- Sidebar — integrated, borderless feel ---- */
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

    /* ---- Native st.metric cards ---- */
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

    /* ---- Custom glow HUD cards ---- */
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

    /* ---- Headings ---- */
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

    /* ---- Tabs ---- */
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

    /* ---- Dataframes ---- */
    div[data-testid="stDataFrame"] {
        border: 1px solid #1F242E;
        border-radius: 10px;
        overflow: hidden;
    }

    /* ---- Inputs ---- */
    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input {
        background-color: #0D0E12;
        border: 1px solid #1F242E;
        color: #F5F6F8;
        font-family: 'JetBrains Mono', monospace;
    }

    /* ---- Order panel execution buttons ---- */
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

    /* ---- Sidebar watchlist rows ---- */
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

    /* ---- AI sentiment insight box ---- */
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
st.caption("A hyper-minimalist financial command center · Live data · Simulated capital")

# =========================================================
# 3. SESSION STATE — PERSISTENCE LAYER
# =========================================================
if "cash" not in st.session_state:
    st.session_state.cash = 100000.0

if "portfolio" not in st.session_state:
    # ticker -> {"shares": int, "avg_cost": float}
    st.session_state.portfolio = {}

if "ledger" not in st.session_state:
    # Permanent transaction log. SELL rows carry Realized P&L; BUY rows don't.
    st.session_state.ledger = []

if "starting_value" not in st.session_state:
    st.session_state.starting_value = 100000.0

if "active_ticker" not in st.session_state:
    st.session_state.active_ticker = "AAPL"


# =========================================================
# 4. DATA HELPERS
# =========================================================
@st.cache_data(ttl=60)
def fetch_history(ticker_symbol: str, period: str = "3mo", interval: str = "1d"):
    stock = yf.Ticker(ticker_symbol)
    return stock.history(period=period, interval=interval)


def get_current_price(ticker_symbol: str):
    """Return (latest_close, full_history_df) or (None, empty_df)."""
    try:
        hist = fetch_history(ticker_symbol, "3mo")
        if hist.empty:
            return None, hist
        return float(hist["Close"].iloc[-1]), hist
    except Exception:
        return None, pd.DataFrame()


@st.cache_data(ttl=60)
def get_macro_quote(ticker_symbol: str):
    """Return (last_price, pct_change) for a macro index/asset."""
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


def get_live_prices_for_portfolio():
    prices = {}
    for tkr in st.session_state.portfolio:
        price, _ = get_current_price(tkr)
        prices[tkr] = price if price is not None else 0.0
    return prices


def log_buy(ticker_symbol, qty, price):
    st.session_state.ledger.append({
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Ticker": ticker_symbol,
        "Action Type": "BUY",
        "Quantity": qty,
        "Execution Price": price,
        "Total Value": price * qty,
        "Realized P&L ($)": None,
        "Realized P&L (%)": None,
    })


def log_sell(ticker_symbol, qty, price, cost_basis_per_share):
    """Realized P&L is computed at execution time against the average cost
    basis being sold — required for Win Rate to mean anything real."""
    realized_dollar = (price - cost_basis_per_share) * qty
    realized_pct = ((price - cost_basis_per_share) / cost_basis_per_share * 100) if cost_basis_per_share > 0 else 0.0
    st.session_state.ledger.append({
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Ticker": ticker_symbol,
        "Action Type": "SELL",
        "Quantity": qty,
        "Execution Price": price,
        "Total Value": price * qty,
        "Realized P&L ($)": realized_dollar,
        "Realized P&L (%)": realized_pct,
    })


def calculate_win_rate():
    closed_trades = [t for t in st.session_state.ledger if t["Action Type"] == "SELL"]
    if not closed_trades:
        return None, 0, 0
    wins = sum(1 for t in closed_trades if t["Realized P&L ($)"] > 0)
    total = len(closed_trades)
    return (wins / total * 100), wins, total


def execute_buy(tkr, qty, price):
    if not price:
        st.error("Can't buy — invalid ticker price.")
        return
    total_cost = price * qty
    if st.session_state.cash < total_cost:
        st.error("Not enough cash for this trade.")
        return
    holding = st.session_state.portfolio.get(tkr, {"shares": 0, "avg_cost": 0.0})
    old_shares, old_avg_cost = holding["shares"], holding["avg_cost"]
    new_shares = old_shares + qty
    new_avg_cost = ((old_shares * old_avg_cost) + (qty * price)) / new_shares

    st.session_state.portfolio[tkr] = {"shares": new_shares, "avg_cost": new_avg_cost}
    st.session_state.cash -= total_cost
    log_buy(tkr, qty, price)
    st.toast(f"Bought {qty} shares of {tkr} @ ${price:.2f}", icon="✅")


def execute_sell(tkr, qty, price):
    if not price:
        st.error("Can't sell — invalid ticker price.")
        return
    holding = st.session_state.portfolio.get(tkr)
    if not holding or holding["shares"] < qty:
        st.error("You don't own enough shares to sell.")
        return

    cost_basis_per_share = holding["avg_cost"]
    total_return = price * qty
    st.session_state.cash += total_return
    holding["shares"] -= qty

    if holding["shares"] == 0:
        del st.session_state.portfolio[tkr]
    else:
        st.session_state.portfolio[tkr] = holding

    log_sell(tkr, qty, price, cost_basis_per_share)
    st.toast(f"Sold {qty} shares of {tkr} @ ${price:.2f}", icon="💰")


def render_hud_card(label, value_str, sub_str=None, glow=None):
    """glow: None | 'green' | 'red' — controls neon glow styling."""
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
# 5. SIDEBAR — GLOBAL LIQUIDITY TRACKER (macro-only)
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
    st.caption("Aether Terminal · Simulated capital only")

    if st.button("♻️ Reset Account", use_container_width=True):
        st.session_state.cash = 100000.0
        st.session_state.portfolio = {}
        st.session_state.ledger = []
        st.rerun()


# =========================================================
# 6. PORTFOLIO VALUATION (feeds HUD + Active Holdings tab)
# =========================================================
live_prices = get_live_prices_for_portfolio()

holdings_value = 0.0
total_cost_basis = 0.0
portfolio_rows = []

for tkr, data in st.session_state.portfolio.items():
    sh = data["shares"]
    avg_cost = data["avg_cost"]
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

total_portfolio_value = st.session_state.cash + holdings_value
overall_pnl_dollar = total_portfolio_value - st.session_state.starting_value
overall_pnl_pct = (overall_pnl_dollar / st.session_state.starting_value * 100) if st.session_state.starting_value else 0.0

win_rate, win_count, closed_count = calculate_win_rate()


# =========================================================
# 7. HUD — 4 GLOWING WIDGETS
# =========================================================
h1, h2, h3, h4 = st.columns(4)

with h1:
    render_hud_card("TOTAL PORTFOLIO LIQUIDITY", f"${total_portfolio_value:,.2f}")

with h2:
    render_hud_card("AVAILABLE BUYING POWER", f"${st.session_state.cash:,.2f}")

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
# 8. MAIN TERMINAL — CHART (3.2) + ORDER PANEL (0.8)
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
        # 20-day EMA (span=20 approximates a 20-day EMA in pandas)
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

    if order_buy:
        execute_buy(active_ticker, order_qty, current_price)
    if order_sell:
        execute_sell(active_ticker, order_qty, current_price)

st.markdown("---")

# =========================================================
# 9. ANALYTICAL GRID & LEDGER — TABS
# =========================================================
tab1, tab2, tab3 = st.tabs(["💼 Active Holdings Grid", "📜 Order Ledger", "🧠 AI Trader Sentiment"])

# ---------------------------------------------------------
# TAB 1 — ACTIVE HOLDINGS GRID
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
# TAB 2 — ORDER LEDGER
# ---------------------------------------------------------
with tab2:
    st.markdown("#### Order Ledger")

    if st.session_state.ledger:
        ledger_df = pd.DataFrame(st.session_state.ledger[::-1])[
            ["Timestamp", "Ticker", "Action Type", "Quantity", "Execution Price", "Total Value"]
        ]  # archive view per spec — core trade fields only

        st.dataframe(
            ledger_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Timestamp": st.column_config.TextColumn("Timestamp"),
                "Ticker": st.column_config.TextColumn("Asset Ticker"),
                "Action Type": st.column_config.TextColumn("Action Type"),
                "Quantity": st.column_config.NumberColumn("Quantity", format="%d"),
                "Execution Price": st.column_config.NumberColumn("Execution Price", format="$%.2f"),
                "Total Value": st.column_config.NumberColumn("Total Value", format="$%.2f"),
            },
        )
        st.caption(f"Total trades executed: {len(st.session_state.ledger)}")
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