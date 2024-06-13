from flask import Flask, render_template, request, redirect, url_for, session
from flask import redirect, url_for

from dotenv import load_dotenv
import os

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

import datetime
import requests
from requests.utils import quote

import pandas as pd
import datetime



# .env 파일 로드
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")


SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
CREDENTIALS_FILE = 'credentials.json'

# Set environment variable for OAuth2
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# GOOGLE_MAPS_API_KEY 불러오기
api_key = os.getenv('GOOGLE_MAPS_API_KEY')


# Load the CSV file with proper encoding
df = pd.read_csv("Dataset\subway_dataset.csv", encoding='cp949')


## 데이터에서 혼잡도 가져오는 함수
def get_congestion_level(station_name, line_number, direction):
    now = datetime.datetime.now()
    current_time_str = now.strftime("%H시%M분")
    row = df[(df['출발역'] == station_name) & (df['호선'] == line_number) & (df['상하구분'] == direction)]
    
    if row.empty:
        return f"No data found for station: {station_name}, line: {line_number}, direction: {direction}"
    
    time_columns = df.columns[6:]
    closest_time_column = min(time_columns, key=lambda col: abs(datetime.datetime.strptime(col, "%H시%M분") - now))
    
    congestion_level = row[closest_time_column].values[0]
    return congestion_level

##Map 대중교통 정보 가져오기
def get_transit_info(origin, destination, api_key):
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&mode=transit&key={api_key}"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200 and data["status"] == "OK":
        routes = data["routes"]
        transit_info = []

        for route in routes:
            legs = route["legs"]
            for leg in legs:
                steps = leg["steps"]
                for step in steps:
                    if step["travel_mode"] == "TRANSIT":
                        transit_details = step["transit_details"]
                        transit_info.append({
                            "line": transit_details["line"]["short_name"],
                            "departure_stop": transit_details["departure_stop"]["name"],
                            "arrival_stop": transit_details["arrival_stop"]["name"],
                            "departure_time": transit_details["departure_time"]["text"],
                            "arrival_time": transit_details["arrival_time"]["text"]
                        })
        return transit_info
    else:
        return None

#위도, 경도 가져오는 함수
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

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        start = request.form.get('start')
        destination = request.form.get('destination')
        print(f"Received POST request with start: {start} and destination: {destination}")  # 디버깅 출력
        return redirect(url_for('map', start=start, destination=destination))
    return render_template('index.html')

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


@app.route('/results', methods=['POST'])
def get_congestion():
    start = request.form['start']
    end = request.form['end']

    print(start,end)
    
    # Use Google Maps Directions API to get the route
    directions_url = f"https://maps.googleapis.com/maps/api/directions/json?origin={start}&destination={end}&mode=transit&key={api_key}"
    response = requests.get(directions_url).json()
    
    # Parse the response to get station, line number, and direction
    if response['status'] == 'OK':
        steps = response['routes'][0]['legs'][0]['steps']
        for step in steps:
            if step['travel_mode'] == 'TRANSIT':
                line = step['transit_details']['line']
                station_name = step['transit_details']['departure_stop']['name']
                line_number = line['short_name']
                direction = '상선' if step['transit_details']['headsign'] == '상선' else '하선'
                break
    else:
        return f"Error: {response['status']}"

    # Get transit info
    transit_info = get_transit_info(start, end, api_key)
    
    # Get congestion level
    congestion_level = get_congestion_level(station_name, line_number, direction)
    
    # 렌더링할 때 map.html에 congestion_level을 넘겨줌
    return render_template('mapApi/map.html', 
                           start=start, 
                           destination=destination, 
                           start_lat=start_lat, 
                           start_lng=start_lng, 
                           end_lat=end_lat, 
                           end_lng=end_lng, 
                           api_key=api_key,
                           congestion_level=congestion_level, 
                           station_name=station_name, 
                           line_number=line_number, 
                           direction=direction,
                           transit_info=transit_info)

