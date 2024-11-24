import time
from flask import Flask, render_template, request, send_from_directory
import threading
from threading import Lock
import matplotlib.pyplot as plt
import os
from engi1020.arduino.api import *

app = Flask(__name__)

digital_write(2, False)
servo_set_angle(6, 0)

# Global variables for storing the current data
data = {
    'temp': [],
    'mosit': [],
    'humid': [],
    'time': []
}

# Global variables for desired values (default values are set here)
d_temp = 20
d_moist = 20
d_humid = 20

# Global variable to hold the latest environmental values (from sensors)
latest_values = {'temp': 0, 'humid': 0, 'mosit': 0}
latest_values_lock = Lock()

# Folder to store the generated plot image
GRAPH_DIR = 'static/graphs'

if not os.path.exists(GRAPH_DIR):
    os.makedirs(GRAPH_DIR)

def current_values():
    # Fetch the current environmental values from the sensor
    current_temp = temp_humid_get_temp(3)
    current_humid = temp_humid_get_humidity(3)
    current_moist = round(analog_read(0)/950*100, 1)
    return current_temp, current_humid, current_moist

def update_data():    # Function to continuously update environmental data
    global data, latest_values
    start_time = time.time()

    while True:
        # Fetch the latest values once per loop iteration
        T, H, M = current_values()

        # Store the values globally for reuse in the Flask app
        with latest_values_lock:
            latest_values['temp'] = T
            latest_values['humid'] = H
            latest_values['mosit'] = M

        # Update the data lists (for plotting or storing historical data)
            data['temp'].append(T)
            data['mosit'].append(M)
            data['humid'].append(H)
            data['time'].append(time.time() - start_time)

            if d_temp > latest_values['temp']:
                if digital_read(2) == False:
                    digital_write(2, True)
            else:
                if digital_read(2) == True:
                    digital_write(2, False)
            if d_moist > latest_values['mosit']:
                if servo_get_angle(6) == 0:
                    servo_set_angle(6, 90)
            else:
                if servo_get_angle(6) == 90:
                    servo_set_angle(6, 0)

        # Update graph every 5 seconds (or based on your needs)
        if len(data['time']) % 5 == 0:
            generate_plot()

        time.sleep(1)  # Update every second

def generate_plot():
    # Generate the graph using matplotlib
    plt.figure(figsize=(8, 6))
    plt.plot(data['time'], data['temp'], label='Temperature (°C)', color='r')
    plt.plot(data['time'], data['humid'], label='Humidity (%)', color='b')
    plt.plot(data['time'], data['mosit'], label='Moisture (%)', color='g')

    plt.xlabel('Time (seconds)')
    plt.ylabel('Sensor Values')
    plt.title('Environmental Sensor Data Over Time')
    plt.legend()

    # Save the plot as a PNG image
    graph_path = os.path.join(GRAPH_DIR, 'sensor_data_plot.png')
    plt.savefig(graph_path)
    plt.close()

@app.route('/')
def home():
    # Use the latest environmental values to render the webpage
    T = latest_values['temp']
    H = latest_values['humid']
    M = latest_values['mosit']

    # Path to the generated plot image
    graph_url = '/static/graphs/sensor_data_plot.png'

    # Pass the current environmental values along with desired ones
    return render_template('index.html', current_temp=T, current_humid=H, current_moist=M,
                           d_temp=d_temp, d_moist=d_moist, d_humid=d_humid, graph_url=graph_url)

@app.route('/set_values', methods=['POST'])
def set_values():
    # Handle the form submission for setting desired values
    global d_temp, d_moist, d_humid
    d_temp = float(request.form['temp'])
    d_moist = float(request.form['moisture'])
    d_humid = float(request.form['humidity'])

    # After setting desired values, return to the home page with updated values
    return render_template('index.html', current_temp=latest_values['temp'], 
                           current_humid=latest_values['humid'], current_moist=latest_values['mosit'],
                           d_temp=d_temp, d_moist=d_moist, d_humid=d_humid, graph_url='/static/graphs/sensor_data_plot.png')

if __name__ == '__main__':
    # Start the data update thread
    data_thread = threading.Thread(target=update_data, daemon=True)
    data_thread.start()

    # Run the Flask app
    app.run(debug=True, use_reloader=False)  # `use_reloader=False` to prevent restarting in Thonny
