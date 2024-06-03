from flask import Flask, render_template, request
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

app = Flask(__name__)

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

        priorities = request.form.getlist('priority')
        people = request.form.getlist('people')
        transports = request.form.getlist('transport')

        result = (f"출발지: {start}, 목적지: {destination}, 우선순위: {', '.join(priorities)}, "
                  f"이동 인원: {', '.join(people)}, 이동수단: {', '.join(transports)} - 추천 경로")

        return render_template('search.html', result=result)
    return render_template('search.html')

@app.route('/map')
def map():
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    return render_template('mapApi/ui.html', api_key=api_key)

@app.route('/traffic')
def traffic():
    return render_template('traffic.html')

if __name__ == '__main__':
    app.run(debug=True)