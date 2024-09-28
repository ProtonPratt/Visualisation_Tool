from flask import Flask, render_template, redirect, url_for, request
import os

app = Flask(__name__)

# Directory where the precomputed JSONs are stored
JSON_DIR = 'data/'

# Route for listing JSON files
@app.route('/')
def home():
    # List all JSON files in the directory
    json_files = [f for f in os.listdir(JSON_DIR) if f.endswith('.json')]
    dict_thresholds = []
    
    for file in json_files:
        dict_thresholds.append([file, 0.6])
        dict_thresholds.append([file, 0.7])
    
    return render_template('homepage.html', json_files=dict_thresholds)

# Route to redirect to app.py with filename
@app.route('/open/<filename>')
def open_json(filename):
    # Redirect to app.py (assuming it's running on the same server at port 8050)
    # filename = request.args.get('filename')
    threshold = request.args.get('threshold', 0.6)
    # Pass the selected JSON file as a query parameter
    return redirect(f'http://localhost:8050/view_json?filename={filename}&threshold={threshold}')

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
