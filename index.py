import requests
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Your actual API details
REAL_API_URL = "https://numinfo.eu.cc/api/check"
API_KEY = "freekeyhostmafia"

@app.route('/api/check', methods=['GET'])
def check_number():
    number = request.args.get('number')
    apikey = request.args.get('apikey')
    
    # Simple API key check (optional, for your bot)
    if apikey != API_KEY:
        return jsonify({"success": False, "error": "Invalid API key"}), 401
    
    if not number:
        return jsonify({"success": False, "error": "Missing number"}), 400
    
    # Clean the number
    number = ''.join(filter(str.isdigit, number))
    if len(number) >= 10:
        number = number[-10:]
    
    try:
        # Call the real API
        response = requests.get(
            REAL_API_URL,
            params={"apikey": API_KEY, "number": number},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract all entries (skip the 'credit' key)
            results = []
            for key, value in data.items():
                if key != "credit" and isinstance(value, dict) and value.get("name"):
                    results.append({
                        "name": value.get("name", "N/A"),
                        "father_name": value.get("father name", value.get("father_name", "N/A")),
                        "address": value.get("address", "N/A").replace("!", " ").strip(),
                        "mobile": value.get("mobile", "N/A"),
                        "alternative_mobile": value.get("alternative mobile", "N/A"),
                        "sim": value.get("circle/sim", "N/A"),
                        "email": value.get("mail", "N/A") or "N/A"
                    })
            
            if results:
                return jsonify({
                    "success": True,
                    "number": number,
                    "total": len(results),
                    "data": results
                })
            else:
                return jsonify({
                    "success": False,
                    "error": f"No data found for {number}"
                }), 404
        else:
            return jsonify({
                "success": False,
                "error": f"API returned status {response.status_code}"
            }), response.status_code
            
    except requests.exceptions.Timeout:
        return jsonify({"success": False, "error": "Request timeout"}), 504
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/tg', methods=['GET'])
def telegram_lookup():
    """Telegram username to number lookup (if your API has this endpoint)"""
    return jsonify({
        "success": False,
        "error": "Telegram lookup not configured. Use /api/check for numbers."
    }), 501

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "name": "Number Info API",
        "status": "Active",
        "endpoint": "/api/check?apikey=freekeyhostmafia&number=XXXXXXXXXX"
    })

# For Vercel serverless
def handler(request, context):
    return app(request, context)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)