import sqlite3
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# All other code is the same...

# --- 🔒 Internal Constants (Server-Side Only) ---
AUTOMATED_COST_PER_INVOICE = 0.20
ERROR_RATE_AUTO = 0.001
MIN_ROI_BOOST_FACTOR = 1.1
TIME_SAVED_PER_INVOICE_MINUTES = 8 # <-- The key to the correct calculation

# --- 🧮 Calculation Logic (Helper Function) ---
def perform_calculation(data):
    # --- ▼▼▼ THIS IS THE UPDATED SECTION ▼▼▼ ---
    monthly_invoice_volume = float(data.get('monthly_invoice_volume', 0))
    # num_ap_staff is no longer needed for this calculation method
    # avg_hours_per_invoice is no longer needed for this calculation method
    hourly_wage = float(data.get('hourly_wage', 0))
    error_rate_manual = float(data.get('error_rate_manual', 0)) / 100
    error_cost = float(data.get('error_cost', 0))
    time_horizon_months = int(data.get('time_horizon_months', 36))
    one_time_implementation_cost = float(data.get('one_time_implementation_cost', 0))

    # Corrected labor savings calculation based on time saved
    time_saved_per_month_hours = (monthly_invoice_volume * TIME_SAVED_PER_INVOICE_MINUTES) / 60
    labor_savings = time_saved_per_month_hours * hourly_wage

    # Other calculations remain the same
    auto_cost = monthly_invoice_volume * AUTOMATED_COST_PER_INVOICE
    error_savings = (error_rate_manual - ERROR_RATE_AUTO) * monthly_invoice_volume * error_cost
    
    # Use the new labor_savings instead of the flawed labor_cost_manual
    monthly_savings_unbiased = (labor_savings + error_savings) - auto_cost
    monthly_savings = monthly_savings_unbiased * MIN_ROI_BOOST_FACTOR
    
    # --- ▲▲▲ END OF UPDATED SECTION ▲▲▲ ---
    
    if monthly_savings <= 0:
        payback_months = float('inf')
    else:
        payback_months = one_time_implementation_cost / monthly_savings

    cumulative_savings = monthly_savings * time_horizon_months
    net_savings = cumulative_savings - one_time_implementation_cost
    
    if one_time_implementation_cost <= 0:
        roi_percentage = float('inf')
    else:
        roi_percentage = (net_savings / one_time_implementation_cost) * 100
        
    return {
        "monthly_savings": round(monthly_savings, 2),
        "payback_months": round(payback_months, 2),
        "cumulative_savings": round(cumulative_savings, 2),
        "net_savings": round(net_savings, 2),
        "roi_percentage": round(roi_percentage, 2)
    }

# ... (The rest of your API endpoints are unchanged) ...

def get_db_connection():
    conn = sqlite3.connect('scenarios.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS scenarios ('
                 'id INTEGER PRIMARY KEY AUTOINCREMENT,'
                 'scenario_name TEXT NOT NULL,'
                 'monthly_invoice_volume REAL,'
                 'num_ap_staff REAL,'
                 'avg_hours_per_invoice REAL,'
                 'hourly_wage REAL,'
                 'error_rate_manual REAL,'
                 'error_cost REAL,'
                 'time_horizon_months INTEGER,'
                 'one_time_implementation_cost REAL,'
                 'monthly_savings REAL,'
                 'payback_months REAL,'
                 'roi_percentage REAL'
                 ')')
    conn.commit()
    conn.close()

init_db()

@app.route('/simulate', methods=['POST'])
def run_simulation():
    return jsonify(perform_calculation(request.json))

@app.route('/scenarios', methods=['GET'])
def list_scenarios():
    conn = get_db_connection()
    scenarios_cursor = conn.execute('SELECT id, scenario_name FROM scenarios ORDER BY scenario_name').fetchall()
    conn.close()
    scenarios = [dict(row) for row in scenarios_cursor]
    return jsonify(scenarios)

@app.route('/scenarios/<int:scenario_id>', methods=['GET'])
def get_scenario(scenario_id):
    conn = get_db_connection()
    scenario_cursor = conn.execute('SELECT * FROM scenarios WHERE id = ?', (scenario_id,)).fetchone()
    conn.close()
    if scenario_cursor is None:
        return jsonify({"error": "Scenario not found"}), 404
    return jsonify(dict(scenario_cursor))

@app.route('/scenarios', methods=['POST'])
def save_scenario():
    data = request.json
    scenario_name = data.get('scenario_name')
    if not scenario_name: return jsonify({"error": "scenario_name is required"}), 400
    results = perform_calculation(data)
    conn = get_db_connection()
    conn.execute('INSERT INTO scenarios (scenario_name, monthly_invoice_volume, num_ap_staff, avg_hours_per_invoice, hourly_wage, error_rate_manual, error_cost, time_horizon_months, one_time_implementation_cost, monthly_savings, payback_months, roi_percentage) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',(scenario_name, data.get('monthly_invoice_volume'), data.get('num_ap_staff'), data.get('avg_hours_per_invoice'), data.get('hourly_wage'), data.get('error_rate_manual'), data.get('error_cost'), data.get('time_horizon_months'), data.get('one_time_implementation_cost'), results['monthly_savings'], results['payback_months'], results['roi_percentage']))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": f"Scenario '{scenario_name}' saved."}), 201

@app.route('/report/generate', methods=['POST'])
def generate_report():
    data = request.json
    email = data.get('email')
    if not email: return jsonify({"error": "Email is required"}), 400
    print(f"--- LEAD CAPTURED: {email} ---")
    results = data.get('results', {})
    report_html = """
    <html><head><title>ROI Report</title></head><body style="font-family: sans-serif;"><h1>Invoice Automation ROI Report</h1><h2>Projected Savings</h2><p><strong>Monthly Savings:</strong> ${{ results.get('monthly_savings', 0) }}</p><p><strong>Payback Period:</strong> {{ results.get('payback_months', 0) }} months</p><p><strong>Total Net Savings:</strong> ${{ results.get('net_savings', 0) }}</p><p><strong>ROI Percentage:</strong> {{ results.get('roi_percentage', 0) }}%</p><hr><p><em>Report generated for: {{ email }}</em></p></body></html>
    """
    return render_template_string(report_html, results=results, email=email)

@app.route('/scenarios/<int:scenario_id>', methods=['DELETE'])
def delete_scenario(scenario_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM scenarios WHERE id = ?', (scenario_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Scenario deleted."}), 200

if __name__ == '__main__':
    app.run(debug=True)