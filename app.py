import os
from datetime import timedelta
from flask import Flask, render_template, request, session, jsonify
import urllib.request
from pusher import Pusher
from datetime import datetime
import httpagentparser
import json
import hashlib
from dbsetup import create_connection, create_session, update_or_create_page, select_all_sessions, \
    select_all_user_visits, select_all_pages, get_all_visits_count, get_home_page_visits_count, \
    get_prediction_page_visits_count, get_unique_visits_count
from inference import Inference

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)

# configure pusher object
pusher = Pusher(
    app_id='1009114',
    key='669915df0dea2e8eabd3',
    secret='c134d19d63c058c7ef9b',
    cluster='ap2',
    ssl=True
)

database = "./visitors_sqlite.db"
conn = create_connection(database)
c = conn.cursor()

userOS = None
userIP = None
userCity = None
userBrowser = None
userCountry = None
userContinent = None
sessionID = None

infer = Inference()


def main():
    global conn, c


def parseVisitor(data):
    update_or_create_page(c, data)
    pusher.trigger(u'pageview', u'new', {
        u'page': data[0],
        u'session': sessionID,
        u'ip': userIP
    })
    pusher.trigger(u'numbers', u'update', {
        u'page': data[0],
        u'session': sessionID,
        u'ip': userIP
    })


@app.before_request
def getAnalyticsData():
    global userOS, userBrowser, userIP, userContinent, userCity, userCountry, sessionID
    userInfo = httpagentparser.detect(request.headers.get('User-Agent'))
    userOS = userInfo['platform']['name']
    userBrowser = userInfo['browser']['name']
    userIP = "39.52.71.249" if request.remote_addr == '127.0.0.1' else request.remote_addr
    api = "https://www.iplocate.io/api/lookup/" + userIP
    try:
        resp = urllib.request.urlopen(api)
        result = resp.read()
        result = json.loads(result.decode("utf-8"))
        userCountry = result["country"]
        userContinent = result["continent"]
        userCity = result["city"]
    except:
        print("Could not find: ", userIP)
    getSession()


def getSession():
    global sessionID
    time = datetime.now().replace(microsecond=0)
    if 'user' not in session:
        lines = (str(time) + userIP).encode('utf-8')
        session['user'] = hashlib.md5(lines).hexdigest()
        sessionID = session['user']
        pusher.trigger(u'session', u'new', {
            u'ip': userIP,
            u'continent': userContinent,
            u'country': userCountry,
            u'city': userCity,
            u'os': userOS,
            u'browser': userBrowser,
            u'session': sessionID,
            u'time': str(time),
        })
        data = [userIP, userContinent, userCountry, userCity, userOS, userBrowser, sessionID, time]
        create_session(c, data)
    else:
        sessionID = session['user']


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def main_page():
    if request.method == 'GET':
        data = ['home', sessionID, str(datetime.now().replace(microsecond=0))]
        parseVisitor(data)
        return render_template('index.html')
    if request.method == 'POST':
        data = ['results', sessionID, str(datetime.now().replace(microsecond=0))]
        parseVisitor(data)
        print(request.files)
        if 'file' not in request.files:
            print('File not Uploaded..!')
            return
        file = request.files['file']
        img = file.read()
        pred_class, pred_cls_name, conf_scr = infer.get_prediction(image_bytes=img)
        return render_template('results.html', class_id=pred_class, category=pred_cls_name, confi=conf_scr)


@app.route('/index')
def index():
    data = ['home', sessionID, str(datetime.now().replace(microsecond=0))]
    parseVisitor(data)
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/dashboard/<session_id>', methods=['GET'])
def sessionPages(session_id):
    result = select_all_user_visits(c, session_id)
    return render_template("dashboard-single.html", data=result)


@app.route('/get-all-sessions')
def get_all_sessions():
    data = []
    dbRows = select_all_sessions(c)
    for row in dbRows:
        data.append({
            'ip': row['ip'],
            'continent': row['continent'],
            'country': row['country'],
            'city': row['city'],
            'os': row['os'],
            'browser': row['browser'],
            'session': row['session'],
            'time': row['created_at']
        })
    return jsonify(data)


@app.route('/api/v1/get-all-visits-count')
def get_all_visits_c():
    data = []
    dbRow = get_all_visits_count(c)
    data.append(
        {
            'total_sessions': dbRow[0]['visits_count']
        }
    )
    return jsonify(data)


@app.route('/api/v1/get-unique-visits-count')
def get_unique_visits_c():
    data = []
    dbRow = get_unique_visits_count(c)
    data.append(
        {
            'unique_sessions': dbRow[0]['unique_visits_count']
        }
    )
    return jsonify(data)


@app.route('/api/v1/get-home-visits-count')
def get_home_visits_c():
    data = []
    dbRow = get_home_page_visits_count(c)
    data.append(
        {
            'home_page_visits': dbRow[0]['home_visits']
        }
    )
    return jsonify(data)


@app.route('/api/v1/get-predictions-made-count')
def get_predictions_page_visits_c():
    data = []
    dbRow = get_prediction_page_visits_count(c)
    data.append(
        {
            'predictions_page_visits': dbRow[0]['predictions_made']
        }
    )
    return jsonify(data)


if __name__ == '__main__':
    main()
    # app.run(debug=True, port=os.getenv('PORT', 5000))
    app.run(threaded=True)
