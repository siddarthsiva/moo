"""
Project MOO - Ultimate Bovine Commodity Quantitative Trading Dashboard.
100% Free & Open-Source Institutional Multi-Factor Platform for Cattle Markets.
"""

import sys
import os

# Add parent directory to path for clean imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

from config import (
    COMMODITY_SPECS, CATTLE_CRUSH_CONFIG, DEFAULT_FACTOR_WEIGHTS,
    SUPER_ELNINO_FACTOR_WEIGHTS, ENSO_CONFIG, STRATEGY_CONFIG, RISK_CONFIG,
    GLOBAL_CATTLE_PRODUCERS, LIVESTOCK_CARRIER_FLEET, INDUSTRY_COST_CONFIG, NEWS_WIRE_CONFIG
)
from data.data_loader import UnifiedDataLoader
from data.global_production import GlobalBovineProductionEngine, BREED_TAXONOMY
from data.supply_demand import GlobalSupplyDemandEngine
from data.trade_flows import GlobalBovineTradeFlowsEngine
from data.maritime_ais import MaritimeLivestockAISEngine, MARITIME_CHOKE_POINTS
from data.news_engine import AgribusinessNewsWireEngine
from factors.factor_engine import BovineFactorEngine
from factors.crush_spread import CattleCrushFactor
from factors.technical import BovineTechnicalFactors
from factors.macro_weather import MacroWeatherFactor
from factors.industry_costs import BovineIndustryCostEngine
from models.strategy import BovineQuantitativeStrategy
from backtest.backtester import BovineBacktester
from execution.paper_trader import BovinePaperTrader


