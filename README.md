# PROJECT MOO // BLOOMBERG BOVINE QUANT DESK
### Institutional Multi-Factor Quantitative Trading System for Cattle Markets
**100% Free & Open-Source Commodity Quantitative Platform**

---

## 1. Executive Overview

**Project MOO (ALPHA-BOVINE)** is an institutional-grade, multi-factor algorithmic trading and risk platform engineered specifically for bovine livestock commodities. The platform models the physical and financial microeconomics of the North American beef supply chain—from cow-calf breeding herds and stocker backgrounding to feedlot conversion margins, packer slaughter dynamics, and wholesale distribution—without requiring paid API licenses or terminal subscriptions.

```
                    +-------------------------------------------------------------+
                    |                   100% FREE DATA PIPELINE                   |
                    |  * Yahoo Finance Continuous Futures (LE=F, GF=F, ZC=F,      |
                    |    ZM=F, HE=F, DC=F, CL=F, DX-Y.NYB)                        |
                    |  * CFTC Commitments of Traders (COT Public Archives)        |
                    |  * FRED Macroeconomic Series (Beef CPI, Real Yields, DXY)   |
                    |  * US Drought Monitor (Plains Pasture Severity Index)       |
                    |  * NOAA CPC ONI (Equatorial Pacific SST Anomaly Archives)   |
                    +------------------------------+------------------------------+
                                                   |
                                                   v
                    +-------------------------------------------------------------+
                    |                  MULTI-FACTOR ALPHA ENGINE                  |
                    |  [1] Cattle Crush & Feedlot Economics (Margin $/head & cwt) |
                    |  [2] CFTC COT Smart Money Sentiment (Commercial Index)      |
                    |  [3] Biological Bovine Seasonality & Grilling Cycles        |
                    |  [4] US Drought Severity, ENSO Climatology & DXY Elasticity |
                    |  [5] Kalman Filter Adaptive Trend & ATR Breakouts           |
                    |  [6] Walk-Forward Ensemble Machine Learning Alpha           |
                    +------------------------------+------------------------------+
                                                   |
                                                   v
                    +-------------------------------------------------------------+
                    |            INSTITUTIONAL RISK & EXECUTION ENGINE            |
                    |  * Volatility-Targeted Position Sizing (15% Target Vol)     |
                    |  * CME Contract Multipliers ($400/pt Live, $500/pt Feeder)  |
                    |  * Dynamic ATR Stop Loss & Chandelier Trailing Take Profit  |
                    |  * Climatology Buffers (2.8x ATR in Super El Nino Regimes)  |
                    |  * Portfolio Drawdown Circuit Breakers (Soft: 8%, Hard: 15%)|
                    +------------------------------+------------------------------+
                                                   |
                                                   v
                    +-------------------------------------------------------------+
                    |                INTERFACES & EXECUTION MODES                 |
                    |  * Bloomberg Terminal Web Cockpit (6 Workstations)          |
                    |    - 01 // LIVE COCKPIT (8-Asset Quotes & Streaming Wire)   |
                    |    - 02 // STRATEGY BACKTESTER (Directional & Spread)       |
                    |    - 03 // FACTOR RESEARCH (Crush, COT, Seasonality, ENSO)  |
                    |    - 04 // PAPER PORTFOLIO (Accounting & Position Brackets) |
                    |    - 05 // CME SPECS & FREE DATA ARCHITECTURE               |
                    |    - 06 // GLOBAL SUPPLY CHAIN, AIS FLEET & INDUSTRY COSTS  |
                    |  * Automated CLI Scanner & Event-Driven Backtester          |
                    |  * Persistent Simulated Paper Trading & Audit Journal       |
                    +-------------------------------------------------------------+
```

---

## 2. Core Quantitative Factors

