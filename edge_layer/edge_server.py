from flask import Flask, request, jsonify
import random
import sys
import os
import time

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_router.query_router import predict_route, generate_system_metrics

app = Flask(__name__)

# Simulate load metrics for the edge server
def generate_edge_metrics():
    cpu_load = random.uniform(30, 80)  # Simulate CPU load for edge (30% to 80%)
    ram_usage = random.uniform(2, 16)   # Simulate RAM usage for edge (2GB to 16GB)
    bandwidth = random.uniform(2, 20)   # Simulate network bandwidth for edge (2 to 20 Mbps)
    
    return [cpu_load, ram_usage, bandwidth]

# Calculate load based on CPU, RAM, and Bandwidth
def get_load(metrics):
    cpu_load, ram_usage, bandwidth = metrics[0], metrics[1], metrics[2]
    # Simple load calculation: higher values mean higher load
    load = (cpu_load + ram_usage * 10 + bandwidth * 2) / 100  # Arbitrary weightage for now
    return load

# Dictionary to store device status (last heartbeat timestamp)
device_status = {}

# Heartbeat mechanism to track device status
@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    device_id = request.json.get('device_id')
    status = request.json.get('status')  # "alive" or "inactive"
    
    # Get current timestamp
    timestamp = time.time()
    
    # Update the device status with the latest timestamp
    device_status[device_id] = timestamp if status == 'alive' else None
    
    print(f"Heartbeat received from {device_id} - Status: {status}")
    return jsonify({"status": "success", "message": "Heartbeat received"})

# Endpoint to receive data from IoT devices
@app.route('/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    device_id = data.get('device_id')
    route = data.get('route')
    print(f"Received data from {device_id} - {data}")
    
    # Simulate load metrics for edge and cloud
    edge_metrics = generate_edge_metrics()
    edge_load = get_load(edge_metrics)  # Get edge load
    print(f"Edge Load: {edge_load:.4f}")
    
    cloud_metrics = [random.uniform(10, 50), random.uniform(1, 8), random.uniform(5, 20)]  # Simulate cloud
    cloud_load = get_load(cloud_metrics)  # Get cloud load
    print(f"Cloud Load: {cloud_load:.4f}")
    
    # Simulate failover logic: Check if the device is active
    device_failed = False
    if device_id not in device_status or device_status[device_id] is None:
        device_failed = True
        print(f"Device {device_id} failed, rerouting query.")
    
    # Make a failover decision
    if device_failed:
        query_route = "Edge" if edge_load <= cloud_load else "Cloud"
    else:
        # Make a load-based decision to route to the least-loaded layer
        if edge_load <= cloud_load:
            query_route = "Edge"
        else:
            query_route = "Cloud"
    
    # Log received data for evaluation
    with open('edge_data_log.txt', 'a') as log_file:
        log_file.write(f"Received data from {device_id} - {data}\n")
    
    if route == "Edge":
        # Process the query at the edge
        print(f"Processing data at Edge: {data}")
        return jsonify({"status": "success", "message": "Data processed at Edge."})
    
    elif route == "Cloud":
        # Forward to the cloud for further processing
        print(f"Forwarding data to Cloud: {data}")
        return jsonify({"status": "success", "message": "Data forwarded to Cloud."})

    else:
        # If the decision is to process on the device, handle it here
        print(f"Data should be processed at Device: {data}")
        return jsonify({"status": "error", "message": "Invalid route."})

if __name__ == '__main__':
    app.run(host='localhost', port=5000)
