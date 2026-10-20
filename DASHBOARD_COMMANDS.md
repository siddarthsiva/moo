# Project MOO // Dashboard Control Guide

This document outlines all commands and procedures to **start up**, **access**, **shut down**, and **troubleshoot** the Bloomberg Terminal-style Streamlit quantitative dashboard (`ui/app.py`).

---

## 1. Quick Reference

| Action | Windows (PowerShell) | Windows (CMD) | Linux / macOS (Bash) |
| :--- | :--- | :--- | :--- |
| **Start (CLI)** | `python main.py --mode dashboard` | `python main.py --mode dashboard` | `python main.py --mode dashboard` |
| **Start (Streamlit)** | `streamlit run ui/app.py` | `streamlit run ui/app.py` | `streamlit run ui/app.py` |
| **Stop (Interactive)** | `Ctrl + C` | `Ctrl + C` | `Ctrl + C` |
| **Stop by Port (8501)** | `Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue \| ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }` | `for /f "tokens=5" %a in ('netstat -aon ^\| findstr :8501') do taskkill /f /pid %a` | `lsof -ti:8501 \| xargs kill -9` |
| **Stop by Process** | `Stop-Process -Name streamlit -Force -ErrorAction SilentlyContinue` | `taskkill /F /IM streamlit.exe` | `pkill -f streamlit` |

---

## 2. Prerequisites

Ensure dependencies are installed and your Python environment is activated:

```bash
# Activate virtual environment if configured:
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
.\venv\Scripts\activate.bat
# Linux/macOS:
source venv/bin/activate

# Install required packages (if not already installed)
pip install -r requirements.txt
```

---

## 3. Starting the Dashboard

### Option A: Via Main Orchestrator (Recommended)
This uses the Project MOO CLI dispatcher and automatically ensures UTF-8 encoding support:

```bash
python main.py --mode dashboard
```

### Option B: Direct Streamlit Execution
Run the Streamlit app directly from the repository root:

```bash
streamlit run ui/app.py
```

*Note: If `streamlit` is not recognized directly in your PATH, use Python module syntax:*
```bash
python -m streamlit run ui/app.py
```

### Option C: Custom Port or Host Binding
By default, the dashboard binds to `http://localhost:8501`. To customize the port or expose it on a local network:

```bash
# Run on port 8502
streamlit run ui/app.py --server.port 8502

# Allow access across local network (bind to all interfaces)
streamlit run ui/app.py --server.address 0.0.0.0 --server.port 8501

# Headless mode (prevents opening browser automatically)
streamlit run ui/app.py --server.headless true

# Production / High-Performance Mode (disables file watcher polling)
streamlit run ui/app.py --server.fileWatcherType none --server.headless true
```

### Option D: Run in Background

#### Windows (PowerShell)
```powershell
Start-Process python -ArgumentList "main.py --mode dashboard" -WindowStyle Hidden
```

#### Linux / macOS (Bash)
```bash
nohup python main.py --mode dashboard > dashboard.log 2>&1 &
```

---

## 4. Accessing the Dashboard & Workstation Layout

