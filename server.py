from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import pandas as pd

app = Flask(__name__)
CORS(app)

# 1. Database Initialization
def init_db():
    conn = sqlite3.connect('bandhobast.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS duties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mobile TEXT,
            name TEXT,
            rank TEXT,
            point TEXT,
            time_slot TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Server Start થતા જ DB Table બનાવશે
init_db()

# 2. Home Route
@app.route('/')
def home():
    return "Server is running successfully!"

# 3. Admin Login Route
@app.route('/admin-login', methods=['POST'])
def admin_login():
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    password = data.get('password')
    
    if username == "admin" and password == "admin123":
        return jsonify({"success": True, "message": "Login successful!"})
    else:
        return jsonify({"success": False, "message": "અમાન્ય યુઝરનેમ અથવા પાસવર્ડ!"}), 401

# 4. Admin Excel Upload Route
@app.route('/upload-excel', methods=['POST'])
def upload_excel():
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "કોઈ ફાઈલ મળી નથી!"}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"success": False, "message": "કોઈ ફાઈલ સિલેક્ટ કરી નથી!"}), 400

    try:
        df = pd.read_excel(file)
        conn = sqlite3.connect('bandhobast.db')
        cursor = conn.cursor()
        
        # જૂનો ડેટા સાફ કરવા માટે
        cursor.execute('DELETE FROM duties')
        
        count = 0
        for _, row in df.iterrows():
            cursor.execute('''
                INSERT INTO duties (mobile, name, rank, point, time_slot)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                str(row['mobile']).split('.')[0].strip(),
                str(row['name']).strip(),
                str(row['rank']).strip(),
                str(row['point']).strip(),
                str(row['time_slot']).strip()
            ))
            count += 1
            
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": f"સફળતાપૂર્વક {count} લોકોનો ડેટા ઉમેરાઈ ગયો છે!"})
        
    except Exception as e:
        return jsonify({"success": False, "message": f"ભૂલ આવી: {str(e)}"}), 500

# 5. User Duty Search Route
@app.route('/get-duty', methods=['POST'])
def get_duty():
    data = request.get_json(silent=True) or {}
    mobile = str(data.get('mobile', '')).strip()
    
    if not mobile:
        return jsonify({"success": False, "message": "મોબાઈલ નંબર જરૂરી છે!"}), 400
        
    conn = sqlite3.connect('bandhobast.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT name, rank, point, time_slot FROM duties WHERE mobile = ?
    ''', (mobile,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return jsonify({
            "success": True,
            "data": {
                "name": result[0],
                "rank": result[1],
                "point": result[2],
                "time_slot": result[3]
            }
        })
    else:
        return jsonify({"success": False, "message": "આ નંબરનો કોઈ બંદોબસ્ત મળ્યો નથી!"}), 404

if __name__ == '__main__':
    app.run(debug=True)
