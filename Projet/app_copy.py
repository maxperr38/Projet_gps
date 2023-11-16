from flask import Flask, render_template, request
import requests
from zeep import Client

app = Flask(__name__)
print("test")
@app.route('/', methods=['GET', 'POST'])
def index():
    
    coordonnees = {"lat": 45.1, "lng": 5.7667}
    result = None
    charge_points = None
    itineraire = None
    API_KEY = "214b4197499b29ec9ba86ef1100ca6c0"
    end_lat = 0.0
    start_lat = 0.0
    end_lng = 0.0
    start_lng = 0.0

    if request.method == 'POST':
        d = float(request.form.get('d'))
        v = float(request.form.get('v'))
        autonomie = float(request.form.get('autonomie'))
        temps_charge = float(request.form.get('temps_charge'))
        
        start_lat = float(request.form.get('start_lat')) 
        start_lng = float(request.form.get('start_lng')) 
        end_lat = float(request.form.get('end_lat')) 
        end_lng = float(request.form.get('end_lng')) 
        
        # Utilisation du client SOAP pour obtenir le résultat
        client = Client('http://192.168.141.59:8000/?wsdl')
        result = client.service.temps(d, v, autonomie, temps_charge)
        
        # Interrogation de l'API OpenDataSoft
        rows = 50  # Nombre de résultats souhaités
        url = f"https://odre.opendatasoft.com/api/records/1.0/search/?dataset=bornes-irve&rows={rows}&geofilter.distance={coordonnees['lat']},{coordonnees['lng']},10000"
        response = requests.get(url)
        
        
        if response.status_code == 200:
            charge_points = response.json().get('records', [])
        
         # Ici, vous pouvez ajouter le code pour interroger l'API de routage avec les coordonnées de départ et d'arrivée pour obtenir l'itinéraire
        # Assurez-vous d'avoir une clé API valide pour l'API de routage que vous allez utiliser.
        # Par exemple, pour l'API OpenStreetMap:
        routing_url = f"https://maps.open-street.com/api/route/?origin={start_lat},{start_lng}&destination={end_lat},{end_lng}&mode=driving&key={API_KEY}"

                        #https://maps.open-street.com/api/route/?origin=48.856614,2.3522219&destination=45.764043,4.835659&mode=driving&key=cle-fournie
        response = requests.get(routing_url)
        if response.status_code == 200:
            itineraire = response.json()
        
    return render_template('page.html', result=result, coordonnees=coordonnees, charge_points=charge_points, itineraire=itineraire)

if __name__ == '__main__':
    app.run(debug=True)

    
    
    
