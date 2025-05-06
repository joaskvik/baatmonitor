from flask import Flask, request, render_template, redirect, url_for
import os
import json
from datetime import datetime

app = Flask(__name__)

STATUSFIL = "status.json"
LOGG_MAPPE = "logger"
os.makedirs(LOGG_MAPPE, exist_ok=True)

def hent_logger():
    if not os.path.exists(STATUSFIL):
        return []
    with open(STATUSFIL, 'r', encoding='utf-8') as f:
        return json.load(f)

def lagre_logger(data):
    with open(STATUSFIL, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

@app.route('/')
def oversikt():
    data = hent_logger()
    data.sort(key=lambda x: (x['status'] != 'feil', x['båt']))
    return render_template('admin_oversikt.html', data=data)

@app.route('/registrer', methods=['POST'])
def registrer():
    data = hent_logger()

    nytt_innslag = {
        "båt": request.form.get('båt', 'Ukjent båt'),
        "status": request.form.get('status', 'ukjent'),
        "tid": request.form.get('tid', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        "posisjon": request.form.get('posisjon', 'Ukjent posisjon'),
        "latitude": request.form.get('latitude', None),
        "longitude": request.form.get('longitude', None)
    }

    eksisterende = next((d for d in data if d['båt'] == nytt_innslag['båt']), None)
    if eksisterende:
        eksisterende.update(nytt_innslag)
    else:
        data.append(nytt_innslag)

    lagre_logger(data)
    return redirect(url_for('oversikt'))

@app.route('/opplasting', methods=['POST'])
def opplasting():
    if 'fil' not in request.files:
        return 'Ingen fil', 400

    fil = request.files['fil']
    båtnavn = request.form.get('båt', 'ukjent_båt').replace(' ', '_')

    if fil:
        fil.save(os.path.join(LOGG_MAPPE, f"{båtnavn}_logg.txt"))
        return 'OK', 200
    return 'Feil', 400

@app.route('/logg/<batnavn>')
def vis_logg_for_bat(batnavn):
    filsti = os.path.join(LOGG_MAPPE, f"{batnavn}_logg.txt")
    data = hent_logger()

    batinfo = next((d for d in data if d['båt'].replace(' ', '_') == batnavn), None)

    if not batinfo:
        batinfo = {
            'status': 'ukjent',
            'tid': 'ukjent',
            'posisjon': 'ukjent',
            'latitude': None,
            'longitude': None
        }

    if not os.path.exists(filsti):
        logginnhold = "Ingen logg funnet."
    else:
        with open(filsti, 'r', encoding='utf-8') as f:
            logginnhold = f.read()

    return render_template(
        'admin_logg_bat.html',
        batnavn=batnavn.replace('_', ' '),
        logginnhold=logginnhold,
        status=batinfo['status'],
        tid=batinfo['tid'],
        posisjon=batinfo['posisjon'],
        latitude=batinfo['latitude'],
        longitude=batinfo['longitude']
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
