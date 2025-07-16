from flask import Flask, render_template, jsonify
import sys
import os
from collections import defaultdict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.database import get_db_connection, create_results_table

app = Flask(__name__)

@app.route('/')
def index():
    conn = get_db_connection()
    try:
        results_chronological = conn.execute('SELECT * FROM results ORDER BY timestamp ASC').fetchall()
        results_for_table = conn.execute('SELECT * FROM results ORDER BY timestamp DESC').fetchall()
    except Exception as e:
        print(f"An error occurred fetching results: {e}")
        results_chronological = []
        results_for_table = []
    finally:
        conn.close()

    chart_data = defaultdict(lambda: defaultdict(int))
    labels = []
    cumulative_counts = defaultdict(int)
    
    for result in results_chronological:
        timestamp = result['timestamp']
        status = result['status']
        
        labels.append(len(labels) + 1)
        
        cumulative_counts[status] += 1
        
        chart_data['bypassed'][len(labels) - 1] = cumulative_counts['bypassed']
        chart_data['blocked'][len(labels) - 1] = cumulative_counts['blocked']

    final_chart_data = {
        'labels': labels,
        'datasets': [
            {'label': 'Bypassed', 'data': list(chart_data['bypassed'].values()), 'borderColor': 'green', 'fill': False},
            {'label': 'Blocked', 'data': list(chart_data['blocked'].values()), 'borderColor': 'red', 'fill': False},
        ]
    }

    return render_template('index.html', results=results_for_table, chart_data=final_chart_data)

if __name__ == '__main__':
    create_results_table()
    app.run(debug=True)