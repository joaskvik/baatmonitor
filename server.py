
from flask import Flask, request, jsonify, render_template_string
import json
import os
from datetime import datetime

app = Flask(__name__)

DATAFIL = 'bater.json'

def last_data():
    if os.path.exists(DATAFIL):
        with open(DATAFIL, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def lagre_data(data):
    with open(DATAFIL, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

@app.route('/ping', methods=['POST'])
def ping():
    data = request.json
    if not data or 'båtnavn' not in data:
        return jsonify({'status': 'error', 'message': 'Båtnavn mangler'}), 400

    båtdata = last_data()
    båtnavn = data['båtnavn']
    tidspunkt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    båtdata[båtnavn] = tidspunkt
    lagre_data(båtdata)

    return jsonify({'status': 'ok', 'båt': båtnavn, 'tid': tidspunkt})

@app.route('/admin')
def admin():
    båtdata = last_data()
    html = '''
    <!DOCTYPE html>
    <html lang="no">
    <head>
        <meta charset="UTF-8">
        <title>Admin - Båtstatus</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            table { width: 100%; border-collapse: collapse; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #007bff; color: white; }
        </style>
    </head>
    <body>
        <h1>Aktive båter</h1>
        <table>
            <thead>
                <tr><th>Båtnavn</th><th>Sist sett</th></tr>
            </thead>
            <tbody>
                {% for båt, tid in båtdata.items() %}
                    <tr><td>{{ båt }}</td><td>{{ tid }}</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </body>
    </html>
    '''
    return render_template_string(html, båtdata=båtdata)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
