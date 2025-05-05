from flask import Flask, render_template, request, redirect, url_for
import os
import json
from datetime import datetime

app = Flask(__name__)

LOGG_MAPPE = "båtlogger"
STATUS_FIL = "status.json"

# Sørg for at mappen finnes
os.makedirs(LOGG_MAPPE, exist_ok=True)

def hent_logger():
    if os.path.exists(STATUS_FIL):
        with open(STATUS_FIL, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def lagre_logger(data):
    with open(STATUS_FIL, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

@app.route('/')
def oversikt():
    data = hent_logger()
    # Sorter: Feil først, så OK
    data = sorted(data, key=lambda x: (x['status'] != 'feil', x['båt']))
    return render_template('admin_oversikt.html', båter=data)

@app.route('/registrer', methods=['POST'])
def registrer():
    data = hent_logger()

    nytt_innslag = {
        "båt": request.form.get('båt', 'Ukjent båt'),
        "status": request.form.get('status', 'ukjent'),
        "tid": request.form.get('tid', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        "posisjon": request.form.get('posisjon', 'Ukjent posisjon')
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
        return "Feil: Mangler fil eller båtnavn", 400

    fil = request.files['fil']
    båt = request.form['båt'].replace(' ', '_')

    filsti = os.path.join(LOGG_MAPPE, f"{båt}_logg.txt")
    fil.save(filsti)

    return "Opplasting fullført", 200

@app.route('/logg/<batnavn>')
def vis_logg_for_bat(batnavn):
    filsti = os.path.join(LOGG_MAPPE, f"{batnavn}_logg.txt")
    if not os.path.exists(filsti):
        return f"Ingen logg funnet for {batnavn}", 404

    with open(filsti, 'r', encoding='utf-8') as f:
        logginnhold = f.read()

    return render_template('admin_logg_bat.html', batnavn=batnavn.replace('_', ' '), logginnhold=logginnhold)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
