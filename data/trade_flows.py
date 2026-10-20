"""
Project MOO - Global Bovine Trade Flows & Bilateral Corridors Engine.
Models international beef and live cattle shipments, bilateral volumes,
transport modes, and interactive Sankey diagram network topologies.
"""

from typing import Dict, List, Any, Tuple
import pandas as pd


GLOBAL_TRADE_CORRIDORS = [
    # Brazil Flows
    {"origin": "Brazil", "destination": "China", "commodity": "Frozen Boneless Beef", "volume_1000mt": 1450, "val_usd_million": 6815, "mode": "40ft Reefer Ocean Container"},
    {"origin": "Brazil", "destination": "United States", "commodity": "Frozen Boneless Beef", "volume_1000mt": 280, "val_usd_million": 1288, "mode": "40ft Reefer Ocean Container"},
    {"origin": "Brazil", "destination": "Chile", "commodity": "Chilled Beef Cuts", "volume_1000mt": 145, "val_usd_million": 841, "mode": "Overland Refrigerated Truck"},
    {"origin": "Brazil", "destination": "Egypt", "commodity": "Live Slaughter Bulls", "volume_1000mt": 195, "val_usd_million": 487, "mode": "Specialized Livestock Carrier Vessel"},
    {"origin": "Brazil", "destination": "United Arab Emirates", "commodity": "Frozen Boneless Beef", "volume_1000mt": 175, "val_usd_million": 787, "mode": "40ft Reefer Ocean Container"},
    {"origin": "Brazil", "destination": "European Union", "commodity": "Chilled Beef Cuts", "volume_1000mt": 95, "val_usd_million": 712, "mode": "40ft Reefer Ocean Container"},

    # Australia Flows
    {"origin": "Australia", "destination": "United States", "commodity": "Frozen Boneless Beef", "volume_1000mt": 440, "val_usd_million": 2640, "mode": "40ft Reefer Ocean Container"},
    {"origin": "Australia", "destination": "China", "commodity": "Frozen Boneless Beef", "volume_1000mt": 310, "val_usd_million": 2015, "mode": "40ft Reefer Ocean Container"},
    {"origin": "Australia", "destination": "Japan", "commodity": "Chilled Beef Cuts", "volume_1000mt": 285, "val_usd_million": 2280, "mode": "Fast Reefer Ocean Container"},
    {"origin": "Australia", "destination": "South Korea", "commodity": "Chilled Beef Cuts", "volume_1000mt": 240, "val_usd_million": 1800, "mode": "Fast Reefer Ocean Container"},
    {"origin": "Australia", "destination": "Indonesia", "commodity": "Live Feeder Cattle", "volume_1000mt": 210, "val_usd_million": 630, "mode": "Specialized Livestock Carrier Vessel"},
    {"origin": "Australia", "destination": "Vietnam", "commodity": "Live Slaughter Bulls", "volume_1000mt": 115, "val_usd_million": 368, "mode": "Specialized Livestock Carrier Vessel"},

    # United States Flows
    {"origin": "United States", "destination": "Japan", "commodity": "Chilled Beef Cuts", "volume_1000mt": 320, "val_usd_million": 2400, "mode": "Fast Reefer Ocean Container"},
    {"origin": "United States", "destination": "South Korea", "commodity": "Chilled Beef Cuts", "volume_1000mt": 290, "val_usd_million": 2320, "mode": "Fast Reefer Ocean Container"},
    {"origin": "United States", "destination": "China", "commodity": "Frozen Boneless Beef", "volume_1000mt": 170, "val_usd_million": 1445, "mode": "40ft Reefer Ocean Container"},
    {"origin": "United States", "destination": "Mexico", "commodity": "Chilled Beef Cuts", "volume_1000mt": 210, "val_usd_million": 1260, "mode": "Refrigerated Rail / Truck"},
    {"origin": "United States", "destination": "Canada", "commodity": "Chilled Beef Cuts", "volume_1000mt": 140, "val_usd_million": 980, "mode": "Refrigerated Truck"},

    # India Flows (Carabeef / Water Buffalo)
    {"origin": "India", "destination": "Vietnam", "commodity": "Frozen Boneless Beef", "volume_1000mt": 420, "val_usd_million": 1260, "mode": "40ft Reefer Ocean Container"},
    {"origin": "India", "destination": "Malaysia", "commodity": "Frozen Boneless Beef", "volume_1000mt": 260, "val_usd_million": 832, "mode": "40ft Reefer Ocean Container"},
    {"origin": "India", "destination": "Egypt", "commodity": "Frozen Boneless Beef", "volume_1000mt": 220, "val_usd_million": 660, "mode": "40ft Reefer Ocean Container"},
    {"origin": "India", "destination": "Indonesia", "commodity": "Frozen Boneless Beef", "volume_1000mt": 180, "val_usd_million": 540, "mode": "40ft Reefer Ocean Container"},
    {"origin": "India", "destination": "Saudi Arabia", "commodity": "Frozen Boneless Beef", "volume_1000mt": 150, "val_usd_million": 495, "mode": "40ft Reefer Ocean Container"},

    # Argentina & Uruguay Flows
    {"origin": "Argentina", "destination": "China", "commodity": "Frozen Boneless Beef", "volume_1000mt": 680, "val_usd_million": 2720, "mode": "40ft Reefer Ocean Container"},
    {"origin": "Argentina", "destination": "European Union", "commodity": "Chilled Beef Cuts", "volume_1000mt": 65, "val_usd_million": 650, "mode": "Fast Reefer Ocean Container"},
    {"origin": "Argentina", "destination": "Israel", "commodity": "Frozen Boneless Beef", "volume_1000mt": 42, "val_usd_million": 294, "mode": "Kosher Certified Reefer Container"},
    {"origin": "Uruguay", "destination": "China", "commodity": "Frozen Boneless Beef", "volume_1000mt": 240, "val_usd_million": 1080, "mode": "40ft Reefer Ocean Container"},
    {"origin": "Uruguay", "destination": "United States", "commodity": "Frozen Boneless Beef", "volume_1000mt": 75, "val_usd_million": 375, "mode": "40ft Reefer Ocean Container"},
    {"origin": "Uruguay", "destination": "Middle East", "commodity": "Live Feeder Cattle", "volume_1000mt": 65, "val_usd_million": 162, "mode": "Specialized Livestock Carrier Vessel"},

    # New Zealand Flows
    {"origin": "New Zealand", "destination": "United States", "commodity": "Frozen Boneless Beef", "volume_1000mt": 260, "val_usd_million": 1560, "mode": "40ft Reefer Ocean Container"},
    {"origin": "New Zealand", "destination": "China", "commodity": "Frozen Boneless Beef", "volume_1000mt": 220, "val_usd_million": 1210, "mode": "40ft Reefer Ocean Container"},
    {"origin": "New Zealand", "destination": "Japan", "commodity": "Chilled Beef Cuts", "volume_1000mt": 35, "val_usd_million": 280, "mode": "Fast Reefer Ocean Container"},

    # European Union Specialty Flows
    {"origin": "European Union", "destination": "United Kingdom", "commodity": "Chilled Beef Cuts", "volume_1000mt": 280, "val_usd_million": 1820, "mode": "Channel Tunnel / Reefer Ferry"},
    {"origin": "European Union", "destination": "Middle East", "commodity": "Live Slaughter Bulls", "volume_1000mt": 130, "val_usd_million": 390, "mode": "Specialized Livestock Carrier Vessel"}
]


