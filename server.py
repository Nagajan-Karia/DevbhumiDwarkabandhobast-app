import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import pandas as pd


app = Flask(__name__)
CORS(app)

def init_db():
    conn = sqlite3.connect('bandhobast.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS duties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mobile TEXT, name TEXT, rank TEXT, point TEXT, time_slot TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/add-duty', methods=['POST'])
def add_duty():
    data = request.json
    conn = sqlite3.connect('bandhobast.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO duties (mobile, name, rank, point, time_slot)
        VALUES (?, ?, ?, ?, ?)
    ''', (str(data['mobile']), data['name'], data['rank'], data['point'], data['time_slot']))
    conn.commit()
    conn.close()
    return jsonify({"message": "બંદોબસ્ત ડ્યુટી સેવ થઈ ગઈ છે!"})

# Excel Upload API
@app.route('/upload-excel', methods=['POST'])
def upload_excel():
    if 'file' not in request.files:
        return jsonify({"message": "કોઈ ફાઈલ મળી નથી!"}), 400
    
    file = request.files['file']
    try:
        df = pd.read_excel(file)
        conn = sqlite3.connect('bandhobast.db')
        cursor = conn.cursor()
        
        count = 0
        for _, row in df.iterrows():
            cursor.execute('''
                INSERT INTO duties (mobile, name, rank, point, time_slot)
                VALUES (?, ?, ?, ?, ?)
            ''', (str(row['mobile']), str(row['name']), str(row['rank']), str(row['point']), str(row['time_slot'])))
            count += 1
            
        conn.commit()
        conn.close()
        return jsonify({"message": f"સફળતાપૂર્વક {count} લોકોનો ડેટા ઉમેરાઈ ગયો!"})
    except Exception as e:
        return jsonify({"message": "Excel ફાઈલ અપલોડ કરવામાં ભૂલ આવી. કોલમના નામ યોગ્ય છે કે નહીં તે ચેક કરો."}), 500

@app.route('/get-duty/<mobile_no>', methods=['GET'])
def get_duty(mobile_no):
    conn = sqlite3.connect('bandhobast.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name, rank, point, time_slot FROM duties WHERE mobile = ?', (str(mobile_no),))
    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify({"found": True, "name": row[0], "rank": row[1], "point": row[2], "time_slot": row[3]})
    return jsonify({"found": False, "message": "આ નંબર પર કોઈ બંદોબસ્ત પોઈન્ટ મળ્યો નથી."})

app.run(debug=True, port=5000)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
