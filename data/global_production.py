"""
Project MOO - Global Bovine Production & Cattle Breed Intelligence Engine.
Provides country-level cattle census, breed taxonomy, carcass yields, and production profiles.
"""

from typing import Dict, List, Any, Optional
import pandas as pd
from config import GLOBAL_CATTLE_PRODUCERS


BREED_TAXONOMY = [
    {
        "breed_name": "Black Angus / Red Angus",
        "scientific_species": "Bos taurus",
        "origin": "Scotland / United States",
        "primary_countries": "USA, Australia, Canada, Argentina, New Zealand",
        "marbling_ability": "Exceptional (USDA Prime / Choice)",
        "climate_adaptation": "Temperate (susceptible to tropical heat/tick stress)",
        "typical_market_weight_lbs": "1,350 - 1,500 lbs",
        "feed_system": "Grain-fed Feedlot (120-200 days) & Premium Pasture",
        "commercial_use": "High-end retail steaks, food service, branded beef programs"
    },
    {
        "breed_name": "Nelore (Zebu)",
        "scientific_species": "Bos indicus",
        "origin": "India / Brazil",
        "primary_countries": "Brazil (~80% of national herd), Paraguay, Bolivia",
        "marbling_ability": "Low to Moderate (Lean, highly muscular)",
        "climate_adaptation": "Extreme Tropical Heat & Parasite Resistance (Hump & Sweat Glands)",
        "typical_market_weight_lbs": "1,150 - 1,300 lbs",
        "feed_system": "Extensive Tropical Pasture (Brachiaria grass) + 90-day Feedlot finish",
        "commercial_use": "Boneless frozen manufacturing beef, export cuts to China/MENA"
    },
    {
        "breed_name": "Japanese Wagyu (Kuroge Washu)",
        "scientific_species": "Bos taurus",
        "origin": "Japan (Kobe, Matsusaka, Ohmi)",
        "primary_countries": "Japan, Australia (F1-Fullblood), USA",
        "marbling_ability": "World Highest (BMS 8 to 12, High Monounsaturated Oleic Acid)",
        "climate_adaptation": "Controlled Barn / Stall Environments",
        "typical_market_weight_lbs": "1,550 - 1,750 lbs",
        "feed_system": "Long-term Grain Rations (500 to 650+ days on rice straw, barley, corn)",
        "commercial_use": "Ultra-luxury gastronomy, high-end exports ($150-$300+/lb)"
    },
    {
        "breed_name": "Brahman",
        "scientific_species": "Bos indicus",
        "origin": "United States (from Indian Zebu roots)",
        "primary_countries": "Northern Australia, US Gulf Coast, Colombia, Mexico",
        "marbling_ability": "Moderate (Lean, hardy)",
        "climate_adaptation": "Supreme Heat, Drought & Tick Resistance",
        "typical_market_weight_lbs": "1,200 - 1,400 lbs",
        "feed_system": "Northern Pastoral Rangeland; Live Ocean Transport to SE Asia Feedlots",
        "commercial_use": "Live export feeder trade to Indonesia/Vietnam, tropical crossbreeding"
    },
    {
        "breed_name": "Carabeef (Water Buffalo)",
        "scientific_species": "Bubalus bubalis",
        "origin": "India / South Asia",
        "primary_countries": "India, Pakistan, Southeast Asia",
        "marbling_ability": "Ultra-Lean (<2% intramuscular fat, low cholesterol)",
        "climate_adaptation": "Tropical Wetlands & Subtropical Forage",
        "typical_market_weight_lbs": "900 - 1,150 lbs",
        "feed_system": "Agricultural Crop Residues, Straw, Forage (No grain feedlots)",
        "commercial_use": "100% Halal boneless frozen export meat to Egypt, Malaysia, Vietnam, Saudi Arabia"
    },
    {
        "breed_name": "Charolais & Limousin",
        "scientific_species": "Bos taurus (Continental)",
        "origin": "France",
        "primary_countries": "European Union (France, Ireland), Canada, USA, Mexico",
        "marbling_ability": "Moderate (High lean meat yield, low waste fat)",
        "climate_adaptation": "Temperate Continental",
        "typical_market_weight_lbs": "1,450 - 1,650 lbs",
        "feed_system": "Intensive young bull rations (maize silage + concentrates) & pasture",
        "commercial_use": "High retail yield primals, lean cuts, European supermarket trim"
    },
    {
        "breed_name": "Hereford",
        "scientific_species": "Bos taurus",
        "origin": "England",
        "primary_countries": "Argentina, Uruguay, USA, Australia, New Zealand, Canada",
        "marbling_ability": "High (Tender, consistent)",
        "climate_adaptation": "Exceptional Foraging Hardiness in Cold and Arid Rangelands",
        "typical_market_weight_lbs": "1,250 - 1,450 lbs",
        "feed_system": "Pampas Pasture Grass-fed & Grain finished",
        "commercial_use": "Premium grass-fed beef (Hilton Quota), retail steaks"
    },
    {
        "breed_name": "Holstein / Friesian Dairy Cull",
        "scientific_species": "Bos taurus",
        "origin": "Netherlands / Global Dairy Sector",
        "primary_countries": "USA, EU, New Zealand, China, India",
        "marbling_ability": "Variable (Mature lean cow meat + high-marbled steers)",
        "climate_adaptation": "Temperate Dairy Facilities",
        "typical_market_weight_lbs": "1,300 - 1,600 lbs",
        "feed_system": "Total Mixed Ration (TMR) dairy diets; feedlot-finished dairy steers",
        "commercial_use": "Ground beef trim (50CL / 90CL blends), processed meat, canned beef"
    }
]