class GlobalBovineTradeFlowsEngine:
    """Manages bilateral trade matrices, volume tracking, and Sankey visualization data."""

    def __init__(self, corridors: Optional[List[Dict[str, Any]]] = None):
        self.corridors = corridors or GLOBAL_TRADE_CORRIDORS

    def get_trade_matrix_df(self) -> pd.DataFrame:
        """Returns comprehensive bilateral trade flow tabular matrix."""
        df = pd.DataFrame(self.corridors)
        return df.sort_values(by="volume_1000mt", ascending=False).reset_index(drop=True)

    def get_top_export_routes(self, n: int = 10) -> pd.DataFrame:
        """Returns top N international cattle/beef shipping routes by volume."""
        return self.get_trade_matrix_df().head(n)

    def build_sankey_data(self) -> Tuple[List[str], List[int], List[int], List[float], List[str]]:
        """
        Builds nodes and links for a 3-tier Sankey diagram:
        Tier 1: Exporter Country -> Tier 2: Commodity Product Type -> Tier 3: Importer Country.
        Returns (labels, sources, targets, values, colors).
        """
        df = self.get_trade_matrix_df()

        exporters = sorted(df["origin"].unique().tolist())
        commodities = sorted(df["commodity"].unique().tolist())
        importers = sorted(df["destination"].unique().tolist())

        # Unique labels
        labels = exporters + commodities + importers
        label_to_id = {label: i for i, label in enumerate(labels)}

        sources = []
        targets = []
        values = []

        # Tier 1: Origin -> Commodity
        tier1 = df.groupby(["origin", "commodity"])["volume_1000mt"].sum().reset_index()
        for _, row in tier1.iterrows():
            sources.append(label_to_id[row["origin"]])
            targets.append(label_to_id[row["commodity"]])
            values.append(float(row["volume_1000mt"]))

        # Tier 2: Commodity -> Destination
        tier2 = df.groupby(["commodity", "destination"])["volume_1000mt"].sum().reset_index()
        for _, row in tier2.iterrows():
            sources.append(label_to_id[row["commodity"]])
            targets.append(label_to_id[row["destination"]])
            values.append(float(row["volume_1000mt"]))

        # Color palette for nodes
        colors = []
        for label in labels:
            if label in exporters:
                colors.append("rgba(255, 153, 0, 0.8)") # Bloomberg Orange
            elif label in commodities:
                colors.append("rgba(0, 204, 153, 0.8)") # Emerald Green
            else:
                colors.append("rgba(0, 180, 216, 0.8)") # Cyan Blue

        return labels, sources, targets, values, colors
