from flask import Flask, render_template, request
from flask import redirect, url_for
from dotenv import load_dotenv
import os
from flask import redirect, url_for, session
from dotenv import load_dotenv
import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import datetime

# .env 파일 로드
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")


SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
CREDENTIALS_FILE = 'credentials.json'

# Set environment variable for OAuth2
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        start = request.form.get('start')
        destination = request.form.get('destination')
        print(f"Received POST request with start: {start} and destination: {destination}")  # 디버깅 출력
        return redirect(url_for('map', start=start, destination=destination))
    return render_template('index.html')

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


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        start = request.form.get('start')
        destination = request.form.get('destination')

        priorities = request.form.getlist('priority')
        people = request.form.getlist('people')
        transports = request.form.getlist('transport')

        result = (f"출발지: {start}, 목적지: {destination}, 우선순위: {', '.join(priorities)}, "
                  f"이동 인원: {', '.join(people)}, 이동수단: {', '.join(transports)} - 추천 경로")

        return render_template('search.html', result=result)
    return render_template('search.html')

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

@app.route('/traffic')
def traffic():
    return render_template('traffic.html')

if __name__ == '__main__':
    app.run(debug=True)