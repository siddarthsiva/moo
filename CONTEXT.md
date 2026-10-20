# PROJECT MOO: QUANTITATIVE BOVINE COMMODITY TRADING ENGINE
## Comprehensive System Context, Market Microstructure, & Quantitative Blueprint

---

## 1. Executive Summary & Purpose

**Project MOO (ALPHA-BOVINE)** is an institutional-grade, multi-factor quantitative algorithmic trading engine designed specifically for cattle and bovine commodities. The system models the physical and financial dynamics of the beef supply chain—primarily **Live Cattle Futures (CME: `LE=F`)** and **Feeder Cattle Futures (CME: `GF=F`)**—along with the entire input and substitute cross-commodity ecosystem:
- **Corn Feed (CBOT: `ZC=F`)**
- **Soybean Meal (CBOT: `ZM=F`)**
- **Lean Hogs (CME: `HE=F`)**
- **Class III Dairy/Milk (CME: `DC=F`)**
- **Crude Oil (NYMEX: `CL=F`)**
- **US Dollar Index (ICE: `DX-Y.NYB`)**

---

## 2. Bovine Market Microstructure & Physical Supply Chain

To trade cattle commodities algorithmically, one must model the real-world biological constraints and physical transformation processes of the livestock industry:

```
+-----------------------------------------------------------------------------+
|                           THE BEEF LIFECYCLE                                |
|                                                                             |
|  [ Cow-Calf Rancher ]                                                       |
|        │ Breeding gestation: ~9 months                                      |
|        │ Calf nursing on pasture: ~6 to 8 months (~500 lbs)                 |
|        ▼                                                                    |
|  [ Backgrounder / Stocker ]                                                 |
|        │ Summer grazing on native grass / forage                            |
|        │ Grows calves to ~700–850 lbs                                       |
|        ▼                                                                    |
|  [ Feeder Cattle Auction / CME: GF=F ] ◄─── Input for Feedlots              |
|        │ Feeder calves purchased by feedlots                                |
|        ▼                                                                    |
|  [ Commercial Feedlots ]                                                    |
|        │ Feed conversion: 150–200 days on Corn (ZC=F) + Soymeal (ZM=F)      |
|        │ Weight gain: ~3.5–4.0 lbs/day up to 1,300–1,450 lbs                |
|        ▼                                                                    |
|  [ Live Cattle / CME: LE=F ] ◄─── Slaughter-ready Finished Steers           |
|        │ Purchased by meat packing conglomerates (Tyson, JBS, Cargill, etc.)|
|        ▼                                                                    |
|  [ Meat Packers & Wholesale Distribution ]                                  |
|        │ Boxed Beef Cutout (Choice vs Select spread)                        |
|        ▼                                                                    |
|  [ Retail Supermarkets & Foodservice / Export Markets ]                     |
+-----------------------------------------------------------------------------+
```

### CME Contract Specifications & Multipliers

Understanding point multipliers is critical for correct position sizing and risk management:

| Commodity | Symbol | Exchange | Contract Size | Point Multiplier ($) | Tick Size | Tick Value ($) | Margin (Typ.) | Settlement |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Live Cattle** | `LE=F` | CME | 40,000 lbs (400 cwt) | **$400.00** per $1.00/cwt | 0.025c/lb | $10.00 | $2,200 | Physical Delivery |
| **Feeder Cattle** | `GF=F` | CME | 50,000 lbs (500 cwt) | **$500.00** per $1.00/cwt | 0.025c/lb | $12.50 | $3,000 | Cash Settled Index |
| **Corn** | `ZC=F` | CBOT | 5,000 bushels | **$50.00** per 1c/bu ($5,000/$1) | 0.25c/bu | $12.50 | $1,800 | Physical Delivery |
| **Soybean Meal** | `ZM=F` | CBOT | 100 short tons | **$100.00** per $1.00/ton | $0.10/ton | $10.00 | $2,000 | Physical Delivery |
| **Lean Hogs** | `HE=F` | CME | 40,000 lbs | **$400.00** per $1.00/cwt | 0.025c/lb | $10.00 | $2,100 | Cash Settled Index |
| **Class III Milk** | `DC=F` | CME | 200,000 lbs (2,000 cwt)| **$2,000.00** per $1.00/cwt | 0.01c/lb | $20.00 | $1,500 | Cash Settled |
| **Crude Oil** | `CL=F` | NYMEX | 1,000 barrels | **$1,000.00** per $1.00/bbl | 0.01/bbl | $10.00 | $6,000 | Physical Delivery |
| **US Dollar Index**| `DX-Y.NYB`| ICE | 1,000 index pts | **$1,000.00** per 1.00 pt | 0.005 pts | $5.00 | $2,500 | Financial |

---

## 3. Biological Cattle Cycles & Climatology Dynamics

