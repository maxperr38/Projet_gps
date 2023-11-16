from flask import Flask, render_template, request
import requests
from zeep import Client

app = Flask(__name__)
print("test")

def obtenir_itineraire_defaut():
    # Coordonnées de Grenoble et Lyon
    coord_grenoble = "45.188529,5.724524"
    coord_lyon = "45.757814,4.832011"
    
    # URL de l'API OSRM
    url = f"http://router.project-osrm.org/route/v1/driving/{coord_grenoble};{coord_lyon}?overview=false"
    
    # Effectuer la requête
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erreur : {response.status_code}")
        return {"routes": []}  # Retourner une structure vide en cas d'erreur

itineraire_defaut = obtenir_itineraire_defaut()

def obtenir_liste_vehicules():
    url_liste = "https://api.chargetrip.io/graphql"
    
    headers = {
         'x-client-id': '65265ed612e5356e23ce69ad',
         'x-app-id': '65265ed612e5356e23ce69af',
        "Content-Type": "application/json"
    }

    vehicules = []
    page = 0
    size = 100

    while True:
        query = {
            "query": """
            query vehicleList($page: Int, $size: Int) {
                vehicleList(page: $page, size: $size) {
                    id
                    naming {
                        make
                        model
                        chargetrip_version
                    }
                    media {
                        image {
                            thumbnail_url
                        }
                    }
                    range {
                        chargetrip_range {
                            best
                            worst
                        }
                    }
                }
            }
            """,
            "variables": {
                "page": page,
                "size": size
            }
        }

        reponse = requests.post(url_liste, json=query, headers=headers)
        if reponse.status_code == 200:
            data = reponse.json()
            batch_vehicules = data["data"]["vehicleList"]
            vehicules.extend(batch_vehicules)
            
            # Si moins de 100 véhicules sont retournés, c'est qu'on a récupéré tous les véhicules.
            if len(batch_vehicules) < 100:
                break

            # Sinon, passez à la page suivante.
            page += 1
        else:
            # En cas d'erreur, arrêtez la boucle.
            break

    return vehicules

@app.route('/', methods=['GET', 'POST'])
def index():
    
    coordonnees = {"lat": 45.1, "lng": 5.7667}
    result = None
    charge_points = None
    itineraire = itineraire_defaut
    #API_KEY = "652796e112e5356e23ce75f6"
    end_lat = 0.0
    start_lat = 0.0
    end_lng = 0.0
    start_lng = 0.0
    start_coords = None
    end_coords = None
    liste_vehicules = obtenir_liste_vehicules()
    vehicule_choisi = None
    # ... (reste du code)

    if request.method == 'POST':
        # ... (reste du code pour la méthode POST)
        v = float(request.form.get('v'))
        #autonomie = float(request.form.get('autonomie'))
        #temps_charge = float(request.form.get('temps_charge'))
        
        start_lat = float(request.form.get('start_lat')) 
        start_lng = float(request.form.get('start_lng')) 
        end_lat = float(request.form.get('end_lat')) 
        end_lng = float(request.form.get('end_lng'))
        start_coords = (float(request.form.get('start_lat')), float(request.form.get('start_lng')))
        end_coords = (float(request.form.get('end_lat')), float(request.form.get('end_lng')))
        
        vehicule_id = request.form.get('vehicule')
        vehicule_choisi = next((v for v in liste_vehicules if v['id'] == vehicule_id), None)
        autonomie = vehicule_choisi['range']['chargetrip_range']['best'] if vehicule_choisi else 0
        #temps_charge = sum(connector['time'] for connector in vehicule_choisi['connectors']) / len(vehicule_choisi['connectors']) if vehicule_choisi and vehicule_choisi['connectors'] else 0
        if vehicule_choisi and 'connectors' in vehicule_choisi and vehicule_choisi['connectors']:
            temps_charge = vehicule_choisi['connectors'][0]['time']
        else:
            temps_charge = 0
        # Utilisation du client SOAP pour obtenir le résultat
        client = Client('http://192.168.141.59:8000/?wsdl')
        routing_url = f"http://router.project-osrm.org/route/v1/driving/{start_lng},{start_lat};{end_lng},{end_lat}?overview=false"
        response = requests.get(routing_url)
        if response.status_code == 200:
            itineraire = response.json()
            d = itineraire['routes'][0]['distance'] / 1000
        else:
            print(f"Erreur : {response.status_code}")
            itineraire = {"routes": []}  # Gérer l'erreur et utiliser une structure vide
        result = client.service.temps(d, v, autonomie, temps_charge)
        
        # Interrogation de l'API OpenDataSoft
        rows = 50  # Nombre de résultats souhaités
        #url = f"https://odre.opendatasoft.com/api/records/1.0/search/?dataset=bornes-irve&rows={rows}&geofilter.distance={coordonnees['lat']},{coordonnees['lng']},20000"
        url = f"https://odre.opendatasoft.com/api/records/1.0/search/?dataset=bornes-irve&rows={rows}&geofilter.distance={start_lat},{start_lng},20000"
        response = requests.get(url)
        
        
        if response.status_code == 200:
            charge_points = response.json().get('records', [])

    return render_template('page.html', result=result, coordonnees=coordonnees, charge_points=charge_points, itineraire=itineraire, start_coords=start_coords, end_coords=end_coords,vehicules=liste_vehicules, vehicule_choisi=vehicule_choisi)

if __name__ == '__main__':
    app.run(debug=True)

    
    
