"""
Project MOO - Global Physical Bovine Supply Chain & Maritime AIS Workstation.
Workstation 06: Global breed geography, supply/demand imbalances, bilateral trade corridors,
real-time livestock carrier AIS tracking, industry cost waterfalls, and live agribusiness news wire.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from data.global_production import GlobalBovineProductionEngine, BREED_TAXONOMY
from data.supply_demand import GlobalSupplyDemandEngine
from data.trade_flows import GlobalBovineTradeFlowsEngine
from data.maritime_ais import MaritimeLivestockAISEngine, MARITIME_CHOKE_POINTS
from data.news_engine import AgribusinessNewsWireEngine
from factors.industry_costs import BovineIndustryCostEngine


def render_bbg_header(title: str, cmd: str = "SUPP <GO>", status: str = "GLOBAL AIS: 15 SHIPS"):
    """Renders authentic Bloomberg terminal top header."""
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


def apply_dark_theme(fig, title: str = "", height: int = 420):
    """Applies Bloomberg terminal dark styling to Plotly figures."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#05070a",
        plot_bgcolor="#05070a",
        height=height,
        autosize=True,
        title=dict(
            text=title if title else None,
            font=dict(size=11, color="#ff9900", family="'Roboto Mono', monospace"),
            x=0.01,
            y=0.98
        ) if title else None,
        font=dict(family="'Roboto Mono', monospace", size=9, color="#b0b5c0"),
        margin=dict(l=35, r=20, t=35 if title else 20, b=30),
        legend=dict(
            bgcolor="rgba(10, 12, 16, 0.8)",
            bordercolor="#202430",
            borderwidth=1,
            font=dict(size=8.5, color="#b0b5c0"),
            orientation="h",
            yanchor="top",
            y=-0.12,
            xanchor="center",
            x=0.5
        )
    )
    return fig


