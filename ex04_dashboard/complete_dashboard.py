import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text

# -----------------------------
# Config page
# -----------------------------
st.set_page_config(page_title="NYC Taxi – Warehouse Dashboard", layout="wide")
st.title("NYC Taxi – Dashboard (PostgreSQL Data Warehouse)")

DB_URL = "postgresql://postgres:postgres@localhost:5432/taxidb"

@st.cache_resource
def get_engine():
    return create_engine(DB_URL, pool_pre_ping=True)

engine = get_engine()

def q(sql: str, params=None) -> pd.DataFrame:
    """Helper SQL -> DataFrame (safe params)."""
    return pd.read_sql(text(sql), engine, params=params or {})

# -----------------------------
# Sidebar filters
# -----------------------------
st.sidebar.header("Filtres")

months_df = q("SELECT DISTINCT month FROM trips WHERE month IS NOT NULL ORDER BY month;")
all_months = months_df["month"].tolist()

selected_months = st.sidebar.multiselect(
    "Mois (YYYY-MM)",
    options=all_months,
    default=all_months[-6:] if len(all_months) >= 6 else all_months
)
if not selected_months:
    st.warning("Sélectionne au moins un mois.")
    st.stop()

# Vendors
vendors_df = q("SELECT vendor_id, vendor_name FROM vendor ORDER BY vendor_name;")
vendor_map = dict(zip(vendors_df["vendor_name"], vendors_df["vendor_id"]))
selected_vendors = st.sidebar.multiselect("Vendors", options=list(vendor_map.keys()), default=[])

# Boroughs (pickup) - on ne propose pas Unknown dans le filtre
borough_df = q("""
               SELECT borough_id, borough_name
               FROM borough
               WHERE borough_name <> 'Unknown'
               ORDER BY borough_name;
               """)
borough_map = dict(zip(borough_df["borough_name"], borough_df["borough_id"]))
selected_boroughs = st.sidebar.multiselect("Boroughs (pickup)", options=list(borough_map.keys()), default=[])

# -----------------------------
# WHERE dynamique (cohérent partout)
# -----------------------------
# Base filters
where_clauses = ["t.month = ANY(:months)"]
params = {"months": selected_months}

# Optional filters
if selected_vendors:
    where_clauses.append("t.vendor_id = ANY(:vendors)")
    params["vendors"] = [vendor_map[v] for v in selected_vendors]

# Pour filtrer borough pickup, on a besoin du join location_table (alias l)
if selected_boroughs:
    where_clauses.append("l.borough_id = ANY(:boroughs)")
    params["boroughs"] = [borough_map[b] for b in selected_boroughs]

# Anti-Unknown pour les zones/boroughs pickup (ça retire Unknown des pickups)
# 264 chez toi = Unknown (vu dans insertion.sql)
where_clauses.append("t.pickup_location_id <> 264")
where_clauses.append("COALESCE(l.zone_name,'') <> 'Unknown'")
where_clauses.append("COALESCE(b.borough_name,'') <> 'Unknown'")

WHERE = " AND ".join(where_clauses)

# -----------------------------
# KPI
# -----------------------------
kpi = q(f"""
SELECT
    COUNT(*) AS trips,
    SUM(t.total_amount) AS revenue,
    AVG(t.total_amount) AS avg_total,
    AVG(t.trip_distance) AS avg_distance,
    100.0 * AVG(CASE WHEN t.tip_amount > 0 THEN 1 ELSE 0 END) AS tip_rate_pct
FROM trips t
JOIN location_table l ON t.pickup_location_id = l.pulocation_id
JOIN borough b ON l.borough_id = b.borough_id
WHERE {WHERE};
""", params)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Courses", f"{int(kpi.loc[0,'trips']):,}")
c2.metric("Revenu total", f"{float(kpi.loc[0,'revenue'] or 0):.2f} $")
c3.metric("Prix moyen", f"{float(kpi.loc[0,'avg_total'] or 0):.2f} $")
c4.metric("Distance moyenne", f"{float(kpi.loc[0,'avg_distance'] or 0):.2f} miles")
c5.metric("Tip rate", f"{float(kpi.loc[0,'tip_rate_pct'] or 0):.2f} %")

st.divider()

# -----------------------------
# 1) Comparatif mensuel (core)
# -----------------------------
monthly = q(f"""
SELECT
    t.month,
    COUNT(*) AS trips,
    SUM(t.total_amount) AS revenue,
    AVG(t.total_amount) AS avg_total,
    AVG(t.trip_distance) AS avg_distance,
    100.0 * AVG(CASE WHEN t.tip_amount > 0 THEN 1 ELSE 0 END) AS tip_rate_pct
FROM trips t
JOIN location_table l ON t.pickup_location_id = l.pulocation_id
JOIN borough b ON l.borough_id = b.borough_id
WHERE {WHERE}
GROUP BY t.month
ORDER BY t.month;
""", params)

