import pandas as pd

# 1. Chargement du CSV
df = pd.read_csv('taxi_zone_lookup.csv')

# On remplace tous les vides (NaN) par "Unknown"
df = df.fillna("Unknown")

# On remplace les textes bizarres "N/A" par "Unknown" pour uniformiser
df.replace("N/A", "Unknown", inplace=True)
df.replace("NV", "Unknown", inplace=True) # Parfois présent pour dire Null Value

# On récupère la liste unique des noms de Boroughs
unique_boroughs = df['Borough'].unique()

borough_map = {} 
print("--INSERTION DES ARRONDISSEMENTS (Borough)")
print("INSERT INTO Borough (borough_id, borough_name) VALUES")

current_id = 1
first_line = True

for borough_name in unique_boroughs:
    # On convertit en string pour être sûr (évite le crash float)
    b_name = str(borough_name).strip()
    
    # Gestion des virgules SQL
    if not first_line:
        print(",")
    first_line = False

    safe_name = b_name.replace("'", "''")
    borough_map[b_name] = current_id
    
    # On affiche la ligne SQL
    print(f"({current_id}, '{safe_name}')", end="")
    current_id += 1

print(";") 
print("\n" + "="*50 + "\n")


# --- ÉTAPE 2 : GÉNÉRER LES LOCATIONS (Zones) ---
print("--INSERTION DES ZONES (Location_table)")
print("INSERT INTO Location_table (pulocation_id, zone_name, service_zone, borough_id) VALUES")

first_line = True

for index, row in df.iterrows():
    loc_id = row['LocationID']
    
    # Nettoyage des chaînes
    zone = str(row['Zone']).replace("'", "''")
    service = str(row['service_zone']).replace("'", "''")
    borough_name = str(row['Borough']).strip()
    
    # Récupération de l'ID
    # Sécurité : Si jamais le borough n'est pas trouvé
    if borough_name in borough_map:
        borough_id = borough_map[borough_name]
    else:
        # Cas de secours extrême
        borough_id = borough_map.get("Unknown", 1) 

    if not first_line:
        print(",")
    first_line = False
    
    print(f"({loc_id}, '{zone}', '{service}', {borough_id})", end="")

print(";")