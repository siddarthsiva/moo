"""
Project MOO - End-to-End Bovine Industry Cost & Logistics Economics Engine.
Calculates marine cargo & mortality insurance, vessel charter economics,
reefer container freight, feedlot cost-of-gain (COG), packer processing margins,
and complete retail supply chain margin waterfalls.
"""

from typing import Dict, List, Any, Optional
import pandas as pd
from config import INDUSTRY_COST_CONFIG


class BovineIndustryCostEngine:
    """Computes comprehensive logistics, insurance, feedlot, and processing economics for cattle markets."""

    def __init__(self, cost_config: Optional[Dict[str, Any]] = None):
        self.config = cost_config or INDUSTRY_COST_CONFIG

    def calculate_marine_mortality_insurance(
        self,
        cargo_cif_value_usd: float,
        route_high_risk: bool = False,
        summer_heat_stress: bool = False,
        has_accredited_vet: bool = True
    ) -> Dict[str, Any]:
        """
        Calculates livestock transit mortality marine insurance premium.
        Returns premium rate %, dollar cost, deductible, and risk factor breakdown.
        """
        ins_cfg = self.config["insurance"]
        rate = ins_cfg["base_premium_pct_cif"]

        surcharges = 0.0
        if route_high_risk:
            surcharges += ins_cfg["war_risk_hra_surcharge_pct"]
        if summer_heat_stress:
            surcharges += ins_cfg["seasonal_heat_surcharge_pct"]
        if has_accredited_vet:
            surcharges -= ins_cfg["vet_onboard_discount_pct"]

        final_rate = max(ins_cfg["min_premium_pct"], min(ins_cfg["max_premium_pct"], rate + surcharges))
        premium_usd = cargo_cif_value_usd * (final_rate / 100.0)
        deductible_usd = cargo_cif_value_usd * (ins_cfg["deductible_pct"] / 100.0)

        return {
            "cargo_cif_value_usd": cargo_cif_value_usd,
            "final_premium_rate_pct": final_rate,
            "base_premium_pct": ins_cfg["base_premium_pct_cif"],
            "war_risk_surcharge_pct": ins_cfg["war_risk_hra_surcharge_pct"] if route_high_risk else 0.0,
            "heat_stress_surcharge_pct": ins_cfg["seasonal_heat_surcharge_pct"] if summer_heat_stress else 0.0,
            "vet_discount_pct": ins_cfg["vet_onboard_discount_pct"] if has_accredited_vet else 0.0,
            "total_insurance_premium_usd": premium_usd,
            "shipper_deductible_usd": deductible_usd
        }

    def calculate_feedlot_cost_of_gain(
        self,
        corn_price_usd_bu: float = 4.25,
        ddgs_price_usd_ton: float = 195.0,
        alfalfa_hay_price_usd_ton: float = 180.0,
        days_on_feed: int = 160,
        total_gain_lbs: float = 550.0
    ) -> Dict[str, Any]:
        """
        Calculates feedlot Cost of Gain (COG) per pound and total finishing cost per steer.
        """
        f_cfg = self.config["feedlot_cog"]

        cwt_gain = total_gain_lbs / 100.0

        # Feed Ration Costs
        corn_cost = cwt_gain * f_cfg["corn_bushels_per_cwt_gain"] * corn_price_usd_bu
        ddgs_cost = cwt_gain * (f_cfg["ddgs_lbs_per_cwt_gain"] / 2000.0) * ddgs_price_usd_ton
        hay_cost = cwt_gain * (f_cfg["forage_hay_lbs_per_cwt_gain"] / 2000.0) * alfalfa_hay_price_usd_ton
        total_feed_ration_cost = corn_cost + ddgs_cost + hay_cost

        # Yardage, Vet & Overhead
        yardage_total = days_on_feed * f_cfg["yardage_charge_usd_head_day"]
        vet_cost = f_cfg["veterinary_medication_usd_head"]
        interest_charge = (corn_cost + yardage_total) * (f_cfg["financing_interest_rate_pct"] / 100.0) * (days_on_feed / 365.0)

        total_finishing_cost = total_feed_ration_cost + yardage_total + vet_cost + interest_charge
        cog_per_lb = total_finishing_cost / total_gain_lbs
        cog_per_cwt = cog_per_lb * 100.0

        return {
            "corn_price_bu": corn_price_usd_bu,
            "ddgs_price_ton": ddgs_price_usd_ton,
            "hay_price_ton": alfalfa_hay_price_usd_ton,
            "feed_ration_cost_usd": total_feed_ration_cost,
            "yardage_charge_usd": yardage_total,
            "veterinary_cost_usd": vet_cost,
            "financing_interest_usd": interest_charge,
            "total_finishing_cost_usd": total_finishing_cost,
            "cost_of_gain_usd_per_lb": cog_per_lb,
            "cost_of_gain_usd_per_cwt": cog_per_cwt,
            "feed_conversion_ratio": f_cfg["feed_conversion_ratio_fcr"]
        }

    def calculate_meat_packer_margin(
        self,
        live_cattle_price_cwt: float = 188.50,
        boxed_beef_cutout_cwt: float = 312.00,
        fed_steer_weight_lbs: float = 1420.0
    ) -> Dict[str, Any]:
        """
        Calculates meat packing plant gross processing spread per head.
        Includes hot carcass weight yield, drop credit (hide & offal), and kill/fab costs.
        """
        p_cfg = self.config["packer_margins"]

        dressing_pct = p_cfg["dressing_percentage_pct"] / 100.0
        carcass_weight_lbs = fed_steer_weight_lbs * dressing_pct
        carcass_weight_cwt = carcass_weight_lbs / 100.0
        live_weight_cwt = fed_steer_weight_lbs / 100.0

        # Revenues per Head
        boxed_beef_rev = carcass_weight_cwt * boxed_beef_cutout_cwt
        drop_credit_rev = live_weight_cwt * p_cfg["drop_credit_byproduct_usd_cwt"]
        total_packer_revenue = boxed_beef_rev + drop_credit_rev

        # Costs per Head
        live_cattle_cost = live_weight_cwt * live_cattle_price_cwt
        kill_and_fab_cost = p_cfg["kill_and_fabrication_cost_usd_head"]
        total_packer_cost = live_cattle_cost + kill_and_fab_cost

        net_margin_head = total_packer_revenue - total_packer_cost
        net_margin_pct = (net_margin_head / total_packer_revenue) * 100.0

        return {
            "live_cattle_price_cwt": live_cattle_price_cwt,
            "boxed_beef_cutout_cwt": boxed_beef_cutout_cwt,
            "fed_steer_live_weight_lbs": fed_steer_weight_lbs,
            "hot_carcass_weight_lbs": carcass_weight_lbs,
            "boxed_beef_revenue_usd": boxed_beef_rev,
            "drop_credit_revenue_usd": drop_credit_rev,
            "total_gross_revenue_usd": total_packer_revenue,
            "live_cattle_cost_usd": live_cattle_cost,
            "kill_and_fab_cost_usd": kill_and_fab_cost,
            "total_packer_cost_usd": total_packer_cost,
            "net_packer_margin_usd_per_head": net_margin_head,
            "net_packer_margin_pct": net_margin_pct
        }

    def get_maritime_freight_summary_df(self) -> pd.DataFrame:
        """Returns benchmark livestock voyage ocean freight rates table."""
        routes = self.config["maritime"]["voyage_freight_benchmarks_usd_per_head"]
        rows = []
        for route, rate in routes.items():
            r_clean = route.replace("_", " ")
            rows.append({
                "VOYAGE ROUTE": r_clean,
                "FREIGHT ($ / HEAD)": rate,
                "EST. FEED & WATER ($ / HEAD)": round(rate * 0.16, 2),
                "EST. DISCHARGE HANDLING ($)": 28.00,
                "TOTAL LANDED LOGISTICS ($ / HEAD)": round(rate * 1.16 + 28.00, 2)
            })
        return pd.DataFrame(rows)

    def get_reefer_ocean_rates_df(self) -> pd.DataFrame:
        """Returns 40ft High Cube refrigerated beef container freight rates."""
        rates = self.config["reefer_freight_usd_per_40ft_feu"]
        rows = []
        for lane, cost in rates.items():
            if lane.startswith("reefer") or lane.startswith("cold"):
                continue
            lane_clean = lane.replace("_", " ")
            # 40ft container carries ~25 Metric Tons (55,115 lbs) of frozen boneless beef
            cost_per_lb = float(cost) / 55115.0
            rows.append({
                "TRADE LANE": lane_clean,
                "40FT REEFER CONTAINER RATE ($)": cost,
                "OCEAN FREIGHT PER LB ($)": round(cost_per_lb, 4),
                "OCEAN FREIGHT PER CWT ($)": round(cost_per_lb * 100.0, 2)
            })
        return pd.DataFrame(rows)

    def get_supply_chain_waterfall_df(self) -> pd.DataFrame:
        """Returns standard cost waterfall from 550lb calf to consumer retail package."""
        return pd.DataFrame([
            {"STAGE": "1. Weaned Calf Purchase (550 lbs @ $2.95/lb)", "STAGE COST ($)": 1622.50, "CUMULATIVE ($)": 1622.50, "COST PER LB ($)": 2.95},
            {"STAGE": "2. Backgrounding & Pasture Gain (250 lbs)", "STAGE COST ($)": 285.00, "CUMULATIVE ($)": 1907.50, "COST PER LB ($)": 2.38},
            {"STAGE": "3. Feedlot Finishing Ration & Yardage (620 lbs Gain)", "STAGE COST ($)": 694.40, "CUMULATIVE ($)": 2601.90, "COST PER LB ($)": 1.83},
            {"STAGE": "4. Feedlot Vet, Medication & Financing", "STAGE COST ($)": 68.50, "CUMULATIVE ($)": 2670.40, "COST PER LB ($)": 1.88},
            {"STAGE": "5. Live Cattle Marketing & Inbound Hauling", "STAGE COST ($)": 38.00, "CUMULATIVE ($)": 2708.40, "COST PER LB ($)": 1.91},
            {"STAGE": "6. Packing Plant Slaughter & Fabrication Cost", "STAGE COST ($)": 285.00, "CUMULATIVE ($)": 2993.40, "COST PER LB ($)": 3.32}, # per carcass lb
            {"STAGE": "7. Net Offal & Byproduct Drop Credit (Deduction)", "STAGE COST ($)": -196.67, "CUMULATIVE ($)": 2796.73, "COST PER LB ($)": 3.10},
            {"STAGE": "8. Cold Storage, Reefer Transport & Wholesale Drayage", "STAGE COST ($)": 165.00, "CUMULATIVE ($)": 2961.73, "COST PER LB ($)": 3.28},
            {"STAGE": "9. Supermarket / Retail Cutting, Shrink & Packaging", "STAGE COST ($)": 480.00, "CUMULATIVE ($)": 3441.73, "COST PER LB ($)": 5.46}, # per retail lb
            {"STAGE": "10. Retailer Gross Margin & Operating Profit", "STAGE COST ($)": 880.00, "CUMULATIVE ($)": 4321.73, "COST PER LB ($)": 6.85}
        ])
