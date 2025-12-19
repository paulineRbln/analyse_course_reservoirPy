import pandas as pd
import matplotlib.pyplot as plt

# Lire les données depuis le fichier CSV
df = pd.read_csv('./data/course5.csv', sep=';')
df = df.iloc[0:500]

# Convertir la colonne Time en datetime
df['Time'] = pd.to_datetime(df['Time'])

# Créer un graphique
plt.figure(figsize=(10,6))

# Tracer la vitesse
plt.plot(df['Time'], df['speed_kmh'], label='Vitesse (km/h)', color='blue', marker='o')
# Tracer la fréquence cardiaque
plt.plot(df['Time'], df['FC'], label='FC (bpm)', color='red', marker='x')
# Tracer la distance
plt.plot(df['Time'], df['km'], label='Distance (km)', color='green', marker='s')

# Ajouter titre et légende
plt.title('Données de course')
plt.xlabel('Temps')
plt.ylabel('Valeurs')
plt.legend()
plt.grid(True)

# Afficher le graphique
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