### The 10–12 Year Macro Cattle Cycle
Unlike crops that can be planted and harvested within 4–6 months, cattle have an unavoidable biological reproduction lag:
1. **Breeding decision to heifer conception:** ~1–2 months
2. **Gestation period:** 9 months (283 days)
3. **Nursing to weaning:** 7 months
4. **Backgrounding to feedlot entry:** 4–6 months
5. **Feedlot finishing to slaughter:** 5–7 months
- **Total Lag:** From the day a rancher decides to expand their herd by retaining a heifer instead of selling her for beef, it takes **2.5 to 3 years** before her first calf is slaughtered and reaches retail shelves.

#### Cyclical Regimes
- **Liquidation Phase (Bearish Short-Term, Ultra-Bullish Long-Term):**
  When drought parches pastures or feed grain prices surge, feedlots and ranchers lose money. Ranchers are forced to cull breeding cows and send heifers to feedlots.
  - *Immediate Effect (Months 1–6):* Slaughter volume temporarily increases -> price caps or slight weakness.
  - *Delayed Effect (Years 1–4):* The breeding herd is decimated. Calf crops shrink to multi-decade lows. Once pasture recovers, ranchers withhold heifers from slaughter to rebuild herds, creating a supply vacuum that drives prices to historic record highs (e.g., the 2014–2015 and 2023–2024 cattle supercycles).
- **Expansion Phase:**
  High calf prices incentivize herd expansion. Heifer retention reduces immediate slaughter supply, driving prices higher until the new, larger calf crops hit the market 3 years later, ushering in cyclical topping.

### Intra-Year Seasonal Climatology
1. **Spring Grilling Season (March–May):**
   Retailers and packers aggressively build beef inventory for Memorial Day, Father's Day, and Fourth of July. Live cattle experience strong seasonal rallies (+0.70 normalized seasonal score).
2. **Summer Heat Demand Lull (June–August):**
   Post-holiday demand cools off, extreme summer heat slows consumer indoor cooking, and fed cattle supplies peak (-0.45 score).
3. **Autumn Calf Run (September–November):**
   Spring-born calves are weaned and brought down from summer mountain pastures into feedlots. This creates a seasonal supply flood of Feeder Cattle, seasonally depressing feeder calf prices (-0.60 score).
4. **Winter Storm Lag (December–February):**
   Severe winter blizzards in the Great Plains (Texas, Kansas, Nebraska, Colorado) force cattle to expend energy staying warm rather than converting feed into fat. Average daily gain drops, packing plant operations are delayed by road closures, creating short-term delivery tightness (+0.25 score).

### The Super El Niño Climatology Compensation Engine
An intense equatorial Pacific ENSO warm phase (Super El Niño, defined by NOAA CPC Oceanic Niño Index $\text{ONI} \ge +2.0^\circ\text{C}$) fundamentally disrupts the biological and microeconomic mechanics of cattle trading:

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

#### The 5 Transmission Channels:
1. **Southern Plains Pasture Hydration & Heifer Retention:**
   Subtropical atmospheric rivers break plains droughts, restoring lush pasture. Ranchers retain heifers and breeding cows instead of sending them to slaughter, generating an acute immediate supply withdrawal ($\alpha_{\text{retention}} = +0.35$).
2. **Midwest Corn Bumper Crop & Cheap Feed:**
   El Niño suppresses summer Midwest heat waves, yielding record corn production (`ZC=F`). Feed grain prices plummet, dramatically expanding gross feeding margins and prompting feedlots to bid aggressively for feeder calves.
3. **Autumn Calf Run Suppression:**
   With abundant winter wheat grazing available across Texas, Oklahoma, and Kansas, ranchers graze spring-born calves through the winter rather than flooding autumn auction rings. The classic September–November feeder calf supply dump is neutralized (shifting $GF$ seasonal bias from $-0.40$ to $+0.15$).
4. **Subtropical Mud & Average Daily Gain (ADG) Degradation:**
   Persistent winter storms turn Great Plains feedlot pens into deep mud. Steers burn energy wading and shivering, reducing ADG by $10\%\text{--}15\%$. Yardage overhead increases by $+\$12.00/\text{head}$ (from $\$85.00$ to $\$97.00$), and slaughter weights fall, tightening prompt wholesale beef availability.
