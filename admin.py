from flask import Flask, render_template, request, redirect, url_for
import os
import json
from datetime import datetime
import requests

app = Flask(__name__)

DATAFIL = 'batlogger.json'
BATLOGGER_MAPPE = 'batlogger'

def hent_logger():
    if not os.path.exists(DATAFIL):
        return []
    with open(DATAFIL, 'r', encoding='utf-8') as fil:
        return json.load(fil)

def lagre_logger(data):
    with open(DATAFIL, 'w', encoding='utf-8') as fil:
        json.dump(data, fil, indent=4, ensure_ascii=False)

def hent_posisjon(ip_adresse):
    try:
        respons = requests.get(f"https://ipapi.co/{ip_adresse}/json/")
        if respons.status_code == 200:
            data = respons.json()
            return f"{data.get('city', 'Ukjent')}, {data.get('country_name', 'Ukjent')}"
        else:
            return "Ukjent posisjon"
    except Exception as e:
        print(f"[Feil] Kunne ikke hente posisjon: {e}")
        return "Ukjent posisjon"

@app.route('/')
def oversikt():
    logger = hent_logger()
    båtliste = []
    for logg in logger:
        båtliste.append({
            'navn': logg['båt'],
            'status': logg.get('status', 'Ukjent'),
            'tid': logg.get('tid', ''),
            'posisjon': logg.get('posisjon', 'Ukjent posisjon')
        })
    båtliste.sort(key=lambda x: (0 if x['status'].lower() == 'feil' else (1 if x['status'].lower() == 'ukjent' else 2), x['navn']))
    return render_template('admin_oversikt.html', båter=båtliste)

@app.route('/logg/<batnavn>')
def vis_logg_for_bat(batnavn):
    logger = hent_logger()
    filtrert = [logg for logg in logger if logg['båt'].replace(' ', '_') == batnavn]
    loggfilsti = os.path.join(BATLOGGER_MAPPE, batnavn, 'konverteringslogg.txt')
    if os.path.exists(loggfilsti):
        with open(loggfilsti, 'r', encoding='utf-8') as f:
            for linje in f:
                filtrert.append({"tid": "Filopplastet", "status": linje.strip()})
    return render_template('admin_logg_bat.html', logger=filtrert, batnavn=batnavn)

@app.route('/registrer', methods=['POST'])
def registrer():
    data = hent_logger()

    nytt_innslag = {
        "båt": request.form['båt'],
        "status": request.form['status'],
        "tid": request.form.get('tid', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        "posisjon": request.form.get('posisjon', 'Ukjent posisjon')  # 👈 her er forskjellen!
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
    if 'fil' not in request.files or 'båt' not in request.form:
        return 'Mangler fil eller båtnavn.', 400
    fil = request.files['fil']
    batnavn = request.form['båt'].replace(' ', '_')
    mappe = os.path.join(BATLOGGER_MAPPE, batnavn)
    os.makedirs(mappe, exist_ok=True)
    filsti = os.path.join(mappe, 'konverteringslogg.txt')
    fil.save(filsti)
    return 'Fil mottatt OK.', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
