import streamlit as st
import pandas as pd
from sqlalchemy import create_engine # traduit le langage Python en SQL
import plotly.express as px # Pour les graphe interactifs

st.set_page_config(page_title="NYC Taxi Dashboard", layout="wide")
st.title("Dashboard NYC Taxi Data Warehouse")


# Très important pour éviter que python se connecte à chaque milliseconde Postgre
@st.cache_resource
def get_connection():
    return create_engine('postgresql://postgres:postgres@localhost:5432/taxidb')

try:
    engine = get_connection()
    st.sidebar.success('Base de données connectée')
except Exception as e:
    st.error(f"Erreur de connexion : {e} ")
    st.stop()


#On affiche le nombre total de course, la moyenne des prix et la moyenne des distances. -> Une ligne
trips_query = """
              SELECT count(*) as total_courses,
                     avg(total_amount) as prix_moyen, 
                     avg(trip_distance) as distance_moyenne
              FROM Trips
"""
df_trips = pd.read_sql(trips_query, engine)


#On affiche le nom du vendeur et le nombre de courses qu'il a faites.
vendor_query = """
    SELECT v.vendor_name, COUNT(t.trip_id) as nb_courses
    FROM Trips t
    JOIN Vendor v ON t.vendor_id = v.vendor_id
    GROUP BY v.vendor_name
"""

df_vendor = df_vendor = pd.read_sql(vendor_query, engine)


#On affiche combien de course ont été payées par Carte Bancaire ? Combien par Espèces ? Combien par Inconnu ?
pay_query = """
            SELECT p.payment_name, COUNT(t.trip_id) as nb_courses
            FROM Trips t
                     JOIN Payment p ON t.payment_type_id = p.payment_type_id
            GROUP BY p.payment_name \
"""
df_pay = pd.read_sql(pay_query, engine)



#Nom de la zone, nom de l'arrondissement et nombre de courses qui sont parties de là.
loc_query = """
            SELECT l.zone_name, b.borough_name, COUNT(t.trip_id) as nb_courses
            FROM Trips t
                     JOIN Location_table l ON t.pickup_location_id = l.pulocation_id
                     JOIN Borough b ON l.borough_id = b.borough_id
            GROUP BY l.zone_name, b.borough_name
            ORDER BY nb_courses DESC
                LIMIT 10 \
"""

df_loc = pd.read_sql(loc_query, engine)

#Affichage des réponses des requêtes
c1, c2, c3 = st.columns(3)

total = df_trips['total_courses'][0]
prix = df_trips['prix_moyen'][0]
distance = df_trips['distance_moyenne'][0]

#le if else sert à gérer l'absence de données
c1.metric("Total Courses", f"{total:,}")
c2.metric("Prix Moyen", f"{prix:.2f} $" if prix else "0.00 $")
c3.metric("Distance Moyenne", f"{distance:.2f} miles" if distance else "0.00 miles")

st.divider()

colonne_gauche, colonne_droite = st.columns(2)

with colonne_gauche:
    st.subheader("Parts de marché des Vendeurs")
    fig_vendor = px.bar(df_vendor, x='vendor_name', y='nb_courses', color='vendor_name')
    st.plotly_chart(fig_vendor, use_container_width=True)

with colonne_droite:
    st.subheader("Mode de paiement")
    fig_pay = px.pie(df_pay, values="nb_courses", names="payment_name", hole=0.4)
    st.plotly_chart(fig_pay, use_container_width=True)


st.divider()
st.subheader("Top 10 des Zones de Départ")
fig_loc = px.bar(df_loc, x="nb_courses", y="zone_name", orientation='h', color="borough_name")
st.plotly_chart(fig_loc, use_container_width=True)