Once started, open any web browser and navigate to:
- **Local:** [http://localhost:8501](http://localhost:8501) or [http://127.0.0.1:8501](http://127.0.0.1:8501)
- **Network (if bound to 0.0.0.0):** `http://<your-machine-ip>:8501`

### The 6 Bloomberg Terminal Workstations:
1. **`01 // LIVE COCKPIT`**: Real-time institutional trading desk featuring the 8-asset Quote Board (`BQ <GO>`), Fundamental & ENSO Telemetry Strip (`AGRI DES <GO>`), Multi-Horizon Trend Matrix (`TREND <GO>`), 12 interactive Plotly charts (`GP <GO>`, `CRUSH <GO>`, `CORR <GO>`, `ANR <GO>`, `FWD <GO>`, `VOL <GO>`, `COF <GO>`, `PACK <GO>`, `COT <GO>`, `SPRD <GO>`, `MD <GO>`, `STRESS <GO>`), Risk Telemetry (`MARG <GO>`), Factor Decomposition, Execution Dispatch Ticket (`OMON <GO>`), Order Blotter (`BLOT <GO>`), and Live Bovine News Wire (`NEWS <GO>`).
2. **`02 // STRATEGY BACKTESTER`**: Event-driven backtester (`BTST <GO>`) simulating Directional Multi-Factor and Feeder/Live Cattle Spread Trading. Includes equity curve vs benchmark, underwater drawdowns, 14 tear-sheet metrics, monthly returns matrix, and trade audit log.
3. **`03 // FACTOR RESEARCH`**: Five dedicated research panes (`ANR <GO>`) covering Cattle Crush feedlot economics, CFTC COT smart-money accumulation, biological monthly seasonality, US Plains pasture drought severity, and NOAA ONI SST climatology.
4. **`04 // PAPER PORTFOLIO`**: Live simulated portfolio accounting (`PORT <GO>`) tracking cash, equity, open position brackets (`POS <GO>`), and trade execution history (`BLOT <GO>`).
5. **`05 // CME SPECS & ARCH`**: Contract specifications matrix (`DES <GO>`) for all 8 instruments, plus architecture documentation for the 100% free data pipeline.
6. **`06 // GLOBAL SUPPLY CHAIN & AIS`**: Physical commodity, maritime AIS fleet tracking, and industry economics desk (`SUPP <GO>`). Features 6 sub-panes:
   - `01 // BREED & HERD GEOGRAPHY [GEOG]`: Country-by-country breakdown of cattle varieties (Angus, Nelore, Wagyu, Brahman, Carabeef, Charolais, Holstein), herd census, carcass yields, and grain-fed vs pasture ratios on an interactive global map.
   - `02 // SUPPLY & DEMAND MATRIX [SND]`: Surplus vs deficit heatmaps, US herd liquidation vs Brazil expansion, pasture drought stress, and biosecurity/quarantine alerts (FMD, BSE, screwworm).
   - `03 // TRADE CORRIDORS & SANKEY [FLOW]`: 3-tier interactive Plotly Sankey diagram (Origin $\to$ Commodity $\to$ Destination), bilateral trade matrices, and transport logistics breakdown.
   - `04 // MARITIME AIS FLEET TRACKER [SHIP]`: Real-time interactive AIS world map tracking 15 flagship livestock carrier vessels (*Ocean Drover*, *Nada*, *Al Kuwait*, *Brahman Express*, etc.), choke point alerts (Suez, Bab-el-Mandeb, Malacca, Gibraltar), and onboard animal welfare telemetry (fodder days, water desalination, ventilation ACH, heat stress THI).
   - `05 // INDUSTRY COST WATERFALL [COST]`: Interactive scenario modelers for marine mortality insurance (1.4%–3.8% with war risk and heat stress surcharges), feedlot cost-of-gain ($/lb), meat packer processing margins, 40ft reefer container freight, and end-to-end calf-to-retail supply chain cost waterfalls.
   - `06 // GLOBAL BOVINE NEWS WIRE [NEWS]`: Real-time agribusiness wire with sentiment classification (bullish/bearish/neutral), market impact ratings (**HIGH** / **MED** / **LOW**), category filters, and live RSS headline streaming.

### Sidebar Controls & Function Keys:
- **Workspace Navigation:** Radio selector for the 6 workspaces above.
- **Market Data Feed Configuration:**
  - **`Live Yahoo Finance Feeds` (Toggle):** Switches between live real-time continuous futures quotes (CME: `LE=F`, `GF=F`, `HE=F`, `DC=F`; CBOT: `ZC=F`, `ZM=F`; NYMEX: `CL=F`; ICE: `DX-Y.NYB`) and local benchmark data.
  - **`🔄 REFRESH LIVE DATA` (Button):** Force-clears Streamlit data cache (`st.cache_data.clear()`) and immediately pulls the latest market quotes and candles.
  - **Data Feed Status Badge:** Live telemetry indicator displaying `● LIVE YAHOO FEED [YYYY-MM-DD]` in terminal green or `● BENCHMARK CACHE` in amber.
  - **Cache Invalidation TTL:** 300-second (5-minute) automated cache cycle ensuring live quote currency without incurring cloud rate-limiting.
- **Climatology Compensation Engine:** Dropdown to toggle active climate regimes (`Super El Niño`, `El Niño`, `Neutral`, `La Niña`).
- **Apply Regime Factor Weights `[F4]`:** Instantly sets recommended alpha weights for the active climate regime.
- **Factor Weight Sliders:** Real-time continuous adjustment of individual factor allocations (Crush Margin, CFTC COT, Seasonality, Drought/Macro, Kalman Trend, ML Ensemble).
- **Bloomberg Function Keys:** Navigation shortcuts in top header (`[F1: HELP]` to `[F12: VaR]`).

### Multi-Display & Universal Device Responsive Design:
The dashboard features an adaptive, cross-device CSS grid and fluid typography engine designed to look and function on any screen resolution:

| Display Form Factor | Viewport Range | Layout Behavior & Visual Adaptation |
| :--- | :--- | :--- |
| **4K & Ultrawide** | $\ge 1920\text{px}$ up to $3840\text{px}+$ | Centered container (`max-width: 2200px`) preventing charts from over-stretching into flat, illegible ribbons while maintaining terminal immersion. |
| **Desktops & Large Laptops** | $1200\text{px} - 1919\text{px}$ | Native institutional workstation layout: 8-column USDA telemetry strip, 6-column target metric deck, side-by-side Plotly chart pairs, and 3-column trade desk. |
| **Small Laptops & Netbooks** | $992\text{px} - 1199\text{px}$ | Telemetry strip adapts to 4×2 grid; metric cards adapt to 3×2 grid; horizontal container margins dynamically compress. |
| **Tablets & iPads (Portrait/Landscape)** | $768\text{px} - 1080\text{px}$ | All 2-column chart pairs (`st.columns([1, 1])`) and 3-column trade desk widgets automatically stack to **100% full width**, giving candlesticks, volume, and subplots maximum resolution without clipping. |
| **Smartphones (iPhone, Galaxy, Pixel)** | $360\text{px} - 767\text{px}$ | Reclaims 140px+ of screen width by reducing default margins from 80px (`5rem`) to `0.5rem`; telemetry cards arrange in a 2×4 touch grid; target metrics arrange in a 2×3 grid; buttons stretch to full width with 38px+ touch targets; dataframes feature touch inertia scrolling. |
| **Compact Handhelds** | $< 360\text{px}$ | Single-column fallback ensures zero horizontal overflow or viewport wobbling. |

#### Key Mobile & Tablet Ergonomic Features:
1. **Fluid Typography:** All headers, metrics, and badges utilize CSS `clamp(...)` scaling to eliminate text truncation or awkward number wrapping across retina and low-DPI displays.
2. **Bottom-Anchored Chart Legends:** Plotly chart legends are dynamically centered at `y = -0.14`, preventing collisions with titles or candle wicks on narrow mobile viewports.
3. **Touch-Inertia Scrolling:** DataFrames, quote boards, and blotters have `-webkit-overflow-scrolling: touch` enabled for smooth multi-touch navigation without horizontal page blowout.
4. **Accessible Touch Targets:** Action buttons (`TRANSMIT REBALANCE ORDER`, `APPLY FACTOR WEIGHTS`, `EXECUTE BACKTEST`) conform to mobile tap target standards with tactile active-state depression.
5. **Testing Different Screen Sizes:** Open DevTools in Chrome, Edge, or Firefox (`F12` or `Ctrl + Shift + I`), toggle the Device Emulation toolbar (`Ctrl + Shift + M`), and select various presets (iPhone 14/15/16 Pro, iPad Pro, Galaxy S20, or custom 4K viewports).

---

## 5. Shutting Down the Dashboard

### Method 1: Foreground Terminal (Standard)
If the dashboard is running in an active terminal/console:
- Press **`Ctrl + C`** (or **`Ctrl + Break`** on Windows).
- If prompted `Terminate batch job (Y/N)?`, type `Y` and press `Enter`.

---

### Method 2: Shutdown Commands by Port (Port 8501)
Use this if the server is running in the background or terminal is unresponsive.

#### Windows PowerShell:
```powershell
Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

#### Windows Command Prompt (CMD):
```cmd
for /f "tokens=5" %a in ('netstat -aon ^| findstr :8501') do taskkill /f /pid %a
```

#### Linux / macOS:
```bash
lsof -ti:8501 | xargs kill -9
# or
fuser -k 8501/tcp
```

---

### Method 3: Shutdown Commands by Process Name

#### Windows PowerShell:
```powershell
# Kill any streamlit process
Stop-Process -Name streamlit -Force -ErrorAction SilentlyContinue

# Or kill any python process running app.py
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like "*ui/app.py*" -or $_.CommandLine -like "*ui\app.py*" } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
```

#### Windows Command Prompt (CMD):
```cmd
taskkill /F /IM streamlit.exe
```

#### Linux / macOS:
```bash
pkill -f "streamlit run ui/app.py"
# or
pkill -f streamlit
```

---

## 6. Dashboard Restart One-Liners

### Windows PowerShell:
```powershell
Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }; python main.py --mode dashboard
```

### Linux / macOS:
```bash
lsof -ti:8501 | xargs kill -9 2>/dev/null; python main.py --mode dashboard
```

---

## 7. Pre-Launch Verification

Before launching the dashboard, you can verify that all 12 quantitative components, factor models, and data pipelines are fully operational:

```powershell
python -m unittest tests/test_all.py
```

---

## 8. Troubleshooting

- **Port Already in Use (`Port 8501 is already in use`)**:
  Execute the shutdown command for port 8501 above, or launch on a different port:
  ```bash
  streamlit run ui/app.py --server.port 8502
  ```
- **Mobile Access Over Local Network (LAN)**:
  To view the dashboard on a smartphone, tablet, or secondary display connected to the same Wi-Fi:
  ```bash
  streamlit run ui/app.py --server.address 0.0.0.0 --server.port 8501
  ```
  Then navigate to `http://<your-machine-local-ip>:8501` on your mobile device.
