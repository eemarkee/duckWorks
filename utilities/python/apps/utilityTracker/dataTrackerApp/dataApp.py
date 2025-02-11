from flask import Flask, render_template, request, redirect, url_for, flash, make_response
import pandas as pd
import os
from processFiles import process_xml, process_csv
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
import json


app = Flask(__name__)
app.secret_key = "some_secret"  # Required for flash messages

# Temporary directory for uploaded files
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'xml', 'csv'}

# In-memory storage for the dataframe
DATAFRAME = pd.DataFrame(columns=['start_datetime', 'end_datetime', 'utility', 'correctedValue', 'unit', 'meter','AmountBilled', 'Days', 'Rate', 'AverageTemperature', 'startEpoch', 'endEpoch', 'duration', 'power', 'rawValue'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    global DATAFRAME
    if DATAFRAME is not None and not DATAFRAME.empty:
        fig = px.line(DATAFRAME, x='start_datetime', y='correctedValue', title='Corrected Value Over Time')
        graphJSON = json.dumps(fig, cls=PlotlyJSONEncoder)
        return render_template('index.html', plot=graphJSON, dataframe=DATAFRAME.to_html())
    return render_template('index.html', dataframe=None)

@app.route('/load_data', methods=['POST'])
def load_data():
    global DATAFRAME
    if 'files[]' not in request.files:
        flash('No file part')
        return redirect(request.url)

    uploaded_files = request.files.getlist('files[]')
    filtered_files = [file for file in uploaded_files if file.filename and allowed_file(file.filename)]

    if not filtered_files:
        flash('No valid files uploaded')
        return redirect(request.url)
    for file in uploaded_files:
        if file.filename.endswith('xml'):
            DATAFRAME = process_xml(file, DATAFRAME)
        elif file.filename.endswith('csv'):
            DATAFRAME = process_csv(file, DATAFRAME)
        else:
            # Other file types or error handling here
            pass

    return redirect(url_for('index'))

@app.route('/download_csv', methods=['GET'])
def download_csv():
    global DATAFRAME
    if DATAFRAME is not None:
        csv_data = DATAFRAME.to_csv(index=False)
        response = make_response(csv_data)
        cd = 'attachment; filename=data.csv'
        response.headers['Content-Disposition'] = cd 
        response.mimetype='text/csv'
        return response
    return "No data available"


if __name__ == '__main__':
    app.run(debug=True)