'''
@app.route('/results', methods=['POST'])
def get_congestion():
    start = request.form['start']
    end = request.form['end']
    
    # Use Google Maps Directions API to get the route
    directions_url = f"https://maps.googleapis.com/maps/api/directions/json?origin={start}&destination={end}&mode=transit&key={api_key}"
    response = requests.get(directions_url).json()
    
    # Parse the response to get station, line number, and direction
    if response['status'] == 'OK':
        steps = response['routes'][0]['legs'][0]['steps']
        for step in steps:
            if step['travel_mode'] == 'TRANSIT':
                line = step['transit_details']['line']
                station_name = step['transit_details']['departure_stop']['name']
                line_number = line['short_name']
                direction = '상선' if step['transit_details']['headsign'] == '상선' else '하선'
                break
    else:
        return f"Error: {response['status']}"

    # Get congestion level
    congestion_level = get_congestion_level(station_name, line_number, direction)
    
    # 렌더링할 때 map.html에 congestion_level을 넘겨줌
    return render_template('mapApi/map.html', 
                           start=start, 
                           destination=destination, 
                           start_lat=start_lat, 
                           start_lng=start_lng, 
                           end_lat=end_lat, 
                           end_lng=end_lng, 
                           api_key=api_key,
                           congestion_level=congestion_level, 
                           station_name=station_name, 
                           line_number=line_number, 
                           direction=direction)
'''

'''
@app.route('/map', methods=['GET', 'POST'])
def map():
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')

    if request.method == 'POST':
        start = request.form.get('start')
        destination = request.form.get('destination')
        # Assuming these parameters might also be passed in POST request, else remove them
        priorities = request.form.getlist('priorities')
        people = request.form.getlist('people')
        transports = request.form.getlist('transports')
    else:
        start = request.args.get('start')
        destination = request.args.get('destination')
        priorities = request.args.getlist('priorities')
        people = request.args.getlist('people')
        transports = request.args.getlist('transports')
    
    print(f"Mapping from start: {start} to destination: {destination}")  # 디버깅 출력
    print(f"Priorities: {priorities}, People: {people}, Transports: {transports}")

    return render_template('mapApi/ui.html', api_key=api_key, start=start, destination=destination, priorities=priorities, people=people, transports=transports)
'''
@app.route('/map', methods=['GET'])
def map():
    start = request.args.get('start')
    destination = request.args.get('destination')
    
    print(f"Mapping from start: {start} to destination: {destination}")  # 디버깅 출력

    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    return render_template('mapApi/ui.html', api_key=api_key, start=start, destination=destination)

'''
@app.route('/get_congestion', methods=['POST'])
def get_congestion():
    start = request.form['start']
    end = request.form['end']
    
    # Here you need to determine the station_name, line_number, and direction based on the start and end inputs
    # For now, let's use some placeholder values
    station_name = "서울역"  # Replace with logic to find the correct station
    line_number = 1  # Replace with logic to find the correct line number
    direction = "상선"  # Replace with logic to find the correct direction
    
    congestion_level = get_congestion_level(station_name, line_number, direction)
    
    return render_template('result.html', congestion_level=congestion_level)
'''

@app.route('/schedule')
def schedule():
    if 'credentials' not in session:
        return redirect(url_for('authorize'))

    credentials = google.oauth2.credentials.Credentials(**session['credentials'])

    service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)

    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    session['credentials'] = credentials_to_dict(credentials)

    return render_template('schedule.html', events=events)

@app.route('/authorize')
def authorize():
    print("Authorize route accessed")  # 라우트가 호출될 때 로그를 출력합니다.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CREDENTIALS_FILE,scopes=SCOPES)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )

    session['state'] = state

    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    print("OAuth2 callback route accessed")  # 라우트가 호출될 때 로그를 출력합니다.
    state = session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        state=state
    )
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)

    return redirect(url_for('schedule'))

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }


if __name__ == '__main__':
    app.run(debug=True)