### 1. Cattle Crush Spread & Feedlot Economics Margin Factor
Models the transformation economics of the commercial feeding sector:
$$\text{Gross Feedlot Margin } (\$/\text{head}) = 13.0 \times P_{\text{Live}} - \left(7.5 \times P_{\text{Feeder}} + 50.0 \times \frac{P_{\text{Corn}}}{100}\right) - \$85.00\text{ Yardage}$$
* **Negative Margin Z-Score ($Z < -1.5$):** Feedlots incur acute operational losses -> cut back calf placements -> induces a medium-term slaughter deficit -> **Bullish Live Cattle / Bearish Feeder Cattle**.
* **Elevated Margin Z-Score ($Z > +1.5$):** Feedlot windfall margins trigger aggressive placements -> future fed supply surplus -> **Bearish Live Cattle**.
* **Feeder-to-Live Price Ratio ($P_{\text{Feeder}} / P_{\text{Live}}$):** Statistical arbitrage spread trading centered at the $1.35$ equilibrium parity (shifts to $1.42$ under Super El Nino regimes).

### 2. CFTC Commitments of Traders (COT) Smart Money Factor
* **Commercial Hedgers (Smart Money):** Cattle ranchers, feedlot operators, and meat packers. Evaluated using a 3-year rolling percentile index:
  $$\text{COT Index}_t = \frac{\text{CommNet}_t - \min_{756}(\text{CommNet})}{\max_{756}(\text{CommNet}) - \min_{756}(\text{CommNet})} \times 100$$
  * $\text{COT Index} > 80$: Commercial accumulation -> cyclical bottom signal.
  * $\text{COT Index} < 20$: Commercial distribution / Speculator bubble -> exhaustion top warning.
* **Managed Money Crowding:** Measures one-sided CTA and trend-following speculator crowding susceptible to liquidity cascades.

### 3. Biological Seasonality & Climatology Factor
* **Spring Grilling Season (March-May):** Peak packer procurement ahead of Memorial Day and Fourth of July wholesale retail demand (+0.70 normalized score).
* **Autumn Calf Run (September-November):** Spring-born calves are weaned off pasture and auctioned into feedlots, producing a seasonal supply flush in feeder cattle (-0.60 score in normal years; suppressed to $+0.15$ during Super El Nino).
* **Winter Storm Lag (December-February):** Subtropical blizzards and feedlot mud decrease Average Daily Gain (ADG), causing slaughter delays and prompt tightness (+0.25 score; amplified under El Nino).

### 4. US Drought Severity, ENSO Climatology & Macro Factor
* **Oceanic Nino Index (ONI):** Measures equatorial Pacific Sea Surface Temperature (SST) anomalies in the Nino 3.4 region:
  * $\text{ONI} \ge +2.0^\circ\text{C}$ (Super El Nino): Southern Plains pasture hydration induces aggressive heifer retention, creating an acute prompt slaughter shortage ($\text{Alpha: } +0.35$).
  * $\text{ONI} \le -0.5^\circ\text{C}$ (La Nina): Severe plains drought forces distress cow herd liquidation.
* **Plains Pasture Drought Severity:** 180-day rolling NDMC pasture stress index relative to the 35.0 baseline.
* **US Dollar Index (DXY) Elasticity:** Dollar weakness expands purchasing power for US beef exports across Asian and Latin American markets.
* **Protein Substitution Ratio:** Models mean-reverting equilibrium between Live Cattle and Lean Hogs ($P_{\text{LE}} / P_{\text{HE}}$).

### 5. Quantitative Technical & Trend Momentum
* **1D Adaptive Kalman Filter:** Zero-lag linear state estimation filter tracking underlying trend velocity without phase distortion.
* **Donchian 20-Day Channels & ATR Volatility Breakout:** Captures institutional breakout momentum.
* **Garman-Klass Volatility Estimator:** Extreme-value OHLC variance metric offering ~8x statistical efficiency over standard close-to-close estimators for dynamic risk scaling.

### 6. Walk-Forward Ensemble Machine Learning Alpha
* **Ensemble Architecture:** Histogram Gradient Boosted Classifiers combined with Random Forests and pure-NumPy regularized Ridge probability fallback estimators.
* **Strict Walk-Forward Cross-Validation:** Expanding window retraining with a 5-day forward embargo buffer to eliminate data leakage and lookahead contamination.

