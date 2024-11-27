from flask import Flask, render_template, request
import matplotlib.pyplot as plt
import os
import sub as s
import sys
import threading as t
import time

app = Flask(__name__)

print(s.control_default())

# Global variables for storing the current data
data = {
    'temp': [],
    'moist': [],
    'humid': [],
    'time': []
}

# Global variables for desired values (default values are set here)
d_temp = s.get_temp()
d_moist = s.get_moist()
d_humid = s.get_humid()

h_s_old = False
v_s_old = False

# Global variable to hold the latest environmental values (from sensors)
latest_values = {'temp': 0, 'humid': 0, 'moist': 0}
latest_values_lock = t.Lock()

# Folder to store the generated plot image
GRAPH_DIR = 'static/graphs'

if not os.path.exists(GRAPH_DIR):
    os.makedirs(GRAPH_DIR)


def current_values():

    current_temp = s.get_temp()
    current_humid = s.get_humid()
    current_moist = s.get_moist()
    return current_temp, current_humid, current_moist


def update_data():

    global data, latest_values, h_s_old, v_s_old
    start_time = time.time()

    while True:
        t, h, m = current_values()

        with latest_values_lock:
            latest_values['temp'] = t
            latest_values['humid'] = h
            latest_values['moist'] = m

            data['temp'].append(t)
            data['moist'].append(m)
            data['humid'].append(h)
            data['time'].append(time.time() - start_time)

            h_status_new = s.heating_status(d_temp, latest_values['temp'])
            v_status_new = s.valve_status(d_moist, latest_values['moist'])

            if h_status_new != h_s_old:
                if h_status_new:
                    print("Heating: ON")
                else:
                    print("Heating: OFF")

            if v_status_new != v_s_old:
                if v_status_new:
                    print("Valve: ON")
                else:
                    print("Valve: OFF")

            h_s_old = h_status_new
            v_s_old = v_status_new

        if len(data['time']) % 5 == 0:
            generate_plot()

        time.sleep(1)


def console():

    while True:
        command = input(
            "Enter '/' to view extra data or 'quit' to end the program:"
        )

        if command == "/":
            s.data_stats(data)
        elif command == "quit":
            sys.exit()
        else:
            print("Invalid command, please enter '/' or 'quit'.")


def generate_plot():

    plt.figure(figsize=(8, 6))
    plt.plot(data['time'], data['temp'], label='Temperature (°C)', color='r')
    plt.plot(data['time'], data['humid'], label='Humidity (%)', color='b')
    plt.plot(data['time'], data['moist'], label='Moisture (%)', color='g')

    plt.xlabel('Time (seconds)')
    plt.ylabel('Sensor Values')
    plt.title('Environmental Sensor Data Over Time')
    plt.legend()

    graph_path = os.path.join(GRAPH_DIR, 'sensor_data_plot.png')
    plt.savefig(graph_path)
    plt.close()


@app.route('/')
def home():

    t = latest_values['temp']
    h = latest_values['humid']
    m = latest_values['moist']

    # Path to the generated plot image
    graph_url = '/static/graphs/sensor_data_plot.png'

    # Pass the current environmental values along with desired ones
    return render_template(
        'index.html',
        current_temp=t,
        current_humid=h,
        current_moist=m,
        d_temp=d_temp,
        d_moist=d_moist,
        d_humid=d_humid,
        graph_url=graph_url
    )


@app.route('/set_values', methods=['POST'])
def set_values():

    # Handle the form submission for setting desired values
    global d_temp, d_moist, d_humid
    d_temp = float(request.form['temp'])
    d_moist = float(request.form['moisture'])
    d_humid = float(request.form['humidity'])

    # After setting desired values, return to the home page with updated values
    return render_template(
        'index.html',
        current_temp=latest_values['temp'],
        current_humid=latest_values['humid'],
        current_moist=latest_values['moist'],
        d_temp=d_temp,
        d_moist=d_moist,
        d_humid=d_humid,
        graph_url='/static/graphs/sensor_data_plot.png')


if __name__ == '__main__':

    data_thread = t.Thread(target=update_data, daemon=True)
    data_thread.start()

    console_thread = t.Thread(target=console, daemon=True)
    console_thread.start()

    app.run(debug=True, use_reloader=False)

