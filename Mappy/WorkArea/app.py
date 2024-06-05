from flask import Flask, render_template, request
from flask import redirect, url_for
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

app = Flask(__name__)

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
    return render_template('schedule.html')

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

@app.route('/traffic')
def traffic():
    return render_template('traffic.html')

if __name__ == '__main__':
    app.run(debug=True)