---

## 3. Super El Nino Climatology Compensation Engine

An intense ENSO warm phase (Super El Nino, $\text{ONI} \ge +2.0^\circ\text{C}$) fundamentally alters livestock microeconomics:

```
                  +-------------------------------------------------------------+
                  |              ACTIVE SUPER EL NINO REGIME (+2.30 C)          |
                  +------------------------------+------------------------------+
                                                 |
         +-----------------------+---------------+-----------------------+
         |                       |                                       |
         v                       v                                       v
[ Southern Plains Moisture ] [ Midwest Corn Bumper Crop ] [ Subtropical Mud & Storms ]
  * Breaks multi-year drought   * Low feed grain costs (ZC=F)   * Winter feedlot mud drag
  * Lush winter wheat pasture   * Expands Feedlot Margins       * Cuts Daily Gain (ADG) -12%
  * Ranchers retain heifers     * Feedlots bid up calves        * Delays slaughter delivery
         |                       |                                       |
         v                       v                                       v
[ Structural Beef Deficit ]  [ Feeder Parity Expands ]      [ Winter Prompt Tightness ]
  * Acute slaughter shortfall  * Parity target: 1.35 -> 1.42  * December-February rally
  * Multi-year secular bull    * Feeder calf price premium    * Widens ATR stop buffers
```

### Compensation Parameters
1. **Regime Factor Allocation (`SUPER_ELNINO_FACTOR_WEIGHTS`):**
   * Macro/Climatology weight increases to $0.25$, Cattle Crush increases to $0.25$, and Technical Trend weight scales down to $0.10$ to prevent trend-following whipsaws.
2. **Seasonal Curve Modulation:**
   * **Autumn Calf Run Suppression:** Abundant winter wheat grazing allows ranchers to withhold calves from auction, neutralizing the autumn feeder price dip ($GF$ seasonal bias shifts from $-0.40$ to $+0.15$).
   * **Feedlot Mud Overhead:** Adds $+\$12/\text{head}$ in yardage overhead for muddy pen conditions.
   * **Feeder/Live Parity Equilibrium:** Shifts normal parity target from $1.35$ to $1.42$.
3. **Adaptive Risk Bounds:**
   * Expands stop-loss distance from $2.5 \times \text{ATR}$ to $2.8 \times \text{ATR}$ to prevent false liquidations during weather-driven headline volatility.

---

## 4. Institutional Bloomberg Terminal Interface

The Streamlit web interface (`ui/app.py`) adheres strictly to Bloomberg Terminal design conventions:
* **Terminal Palette:** Obsidian black canvas (`#000000`), signature Bloomberg amber headers (`#ff9900`), terminal uptick green (`#00ff66`), crimson red (`#ff3b30`), cyan ratios (`#00e5ff`), and monospace typography (`Roboto Mono`).
* **Command Bar & Status Strip:** Top-level terminal emulation (`CMD> AGRI LE <GO>`), live connection status (`GLOBEX CME: LIVE`), UTC timestamps, and quick function keys (`[F1: HELP]`, `[F2: BQ]`, `[F3: CRUSH]`, `[F4: REGIME]`, `[F5: BTST]`, `[F8: REBAL]`).

### Home Cockpit Charts & Telemetry (`01 // LIVE COCKPIT`)
1. **Direct Terminal Keys & Status Bar**:
   * Direct shortcut navigation keys: `[F1: HELP]`, `[F2: BQ]`, `[F3: CRUSH]`, `[F4: CORR]`, `[F5: RADAR]`, `[F6: VOL]`, `[F7: COT]`, `[F8: REBAL]`, `[F9: DOM]`, `[F10: COF]`, `[F11: CUTOUT]`, `[F12: VaR]`.
   * Real-time network telemetry: Globex feed latency (1.2ms), CME ClearPort sync status, and automated risk circuit breaker status.
