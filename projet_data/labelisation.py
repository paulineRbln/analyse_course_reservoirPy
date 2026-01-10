import pandas as pd
import numpy as np
import glob
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.interpolate import interp1d

# --- CONFIGURATION ---
DATA_DIR = "../projet_data/data/" 
OUTPUT_DIR = "../projet_data/data_labeled/"
WINDOW_SIZE = 30

import os
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

files = glob.glob(f"{DATA_DIR}/course*.csv")
all_data = []

for f in files:
    try:
        df = pd.read_csv(f, sep=';', decimal=',')
        # On ne garde que les moments où on court vraiment
        # On lisse pour enlever le bruit GPS
        df['speed_smooth'] = df['speed_kmh'].rolling(WINDOW_SIZE, center=True).mean()
        df['fc_smooth'] = df['FC'].rolling(WINDOW_SIZE, center=True).mean()
        
        # Filtre : On garde seulement quand on court (> 5 km/h) et cardio actif (> 80 bpm)
        clean_df = df[(df['speed_smooth'] > 5) & (df['fc_smooth'] > 80)].copy()
        all_data.append(clean_df[['speed_smooth', 'fc_smooth']])
    except Exception as e:
        print(f"Erreur lecture {f}: {e}")

total_df = pd.concat(all_data)

# On arrondit la vitesse à 0.5 km/h près pour faire des groupes
total_df['speed_bin'] = (total_df['speed_smooth'] * 2).round() / 2

# Calcul des statistiques par palier de vitesse
profile = total_df.groupby('speed_bin')['fc_smooth'].agg(['mean', 'std']).reset_index()
profile = profile.fillna(0)

# Création des fonctions d'interpolation (pour prédire la FC à n'importe quelle vitesse)
# Si on court à une vitesse inconnue, on extrapole
get_expected_fc = interp1d(profile['speed_bin'], profile['mean'], kind='linear', fill_value="extrapolate")
get_std_fc = interp1d(profile['speed_bin'], profile['std'], kind='linear', fill_value="extrapolate")

print(f"Profil établi sur {len(total_df)} points de mesure.")


def define_label(row):
    # Z-score = {FC_réelle - FC_théorique}/ {EcartType}
    # > 1 : Je suis 1 écart-type au-dessus de la normale
    if row['std_ref'] == 0: return "Normal" 
    
    z_score = (row['fc_smooth'] - row['fc_ref']) / row['std_ref']
    
    if z_score > 1.0:
        return "Sur-régime"      
    elif z_score < -1.0:
        return "Sous-régime"     
    else:
        return "Normal"         

for f in files:
    filename = os.path.basename(f)
    df = pd.read_csv(f, sep=';', decimal=',')
    
    # 1. Prétraitement
    df['speed_smooth'] = df['speed_kmh'].rolling(WINDOW_SIZE, min_periods=1).mean()
    df['fc_smooth'] = df['FC'].rolling(WINDOW_SIZE, min_periods=1).mean()
    
    # 2. Calcul des références pour chaque point
    df['fc_ref'] = get_expected_fc(df['speed_smooth'])
    df['std_ref'] = get_std_fc(df['speed_smooth'])
    
    # 3. Calcul de l'écart (Différence FC Réelle - FC Théorique)
    df['fc_delta'] = df['fc_smooth'] - df['fc_ref']
    
    # 4. Application du Label
    mask_run = (df['speed_smooth'] > 5) & (df['fc_smooth'] > 60)
    df.loc[mask_run, 'label_effort'] = df[mask_run].apply(define_label, axis=1)
    df.loc[~mask_run, 'label_effort'] = "Repos/Arret"
    
    # 5. Sauvegarde
    save_path = f"{OUTPUT_DIR}/labeled_{filename}"
    df.to_csv(save_path, index=False, sep=';')
    
    # Stats rapides
    counts = df['label_effort'].value_counts()
    pct_sur = counts.get('Sur-régime', 0) / len(df) * 100
    print(f"   📄 {filename} : {pct_sur:.1f}% de temps en Sur-régime -> Sauvegardé.")
