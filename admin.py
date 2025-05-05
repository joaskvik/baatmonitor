from flask import Flask, render_template, request, redirect, url_for
import os
import json
from datetime import datetime

app = Flask(__name__)

DATAFIL = 'batlogger.json'
BATLOGGER_MAPPE = 'batlogger'

# Hjelpefunksjon for å laste logger
def hent_logger():
    if not os.path.exists(DATAFIL):
        return []
    with open(DATAFIL, 'r', encoding='utf-8') as fil:
        return json.load(fil)

# Hjelpefunksjon for å lagre logger
def lagre_logger(data):
    with open(DATAFIL, 'w', encoding='utf-8') as fil:
        json.dump(data, fil, indent=4, ensure_ascii=False)

@app.route('/')
def oversikt():
    logger = hent_logger()
    status_per_bat = {}

    # Finn siste status + tidspunkt for hver båt
    for logg in logger:
        status_per_bat[logg['båt']] = {
            'status': logg['status'],
            'tid': logg['tid']
        }

    båter = set(logg['båt'] for logg in logger)

    # Hent båter fra opplastede logger også
    if os.path.exists(BATLOGGER_MAPPE):
        for batnavn in os.listdir(BATLOGGER_MAPPE):
            batnavn_clean = batnavn.replace('_', ' ')
            båter.add(batnavn_clean)
            if batnavn_clean not in status_per_bat:
                status_per_bat[batnavn_clean] = {
                    'status': 'Ukjent',
                    'tid': ''
                }

    båtliste = []
    for bat in båter:
        båtliste.append({
            'navn': bat,
            'status': status_per_bat.get(bat, {}).get('status', 'Ukjent'),
            'tid': status_per_bat.get(bat, {}).get('tid', '')
        })

    # 🚦 Sorter: FEIL først, så UKJENT, så OK
    båtliste.sort(key=lambda x: (0 if x['status'].lower() == 'feil' else (1 if x['status'].lower() == 'ukjent' else 2), x['navn']))

    return render_template('admin_oversikt.html', båter=båtliste)

@app.route('/logg/<batnavn>')
def vis_logg_for_bat(batnavn):
    logger = hent_logger()
    filtrert = [logg for logg in logger if logg['båt'].replace(' ', '_') == batnavn]

    # Legg til fil fra opplastet logg
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
        "tid": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # 🛠️ OVERSKRIV status for båten hvis den finnes
    eksisterende = next((d for d in data if d['båt'] == nytt_innslag['båt']), None)

    if eksisterende:
        eksisterende['status'] = nytt_innslag['status']
        eksisterende['tid'] = nytt_innslag['tid']
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