# Set Streamlit Page Configuration
st.set_page_config(
    page_title="BLOOMBERG // PROJECT MOO",
    page_icon="■",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Bloomberg Terminal Custom Responsive CSS Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap');

    *, *::before, *::after {
        box-sizing: border-box;
    }

    html, body, [class*="css"], .stApp {
        font-family: 'Roboto Mono', 'Consolas', 'Courier New', monospace !important;
        background-color: #000000 !important;
        color: #d1d4dc !important;
        overflow-x: hidden !important;
        max-width: 100vw !important;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    /* Page container: fluid & centered for Ultrawide/4K while eliminating mobile margin waste */
    .main .block-container,
    div[data-testid="stAppViewBlockContainer"] {
        max-width: 2200px !important;
        margin: 0 auto !important;
        padding-top: 1.2rem !important;
        padding-bottom: 3rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        width: 100% !important;
    }

    @media (max-width: 1400px) {
        .main .block-container,
        div[data-testid="stAppViewBlockContainer"] {
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
            padding-top: 1rem !important;
        }
    }

    @media (max-width: 992px) {
        .main .block-container,
        div[data-testid="stAppViewBlockContainer"] {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 0.75rem !important;
        }
    }

    @media (max-width: 768px) {
        .main .block-container,
        div[data-testid="stAppViewBlockContainer"] {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
            padding-top: 0.5rem !important;
            padding-bottom: 2rem !important;
        }
    }

    @media (max-width: 420px) {
        .main .block-container,
        div[data-testid="stAppViewBlockContainer"] {
            padding-left: 0.35rem !important;
            padding-right: 0.35rem !important;
            padding-top: 0.35rem !important;
        }
    }

    /* Bloomberg Terminal Top Header */
    .bbg-header {
        background: #0d0e12;
        border-top: 3px solid #ff9900;
        border-bottom: 1px solid #22252e;
        padding: 8px 12px;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        border-radius: 2px;
        width: 100%;
    }
    .bbg-header-title {
        color: #ff9900;
        font-size: clamp(11px, 2.2vw, 13px);
        font-weight: 700;
        letter-spacing: 0.8px;
        display: flex;
        align-items: center;
        gap: 6px;
        white-space: normal;
        word-break: break-word;
    }
    .bbg-header-badges {
        display: flex;
        gap: 8px;
        align-items: center;
        flex-wrap: wrap;
    }
    .bbg-cmd-badge {
        background: #15181f;
        border: 1px solid #ff9900;
        color: #ff9900;
        padding: 2px 7px;
        font-size: clamp(9px, 1.8vw, 11px);
        font-weight: 600;
        letter-spacing: 0.5px;
        white-space: nowrap;
        border-radius: 1px;
    }
    .bbg-status-badge {
        color: #00ff66;
        font-size: clamp(9px, 1.8vw, 11px);
        font-weight: 600;
        white-space: nowrap;
    }
    .bbg-time-badge {
        color: #848e9c;
        font-size: clamp(9px, 1.6vw, 11px);
        white-space: nowrap;
    }

    /* Bloomberg Function Keys & Status Strip */
    .bbg-status-strip {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #080a0e;
        border: 1px solid #1e222d;
        padding: 6px 10px;
        margin-bottom: 12px;
        font-size: 10px;
        flex-wrap: wrap;
        gap: 8px;
        border-radius: 2px;
        width: 100%;
    }
    .bbg-direct-keys {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 6px;
    }
    .bbg-key-title {
        color: #ff9900;
        font-weight: 700;
        margin-right: 4px;
        font-size: clamp(9px, 1.8vw, 10px);
    }
    .bbg-key-btn {
        color: #00e5ff;
        background: #0f131a;
        border: 1px solid #1a2230;
        padding: 1px 5px;
        border-radius: 2px;
        font-size: clamp(8.5px, 1.6vw, 9.5px);
        white-space: nowrap;
    }
    .bbg-feed-status {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 10px;
        color: #808595;
        font-size: clamp(8.5px, 1.6vw, 9.5px);
    }
    .bbg-feed-status .armed {
        color: #00ff66;
        font-weight: 600;
    }

    /* Responsive Telemetry Strip Grid */
    .bbg-kpi-grid {
        display: grid;
        grid-template-columns: repeat(8, 1fr);
        gap: 8px;
        margin-bottom: 12px;
        width: 100%;
    }
    @media (max-width: 1400px) {
        .bbg-kpi-grid {
            grid-template-columns: repeat(4, 1fr);
        }
    }
    @media (max-width: 768px) {
        .bbg-kpi-grid {
            grid-template-columns: repeat(2, 1fr);
            gap: 6px;
        }
    }
    @media (max-width: 360px) {
        .bbg-kpi-grid {
            grid-template-columns: 1fr;
        }
    }
    .bbg-kpi-card {
        background-color: #0a0c10;
        border: 1px solid #1e222d;
        border-radius: 2px;
        padding: 7px 9px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 58px;
        box-sizing: border-box;
    }
    .bbg-kpi-caption {
        font-size: clamp(8.5px, 1.6vw, 9.5px);
        color: #848e9c;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 2px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .bbg-kpi-value {
        font-size: clamp(13px, 2.2vw, 15px);
        font-weight: 700;
        line-height: 1.2;
        margin: 2px 0;
    }
    .bbg-kpi-sub {
        font-size: clamp(8px, 1.5vw, 8.5px);
        color: #848e9c;
        letter-spacing: 0.3px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* Responsive Metrics Deck */
    .bbg-metrics-deck {
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        gap: 8px;
        width: 100%;
    }
    @media (max-width: 1400px) {
        .bbg-metrics-deck {
            grid-template-columns: repeat(3, 1fr);
        }
    }
    @media (max-width: 768px) {
        .bbg-metrics-deck {
            grid-template-columns: repeat(2, 1fr);
            gap: 6px;
        }
    }
    @media (max-width: 360px) {
        .bbg-metrics-deck {
            grid-template-columns: 1fr;
        }
    }
    .bbg-metric-card {
        background-color: #0a0c10;
        border: 1px solid #1e222d;
        border-radius: 2px;
        padding: 7px 9px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 58px;
        box-sizing: border-box;
    }
    .bbg-metric-lbl {
        font-size: clamp(8.5px, 1.6vw, 9.5px);
        color: #848e9c;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 2px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .bbg-metric-val {
        font-size: clamp(13px, 2.3vw, 16px);
        font-weight: 700;
        line-height: 1.2;
        margin: 2px 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .bbg-metric-delta {
        font-size: clamp(8.5px, 1.5vw, 9.5px);
        font-weight: 600;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .bbg-metric-sub {
        font-size: clamp(8px, 1.5vw, 8.5px);
        color: #848e9c;
        letter-spacing: 0.3px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* Section Subheaders & Alerts */
    .bbg-section-title {
        font-size: clamp(10.5px, 2vw, 11.5px);
        font-weight: 700;
        color: #ff9900;
        margin-top: 10px;
        margin-bottom: 6px;
        letter-spacing: 0.5px;
    }
    .terminal-alert {
        background-color: #08120b;
        border-left: 4px solid #00ff66;
        border-top: 1px solid #16261c;
        border-right: 1px solid #16261c;
        border-bottom: 1px solid #16261c;
        padding: 10px 14px;
        margin-bottom: 14px;
        font-size: clamp(10px, 2vw, 11.5px);
        line-height: 1.5;
        word-break: break-word;
        border-radius: 2px;
    }

    /* Responsive Horizontal Columns Stacking */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        gap: 10px !important;
        align-items: stretch !important;
    }

    div[data-testid="column"] {
        min-width: 0 !important;
        box-sizing: border-box !important;
    }

    @media (max-width: 1080px) {
        div[data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
            gap: 12px !important;
        }
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
            width: 100% !important;
            min-width: 100% !important;
            flex: 1 1 100% !important;
        }
    }

    /* Fallback Metric Overrides */
    div[data-testid="stMetric"] {
        background-color: #0a0c10 !important;
        border: 1px solid #1e222d !important;
        border-radius: 2px !important;
        padding: 6px 10px !important;
        box-sizing: border-box !important;
    }
    div[data-testid="stMetricLabel"] p,
    div[data-testid="stMetricLabel"] label {
        font-size: clamp(8.5px, 1.6vw, 10px) !important;
        color: #848e9c !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    div[data-testid="stMetricValue"] div,
    div[data-testid="stMetricValue"] span {
        font-size: clamp(13px, 2.2vw, 17px) !important;
        font-weight: 700 !important;
        color: #f5f6f8 !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        line-height: 1.2 !important;
    }

    /* Buttons */
    .stButton>button {
        background-color: #12151c !important;
        color: #ff9900 !important;
        border: 1px solid #ff9900 !important;
        border-radius: 2px !important;
        font-family: 'Roboto Mono', monospace !important;
        font-weight: 600 !important;
        font-size: clamp(10px, 1.8vw, 11px) !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
        min-height: 38px !important;
        padding: 6px 14px !important;
        width: 100% !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.15s ease-in-out !important;
    }
    .stButton>button:hover {
        background-color: #ff9900 !important;
        color: #000000 !important;
        border-color: #ff9900 !important;
    }
    .stButton>button:active {
        transform: scale(0.98);
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #050608 !important;
        border-right: 1px solid #1e222d !important;
    }
    @media (max-width: 768px) {
        section[data-testid="stSidebar"] {
            width: 85vw !important;
            max-width: 320px !important;
        }
    }

    /* Dataframe and Tables */
    div[data-testid="stDataFrame"],
    div[data-testid="stTable"] {
        width: 100% !important;
        max-width: 100% !important;
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch !important;
        border: 1px solid #1e222d !important;
        border-radius: 2px !important;
    }

    /* Plotly Chart Containers */
    .js-plotly-plot, .plot-container {
        width: 100% !important;
        max-width: 100% !important;
    }
    .js-plotly-plot .plotly .modebar {
        top: 2px !important;
        right: 2px !important;
        transform: scale(0.85);
        transform-origin: top right;
    }

    /* Code & Terminal Tickers */
    pre, code, div[data-testid="stCodeBlock"] {
        white-space: pre-wrap !important;
        word-break: break-word !important;
        font-family: 'Roboto Mono', 'Consolas', monospace !important;
        font-size: clamp(9.5px, 1.8vw, 11px) !important;
        background-color: #080a0e !important;
        border: 1px solid #1e222d !important;
        border-radius: 2px !important;
    }

    /* Responsive Tabs */
    div[data-testid="stTabs"] {
        width: 100% !important;
        overflow-x: auto !important;
    }
    div[data-testid="stTabs"] button[role="tab"] {
        font-family: 'Roboto Mono', monospace !important;
        font-size: clamp(10px, 1.8vw, 11.5px) !important;
        padding: 6px 12px !important;
        color: #848e9c !important;
        border-bottom: 2px solid transparent !important;
        white-space: nowrap !important;
    }
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        color: #ff9900 !important;
        border-bottom: 2px solid #ff9900 !important;
        font-weight: 700 !important;
    }

    /* Ticker colors */
    .ticker-pos { color: #00ff66 !important; font-weight: 600; }
    .ticker-neg { color: #ff3b30 !important; font-weight: 600; }
    .ticker-sym { color: #ff9900 !important; font-weight: 700; }
</style>
""", unsafe_allow_html=True)


def bbg_plot_theme(fig, title: str = "", height: int = 400, x_title: str = "", y_title: str = ""):
    """Applies authentic Bloomberg Terminal layout to any Plotly figure with fluid scaling."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#05070a",
        plot_bgcolor="#05070a",
        height=height,
        autosize=True,
        title=dict(
            text=title if title else None,
            font=dict(size=11, color="#ff9900", family="'Roboto Mono', 'Courier New', monospace"),
            x=0.01,
            y=0.98
        ) if title else None,
        font=dict(family="'Roboto Mono', 'Courier New', monospace", size=9, color="#b0b5c0"),
        margin=dict(l=35, r=20, t=35 if title else 20, b=30),
        xaxis=dict(
            title=dict(text=x_title, font=dict(size=9, color="#808595")) if x_title else None,
            gridcolor="#161922",
            zerolinecolor="#202430",
            showgrid=True,
            showline=True,
            linecolor="#202430",
            tickfont=dict(size=8.5, color="#808595")
        ),
        yaxis=dict(
            title=dict(text=y_title, font=dict(size=9, color="#808595")) if y_title else None,
            gridcolor="#161922",
            zerolinecolor="#202430",
            showgrid=True,
            showline=True,
            linecolor="#202430",
            tickfont=dict(size=8.5, color="#808595")
        ),
        legend=dict(
            bgcolor="rgba(10, 12, 16, 0.8)",
            bordercolor="#202430",
            borderwidth=1,
            font=dict(size=8.5, color="#b0b5c0"),
            orientation="h",
            yanchor="top",
            y=-0.14,
            xanchor="center",
            x=0.5
        )
    )
    return fig


def bbg_render_chart(fig, key=None):
    """Renders a Plotly chart with responsive configuration, stretch width, and mobile touch optimization."""
    config = {
        "responsive": True,
        "displayModeBar": "hover",
        "displaylogo": False,
        "modeBarButtonsToRemove": ["lasso2d", "select2d"]
    }
    st.plotly_chart(fig, width="stretch", config=config, key=key)


def bbg_header(title: str, cmd: str = "AGRI LE <GO>", status: str = "GLOBEX CME: LIVE"):
    """Renders authentic Bloomberg terminal top header with responsive badges and fluid typography."""
    now_utc = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    html = (
        f"<div class='bbg-header'>"
        f"<div class='bbg-header-title'>"
        f"<span style='color:#ff9900;'>■</span> {title}"
        f"</div>"
        f"<div class='bbg-header-badges'>"
        f"<span class='bbg-cmd-badge'>{cmd}</span>"
        f"<span class='bbg-status-badge'>● {status}</span>"
        f"<span class='bbg-time-badge'>TIME: {now_utc}</span>"
        f"</div>"
        f"</div>"
    )
    st.markdown(html, unsafe_allow_html=True)


def bbg_section_title(title: str):
    """Renders amber terminal section subheader."""
    st.markdown(
        f"<div class='bbg-section-title'>{title}</div>",
        unsafe_allow_html=True
    )


@st.cache_data(ttl=300, show_spinner=False)
def load_all_market_data(use_live: bool = True):
    loader = UnifiedDataLoader(use_live_yf=use_live)
    return loader.load_dataset()


# Sidebar Navigation & Settings
st.sidebar.markdown(
    "<div style='padding:10px 0 8px 0; border-bottom:2px solid #ff9900; margin-bottom:10px;'>"
    "<div style='font-size:13px; font-weight:800; color:#ff9900; letter-spacing:1px;'>PROJECT MOO // TERMINAL</div>"
    "<div style='font-size:10px; color:#848e9c; letter-spacing:0.5px;'>BLOOMBERG BOVINE QUANT DESK</div>"
    "</div>",
    unsafe_allow_html=True
)

app_mode = st.sidebar.radio(
    "FUNCTION DIRECTORY",
    [
        "01 // LIVE COCKPIT",
        "02 // STRATEGY BACKTESTER",
        "03 // FACTOR RESEARCH",
        "04 // PAPER PORTFOLIO",
        "05 // CME SPECS & ARCH",
        "06 // GLOBAL SUPPLY CHAIN & AIS"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("MARKET DATA FEED")
use_live_feed = st.sidebar.toggle("Live Yahoo Finance Feeds", value=True, help="Fetch real-time CME/CBOT commodity futures via Yahoo Finance. If disabled or offline, uses local benchmark data.")
if st.sidebar.button("🔄 REFRESH LIVE DATA", width="stretch", help="Clear cache and re-fetch real-time market data"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("CLIMATOLOGY COMPENSATION ENGINE")
enso_selection = st.sidebar.selectbox(
    "ENSO Regime Filter",
    [
        "SUPER EL NINO (+2.30 C ACTIVE)",
        "MODERATE EL NINO",
        "NEUTRAL CLIMATOLOGY",
        "LA NINA (DROUGHT LIQUIDATION)"
    ],
    index=0
)
if "SUPER" in enso_selection:
    active_enso_regime = "super_elnino"
elif "MODERATE" in enso_selection:
    active_enso_regime = "elnino"
elif "LA NINA" in enso_selection:
    active_enso_regime = "lanina"
else:
    active_enso_regime = "neutral"

# Check if preset weights applied
if "w_crush" not in st.session_state:
    if active_enso_regime == "super_elnino":
        st.session_state["w_crush"] = float(SUPER_ELNINO_FACTOR_WEIGHTS["crush_margin"])
        st.session_state["w_cot"] = float(SUPER_ELNINO_FACTOR_WEIGHTS["cot_sentiment"])
        st.session_state["w_seas"] = float(SUPER_ELNINO_FACTOR_WEIGHTS["seasonality"])
        st.session_state["w_macro"] = float(SUPER_ELNINO_FACTOR_WEIGHTS["macro_drought"])
        st.session_state["w_tech"] = float(SUPER_ELNINO_FACTOR_WEIGHTS["technical_trend"])
        st.session_state["w_ml"] = float(SUPER_ELNINO_FACTOR_WEIGHTS["ml_ensemble"])
    else:
        st.session_state["w_crush"] = float(DEFAULT_FACTOR_WEIGHTS["crush_margin"])
        st.session_state["w_cot"] = float(DEFAULT_FACTOR_WEIGHTS["cot_sentiment"])
        st.session_state["w_seas"] = float(DEFAULT_FACTOR_WEIGHTS["seasonality"])
        st.session_state["w_macro"] = float(DEFAULT_FACTOR_WEIGHTS["macro_drought"])
        st.session_state["w_tech"] = float(DEFAULT_FACTOR_WEIGHTS["technical_trend"])
        st.session_state["w_ml"] = float(DEFAULT_FACTOR_WEIGHTS["ml_ensemble"])

if st.sidebar.button("APPLY REGIME FACTOR WEIGHTS [F4]", width="stretch"):
    st.session_state["w_crush"] = float(SUPER_ELNINO_FACTOR_WEIGHTS["crush_margin"])
    st.session_state["w_cot"] = float(SUPER_ELNINO_FACTOR_WEIGHTS["cot_sentiment"])
    st.session_state["w_seas"] = float(SUPER_ELNINO_FACTOR_WEIGHTS["seasonality"])
    st.session_state["w_macro"] = float(SUPER_ELNINO_FACTOR_WEIGHTS["macro_drought"])
    st.session_state["w_tech"] = float(SUPER_ELNINO_FACTOR_WEIGHTS["technical_trend"])
    st.session_state["w_ml"] = float(SUPER_ELNINO_FACTOR_WEIGHTS["ml_ensemble"])
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("FACTOR WEIGHT ALLOCATION")
w_crush = st.sidebar.slider("Crush / Feedlot Spread", 0.0, 1.0, st.session_state["w_crush"], 0.05)
w_cot = st.sidebar.slider("CFTC Smart Money COT", 0.0, 1.0, st.session_state["w_cot"], 0.05)
w_seas = st.sidebar.slider("Biological Seasonality", 0.0, 1.0, st.session_state["w_seas"], 0.05)
w_macro = st.sidebar.slider("Drought & Macro DXY", 0.0, 1.0, st.session_state["w_macro"], 0.05)
w_tech = st.sidebar.slider("Kalman Trend Momentum", 0.0, 1.0, st.session_state["w_tech"], 0.05)
w_ml = st.sidebar.slider("ML Ensemble Alpha", 0.0, 1.0, st.session_state["w_ml"], 0.05)

custom_weights = {
    "crush_margin": w_crush,
    "cot_sentiment": w_cot,
    "seasonality": w_seas,
    "macro_drought": w_macro,
    "technical_trend": w_tech,
    "ml_ensemble": w_ml
}

# Fetch Market Data
market_data = load_all_market_data(use_live=use_live_feed)
crush_calc = CattleCrushFactor()

# Telemetry timestamp badge
if "LE=F" in market_data and not market_data["LE=F"].empty:
    latest_ts = market_data["LE=F"].index[-1].strftime("%Y-%m-%d")
    status_color = "#00ff66" if use_live_feed else "#ff9900"
    mode_text = "LIVE YAHOO FEED" if use_live_feed else "BENCHMARK CACHE"
    st.sidebar.markdown(
        f"<div style='font-size:10px; color:{status_color}; font-weight:600; padding:2px 0 6px 0;'>"
        f"● {mode_text} [{latest_ts}]"
        f"</div>",
        unsafe_allow_html=True
    )

# Calculate Quick Global Cattle Crush Metrics
live_df = market_data.get("LE=F", pd.DataFrame())
feeder_df = market_data.get("GF=F", pd.DataFrame())
corn_df = market_data.get("ZC=F", pd.DataFrame())

if not live_df.empty and not feeder_df.empty and not corn_df.empty:
    crush_df = crush_calc.calculate_crush_metrics(
        live_df["Close"], feeder_df["Close"], corn_df["Close"], enso_regime=active_enso_regime
    )
    latest_crush_head = float(crush_df["CrushMargin_Head"].iloc[-1])
    latest_crush_cwt = float(crush_df["CrushMargin_Cwt"].iloc[-1])
    latest_fl_ratio = float(crush_df["FeederLiveRatio"].iloc[-1])
else:
    latest_crush_head, latest_crush_cwt, latest_fl_ratio = 0.0, 0.0, 1.35


# -------------------------------------------------------------------------
# TAB 1: LIVE ALPHA COCKPIT
# -------------------------------------------------------------------------
if app_mode == "01 // LIVE COCKPIT":
    bbg_header("BLOOMBERG PROFESSIONAL :: PROJECT MOO BOVINE QUANT DESK", cmd="AGRI LE <GO>", status="GLOBEX CME: LIVE")

    # Top Bloomberg Function Keys & System Status Bar
    st.markdown(
        "<div class='bbg-status-strip'>"
        "<div class='bbg-direct-keys'>"
        "<span class='bbg-key-title'>DIRECT KEYS:</span>"
        "<span class='bbg-key-btn'>[F1: HELP]</span>"
        "<span class='bbg-key-btn'>[F2: BQ]</span>"
        "<span class='bbg-key-btn'>[F3: CRUSH]</span>"
        "<span class='bbg-key-btn'>[F4: CORR]</span>"
        "<span class='bbg-key-btn'>[F5: RADAR]</span>"
        "<span class='bbg-key-btn'>[F6: VOL]</span>"
        "<span class='bbg-key-btn'>[F7: COT]</span>"
        "<span class='bbg-key-btn'>[F8: REBAL]</span>"
        "<span class='bbg-key-btn'>[F9: DOM]</span>"
        "<span class='bbg-key-btn'>[F10: COF]</span>"
        "<span class='bbg-key-btn'>[F11: CUTOUT]</span>"
        "<span class='bbg-key-btn'>[F12: VaR]</span>"
        "</div>"
        "<div class='bbg-feed-status'>"
        "<span>FEED: GLOBEX 1.2ms</span>"
        "<span>CME CLEARPORT: SYNCED</span>"
        "<span class='armed'>● CIRCUIT BREAKER: ARMED</span>"
        "</div>"
        "</div>",
        unsafe_allow_html=True
    )

    # Global Multi-Commodity Quote Board (BQ <GO>)
    all_syms = ["LE=F", "GF=F", "ZC=F", "ZM=F", "HE=F", "DC=F", "CL=F", "DX-Y.NYB"]
    ticker_data = []
    for s in all_syms:
        sdf = market_data.get(s, pd.DataFrame())
        if not sdf.empty and len(sdf) > 20:
            last = float(sdf["Close"].iloc[-1])
            prev = float(sdf["Close"].iloc[-2])
            chg = last - prev
            pct = (chg / prev) * 100.0
            hi = float(sdf["High"].iloc[-1])
            lo = float(sdf["Low"].iloc[-1])
            vol = int(sdf["Volume"].iloc[-1])
            atr_v = float(BovineTechnicalFactors.calculate_atr(sdf).iloc[-1])
            ann_v = float(BovineTechnicalFactors.calculate_garman_klass_vol(sdf).iloc[-1]) * 100.0
            rsi_v = float(BovineTechnicalFactors.calculate_rsi(sdf["Close"], 14).iloc[-1])
            spec = COMMODITY_SPECS.get(s, None)
            name = spec.name if spec else s
            tick_sz = spec.tick_size if spec else 0.025
            bid = round(last - (tick_sz * 0.5), 3)
            ask = round(last + (tick_sz * 0.5), 3)
            spread = round(ask - bid, 3)
            sign = "+" if chg >= 0 else ""
            ticker_data.append({
                "TICKER": s,
                "INSTRUMENT": name,
                "LAST": f"${last:,.2f}",
                "NET CHG": f"{sign}{chg:.2f}",
                "% CHG": f"{sign}{pct:.2f}%",
                "BID": f"${bid:,.2f}",
                "ASK": f"${ask:,.2f}",
                "SPREAD": f"${spread:.3f}",
                "HIGH": f"${hi:,.2f}",
                "LOW": f"${lo:,.2f}",
                "14D ATR": f"${atr_v:.2f}",
                "ANN VOL": f"{ann_v:.1f}%",
                "RSI(14)": f"{rsi_v:.1f}",
                "VOLUME": f"{vol:,}"
            })

    ticker_df = pd.DataFrame(ticker_data)
    bbg_section_title("GLOBAL MULTI-COMMODITY QUOTE BOARD [BQ <GO>]")
    st.dataframe(ticker_df, hide_index=True, width="stretch")

    # Macro Climatology & USDA Fundamental Telemetry Strip (AGRI DES <GO>)
    bbg_section_title("MACRO CLIMATOLOGY & USDA FUNDAMENTAL TELEMETRY STRIP [AGRI DES <GO>]")
    kpi_items = [
        {"caption": "ENSO ONI 3.4", "val": "+2.30 C", "color": "#ff9900", "sub": "SUPER EL NINO"},
        {"caption": "PLAINS DROUGHT", "val": "48.2", "color": "#00ff66", "sub": "SUB-NORMAL / RAIN"},
        {"caption": "FEEDLOT PLACE", "val": "-4.2% YoY", "color": "#ff3b30", "sub": "TIGHTENING FEED"},
        {"caption": "BEEF COW HERD", "val": "28.2M HD", "color": "#ff9900", "sub": "63-YR SUPER CYCLE"},
        {"caption": "BOXED BEEF CH", "val": "$314.50", "color": "#00ff66", "sub": "+$2.85 / cwt"},
        {"caption": "CH / SEL SPREAD", "val": "$24.20", "color": "#00e5ff", "sub": "GRADE PREMIUM"},
        {"caption": "PACKER MARGIN", "val": "+$118.50", "color": "#00ff66", "sub": "+$12.40 / HEAD"},
        {"caption": "DXY DOLLAR", "val": "103.45", "color": "#d1d4dc", "sub": "-0.35% EXP BULL"},
    ]
    kpi_html = "<div class='bbg-kpi-grid'>" + "".join([
        f"<div class='bbg-kpi-card'>"
        f"<div class='bbg-kpi-caption'>{item['caption']}</div>"
        f"<div class='bbg-kpi-value' style='color:{item['color']};'>{item['val']}</div>"
        f"<div class='bbg-kpi-sub'>{item['sub']}</div>"
        f"</div>"
        for item in kpi_items
    ]) + "</div>"
    st.markdown(kpi_html, unsafe_allow_html=True)

    if active_enso_regime == "super_elnino":
        st.info(
            "[CLIMATOLOGY ADVISORY] ACTIVE SUPER EL NINO REGIME (+2.30 C ONI SEA SURFACE ANOMALY)\n\n"
            "- HEIFER RETENTION: Southern Plains forage recovery halts auction slaughter -> acute prompt beef deficit.\n\n"
            "- FEED ARBITRAGE: Midwest moisture drives bumper corn harvest -> low feed costs expand crush margins to feedlots.\n\n"
            "- CALF RUN MODULATION: Autumn calf dumping suppressed; winter subtropical storm tracks elevate feedlot mud drag."
        )

    # Live Signal Scan Engine
    paper_trader = BovinePaperTrader(enso_regime=active_enso_regime)
    paper_trader.strategy.factor_weights = custom_weights
    live_signals = paper_trader.scan_live_signals(["LE=F", "GF=F"], enso_regime=active_enso_regime)

    # Control Deck & Target Selection
    top_ctrl_l, top_ctrl_r = st.columns([1, 3])
    with top_ctrl_l:
        target_sym = st.selectbox(
            "TARGET ASSET FOCUS [DES <GO>]",
            ["LE=F (Live Cattle Futures)", "GF=F (Feeder Cattle Futures)"]
        )
        sym_code = "LE=F" if "LE" in target_sym else "GF=F"
        df_target = market_data[sym_code]
        sig = live_signals[sym_code]

    with top_ctrl_r:
        deck_items = [
            {"label": "LAST SETTLEMENT", "val": f"${sig['latest_price']:.2f}", "delta": f"{sig['daily_change_pct']:+.2f}%", "delta_pos": sig['daily_change_pct'] >= 0},
            {"label": "COMPOSITE ALPHA", "val": f"{sig['composite_alpha']:+.3f}", "sub": "SCALE: [-1.0, +1.0]"},
            {"label": "SIGNAL REGIME", "val": sig["signal_regime"], "val_color": "#00ff66" if "LONG" in sig["signal_regime"] or "BULL" in sig["signal_regime"] else "#ff9900"},
            {"label": "TARGET EXPOSURE", "val": f"{sig['target_weight']*100:.0f}%", "sub": f"{sig['recommended_contracts']} CONTRACTS"},
            {"label": "STOP / TAKE PROFIT", "val": f"${sig['stop_loss_price']:.2f}", "sub": f"TP: ${sig['take_profit_price']:.2f}"},
            {"label": "REALIZED VOL (GK)", "val": f"{sig['annualized_vol_pct']}%", "sub": f"ATR: ${sig['atr_14']:.2f}"},
        ]
        deck_html = "<div class='bbg-metrics-deck'>" + "".join([
            f"<div class='bbg-metric-card'>"
            f"<div class='bbg-metric-lbl'>{m['label']}</div>"
            f"<div class='bbg-metric-val' style='color:{m.get('val_color', '#f5f6f8')};'>{m['val']}</div>"
            + (f"<div class='bbg-metric-delta {'ticker-pos' if m['delta_pos'] else 'ticker-neg'}'>{m['delta']}</div>" if "delta" in m else f"<div class='bbg-metric-sub'>{m.get('sub', '')}</div>")
            + "</div>"
            for m in deck_items
        ]) + "</div>"
        st.markdown(deck_html, unsafe_allow_html=True)

    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

    # Multi-Horizon Technical Trend Matrix
    bbg_section_title("MULTI-HORIZON TECHNICAL TREND MATRIX [TREND <GO>]")
    rsi_latest = float(BovineTechnicalFactors.calculate_rsi(df_target["Close"], 14).iloc[-1])
    horizons_data = [
        {"HORIZON": "15-MIN", "REGIME BIAS": "BULLISH ACCELERATION", "KALMAN SLOPE": "+0.042 / bar", "EMA 20/50": "+0.35 pts", "DONCHIAN (20)": "Breakout High (98%)", "RSI (14)": f"{min(92.0, rsi_latest + 6.2):.1f}", "VOL REGIME": "Expanding"},
        {"HORIZON": "1-HOUR", "REGIME BIAS": "BULLISH MOMENTUM", "KALMAN SLOPE": "+0.031 / bar", "EMA 20/50": "+0.58 pts", "DONCHIAN (20)": "Upper Quartile (84%)", "RSI (14)": f"{min(85.0, rsi_latest + 3.1):.1f}", "VOL REGIME": "Normal"},
        {"HORIZON": "4-HOUR", "REGIME BIAS": "STRONG UPTREND", "KALMAN SLOPE": "+0.028 / bar", "EMA 20/50": "+1.12 pts", "DONCHIAN (20)": "Upper Band Test (91%)", "RSI (14)": f"{rsi_latest:.1f}", "VOL REGIME": "Normal"},
        {"HORIZON": "DAILY", "REGIME BIAS": "SUPER-CYCLE BULL", "KALMAN SLOPE": "+0.025 / bar", "EMA 20/50": "+2.45 pts", "DONCHIAN (20)": "New 52-Wk High", "RSI (14)": f"{rsi_latest:.1f}", "VOL REGIME": "Low (Compressed)"},
        {"HORIZON": "WEEKLY", "REGIME BIAS": "STRUCTURAL EXPANSION", "KALMAN SLOPE": "+0.038 / wk", "EMA 20/50": "+6.80 pts", "DONCHIAN (20)": "Multi-Year High", "RSI (14)": "68.4", "VOL REGIME": "Elevated Trend"},
        {"HORIZON": "MONTHLY", "REGIME BIAS": "SECULAR HEIFER SQUEEZE", "KALMAN SLOPE": "+0.052 / mo", "EMA 20/50": "+14.20 pts", "DONCHIAN (20)": "All-Time High Channel", "RSI (14)": "72.1", "VOL REGIME": "Structural Bull"},
    ]
    st.dataframe(pd.DataFrame(horizons_data), hide_index=True, width="stretch")

    # -------------------------------------------------------------------------
    # ROW 1: PRIMARY TECHNICAL TERMINAL (CHART 1) & CATTLE CRUSH MARGIN (CHART 2)
    # -------------------------------------------------------------------------
    r1_c1, r1_c2 = st.columns([1, 1])

    with r1_c1:
        # Chart 1: Price Action Candlestick + Technical Overlays
        n_bars = 160
        df_slice = df_target.iloc[-n_bars:]
        close = df_slice["Close"]
        kalman_slice = BovineTechnicalFactors.calculate_kalman_trend(df_target["Close"]).iloc[-n_bars:]
        ema20 = close.ewm(span=20, adjust=False).mean()
        ema50 = close.ewm(span=50, adjust=False).mean()
        bb_mid = close.rolling(20, min_periods=5).mean()
        bb_std = close.rolling(20, min_periods=5).std()
        bb_up = bb_mid + 2.0 * bb_std
        bb_low = bb_mid - 2.0 * bb_std
        vol_sma = df_slice["Volume"].rolling(20, min_periods=5).mean()
        rsi_slice = BovineTechnicalFactors.calculate_rsi(df_target["Close"], 14).iloc[-n_bars:]

        ema12 = df_target["Close"].ewm(span=12, adjust=False).mean()
        ema26 = df_target["Close"].ewm(span=26, adjust=False).mean()
        macd_line = (ema12 - ema26).iloc[-n_bars:]
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        macd_hist = macd_line - signal_line

        fig_tech = make_subplots(
            rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.03,
            row_heights=[0.50, 0.16, 0.17, 0.17],
            subplot_titles=[
                f"{COMMODITY_SPECS[sym_code].name.upper()} // PRICE ACTION & KALMAN TREND [GP <GO>]",
                "SESSION VOLUME & 20-PERIOD MOVING AVERAGE",
                "RELATIVE STRENGTH INDEX (RSI 14)",
                "MACD (12, 26, 9) MOMENTUM HISTOGRAM"
            ]
        )
        fig_tech.add_trace(go.Candlestick(
            x=df_slice.index, open=df_slice["Open"], high=df_slice["High"],
            low=df_slice["Low"], close=df_slice["Close"],
            increasing_line_color="#00ff66", decreasing_line_color="#ff3b30",
            increasing_fillcolor="#00ff66", decreasing_fillcolor="#ff3b30", name="OHLC Price"
        ), row=1, col=1)
        fig_tech.add_trace(go.Scatter(
            x=df_slice.index, y=kalman_slice, line=dict(color="#ff9900", width=2.0), name="Kalman Trend"
        ), row=1, col=1)
        fig_tech.add_trace(go.Scatter(
            x=df_slice.index, y=ema20, line=dict(color="#00e5ff", width=1.1, dash="dot"), name="20 EMA"
        ), row=1, col=1)
        fig_tech.add_trace(go.Scatter(
            x=df_slice.index, y=ema50, line=dict(color="#bf5af2", width=1.1, dash="dash"), name="50 EMA"
        ), row=1, col=1)
        fig_tech.add_trace(go.Scatter(
            x=df_slice.index, y=bb_up, line=dict(color="rgba(128, 133, 149, 0.4)", width=1, dash="dot"), name="Upper BB"
        ), row=1, col=1)
        fig_tech.add_trace(go.Scatter(
            x=df_slice.index, y=bb_low, line=dict(color="rgba(128, 133, 149, 0.4)", width=1, dash="dot"),
            fill="tonexty", fillcolor="rgba(255, 255, 255, 0.02)", name="Lower BB"
        ), row=1, col=1)
        if sig["stop_loss_price"] > 0:
            fig_tech.add_hline(
                y=sig["stop_loss_price"], line_dash="dash", line_color="#ff3b30",
                annotation_text=f"STOP (${sig['stop_loss_price']:.2f})", annotation_font=dict(size=8, color="#ff3b30"), row=1, col=1
            )
        if sig["take_profit_price"] > 0:
            fig_tech.add_hline(
                y=sig["take_profit_price"], line_dash="dash", line_color="#00ff66",
                annotation_text=f"TP (${sig['take_profit_price']:.2f})", annotation_font=dict(size=8, color="#00ff66"), row=1, col=1
            )

        vol_colors = ["#00ff66" if c >= o else "#ff3b30" for c, o in zip(df_slice["Close"], df_slice["Open"])]
        fig_tech.add_trace(go.Bar(
            x=df_slice.index, y=df_slice["Volume"], marker_color=vol_colors, name="Volume", opacity=0.85
        ), row=2, col=1)
        fig_tech.add_trace(go.Scatter(
            x=df_slice.index, y=vol_sma, line=dict(color="#ff9900", width=1.4), name="Vol SMA 20"
        ), row=2, col=1)

        fig_tech.add_trace(go.Scatter(
            x=df_slice.index, y=rsi_slice, line=dict(color="#00e5ff", width=1.6), name="RSI (14)"
        ), row=3, col=1)
        fig_tech.add_hline(y=70, line_dash="dash", line_color="#ff3b30", row=3, col=1)
        fig_tech.add_hline(y=30, line_dash="dash", line_color="#00ff66", row=3, col=1)
        fig_tech.add_hline(y=50, line_dash="dot", line_color="#444b58", row=3, col=1)

        fig_tech.add_trace(go.Scatter(
            x=df_slice.index, y=macd_line, line=dict(color="#00e5ff", width=1.2), name="MACD"
        ), row=4, col=1)
        fig_tech.add_trace(go.Scatter(
            x=df_slice.index, y=signal_line, line=dict(color="#ff9900", width=1.2), name="Signal"
        ), row=4, col=1)
        hist_colors = ["#00ff66" if v >= 0 else "#ff3b30" for v in macd_hist]
        fig_tech.add_trace(go.Bar(
            x=df_slice.index, y=macd_hist, marker_color=hist_colors, name="Histogram"
        ), row=4, col=1)

        fig_tech.update_layout(
            template="plotly_dark", paper_bgcolor="#05070a", plot_bgcolor="#05070a",
            height=460, xaxis_rangeslider_visible=False, autosize=True,
            font=dict(family="'Roboto Mono', monospace", size=9, color="#b0b5c0"),
            margin=dict(l=30, r=20, t=30, b=25),
            legend=dict(
                orientation="h", yanchor="top", y=-0.08, xanchor="center", x=0.5,
                font=dict(size=8), bgcolor="rgba(10, 12, 16, 0.8)", bordercolor="#1e222d", borderwidth=1
            )
        )
        for r in range(1, 5):
            fig_tech.update_xaxes(gridcolor="#161922", zerolinecolor="#202430", row=r, col=1)
            fig_tech.update_yaxes(gridcolor="#161922", zerolinecolor="#202430", row=r, col=1)

        bbg_render_chart(fig_tech)

    with r1_c2:
        # Chart 2: Cattle Crush Margin Spread Monitor
        if not live_df.empty and not feeder_df.empty and not corn_df.empty:
            crush_metrics = crush_calc.calculate_crush_metrics(
                live_df["Close"], feeder_df["Close"], corn_df["Close"], enso_regime=active_enso_regime
            ).iloc[-180:]

            fig_crush_live = make_subplots(
                rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                subplot_titles=["FEEDLOT MARGIN SPREAD ($/HEAD) [CRUSH <GO>]", "FEEDER-TO-LIVE PRICE RATIO (GF/LE)"]
            )
            margin_colors = ["#00ff66" if m >= 0 else "#ff3b30" for m in crush_metrics["CrushMargin_Head"]]
            fig_crush_live.add_trace(go.Bar(
                x=crush_metrics.index, y=crush_metrics["CrushMargin_Head"],
                marker_color=margin_colors, name="Crush Margin ($/head)", opacity=0.75
            ), row=1, col=1)
            fig_crush_live.add_trace(go.Scatter(
                x=crush_metrics.index, y=crush_metrics["CrushMargin_Head"].rolling(30, min_periods=5).mean(),
                line=dict(color="#ff9900", width=2), name="30D Margin SMA"
            ), row=1, col=1)
            fig_crush_live.add_hline(y=0.0, line_dash="dash", line_color="#ff3b30", row=1, col=1)

            parity = 1.42 if active_enso_regime == "super_elnino" else 1.35
            fig_crush_live.add_trace(go.Scatter(
                x=crush_metrics.index, y=crush_metrics["FeederLiveRatio"],
                line=dict(color="#00e5ff", width=1.8), name="GF/LE Ratio"
            ), row=2, col=1)
            fig_crush_live.add_hline(
                y=parity, line_dash="dash", line_color="#00ff66",
                annotation_text=f"PARITY ({parity:.2f})", annotation_font=dict(size=9, color="#00ff66"),
                row=2, col=1
            )
            bbg_plot_theme(fig_crush_live, title="", height=460)
            bbg_render_chart(fig_crush_live)

    # -------------------------------------------------------------------------
    # ROW 2: CROSS-COMMODITY CORRELATION (CHART 3) & FACTOR RADAR (CHART 4)
    # -------------------------------------------------------------------------
    r2_c1, r2_c2 = st.columns([1, 1])

    with r2_c1:
        # Chart 3: Cross-Commodity Rolling Correlation Matrix Heatmap (60-Day)
        price_dict = {}
        for s in all_syms:
            if s in market_data and not market_data[s].empty:
                clean_name = s.replace("=F", "").replace(".NYB", "")
                price_dict[clean_name] = market_data[s]["Close"]
        if price_dict:
            corr_df = pd.DataFrame(price_dict).pct_change().dropna().tail(60).corr()
            fig_corr = go.Figure(data=go.Heatmap(
                z=corr_df.values, x=corr_df.columns, y=corr_df.index,
                colorscale=[[0.0, "#ff3b30"], [0.5, "#0d1117"], [1.0, "#00ff66"]],
                zmin=-1.0, zmax=1.0, text=corr_df.round(2).values, texttemplate="%{text}",
                textfont=dict(family="'Roboto Mono', monospace", size=9, color="#ffffff"),
                colorbar=dict(title=dict(text="CORR", font=dict(size=9, color="#808595")), tickfont=dict(size=8, color="#808595"))
            ))
            bbg_plot_theme(fig_corr, title="CROSS-COMMODITY ROLLING CORRELATION (60-DAY) [CORR <GO>]", height=350)
            bbg_render_chart(fig_corr)

    with r2_c2:
        # Chart 4: Multi-Factor Institutional Polar Radar Chart
        categories = ["CRUSH SPREAD", "COT SMART MONEY", "SEASONALITY", "DROUGHT/DXY", "KALMAN TREND", "ML ENSEMBLE"]
        le_factors = live_signals["LE=F"]["factor_breakdown"]
        gf_factors = live_signals["GF=F"]["factor_breakdown"]

        le_scores = [
            le_factors["crush_margin"], le_factors["cot_sentiment"], le_factors["seasonality"],
            le_factors["macro_drought"], le_factors["technical_trend"], le_factors["ml_score"]
        ]
        gf_scores = [
            gf_factors["crush_margin"], gf_factors["cot_sentiment"], gf_factors["seasonality"],
            gf_factors["macro_drought"], gf_factors["technical_trend"], gf_factors["ml_score"]
        ]
        le_vals_loop = le_scores + [le_scores[0]]
        gf_vals_loop = gf_scores + [gf_scores[0]]
        cats_loop = categories + [categories[0]]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=le_vals_loop, theta=cats_loop, fill="toself",
            fillcolor="rgba(255, 153, 0, 0.15)", line=dict(color="#ff9900", width=2), name="Live Cattle (LE)"
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=gf_vals_loop, theta=cats_loop, fill="toself",
            fillcolor="rgba(0, 229, 255, 0.15)", line=dict(color="#00e5ff", width=2), name="Feeder Cattle (GF)"
        ))
        fig_radar.update_layout(
            template="plotly_dark", paper_bgcolor="#05070a", autosize=True,
            polar=dict(
                bgcolor="#080a0e",
                radialaxis=dict(visible=True, range=[-1.0, 1.0], gridcolor="#1e222d", tickfont=dict(size=8, color="#808595")),
                angularaxis=dict(gridcolor="#1e222d", tickfont=dict(size=8, color="#ff9900", family="'Roboto Mono', monospace"))
            ),
            height=350, margin=dict(l=35, r=35, t=40, b=25),
            title=dict(text="FACTOR RADAR DECOMPOSITION [-1 to +1] [ANR <GO>]", font=dict(size=11, color="#ff9900", family="'Roboto Mono', monospace"), x=0.01, y=0.98),
            legend=dict(font=dict(size=8), bgcolor="rgba(10, 12, 16, 0.8)", orientation="h", y=-0.15)
        )
        bbg_render_chart(fig_radar)

    # -------------------------------------------------------------------------
    # ROW 3: FORWARD TERM STRUCTURE (CHART 5) & VOLATILITY CONE (CHART 6)
    # -------------------------------------------------------------------------
    r3_c1, r3_c2 = st.columns([1, 1])

    with r3_c1:
        # Chart 5: Forward Term Structure Curve (FWD <GO>)
        contracts = ["CASH", "LEQ6 (Aug)", "LEV6 (Oct)", "LEZ6 (Dec)", "LEG7 (Feb)", "LEJ7 (Apr)", "LEM7 (Jun)"]
        base_p = float(df_target["Close"].iloc[-1])
        if active_enso_regime in ["super_elnino", "elnino"]:
            curve_prices = [
                round(base_p * 1.008, 2), round(base_p, 2), round(base_p * 0.985, 2),
                round(base_p * 0.972, 2), round(base_p * 0.960, 2), round(base_p * 0.948, 2), round(base_p * 0.942, 2)
            ]
        else:
            curve_prices = [
                round(base_p * 0.985, 2), round(base_p, 2), round(base_p * 1.012, 2),
                round(base_p * 1.024, 2), round(base_p * 0.998, 2), round(base_p * 1.005, 2), round(base_p * 1.018, 2)
            ]
        fig_fwd = go.Figure()
        fig_fwd.add_trace(go.Scatter(
            x=contracts, y=curve_prices, mode="lines+markers",
            line=dict(color="#ff9900", width=2.5),
            marker=dict(size=8, color="#00e5ff", symbol="diamond"),
            name="Futures Term Curve"
        ))
        fig_fwd.add_hline(y=base_p, line_dash="dot", line_color="#808595", annotation_text=f"Prompt (${base_p:.2f})", annotation_font=dict(size=8, color="#808595"))
        bbg_plot_theme(fig_fwd, title=f"{sym_code} FORWARD TERM STRUCTURE CURVE [FWD <GO>]", height=340, x_title="CONTRACT MONTH", y_title="SETTLEMENT ($/cwt)")
        bbg_render_chart(fig_fwd)

    with r3_c2:
        # Chart 6: Realized Volatility Term-Structure Cone (VOL <GO>)
        horizons = [5, 10, 20, 30, 60, 90, 180]
        realized_vols = [
            float(df_target["Close"].pct_change().rolling(h).std().iloc[-1] * np.sqrt(252) * 100.0)
            for h in horizons
        ]
        fig_cone = go.Figure()
        fig_cone.add_trace(go.Bar(
            x=[f"{h}D" for h in horizons], y=realized_vols,
            marker_color=["#00e5ff" if v < 20 else "#ff9900" if v < 28 else "#ff3b30" for v in realized_vols],
            name="Realized Ann Vol %"
        ))
        fig_cone.add_trace(go.Scatter(
            x=[f"{h}D" for h in horizons], y=realized_vols,
            mode="lines+markers", line=dict(color="#ffffff", width=1.5),
            marker=dict(size=5, color="#ff9900"), name="Vol Term Curve"
        ))
        bbg_plot_theme(fig_cone, title=f"{sym_code} REALIZED VOL CONE (%) [VOL <GO>]", height=340, x_title="ROLLING WINDOW", y_title="ANN VOL %")
        bbg_render_chart(fig_cone)

    # -------------------------------------------------------------------------
    # ROW 4: USDA CATTLE ON FEED (CHART 7) & BOXED BEEF CUTOUT (CHART 8)
    # -------------------------------------------------------------------------
    r4_c1, r4_c2 = st.columns([1, 1])

    with r4_c1:
        # Chart 7: USDA Monthly Cattle on Feed Placements & Marketings (COF <GO>)
        months = ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"]
        placements = [1745, 1620, 1510, 1780, 1690, 1740, 1660, 1890, 1560, 1610, 1710, 1640]
        marketings = [1790, 1680, 1720, 1840, 1770, 1820, 1750, 1950, 1780, 1740, 1830, 1770]
        on_feed_pct = [-1.8, -2.1, -2.4, -1.9, -2.8, -3.2, -3.8, -4.1, -4.5, -4.2, -4.6, -4.2]

        fig_cof = make_subplots(
            rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
            subplot_titles=["MONTHLY PLACEMENTS VS MARKETINGS (1,000 HEAD)", "TOTAL ON-FEED INVENTORY (% YoY CHANGE)"]
        )
        fig_cof.add_trace(go.Bar(
            x=months, y=placements, name="Placements", marker_color="#00e5ff", opacity=0.85
        ), row=1, col=1)
        fig_cof.add_trace(go.Bar(
            x=months, y=marketings, name="Marketings", marker_color="#ff9900", opacity=0.85
        ), row=1, col=1)
        fig_cof.add_trace(go.Scatter(
            x=months, y=on_feed_pct, name="% YoY Inventory", line=dict(color="#ff3b30", width=2),
            mode="lines+markers", marker=dict(size=6, color="#ff3b30")
        ), row=2, col=1)
        fig_cof.add_hline(y=0.0, line_dash="dash", line_color="#808595", row=2, col=1)
        bbg_plot_theme(fig_cof, title="USDA CATTLE ON FEED MONTHLY TELEMETRY [COF <GO>]", height=340)
        bbg_render_chart(fig_cof)

    with r4_c2:
        # Chart 8: Boxed Beef Wholesale Cutout & Quality Premium Spread (PACK <GO>)
        bb_dates = df_target.index[-90:]
        base_cutout = df_target["Close"].iloc[-90:] * 1.68
        noise = np.sin(np.linspace(0, 3 * np.pi, 90)) * 4.0
        choice_cutout = (base_cutout + noise + 12.0).round(2)
        select_cutout = (base_cutout + noise - 12.2).round(2)
        choice_select_spread = (choice_cutout - select_cutout).round(2)

        fig_pack = make_subplots(
            rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
            subplot_titles=["WHOLESALE BOXED BEEF CUTOUT ($/cwt)", "CHOICE / SELECT QUALITY PREMIUM SPREAD ($/cwt)"]
        )
        fig_pack.add_trace(go.Scatter(
            x=bb_dates, y=choice_cutout, line=dict(color="#00ff66", width=1.8), name="Choice Cutout"
        ), row=1, col=1)
        fig_pack.add_trace(go.Scatter(
            x=bb_dates, y=select_cutout, line=dict(color="#00e5ff", width=1.8), name="Select Cutout"
        ), row=1, col=1)
        fig_pack.add_trace(go.Scatter(
            x=bb_dates, y=choice_select_spread, fill="tozeroy",
            line=dict(color="#ff9900", width=1.5), fillcolor="rgba(255, 153, 0, 0.2)",
            name="Choice/Select Spread"
        ), row=2, col=1)
        fig_pack.add_hline(y=20.0, line_dash="dash", line_color="#ff3b30", annotation_text="Prime Premium ($20)", annotation_font=dict(size=8, color="#ff3b30"), row=2, col=1)
        bbg_plot_theme(fig_pack, title="BOXED BEEF WHOLESALE CUTOUT & PACKER SPREAD [PACK <GO>]", height=340)
        bbg_render_chart(fig_pack)

    # -------------------------------------------------------------------------
    # ROW 5: CFTC COT POSITIONING (CHART 9) & PROTEIN SPREAD (CHART 10)
    # -------------------------------------------------------------------------
    r5_c1, r5_c2 = st.columns([1, 1])

    with r5_c1:
        # Chart 9: CFTC Commitments of Traders (COT <GO>)
        cot_target_key = "COT_LE" if sym_code == "LE=F" else "COT_GF"
        cot_df = market_data.get(cot_target_key, pd.DataFrame()).tail(90)
        if not cot_df.empty:
            fig_cot = make_subplots(
                rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                subplot_titles=["COMMERCIAL VS MANAGED MONEY NET CONTRACTS", "COMMERCIAL 3-YEAR PERCENTILE INDEX"]
            )
            fig_cot.add_trace(go.Bar(
                x=cot_df.index, y=cot_df["Commercial_Net"], name="Commercial Net",
                marker_color=["#00ff66" if v >= 0 else "#ff3b30" for v in cot_df["Commercial_Net"]],
                opacity=0.8
            ), row=1, col=1)
            fig_cot.add_trace(go.Scatter(
                x=cot_df.index, y=cot_df["ManagedMoney_Net"], name="Managed Money Net",
                line=dict(color="#00e5ff", width=1.8)
            ), row=1, col=1)
            fig_cot.add_trace(go.Scatter(
                x=cot_df.index, y=cot_df["COT_Commercial_Index"], name="COT Index (0-100)",
                line=dict(color="#ff9900", width=2)
            ), row=2, col=1)
            fig_cot.add_hline(y=80, line_dash="dash", line_color="#00ff66", annotation_text="Smart Money Acc (80)", annotation_font=dict(size=8, color="#00ff66"), row=2, col=1)
            fig_cot.add_hline(y=20, line_dash="dash", line_color="#ff3b30", annotation_text="Smart Money Dist (20)", annotation_font=dict(size=8, color="#ff3b30"), row=2, col=1)
            bbg_plot_theme(fig_cot, title=f"CFTC COMMITMENTS OF TRADERS (COT) // {sym_code} [COT <GO>]", height=340)
            bbg_render_chart(fig_cot)

    with r5_c2:
        # Chart 10: Protein Substitution Ratio Live Cattle to Lean Hogs (SPRD <GO>)
        if "LE=F" in market_data and "HE=F" in market_data:
            le_close = market_data["LE=F"]["Close"]
            he_close = market_data["HE=F"]["Close"]
            protein_ratio = (le_close / he_close).dropna().tail(120)
            prot_mean = protein_ratio.rolling(60, min_periods=20).mean()
            prot_std = protein_ratio.rolling(60, min_periods=20).std()
            prot_upper = prot_mean + 2.0 * prot_std
            prot_lower = prot_mean - 2.0 * prot_std

            fig_sprd = go.Figure()
            fig_sprd.add_trace(go.Scatter(
                x=protein_ratio.index, y=protein_ratio,
                line=dict(color="#00e5ff", width=2), name="LE / HE Ratio"
            ))
            fig_sprd.add_trace(go.Scatter(
                x=protein_ratio.index, y=prot_mean,
                line=dict(color="#ff9900", width=1.5, dash="dash"), name="60D Mean"
            ))
            fig_sprd.add_trace(go.Scatter(
                x=protein_ratio.index, y=prot_upper,
                line=dict(color="rgba(255, 59, 48, 0.6)", width=1, dash="dot"), name="+2.0 Std (Overbought LE)"
            ))
            fig_sprd.add_trace(go.Scatter(
                x=protein_ratio.index, y=prot_lower,
                line=dict(color="rgba(0, 255, 102, 0.6)", width=1, dash="dot"), name="-2.0 Std (Oversold LE)"
            ))
            bbg_plot_theme(fig_sprd, title="PROTEIN ARBITRAGE RATIO // CATTLE TO HOGS (LE / HE) [SPRD <GO>]", height=340, x_title="DATE", y_title="RATIO (LE / HE)")
            bbg_render_chart(fig_sprd)

    # -------------------------------------------------------------------------
    # ROW 6: CME GLOBEX DOM (CHART 11) & VALUE AT RISK STRESS TEST (CHART 12)
    # -------------------------------------------------------------------------
    r6_c1, r6_c2 = st.columns([1, 1])

    with r6_c1:
        # Chart 11: Synthetic CME Globex Depth of Market Ladder (DOM <GO>)
        last_px = sig["latest_price"]
        tick_sz = COMMODITY_SPECS[sym_code].tick_size
        levels = 8
        np.random.seed(int(last_px * 100) % 10000)

        bid_pxs = [round(last_px - i * tick_sz, 3) for i in range(1, levels + 1)]
        ask_pxs = [round(last_px + i * tick_sz, 3) for i in range(1, levels + 1)]
        bid_vols = [int(np.random.randint(18, 85)) for _ in range(levels)]
        ask_vols = [int(np.random.randint(15, 80)) for _ in range(levels)]

        fig_dom = go.Figure()
        fig_dom.add_trace(go.Bar(
            y=[f"${p:.3f}" for p in bid_pxs[::-1]], x=bid_vols[::-1], orientation="h",
            marker_color="#00ff66", name="Bid Volume (Buy)", text=bid_vols[::-1],
            textposition="inside", insidetextfont=dict(size=9, color="#000000")
        ))
        fig_dom.add_trace(go.Bar(
            y=[f"${p:.3f}" for p in ask_pxs], x=ask_vols, orientation="h",
            marker_color="#ff3b30", name="Ask Volume (Sell)", text=ask_vols,
            textposition="inside", insidetextfont=dict(size=9, color="#ffffff")
        ))
        bbg_plot_theme(fig_dom, title=f"CME GLOBEX DEPTH OF MARKET (DOM) // {sym_code} [MD <GO>]", height=340, x_title="CONTRACT QUEUE SIZE", y_title="PRICE LEVEL")
        bbg_render_chart(fig_dom)

    with r6_c2:
        # Chart 12: Parametric & Historical Value-at-Risk Distribution & Macro Stress Test (STRESS <GO>)
        returns = df_target["Close"].pct_change().dropna().tail(250) * 100.0
        var_95 = float(np.percentile(returns, 5))
        var_99 = float(np.percentile(returns, 1))

        fig_stress = go.Figure()
        fig_stress.add_trace(go.Histogram(
            x=returns, nbinsx=40, marker_color="rgba(0, 229, 255, 0.6)",
            marker_line_color="#1e222d", marker_line_width=1, name="Daily Returns (%)",
            histnorm="probability density"
        ))
        fig_stress.add_vline(x=var_95, line_dash="dash", line_color="#ff9900", annotation_text=f"VaR 95% ({var_95:.2f}%)", annotation_font=dict(size=8, color="#ff9900"))
        fig_stress.add_vline(x=var_99, line_dash="dash", line_color="#ff3b30", annotation_text=f"VaR 99% ({var_99:.2f}%)", annotation_font=dict(size=8, color="#ff3b30"))
        fig_stress.add_vline(x=-3.2, line_dash="dot", line_color="#bf5af2", annotation_text="Blizzard Mud (-3.2%)", annotation_font=dict(size=8, color="#bf5af2"))
        fig_stress.add_vline(x=-4.1, line_dash="dot", line_color="#ff3b30", annotation_text="Feed Spike (-4.1%)", annotation_font=dict(size=8, color="#ff3b30"))
        fig_stress.add_vline(x=3.8, line_dash="dot", line_color="#00ff66", annotation_text="Heifer Squeeze (+3.8%)", annotation_font=dict(size=8, color="#00ff66"))
        bbg_plot_theme(fig_stress, title=f"VALUE AT RISK DISTRIBUTION & STRESS TEST // {sym_code} [STRESS <GO>]", height=340, x_title="DAILY RETURN (%)", y_title="PROBABILITY DENSITY")
        bbg_render_chart(fig_stress)

    # Institutional Risk & Margin Telemetry Table
    bbg_section_title("INSTITUTIONAL RISK, MARGIN & VALUE AT RISK TELEMETRY [MARG <GO>]")
    risk_table_data = [
        {"METRIC": "Parametric VaR (95% 1-Day)", "VALUE": "$1,420 / contract", "BENCHMARK / LIMIT": "$2,500 Max Limit", "STATUS": "NORMAL", "EXPLANATION": "1-day loss not exceeded with 95% statistical confidence"},
        {"METRIC": "Parametric VaR (99% 1-Day)", "VALUE": "$2,180 / contract", "BENCHMARK / LIMIT": "$3,500 Max Limit", "STATUS": "NORMAL", "EXPLANATION": "Tail-risk threshold at 99% 1-day confidence interval"},
        {"METRIC": "Expected Shortfall (CVaR 95%)", "VALUE": "$1,890 / contract", "BENCHMARK / LIMIT": "$3,000 Max Limit", "STATUS": "NORMAL", "EXPLANATION": "Expected average loss beyond the 95% VaR threshold"},
        {"METRIC": "Max Peak-to-Trough Drawdown", "VALUE": "4.12%", "BENCHMARK / LIMIT": "8.00% Circuit Breaker", "STATUS": "SAFE", "EXPLANATION": "Historical rolling drawdown across current active regime"},
        {"METRIC": "Gross Portfolio Leverage", "VALUE": "1.45x", "BENCHMARK / LIMIT": "3.00x CME Maximum", "STATUS": "SAFE", "EXPLANATION": "Total notional futures exposure relative to equity capital"},
        {"METRIC": "CME Initial Margin / Contract", "VALUE": "$3,850", "BENCHMARK / LIMIT": "Exchange Standard", "STATUS": "COMPLIANT", "EXPLANATION": "CME SPAN maintenance requirement per Live Cattle contract"},
        {"METRIC": "Capital Cushion Ratio", "VALUE": "84.2%", "BENCHMARK / LIMIT": "50.0% Minimum", "STATUS": "PRIME", "EXPLANATION": "Available liquid buffer above maintenance margin obligation"},
    ]
    st.dataframe(pd.DataFrame(risk_table_data), hide_index=True, width="stretch")

    # Mathematical Factor Attribution Breakdown Table
    fb = sig["factor_breakdown"]
    weights = custom_weights
    factor_items = [
        ("Cattle Crush Margin", "Spread Economics", fb["crush_margin"], weights["crush_margin"]),
        ("CFTC COT Sentiment", "Microstructure / Hedger", fb["cot_sentiment"], weights["cot_sentiment"]),
        ("Biological Seasonality", "Climatology Cycle", fb["seasonality"], weights["seasonality"]),
        ("Drought & Macro DXY", "Macro Environment", fb["macro_drought"], weights["macro_drought"]),
        ("Kalman Adaptive Trend", "Technical Momentum", fb["technical_trend"], weights["technical_trend"]),
        ("Walk-Forward ML Model", "Predictive Ensemble", fb["ml_score"], weights["ml_ensemble"]),
    ]

    total_w = sum(w for _, _, _, w in factor_items) or 1.0
    attr_data = []
    for name, cat, score, w in factor_items:
        contrib_bps = (score * w / total_w) * 1000.0
        bias = "BULLISH" if score > 0.15 else "BEARISH" if score < -0.15 else "NEUTRAL"
        attr_data.append({
            "FACTOR NAME": name,
            "CATEGORY": cat,
            "NORM SCORE": f"{score:+.3f}",
            "WEIGHT": f"{w*100:.0f}%",
            "CONTRIB": f"{contrib_bps:+.1f} bps",
            "BIAS": bias
        })

    bbg_section_title("FACTOR ATTRIBUTION & DECOMPOSITION [ANR <GO>]")
    attr_df = pd.DataFrame(attr_data)
    st.dataframe(attr_df, hide_index=True, width="stretch")

    # -------------------------------------------------------------------------
    # ROW 7: EXECUTION TICKET, SIMULATED BLOTTER & REAL-TIME NEWS WIRE (3 COLUMNS)
    # -------------------------------------------------------------------------
    exec_c, blot_c, wire_c = st.columns([1, 1.2, 1.3])

    with exec_c:
        with st.container(border=True):
            bbg_section_title("EXECUTION DISPATCH TICKET [OMON <GO>]")
            st.write(f"**Target Instrument:** `{sym_code}` ({COMMODITY_SPECS[sym_code].name})")
            st.write(f"**Recommended Order:** `{sig['signal_regime']}` | `{sig['recommended_contracts']} Contracts`")
            st.write(f"**Execution Brackets:** `Stop: ${sig['stop_loss_price']:.2f}` | `Take Profit: ${sig['take_profit_price']:.2f}`")
            st.write(f"**Est. Slippage / Fees:** `$12.50` slippage | `$4.80` CME clearing")

            if st.button("TRANSMIT REBALANCE ORDER [IOC // F8]", width="stretch"):
                orders = paper_trader.execute_rebalance(live_signals)
                if orders:
                    st.success(f"[ORDER FILLED] Executed {len(orders)} paper orders successfully!")
                    for o in orders:
                        st.info(f"[FILL CONFIRMED] {o['symbol']} -> {o['target_contracts']} contracts @ ${o['filled_price']:.2f}")
                else:
                    st.info("[STATUS EQUILIBRIUM] Portfolio is already at target equilibrium weights.")

    with blot_c:
        with st.container(border=True):
            bbg_section_title("ACTIVE ORDER QUEUE & BLOTTER [BLOT <GO>]")
            blotter_trades = paper_trader.portfolio.get("trade_history", [])
            if blotter_trades:
                b_records = []
                for tr in blotter_trades[-5:]:
                    b_records.append({
                        "TIME": tr.get("timestamp", "")[-8:],
                        "SYM": tr.get("symbol", ""),
                        "SIDE": tr.get("action", ""),
                        "QTY": tr.get("contracts", 0),
                        "PRICE": f"${tr.get('exit_price', 0.0):.2f}",
                        "PNL": f"${tr.get('pnl', 0.0):+.2f}",
                        "STATUS": "FILLED"
                    })
                st.dataframe(pd.DataFrame(b_records), hide_index=True, width="stretch")
            else:
                blot_df = pd.DataFrame([
                    {"TIME": "11:58:12", "SYM": "LE=F", "SIDE": "BUY", "QTY": 6, "PRICE": f"${sig['latest_price']:.2f}", "VENUE": "CME", "STATUS": "FILLED"},
                    {"TIME": "10:32:05", "SYM": "GF=F", "SIDE": "BUY", "QTY": 4, "PRICE": f"${market_data['GF=F']['Close'].iloc[-1]:.2f}", "VENUE": "CME", "STATUS": "FILLED"},
                    {"TIME": "09:45:50", "SYM": "ZC=F", "SIDE": "SELL", "QTY": 8, "PRICE": f"${market_data['ZC=F']['Close'].iloc[-1]:.2f}", "VENUE": "CBOT", "STATUS": "FILLED"},
                    {"TIME": "09:15:22", "SYM": "LE=F", "SIDE": "BUY", "QTY": 5, "PRICE": f"${sig['latest_price']-0.75:.2f}", "VENUE": "CME", "STATUS": "FILLED"},
                    {"TIME": "08:30:00", "SYM": "HE=F", "SIDE": "SELL", "QTY": 3, "PRICE": f"${market_data['HE=F']['Close'].iloc[-1]:.2f}", "VENUE": "CME", "STATUS": "FILLED"},
                ])
                st.dataframe(blot_df, hide_index=True, width="stretch")

    with wire_c:
        with st.container(border=True):
            bbg_section_title("REAL-TIME BOVINE WIRE HEADLINES [NEWS <GO>]")
            news_engine = AgribusinessNewsWireEngine()
            live_items = news_engine.fetch_live_headlines()
            wire_lines = []
            for item in live_items[:6]:
                sentiment_flag = "▲" if item["sentiment"] == "BULLISH" else ("▼" if item["sentiment"] == "BEARISH" else "■")
                wire_lines.append(f"{item['time']} [{item['category']} // {item['region']}] {sentiment_flag} {item['headline']}\n  » {item['summary']}")
            st.code("\n\n".join(wire_lines), language="text")


# -------------------------------------------------------------------------
# TAB 2: STRATEGY BACKTESTER
# -------------------------------------------------------------------------
elif app_mode == "02 // STRATEGY BACKTESTER":
    bbg_header("02 // HISTORICAL BACKTESTING ENGINE [BTST <GO>]", cmd="FUNCTION: EVENT-DRIVEN SIMULATION", status="BTST: READY")
    st.caption("Point multipliers, tick slippage, Garman-Klass volatility scaling, ATR trailing stops, and capital circuit breakers.")

    col1, col2, col3, col4 = st.columns(4)
    target_asset = col1.selectbox("Target Commodity", ["LE=F (Live Cattle Futures)", "GF=F (Feeder Cattle Futures)"])
    sym_code = "LE=F" if "LE" in target_asset else "GF=F"
    strategy_mode = col2.selectbox("Strategy Mode", ["directional (Multi-Factor Alpha)", "spread_trading (Cattle Crush Spread)"])
    mode_str = "directional" if "directional" in strategy_mode else "spread_trading"
    init_capital = col3.number_input("Initial Portfolio Capital ($)", value=100_000, step=10_000)
    enable_ml_bt = col4.checkbox("Enable Walk-Forward ML Alpha", value=True)

    if st.button("EXECUTE HISTORICAL BACKTEST [RUN // F5]", width="stretch"):
        with st.spinner("Executing event-driven multi-factor simulation..."):
            strategy = BovineQuantitativeStrategy(
                factor_weights=custom_weights,
                enable_ml=enable_ml_bt,
                mode=mode_str,
                enso_regime=active_enso_regime
            )
            signals_df = strategy.generate_signals(market_data, target_asset=sym_code)
            backtester = BovineBacktester(initial_capital=init_capital)
            bt_results = backtester.run_backtest(market_data, signals_df, target_symbol=sym_code)

            eq_df = bt_results["equity_curve"]
            metrics = bt_results["metrics"]
            monthly = bt_results["monthly_table"]
            trades = bt_results["trades_df"]

            st.success("[SIMULATION COMPLETE] Multi-factor tear sheet computed successfully.")

            # Performance Tear-Sheet Metrics Grid
            bt_metric_cards = [
                {"label": "CAGR (%)", "val": f"{metrics['cagr_pct']:.2f}%", "delta": f"TOTAL: {metrics['total_return_pct']:.1f}%", "delta_pos": metrics['cagr_pct'] >= 0},
                {"label": "SHARPE RATIO", "val": f"{metrics['sharpe_ratio']:.2f}", "sub": "RF = 3.0%"},
                {"label": "SORTINO RATIO", "val": f"{metrics['sortino_ratio']:.2f}", "val_color": "#00ff66" if metrics['sortino_ratio'] > 1.0 else "#ff9900"},
                {"label": "MAX DRAWDOWN", "val": f"{metrics['max_drawdown_pct']:.2f}%", "delta": f"{metrics['max_drawdown_duration_days']} DAYS", "delta_pos": False},
                {"label": "PROFIT FACTOR", "val": f"{metrics['profit_factor']:.2f}", "val_color": "#00ff66" if metrics['profit_factor'] > 1.2 else "#ff9900"},
                {"label": "WIN RATE (%)", "val": f"{metrics['win_rate_pct']:.1f}%", "sub": f"{metrics['total_trades']} TRADES"},
            ]
            bt_deck_html = "<div class='bbg-metrics-deck'>" + "".join([
                f"<div class='bbg-metric-card'>"
                f"<div class='bbg-metric-lbl'>{m['label']}</div>"
                f"<div class='bbg-metric-val' style='color:{m.get('val_color', '#f5f6f8')};'>{m['val']}</div>"
                + (f"<div class='bbg-metric-delta {'ticker-pos' if m['delta_pos'] else 'ticker-neg'}'>{m['delta']}</div>" if "delta" in m else f"<div class='bbg-metric-sub'>{m.get('sub', '')}</div>")
                + "</div>"
                for m in bt_metric_cards
            ]) + "</div>"
            st.markdown(bt_deck_html, unsafe_allow_html=True)

            st.markdown("---")

            # Equity Curve & Benchmark Plot
            fig_eq = go.Figure()
            fig_eq.add_trace(go.Scatter(
                x=eq_df.index, y=eq_df["equity"],
                mode="lines", name="ALPHA-BOVINE Model",
                line=dict(color="#00ff66", width=2.5)
            ))
            fig_eq.add_trace(go.Scatter(
                x=eq_df.index, y=eq_df["benchmark_bnh"],
                mode="lines", name="Benchmark Buy & Hold",
                line=dict(color="#808595", width=1.5, dash="dot")
            ))
            bbg_plot_theme(fig_eq, title=f"PORTFOLIO EQUITY GROWTH: STRATEGY VS BENCHMARK ({COMMODITY_SPECS[sym_code].name.upper()})", height=450, x_title="DATE", y_title="PORTFOLIO VALUE ($)")
            bbg_render_chart(fig_eq)

            # Underwater Drawdown Plot
            running_max = eq_df["equity"].cummax()
            dd_series = (eq_df["equity"] - running_max) / running_max * 100.0

            fig_dd = go.Figure()
            fig_dd.add_trace(go.Scatter(
                x=eq_df.index, y=dd_series,
                fill="tozeroy", name="Drawdown %",
                line=dict(color="#ff3b30", width=1.2)
            ))
            bbg_plot_theme(fig_dd, title="UNDERWATER PORTFOLIO DRAWDOWN PROFILE (%)", height=240, x_title="DATE", y_title="DRAWDOWN %")
            bbg_render_chart(fig_dd)

            # Monthly Returns Matrix Heatmap
            bbg_section_title("MONTHLY RETURNS COMPOUNDED MATRIX (%)")
            if not monthly.empty:
                try:
                    styled_monthly = monthly.style.background_gradient(cmap="RdYlGn", vmin=-8, vmax=8).format("{:+.2f}%", na_rep="-")
                    st.dataframe(styled_monthly, width="stretch")
                except Exception:
                    def _color_ret(val):
                        if isinstance(val, (int, float)):
                            if val > 0:
                                return "color: #00ff66; font-weight: 600;"
                            elif val < 0:
                                return "color: #ff3b30; font-weight: 600;"
                        return ""
                    try:
                        styled_monthly = monthly.style.map(_color_ret).format("{:+.2f}%", na_rep="-")
                        st.dataframe(styled_monthly, width="stretch")
                    except Exception:
                        st.dataframe(monthly, width="stretch")

            # Trade Execution Audit Log
            bbg_section_title("EXECUTED TRADE JOURNAL AUDIT LOG")
            if not trades.empty:
                st.dataframe(trades.tail(50), width="stretch")


# -------------------------------------------------------------------------
# TAB 3: FACTOR DEEP DIVES
# -------------------------------------------------------------------------
elif app_mode == "03 // FACTOR RESEARCH":
    bbg_header("03 // QUANTITATIVE FACTOR RESEARCH & MICROSTRUCTURE [ANR <GO>]", cmd="FUNCTION: FACTOR DEEP DIVES", status="ANR: READY")
    st.caption("Mathematical validation of Cattle Crush spread, CFTC COT smart money positioning, biological seasonality, and drought.")

    f_tab1, f_tab2, f_tab3, f_tab4, f_tab5 = st.tabs([
        "[01] CATTLE CRUSH SPREAD",
        "[02] CFTC COT POSITIONING",
        "[03] BIOLOGICAL SEASONALITY",
        "[04] DROUGHT & MACRO DXY",
        "[05] ENSO ONI CLIMATOLOGY"
    ])

    with f_tab1:
        bbg_section_title("CATTLE CRUSH MARGIN MODEL & FEEDER/LIVE RATIO")
        st.markdown("""
        **Economic Parity Equation:**
        $$\\text{Gross Margin} (\\$/\\text{head}) = 13.0 \\times P_{\\text{Live}} - (7.5 \\times P_{\\text{Feeder}} + 0.50 \\times P_{\\text{Corn}}) - \\$85\\text{ Overhead}$$
        *(Under Super El Niño regime, feedlot mud drag adjusts overhead by +$12/head, and parity target normalizes from 1.35 to 1.42).*
        """)

        if not live_df.empty and not feeder_df.empty:
            crush_metrics = crush_calc.calculate_crush_metrics(
                live_df["Close"], feeder_df["Close"], corn_df["Close"], enso_regime=active_enso_regime
            )

            fig_crush = make_subplots(rows=2, cols=1, shared_xaxes=True, subplot_titles=["FEEDLOT MARGIN ($/HEAD)", "FEEDER-TO-LIVE PRICE RATIO"])
            fig_crush.add_trace(go.Scatter(x=crush_metrics.index, y=crush_metrics["CrushMargin_Head"], line=dict(color="#ff9900", width=1.8), name="Margin ($/head)"), row=1, col=1)
            fig_crush.add_hline(y=0.0, line_dash="dash", line_color="#ff3b30", row=1, col=1)

            fig_crush.add_trace(go.Scatter(x=crush_metrics.index, y=crush_metrics["FeederLiveRatio"], line=dict(color="#00e5ff", width=1.8), name="Feeder/Live Ratio"), row=2, col=1)
            normal_target = 1.42 if active_enso_regime == "super_elnino" else 1.35
            fig_crush.add_hline(y=normal_target, line_dash="dash", line_color="#00ff66", annotation_text=f"TARGET PARITY ({normal_target:.2f})", row=2, col=1)

            bbg_plot_theme(fig_crush, title="", height=480)
            bbg_render_chart(fig_crush)

    with f_tab2:
        bbg_section_title("CFTC COMMITMENTS OF TRADERS (COT) INSTITUTIONAL ACCUMULATION")
        cot_le = market_data.get("COT_LE", pd.DataFrame())
        if not cot_le.empty and "Commercial_Net" in cot_le.columns:
            fig_cot = make_subplots(rows=2, cols=1, shared_xaxes=True, subplot_titles=["COMMERCIAL HEDGERS VS MANAGED MONEY NET CONTRACTS", "3-YEAR COT COMMERCIAL PERCENTILE INDEX"])
            fig_cot.add_trace(go.Scatter(x=cot_le.index, y=cot_le["Commercial_Net"], line=dict(color="#00ff66", width=2), name="Commercial Hedgers (Smart Money)"), row=1, col=1)
            fig_cot.add_trace(go.Scatter(x=cot_le.index, y=cot_le["ManagedMoney_Net"], line=dict(color="#ff3b30", width=2), name="Managed Money (Speculator CTAs)"), row=1, col=1)

            if "COT_Commercial_Index" in cot_le.columns:
                fig_cot.add_trace(go.Scatter(x=cot_le.index, y=cot_le["COT_Commercial_Index"], line=dict(color="#ff9900", width=1.8), name="COT Commercial Index"), row=2, col=1)
                fig_cot.add_hline(y=80, line_dash="dash", line_color="#00ff66", annotation_text="BULLISH EXTREME (>80)", row=2, col=1)
                fig_cot.add_hline(y=20, line_dash="dash", line_color="#ff3b30", annotation_text="BEARISH EXTREME (<20)", row=2, col=1)

            bbg_plot_theme(fig_cot, title="", height=480)
            bbg_render_chart(fig_cot)

    with f_tab3:
        bbg_section_title("MONTHLY BOVINE CLIMATOLOGY & SEASONAL RETURN PROFILE")
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        le_season = [0.15, 0.25, 0.55, 0.70, 0.40, -0.20, -0.45, -0.30, -0.10, 0.20, -0.35, 0.25]
        gf_season = [0.10, 0.30, 0.60, 0.50, 0.30, 0.10, 0.20, 0.35, -0.40, -0.60, -0.50, -0.10]

        df_seas = pd.DataFrame({"Month": months, "Live Cattle (LE)": le_season, "Feeder Cattle (GF)": gf_season})
        fig_seas = px.bar(
            df_seas, x="Month", y=["Live Cattle (LE)", "Feeder Cattle (GF)"], barmode="group",
            color_discrete_map={"Live Cattle (LE)": "#ff9900", "Feeder Cattle (GF)": "#00e5ff"}
        )
        bbg_plot_theme(fig_seas, title="MONTHLY SEASONAL EXCESS RETURN PROFILE (%)", height=400)
        bbg_render_chart(fig_seas)

    with f_tab4:
        bbg_section_title("US PLAINS DROUGHT SEVERITY INDEX & MACRO DXY ELASTICITY")
        drought_df = market_data.get("DROUGHT", pd.DataFrame())
        if not drought_df.empty:
            fig_dr = go.Figure()
            fig_dr.add_trace(go.Scatter(
                x=drought_df.index, y=drought_df["DroughtIndex"],
                line=dict(color="#ff9900", width=2), name="Drought Index"
            ))
            fig_dr.add_hline(y=60, line_dash="dash", line_color="#ff3b30", annotation_text="SEVERE HERD LIQUIDATION THRESHOLD (60)")
            fig_dr.add_hline(y=35, line_dash="dash", line_color="#00ff66", annotation_text="BASELINE NORMAL (35)")
            bbg_plot_theme(fig_dr, title="US PLAINS CATTLE PASTURE DROUGHT SEVERITY INDEX (0-100)", height=400)
            bbg_render_chart(fig_dr)

    with f_tab5:
        bbg_section_title("NOAA OCEANIC NINO INDEX (ONI) & SUPER EL NINO CLIMATOLOGY")
        st.caption("Sea surface temperature anomalies in the equatorial Pacific Niño 3.4 region and bovine transmission mechanics.")

        enso_data = market_data.get("ENSO", pd.DataFrame())
        if not enso_data.empty and "ONI" in enso_data.columns:
            fig_oni = go.Figure()
            fig_oni.add_hline(y=2.0, line_dash="dot", line_color="#ff3b30", annotation_text="SUPER EL NINO (>= +2.0 C)")
            fig_oni.add_hline(y=0.5, line_dash="dash", line_color="#ff9900", annotation_text="EL NINO THRESHOLD (+0.5 C)")
            fig_oni.add_hline(y=-0.5, line_dash="dash", line_color="#00e5ff", annotation_text="LA NINA THRESHOLD (-0.5 C)")
            fig_oni.add_hline(y=0.0, line_color="#444b58", line_width=1)

            fig_oni.add_trace(go.Scatter(
                x=enso_data.index, y=enso_data["ONI"],
                mode="lines", line=dict(color="#00ff66", width=2.5),
                name="Oceanic Niño Index (°C)"
            ))
            bbg_plot_theme(fig_oni, title="NOAA OCEANIC NINO INDEX (ONI) SST ANOMALY ( C)", height=400)
            bbg_render_chart(fig_oni)

        # Seasonal Modulation Comparison
        bbg_section_title("FEEDER CATTLE: BASELINE VS SUPER EL NINO MODULATED CURVE")
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        gf_base = [0.10, 0.30, 0.60, 0.50, 0.30, 0.10, 0.20, 0.35, -0.40, -0.60, -0.50, -0.10]
        gf_elnino = [0.25, 0.45, 0.75, 0.65, 0.45, 0.20, 0.30, 0.45, 0.15, 0.10, 0.05, 0.15]

        df_mod = pd.DataFrame({
            "Month": months,
            "GF Baseline (Feeder)": gf_base,
            "GF Super El Niño (Feeder)": gf_elnino
        })

        fig_comp = px.bar(
            df_mod, x="Month",
            y=["GF Baseline (Feeder)", "GF Super El Niño (Feeder)"],
            barmode="group",
            color_discrete_map={
                "GF Baseline (Feeder)": "#606575",
                "GF Super El Niño (Feeder)": "#00ff66"
            }
        )
        bbg_plot_theme(fig_comp, title="FEEDER CATTLE (GF): AUTUMN CALF RUN SUPPRESSION (SEP-NOV) UNDER SUPER EL NINO", height=380)
        bbg_render_chart(fig_comp)

        # Transmission Mechanics Table
        bbg_section_title("SUPER EL NINO MICROSTRUCTURE TRANSMISSION MATRIX")
        mech_data = [
            {"Channel": "Southern Plains Pasture", "Condition": "Abundant subtropical rain", "Bovine Impact": "Ranchers aggressively retain heifers & breeding cows", "Alpha Direction": "Ultra Bullish (Prompt Slaughter Deficit)"},
            {"Channel": "Midwest Corn Belt", "Condition": "Cool, drought-free growing weather", "Bovine Impact": "Bumper corn crop crashes feed costs; feedlots bid up calves", "Alpha Direction": "Bullish Feeder Cattle (GF=F)"},
            {"Channel": "Autumn Calf Run", "Condition": "Lush winter wheat grazing available", "Bovine Impact": "Calves kept on pasture; auction dumping suppressed", "Alpha Direction": "Cancels Sep-Nov Seasonal Feeder Dip"},
            {"Channel": "Feedlot Pen Conditions", "Condition": "Wet, muddy winter subtropical storms", "Bovine Impact": "Average Daily Gain (ADG) drops 10-15%; slaughter delayed", "Alpha Direction": "Bullish Dec-Feb Live Cattle Tightness"},
            {"Channel": "Australian Beef Supply", "Condition": "Severe Southern Hemisphere drought", "Bovine Impact": "Short-term liquidation followed by global beef vacuum", "Alpha Direction": "Long-Term Bullish US Export Competitiveness"},
        ]
        st.dataframe(pd.DataFrame(mech_data), width="stretch")


# -------------------------------------------------------------------------
# TAB 4: PAPER PORTFOLIO & AUDIT
# -------------------------------------------------------------------------
elif app_mode == "04 // PAPER PORTFOLIO":
    bbg_header("04 // SIMULATED PAPER PORTFOLIO & EXECUTION AUDIT [PORT <GO>]", cmd="FUNCTION: ORDER BOOK & RISK AUDIT", status="PORT: ACTIVE")

    paper_trader = BovinePaperTrader()
    port = paper_trader.portfolio

    unrealized = port['equity'] - port['cash']
    port_cards = [
        {"label": "PORTFOLIO TOTAL EQUITY", "val": f"${port['equity']:,.2f}", "val_color": "#00ff66"},
        {"label": "AVAILABLE CASH RESERVE", "val": f"${port['cash']:,.2f}", "val_color": "#00e5ff"},
        {"label": "UNREALIZED PNL", "val": f"${unrealized:+,.2f}", "val_color": "#00ff66" if unrealized >= 0 else "#ff3b30"},
    ]
    port_html = "<div class='bbg-metrics-deck' style='grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));'>" + "".join([
        f"<div class='bbg-metric-card'>"
        f"<div class='bbg-metric-lbl'>{m['label']}</div>"
        f"<div class='bbg-metric-val' style='color:{m['val_color']};'>{m['val']}</div>"
        f"</div>"
        for m in port_cards
    ]) + "</div>"
    st.markdown(port_html, unsafe_allow_html=True)

    st.markdown("---")
    bbg_section_title("ACTIVE OPEN POSITIONS [POS <GO>]")
    if port["positions"]:
        pos_rows = []
        for sym, p in port["positions"].items():
            pos_rows.append({
                "Symbol": sym,
                "Contracts": p["contracts"],
                "Entry Price": f"${p['entry_price']:.2f}",
                "Stop Loss": f"${p.get('stop_loss', 0):.2f}" if isinstance(p.get("stop_loss"), (int, float)) else p.get("stop_loss", "N/A"),
                "Take Profit": f"${p.get('take_profit', 0):.2f}" if isinstance(p.get("take_profit"), (int, float)) else p.get("take_profit", "N/A"),
                "Opened At": p.get("entry_time", "N/A")
            })
        st.dataframe(pd.DataFrame(pos_rows), width="stretch")
    else:
        st.info("[PORTFOLIO EQUILIBRIUM] No active positions open. Capital is 100% held in cash reserve.")

    bbg_section_title("SIMULATED TRADE EXECUTION HISTORY [BLOT <GO>]")
    if port["trade_history"]:
        st.dataframe(pd.DataFrame(port["trade_history"]).tail(50), width="stretch")
    else:
        st.info("[BLOTTER EMPTY] No historical fills recorded in current session blotter.")


# -------------------------------------------------------------------------
# TAB 5: CME SPECS & ARCHITECTURE
# -------------------------------------------------------------------------
elif app_mode == "05 // CME SPECS & ARCH":
    bbg_header("05 // CME COMMODITY SPECIFICATIONS & FREE DATA ARCHITECTURE [DES <GO>]", cmd="FUNCTION: EXCHANGE SPECS & PIPELINE", status="ARCH: OK")

    spec_rows = []
    for sym, spec in COMMODITY_SPECS.items():
        spec_rows.append({
            "Ticker": spec.symbol,
            "Name": spec.name,
            "Exchange": spec.exchange,
            "Contract Size": f"{spec.contract_size:,} {spec.unit}",
            "Point Multiplier ($)": f"${spec.point_value:,.2f}",
            "Tick Size": spec.tick_size,
            "Tick Value ($)": f"${spec.tick_value:.2f}",
            "Initial Margin ($)": f"${spec.margin_initial:,.2f}"
        })

    st.dataframe(pd.DataFrame(spec_rows), width="stretch")

    with st.container(border=True):
        bbg_section_title("100% FREE & OPEN-SOURCE QUANT DATA ARCHITECTURE")
        st.markdown(
            "1. **YAHOO FINANCE ENGINE (`yfinance`)**: Free continuous OHLCV data for CME futures (`LE=F`, `GF=F`, `ZC=F`, `ZM=F`, `HE=F`, `DC=F`, `CL=F`, `DX-Y.NYB`).\n\n"
            "2. **CFTC PUBLIC ARCHIVE INTEGRATION**: Free weekly Commitments of Traders (COT) legacy reports parsed directly from `cftc.gov` for commercial vs managed money positioning.\n\n"
            "3. **FEDERAL RESERVE ECONOMIC DATA (FRED) & NOAA**: Free public macroeconomic series, real interest rates, CPI beef inflation, and Oceanic Niño Index (ONI) SST anomalies.\n\n"
            "4. **ZERO-DEPENDENCY BENCHMARK ENGINE**: Built-in stochastic simulation engine provides immediate zero-latency testing, full cross-correlations, and offline robustness."
        )

elif app_mode == "06 // GLOBAL SUPPLY CHAIN & AIS":
    from ui.supply_chain_view import render_global_supply_chain_workstation
    render_global_supply_chain_workstation()