- **Display Scaling & Viewport Testing**:
  If testing layout responsiveness across simulated devices on desktop:
  - Press `F12` in Chrome/Edge/Firefox to open Developer Tools.
  - Press `Ctrl + Shift + M` (`Cmd + Shift + M` on macOS) to activate Responsive Device Toolbar.
  - Select preset dimensions (e.g. *iPhone 14 Pro*, *iPad Air*, *Nest Hub*, or *4K Ultra HD*).
  - The dashboard CSS automatically triggers adaptive grids (`.bbg-kpi-grid`, `.bbg-metrics-deck`) and chart auto-stacking.
- **UTF-8 Character Display Issues (Windows)**:
  If Bloomberg UI Unicode box characters render improperly in the terminal:
  ```powershell
  $env:PYTHONUTF8 = "1"
  python main.py --mode dashboard
  ```
- **Streamlit Command Not Found**:
  Use `python -m streamlit run ui/app.py` with your active Python interpreter.
- **Offline / Low Connectivity Mode**:
  If Yahoo Finance or remote public endpoints are blocked or slow, the data pipeline automatically falls back to the deterministic high-fidelity synthetic benchmark generator without crashing.
- **Additional System Context**:
  For comprehensive mathematics, factor weighting tables, contract specs, and market microstructure, refer to [`CONTEXT.md`](CONTEXT.md) and [`README.md`](README.md).

