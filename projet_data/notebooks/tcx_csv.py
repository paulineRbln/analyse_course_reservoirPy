import xml.etree.ElementTree as ET
import csv
import os

# Dossier contenant tes fichiers TCX
folder_path = 'data'  # à remplacer par ton dossier

# Namespace du fichier TCX
ns = {
    'tcx': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
    'ext': 'http://www.garmin.com/xmlschemas/ActivityExtension/v2'
}

# Parcourir tous les fichiers .tcx du dossier
for filename in os.listdir(folder_path):
    if filename.endswith('.tcx'):
        file_path = os.path.join(folder_path, filename)
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Nom du CSV de sortie basé sur le fichier TCX
        csv_filename = os.path.splitext(filename)[0] + '.csv'
        csv_path = os.path.join(folder_path, csv_filename)

        with open(csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(['Time', 'km', 'speed_kmh', 'FC'])

            for trackpoint in root.findall('.//tcx:Trackpoint', ns):
                time = trackpoint.find('tcx:Time', ns)
                distance = trackpoint.find('tcx:DistanceMeters', ns)
                hr = trackpoint.find('tcx:HeartRateBpm/tcx:Value', ns)
                speed = trackpoint.find('tcx:Extensions/ext:TPX/ext:Speed', ns)

                km = float(distance.text)/1000 if distance is not None else ''
                spd = float(speed.text)*3.6 if speed is not None else ''  # convertir m/s en km/h

                writer.writerow([
                    time.text if time is not None else '',
                    f"{km:.3f}" if km != '' else '',
                    f"{spd:.2f}" if spd != '' else '',
                    hr.text if hr is not None else ''
                ])

        print(f"{csv_filename} généré avec succès !")
