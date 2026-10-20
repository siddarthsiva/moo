"""
Project MOO - Global Supply & Demand Balance Engine.
Calculates regional surplus/deficit balances, herd expansion/liquidation phase scores,
drought & pasture stress metrics, and phytosanitary biosecurity alerts.
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from config import GLOBAL_CATTLE_PRODUCERS


# Qualitative and Quantitative S&D Balance Matrix
SUPPLY_DEMAND_INTELLIGENCE = {
    "USA": {
        "herd_phase": "LIQUIDATION_CYCLE_TROUGH",
        "herd_phase_score": -85,       # Scale -100 (Deep liquidation) to +100 (Aggressive retention)
        "supply_condition": "SEVERE_DEFICIT",
        "supply_score": 18,            # 0 (Severe Shortage) to 100 (Massive Glut)
        "demand_condition": "HYPER_INTENSE",
        "demand_score": 92,            # 0 (Collapsed) to 100 (Extreme Inelastic Demand)
        "pasture_stress_index": 68,     # 0 (Optimal Lush) to 100 (Extreme Arid Drought)
        "import_dependency_pct": 14.2, # % of total domestic beef consumption imported
        "per_capita_consumption_kg": 26.8,
        "key_driver": "Historic 73-year low cattle inventory drives feeder calves to record highs. Packer margins squeezed by record live cattle cash prices."
    },
    "BRA": {
        "herd_phase": "PEAK_FEMALE_SLAUGHTER_TRANSITION",
        "herd_phase_score": -45,
        "supply_condition": "MASSIVE_SURPLUS",
        "supply_score": 95,
        "demand_condition": "EXPORT_PULL_STRONG",
        "demand_score": 84,
        "pasture_stress_index": 35,
        "import_dependency_pct": 0.5,
        "per_capita_consumption_kg": 34.2,
        "key_driver": "Record packing throughput and female slaughter rates. Currency advantage cements dominance in Chinese and Middle Eastern volume beef supply."
    },
    "AUS": {
        "herd_phase": "EXPANSION_MATURATION",
        "herd_phase_score": 75,
        "supply_condition": "ROBUST_SURPLUS",
        "supply_score": 88,
        "demand_condition": "GLOBAL_IMPORT_PULL",
        "demand_score": 86,
        "pasture_stress_index": 30,
        "import_dependency_pct": 0.8,
        "per_capita_consumption_kg": 19.5,
        "key_driver": "Post-La Niña herd rebuilding fully realized. Heavy slaughter weights and record exports of 90CL lean manufacturing trim to the United States."
    },
    "IND": {
        "herd_phase": "STABLE_CONTINUOUS_EXPANSION",
        "herd_phase_score": 20,
        "supply_condition": "STEADY_EQUILIBRIUM",
        "supply_score": 78,
        "demand_condition": "PRICE_SENSITIVE_GROWTH",
        "demand_score": 74,
        "pasture_stress_index": 42,
        "import_dependency_pct": 0.0,
        "per_capita_consumption_kg": 4.1, # Carabeef (Buffalo)
        "key_driver": "Continuous supply of water buffalo culled from expanding national dairy sector. Serves price-sensitive Halal import markets across Southeast Asia and MENA."
    },
    "ARG": {
        "herd_phase": "POST_DROUGHT_RECOVERY",
        "herd_phase_score": 10,
        "supply_condition": "TIGHT_RECOVERING",
        "supply_score": 52,
        "demand_condition": "DOMESTIC_WEAK_EXPORT_STRONG",
        "demand_score": 68,
        "pasture_stress_index": 48,
        "import_dependency_pct": 0.3,
        "per_capita_consumption_kg": 48.5, # Historically highest global beef intake
        "key_driver": "Severe 2023/24 drought reduced calf crops. Domestic economic headwinds curb local demand, forcing meatpackers to maximize export shipments."
    },
    "CHN": {
        "herd_phase": "DOMESTIC_FEEDLOT_LIQUIDATION",
        "herd_phase_score": -60,
        "supply_condition": "DOMESTIC_GLUT_LOW_PRICES",
        "supply_score": 65,
        "demand_condition": "SUPER_IMPORTER_VALUE_SEEKING",
        "demand_score": 88,
        "pasture_stress_index": 50,
        "import_dependency_pct": 32.5,
        "per_capita_consumption_kg": 7.3,
        "key_driver": "Domestic cattle farm-gate prices fell below break-even causing domestic calf liquidation, yet reliance on low-cost Brazilian frozen beef imports remains near record highs."
    },
    "JPN": {
        "herd_phase": "STABLE_STALL_HERD",
        "herd_phase_score": 5,
        "supply_condition": "DEFICIT_HIGH_COST",
        "supply_score": 38,
        "demand_condition": "HIGH_VALUE_STEADY",
        "demand_score": 78,
        "pasture_stress_index": 15,
        "import_dependency_pct": 60.5,
        "per_capita_consumption_kg": 9.8,
        "key_driver": "High imported feed grain prices squeeze domestic Wagyu and dairy-steer feedlot margins. Steady demand for chilled grain-fed beef cuts from US and Australia."
    },
    "EU": {
        "herd_phase": "STRUCTURAL_HERD_CONTRACTION",
        "herd_phase_score": -50,
        "supply_condition": "TIGHT_STRUCTURAL_DEFICIT",
        "supply_score": 42,
        "demand_condition": "MATURE_SUSTAINABILITY_FOCUS",
        "demand_score": 64,
        "pasture_stress_index": 38,
        "import_dependency_pct": 5.3,
        "per_capita_consumption_kg": 13.5,
        "key_driver": "Environmental nitrogen regulations, Common Agricultural Policy changes, and farm succession issues permanently downsizing the suckler cow herd."
    },
    "NZL": {
        "herd_phase": "EQUILIBRIUM_CYCLICAL",
        "herd_phase_score": 15,
        "supply_condition": "SEASONAL_SURPLUS",
        "supply_score": 75,
        "demand_condition": "EXPORT_PULL",
        "demand_score": 80,
        "pasture_stress_index": 25,
        "import_dependency_pct": 2.1,
        "per_capita_consumption_kg": 14.8,
        "key_driver": "100% pasture grass-fed model enables seasonal peak slaughter. Premium exporter of lean grinding beef to North American quick-service restaurant supply chains."
    },
    "EGY": {
        "herd_phase": "CHRONIC_CONTRACTION",
        "herd_phase_score": -30,
        "supply_condition": "ACUTE_DOMESTIC_DEFICIT",
        "supply_score": 22,
        "demand_condition": "ROBUST_HALAL_IMPORT_DEMAND",
        "demand_score": 85,
        "pasture_stress_index": 85,
        "import_dependency_pct": 55.0,
        "per_capita_consumption_kg": 8.2,
        "key_driver": "Limited arable forage and irrigation water forces heavy reliance on maritime shipments of live slaughter bulls from Brazil/Colombia and boneless carabeef from India."
    },
    "IDN": {
        "herd_phase": "SMALLHOLDER_STATIC",
        "herd_phase_score": 0,
        "supply_condition": "CHRONIC_STRUCTURAL_DEFICIT",
        "supply_score": 25,
        "demand_condition": "SURGING_POPULATION_PULL",
        "demand_score": 89,
        "pasture_stress_index": 40,
        "import_dependency_pct": 43.0,
        "per_capita_consumption_kg": 2.8,
        "key_driver": "Rapidly growing protein consumption among 280M citizens. Feedlot finishing sector relies entirely on imported Australian live feeder steers."
    }
}


class GlobalSupplyDemandEngine:
    """Computes regional supply/demand imbalances, stress matrices, and market tension indices."""

    def __init__(self, sd_data: Optional[Dict[str, Any]] = None):
        self.sd_data = sd_data or SUPPLY_DEMAND_INTELLIGENCE
        self.producers = GLOBAL_CATTLE_PRODUCERS

    def get_sd_overview_df(self) -> pd.DataFrame:
        """Returns consolidated Supply & Demand balance scorecard table."""
        rows = []
        for code, info in self.sd_data.items():
            prod_info = self.producers.get(code, {})
            c_name = prod_info.get("name", code)
            rows.append({
                "CODE": code,
                "COUNTRY": c_name,
                "SUPPLY SCORE (0-100)": info["supply_score"],
                "SUPPLY CONDITION": info["supply_condition"],
                "DEMAND SCORE (0-100)": info["demand_score"],
                "DEMAND CONDITION": info["demand_condition"],
                "NET BALANCE (SD DIFF)": info["supply_score"] - info["demand_score"],
                "HERD PHASE SCORE": info["herd_phase_score"],
                "HERD PHASE": info["herd_phase"],
                "PASTURE DROUGHT INDEX": info["pasture_stress_index"],
                "IMPORT DEPENDENCY %": info["import_dependency_pct"],
                "PER CAPITA CONSUMPTION (KG)": info["per_capita_consumption_kg"],
                "KEY MARKET DRIVER": info["key_driver"]
            })
        df = pd.DataFrame(rows)
        return df.sort_values(by="NET BALANCE (SD DIFF)").reset_index(drop=True)

    def get_biosecurity_alerts_df(self) -> pd.DataFrame:
        """Returns active biosecurity, disease, and phytosanitary border control alerts."""
        alerts = []
        for code, info in self.producers.items():
            alerts.append({
                "CODE": code,
                "COUNTRY": info["name"],
                "FMD STATUS": info.get("fmd_status", "N/A"),
                "BSE RISK": info.get("bse_risk", "N/A"),
                "BIOSECURITY & QUARANTINE PROTOCOL": info.get("quarantine_alerts", "Standard phytosanitary inspections")
            })
        return pd.DataFrame(alerts)