---

## 9. 100% Free Cloud Hosting (Streamlit Community Cloud)

Project MOO can be hosted **100% free forever** on Streamlit Community Cloud with **no credit card required, no trial periods, and automated CI/CD re-deployments on Git push**.

### Step-by-Step Deployment:

1. **Initialize & Push Git Repository to GitHub:**
   ```bash
   git remote add origin https://github.com/<your-username>/moo.git
   git branch -M main
   git push -u origin main
   ```

2. **Connect Streamlit Community Cloud:**
   - Navigate to [share.streamlit.io](https://share.streamlit.io) and sign in with your GitHub account.
   - Click **"New app"**.
   - Set **Repository:** `<your-username>/moo`
   - Set **Branch:** `main`
   - Set **Main file path:** `ui/app.py`
   - Set **App URL (optional):** Choose your custom subdomain (e.g. `project-moo.streamlit.app`).
   - Click **Deploy!**

3. **Runtime Configuration & Cloud Optimization:**
   - **Pre-configured Theme & Server:** Included in `.streamlit/config.toml` (enforces Bloomberg terminal pure black background `#000000`, amber accent `#ff9900`, monospace font, and headless execution).
   - **Parquet Support:** `pyarrow>=14.0.0` is specified in `requirements.txt` to enable high-speed parquet parsing on Debian cloud containers.
   - **Continuous Live Market Updates:** The hosted dashboard connects to Yahoo Finance directly with a 5-minute cache TTL (`ttl=300`), pulling fresh price action whenever users interact with the dashboard.
   - **Zero-Downtime Continuous Deployment:** Any commit pushed to your GitHub repository automatically triggers an instantaneous build and hot-reload on Streamlit Community Cloud.
