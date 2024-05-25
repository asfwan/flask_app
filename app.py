from flask import Flask, jsonify, render_template
import networkx as nx
import requests
import threading
import time as time_module
from datetime import datetime, time
from typing import List, Tuple, Dict

app = Flask(__name__)

# Graph Representation
class Graph:
    def __init__(self):
        self.graph = nx.Graph()

    def add_node(self, node: str):
        self.graph.add_node(node)

    def add_edge(self, u: str, v: str, weight: float):
        self.graph.add_edge(u, v, weight=weight)

    def dijkstra(self, start: str):
        return nx.single_source_dijkstra_path_length(self.graph, start)

    def minimum_spanning_tree(self):
        return nx.minimum_spanning_tree(self.graph)

    def update_weights_with_traffic(self, traffic_data: Dict[str, float]):
        for (u, v, data) in self.graph.edges(data=True):
            if (u, v) in traffic_data:
                data['weight'] = traffic_data[(u, v)]
            else:
                # Default to some large weight if no traffic data is available
                data['weight'] = 10

# Vehicle Constraints
class Vehicle:
    def __init__(self, vehicle_id: str, capacity: float, max_distance: float):
        self.vehicle_id = vehicle_id
        self.capacity = capacity
        self.max_distance = max_distance
        self.current_location = "Presint 3"
        self.status = "available"
        self.route = []
        self.current_load = 0

class Motorcycle(Vehicle):
    def __init__(self, vehicle_id: str):
        super().__init__(vehicle_id, 20, 5000)

class Van(Vehicle):
    def __init__(self, vehicle_id: str):
        super().__init__(vehicle_id, 100, 5000)

class Lorry(Vehicle):
    def __init__(self, vehicle_id: str):
        super().__init__(vehicle_id, 300, 5000)

# Delivery Constraints
class Delivery:
    def __init__(self, delivery_id: str, location: str, time_window: Tuple[str, str], priority: int, weight: float):
        self.delivery_id = delivery_id
        self.location = location
        self.time_window = (datetime.strptime(time_window[0], "%I%p").time(), datetime.strptime(time_window[1], "%I%p").time())
        self.priority = priority
        self.weight = weight

# Fleet Management
class FleetManager:
    def __init__(self):
        self.vehicles = []
        self.deliveries = []

    def add_vehicle(self, vehicle: Vehicle):
        self.vehicles.append(vehicle)

    def add_delivery(self, delivery: Delivery):
        self.deliveries.append(delivery)

    def assign_deliveries(self):
        # Sort deliveries by priority and time window
        sorted_deliveries = sorted(self.deliveries, key=lambda d: (d.priority, d.time_window))
        for delivery in sorted_deliveries:
            for vehicle in self.vehicles:
                if vehicle.current_load + delivery.weight <= vehicle.capacity:
                    vehicle.route.append(delivery)
                    vehicle.current_load += delivery.weight
                    break

    def optimize_routes(self, graph: Graph):
        for vehicle in self.vehicles:
            if vehicle.route:
                delivery_locations = [vehicle.current_location] + [delivery.location for delivery in vehicle.route]
                # Optimize route using Dijkstra's algorithm
                optimized_route = []
                for i in range(len(delivery_locations) - 1):
                    dijkstra_path = nx.dijkstra_path(graph.graph, delivery_locations[i], delivery_locations[i+1])
                    optimized_route.extend(dijkstra_path if i == 0 else dijkstra_path[1:])
                vehicle.route = optimized_route

    def update_routes_with_traffic(self, graph: Graph):
        # Fetch real-time traffic data
        traffic_data = fetch_real_time_traffic()
        # Update graph weights with traffic data
        graph.update_weights_with_traffic(traffic_data)
        # Re-optimize routes
        self.optimize_routes(graph)

# Real-time Traffic Data
def fetch_real_time_traffic():
    # Example API call, replace with actual traffic data source
    try:
        response = requests.get("https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY")
        # Example format of traffic data {(u, v): weight, ...}
        return response.json()  # Adjust this based on actual API response
    except requests.exceptions.RequestException as e:
        print("Error fetching traffic data:", e)
        return {}

# Periodic Traffic Data Update
def periodic_traffic_update(fleet_manager: FleetManager, graph: Graph, interval: int):
    while True:
        fleet_manager.update_routes_with_traffic(graph)
        time_module.sleep(interval)

@app.route('/routes')
def get_routes():
    data = []
    for vehicle in fleet_manager.vehicles:
        data.append({
            'vehicle_id': vehicle.vehicle_id,
            'route': vehicle.route
        })
    return jsonify(data)

@app.route('/')
def index():
    return render_template('index.html')

# Example Usage
if __name__ == "__main__":
    # Create graph
    g = Graph()
    locations = ["Presint 3", "Presint 1", "Presint 2", "Presint 4", "Presint 5", "Presint 6", "Presint 7", "Presint 8",
                 "Presint 9", "Presint 10", "Presint 11", "Presint 12", "Presint 13", "Presint 14", "Presint 15",
                 "Presint 16", "Presint 17", "Presint 18"]

    for loc in locations:
        g.add_node(loc)

    # Adding some edges as an example (these should be derived from actual distances)
    edges = [
        ("Presint 3", "Presint 1", 2), ("Presint 3", "Presint 2", 4), ("Presint 3", "Presint 4", 1),
        ("Presint 1", "Presint 5", 3), ("Presint 2", "Presint 6", 2), ("Presint 4", "Presint 7", 5),
        ("Presint 5", "Presint 8", 6), ("Presint 6", "Presint 9", 4), ("Presint 7", "Presint 10", 3),
        ("Presint 8", "Presint 11", 2), ("Presint 9", "Presint 12", 7), ("Presint 10", "Presint 13", 1),
        ("Presint 11", "Presint 14", 5), ("Presint 12", "Presint 15", 3), ("Presint 13", "Presint 16", 4),
        ("Presint 14", "Presint 17", 6), ("Presint 15", "Presint 18", 2)
    ]

    for edge in edges:
        g.add_edge(*edge)

    # Create vehicles
    fleet_manager = FleetManager()
    fleet_manager.add_vehicle(Motorcycle("Motorcycle_1"))
    fleet_manager.add_vehicle(Van("Van_1"))
    fleet_manager.add_vehicle(Lorry("Lorry_1"))

    # Create deliveries
    fleet_manager.add_delivery(Delivery("Delivery_1", "Presint 1", ("9am", "12pm"), 1, 10))
    fleet_manager.add_delivery(Delivery("Delivery_2", "Presint 2", ("12pm", "3pm"), 2, 50))
    fleet_manager.add_delivery(Delivery("Delivery_3", "Presint 4", ("3pm", "5pm"), 3, 20))

    # Assign deliveries to vehicles
    print("Assigning deliveries to vehicles...")
    fleet_manager.assign_deliveries()

    # Optimize routes
    print("Optimizing routes...")
    fleet_manager.optimize_routes(g)

    # Commented out for initial testing
    # Start periodic traffic updates in a separate thread
    # traffic_update_thread = threading.Thread(target=periodic_traffic_update, args=(fleet_manager, g, 300))
    # traffic_update_thread.start()

    # Run Flask app
    app.run(debug=True, use_reloader=False)

# Templates and static files should be served correctly with this structure






