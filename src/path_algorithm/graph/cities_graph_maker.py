import networkx as nx
import pandas as pd
from geopy.distance import geodesic
import matplotlib.pyplot as plt

class FranceCityGraph:
    def __init__(self, city_data_file='../dataset/cities.csv', max_distance_km=20, num_rows=20):
        self.city_data_file = city_data_file
        self.max_distance_km = max_distance_km
        self.num_rows = num_rows  # Limit on the number of rows to read
        self.graph = nx.Graph()  # Initialize the graph here

    def create_graph(self) -> nx.Graph:
        """Creates a graph of cities in France based on geographical proximity."""
        # Read only the specified number of rows
        df = pd.read_csv(self.city_data_file, nrows=self.num_rows)

        # Check for missing values and ignore incomplete rows
        df = df.dropna(subset=['latitude', 'longitude', 'label'])
        print("Cleaned Data:")
        print(df[['label', 'latitude', 'longitude']].head())  # Display the first 5 rows for verification

        # Add cities as nodes with their positions
        for _, row in df.iterrows():
            self.graph.add_node(row['label'], pos=(row['latitude'], row['longitude']))  # (latitude, longitude)

        # Add connections based on geographical distance
        cities = list(df.itertuples())
        for i, city1 in enumerate(cities):
            for j in range(i + 1, len(cities)):
                city2 = cities[j]
                pos1 = (city1.latitude, city1.longitude)  # (latitude, longitude)
                pos2 = (city2.latitude, city2.longitude)  # (latitude, longitude)

                # Check that positions are valid before calculating the distance
                if pd.notna(pos1[0]) and pd.notna(pos1[1]) and pd.notna(pos2[0]) and pd.notna(pos2[1]):
                    distance = geodesic(pos1, pos2).km
                    if distance <= self.max_distance_km:
                        self.graph.add_edge(city1.label, city2.label, weight=distance)
        
        # Remove nodes without connections
        self.graph.remove_nodes_from(list(nx.isolates(self.graph)))
        print("Edges in the graph:", self.graph.edges(data=True))  # Display the edges created
        return self.graph

    def draw_graph(self):
        """Visualizes the graph using matplotlib."""
        pos = nx.get_node_attributes(self.graph, 'pos')
        nx.draw(self.graph, pos, with_labels=True, node_size=700, node_color='lightblue', font_size=10, font_weight='bold', edge_color='gray')
        
        edge_labels = nx.get_edge_attributes(self.graph, 'weight')
        # Corrected edge label assignment
        edge_labels_formatted = {k: f"{v:.2f} km" for k, v in edge_labels.items()}
        
        # Display distances on the edges
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels_formatted, font_color='red')
        
        plt.title("Graphe des villes en France")
        plt.show()

# Instantiate the class with the path to your CSV file
graph_builder = FranceCityGraph(city_data_file='../dataset/cities.csv', max_distance_km=20, num_rows=20)

# Create the graph
graph = graph_builder.create_graph()

# Display the number of cities and connections in the graph
print(f"Number of cities (nodes): {graph.number_of_nodes()}")
print(f"Number of connections (edges): {graph.number_of_edges()}")

# Visualize the graph
graph_builder.draw_graph()
