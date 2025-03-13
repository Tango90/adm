from flask import Flask, request, jsonify
import pandas as pd
import networkx as nx

# Load Data
item_info = pd.read_csv(r"data\item_info.csv")
orders = pd.read_csv(r"data\orders.csv")
trucks = pd.read_excel(r"data\trucks.xlsx", sheet_name="Sheet1")


# Initialize Flask App
app = Flask(__name__)

# Build Graph for Route Optimization
G = nx.Graph()

# Placeholder: Add nodes (cities) and edges (distances between them)
# In a real-world case, we'd use an API like Google Maps to get distances

# API Endpoint for Delivery Optimization
@app.route("/optimize_routes", methods=["POST"])
def optimize_routes():
    data = request.get_json()
    orders = data.get("orders", [])

    optimized_routes = []
    for order in orders:
        destination = order["Destination"]
        weight = int(order["Number of Units"]) * int(item_info[item_info["ItemId"] == order["Item"]]["weight (pounds)"].values[0])  # Convert to int
        truck = trucks.loc[trucks["Weight Capacity (kg)"] >= weight].iloc[0]
        
        optimized_routes.append({
            "Truck ID": int(truck["Truck ID"]),  # Convert int64 to int
            "Destination": destination,
            "Weight": int(weight)  # Convert int64 to int
        })
    
    return jsonify({"optimized_routes": optimized_routes})


# Run API
if __name__ == "__main__":
    app.run(debug=True)