2. **Global Multi-Commodity Quote Board (`BQ <GO>`)**:
   * Real-time quotes across the 8-asset commodity universe: Live Cattle (`LE=F`), Feeder Cattle (`GF=F`), Corn (`ZC=F`), Soybean Meal (`ZM=F`), Lean Hogs (`HE=F`), Class III Milk (`DC=F`), WTI Crude (`CL=F`), and the US Dollar Index (`DX-Y.NYB`).
   * Displays Last Settlement, Net Change, % Change, Synthetic Bid, Ask, Spread, High, Low, 14-Day ATR, Annualized Volatility (GK), RSI(14), and Session Volume.
3. **Macro Climatology & USDA Fundamental Telemetry Strip (`AGRI DES <GO>`)**:
   * 8 KPI cards: ENSO ONI 3.4 SST Anomaly (`+2.30 C`), Plains Drought Index (`48.2`), USDA Feedlot Placements (`-4.2% YoY`), U.S. Beef Cow Inventory (`28.2M Head`), Boxed Beef Choice Cutout (`$314.50`), Choice/Select Spread (`$24.20`), Packer Gross Margin (`+$118.50/head`), and DXY Index (`103.45`).
4. **Multi-Horizon Technical Trend Matrix (`TREND <GO>`)**:
   * Multi-timeframe trend decomposition across 6 distinct horizons: 15-Minute, 1-Hour, 4-Hour, Daily, Weekly, and Monthly.
   * Details Regime Bias, Kalman Trend Slope, EMA 20/50 Spread, Donchian Channel Position, RSI(14), and Volatility Regime.
5. **Chart 1 — Primary Technical Terminal (`GP <GO>`)**:
   * 4 subplots: OHLC Candlesticks + 1D Adaptive Kalman Filter + 20/50 EMAs + Bollinger Bands + Dynamic Stops / Take Profit, Session Volume + 20 SMA, RSI(14), and MACD Histogram.
6. **Chart 2 — Cattle Crush Margin Spread Monitor (`CRUSH <GO>`)**:
   * 180-day feedlot margin ($/head) with 30-day moving average and Feeder-to-Live price ratio against regime parity line (1.35 neutral, 1.42 Super El Nino).
7. **Chart 3 — Cross-Commodity Rolling Correlation Heatmap (`CORR <GO>`)**:
   * 60-day rolling correlation matrix across cattle, feed grains, substitute proteins, energy, and currency.
8. **Chart 4 — Multi-Factor Institutional Polar Radar (`ANR <GO>`)**:
   * Radar chart comparing Live Cattle (LE) and Feeder Cattle (GF) across all 6 quantitative alpha engines on a $[-1.0, +1.0]$ standardized scale.
9. **Chart 5 — Forward Term Structure Curve (`FWD <GO>`)**:
   * Futures curve across prompt Cash and 6 consecutive contract months (LEQ, LEV, LEZ, LEG, LEJ, LEM) displaying backwardation prompt shortage premiums.
10. **Chart 6 — Realized Volatility Term-Structure Cone (`VOL <GO>`)**:
    * Annualized Garman-Klass volatility term structure across 5D, 10D, 20D, 30D, 60D, 90D, and 180D rolling windows.
11. **Chart 7 — USDA Cattle on Feed Monthly Telemetry (`COF <GO>`)**:
    * Monthly Placements vs Marketings (1,000 head) dual-bar chart and total on-feed inventory % YoY trend line.
12. **Chart 8 — Boxed Beef Wholesale Cutout & Quality Spread (`PACK <GO>`)**:
    * Wholesale Choice cutout, Select cutout, and Choice/Select grade premium spread with prime quality thresholds.
13. **Chart 9 — CFTC Commitments of Traders (`COT <GO>`)**:
    * Commercial hedgers vs managed money net contracts and 3-year commercial percentile index with accumulation/distribution triggers.
14. **Chart 10 — Inter-Commodity Protein Substitution Ratio (`SPRD <GO>`)**:
    * Live Cattle to Lean Hogs relative price ratio ($P_{\text{LE}} / P_{\text{HE}}$) with 60-day moving average and $\pm 2.0\sigma$ statistical arbitrage bands.
