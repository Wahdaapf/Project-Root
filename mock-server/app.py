from flask import Flask, jsonify, request, abort

app = Flask(__name__)

import json
import os

# Load data from JSON file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "customers.json")

def load_customers():
    try:
        if not os.path.exists(DATA_PATH):
            return []
        with open(DATA_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading customers.json: {e}")
        return []

# =========================
# GET /api/health
# =========================
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "OK"}), 200


# =========================
# GET /api/customers (pagination)
# =========================
@app.route("/api/customers", methods=["GET"])
def get_customers():
    customers = load_customers()
    
    # Validation for pagination input
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
    except (ValueError, TypeError):
        # Fallback to defaults if input is not a valid integer
        page = 1
        limit = 10

    # Ensure values are within sensible ranges
    if page < 1: 
        page = 1
    if limit < 1: 
        limit = 10
    if limit > 100: 
        limit = 100 # Prevent massive data fetching in one go

    start = (page - 1) * limit
    end = start + limit

    data = customers[start:end]

    return jsonify({
        "page": page,
        "limit": limit,
        "total": len(customers),
        "data": data
    })


# =========================
# GET /api/customers/{id}
# =========================
@app.route("/api/customers/<id>", methods=["GET"])
def get_customer(id):
    customers = load_customers()
    customer = next((c for c in customers if c["customer_id"] == id), None)

    if not customer:
        return jsonify({"message": "Customer not found"}), 404

    return jsonify(customer), 200


# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)