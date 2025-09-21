import pickle
import random
import numpy as np
from sklearn.tree import DecisionTreeClassifier

# Simulated system metrics (features)
def generate_system_metrics():
    cpu_load = random.uniform(0, 100)  # Random CPU load (0-100%)
    ram_usage = random.uniform(0, 16)  # Random RAM usage (0-16 GB)
    bandwidth = random.uniform(1, 10)  # Random network bandwidth (1-10 Mbps)
    query_size = random.choice([1, 2, 3])  # Query size: 1 (small), 2 (medium), 3 (large)
    return [cpu_load, ram_usage, bandwidth, query_size]

# Train the decision tree model and save it to a file
def train_model():
    # Generate some training data (for the sake of this example)
    X = []  # Features (system metrics)
    y = []  # Labels (0 = device, 1 = edge, 2 = cloud)
    
    for _ in range(100):
        metrics = generate_system_metrics()
        X.append(metrics)
        if metrics[0] < 50 and metrics[1] < 8:
            y.append(0)  # Device
        elif metrics[0] < 80:
            y.append(1)  # Edge
        else:
            y.append(2)  # Cloud

    # Convert to numpy arrays
    X = np.array(X)
    y = np.array(y)

    # Train the model
    model = DecisionTreeClassifier()
    model.fit(X, y)

    # Save the model to a file using pickle
    with open("query_model.pkl", "wb") as model_file:
        pickle.dump(model, model_file)

    return model

# Load the trained model from the file
def load_model():
    try:
        with open("query_model.pkl", "rb") as model_file:
            model = pickle.load(model_file)
        return model
    except FileNotFoundError:
        return None

# Predict where to route the query (device, edge, or cloud)
def predict_route(metrics):
    model = load_model()  # Load the model once

    if model is None:
        print("Model is not available. Please train the model first.")
        return None

    # Use the model to predict the route based on system metrics
    prediction = model.predict([metrics])

    if prediction == 0:
        return "Device"
    elif prediction == 1:
        return "Edge"
    else:
        return "Cloud"