class GlobalBovineProductionEngine:
    """Engine for querying and aggregating global cattle production data and breed intelligence."""

    def __init__(self, producers_data: Optional[Dict[str, Any]] = None):
        self.producers = producers_data or GLOBAL_CATTLE_PRODUCERS

    def get_country_summary_df(self) -> pd.DataFrame:
        """Returns consolidated country-level production and trade summary table."""
        records = []
        for code, info in self.producers.items():
            records.append({
                "CODE": code,
                "COUNTRY": info["name"],
                "HERD (M Head)": info["cattle_herd_million_head"],
                "BEEF PROD (1K MT)": info["annual_beef_production_1000mt"],
                "EXPORTS (1K MT)": info["annual_exports_1000mt"],
                "IMPORTS (1K MT)": info["annual_imports_1000mt"],
                "NET TRADE (1K MT)": info["annual_exports_1000mt"] - info["annual_imports_1000mt"],
                "CARCASS WT (KG)": info["avg_carcass_weight_kg"],
                "CARCASS WT (LBS)": info["avg_carcass_weight_lbs"],
                "SUPPLY STATUS": info["supply_status"],
                "DEMAND STATUS": info["demand_status"],
                "PRIMARY BREEDS": ", ".join(info["primary_breeds"][:3]),
                "FMD STATUS": info["fmd_status"],
                "LAT": info["lat"],
                "LON": info["lon"]
            })
        df = pd.DataFrame(records)
        return df.sort_values(by="BEEF PROD (1K MT)", ascending=False).reset_index(drop=True)

    def get_breed_taxonomy_df(self) -> pd.DataFrame:
        """Returns detailed reference table of major global cattle breeds and commercial characteristics."""
        return pd.DataFrame(BREED_TAXONOMY)

    def get_country_finishing_df(self) -> pd.DataFrame:
        """Returns comparative finishing methods (% Grain Feedlot vs % Pasture vs % Cull) by country."""
        rows = []
        for code, info in self.producers.items():
            f_types = info.get("finish_type_pct", {})
            rows.append({
                "COUNTRY": info["name"],
                "GRAIN FEEDLOT %": f_types.get("Grain-fed Feedlot", f_types.get("Commercial Feedlot Finished", 0)),
                "PASTURE GRASS %": f_types.get("Pasture Grass-fed", f_types.get("Pampas Grass-fed", f_types.get("100% Pasture Grass-fed", 0))),
                "FORAGE / CULL %": f_types.get("Smallholder Forage", f_types.get("Agricultural Byproduct Forage", f_types.get("Dairy Cull", 0)))
            })
        return pd.DataFrame(rows)

    def get_country_detail(self, country_code: str) -> Optional[Dict[str, Any]]:
        """Returns full metadata specification for a single country."""
        return self.producers.get(country_code.upper())