15. **Chart 11 — CME Globex Depth of Market Ladder (`MD <GO>`)**:
    * Synthetic Level 2 order book showing bid/ask contract queue distribution across 8 depth levels.
16. **Chart 12 — Value at Risk Distribution & Macro Stress Scenarios (`STRESS <GO>`)**:
    * Return distribution histogram with fitted density, VaR 95%, VaR 99%, and stress test scenarios (Blizzard Mud Drag -3.2%, Feed Grain Spike -4.1%, Heifer Retention Squeeze +3.8%).
17. **Institutional Risk, Margin & Value-at-Risk Telemetry Table (`MARG <GO>`)**:
    * Value at Risk, Expected Shortfall (CVaR), Maximum Drawdown, Gross Leverage, CME Initial Margin, and Capital Cushion Ratio.
18. **Mathematical Factor Attribution & Decomposition Matrix (`ANR <GO>`)**:
    * Normalized factor scores, weights, bps contributions, and directional regime bias.
19. **Institutional Order Execution, Active Blotter & Live News Wire**:
    * **OMON <GO>**: Execution dispatch ticket with slippage and clearing fee estimates.
    * **BLOT <GO>**: Active order queue and fill ledger tracking execution history and venue.
    * **NEWS <GO>**: Real-time timestamped bovine and macroeconomic news wire.

### Additional Dedicated Workstations
* **`02 // STRATEGY BACKTESTER` (`BTST <GO>`)**:
  Interactive event-driven futures backtesting engine. Configure asset, strategy mode (Directional Multi-Factor vs Feeder/Live Spread Trading), date range, capital, volatility targeting, ATR stops, and ML walk-forward loop. Visualizes equity curve vs Buy & Hold benchmark, underwater drawdown profile, 14 institutional tear-sheet metrics, compounded monthly returns heatmap matrix, and complete trade audit ledger.
* **`03 // FACTOR RESEARCH` (`ANR <GO>`)**:
  Five deep-dive quantitative research panes:
  1. `[01] CATTLE CRUSH SPREAD`: Feedlot gross margin ($/head) with zero-line boundary and Feeder-to-Live price ratio against regime parity (1.35 neutral, 1.42 Super El Niño).
  2. `[02] CFTC COT POSITIONING`: Commercial hedgers vs managed money net contracts and 3-year commercial percentile index with 80/20 extreme bounds.
  3. `[03] BIOLOGICAL SEASONALITY`: Monthly excess return profile (%) across all 12 calendar months for Live Cattle and Feeder Cattle.
  4. `[04] DROUGHT & MACRO DXY`: US Plains Cattle Pasture Drought Severity Index (0–100) with severe herd liquidation threshold (60) and baseline normal (35).
  5. `[05] ENSO ONI CLIMATOLOGY`: NOAA ONI SST Anomaly historical curve, Feeder Cattle autumn calf run comparison (baseline vs Super El Niño damped curve), and the 5-channel Super El Niño transmission matrix.
* **`04 // PAPER PORTFOLIO` (`PORT <GO>`)**:
  Persistent simulated portfolio accounting engine. Tracks live equity, cash balance, open position count, unrealized PnL, realized PnL, and ROI. Includes an active position blotter (`POS <GO>`) with live stop-loss/take-profit brackets and complete simulated trade execution history (`BLOT <GO>`).
* **`05 // CME SPECS & ARCH` (`DES <GO>`)**:
  Exchange contract specifications matrix across all 8 supported instruments (contract sizes, units, point values, tick sizes, tick values, and initial margin requirements), along with full documentation of the 100% free open-source data pipeline with local caching and deterministic synthetic fallback.

---

## 5. Quickstart Guide

### 1. Installation
The entire platform relies solely on open-source packages:
```bash
pip install -r requirements.txt
```

