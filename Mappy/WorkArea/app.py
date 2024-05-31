from flask import Flask, render_template

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

@app.route('/traffic')
def traffic():
    return render_template('traffic.html')

if __name__ == '__main__':
    app.run(debug=True)