colA, colB = st.columns(2)
with colA:
    st.plotly_chart(px.line(monthly, x="month", y="trips", markers=True, title="Courses par mois"),
                    use_container_width=True)
with colB:
    st.plotly_chart(px.line(monthly, x="month", y="revenue", markers=True, title="Revenu par mois ($)"),
                    use_container_width=True)

colC, colD, colE = st.columns(3)
with colC:
    st.plotly_chart(px.line(monthly, x="month", y="avg_total", markers=True, title="Prix moyen ($)"),
                    use_container_width=True)
with colD:
    st.plotly_chart(px.line(monthly, x="month", y="avg_distance", markers=True, title="Distance moyenne (miles)"),
                    use_container_width=True)
with colE:
    st.plotly_chart(px.line(monthly, x="month", y="tip_rate_pct", markers=True, title="Tip rate (%)"),
                    use_container_width=True)

st.divider()

# -----------------------------
# 2) Analyse temporelle : heure
# -----------------------------
hourly = q(f"""
SELECT
    EXTRACT(HOUR FROM t.pickup_datetime) AS hour,
    t.month,
    COUNT(*) AS trips,
    AVG(t.total_amount) AS avg_total
FROM trips t
JOIN location_table l ON t.pickup_location_id = l.pulocation_id
JOIN borough b ON l.borough_id = b.borough_id
WHERE {WHERE}
GROUP BY hour, t.month
ORDER BY hour;
""", params)

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(px.line(hourly, x="hour", y="trips", color="month", markers=True,
                            title="Courses par heure (comparatif mois)"),
                    use_container_width=True)
with col2:
    st.plotly_chart(px.line(hourly, x="hour", y="avg_total", color="month", markers=True,
                            title="Prix moyen par heure (comparatif mois)"),
                    use_container_width=True)

st.divider()

# -----------------------------
# 3) Vendors & paiements (sans Unknown)
# -----------------------------
vendor_share = q(f"""
SELECT
    t.month,
    v.vendor_name,
    COUNT(*) AS trips
FROM trips t
JOIN vendor v ON t.vendor_id = v.vendor_id
JOIN location_table l ON t.pickup_location_id = l.pulocation_id
JOIN borough b ON l.borough_id = b.borough_id
WHERE {WHERE}
GROUP BY t.month, v.vendor_name
ORDER BY t.month, trips DESC;
""", params)

# Ici on exclut les paiements non souhaités
pay = q(f"""
SELECT
    t.month,
    p.payment_name,
    COUNT(*) AS trips
FROM trips t
JOIN payment p ON t.payment_type_id = p.payment_type_id
JOIN location_table l ON t.pickup_location_id = l.pulocation_id
JOIN borough b ON l.borough_id = b.borough_id
WHERE {WHERE}
  AND p.payment_name NOT IN ('Unknown', 'Voided trip')
  -- si tu veux encore plus "clean", décommente :
  -- AND p.payment_name NOT IN ('Unknown','Voided trip','No charge','Dispute')
GROUP BY t.month, p.payment_name
ORDER BY t.month, trips DESC;
""", params)

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(px.bar(vendor_share, x="vendor_name", y="trips", color="month",
                           barmode="group", title="Parts de marché Vendor"),
                    use_container_width=True)
with col2:
    st.plotly_chart(px.bar(pay, x="payment_name", y="trips", color="month",
                           barmode="group", title="Répartition paiements (clean)"),
                    use_container_width=True)

st.divider()

# -----------------------------
# 4) Top zones pickup (clean, sans Unknown)
# -----------------------------s
top_pickup = q(f"""
SELECT
    t.month,
    b.borough_name,
    l.zone_name,
    COUNT(*) AS trips
FROM trips t
JOIN location_table l ON t.pickup_location_id = l.pulocation_id
JOIN borough b ON l.borough_id = b.borough_id
WHERE {WHERE}
GROUP BY t.month, b.borough_name, l.zone_name
ORDER BY trips DESC
LIMIT 20;
""", params)

fig = px.bar(
    top_pickup,
    x="trips",
    y="zone_name",
    color="borough_name",
    orientation="h",
    title="Top 20 zones de PICKUP (clean)"
)
fig.update_layout(height=650)
st.plotly_chart(fig, use_container_width=True)

st.caption("Perf: rester sur des requêtes agrégées + filtres. 20M+ lignes → éviter SELECT *.")
