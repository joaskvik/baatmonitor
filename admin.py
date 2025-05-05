from flask import Flask, render_template, send_file
import os

app = Flask(__name__)

BÅTLOGG_MAPPE = 'båtlogger'  # Her lagres alle båt-loggfilene

@app.route('/')
def index():
    båter = []
    if os.path.exists(BÅTLOGG_MAPPE):
        for filnavn in os.listdir(BÅTLOGG_MAPPE):
            if filnavn.startswith('konverteringslogg_') and filnavn.endswith('.txt'):
                båt_navn = filnavn[len('konverteringslogg_'):-len('.txt')].replace('_', ' ')
                båter.append(båt_navn)
    return render_template('admin_index.html', båter=båter)

@app.route('/logg/<båtnavn>')
def vis_båtlogg(båtnavn):
    filsti = os.path.join(BÅTLOGG_MAPPE, f'konverteringslogg_{båtnavn.replace(\" \", \"_\")}.txt')
    logglinjer = []

    if os.path.exists(filsti):
        with open(filsti, 'r', encoding='utf-8') as f:
            logglinjer = f.readlines()

    return render_template('admin_båtlogg.html', båtnavn=båtnavn, logglinjer=logglinjer)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
