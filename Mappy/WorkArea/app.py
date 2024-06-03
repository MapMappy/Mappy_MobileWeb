from flask import Flask, render_template
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

@app.route('/search')
def search():
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