### 2. Live Alpha Scan (CLI)
Scan real-time market data and calculate volatility-targeted position sizing:
```bash
# Scan with Super El Nino climatology compensation (Default)
python main.py --mode scan --enso super_elnino

# Scan under neutral climatology
python main.py --mode scan --enso neutral
```

### 3. Historical Backtest
Execute multi-factor backtests with point multipliers, tick slippage, and ATR trailing stops:
```bash
# Directional Multi-Factor Strategy on Live Cattle
python main.py --mode backtest --symbol LE=F --start-date 2018-01-01 --enso super_elnino

# Feeder vs Live Statistical Arbitrage Spread Trading
python main.py --mode backtest --symbol LE=F --strategy spread_trading --enso super_elnino

# Fast backtest disabling ML walk-forward loop
python main.py --mode backtest --symbol LE=F --no-ml
```

### 4. Bloomberg Terminal Web Dashboard
Launch the Streamlit quantitative workstation:
```bash
python main.py --mode dashboard
# or
streamlit run ui/app.py
```
Open your browser at `http://localhost:8501`.

#### The 6 Institutional Workstations:
1. **`01 // LIVE COCKPIT`**: Real-time trading desk featuring 8-asset quote board (`BQ`), ENSO telemetry (`AGRI DES`), multi-horizon trend matrix, 12 Plotly charts, margin telemetry (`MARG`), order blotter, and streaming agribusiness news wire.
2. **`02 // STRATEGY BACKTESTER`**: Directional multi-factor & feeder/live cattle spread backtesting (`BTST`), equity curves vs benchmark, underwater drawdowns, and 14 tear-sheet metrics.
3. **`03 // FACTOR RESEARCH`**: Five dedicated research panes (`ANR`) covering cattle crush margins, CFTC COT positioning, biological seasonality, US Plains drought, and NOAA ONI climatology.
4. **`04 // PAPER PORTFOLIO`**: Simulated portfolio accounting (`PORT`) and open position brackets (`POS`).
5. **`05 // CME SPECS & ARCH`**: Contract specifications matrix (`DES`) and 100% free data pipeline architecture.
6. **`06 // GLOBAL SUPPLY CHAIN & AIS`**: Global physical bovine intelligence, maritime tracking, and industry economics desk (`SUPP <GO>`):
   - **`01 // BREED & HERD GEOGRAPHY [GEOG]`**: World map of cattle herds, breed taxonomy (Angus, Nelore, Wagyu, Brahman, Carabeef, Charolais, Holstein), and pasture vs feedlot ratios.
   - **`02 // SUPPLY & DEMAND MATRIX [SND]`**: Surplus vs deficit heatmaps, national herd cycle phase (-100 to +100), pasture drought stress, and biosecurity alerts (FMD, BSE, screwworm).
   - **`03 // TRADE CORRIDORS & SANKEY [FLOW]`**: 3-tier interactive Sankey diagram (Origin $\to$ Commodity $\to$ Destination), bilateral trade matrices, and transport logistics breakdown.
   - **`04 // MARITIME AIS FLEET TRACKER [SHIP]`**: Real-time interactive AIS world map tracking 15 flagship livestock carrier vessels, choke point alerts (Suez, Bab-el-Mandeb, Malacca, Gibraltar), and onboard animal welfare telemetry (fodder days, water desalination, ventilation ACH, heat stress THI).
   - **`05 // INDUSTRY COST WATERFALL [COST]`**: Interactive modelers for marine mortality insurance (1.4%–3.8% with war-risk and heat-stress multipliers), feedlot cost-of-gain ($/lb), meat packer processing margins, 40ft reefer container freight, and end-to-end calf-to-retail supply chain cost waterfalls.
   - **`06 // GLOBAL BOVINE NEWS WIRE [NEWS]`**: Real-time agribusiness wire with sentiment classification, market impact badges (**HIGH** / **MED** / **LOW**), category filters, and live RSS headline streaming.

