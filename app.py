import os
import time
import pandas as pd
from flask import Flask, render_template
import plotly.graph_objs as go

app = Flask(__name__)
app.static_folder = 'templates/static'

# Configure the server name and application root
app.config['SERVER_NAME'] = '127.0.0.1:5000'  # Replace with your server name or IP address
app.config['APPLICATION_ROOT'] = ''  # Set to the root path of your application

# Load the data from the CSV file
data_path = os.path.join(os.getcwd(), 'energy_data.csv')
full_data = pd.read_csv(data_path)

# Filter the data to start from May 20, 2015
full_data = full_data[full_data['utc_timestamp'] >= '2015-05-20']

# Helper function to generate real-time visualization
def generate_real_time_visualization(data):
    # Create a trace for each appliance
    traces = []
    for col in data.columns[1:]:
        trace = go.Scatter(x=data['utc_timestamp'], y=data[col], mode='lines', name=col)
        traces.append(trace)

    layout = go.Layout(title='Real-Time Energy Usage Visualization',
                       xaxis=dict(title='UTC Timestamp'),
                       yaxis=dict(title='Energy Usage'))

    fig = go.Figure(data=traces, layout=layout)
    return fig.to_html(full_html=False)

# Route for real-time visualization
@app.route('/')
def real_time_visualization():
    # Initialize the data with the first minute
    data = full_data[full_data['minute'] == 0]
    current_minute = 0
    current_hour = data['hour'].unique()[0]
    current_day = data['day'].unique()[0]

    # Simulate real-time data playback
    while True:
        with app.app_context():
            visualization = generate_real_time_visualization(data)
            yield render_template('real_time_visualization.html', visualization=visualization)

        # Switch to the next minute
        time.sleep(10)
        current_minute += 15
        if current_minute >= 60:
            current_minute = 0
            current_hour += 1
            if current_hour >= 24:
                current_hour = 0
                current_day += 1

        # Filter the data for the next minute
        data = full_data[(full_data['minute'] == current_minute) &
                         (full_data['hour'] == current_hour) &
                         (full_data['day'] == current_day)]

        # If the data is empty, move to the next day
        if data.empty:
            current_day += 1
            data = full_data[(full_data['minute'] == 0) &
                             (full_data['hour'] == 0) &
                             (full_data['day'] == current_day)]

if __name__ == '__main__':
    app.run(debug=True)