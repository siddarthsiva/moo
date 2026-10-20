"""
Project MOO - Global Configuration & Bovine Commodity Specifications.
Contains contract specifications, free data sources, factor weights, and risk settings.
100% Free & Open-Source Stack.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Any

# Root Directory Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data_cache")
os.makedirs(DATA_DIR, exist_ok=True)

# -------------------------------------------------------------------------
# CME / ICE Commodity Contract Specifications
# -------------------------------------------------------------------------
@dataclass
class CommoditySpec:
    symbol: str             # Yahoo Finance / CME ticker
    name: str               # Human-readable name
    category: str           # Bovine, Feed, Macro, Competitor
    contract_size: int      # Standard contract size in units (e.g. 40,000 lbs)
    unit: str               # lbs, bushels, barrels, index
    point_value: float      # $ value per 1.00 full price point move
    tick_size: float        # Minimum price fluctuation
    tick_value: float       # $ value of minimum price tick
    exchange: str           # CME, CBOT, NYMEX, ICE
    margin_initial: float   # Typical maintenance margin ($ / contract)

COMMODITY_SPECS: Dict[str, CommoditySpec] = {
    "LE=F": CommoditySpec(
        symbol="LE=F",
        name="Live Cattle Futures",
        category="Bovine",
        contract_size=40_000,
        unit="lbs (cents/lb or $/cwt)",
        point_value=400.0,       # 1 cent/lb = $400 / contract ($1/cwt = $400)
        tick_size=0.025,         # 0.025 cents/lb
        tick_value=10.0,         # $10.00
        exchange="CME",
        margin_initial=2200.0,
    ),
    "GF=F": CommoditySpec(
        symbol="GF=F",
        name="Feeder Cattle Futures",
        category="Bovine",
        contract_size=50_000,
        unit="lbs (cents/lb or $/cwt)",
        point_value=500.0,       # 1 cent/lb = $500 / contract ($1/cwt = $500)
        tick_size=0.025,
        tick_value=12.50,
        exchange="CME",
        margin_initial=3000.0,
    ),
    "ZC=F": CommoditySpec(
        symbol="ZC=F",
        name="Corn Futures",
        category="Feed",
        contract_size=5_000,
        unit="bushels (cents/bushel)",
        point_value=50.0,        # 1 cent/bu = $50 ($1/bu = $5000)
        tick_size=0.25,
        tick_value=12.50,
        exchange="CBOT",
        margin_initial=1800.0,
    ),
    "ZM=F": CommoditySpec(
        symbol="ZM=F",
        name="Soybean Meal Futures",
        category="Feed",
        contract_size=100,
        unit="short tons ($/ton)",
        point_value=100.0,
        tick_size=0.10,
        tick_value=10.0,
        exchange="CBOT",
        margin_initial=2000.0,
    ),
    "HE=F": CommoditySpec(
        symbol="HE=F",
        name="Lean Hogs Futures",
        category="Competitor",
        contract_size=40_000,
        unit="lbs (cents/lb)",
        point_value=400.0,
        tick_size=0.025,
        tick_value=10.0,
        exchange="CME",
        margin_initial=2100.0,
    ),
    "DC=F": CommoditySpec(
        symbol="DC=F",
        name="Class III Milk Futures",
        category="Dairy",
        contract_size=200_000,
        unit="lbs ($/cwt)",
        point_value=2000.0,
        tick_size=0.01,
        tick_value=20.0,
        exchange="CME",
        margin_initial=1500.0,
    ),
    "CL=F": CommoditySpec(
        symbol="CL=F",
        name="Crude Oil Futures",
        category="Macro",
        contract_size=1_000,
        unit="barrels ($/bbl)",
        point_value=1000.0,
        tick_size=0.01,
        tick_value=10.0,
        exchange="NYMEX",
        margin_initial=6000.0,
    ),
    "DX-Y.NYB": CommoditySpec(
        symbol="DX-Y.NYB",
        name="US Dollar Index",
        category="Macro",
        contract_size=1_000,
        unit="index pts",
        point_value=1000.0,
        tick_size=0.005,
        tick_value=5.0,
        exchange="ICE",
        margin_initial=2500.0,
    ),
}

# -------------------------------------------------------------------------
# Cattle Crush & Feedlot Economics Parameters
# -------------------------------------------------------------------------
# Standard Feedlot Transformation Model:
# 1 Live Slaughter Steer (~1,300 lbs / 13.0 cwt) =
#   7.5 cwt Feeder Calf (~750 lbs) + 50 Bushels of Corn + Yardage/Overhead
CATTLE_CRUSH_CONFIG = {
    "live_weight_cwt": 13.0,       # 1,300 lbs finished steer
    "feeder_weight_cwt": 7.5,      # 750 lbs feeder calf
    "corn_bushels_per_head": 50.0, # 50 bu of corn to finish
    "yardage_overhead_usd": 85.0,  # Fixed vet, labor, yardage fee per head
    "feeder_live_normal_ratio": 1.35, # Normal Feeder/Live price parity ratio
}

# -------------------------------------------------------------------------
# Multi-Factor Weight Configuration (Composite Alpha)
# -------------------------------------------------------------------------
DEFAULT_FACTOR_WEIGHTS = {
    "crush_margin": 0.25,     # Feedlot Crush Margin & Spread mean-reversion
    "cot_sentiment": 0.20,    # Commercial Hedger smart-money vs Speculator crowding
    "seasonality": 0.15,      # Monthly/Weekly seasonal biological cycle
    "macro_drought": 0.15,    # US Drought severity & DXY dollar export pressure
    "technical_trend": 0.15,  # Kalman trend, ATR breakout, momentum
    "ml_ensemble": 0.10,      # Machine Learning Ensemble forward probability
}

# -------------------------------------------------------------------------
# ENSO (El Niño-Southern Oscillation) & Super El Niño Climatology Model
# -------------------------------------------------------------------------
# An intense El Niño warm event (ONI >= +2.0°C) radically alters cattle fundamentals:
# 1. Southern Plains pasture moisture surges, breaking drought and triggering aggressive heifer retention (bullish supply shock).
# 2. Corn Belt experiences cooler, non-drought conditions, producing bumper corn crops (low feed prices -> higher feedlot margins).
# 3. Autumn calf run price dip is dampened as calves graze winter wheat rather than entering auction rings.
# 4. Severe winter storms and wet muddy feedlots decrease Average Daily Gain (ADG), delaying marketings.
# 5. Australian beef herd liquidates under extreme drought, creating subsequent global supply vacuums.
ENSO_CONFIG = {
    "active_regime": "super_elnino",       # Default active regime: "super_elnino", "elnino", "neutral", "lanina"
    "oni_anomaly_super_elnino": 2.3,       # 2026 Super El Niño Sea Surface Temp Anomaly (°C)
    "threshold_super_elnino": 2.0,         # ONI >= 2.0°C defines Super El Niño
    "threshold_elnino": 0.5,               # ONI >= 0.5°C defines El Niño
    "threshold_lanina": -0.5,              # ONI <= -0.5°C defines La Niña
    "heifer_retention_alpha_boost": 0.35,  # Structural bullish supply withdrawal for LE & GF
    "autumn_calf_run_damping": 0.75,       # Mutes seasonal feeder calf selloff (calves stay on wheat)
    "winter_storm_mud_boost": 0.20,        # Exacerbates winter storm/mud delivery lag
    "feeder_live_parity_elnino": 1.42,     # Parity elevates from 1.35 to 1.42 with cheap corn
    "feedlot_mud_yardage_drag_usd": 12.0,  # Additional yardage/overhead per head due to mud ($85 -> $97)
    "atr_stop_loss_mult_elnino": 2.8,      # Wider stops to withstand weather headline volatility
}

# Factor Weights Tuned for Super El Niño Climatology Regime
SUPER_ELNINO_FACTOR_WEIGHTS = {
    "crush_margin": 0.25,     # Feedlot margins expand as corn plunges
    "cot_sentiment": 0.15,    # Commercial positioning confirmation
    "seasonality": 0.20,      # Modulated seasonal curve (damped autumn calf run)
    "macro_drought": 0.25,    # Elevated weight: ENSO moisture, heifer retention & export shock
    "technical_trend": 0.10,  # Lower weight: trend followers get whipsawed by weather jumps
    "ml_ensemble": 0.05,      # ML ensemble probability
}

# -------------------------------------------------------------------------
# Strategy & Signal Thresholds
# -------------------------------------------------------------------------
STRATEGY_CONFIG = {
    "signal_threshold_strong_long": 0.35,
    "signal_threshold_weak_long": 0.15,
    "signal_threshold_weak_short": -0.15,
    "signal_threshold_strong_short": -0.35,
    "min_holding_period_days": 3,
    "spread_trade_zscore_threshold": 1.75, # For Feeder vs Live pairs trading
}

# -------------------------------------------------------------------------
# Institutional Risk Management Parameters
# -------------------------------------------------------------------------
RISK_CONFIG = {
    "initial_capital": 100_000.0,
    "target_annual_volatility": 0.15,  # 15% Annualized target vol
    "max_portfolio_leverage": 2.5,
    "max_position_weight": 0.60,       # Max single asset exposure
    "atr_stop_loss_mult": 2.5,         # Stop Loss = 2.5 * ATR(14)
    "atr_take_profit_mult": 4.5,       # Take Profit = 4.5 * ATR(14)
    "trailing_stop_activation": 2.0,   # Activate trailing stop after 2.0 * ATR in profit
    "slippage_bps": 2.5,               # 2.5 bps slippage per trade
    "commission_per_contract": 2.50,   # $2.50 per round-turn contract fee
    "max_drawdown_soft_limit": 0.08,   # Halve size at 8% DD
    "max_drawdown_hard_circuit": 0.15, # Liquidate to cash at 15% DD
}

# -------------------------------------------------------------------------
# Free Public Data Endpoints
# -------------------------------------------------------------------------
FREE_DATA_SOURCES = {
    "yfinance_active": True,
    "cftc_cot_url": "https://www.cftc.gov/files/dea/history/deacot{year}.zip",
    "cftc_cme_code_live_cattle": "057642",
    "cftc_cme_code_feeder_cattle": "061641",
    "drought_monitor_url": "https://droughtmonitor.unl.edu/DmData/DataDownload/ComprehensiveStatistics.aspx",
    "fred_api_free_url": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=",
    "noaa_oni_url": "https://origin.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/ONI_v5.php",
    "noaa_psl_oni_url": "https://psl.noaa.gov/data/correlation/oni.data",
    "fred_series": {
        "cpi_beef": "CUUR0000SEFD01",     # CPI: Beef and Veal
        "dxy_broad": "DTWEXBGS",          # Nominal Broad US Dollar Index
        "cattle_headcount": "APU0000703112", # US Retail Beef Chuck Price
    }
}

# -------------------------------------------------------------------------
# Global Bovine Country Production & Breed Demographics
# -------------------------------------------------------------------------
GLOBAL_CATTLE_PRODUCERS = {
    "USA": {
        "name": "United States",
        "iso": "USA",
        "lat": 37.0902,
        "lon": -95.7129,
        "cattle_herd_million_head": 87.2,
        "annual_beef_production_1000mt": 12150,
        "primary_breeds": ["Black Angus", "Red Angus", "Hereford", "Charolais Cross", "Brangus"],
        "finish_type_pct": {"Grain-fed Feedlot": 82, "Pasture Grass-fed": 11, "Dairy Cull": 7},
        "avg_carcass_weight_kg": 405.0,
        "avg_carcass_weight_lbs": 892.8,
        "supply_status": "HERD_CONTRACTION",
        "supply_status_desc": "73-Year Inventory Low (Severe Southern Plains Drought Culling)",
        "demand_status": "HYPER_DEMAND",
        "demand_status_desc": "Record Domestic Retail Beef Prices; Extreme Deficit in 90CL Lean Trimmings",
        "trade_role": "TOP_EXPORTER_AND_IMPORTER",
        "annual_exports_1000mt": 1380,
        "annual_imports_1000mt": 1720,
        "top_export_markets": ["Japan", "South Korea", "China", "Mexico", "Canada"],
        "top_import_sources": ["Australia", "Canada", "Brazil", "New Zealand", "Mexico"],
        "fmd_status": "FMD_FREE_WITHOUT_VACCINATION",
        "bse_risk": "NEGLIGIBLE_RISK",
        "quarantine_alerts": "Screwworm southern border surveillance; Dairy-to-Beef H5N1 cross-species monitoring."
    },
    "BRA": {
        "name": "Brazil",
        "iso": "BRA",
        "lat": -14.2350,
        "lon": -51.9253,
        "cattle_herd_million_head": 232.0,
        "annual_beef_production_1000mt": 11200,
        "primary_breeds": ["Nelore (Zebu Bos indicus)", "Braford", "Brangus", "Angus Tropical", "Senepol"],
        "finish_type_pct": {"Pasture Grass-fed": 76, "Grain-fed Feedlot": 18, "Pastoral Cull": 6},
        "avg_carcass_weight_kg": 272.0,
        "avg_carcass_weight_lbs": 599.6,
        "supply_status": "LIQUIDATION_GLUT",
        "supply_status_desc": "Peak Female Slaughter Cycle; Record Packing Plant Throughput & Export Surplus",
        "demand_status": "ROBUST_IMPORT_DEMAND_SERVICER",
        "demand_status_desc": "Dominant Global Supplier to China and Middle East; Currency Depreciation Boosts Margin",
        "trade_role": "LARGEST_GLOBAL_EXPORTER",
        "annual_exports_1000mt": 3350,
        "annual_imports_1000mt": 55,
        "top_export_markets": ["China", "United States", "Chile", "United Arab Emirates", "Egypt", "Hong Kong"],
        "top_import_sources": ["Uruguay", "Argentina"],
        "fmd_status": "FMD_FREE_TRANSITION_WITHOUT_VACCINATION",
        "bse_risk": "NEGLIGIBLE_RISK",
        "quarantine_alerts": "Transitioning nationwide to FMD-free without vaccination; strict China traceability protocols."
    },
    "AUS": {
        "name": "Australia",
        "iso": "AUS",
        "lat": -25.2744,
        "lon": 133.7751,
        "cattle_herd_million_head": 28.8,
        "annual_beef_production_1000mt": 2480,
        "primary_breeds": ["Brahman (Northern Live Export)", "Black Angus", "Wagyu (F1-Fullblood)", "Hereford", "Santa Gertrudis"],
        "finish_type_pct": {"Pasture Grass-fed": 58, "Grain-fed Feedlot": 38, "Live Export Pastoral": 4},
        "avg_carcass_weight_kg": 318.0,
        "avg_carcass_weight_lbs": 701.0,
        "supply_status": "EXPANSION_SURPLUS",
        "supply_status_desc": "Herd Rebuilding Complete; Heavy Slaughter Weights and Record Chilled/Frozen Shipments",
        "demand_status": "PREMIUM_EXPORT_DEMAND",
        "demand_status_desc": "Surging US demand for 90CL lean manufacturing beef; High-tier Wagyu to Japan/Korea",
        "trade_role": "TOP_GLOBAL_EXPORTER",
        "annual_exports_1000mt": 1850,
        "annual_imports_1000mt": 20,
        "top_export_markets": ["United States", "China", "Japan", "South Korea", "Indonesia (Live Feeder)"],
        "top_import_sources": ["New Zealand"],
        "fmd_status": "FMD_FREE_WITHOUT_VACCINATION",
        "bse_risk": "NEGLIGIBLE_RISK",
        "quarantine_alerts": "Strict biosecurity buffer for Northern Territory live export to Indonesia & Vietnam."
    },
    "IND": {
        "name": "India",
        "iso": "IND",
        "lat": 20.5937,
        "lon": 78.9629,
        "cattle_herd_million_head": 305.0, # Combined Bovine + Water Buffalo
        "annual_beef_production_1000mt": 4350,
        "primary_breeds": ["Murrah Water Buffalo (Bubalus bubalis)", "Nili-Ravi Carabeef", "Zebu Indigenous Dairy Cull"],
        "finish_type_pct": {"Agricultural Byproduct Forage": 85, "Dairy Cull": 15, "Grain-fed Feedlot": 0},
        "avg_carcass_weight_kg": 142.0,
        "avg_carcass_weight_lbs": 313.0,
        "supply_status": "STABLE_EQUILIBRIUM",
        "supply_status_desc": "Continuous Halal Carabeef Processing from Massive Dairy Herd Replacements",
        "demand_status": "HIGH_PRICE_SENSITIVE_DEMAND",
        "demand_status_desc": "Lowest-cost boneless frozen red meat for Southeast Asia, Middle East, and North Africa",
        "trade_role": "TOP_GLOBAL_EXPORTER",
        "annual_exports_1000mt": 1420,
        "annual_imports_1000mt": 0,
        "top_export_markets": ["Vietnam", "Malaysia", "Egypt", "Indonesia", "Saudi Arabia", "Iraq"],
        "top_import_sources": [],
        "fmd_status": "FMD_ENDEMIC_CONTROL_ZONE",
        "bse_risk": "NEGLIGIBLE_RISK",
        "quarantine_alerts": "Strict thermal deboning & Halal sanitary certificate requirements for Middle East entry."
    },
    "ARG": {
        "name": "Argentina",
        "iso": "ARG",
        "lat": -38.4161,
        "lon": -63.6167,
        "cattle_herd_million_head": 52.8,
        "annual_beef_production_1000mt": 3150,
        "primary_breeds": ["Aberdeen Angus", "Hereford", "Braford", "Brangus", "Shorthorn"],
        "finish_type_pct": {"Pampas Grass-fed": 64, "Grain-fed Feedlot": 30, "Pastoral Cull": 6},
        "avg_carcass_weight_kg": 235.0,
        "avg_carcass_weight_lbs": 518.0,
        "supply_status": "HERD_CONTRACTION",
        "supply_status_desc": "Severe 2023/24 Pampas Drought Liquidations followed by Deregulation Recovery",
        "demand_status": "DOMESTIC_SQUEEZE_EXPORT_PUSH",
        "demand_status_desc": "High domestic inflation lowers local consumption; Exporters pivot aggressively to China and EU",
        "trade_role": "TOP_GLOBAL_EXPORTER",
        "annual_exports_1000mt": 910,
        "annual_imports_1000mt": 10,
        "top_export_markets": ["China", "European Union (Hilton Quota)", "Israel", "United States", "Chile"],
        "top_import_sources": ["Uruguay"],
        "fmd_status": "FMD_FREE_WITH_VACCINATION_NORTH_WITHOUT_SOUTH",
        "bse_risk": "NEGLIGIBLE_RISK",
        "quarantine_alerts": "DEX export withholding tax rate shifts; Patagonia designated FMD-free without vaccination."
    },
    "CHN": {
        "name": "China",
        "iso": "CHN",
        "lat": 35.8617,
        "lon": 104.1954,
        "cattle_herd_million_head": 101.5,
        "annual_beef_production_1000mt": 7500,
        "primary_breeds": ["Qinchuan Yellow Cattle", "Luxi Cattle", "Simmental Cross", "Yanbian", "Dairy Holstein Cull"],
        "finish_type_pct": {"Smallholder Forage": 52, "Feedlot Finished": 36, "Dairy Cull": 12},
        "avg_carcass_weight_kg": 195.0,
        "avg_carcass_weight_lbs": 429.9,
        "supply_status": "DOMESTIC_MARGIN_CRISIS",
        "supply_status_desc": "Domestic Cattle Prices Plunge Below Production Cost; Feedlot Operators Liquidating Calves",
        "demand_status": "SUPER_IMPORTER_STEADY",
        "demand_status_desc": "Consuming over 30% of Global Exported Beef; Value-seeking shift towards Brazil frozen cuts",
        "trade_role": "WORLD_LARGEST_IMPORTER",
        "annual_exports_1000mt": 25,
        "annual_imports_1000mt": 3650,
        "top_export_markets": ["Hong Kong", "Macau"],
        "top_import_sources": ["Brazil", "Argentina", "Uruguay", "Australia", "New Zealand", "United States"],
        "fmd_status": "FMD_ZONED_CONTROL",
        "bse_risk": "NEGLIGIBLE_RISK",
        "quarantine_alerts": "GACC approval audits for Brazilian & Australian meat packing establishments."
    },
    "JPN": {
        "name": "Japan",
        "iso": "JPN",
        "lat": 36.2048,
        "lon": 138.2529,
        "cattle_herd_million_head": 3.9,
        "annual_beef_production_1000mt": 475,
        "primary_breeds": ["Japanese Black Wagyu (Kuroge Washu)", "Japanese Brown (Akage)", "Holstein Dairy Cull", "F1 Cross"],
        "finish_type_pct": {"Ultra-High Grain Stall Feedlot": 68, "Dairy Cull Finishing": 32, "Pasture Grass": 0},
        "avg_carcass_weight_kg": 490.0,
        "avg_carcass_weight_lbs": 1080.2,
        "supply_status": "STABLE_EQUILIBRIUM",
        "supply_status_desc": "Ultra-High Feed Costs for 650-Day Wagyu Finishing; High Carcass Values Offset Rations",
        "demand_status": "PREMIUM_SELECTIVE_DEMAND",
        "demand_status_desc": "High demand for grain-fed US short plate (gyudon bowls) & Australian chilled Angus",
        "trade_role": "TOP_GLOBAL_IMPORTER",
        "annual_exports_1000mt": 9,
        "annual_imports_1000mt": 720,
        "top_export_markets": ["United States", "Hong Kong", "Singapore", "Taiwan"],
        "top_import_sources": ["Australia", "United States", "Canada", "New Zealand"],
        "fmd_status": "FMD_FREE_WITHOUT_VACCINATION",
        "bse_risk": "NEGLIGIBLE_RISK",
        "quarantine_alerts": "Strict age-at-slaughter verification and zero-tolerance pesticide residue limits."
    },
    "EU": {
        "name": "European Union",
        "iso": "EU",
        "lat": 50.8503,
        "lon": 4.3517,
        "cattle_herd_million_head": 74.5,
        "annual_beef_production_1000mt": 6450,
        "primary_breeds": ["Charolais", "Limousin", "Simmental", "Belgian Blue", "Irish Angus", "Holstein Friesian"],
        "finish_type_pct": {"Intensive Young Bull Bull-pens": 45, "Dairy Cull": 35, "Grass-fed Pasture": 20},
        "avg_carcass_weight_kg": 345.0,
        "avg_carcass_weight_lbs": 760.6,
        "supply_status": "STRUCTURAL_DECLINE",
        "supply_status_desc": "EU Green Deal, Nitrogen Emission Caps, and Farm Succession Deficits Reducing Herds",
        "demand_status": "MATURE_STABLE_DEMAND",
        "demand_status_desc": "Strict non-hormone treated cattle (NHTC) demand; Deforestation-free EUDR regulations",
        "trade_role": "BALANCED_SPECIALTY_TRADER",
        "annual_exports_1000mt": 690,
        "annual_imports_1000mt": 360,
        "top_export_markets": ["United Kingdom", "Israel", "Turkey", "Switzerland", "Ghana"],
        "top_import_sources": ["United Kingdom", "Brazil", "Argentina", "Uruguay", "Australia"],
        "fmd_status": "FMD_FREE_WITHOUT_VACCINATION",
        "bse_risk": "NEGLIGIBLE_RISK",
        "quarantine_alerts": "EUDR compliance satellite geolocation verification required for imported beef."
    },
    "NZL": {
        "name": "New Zealand",
        "iso": "NZL",
        "lat": -40.9006,
        "lon": 174.8860,
        "cattle_herd_million_head": 9.6,
        "annual_beef_production_1000mt": 725,
        "primary_breeds": ["Angus", "Hereford", "Dairy-Beef Kiwi Cross (Friesian-Jersey)", "Wagyu Cross"],
        "finish_type_pct": {"100% Pasture Grass-fed": 94, "Dairy Cull Grass Finish": 6, "Grain Feedlot": 0},
        "avg_carcass_weight_kg": 298.0,
        "avg_carcass_weight_lbs": 657.0,
        "supply_status": "STABLE_EQUILIBRIUM",
        "supply_status_desc": "Pasture-driven seasonal slaughter peak; High reliance on Spring flush",
        "demand_status": "EXPORT_LEAN_BEEF_HUB",
        "demand_status_desc": "Massive supplier of lean 90/95CL processing beef to US burger quick-service chains",
        "trade_role": "TOP_GLOBAL_EXPORTER",
        "annual_exports_1000mt": 680,
        "annual_imports_1000mt": 15,
        "top_export_markets": ["United States", "China", "Japan", "Canada", "South Korea"],
        "top_import_sources": ["Australia"],
        "fmd_status": "FMD_FREE_WITHOUT_VACCINATION",
        "bse_risk": "NEGLIGIBLE_RISK",
        "quarantine_alerts": "Mycoplasma bovis eradication monitoring program in final surveillance stages."
    },
    "EGY": {
        "name": "Egypt",
        "iso": "EGY",
        "lat": 26.8206,
        "lon": 30.8025,
        "cattle_herd_million_head": 7.8,
        "annual_beef_production_1000mt": 390,
        "primary_breeds": ["Baladi Cattle", "Saidi", "Water Buffalo Cull"],
        "finish_type_pct": {"Nile Valley Forage": 82, "Small Feedlot": 18, "Pasture": 0},
        "avg_carcass_weight_kg": 210.0,
        "avg_carcass_weight_lbs": 463.0,
        "supply_status": "CRITICAL_DEFICIT",
        "supply_status_desc": "Severe Domestic Feed Shortage and Currency Devaluation Curbing Domestic Herd",
        "demand_status": "SURGING_IMPORT_DEMAND",
        "demand_status_desc": "Major Importer of Live Cattle (Brazil, Colombia, Sudan) and Frozen Boneless Carabeef (India)",
        "trade_role": "TOP_GLOBAL_IMPORTER",
        "annual_exports_1000mt": 2,
        "annual_imports_1000mt": 480,
        "top_export_markets": [],
        "top_import_sources": ["India (Carabeef)", "Brazil (Beef & Live Cattle)", "Colombia (Live)", "Sudan (Live)"],
        "fmd_status": "FMD_ENDEMIC",
        "bse_risk": "NEGLIGIBLE_RISK",
        "quarantine_alerts": "Port quarantine quarantine stations at Alexandria and Damietta for imported feeder bulls."
    },
    "IDN": {
        "name": "Indonesia",
        "iso": "IDN",
        "lat": -0.7893,
        "lon": 113.9213,
        "cattle_herd_million_head": 18.2,
        "annual_beef_production_1000mt": 450,
        "primary_breeds": ["Ongole Grade (PO)", "Bali Cattle (Bos javanicus)", "Madura Cattle"],
        "finish_type_pct": {"Smallholder Forage": 70, "Commercial Feedlot Finished": 30, "Pasture": 0},
        "avg_carcass_weight_kg": 185.0,
        "avg_carcass_weight_lbs": 407.8,
        "supply_status": "CHRONIC_DEFICIT",
        "supply_status_desc": "Domestic Smallholders Unable to Meet 280M Population Demand; Dependent on Live Feeders",
        "demand_status": "HYPER_DEMAND_LIVE_FEEDERS",
        "demand_status_desc": "World's largest destination for Australian live feeder steers finished in West Java feedlots",
        "trade_role": "TOP_LIVE_CATTLE_IMPORTER",
        "annual_exports_1000mt": 0,
        "annual_imports_1000mt": 340, # Plus 500k-700k live cattle head
        "top_export_markets": [],
        "top_import_sources": ["Australia (Live Feeders & Boxed Beef)", "India (Frozen Carabeef)", "Brazil", "USA"],
        "fmd_status": "FMD_ACTIVE_CONTROL_VACCINATION",
        "bse_risk": "NEGLIGIBLE_RISK",
        "quarantine_alerts": "LSD (Lumpy Skin Disease) and FMD pre-export testing protocol with Australia."
    }
}

# -------------------------------------------------------------------------
# Specialized Livestock Carrier Fleet (Real Maritime AIS Tracking)
# -------------------------------------------------------------------------
LIVESTOCK_CARRIER_FLEET = [
    {
        "name": "MV Ocean Drover",
        "imo": 9232852,
        "mmsi": 538002634,
        "flag": "Marshall Islands",
        "built_year": 2002,
        "dwt": 12892,
        "deck_area_sqm": 24115,
        "cattle_head_capacity": 20000,
        "ventilation_air_changes_per_hr": 75,
        "speed_service_knots": 17.5,
        "origin_port": "Darwin (AUS)",
        "destination_port": "Jakarta (IDN)",
        "cargo_manifest": "18,450 Head Northern Australian Brahman Steers",
        "cargo_val_usd": 22_140_000,
        "current_lat": -10.824,
        "current_lon": 123.412,
        "current_speed": 16.2,
        "current_heading": 298,
        "status": "UNDERWAY",
        "choke_point_status": "Approaching Lombok Strait Corridor",
        "departure_date": "2026-10-14",
        "eta_date": "2026-10-19",
        "fodder_days_remaining": 14,
        "water_generation_liters_day": 350000,
        "heat_stress_index": "NOMINAL (THI 72)"
    },
    {
        "name": "MV Nada",
        "imo": 9005429,
        "mmsi": 352002441,
        "flag": "Panama",
        "built_year": 1993,
        "dwt": 26112,
        "deck_area_sqm": 28400,
        "cattle_head_capacity": 22000,
        "ventilation_air_changes_per_hr": 68,
        "speed_service_knots": 15.8,
        "origin_port": "Vila do Conde (BRA)",
        "destination_port": "Alexandria (EGY)",
        "cargo_manifest": "21,100 Head Brazilian Nelore Yearling Bulls",
        "cargo_val_usd": 24_265_000,
        "current_lat": 31.850,
        "current_lon": 28.450,
        "current_speed": 14.9,
        "current_heading": 105,
        "status": "UNDERWAY",
        "choke_point_status": "Eastern Mediterranean Transit Zone",
        "departure_date": "2026-10-02",
        "eta_date": "2026-10-18",
        "fodder_days_remaining": 8,
        "water_generation_liters_day": 420000,
        "heat_stress_index": "NOMINAL (THI 69)"
    },
    {
        "name": "MV Al Kuwait",
        "imo": 9590931,
        "mmsi": 447000180,
        "flag": "Kuwait",
        "built_year": 2013,
        "dwt": 16841,
        "deck_area_sqm": 22500,
        "cattle_head_capacity": 17500,
        "ventilation_air_changes_per_hr": 80,
        "speed_service_knots": 16.5,
        "origin_port": "Montevideo (URY)",
        "destination_port": "Jeddah (SAU)",
        "cargo_manifest": "16,800 Head Uruguayan Angus-Hereford Cross Feeders",
        "cargo_val_usd": 19_320_000,
        "current_lat": 12.580,
        "current_lon": 43.320,
        "current_speed": 15.8,
        "current_heading": 328,
        "status": "CHOKE_POINT_ALERT",
        "choke_point_status": "Bab-el-Mandeb / Southern Red Sea HRA Corridor",
        "departure_date": "2026-09-28",
        "eta_date": "2026-10-21",
        "fodder_days_remaining": 11,
        "water_generation_liters_day": 380000,
        "heat_stress_index": "ELEVATED (THI 79 - High Sea Surface Temps)"
    },
    {
        "name": "MV Brahman Express",
        "imo": 9238416,
        "mmsi": 564536000,
        "flag": "Singapore",
        "built_year": 2002,
        "dwt": 5160,
        "deck_area_sqm": 7200,
        "cattle_head_capacity": 4200,
        "ventilation_air_changes_per_hr": 85,
        "speed_service_knots": 18.0,
        "origin_port": "Broome (AUS)",
        "destination_port": "Haiphong (VNM)",
        "cargo_manifest": "3,950 Head Australian Brahman Feeder Bulls",
        "cargo_val_usd": 4_740_000,
        "current_lat": 16.420,
        "current_lon": 109.850,
        "current_speed": 17.2,
        "current_heading": 345,
        "status": "UNDERWAY",
        "choke_point_status": "South China Sea Transit Corridor",
        "departure_date": "2026-10-11",
        "eta_date": "2026-10-18",
        "fodder_days_remaining": 9,
        "water_generation_liters_day": 120000,
        "heat_stress_index": "NOMINAL (THI 74)"
    },
    {
        "name": "MV Ocean Shearer",
        "imo": 9632882,
        "mmsi": 357321000,
        "flag": "Panama",
        "built_year": 2016,
        "dwt": 16211,
        "deck_area_sqm": 23500,
        "cattle_head_capacity": 20000,
        "ventilation_air_changes_per_hr": 78,
        "speed_service_knots": 17.0,
        "origin_port": "São Sebastião (BRA)",
        "destination_port": "Mersin (TUR)",
        "cargo_manifest": "19,200 Head Brazilian Feedlot Cross Steers",
        "cargo_val_usd": 22_080_000,
        "current_lat": 35.850,
        "current_lon": 14.620,
        "current_speed": 16.4,
        "current_heading": 85,
        "status": "UNDERWAY",
        "choke_point_status": "Sicily Channel / Central Mediterranean Transit",
        "departure_date": "2026-10-04",
        "eta_date": "2026-10-20",
        "fodder_days_remaining": 10,
        "water_generation_liters_day": 410000,
        "heat_stress_index": "NOMINAL (THI 66)"
    },
    {
        "name": "MV Gudali Express",
        "imo": 9668049,
        "mmsi": 565158000,
        "flag": "Singapore",
        "built_year": 2014,
        "dwt": 4800,
        "deck_area_sqm": 6900,
        "cattle_head_capacity": 4000,
        "ventilation_air_changes_per_hr": 84,
        "speed_service_knots": 17.5,
        "origin_port": "Townsville (AUS)",
        "destination_port": "Surabaya (IDN)",
        "cargo_manifest": "3,820 Head Northern Queensland Feeder Steers",
        "cargo_val_usd": 4_584_000,
        "current_lat": -9.150,
        "current_lon": 118.420,
        "current_speed": 16.8,
        "current_heading": 282,
        "status": "UNDERWAY",
        "choke_point_status": "Savu Sea Corridor",
        "departure_date": "2026-10-13",
        "eta_date": "2026-10-18",
        "fodder_days_remaining": 12,
        "water_generation_liters_day": 115000,
        "heat_stress_index": "NOMINAL (THI 73)"
    },
    {
        "name": "MV Polaris 2",
        "imo": 9170248,
        "mmsi": 354674000,
        "flag": "Panama",
        "built_year": 1999,
        "dwt": 7200,
        "deck_area_sqm": 9800,
        "cattle_head_capacity": 5800,
        "ventilation_air_changes_per_hr": 70,
        "speed_service_knots": 14.5,
        "origin_port": "Cartagena (COL)",
        "destination_port": "Beirut (LBN)",
        "cargo_manifest": "5,400 Head Colombian Zebu Yearling Bulls",
        "cargo_val_usd": 5_940_000,
        "current_lat": 34.120,
        "current_lon": 32.850,
        "current_speed": 13.8,
        "current_heading": 92,
        "status": "UNDERWAY",
        "choke_point_status": "Levantine Sea Approach",
        "departure_date": "2026-09-30",
        "eta_date": "2026-10-18",
        "fodder_days_remaining": 6,
        "water_generation_liters_day": 160000,
        "heat_stress_index": "NOMINAL (THI 70)"
    },
    {
        "name": "MV Maysora",
        "imo": 8611142,
        "mmsi": 308696000,
        "flag": "Bahamas",
        "built_year": 1989,
        "dwt": 14350,
        "deck_area_sqm": 21000,
        "cattle_head_capacity": 15000,
        "ventilation_air_changes_per_hr": 65,
        "speed_service_knots": 15.0,
        "origin_port": "Midia (ROU)",
        "destination_port": "Tripoli (LBY)",
        "cargo_manifest": "12,800 Head European Simmental-Limousin Bulls",
        "cargo_val_usd": 15_360_000,
        "current_lat": 33.450,
        "current_lon": 15.200,
        "current_speed": 14.2,
        "current_heading": 240,
        "status": "UNDERWAY",
        "choke_point_status": "Gulf of Sidra Approach",
        "departure_date": "2026-10-12",
        "eta_date": "2026-10-18",
        "fodder_days_remaining": 7,
        "water_generation_liters_day": 290000,
        "heat_stress_index": "NOMINAL (THI 67)"
    },
    {
        "name": "MV Barkly Pearl",
        "imo": 9070773,
        "mmsi": 538008892,
        "flag": "Marshall Islands",
        "built_year": 1993,
        "dwt": 6800,
        "deck_area_sqm": 9200,
        "cattle_head_capacity": 5200,
        "ventilation_air_changes_per_hr": 72,
        "speed_service_knots": 15.2,
        "origin_port": "Darwin (AUS)",
        "destination_port": "Batangas (PHL)",
        "cargo_manifest": "4,900 Head Australian Pastoral Cattle",
        "cargo_val_usd": 5_635_000,
        "current_lat": 8.420,
        "current_lon": 122.150,
        "current_speed": 14.7,
        "current_heading": 352,
        "status": "UNDERWAY",
        "choke_point_status": "Sulu Sea Corridor",
        "departure_date": "2026-10-12",
        "eta_date": "2026-10-19",
        "fodder_days_remaining": 10,
        "water_generation_liters_day": 145000,
        "heat_stress_index": "NOMINAL (THI 75)"
    },
    {
        "name": "MV Spiridon",
        "imo": 7311329,
        "mmsi": 671804000,
        "flag": "Togo",
        "built_year": 1974,
        "dwt": 4500,
        "deck_area_sqm": 5800,
        "cattle_head_capacity": 3200,
        "ventilation_air_changes_per_hr": 60,
        "speed_service_knots": 12.5,
        "origin_port": "Cartagena (ESP)",
        "destination_port": "Algiers (DZA)",
        "cargo_manifest": "2,950 Head Spanish Young Bulls",
        "cargo_val_usd": 3_540_000,
        "current_lat": 37.100,
        "current_lon": 1.250,
        "current_speed": 11.9,
        "current_heading": 135,
        "status": "UNDERWAY",
        "choke_point_status": "Western Mediterranean Crossing",
        "departure_date": "2026-10-16",
        "eta_date": "2026-10-18",
        "fodder_days_remaining": 5,
        "water_generation_liters_day": 85000,
        "heat_stress_index": "NOMINAL (THI 65)"
    },
    {
        "name": "MV Finola",
        "imo": 9133496,
        "mmsi": 352001552,
        "flag": "Panama",
        "built_year": 1996,
        "dwt": 5600,
        "deck_area_sqm": 7600,
        "cattle_head_capacity": 4500,
        "ventilation_air_changes_per_hr": 74,
        "speed_service_knots": 15.0,
        "origin_port": "Tarragona (ESP)",
        "destination_port": "Misrata (LBY)",
        "cargo_manifest": "4,100 Head European Holstein/Charolais Cross",
        "cargo_val_usd": 4_920_000,
        "current_lat": 34.800,
        "current_lon": 13.900,
        "current_speed": 14.1,
        "current_heading": 155,
        "status": "UNDERWAY",
        "choke_point_status": "Malta Channel Transit",
        "departure_date": "2026-10-14",
        "eta_date": "2026-10-18",
        "fodder_days_remaining": 6,
        "water_generation_liters_day": 125000,
        "heat_stress_index": "NOMINAL (THI 68)"
    },
    {
        "name": "MV Shorthorn Express",
        "imo": 9166297,
        "mmsi": 564284000,
        "flag": "Singapore",
        "built_year": 1998,
        "dwt": 4200,
        "deck_area_sqm": 6100,
        "cattle_head_capacity": 3800,
        "ventilation_air_changes_per_hr": 82,
        "speed_service_knots": 16.8,
        "origin_port": "Broome (AUS)",
        "destination_port": "Belawan (IDN)",
        "cargo_manifest": "3,600 Head Western Australian Feeder Cattle",
        "cargo_val_usd": 4_140_000,
        "current_lat": 3.450,
        "current_lon": 99.850,
        "current_speed": 16.1,
        "current_heading": 305,
        "status": "CHOKE_POINT_ALERT",
        "choke_point_status": "Strait of Malacca Congestion Zone",
        "departure_date": "2026-10-11",
        "eta_date": "2026-10-18",
        "fodder_days_remaining": 8,
        "water_generation_liters_day": 110000,
        "heat_stress_index": "NOMINAL (THI 76)"
    },
    {
        "name": "MV Murray Express",
        "imo": 9186390,
        "mmsi": 564619000,
        "flag": "Singapore",
        "built_year": 2000,
        "dwt": 3900,
        "deck_area_sqm": 5700,
        "cattle_head_capacity": 3500,
        "ventilation_air_changes_per_hr": 80,
        "speed_service_knots": 16.5,
        "origin_port": "Wyndham (AUS)",
        "destination_port": "Kuching (MYS)",
        "cargo_manifest": "3,350 Head Kimberley Shorthorn Cross",
        "cargo_val_usd": 3_852_500,
        "current_lat": 0.450,
        "current_lon": 109.120,
        "current_speed": 15.6,
        "current_heading": 348,
        "status": "UNDERWAY",
        "choke_point_status": "Karimata Strait Corridor",
        "departure_date": "2026-10-13",
        "eta_date": "2026-10-19",
        "fodder_days_remaining": 9,
        "water_generation_liters_day": 105000,
        "heat_stress_index": "NOMINAL (THI 74)"
    },
    {
        "name": "MV Elevation M",
        "imo": 9253454,
        "mmsi": 355601000,
        "flag": "Panama",
        "built_year": 2003,
        "dwt": 5100,
        "deck_area_sqm": 7100,
        "cattle_head_capacity": 4100,
        "ventilation_air_changes_per_hr": 76,
        "speed_service_knots": 15.4,
        "origin_port": "Montevideo (URY)",
        "destination_port": "Damietta (EGY)",
        "cargo_manifest": "3,950 Head Uruguayan Grass Bulls",
        "cargo_val_usd": 4_542_500,
        "current_lat": 22.450,
        "current_lon": -35.200,
        "current_speed": 14.8,
        "current_heading": 62,
        "status": "UNDERWAY",
        "choke_point_status": "Mid-Atlantic Transatlantic Crossing",
        "departure_date": "2026-10-06",
        "eta_date": "2026-10-24",
        "fodder_days_remaining": 16,
        "water_generation_liters_day": 128000,
        "heat_stress_index": "NOMINAL (THI 71)"
    },
    {
        "name": "MV Angusland",
        "imo": 9324560,
        "mmsi": 636015782,
        "flag": "Liberia",
        "built_year": 2007,
        "dwt": 6200,
        "deck_area_sqm": 8500,
        "cattle_head_capacity": 4800,
        "ventilation_air_changes_per_hr": 78,
        "speed_service_knots": 15.6,
        "origin_port": "Porto Alegre (BRA)",
        "destination_port": "Beirut (LBN)",
        "cargo_manifest": "4,600 Head Braford-Angus Cross Feeder Bulls",
        "cargo_val_usd": 5_290_000,
        "current_lat": 36.120,
        "current_lon": -5.350,
        "current_speed": 13.9,
        "current_heading": 88,
        "status": "CHOKE_POINT_ALERT",
        "choke_point_status": "Strait of Gibraltar Choke Point Inbound",
        "departure_date": "2026-10-03",
        "eta_date": "2026-10-23",
        "fodder_days_remaining": 14,
        "water_generation_liters_day": 140000,
        "heat_stress_index": "NOMINAL (THI 68)"
    }
]

# -------------------------------------------------------------------------
# Industry Cost Breakdown & Ancillary Logistics Parameters
# -------------------------------------------------------------------------
INDUSTRY_COST_CONFIG = {
    # 1. Marine Livestock Transit Mortality Insurance
    "insurance": {
        "base_premium_pct_cif": 2.25,        # 2.25% of declared animal CIF value
        "min_premium_pct": 1.40,
        "max_premium_pct": 3.80,
        "seasonal_heat_surcharge_pct": 0.65, # Summer / high THI voyage surcharge
        "war_risk_hra_surcharge_pct": 0.75,  # Bab-el-Mandeb / Red Sea / Gulf of Aden transit
        "deductible_pct": 1.0,               # First 1% natural mortality absorbed by shipper
        "vet_onboard_discount_pct": 0.20     # Accredited vet on board reduction
    },
    # 2. Livestock Maritime Fleet Charter & Freight Economics
    "maritime": {
        "time_charter_rates_usd_day": {
            "handy_livestock_3k_6k_dwt": 32000.0,
            "large_livestock_10k_17k_dwt": 44000.0,
            "super_livestock_20k_plus_dwt": 52000.0
        },
        "bunker_fuel_usd_mt": {
            "vlsfo_singapore": 615.0,
            "vlsfo_rotterdam": 575.0,
            "vlsfo_santos": 630.0,
            "mgo_marine_gas_oil": 785.0
        },
        "voyage_freight_benchmarks_usd_per_head": {
            "Darwin_to_Jakarta": 118.0,
            "Townsville_to_Haiphong": 148.0,
            "Vila_do_Conde_to_Alexandria": 265.0,
            "Montevideo_to_Jeddah": 285.0,
            "Cartagena_to_Beirut": 240.0,
            "Spain_to_Libya": 95.0
        },
        "choke_point_transit_tolls_usd": {
            "suez_canal_laden_livestock": 210000.0,
            "panama_canal_neopanamax": 285000.0,
            "bosphorus_strait_dues": 45000.0
        }
    },
    # 3. Refrigerated Container (Reefer Box) Ocean Freight
    "reefer_freight_usd_per_40ft_feu": {
        "Santos_Brazil_to_Shanghai": 4350.0,
        "Brisbane_Australia_to_Long_Beach": 3850.0,
        "Houston_USA_to_Rotterdam": 2950.0,
        "Long_Beach_USA_to_Tokyo": 2800.0,
        "Buenos_Aires_to_St_Petersburg": 4600.0,
        "reefer_genset_power_plug_usd_day": 85.0,
        "cold_storage_warehousing_usd_cwt_month": 3.75
    },
    # 4. Feedlot Cost-of-Gain (COG) Model Parameters
    "feedlot_cog": {
        "corn_bushels_per_cwt_gain": 8.5,       # ~8.5 bushels corn per 100 lbs gain
        "ddgs_lbs_per_cwt_gain": 65.0,           # Distillers grains protein supplement
        "forage_hay_lbs_per_cwt_gain": 85.0,     # Alfalfa / prairie hay roughage
        "yardage_charge_usd_head_day": 0.58,     # Facilities, equipment, labor
        "veterinary_medication_usd_head": 26.50, # Vaccines, implants, parasiticides
        "feedlot_death_loss_allowance_pct": 1.25,# Typical feedlot death loss
        "financing_interest_rate_pct": 8.25,     # Live feeder animal financing rate
        "feed_conversion_ratio_fcr": 6.2         # lbs dry matter feed per 1 lb live gain
    },
    # 5. Meat Processing & Packer Margin Parameters
    "packer_margins": {
        "dressing_percentage_pct": 63.5,         # Live weight to hot carcass weight (HCW)
        "kill_and_fabrication_cost_usd_head": 285.0, # Labor, energy, packaging, cold storage
        "drop_credit_byproduct_usd_cwt": 13.85,  # Hides, edible tallow, blood meal, offal
        "box_loss_shrink_pct": 1.5               # Fabrication cutting shrink
    },
    # 6. Tariffs, Duties & Phytosanitary Export Costs
    "tariffs_and_quotas": {
        "argentina_dex_export_tax_pct": 9.0,
        "us_trq_in_quota_cents_kg": 4.4,
        "us_trq_out_of_quota_tariff_pct": 26.4,
        "china_mfn_beef_tariff_pct": 12.0,
        "eu_hilton_quota_tariff_pct": 20.0,
        "eu_non_quota_beef_tariff_pct": 45.0,
        "pre_export_quarantine_peq_usd_head": 48.0,
        "halal_certification_audit_usd_container": 350.0
    }
}

# -------------------------------------------------------------------------
# Real-Time Bovine & Agribusiness News Wire Endpoints
# -------------------------------------------------------------------------
NEWS_WIRE_CONFIG = {
    "rss_feeds": [
        {"name": "USDA FAS News", "url": "https://www.fas.usda.gov/rss/news.xml", "category": "POLICY"},
        {"name": "CME Group Ag", "url": "https://www.cmegroup.com/rss/news-commodities.xml", "category": "CASH"},
        {"name": "Beef Central Feed", "url": "https://www.beefcentral.com/feed/", "category": "TRADE"},
        {"name": "Meat & Livestock Australia", "url": "https://www.mla.com.au/rss/news", "category": "MARITIME"}
    ],
    "refresh_interval_sec": 300
}