#### Universal Multi-Display & Mobile Responsive Engine:
The web workstation is built with a custom CSS Grid and fluid typography engine guaranteeing an optimal institutional display across all device types:
- **4K / Ultrawide Monitors ($\ge 1920\text{px}$ up to $3840\text{px}+$):** Centered `max-width: 2200px` layout prevents charts from stretching into flat ribbons while preserving multi-column immersion.
- **Laptops & Standard Desktops ($992\text{px} - 1440\text{px}$):** Multi-column quote board, USDA telemetry strip (`AGRI DES <GO>`), and side-by-side Plotly charts with auto-scaling fonts.
- **Tablets & iPads ($768\text{px} - 1080\text{px}$):** Side-by-side charts and 3-column trade desk widgets automatically stack to **100% full width**, providing full detail for candlesticks and subplots.
- **Mobile Phones (< 768px, iPhone / Galaxy / Pixel):** Mobile-optimized padding (`0.5rem` vs default `5rem`) recovers over 140px of screen width; telemetry strip reflows into a 2×4 touch card grid; target metrics reflow into a 2×3 grid; buttons stretch with 38px+ touch targets; tables support touch inertia scrolling.

*For detailed startup, shutdown, background running, mobile LAN access, and troubleshooting commands across Windows, Linux, and macOS, see [`DASHBOARD_COMMANDS.md`](DASHBOARD_COMMANDS.md).*

### 5. 100% Free Cloud Hosting (Streamlit Community Cloud)
Project MOO is configured for permanent free cloud deployment without credit cards or trial limitations:
1. Push this repository to GitHub:
   ```bash
   git remote add origin https://github.com/<your-username>/moo.git
   git push -u origin main
   ```
