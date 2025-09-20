import time
import random
import requests
import json
import csv
import sys
import os
from collections import OrderedDict

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_router.query_router import predict_route, generate_system_metrics, train_model

# Load the trained AI model
model = train_model()

# LRU Cache Implementation
class LRUCache:
    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity  # Set a larger capacity

    def get(self, key: str):
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        return None

    def put(self, key: str, value):
        if len(self.cache) >= self.capacity:
            self.cache.popitem(last=False)  # Evict the least recently used item
        self.cache[key] = value
        self.cache.move_to_end(key)  # Mark as recently used

# In-memory cache (simulating Redis for now)
cache = LRUCache(capacity=1000)  # Set a larger cache size for better hit rate

# Simulating IoT devices (e.g., temperature sensors)
def generate_data(device_id):
    temperature = random.uniform(20.0, 30.0)  # Random temperature between 20°C and 30°C
    humidity = random.uniform(40.0, 60.0)     # Random humidity between 40% and 60%
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
    
    data = {
        'device_id': device_id,
        'temperature': round(temperature, 2),
        'humidity': round(humidity, 2),
        'timestamp': timestamp
    }
    return data

# Simulate load metrics for the device
def generate_system_metrics():
    # Simulate load metrics for the device
    cpu_load = random.uniform(10, 70)  # Simulate CPU usage (10% to 70%)
    ram_usage = random.uniform(1, 8)   # Simulate RAM usage (1GB to 8GB)
    bandwidth = random.uniform(1, 10)  # Simulate network bandwidth (1 to 10 Mbps)
    query_size = random.choice([1, 2, 3])  # Simulate query size: 1 (small), 2 (medium), 3 (large)
    
    return [cpu_load, ram_usage, bandwidth, query_size]

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

# Simulate cache retrieval
def get_from_cache(query_key):
    return cache.get(query_key)

# Simulate storing data in cache
def store_in_cache(query_key, data):
    cache.put(query_key, data)
    print(f"Stored data in cache for {query_key}")

# Send heartbeat to the edge server
def send_heartbeat(device_id, status='alive', url="http://localhost:5000/heartbeat"):
    heartbeat_data = {'device_id': device_id, 'status': status}  # Ensure status is included in the payload
    
    try:
        response = requests.post(url, json=heartbeat_data)
        if response.status_code == 200:
            print(f"Heartbeat from {device_id} sent successfully.")
        else:
            print(f"Failed to send heartbeat from {device_id}.")
    except requests.exceptions.RequestException as e:
        print(f"Error sending heartbeat from {device_id}: {e}")

# Log data to CSV
def log_metrics_to_csv(device_id, metrics, query_route, round_trip_time):
    with open('metrics_log.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([device_id, *metrics, query_route, round_trip_time])

# Function to send data to the edge server (via HTTP)
def send_data_to_edge_server(device_id, url="http://localhost:5000/data"):
    data = generate_data(device_id)
    system_metrics = generate_system_metrics()  # Get system metrics for AI routing
    
    # Generate a unique query key (this is just an example, you can generate better keys based on the query data)
    query_key = f"{device_id}_{system_metrics}"
    
    # Check if data is in cache
    cached_data = get_from_cache(query_key)
    if cached_data:
        print(f"Cache hit for {query_key}. Using cached data.")
        data = cached_data  # Use cached data
    else:
        # Cache miss - route and process the query
        device_load = get_load(system_metrics)  # Get device load
        print(f"Device Load: {device_load:.4f}")

        # Simulate edge load (you could use real edge metrics)
        edge_metrics = generate_edge_metrics()
        edge_load = get_load(edge_metrics)  # Get edge load
        print(f"Edge Load: {edge_load:.4f}")

        # Simulate cloud load (you could use real cloud metrics)
        cloud_metrics = [random.uniform(10, 50), random.uniform(1, 8), random.uniform(5, 20)]  # Simulate cloud
        cloud_load = get_load(cloud_metrics)  # Get cloud load
        print(f"Cloud Load: {cloud_load:.4f}")

        # Determine where to route the query based on load
        if device_load <= edge_load and device_load <= cloud_load:
            query_route = "Device"
        elif edge_load <= cloud_load:
            query_route = "Edge"
        else:
            query_route = "Cloud"

        # Get routing decision from AI model (can be a fallback option)
        query_route = predict_route(system_metrics)  # AI-based routing

        data['route'] = query_route  # Append route prediction to data
        
        # Store data in cache for future use
        store_in_cache(query_key, data)
    
    # Measure the round-trip time
    start_time = time.time()
    
    response = requests.post(url, json=data)
    
    end_time = time.time()
    round_trip_time = end_time - start_time
    print(f"Round-trip time for {device_id}: {round_trip_time:.4f} seconds")
    
    # Log the metrics and round-trip time
    log_metrics_to_csv(device_id, system_metrics, query_route, round_trip_time)
    
    if response.status_code == 200:
        print(f"Data from {device_id} sent successfully!")
    else:
        print(f"Failed to send data from {device_id}.")

# Simulate random device failure (stop sending heartbeat)
def simulate_device_failures():
    device_ids = ['Device1', 'Device2', 'Device3', 'Device4', 'Device5']
    
    # Randomly pick a device to stop sending heartbeat
    failed_device = random.choice(device_ids)
    print(f"Simulating failure of {failed_device}...")
    
    # Send "inactive" heartbeat for the failed device
    send_heartbeat(failed_device, status="inactive")
    
    # Simulate sending data for the remaining devices
    for device_id in device_ids:
        if device_id != failed_device:
            send_data_to_edge_server(device_id)
        send_heartbeat(device_id)  # Send heartbeat signal every time

# Simulate data from multiple devices
def simulate_devices():
    device_ids = ['Device1', 'Device2', 'Device3', 'Device4', 'Device5']
    
    while True:
        simulate_device_failures()  # Simulate random device failures
        for device_id in device_ids:
            send_data_to_edge_server(device_id)
            send_heartbeat(device_id)  # Send heartbeat signal every time
        time.sleep(5)  # Simulate sending data every 5 seconds

if __name__ == "__main__":
    simulate_devices()
