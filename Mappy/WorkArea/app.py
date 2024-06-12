from flask import Flask, render_template, request
import requests
#import googlemaps
from dotenv import load_dotenv
import os
from requests.utils import quote

# .env 파일 로드
load_dotenv()
api_key = os.getenv('GOOGLE_MAPS_API_KEY')

app = Flask(__name__)
'''
def get_coordinates(address):
    gmaps = googlemaps.Client(key=api_key)
    
    try:
        geocode_result = gmaps.geocode(address)
        if geocode_result and geocode_result[0]['geometry']['location']:
            location = geocode_result[0]['geometry']['location']
            return location['lat'], location['lng']
        else:
            print(f"Geocoding error for address '{address}': No results found")
            return None, None
    except googlemaps.exceptions.ApiError as e:
        print(f"API error: {e}")
        return None, None
 '''   

def get_coordinates(address):
    # 주소를 URL로 인코딩
    encoded_address = quote(address)
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"
    response = requests.get(url)
    data = response.json()

    if data['status'] == 'OK':
        location = data['results'][0]['geometry']['location']
        return location['lat'], location['lng']
    else:
        print(f"Geocoding error for address '{address}': {data['status']}")
        return None, None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/schedule')
def schedule():
    return render_template('schedule.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        start = request.form.get('start')
        destination = request.form.get('destination')
        start_lat, start_lng = get_coordinates(start)
        end_lat, end_lng = get_coordinates(destination)

        if start_lat is None or end_lat is None:
            return "Error: Could not geocode address."

        return render_template('mapApi/map.html', 
                               start=start, 
                               destination=destination, 
                               start_lat=start_lat, 
                               start_lng=start_lng, 
                               end_lat=end_lat, 
                               end_lng=end_lng, 
                               api_key=api_key)
    else:
        return render_template('search.html', api_key=api_key)

@app.route('/map')
def map():
    return render_template('mapApi/ui.html', api_key=api_key)


@app.route('/route')
def route():
    return render_template('mapApi/route.html', api_key=api_key)

@app.route('/traffic')
def traffic():
    return render_template('traffic.html')

if __name__ == '__main__':
    app.run(debug=True)