2. Connect to [share.streamlit.io](https://share.streamlit.io) via GitHub.
3. Select repository `<your-username>/moo`, branch `main`, and main file `ui/app.py`.
4. Click **Deploy!** Continuous live market quotes, 5-minute cache TTL, and Bloomberg dark terminal styling are pre-configured.

### 6. Simulated Paper Trading Rebalance
Generate and dispatch simulated portfolio rebalance orders:
```bash
python main.py --mode rebalance --enso super_elnino
```

### 7. Train Walk-Forward ML Alpha Model
Train the ensemble ML model (Gradient Boosted Trees + Random Forest + pure-NumPy regularized Ridge fallback) and output factor importances:
```bash
python main.py --mode train-ml --symbol LE=F
```

### 8. Run Comprehensive Test Suite
Execute the unit and integration test suite across data loading, factors, ML, risk manager, backtester, and paper trader:
```bash
python -m unittest tests/test_all.py
```

---

## 6. Repository Architecture

```
moo/
├── .streamlit/
│   └── config.toml               # Bloomberg Terminal dark theme & headless server settings
├── .gitignore                    # Python cache, virtual env & OS ignore rules
├── config.py                     # CME specs, global country profiles, vessel fleet & cost benchmarks
├── main.py                       # CLI orchestrator and command dispatcher
├── requirements.txt              # 100% free open-source dependencies (incl. pyarrow)
├── README.md                     # System overview and quickstart guide
├── CONTEXT.md                    # Complete technical context, math, and domain manual
├── DASHBOARD_COMMANDS.md         # Terminal dashboard lifecycle and execution control guide
├── data_cache/                   # Local parquet/pickle cache and simulated portfolio state
│   ├── paper_portfolio.json      # Persistent simulated portfolio ledger
│   └── *.parquet, *.pkl          # Cached price, COT, drought, and ONI series
├── data/
│   ├── __init__.py
│   ├── data_loader.py            # Unified market data loader (live Yahoo Finance + parquet fallback)
│   ├── cot_fetcher.py            # Free CFTC Commitments of Traders downloader & parser
│   ├── macro_fetcher.py          # Free FRED Macro, US Drought Monitor & NOAA ONI loader
│   ├── mock_generator.py         # High-fidelity synthetic 8-asset market generator
│   ├── global_production.py      # [NEW] Country-level cattle census, breed taxonomy & carcass yields
│   ├── supply_demand.py          # [NEW] S&D balances, herd phase scores & biosecurity alerts
│   ├── trade_flows.py            # [NEW] Bilateral trade matrices, corridors & Sankey flow engine
│   ├── maritime_ais.py           # [NEW] Real-time livestock carrier AIS tracker & welfare telemetry
│   └── news_engine.py            # [NEW] Agribusiness RSS aggregator & Bloomberg wire engine
├── factors/
│   ├── __init__.py
│   ├── crush_spread.py           # Cattle Crush gross margin & Feeder/Live parity ratio
│   ├── sentiment_cot.py          # Commercial Smart Money index & Speculator crowding
│   ├── seasonality.py            # Biological cattle calendar & empirical climatology
│   ├── macro_weather.py          # Drought severity, NOAA ONI & DXY dollar export elasticity
│   ├── technical.py              # Kalman trend filter, Donchian, RSI, Garman-Klass vol
│   ├── factor_engine.py          # Composite alpha aggregator & Information Coefficient (IC)
│   └── industry_costs.py         # [NEW] Marine insurance, livestock charter, feedlot COG & packer margins
├── models/
│   ├── __init__.py
│   ├── ml_predictor.py           # Walk-forward ensemble ML with pure-NumPy regularized fallback
│   └── strategy.py               # Directional & Spread trading signal generator
├── execution/
│   ├── __init__.py
│   ├── risk_manager.py           # Volatility targeting, ATR stops, and DD circuit breakers
│   └── paper_trader.py           # Live signal scanner & paper trading portfolio engine
├── backtest/
│   ├── __init__.py
│   ├── backtester.py             # Event-driven futures simulation with realistic point values
│   └── metrics.py                # Institutional tear-sheet metrics & monthly returns matrix
├── ui/
│   ├── __init__.py
│   ├── app.py                    # Bloomberg Terminal UI with Live CME Feeds & Responsive Engine
│   └── supply_chain_view.py      # [NEW] Workstation 06 UI (Breed map, S&D, Sankey, AIS, Costs, News)
└── tests/
    ├── __init__.py
    └── test_all.py               # Comprehensive unit & integration test suite (100% pass)
```

---

## 7. Institutional Risk Management Specifications

| Parameter | Configuration | Economic Rationale |
| :--- | :--- | :--- |
| **Target Portfolio Volatility** | $15.0\%$ Annualized | Continuous volatility-targeted position sizing |
| **Maximum Portfolio Leverage** | $2.5\times$ Equity | Caps aggregate notional exposure across all open futures contracts |
| **Maximum Position Weight** | $60.0\%$ Portfolio Equity | Restricts single-commodity concentration risk |
| **Live Cattle Multiplier (`LE=F`)** | $\$400.00$ / point ($1\text{c}/\text{lb} = \$400$) | Full 40,000 lb contract value tracking |
| **Feeder Cattle Multiplier (`GF=F`)** | $\$500.00$ / point ($1\text{c}/\text{lb} = \$500$) | Full 50,000 lb contract value tracking |
| **Dynamic Stop Loss** | $2.5 \times \text{ATR}(14)$ ($2.8\times$ in Super El Nino) | Adapts stop distance to market volatility & weather shocks |
| **Trailing Take Profit** | $4.5 \times \text{ATR}(14)$ | Chandelier exit ratcheting after $2.0 \times \text{ATR}$ gain |
| **Soft Drawdown Limit** | $8.0\%$ Peak-to-Trough | Automatically halves target contract sizing |
| **Hard Circuit Breaker** | $15.0\%$ Peak-to-Trough | Forces $100\%$ flat liquidation to cash to protect principal |
| **Minimum Holding Period** | $3\text{ Days}$ | Hysteresis smoothing filter to eliminate execution whip |
| **Slippage & Fees** | $2.5\text{ bps} + \$2.50/\text{contract}$ | Realistic transaction friction and clearing fee modeling |

---

## 8. License
Released under the MIT Open Source License. 100% Free for personal and quantitative research.
