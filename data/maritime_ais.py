"""
Project MOO - Real-Time Livestock Carrier Maritime AIS Fleet Tracker.
Simulates and tracks specialized cattle carrier vessels across global maritime corridors,
monitoring navigation status, choke point transits, ETA, and onboard animal welfare telemetry.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd
import numpy as np
from config import LIVESTOCK_CARRIER_FLEET


# Global Maritime Choke Points for Livestock Shipping
MARITIME_CHOKE_POINTS = [
    {"name": "Suez Canal", "lat": 30.5852, "lon": 32.2654, "risk_category": "CONGESTION_TOLL", "desc": "Key transit linking Atlantic/Med to Red Sea & Gulf"},
    {"name": "Bab-el-Mandeb", "lat": 12.5833, "lon": 43.3333, "risk_category": "WAR_RISK_HRA", "desc": "High Risk Area; requires armed security escort & war risk premium"},
    {"name": "Strait of Malacca", "lat": 2.5000, "lon": 101.5000, "risk_category": "DENSE_TRAFFIC", "desc": "Major corridor for Australian cattle bound for SE Asia/China"},
    {"name": "Strait of Gibraltar", "lat": 35.9641, "lon": -5.5000, "risk_category": "WEATHER_TRANSIT", "desc": "Gateway for South American cattle carriers entering Mediterranean"},
    {"name": "Lombok Strait", "lat": -8.5000, "lon": 115.7500, "risk_category": "DEEP_WATER_CORRIDOR", "desc": "Alternative deep-water corridor for large livestock carriers to Indonesia"}
]


class MaritimeLivestockAISEngine:
    """Manages real-time position telemetry, voyage tracks, and animal welfare monitoring for livestock vessels."""

    def __init__(self, fleet_data: Optional[List[Dict[str, Any]]] = None):
        self.fleet = fleet_data or LIVESTOCK_CARRIER_FLEET

    def get_fleet_telemetry_df(self) -> pd.DataFrame:
        """Returns consolidated DataFrame of all tracked livestock carriers with live AIS positions."""
        rows = []
        for v in self.fleet:
            rows.append({
                "VESSEL": v["name"],
                "IMO": v["imo"],
                "FLAG": v["flag"],
                "DWT": v["dwt"],
                "CAPACITY (HEAD)": v["cattle_head_capacity"],
                "SPEED (KTS)": v["current_speed"],
                "HEADING": v["current_heading"],
                "STATUS": v["status"],
                "CHOKE POINT STATUS": v["choke_point_status"],
                "ORIGIN": v["origin_port"],
                "DESTINATION": v["destination_port"],
                "CARGO MANIFEST": v["cargo_manifest"],
                "CARGO VAL ($)": v["cargo_val_usd"],
                "ETA": v["eta_date"],
                "FODDER REMAINING (DAYS)": v["fodder_days_remaining"],
                "HEAT STRESS RISK": v["heat_stress_index"],
                "VENTILATION (ACH)": v["ventilation_air_changes_per_hr"],
                "LAT": v["current_lat"],
                "LON": v["current_lon"]
            })
        df = pd.DataFrame(rows)
        return df.sort_values(by="CAPACITY (HEAD)", ascending=False).reset_index(drop=True)

    def get_fleet_summary_metrics(self) -> Dict[str, Any]:
        """Calculates global fleet aggregate statistics."""
        df = self.get_fleet_telemetry_df()
        total_vessels = len(df)
        total_capacity = int(df["CAPACITY (HEAD)"].sum())
        total_active_cargo_val = float(df["CARGO VAL ($)"].sum())
        choke_point_alerts = int((df["STATUS"] == "CHOKE_POINT_ALERT").sum())
        avg_speed = float(df["SPEED (KTS)"].mean())

        return {
            "total_vessels_tracked": total_vessels,
            "total_fleet_capacity_head": total_capacity,
            "total_active_cargo_value_usd": total_active_cargo_val,
            "vessels_in_choke_points": choke_point_alerts,
            "average_transit_speed_knots": avg_speed
        }
    
    def get_choke_points(self) -> List[Dict[str, Any]]:
        """Returns list of strategic maritime choke points."""
        return MARITIME_CHOKE_POINTS

    def get_vessel_by_imo(self, imo: int) -> Optional[Dict[str, Any]]:
        """Retrieves individual vessel dossier by IMO number."""
        for v in self.fleet:
            if v["imo"] == imo:
                return v
        return None