def render_global_supply_chain_workstation():
    """Main rendering entrypoint for Workstation 06."""
    render_bbg_header(
        "06 // GLOBAL BOVINE PHYSICAL SUPPLY CHAIN, MARITIME AIS & INDUSTRY ECONOMICS [SUPP <GO>]",
        cmd="PHYSICAL COMMODITY & FLEET DESK",
        status="TELEMETRY: VERIFIED"
    )

    # Initialize domain engines
    prod_engine = GlobalBovineProductionEngine()
    sd_engine = GlobalSupplyDemandEngine()
    trade_engine = GlobalBovineTradeFlowsEngine()
    ais_engine = MaritimeLivestockAISEngine()
    cost_engine = BovineIndustryCostEngine()
    news_engine = AgribusinessNewsWireEngine()

    # Sub-tabs navigation
    tab_geog, tab_snd, tab_flow, tab_ship, tab_cost, tab_news = st.tabs([
        "01 // BREED & HERD GEOGRAPHY [GEOG]",
        "02 // SUPPLY & DEMAND MATRIX [SND]",
        "03 // TRADE CORRIDORS & SANKEY [FLOW]",
        "04 // MARITIME AIS FLEET TRACKER [SHIP]",
        "05 // INDUSTRY COST WATERFALL [COST]",
        "06 // GLOBAL BOVINE NEWS WIRE [NEWS]"
    ])

    # -------------------------------------------------------------------------
    # SUB-TAB 1: BREED & HERD GEOGRAPHY [GEOG]
    # -------------------------------------------------------------------------
    with tab_geog:
        prod_df = prod_engine.get_country_summary_df()
        total_herd = prod_df["HERD (M Head)"].sum()
        total_prod = prod_df["BEEF PROD (1K MT)"].sum()
        top_prod_nation = prod_df.iloc[0]["COUNTRY"]

        # Metrics Deck
        st.markdown(
            f"""
            <div class='bbg-metrics-deck'>
                <div class='bbg-metric-card'>
                    <div class='bbg-metric-lbl'>TOTAL TRACKED HERD</div>
                    <div class='bbg-metric-val'>{total_herd:,.1f} M</div>
                    <div class='bbg-kpi-sub'>GLOBAL HEADCOUNT</div>
                </div>
                <div class='bbg-metric-card'>
                    <div class='bbg-metric-lbl'>TOTAL BEEF PRODUCTION</div>
                    <div class='bbg-metric-val'>{total_prod:,.0f}K MT</div>
                    <div class='bbg-kpi-sub'>CARCASS WEIGHT EQUIV</div>
                </div>
                <div class='bbg-metric-card'>
                    <div class='bbg-metric-lbl'>LARGEST PRODUCER</div>
                    <div class='bbg-metric-val'>{top_prod_nation}</div>
                    <div class='bbg-kpi-sub'>12,150K MT CWE / YR</div>
                </div>
                <div class='bbg-metric-card'>
                    <div class='bbg-metric-lbl'>LARGEST EXPORT HUB</div>
                    <div class='bbg-metric-val'>BRAZIL</div>
                    <div class='bbg-kpi-sub'>3,350K MT EXPORTS</div>
                </div>
                <div class='bbg-metric-card'>
                    <div class='bbg-metric-lbl'>DOMINANT GLOBAL BREEDS</div>
                    <div class='bbg-metric-val'>ANGUS / NELORE</div>
                    <div class='bbg-kpi-sub'>TEMPERATE & ZEBU HUBS</div>
                </div>
                <div class='bbg-metric-card'>
                    <div class='bbg-metric-lbl'>MONITORED PRODUCERS</div>
                    <div class='bbg-metric-val'>{len(prod_df)} NATIONS</div>
                    <div class='bbg-kpi-sub'>100% CENSUS COVERAGE</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

        # Global Geographic Bubble Map
        fig_map = go.Figure()
        fig_map.add_trace(go.Scattergeo(
            lon=prod_df["LON"],
            lat=prod_df["LAT"],
            text=prod_df["COUNTRY"],
            customdata=np.stack([
                prod_df["HERD (M Head)"],
                prod_df["BEEF PROD (1K MT)"],
                prod_df["CARCASS WT (LBS)"],
                prod_df["PRIMARY BREEDS"],
                prod_df["SUPPLY STATUS"]
            ], axis=-1),
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Herd Inventory: %{customdata[0]:.1f}M Head<br>"
                "Annual Beef Prod: %{customdata[1]:,d}K MT CWE<br>"
                "Avg Carcass Wt: %{customdata[2]:.1f} lbs<br>"
                "Primary Breeds: %{customdata[3]}<br>"
                "Status: %{customdata[4]}<extra></extra>"
            ),
            mode="markers+text",
            textposition="top center",
            textfont=dict(family="'Roboto Mono', monospace", size=8.5, color="#d1d4dc"),
            marker=dict(
                size=np.sqrt(prod_df["BEEF PROD (1K MT)"]) * 0.75 + 10,
                color=prod_df["HERD (M Head)"],
                colorscale="YlOrRd",
                showscale=True,
                colorbar=dict(
                    title=dict(text="Herd (M)", font=dict(size=9, color="#ff9900")),
                    tickfont=dict(size=8, color="#848e9c"),
                    thickness=10,
                    len=0.7
                ),
                line=dict(width=1.5, color="#ff9900"),
                opacity=0.88
            )
        ))

        fig_map.update_geos(
            projection_type="natural earth",
            showcoastlines=True,
            coastlinecolor="#202430",
            showland=True,
            landcolor="#0e1117",
            showocean=True,
            oceancolor="#05070a",
            showcountries=True,
            countrycolor="#1c202a",
            bgcolor="#05070a"
        )
        apply_dark_theme(fig_map, title="GLOBAL CATTLE PRODUCTION & HERD DENSITY WORLD MAP [GEOG <GO>]", height=450)
        st.plotly_chart(fig_map, width="stretch", config={"displayModeBar": False})

        # Columns: Left Summary Table, Right Country Dossier Inspector
        c_left, c_right = st.columns([7, 5])
        with c_left:
            st.markdown("<div class='bbg-section-title'>GLOBAL PRODUCER CENSUS & BREED COMPOSITION</div>", unsafe_allow_html=True)
            display_cols = ["CODE", "COUNTRY", "HERD (M Head)", "BEEF PROD (1K MT)", "EXPORTS (1K MT)", "IMPORTS (1K MT)", "CARCASS WT (LBS)", "PRIMARY BREEDS"]
            st.dataframe(prod_df[display_cols], hide_index=True, width="stretch")

        with c_right:
            st.markdown("<div class='bbg-section-title'>COUNTRY DOSSIER INSPECTOR</div>", unsafe_allow_html=True)
            sel_country = st.selectbox("Select Country", options=prod_df["CODE"].tolist(), index=0, format_func=lambda x: f"{x} - {prod_engine.get_country_detail(x)['name']}")
            c_meta = prod_engine.get_country_detail(sel_country)

            if c_meta:
                with st.container(border=True):
                    st.markdown(f"<div style='font-size:14px; font-weight:700; color:#ff9900;'>{c_meta['name'].upper()} [{sel_country}]</div>", unsafe_allow_html=True)
                    st.caption(f"Trade Role: {c_meta['trade_role']} | FMD Status: {c_meta['fmd_status']}")

                    d_col1, d_col2, d_col3 = st.columns(3)
                    d_col1.metric("Cattle Herd", f"{c_meta['cattle_herd_million_head']} M Head")
                    d_col2.metric("Beef Production", f"{c_meta['annual_beef_production_1000mt']:,}K MT")
                    d_col3.metric("Avg Carcass Wt", f"{c_meta['avg_carcass_weight_lbs']:.1f} lbs")

                    st.markdown("**Finishing Method Breakdown:**")
                    fin_dict = c_meta.get("finish_type_pct", {})
                    for f_name, f_pct in fin_dict.items():
                        st.progress(f_pct / 100.0, text=f"{f_name}: {f_pct}%")

                    st.markdown(f"**Primary Breeds:** `{', '.join(c_meta['primary_breeds'])}`")
                    st.markdown(f"**Supply Condition:** `{c_meta['supply_status']}` - {c_meta['supply_status_desc']}")
                    st.markdown(f"**Demand Condition:** `{c_meta['demand_status']}` - {c_meta['demand_status_desc']}")
                    st.markdown(f"**Biosecurity & Quarantine:** `{c_meta['quarantine_alerts']}`")

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

        # Global Cattle Breed Taxonomy Reference Table
        with st.container(border=True):
            st.markdown("<div class='bbg-section-title'>INSTITUTIONAL BOVINE BREED TAXONOMY & COMMERCIAL SPECIFICATIONS</div>", unsafe_allow_html=True)
            breed_df = prod_engine.get_breed_taxonomy_df()
            st.dataframe(breed_df, hide_index=True, width="stretch")

    # -------------------------------------------------------------------------
    # SUB-TAB 2: SUPPLY & DEMAND MATRIX [SND]
    # -------------------------------------------------------------------------
    with tab_snd:
        sd_df = sd_engine.get_sd_overview_df()

        # Metrics Deck
        st.markdown(
            """
            <div class='bbg-metrics-deck'>
                <div class='bbg-metric-card'>
                    <div class='bbg-metric-lbl'>HIGHEST SURPLUS HUB</div>
                    <div class='bbg-metric-val'>BRAZIL (+95)</div>
                    <div class='bbg-kpi-sub'>RECORD FEMALE CULLING</div>
                </div>
                <div class='bbg-metric-card'>
                    <div class='bbg-metric-lbl'>CRITICAL DEFICIT HUB</div>
                    <div class='bbg-metric-val'>USA (-74 NET)</div>
                    <div class='bbg-kpi-sub'>73-YR HERD LOW / EXTREME TIGHTNESS</div>
                </div>
                <div class='bbg-metric-card'>
                    <div class='bbg-metric-lbl'>WORLD LARGEST IMPORTER</div>
                    <div class='bbg-metric-val'>CHINA (3,650K MT)</div>
                    <div class='bbg-kpi-sub'>32.5% IMPORT DEPENDENCY</div>
                </div>
                <div class='bbg-metric-card'>
                    <div class='bbg-metric-lbl'>HIGHEST BEEF INTAKE</div>
                    <div class='bbg-metric-val'>ARGENTINA (48.5 KG)</div>
                    <div class='bbg-kpi-sub'>PER CAPITA / YEAR</div>
                </div>
                <div class='bbg-metric-card'>
                    <div class='bbg-metric-lbl'>LIVE CATTLE DEMAND HUB</div>
                    <div class='bbg-metric-val'>INDONESIA / EGYPT</div>
                    <div class='bbg-kpi-sub'>HALAL SLAUGHTER & FEEDLOTS</div>
                </div>
                <div class='bbg-metric-card'>
                    <div class='bbg-metric-lbl'>HERD EXPANSION LEADER</div>
                    <div class='bbg-metric-val'>AUSTRALIA (+75)</div>
                    <div class='bbg-kpi-sub'>POST-DROUGHT REBUILD COMPLETE</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

        # Charts: Net Balance and Herd Phase
        sd_col1, sd_col2 = st.columns(2)
        with sd_col1:
            fig_sd_bal = go.Figure()
            colors_sd = ["#00ff66" if val >= 0 else "#ff3b30" for val in sd_df["NET BALANCE (SD DIFF)"]]
            fig_sd_bal.add_trace(go.Bar(
                x=sd_df["COUNTRY"],
                y=sd_df["NET BALANCE (SD DIFF)"],
                marker=dict(color=colors_sd, line=dict(color="#1e222d", width=1)),
                hovertemplate="<b>%{x}</b><br>Net Imbalance: %{y}<extra></extra>"
            ))
            fig_sd_bal.add_hline(y=0, line_dash="dash", line_color="#848e9c")
            apply_dark_theme(fig_sd_bal, title="NET SUPPLY-DEMAND TENSION SPREAD (SUPPLY - DEMAND SCORE)", height=380)
            st.plotly_chart(fig_sd_bal, width="stretch", config={"displayModeBar": False})

        with sd_col2:
            fig_phase = go.Figure()
            colors_phase = ["#00ff66" if val >= 0 else "#ff3b30" for val in sd_df["HERD PHASE SCORE"]]
            fig_phase.add_trace(go.Bar(
                x=sd_df["COUNTRY"],
                y=sd_df["HERD PHASE SCORE"],
                marker=dict(color=colors_phase, line=dict(color="#1e222d", width=1)),
                hovertemplate="<b>%{x}</b><br>Herd Phase: %{y} (-100 Liquidation to +100 Retention)<extra></extra>"
            ))
            fig_phase.add_hline(y=0, line_dash="dash", line_color="#848e9c")
            apply_dark_theme(fig_phase, title="NATIONAL HERD CYCLE PHASE (-100 LIQUIDATION / +100 RETENTION)", height=380)
            st.plotly_chart(fig_phase, width="stretch", config={"displayModeBar": False})

        # Detailed S&D Scorecard Table
        with st.container(border=True):
            st.markdown("<div class='bbg-section-title'>GLOBAL REGIONAL SUPPLY / DEMAND BALANCE SCORECARD</div>", unsafe_allow_html=True)
            st.dataframe(sd_df, hide_index=True, width="stretch")

        # Biosecurity Alerts Table
        with st.container(border=True):
            st.markdown("<div class='bbg-section-title'>ACTIVE BIOSECURITY, PHYTOSANITARY & QUARANTINE PROTOCOLS</div>", unsafe_allow_html=True)
            bio_df = sd_engine.get_biosecurity_alerts_df()
            st.dataframe(bio_df, hide_index=True, width="stretch")

    # -------------------------------------------------------------------------
    # SUB-TAB 3: TRADE CORRIDORS & SANKEY [FLOW]
    # -------------------------------------------------------------------------
    with tab_flow:
        trade_df = trade_engine.get_trade_matrix_df()
        total_trade_vol = trade_df["volume_1000mt"].sum()
        total_trade_val = trade_df["val_usd_million"].sum()

        st.markdown(
            f"""
            <div class='bbg-metrics-deck'>
                <div class='bbg-metric-card'>
                    <div class='bbg-metric-lbl'>TOTAL BILATERAL VOLUME</div>
                    <div class='bbg-metric-val'>{total_trade_vol:,.0f}K MT</div>
                    <div class='bbg-kpi-sub'>ANNUAL MONITORED SHIPMENTS</div>
                </div>
                <div class='bbg-metric-card'>
                    <div class='bbg-metric-lbl'>ESTIMATED CARGO VALUE</div>
                    <div class='bbg-metric-val'>${total_trade_val/1000.0:,.2f} B</div>
                    <div class='bbg-kpi-sub'>USD TOTAL COMMODITY VALUE</div>
                </div>
                <div class='bbg-metric-card'>
                    <div class='bbg-metric-lbl'>LARGEST EXPORT CORRIDOR</div>
                    <div class='bbg-metric-val'>BRAZIL » CHINA</div>
                    <div class='bbg-kpi-sub'>1,450K MT ($6.8B USD)</div>
                </div>
                <div class='bbg-metric-card'>
                    <div class='bbg-metric-lbl'>TOP LIVE CATTLE CORRIDOR</div>
                    <div class='bbg-metric-val'>AUS » INDONESIA</div>
                    <div class='bbg-kpi-sub'>210K MT (~600,000 HEAD)</div>
                </div>
                <div class='bbg-metric-card'>
                    <div class='bbg-metric-lbl'>LEAN TRIMMINGS ARBITRAGE</div>
                    <div class='bbg-metric-val'>AUS / NZL » USA</div>
                    <div class='bbg-kpi-sub'>700K MT 90CL LEAN GROUND BEEF</div>
                </div>
                <div class='bbg-metric-card'>
                    <div class='bbg-metric-lbl'>PRIMARY TRANSPORT MODE</div>
                    <div class='bbg-metric-val'>40FT REEFER BOX</div>
                    <div class='bbg-kpi-sub'>84% OF MONITORED TONNAGE</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

        # 3-Tier Interactive Sankey Diagram
        labels, sources, targets, values, colors = trade_engine.build_sankey_data()
        fig_sankey = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=18,
                line=dict(color="#000000", width=0.5),
                label=labels,
                color=colors,
                hovertemplate="Node: %{label}<br>Volume: %{value:,.0f}K MT<extra></extra>"
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
                color="rgba(132, 142, 156, 0.22)",
                hovertemplate="Flow: %{source.label} » %{target.label}<br>Volume: %{value:,.0f}K MT CWE<extra></extra>"
            )
        )])
        apply_dark_theme(fig_sankey, title="GLOBAL BOVINE BILATERAL TRADE FLOWS: ORIGIN » COMMODITY » DESTINATION [SANKEY <GO>]", height=520)
        st.plotly_chart(fig_sankey, width="stretch", config={"displayModeBar": False})

        # Trade Corridors Matrix & Mode Breakdown
        fl_col1, fl_col2 = st.columns([8, 4])
        with fl_col1:
            st.markdown("<div class='bbg-section-title'>BILATERAL TRADE CORRIDORS & VOLUMES</div>", unsafe_allow_html=True)
            st.dataframe(trade_df, hide_index=True, width="stretch")

        with fl_col2:
            st.markdown("<div class='bbg-section-title'>TRANSPORTATION MODES</div>", unsafe_allow_html=True)
            mode_df = trade_df.groupby("mode")["volume_1000mt"].sum().reset_index()
            fig_mode = px.pie(
                mode_df,
                names="mode",
                values="volume_1000mt",
                color_discrete_sequence=["#ff9900", "#00cc99", "#00b4d8", "#e63946", "#f4a261"],
                hole=0.45
            )
            apply_dark_theme(fig_mode, title="TRADE VOLUME BY LOGISTICS MODE", height=350)
            st.plotly_chart(fig_mode, width="stretch", config={"displayModeBar": False})

    # -------------------------------------------------------------------------
    # SUB-TAB 4: MARITIME AIS FLEET TRACKER [SHIP]
    # -------------------------------------------------------------------------
    with tab_ship:
        fleet_df = ais_engine.get_fleet_telemetry_df()
        fleet_metrics = ais_engine.get_fleet_summary_metrics()

        st.markdown(
            f"""
            <div class='bbg-metrics-deck'>
                <div class='bbg-metric-card'>
                    <div class='bbg-metric-lbl'>TRACKED LIVESTOCK SHIPS</div>
                    <div class='bbg-metric-val'>{fleet_metrics['total_vessels_tracked']} VESSELS</div>
                    <div class='bbg-kpi-sub'>ACTIVE MARITIME AIS FLEET</div>
                </div>
                <div class='bbg-metric-card'>
                    <div class='bbg-metric-lbl'>TOTAL FLEET CAPACITY</div>
                    <div class='bbg-metric-val'>{fleet_metrics['total_fleet_capacity_head']:,} HEAD</div>
                    <div class='bbg-kpi-sub'>PURPOSE-BUILT CARRIERS</div>
                </div>
                <div class='bbg-metric-card'>
                    <div class='bbg-metric-lbl'>IN-TRANSIT CARGO VALUE</div>
                    <div class='bbg-metric-val'>${fleet_metrics['total_active_cargo_value_usd']/1e6:,.1f} M</div>
                    <div class='bbg-kpi-sub'>TOTAL DECLARED LIVESTOCK CIF</div>
                </div>
                <div class='bbg-metric-card'>
                    <div class='bbg-metric-lbl'>CHOKE POINT ALERTS</div>
                    <div class='bbg-metric-val' style='color:#ff9900;'>{fleet_metrics['vessels_in_choke_points']} SHIPS</div>
                    <div class='bbg-kpi-sub'>SUEZ / BAB-EL-MANDEB / MALACCA</div>
                </div>
                <div class='bbg-metric-card'>
                    <div class='bbg-metric-lbl'>AVERAGE FLEET SPEED</div>
                    <div class='bbg-metric-val'>{fleet_metrics['average_transit_speed_knots']:.1f} KTS</div>
                    <div class='bbg-kpi-sub'>CRUISING SERVICE SPEED</div>
                </div>
                <div class='bbg-metric-card'>
                    <div class='bbg-metric-lbl'>ANIMAL WELFARE MONITOR</div>
                    <div class='bbg-metric-val' style='color:#00ff66;'>ALL NOMINAL</div>
                    <div class='bbg-kpi-sub'>VENTILATION & WATER OK</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

        # Plotly Scattergeo World Map of Cattle Ships and Choke Points
        fig_ship_map = go.Figure()

        # Add Choke Points
        choke_points = ais_engine.get_choke_points()
        cp_lats = [cp["lat"] for cp in choke_points]
        cp_lons = [cp["lon"] for cp in choke_points]
        cp_names = [f"ALERT: {cp['name']} ({cp['risk_category']})" for cp in choke_points]

        fig_ship_map.add_trace(go.Scattergeo(
            lon=cp_lons,
            lat=cp_lats,
            text=cp_names,
            mode="markers+text",
            textposition="bottom center",
            textfont=dict(family="'Roboto Mono', monospace", size=8.5, color="#ff9900"),
            marker=dict(
                size=12,
                symbol="diamond",
                color="#ff3b30",
                line=dict(width=1.5, color="#ffffff")
            ),
            hoverinfo="text",
            name="Strategic Choke Points"
        ))

        # Add Vessels
        vessel_colors = ["#ff9900" if s == "CHOKE_POINT_ALERT" else "#00ff66" for s in fleet_df["STATUS"]]
        fig_ship_map.add_trace(go.Scattergeo(
            lon=fleet_df["LON"],
            lat=fleet_df["LAT"],
            text=fleet_df["VESSEL"],
            customdata=np.stack([
                fleet_df["FLAG"],
                fleet_df["SPEED (KTS)"],
                fleet_df["HEADING"],
                fleet_df["ORIGIN"],
                fleet_df["DESTINATION"],
                fleet_df["CARGO MANIFEST"],
                fleet_df["FODDER REMAINING (DAYS)"],
                fleet_df["HEAT STRESS RISK"],
                fleet_df["ETA"]
            ], axis=-1),
            hovertemplate=(
                "<b>%{text}</b> (Flag: %{customdata[0]})<br>"
                "Speed: %{customdata[1]:.1f} kts | Heading: %{customdata[2]}°<br>"
                "Route: %{customdata[3]} » %{customdata[4]} (ETA: %{customdata[8]})<br>"
                "Cargo: %{customdata[5]}<br>"
                "Fodder: %{customdata[6]} Days Remaining<br>"
                "Heat Stress: %{customdata[7]}<extra></extra>"
            ),
            mode="markers+text",
            textposition="top center",
            textfont=dict(family="'Roboto Mono', monospace", size=8.5, color="#f5f6f8"),
            marker=dict(
                size=11,
                symbol="triangle-up",
                color=vessel_colors,
                line=dict(width=1.2, color="#000000")
            ),
            name="Livestock Carriers"
        ))

        fig_ship_map.update_geos(
            projection_type="natural earth",
            showcoastlines=True,
            coastlinecolor="#202430",
            showland=True,
            landcolor="#0e1117",
            showocean=True,
            oceancolor="#05070a",
            showcountries=True,
            countrycolor="#1c202a",
            bgcolor="#05070a"
        )
        apply_dark_theme(fig_ship_map, title="REAL-TIME GLOBAL LIVESTOCK CARRIER AIS MARITIME TRACKING [SHIP <GO>]", height=480)
        st.plotly_chart(fig_ship_map, width="stretch", config={"displayModeBar": False})

        # Columns: Fleet Table & Vessel Dossier Inspector
        v_col1, v_col2 = st.columns([7, 5])
        with v_col1:
            st.markdown("<div class='bbg-section-title'>ACTIVE LIVESTOCK FLEET TELEMETRY</div>", unsafe_allow_html=True)
            v_disp_cols = ["VESSEL", "FLAG", "CAPACITY (HEAD)", "SPEED (KTS)", "STATUS", "ORIGIN", "DESTINATION", "ETA"]
            st.dataframe(fleet_df[v_disp_cols], hide_index=True, width="stretch")

        with v_col2:
            st.markdown("<div class='bbg-section-title'>VESSEL DOSSIER & ANIMAL WELFARE</div>", unsafe_allow_html=True)
            sel_imo = st.selectbox("Select Vessel", options=fleet_df["IMO"].tolist(), format_func=lambda x: ais_engine.get_vessel_by_imo(x)["name"])
            v_info = ais_engine.get_vessel_by_imo(sel_imo)

            if v_info:
                with st.container(border=True):
                    st.markdown(f"<div style='font-size:14px; font-weight:700; color:#ff9900;'>{v_info['name'].upper()}</div>", unsafe_allow_html=True)
                    st.caption(f"IMO: {v_info['imo']} | MMSI: {v_info['mmsi']} | Flag: {v_info['flag']} | Built: {v_info['built_year']}")

                    vm1, vm2, vm3 = st.columns(3)
                    vm1.metric("Capacity", f"{v_info['cattle_head_capacity']:,} Head")
                    vm2.metric("DWT", f"{v_info['dwt']:,} MT")
                    vm3.metric("Deck Area", f"{v_info['deck_area_sqm']:,} m²")

                    st.markdown(f"**Route:** `{v_info['origin_port']}` » `{v_info['destination_port']}` (ETA: `{v_info['eta_date']}`)")
                    st.markdown(f"**Cargo:** `{v_info['cargo_manifest']}` (Declared: `${v_info['cargo_val_usd']:,}` USD)")
                    st.markdown(f"**Position:** Lat `{v_info['current_lat']:.3f}`, Lon `{v_info['current_lon']:.3f}` @ `{v_info['current_speed']} kts` (Hdg: `{v_info['current_heading']}°`)")
                    st.markdown(f"**Choke Point Status:** `{v_info['choke_point_status']}`")

                    st.markdown("---")
                    st.markdown("<div style='font-size:11px; font-weight:700; color:#00cc99;'>ONBOARD ANIMAL WELFARE TELEMETRY</div>", unsafe_allow_html=True)
                    w1, w2 = st.columns(2)
                    w1.metric("Fodder Days Left", f"{v_info['fodder_days_remaining']} Days")
                    w2.metric("Water Generation", f"{v_info['water_generation_liters_day']:,} L/Day")
                    st.caption(f"Ventilation: {v_info['ventilation_air_changes_per_hr']} Air Changes/Hour | Heat Stress: {v_info['heat_stress_index']}")

        # Choke Points Table
        with st.container(border=True):
            st.markdown("<div class='bbg-section-title'>STRATEGIC MARITIME CHOKE POINTS & WAR RISK SURCHARGES</div>", unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(MARITIME_CHOKE_POINTS), hide_index=True, width="stretch")

    # -------------------------------------------------------------------------
    # SUB-TAB 5: INDUSTRY COST WATERFALL [COST]
    # -------------------------------------------------------------------------
    with tab_cost:
        st.markdown(
            """
            <div class='bbg-metrics-deck'>
                <div class='bbg-metric-card'>
                    <div class='bbg-metric-lbl'>MARINE MORTALITY INSURANCE</div>
                    <div class='bbg-metric-val'>1.4% - 3.8%</div>
                    <div class='bbg-kpi-sub'>BASE 2.25% OF CIF VALUE</div>
                </div>
                <div class='bbg-metric-card'>
                    <div class='bbg-metric-lbl'>LIVESTOCK CHARTER DAY RATE</div>
                    <div class='bbg-metric-val'>$32K - $52K</div>
                    <div class='bbg-kpi-sub'>TIME CHARTER $/DAY</div>
                </div>
                <div class='bbg-metric-card'>
                    <div class='bbg-metric-lbl'>VLSFO BUNKER FUEL</div>
                    <div class='bbg-metric-val'>$615 / MT</div>
                    <div class='bbg-kpi-sub'>SINGAPORE BUNKER BENCHMARK</div>
                </div>
                <div class='bbg-metric-card'>
                    <div class='bbg-metric-lbl'>FEEDLOT COST-OF-GAIN</div>
                    <div class='bbg-metric-val'>$1.18 / LB</div>
                    <div class='bbg-kpi-sub'>CORN $4.25 / BU RATION</div>
                </div>
                <div class='bbg-metric-card'>
                    <div class='bbg-metric-lbl'>PACKER GROSS MARGIN</div>
                    <div class='bbg-metric-val'>+$48.20 / HEAD</div>
                    <div class='bbg-kpi-sub'>CHOICE CUTOUT $312 / CWT</div>
                </div>
                <div class='bbg-metric-card'>
                    <div class='bbg-metric-lbl'>REEFER OCEAN FREIGHT</div>
                    <div class='bbg-metric-val'>$4,350 / 40FT</div>
                    <div class='bbg-kpi-sub'>SANTOS » SHANGHAI REEFER</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

        # Three Interactive Cost Calculators
        st.markdown("<div class='bbg-section-title'>INTERACTIVE INDUSTRY COST MODELERS</div>", unsafe_allow_html=True)
        calc1, calc2, calc3 = st.columns(3)

        with calc1:
            with st.container(border=True):
                st.markdown("<div style='font-size:12px; font-weight:700; color:#ff9900;'>1. LIVESTOCK TRANSIT MORTALITY INSURANCE</div>", unsafe_allow_html=True)
                c_val = st.number_input("Cargo CIF Value ($ USD)", min_value=1_000_000, max_value=50_000_000, value=18_500_000, step=500_000)
                is_war = st.checkbox("Bab-el-Mandeb / Red Sea War Risk (+0.75%)", value=True)
                is_heat = st.checkbox("Summer Heat Stress Corridor (+0.65%)", value=False)
                is_vet = st.checkbox("Accredited Vet Onboard (-0.20%)", value=True)

                ins_res = cost_engine.calculate_marine_mortality_insurance(c_val, is_war, is_heat, is_vet)
                st.metric("Final Insurance Premium Rate", f"{ins_res['final_premium_rate_pct']:.2f}%")
                st.metric("Total Insurance Cost", f"${ins_res['total_insurance_premium_usd']:,.2f}")
                st.caption(f"Shipper Policy Deductible: ${ins_res['shipper_deductible_usd']:,.2f}")

        with calc2:
            with st.container(border=True):
                st.markdown("<div style='font-size:12px; font-weight:700; color:#ff9900;'>2. FEEDLOT COST-OF-GAIN (COG)</div>", unsafe_allow_html=True)
                corn_p = st.slider("Corn Price ($/bushel)", min_value=3.0, max_value=8.0, value=4.25, step=0.25)
                ddgs_p = st.slider("DDGS Protein ($/ton)", min_value=120.0, max_value=350.0, value=195.0, step=5.0)
                hay_p = st.slider("Alfalfa Hay ($/ton)", min_value=100.0, max_value=300.0, value=180.0, step=10.0)

                cog_res = cost_engine.calculate_feedlot_cost_of_gain(corn_p, ddgs_p, hay_p)
                st.metric("Net Cost of Gain (COG)", f"${cog_res['cost_of_gain_usd_per_lb']:.2f} / lb", f"${cog_res['cost_of_gain_usd_per_cwt']:.2f} / cwt")
                st.metric("Total Finishing Cost (550 lbs)", f"${cog_res['total_finishing_cost_usd']:,.2f} / steer")
                st.caption(f"Feed Ration: ${cog_res['feed_ration_cost_usd']:.2f} | Yardage: ${cog_res['yardage_charge_usd']:.2f} | FCR: {cog_res['feed_conversion_ratio']}")

        with calc3:
            with st.container(border=True):
                st.markdown("<div style='font-size:12px; font-weight:700; color:#ff9900;'>3. MEAT PACKER GROSS PROCESSING SPREAD</div>", unsafe_allow_html=True)
                live_p = st.slider("Live Cattle Cash ($/cwt)", min_value=150.0, max_value=230.0, value=188.50, step=0.50)
                box_p = st.slider("Choice Boxed Beef Cutout ($/cwt)", min_value=240.0, max_value=380.0, value=312.00, step=1.00)

                pack_res = cost_engine.calculate_meat_packer_margin(live_p, box_p)
                st.metric("Net Packer Margin", f"${pack_res['net_packer_margin_usd_per_head']:+,.2f} / head", f"{pack_res['net_packer_margin_pct']:+.1f}%")
                st.metric("Total Gross Revenue", f"${pack_res['total_gross_revenue_usd']:,.2f}")
                st.caption(f"Live Animal Cost: ${pack_res['live_cattle_cost_usd']:,.2f} | Kill/Fab Cost: ${pack_res['kill_and_fab_cost_usd']:.2f}")

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

        # Supply Chain Waterfall & Freight Tables
        w_col1, w_col2 = st.columns([7, 5])
        with w_col1:
            st.markdown("<div class='bbg-section-title'>FARM-GATE TO RETAIL PACKER SUPPLY CHAIN WATERFALL</div>", unsafe_allow_html=True)
            wf_df = cost_engine.get_supply_chain_waterfall_df()

            fig_wf = go.Figure(go.Waterfall(
                name="Cost Build-up",
                orientation="v",
                measure=["relative"] * len(wf_df),
                x=[s.split(". ")[1] for s in wf_df["STAGE"]],
                textposition="outside",
                text=[f"${c:,.0f}" for c in wf_df["STAGE COST ($)"]],
                y=wf_df["STAGE COST ($)"],
                connector={"line": {"color": "#848e9c"}},
                decreasing={"marker": {"color": "#00ff66"}},
                increasing={"marker": {"color": "#ff9900"}}
            ))
            apply_dark_theme(fig_wf, title="SUPPLY CHAIN COST ACCUMULATION (USD PER FINISHED BOVINE)", height=400)
            st.plotly_chart(fig_wf, width="stretch", config={"displayModeBar": False})

        with w_col2:
            st.markdown("<div class='bbg-section-title'>OCEAN FREIGHT & LOGISTICS BENCHMARKS</div>", unsafe_allow_html=True)
            st.markdown("**Refrigerated Beef Container Freight (40ft HC Reefer):**")
            st.dataframe(cost_engine.get_reefer_ocean_rates_df(), hide_index=True, width="stretch")
            st.markdown("**Live Cattle Voyage Freight Rates ($/head):**")
            st.dataframe(cost_engine.get_maritime_freight_summary_df(), hide_index=True, width="stretch")

    # -------------------------------------------------------------------------
    # SUB-TAB 6: GLOBAL BOVINE NEWS WIRE [NEWS]
    # -------------------------------------------------------------------------
    with tab_news:
        st.markdown("<div class='bbg-section-title'>REAL-TIME AGRIBUSINESS & BOVINE COMMODITY NEWS WIRE [NEWS <GO>]</div>", unsafe_allow_html=True)

        n_col1, n_col2, n_col3 = st.columns([3, 3, 6])
        with n_col1:
            cat_choice = st.selectbox("Filter Category", ["ALL", "TRADE", "MARITIME", "CASH / PACKER", "BIOSECURITY", "CLIMATE", "POLICY"])
        with n_col2:
            imp_choice = st.selectbox("Filter Impact", ["ALL", "HIGH", "MEDIUM", "LOW"])
        with n_col3:
            search_query = st.text_input("Search News Headlines", placeholder="e.g. China, drought, feedlot, feeder, Brazil...")

        news_items = news_engine.fetch_live_headlines()

        # Apply filters
        filtered_news = []
        for item in news_items:
            if cat_choice != "ALL" and item["category"] != cat_choice:
                continue
            if imp_choice != "ALL" and item["impact"] != imp_choice:
                continue
            if search_query:
                q = search_query.lower()
                if q not in item["headline"].lower() and q not in item["summary"].lower() and q not in item["region"].lower():
                    continue
            filtered_news.append(item)

        st.caption(f"Showing {len(filtered_news)} real-time agribusiness dispatches (Refreshed continuously)")

        for article in filtered_news:
            sent = article["sentiment"]
            if sent == "BULLISH":
                sent_color = "#00ff66"
                sent_badge = "▲ BULLISH"
            elif sent == "BEARISH":
                sent_color = "#ff3b30"
                sent_badge = "▼ BEARISH"
            else:
                sent_color = "#848e9c"
                sent_badge = "■ NEUTRAL"

            imp = article["impact"]
            imp_color = "#ff3b30" if imp == "HIGH" else ("#ff9900" if imp == "MEDIUM" else "#00b4d8")

            with st.container(border=True):
                st.markdown(
                    f"""
                    <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;'>
                        <div>
                            <span style='background:#161922; color:#ff9900; padding:2px 6px; font-size:10px; font-weight:700; border:1px solid #ff9900; margin-right:6px;'>{article['time']}</span>
                            <span style='background:#12151c; color:#d1d4dc; padding:2px 6px; font-size:10px; font-weight:600; border:1px solid #1e222d; margin-right:6px;'>{article['category']}</span>
                            <span style='background:#12151c; color:#848e9c; padding:2px 6px; font-size:10px; font-weight:600; border:1px solid #1e222d; margin-right:6px;'>{article['region']}</span>
                            <span style='background:{imp_color}22; color:{imp_color}; padding:2px 6px; font-size:10px; font-weight:700; border:1px solid {imp_color};'>{article['impact']} IMPACT</span>
                        </div>
                        <div>
                            <span style='color:{sent_color}; font-weight:700; font-size:11px;'>{sent_badge}</span>
                        </div>
                    </div>
                    <div style='font-size:12px; font-weight:700; color:#f5f6f8; margin:6px 0;'>{article['headline']}</div>
                    <div style='font-size:11px; color:#b0b5c0; line-height:1.4;'>{article['summary']}</div>
                    """,
                    unsafe_allow_html=True
                )
