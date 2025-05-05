from flask import Flask, render_template, request, redirect, url_for
import os
import json
from datetime import datetime

app = Flask(__name__)

DATAFIL = 'batlogger.json'

def hent_logger():
    if not os.path.exists(DATAFIL):
        return []
    with open(DATAFIL, 'r', encoding='utf-8') as fil:
        return json.load(fil)

def lagre_logger(data):
    with open(DATAFIL, 'w', encoding='utf-8') as fil:
        json.dump(data, fil, indent=4, ensure_ascii=False)

@app.route('/')
def oversikt():
    logger = hent_logger()
    båter = set(logg['båt'] for logg in logger)
    return render_template('admin_oversikt.html', båter=båter)

@app.route('/logg/<batnavn>')
def vis_logg_for_bat(batnavn):
    logger = hent_logger()
    filtrert = [logg for logg in logger if logg['båt'].replace(' ', '_') == batnavn]
    return render_template('admin_logg_bat.html', logger=filtrert, batnavn=batnavn)

@app.route('/registrer', methods=['POST'])
def registrer():
    data = hent_logger()
    nytt_innslag = {
        "båt": request.form['båt'],
        "status": request.form['status'],
        "tid": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    data.append(nytt_innslag)
    lagre_logger(data)
    return redirect(url_for('oversikt'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