5. **Australian Drought Liquidation & Global Export Vacuum:**
   While North America receives moisture, El Niño inflicts severe drought on Australia (the world's second-largest beef exporter). After short-term Australian culling subsides, their national herd shrinks, creating a massive Pacific Rim export vacuum that channels foreign demand directly toward US beef.

---

## 4. The 6 Multi-Factor Quantitative Engines

Project MOO synthesizes 6 uncorrelated alpha drivers into a composite alpha score $S_t \in [-1.0, +1.0]$:

$$S_t = \sum_{i=1}^{6} w_i \cdot F_{i,t} \quad \text{where } \sum w_i = 1.0$$

### Quantitative Factor Weight Regimes

| Factor Engine | Key | Neutral / Baseline Weight | Super El Niño Weight | Quantitative Mechanism |
| :--- | :--- | :--- | :--- | :--- |
| **Cattle Crush & Feedlot Margin** | `crush_margin` | $0.25$ ($25\%$) | $0.25$ ($25\%$) | Feedlot gross transformation margin & Feeder/Live parity ratio |
| **CFTC COT Smart Money** | `cot_sentiment` | $0.20$ ($20\%$) | $0.15$ ($15\%$) | Commercial hedger accumulation vs Managed Money crowding |
| **Biological Seasonality** | `seasonality` | $0.15$ ($15\%$) | $0.20$ ($20\%$) | Biological cattle calendar & Fourier harmonic regression |
| **US Drought & Macro DXY** | `macro_drought` | $0.15$ ($15\%$) | $0.25$ ($25\%$) | Plains drought severity, NOAA ONI SST, & DXY currency elasticity |
| **Kalman Adaptive Trend** | `technical_trend` | $0.15$ ($15\%$) | $0.10$ ($10\%$) | 1D Kalman state filter, Donchian breakout & Garman-Klass vol |
| **Walk-Forward ML Ensemble** | `ml_ensemble` | $0.10$ ($10\%$) | $0.05$ ($5\%$) | Walk-forward Gradient Boosted Trees + Random Forest ensemble |

---

### Factor 1: Cattle Crush Spread & Feedlot Margin (`crush_margin`)
Models the physical transformation economics of commercial feedlots finishing calves into slaughter steers:
$$\text{Gross Feedlot Margin } (\$/\text{head}) = 13.0 \times P_{\text{Live}} - \left(7.5 \times P_{\text{Feeder}} + 50.0 \times \frac{P_{\text{Corn}}}{100}\right) - \text{Yardage Overhead}$$

* **Baseline Yardage:** $\$85.00/\text{head}$ fixed overhead (veterinary, labor, maintenance).
* **Super El Niño Yardage:** $\$97.00/\text{head}$ ($+\$12.00/\text{head}$ mud drag due to saturated feedlot pen conditions).
* **1-Year Rolling Margin Z-Score:**
  $$Z_t = \frac{\text{Margin}_t - \mu_{252}}{\sigma_{252}}$$
* **Live Cattle Directional Signal:**
  $$F_{\text{crush, LE}} = -0.5 \times Z_t$$
  *(Inverted mean-reversion: deep negative margin leads to placement cutbacks -> future live cattle deficit -> Bullish).*
* **Feeder-to-Live Ratio Parity Arbitrage:**
  $$\text{Ratio}_t = \frac{P_{\text{Feeder}}}{P_{\text{Live}}}$$
  * Baseline parity equilibrium: $1.35$
  * Super El Niño parity equilibrium: $1.42$ (feedlots bid up calves as cheap corn expands conversion margins)
  * Statistical pairs trading triggers when $|Z_{\text{Ratio}}| > 1.75$.

---

### Factor 2: CFTC COT Smart Money Sentiment (`cot_sentiment`)
Extracts institutional positioning from public CFTC Commitments of Traders weekly reports:
* **Commercial Hedgers (Packers, Cattlemen):** Regarded as the informed "smart money" operators.
* **Managed Money (CTAs, Hedge Funds):** Trend-following momentum speculators prone to overextension and stop cascades.
* **3-Year Rolling Commercial Percentile Index:**
  $$\text{COT Index}_t = \frac{\text{CommNet}_t - \min_{756}(\text{CommNet})}{\max_{756}(\text{CommNet}) - \min_{756}(\text{CommNet})} \times 100$$
  * $\text{COT Index} > 80$: Commercial accumulation -> Cyclical bottom signal.
  * $\text{COT Index} < 20$: Commercial distribution / Speculator bubble -> Exhaustion top warning.
* **Speculator Crowding Penalty:** Activated when Managed Money net long positioning reaches the 90th percentile of its 3-year history.

---

### Factor 3: Bovine Seasonality & Climatology (`seasonality`)
* Combines empirical monthly biological weights with a 2-frequency Fourier harmonic series regressed against daily price returns over rolling 10-year windows without lookahead bias.
* **Super El Niño Modulation:**
  * Autumn calf run damping: Abundant winter wheat grazing neutralizes the autumn feeder price collapse ($GF$ seasonal factor shifts from $-0.40$ in normal regimes to $+0.15$ under Super El Niño).
  * Winter delivery premium: Wet muddy feedlots reduce daily weight gain, amplifying the December–February seasonal rally.

---

### Factor 4: US Drought Severity, ENSO Climatology & Macro DXY (`macro_drought`)
* **Oceanic Niño Index (ONI):** 3-month running mean of ERSST.v5 SST anomalies in the Niño 3.4 region ($5^\circ\text{N}-5^\circ\text{S}, 120^\circ-170^\circ\text{W}$):
  * $\text{ONI} \ge +2.0^\circ\text{C}$: Super El Niño regime -> Heifer retention supply withdrawal (+0.35 alpha boost).
  * $\text{ONI} \le -0.5^\circ\text{C}$: La Niña regime -> Plains pasture drought and cow herd liquidation.
* **US Plains Pasture Drought Severity:** 180-day rolling NDMC pasture stress index relative to the 35.0 baseline (threshold of 60 indicates severe herd liquidation).
* **US Dollar Index (DXY) Export Competitiveness:** Inverted 60-day DXY Z-score. Weaker dollar stimulates foreign demand for US beef across export markets.
* **Protein Substitution Ratio:** Mean-reversion of the Live Cattle to Lean Hogs price ratio ($P_{\text{LE}} / P_{\text{HE}}$) with $\pm 2.0\sigma$ Bollinger bands.

---

### Factor 5: Kalman Trend & Momentum (`technical_trend`)
* **1D Adaptive Kalman Filter:**
  $$\hat{x}_t^- = \hat{x}_{t-1}, \quad P_t^- = P_{t-1} + Q$$
  $$K_t = \frac{P_t^-}{P_t^- + R}, \quad \hat{x}_t = \hat{x}_t^- + K_t(z_t - \hat{x}_t^-), \quad P_t = (1 - K_t)P_t^-$$
* **Donchian 20-Day Breakout:** Position within 20-day high-low envelope.
* **Garman-Klass Efficient Volatility Estimator:**
  $$\sigma_{GK}^2 = \frac{1}{2}\left(\ln\frac{\text{High}}{\text{Low}}\right)^2 - (2\ln 2 - 1)\left(\ln\frac{\text{Close}}{\text{Open}}\right)^2$$
  Offers ~8x greater efficiency than close-to-close estimators, providing real-time volatility estimates for continuous contract sizing.

---

### Factor 6: Walk-Forward Ensemble Machine Learning (`ml_ensemble`)
* **Model Architecture:** Histogram Gradient Boosted Trees (`HistGradientBoostingClassifier`) blended with Random Forests (`RandomForestClassifier`), featuring an automated pure-NumPy regularized Ridge probability fallback when binary C-extension DLLs are constrained.
* **Validation:** Strict expanding window walk-forward validation with a 5-day forward embargo to ensure **zero data leakage**.

---

## 5. Institutional Risk Management Specifications

Futures contracts carry significant leverage. The execution engine enforces strict institutional risk parameters:

```
[ New Target Signal ]
         │
         ▼
[ Volatility Targeting ] ───► Target Annual Portfolio Vol: 15%
         │                    Contract Count = floor( (Equity * 15%) / (Price * Multiplier * AnnVol) )
         │                    Leverage Cap: <= 2.5x Gross Notional | Max Single-Asset Weight: <= 60%
         ▼
[ Drawdown Circuit Breakers ]
         │
         ├─► If Drawdown >= 8.0% (Soft Limit)  ──► Scale position size by 50%
         │
         └─► If Drawdown >= 15.0% (Hard Limit) ──► Immediate 100% Flat Cash Liquidation
         │
         ▼
[ Dynamic Stop Architecture ]
         │
         ├─► Initial Stop Loss: Entry +/- (2.5 * ATR_14) [Widened to 2.8 * ATR in Super El Niño]
         │
         ├─► Initial Take Profit: Entry -/+ (4.5 * ATR_14)
         │
         └─► Chandelier Trailing Exit: Ratchets stop after profit reaches 2.0 * ATR_14
         │
         ▼
[ Execution Friction & Smoothing ]
         │
         ├─► Minimum Holding Period: 3 Days (Hysteresis Filter against Whipsaws)
         │
         └─► Friction Modeling: 2.5 bps Slippage + $2.50 / Contract Commission
```

---

## 6. Project Architecture & File Directory

```
C:\projects\moo\
│
├── config.py                 # CME contract specifications, crush models, risk parameters, factor weights
├── main.py                   # Command-line orchestrator (scan, backtest, rebalance, dashboard, train-ml)
├── requirements.txt          # 100% free open-source dependencies
├── README.md                 # System overview and quickstart guide
├── CONTEXT.md                # (This file) Complete technical context, math, and domain manual
├── DASHBOARD_COMMANDS.md     # Bloomberg terminal dashboard lifecycle and execution control guide
│
├── data_cache/               # Local High-Speed Parquet & Pickle Cache
│   ├── paper_portfolio.json  # Persistent simulated portfolio ledger
│   └── *.parquet, *.pkl      # Aligned OHLCV, COT, Drought & NOAA ONI binary stores
│
├── data/                     # Free Data Acquisition Pipeline
│   ├── __init__.py
│   ├── data_loader.py        # Unified market loader with local pickle/parquet caching & offline fallback
│   ├── cot_fetcher.py        # Public CFTC Commitments of Traders downloader & parser
│   ├── macro_fetcher.py      # Free FRED macro series, US Drought Monitor & NOAA ONI SST loader
│   └── mock_generator.py     # Stochastic synthetic generator for deterministic 8-asset testing
│
├── factors/                  # Quantitative Factor Modules
│   ├── __init__.py
│   ├── crush_spread.py       # Cattle Crush feedlot margin ($/head & cwt) and parity ratio
│   ├── sentiment_cot.py      # Commercial Smart Money index and speculator crowding factor
│   ├── seasonality.py        # Biological cattle calendar and climatology regressions
│   ├── macro_weather.py      # Drought severity, NOAA ONI, DXY elasticity, and protein substitution
│   ├── technical.py          # Kalman trend filter, Donchian channels, RSI, Garman-Klass vol
│   └── factor_engine.py      # Composite alpha aggregator & Information Coefficient (IC) engine
│
├── models/                   # Prediction & Strategy Logic
│   ├── __init__.py
│   ├── ml_predictor.py       # Walk-forward ensemble ML alpha predictor with pure-NumPy fallback
│   └── strategy.py           # Directional alpha & Cattle Crush spread trading signal engine
│
├── execution/                # Execution & Risk Control
│   ├── __init__.py
│   ├── risk_manager.py       # Volatility targeting, dynamic ATR stops, and DD circuit breakers
│   └── paper_trader.py       # Live scanner, simulated order book, and persistent JSON portfolio
│
├── backtest/                 # Simulation Engine
│   ├── __init__.py
│   ├── backtester.py         # Event-driven futures backtester with slippage and point values
│   └── metrics.py            # Institutional tear-sheet metrics and monthly returns heatmap
│
├── ui/                       # User Interface
│   ├── __init__.py
│   └── app.py                # Bloomberg Terminal-style quantitative trading dashboard (5 workspaces)
│
└── tests/                    # Testing Suite
    ├── __init__.py
    └── test_all.py           # Exhaustive unit and integration test suite (100% pass)
```

---

## 7. Bloomberg Terminal Interface (`ui/app.py`)

The platform's frontend is styled as an authentic Bloomberg Professional Terminal interface:
- **Aesthetic Design:** Pure obsidian black (`#000000`), signature amber headers (`#ff9900`), terminal uptick green (`#00ff66`), crimson red (`#ff3b30`), cyan ratios (`#00e5ff`), dark gridlines (`#161922`), and monospace typography (`Roboto Mono`).
- **Terminal Status Bar:** Command line prompt emulation (`CMD> AGRI LE <GO>`), live connection status (`GLOBEX CME: LIVE`), and UTC timestamps.
- **Universal Multi-Display Responsive Engine:** Custom CSS Grid, media query breakpoints, and fluid typography system ensuring that the terminal renders on any screen resolution from 4K ultrawide monitors down to smartphones.

#### Cross-Device Responsive Architecture & Ergonomic Specifications:

| Display Form Factor | Viewport Range | Layout Behavior & Visual Adaptation |
| :--- | :--- | :--- |
| **4K & Ultrawide** | $\ge 1920\text{px}$ up to $3840\text{px}+$ | Centered container (`max-width: 2200px`) prevents horizontal chart elongation into thin, flat ribbons, preserving optimal aspect ratios for technical wicks and volume bars. |
| **Desktops & Large Laptops** | $1200\text{px} - 1919\text{px}$ | Native institutional workstation layout: 8-column USDA telemetry strip (`AGRI DES <GO>`), 6-column target metrics deck, side-by-side Plotly chart pairs, and 3-column trade desk. |
| **Small Laptops & Netbooks** | $992\text{px} - 1199\text{px}$ | Telemetry strip adapts to 4×2 grid; metric cards adapt to 3×2 grid; horizontal container margins dynamically compress. |
| **Tablets & iPads (Portrait/Landscape)** | $768\text{px} - 1080\text{px}$ | All 2-column chart pairs (`st.columns([1, 1])`) and 3-column trade desk widgets automatically stack to **100% full width**, giving candlesticks, volume, and subplots maximum resolution without clipping. |
| **Smartphones (iPhone, Galaxy, Pixel)** | $360\text{px} - 767\text{px}$ | Reclaims 140px+ of screen width by reducing default margins from 80px (`5rem`) to `0.5rem`; telemetry cards arrange in a 2×4 touch grid; target metrics arrange in a 2×3 grid; buttons stretch to full width with 38px+ touch targets; dataframes feature touch inertia scrolling. |
| **Compact Handhelds** | $< 360\text{px}$ | Single-column fallback ensures zero horizontal overflow or viewport wobbling. |

#### Key UI Engineering Principles:
1. **Fluid Typography:** Uses CSS `clamp(min, preferred, max)` on all headers, metrics, and badges to eliminate text truncation or single-character wraps across high-DPI retina screens and small viewports.
2. **Bottom-Anchored Chart Legends:** Plotly chart legends are dynamically centered at `y = -0.14`, preventing collisions with titles or candle wicks on narrow mobile viewports.
3. **Touch-Inertia Scrolling:** DataFrames, quote boards, and blotters have `-webkit-overflow-scrolling: touch` enabled for smooth multi-touch navigation without horizontal page blowout.
4. **Accessible Touch Targets:** Action buttons (`TRANSMIT REBALANCE ORDER`, `APPLY FACTOR WEIGHTS`, `EXECUTE BACKTEST`) conform to mobile tap target standards with tactile active-state depression.

### Workspace 1: `01 // LIVE COCKPIT`
Comprehensive real-time trading station featuring 19 integrated components:
1. Direct Bloomberg Function Key navigation bar (`[F1: HELP]` to `[F12: VaR]`) and network latency telemetry.
2. Global Multi-Commodity Quote Board (`BQ <GO>`) with Bid, Ask, Spread, Last, Net Change, ATR, Ann Vol, RSI, and Volume across 8 assets.
3. Macro Climatology & USDA Fundamental Telemetry Strip (`AGRI DES <GO>`) with 8 KPI cards (ENSO ONI, Drought, Feedlot Placements, Beef Cow Herd, Boxed Beef Choice, Choice/Select Spread, Packer Margin, DXY).
4. Multi-Horizon Technical Trend Matrix (`TREND <GO>`) across 6 horizons (15-Min, 1-Hour, 4-Hour, Daily, Weekly, Monthly).
5. Chart 1 (`GP <GO>`): Primary Technical Candlestick Terminal with Adaptive Kalman Trend, EMAs, Bollinger Bands, Stops, Volume, RSI, and MACD.
6. Chart 2 (`CRUSH <GO>`): Cattle Crush Margin Spread Monitor ($/head) with 30D SMA and Feeder/Live parity ratio.
7. Chart 3 (`CORR <GO>`): 60-Day Rolling Cross-Commodity Correlation Heatmap matrix.
8. Chart 4 (`ANR <GO>`): Multi-Factor Institutional Polar Radar Decomposition.
9. Chart 5 (`FWD <GO>`): Forward Term Structure Curve displaying prompt shortage backwardation premiums.
10. Chart 6 (`VOL <GO>`): Realized Volatility Term-Structure Cone across 5D to 180D windows.
11. Chart 7 (`COF <GO>`): USDA Cattle on Feed Monthly Placements, Marketings & Inventory % YoY.
12. Chart 8 (`PACK <GO>`): Boxed Beef Wholesale Cutout (Choice vs Select) & Grade Premium Spread.
13. Chart 9 (`COT <GO>`): CFTC Commitments of Traders Commercial Hedgers vs Managed Money Net Contracts & 3-Year Index.
14. Chart 10 (`SPRD <GO>`): Inter-Commodity Protein Substitution Ratio (Live Cattle to Lean Hogs) with $\pm 2\sigma$ bands.
15. Chart 11 (`MD <GO>`): Synthetic CME Globex Depth of Market Ladder (Level 2 DOM).
16. Chart 12 (`STRESS <GO>`): Value at Risk Return Distribution with 3 Macro Stress Scenarios (Blizzard Mud Drag, Feed Spike, Heifer Squeeze).
17. Institutional Risk & Margin Telemetry Table (`MARG <GO>`) with VaR 95/99, Expected Shortfall, Drawdown, and Leverage.
18. Mathematical Factor Attribution & Decomposition Matrix (`ANR <GO>`).
19. 3-Column Execution Dispatch Ticket (`OMON <GO>`), Active Order Blotter (`BLOT <GO>`), and Live Financial News Wire (`NEWS <GO>`).

### Workspace 2: `02 // STRATEGY BACKTESTER` (`BTST <GO>`)
Event-driven futures simulation platform providing:
- Parameter configuration: Symbol selection (`LE=F`, `GF=F`), Strategy mode (Directional Multi-Factor vs Feeder/Live Spread Trading), date ranges, initial capital, volatility targeting toggle, ATR stops, Chandelier trailing exits, and ML walk-forward loop toggle.
- Cumulative equity growth curve plotted against Buy & Hold benchmark.
- Underwater drawdown profile (%) tracking peak-to-trough drawdowns and recovery periods.
- 14 institutional tear-sheet performance metrics (CAGR, Annualized Volatility, Sharpe Ratio, Sortino Ratio, Calmar Ratio, Max Drawdown, Max DD Duration, Total Executed Trades, Win Rate, Profit Factor, Average Trade PnL).
- Compounded Monthly Returns Matrix (%) heatmap table.
- Executed Trade Journal Audit Log tracking entry/exit timestamps, executed prices, contracts, PnL, commissions, and exit triggers.

### Workspace 3: `03 // FACTOR RESEARCH` (`ANR <GO>`)
Deep-dive mathematical research panes across 5 dedicated sub-workspaces:
1. `[01] CATTLE CRUSH SPREAD`: Feedlot gross margin ($/head) with zero-line boundary and Feeder-to-Live price ratio against regime parity (1.35 neutral, 1.42 Super El Niño).
2. `[02] CFTC COT POSITIONING`: Commercial hedgers vs managed money net contracts and 3-year commercial percentile index with 80/20 extreme bounds.
3. `[03] BIOLOGICAL SEASONALITY`: Monthly excess return profile (%) across all 12 calendar months for Live Cattle and Feeder Cattle.
4. `[04] DROUGHT & MACRO DXY`: US Plains Cattle Pasture Drought Severity Index (0–100) with severe herd liquidation threshold (60) and baseline normal (35).
5. `[05] ENSO ONI CLIMATOLOGY`: NOAA ONI SST Anomaly historical curve, Feeder Cattle autumn calf run comparison (baseline vs Super El Niño damped curve), and the 5-channel Super El Niño transmission matrix.

### Workspace 4: `04 // PAPER PORTFOLIO` (`PORT <GO>`)
Persistent simulated account management engine:
- Portfolio summary telemetry: Total Portfolio Equity, Available Cash, Open Position Count, Unrealized PnL, Realized PnL, and ROI.
- Active Open Positions Blotter (`POS <GO>`) with live market pricing, unrealized PnL, entry timestamp, and dynamic stop-loss/take-profit brackets.
- Simulated Trade Execution History (`BLOT <GO>`) tracking execution actions, fills, contract quantities, and net realized PnL.

### Workspace 5: `05 // CME SPECS & ARCH` (`DES <GO>`)
Institutional reference guide:
- Complete CME/ICE exchange specifications matrix across the 8-asset universe (contract sizes, units, point multipliers, tick sizes, tick values, and initial margin requirements).
- Full documentation of the 100% free open-source data architecture, including Yahoo Finance continuous futures, CFTC COT archives, FRED macro, US Drought Monitor, NOAA ONI archives, and deterministic synthetic benchmark fallback.

### Workspace 6: `06 // GLOBAL SUPPLY CHAIN & AIS` (`SUPP <GO>`)
Physical livestock intelligence, maritime AIS fleet tracking, and industry economics desk structured across 6 dedicated sub-panes:

1. **`01 // BREED & HERD GEOGRAPHY [GEOG]`**:
   - Global interactive geographic Scattergeo map plotting 11 major cattle nations by herd inventory and beef production.
   - Comprehensive breed taxonomy matrix detailing *Bos taurus* (Angus, Wagyu, Charolais, Hereford, Holstein) and *Bos indicus* / *Bubalus bubalis* (Nelore, Brahman, Indian Carabeef) with marbling potential, heat tolerance, market weights, and commercial utilization.
   - Finishing system breakdown (% Grain Feedlot vs % Pasture Grass-fed vs % Cull).
   - Individual Country Dossier Inspector with herd census, trade roles, carcass yields, and quarantine protocols.

2. **`02 // SUPPLY & DEMAND MATRIX [SND]`**:
   - Quantitative surplus/deficit scoring: Net S&D tension spread ($\text{Supply Score} - \text{Demand Score}$).
   - National Herd Cycle Phase indicator ($-100$ liquidation trough to $+100$ aggressive retention).
   - Plains pasture drought severity ratings and national per-capita beef consumption metrics.
   - Active biosecurity and phytosanitary border tracking (FMD vaccination zones, BSE negligible risk status, screwworm border barriers).

3. **`03 // TRADE CORRIDORS & SANKEY [FLOW]`**:
   - 3-tier interactive Plotly Sankey topology: Exporter Nations $\to$ Commodity Types (Chilled Cuts, Frozen Boneless, Live Feeder/Slaughter Cattle, Offal) $\to$ Importer Nations.
   - Bilateral trade flow matrices tracking annual tonnage, USD valuation, and transportation logistics modes (40ft Reefer, Livestock Carrier, Fast Reefer, Truck).

4. **`04 // MARITIME AIS FLEET TRACKER [SHIP]`**:
   - Real-time AIS maritime world map tracking 15 flagship specialized livestock carriers (*MV Ocean Drover*, *MV Nada*, *MV Al Kuwait*, *MV Brahman Express*, *MV Ocean Shearer*, *MV Gudali Express*, *MV Polaris 2*, etc.).
   - Maritime choke point detection: Automated alerts for passages through Suez Canal, Bab-el-Mandeb / Red Sea War Risk Area, Strait of Malacca, Strait of Gibraltar, and Lombok Strait.
   - Live Onboard Animal Welfare Telemetry: Fodder reserve days, water desalination capacity ($L/\text{day}$), mechanical ventilation air changes per hour (ACH: 60–85 ACH), and voyage heat stress indices (THI).

5. **`05 // INDUSTRY COST WATERFALL [COST]`**:
   - **Marine Mortality Insurance Engine:** Base premium (1.4%–3.8% CIF) with war-risk surcharges (+0.75%), seasonal heat stress multipliers (+0.65%), and accredited veterinarian discounts (-0.20%).
   - **Feedlot Cost-of-Gain (COG) Engine:** Dynamic calculation based on corn ($/bu), DDGS protein ($/ton), and alfalfa hay ($/ton) with yardage and financing charges.
   - **Packer Gross Processing Spread:** Live cattle cash price vs Choice boxed beef cutout + drop credit hide/offal byproduct value ($/head).
   - **Farm-to-Retail Cost Waterfall:** 10-stage cumulative cost accumulation from a 550 lb weaned calf to the retail supermarket meat counter.

6. **`06 // GLOBAL BOVINE NEWS WIRE [NEWS]`**:
   - Real-time streaming news engine integrating USDA FAS, CME Group Ag, Beef Central, and Meat & Livestock Australia (MLA).
   - Automated NLP sentiment classification (▲ Bullish, ▼ Bearish, ■ Neutral) and market impact scoring (**HIGH**, **MEDIUM**, **LOW**).
   - Category filtering across `[TRADE]`, `[MARITIME]`, `[CASH / PACKER]`, `[BIOSECURITY]`, `[CLIMATE]`, and `[POLICY]`.

---

## 8. Command Reference & Usage Guide

```powershell
# 1. Run Live Multi-Factor Signal Scan (Compensating for Super El Niño)
python main.py --mode scan --enso super_elnino

# 2. Run Live Scan under Neutral Climatology
python main.py --mode scan --enso neutral

# 3. Run Comprehensive Backtest (Live Cattle, Directional Multi-Factor)
python main.py --mode backtest --symbol LE=F --start-date 2018-01-01 --enso super_elnino

# 4. Run Cattle Crush Statistical Arbitrage Backtest (Feeder vs Live Spread Trading)
python main.py --mode backtest --symbol LE=F --strategy spread_trading --enso super_elnino

# 5. Run Fast Backtest Disabling ML Walk-Forward Loop
python main.py --mode backtest --symbol LE=F --no-ml

# 6. Execute Simulated Paper Trade Rebalance
python main.py --mode rebalance --enso super_elnino

# 7. Train Walk-Forward ML Alpha Model & Output Feature Importances
python main.py --mode train-ml --symbol LE=F

# 8. Launch Bloomberg Terminal Interactive Web Dashboard
streamlit run ui/app.py
# or
python main.py --mode dashboard

# 9. Launch Dashboard on Custom Port in Headless Mode
streamlit run ui/app.py --server.port 8502 --server.headless true
```

---

## 9. Unit & Integration Test Suite Verification

Project MOO maintains an exhaustive test suite with 100% pass rates across all modules:

```powershell
python -m unittest tests/test_all.py
```

### Verified Test Cases:
1. `test_mock_data_generation`: Validates deterministic synthetic OHLCV generation across all 8 assets with proper price relationships ($H \ge L$).
2. `test_cattle_crush_factor`: Verifies gross feedlot margin ($/head), Feeder/Live price ratio, and normalized factor score bounds $[-1.0, +1.0]$.
3. `test_cot_sentiment_factor`: Verifies CFTC commercial net percentile index and speculator crowding penalty score.
4. `test_seasonality_factor`: Verifies biological monthly excess return regressions and Fourier harmonic series.
5. `test_macro_weather_factor`: Verifies Plains pasture drought severity, DXY currency elasticity, and protein substitution ratio scores.
6. `test_technical_factors`: Verifies 1D adaptive Kalman filter, 14-day ATR, RSI(14), and Garman-Klass volatility efficiency.
7. `test_factor_engine`: Verifies factor matrix assembly, composite alpha calculation, and rolling Information Coefficient (IC) telemetry.
8. `test_ml_alpha_model`: Verifies feature engineering, 5-day embargo cross-validation, and pure-NumPy Ridge fallback prediction.
9. `test_risk_manager`: Verifies continuous volatility-targeted contract sizing and dynamic stop-loss/take-profit exit triggers.
10. `test_backtest_simulation`: Verifies event-driven simulation, realistic slippage/commissions, tear-sheet metrics, and monthly return heatmaps.
11. `test_paper_trader_scan_and_execute`: Verifies live multi-asset signal scanning and persistent portfolio ledger updates.
12. `test_super_elnino_compensation`: Verifies end-to-end Super El Niño climatology compensation (ONI classification, heifer retention alpha boost, autumn calf run damping, and feedlot mud drag).
