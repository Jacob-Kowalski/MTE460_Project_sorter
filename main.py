import paho.mqtt.client as mqtt
import tkinter as tk
from tkinter import ttk
import csv
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Dictionary to store CSV file writers and file objects for each topic
csv_files = {}

# Function to be called whenever a new message is received on a subscribed MQTT topic
def on_message(client, userdata, message):
    topic = message.topic
    payload = message.payload.decode()

    # Update the GUI with the most recent value for the subscribed topic
    if topic in topic_labels:
        topic_labels[topic].config(text=f"{topic}: {payload}")

    # Store the received value in the corresponding CSV file
    if topic in csv_files:
        csv_file, csv_writer = csv_files[topic]
        csv_writer.writerow([payload])

# Function to publish motor voltage to the broker
def publish_voltage():
    voltage = voltage_entry.get()
    topic = "Conveyor04/set_speed"
    client.publish(topic, voltage)

# Function to publish run status to the broker (0 or 1)
def publish_run_status():
    run_status = run_status_var.get()
    topic = "Conveyor04/set_run_status"
    client.publish(topic, str(run_status))

# Function to exit the application
def exit_application():
    # Close all open CSV files
    for csv_file, _ in csv_files.values():
        csv_file.close()
    root.destroy()

# Create an instance of the MQTT client
client = mqtt.Client()

# Set the on_message attribute of the client to the function on_message
client.on_message = on_message

# Define the MQTT broker's address and port
broker_address = "129.97.228.106"
broker_port = 1883

# Connect to the MQTT broker
client.connect(broker_address, broker_port)

# Subscribe to multiple relevant topics
topics = ["Conveyor04/get_belt_speed", "Conveyor03/box_shape", "Conveyor03/box_enc"]
for topic in topics:
    client.subscribe(topic)

# Create and configure the GUI
root = tk.Tk()
root.title("MQTT Data Monitoring")

# Maximize the main window to fit the full screen
root.attributes("-fullscreen", True)

# Create a custom style with the desired font size
custom_style = ttk.Style()
custom_style.configure('Custom.TLabel', font=("Helvetica", 18))

# Create labels to display the most recent values for subscribed topics with the custom style
topic_labels = {}
for i, topic in enumerate(topics):
    topic_label = ttk.Label(root, text=f"{topic}:", style='Custom.TLabel')
    topic_label.grid(row=i, column=0, padx=10, pady=10, sticky='w')
    topic_labels[topic] = topic_label

# Create an entry box to input motor voltage with the custom style
voltage_label = ttk.Label(root, text="Enter Motor Voltage:", style='Custom.TLabel')
voltage_label.grid(row=len(topics), column=0, padx=10, pady=10, sticky='w')
voltage_entry = ttk.Entry(root, font=("Helvetica", 18))
voltage_entry.grid(row=len(topics), column=1, padx=10, pady=10, sticky='w')
voltage_button = ttk.Button(root, text="Publish Voltage", command=publish_voltage, style='Custom.TButton')
voltage_button.grid(row=len(topics), column=2, padx=10, pady=10, sticky='w')

# Create a Checkbutton to control the conveyor's run status with the custom style
run_status_label = ttk.Label(root, text="Conveyor Run Status:", style='Custom.TLabel')
run_status_label.grid(row=len(topics) + 1, column=0, padx=10, pady=10, sticky='w')
run_status_var = tk.IntVar()
run_status_switch = ttk.Checkbutton(root, text="Run", variable=run_status_var, command=publish_run_status, style='Custom.TCheckbutton')
run_status_switch.grid(row=len(topics) + 1, column=1, padx=10, pady=10, sticky='w')

# Create a function to update the live graph
def update_graph(x_data, y_data, line, ax):
    try:
        # Get the new y-value
        new_value = float(topic_labels["Conveyor04/get_belt_speed"].cget("text").split(': ')[1])

        # Update x and y data with new values
        x_data.append(len(x_data))
        y_data.append(new_value)

        # Ensure that x_data and y_data have the same length
        if len(x_data) > len(y_data):
            x_data.pop(0)
        elif len(y_data) > len(x_data):
            y_data.pop(0)

        # Update the graph
        line.set_data(x_data, y_data)
        ax.relim()
        ax.autoscale_view()
        canvas.draw()
    except Exception as e:
        print(e)

# Create a figure for the live graph
fig = Figure(figsize=(6, 4), dpi=100)
ax = fig.add_subplot(111)
x_data = []
y_data = []
line, = ax.plot(x_data, y_data)

# Create a canvas to display the live graph in the GUI
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.grid(row=len(topics) + 3, column=0, columnspan=3, padx=10, pady=10)

# Add a label for the live graph
live_graph_label = ttk.Label(root, text="Live Belt Speed Graph:", style='Custom.TLabel')
live_graph_label.grid(row=len(topics) + 2, column=0, columnspan=3, padx=10, pady=10)

# Schedule the update_graph function to be called periodically
def update_graph_periodically():
    update_graph(x_data, y_data, line, ax)
    root.after(1000, update_graph_periodically)  # Update every 1000 milliseconds (1 second)

# Start the update_graph function to continuously update the graph
update_graph_periodically()

# Create an "Exit" button with the custom style
exit_button = ttk.Button(root, text="Exit", command=exit_application, style='Custom.TButton')
exit_button.grid(row=len(topics) + 2, column=6, padx=10, pady=20, sticky='se')

# Open CSV files for writing (assuming they exist)
for topic in topics:
    valid_topic = topic.replace('/', '_')
    csv_file = open(f"{valid_topic}_data.csv", "a", newline="")
    csv_writer = csv.writer(csv_file)
    csv_files[topic] = (csv_file, csv_writer)

# Start the MQTT client's main loop to wait for updates on the subscribed topics
client.loop_start()

# Keep the GUI running
root.mainloop()

# Close all open CSV files
for csv_file, _ in csv_files.values():
    csv_file.close()

# Stop the MQTT client's main loop and disconnect from the broker
client.loop_stop()
client.disconnect()