from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd

app = Flask(_name_)
CORS(app)  # બ્રાઉઝર/એપમાંથી રિક્વેસ્ટ એલો કરવા માટે

# તમારી લાઈવ Google Sheet ની CSV લિંક
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRZUCXaVt5EJyWIGT4ABCsNwd_bkZfO8c5wWedJO9dV6EMdQ3xfXuMvdINP0zBx_fU5i-lkepLTzyWw/pub?output=csv"

def get_sheet_data():
    try:
        # ગૂગલ શીટમાંથી સીધો ડેટા રીડ કરશે
        df = pd.read_csv(SHEET_URL)
        df = df.fillna('')  # ખાલી ખાનાઓને ખાલી સ્ટ્રિંગમાં બદલશે
        
        # કોલમના નામમાં આજુબાજુની સ્પેસ દૂર કરશે
        df.columns = df.columns.str.strip()
        
        # ડેટામાં દરેક વેલ્યુને ટેક્સ્ટ (String) ફોર્મેટમાં કન્વર્ટ કરશે જેથી સર્ચ સરળ બને
        return df.astype(str).to_dict(orient='records')
    except Exception as e:
        print("Error fetching Google Sheet data:", e)
        return []

@app.route('/')
def home():
    return "Bandhobast API is Running!"

@app.route('/get_data', methods=['GET'])
def get_all_data():
    # આખો ડેટા આપશે
    data = get_sheet_data()
    return jsonify(data)

@app.route('/search', methods=['GET'])
def search_data():
    query = request.args.get('q', '').strip().lower()
    data = get_sheet_data()
    
    if not query:
        return jsonify(data)
    
    # કોઈપણ કોલમમાં (મોબાઈલ નંબર, નામ, હોદ્દો વગેરે) સર્ચ શબ્દ આવે તો રિઝલ્ટ આપશે
    filtered = []
    for row in data:
        for val in row.values():
            if query in str(val).lower():
                filtered.append(row)
                break
                
    return jsonify(filtered)

if _name_ == '_main_':
    app.run(host='0.0.0.0', port=5000, debug=True)
