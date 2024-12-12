import heapq
import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from typing import Union


class TravelPathFinder:
    TIMETABLE_PATH = r"C:\Users\vikne\Documents\Master 2\Semestre 9\Intelligence artificielle\Travel-Order-Resolver\ai\path_algorithm\dataset\timetables_with_cities.csv"
    GRAPH_PATH = r"C:\Users\vikne\Documents\Master 2\Semestre 9\Intelligence artificielle\Travel-Order-Resolver\ai\path_algorithm\dataset\graph.parquet"
    STATIONS_CITIES_PATH = r"C:\Users\vikne\Documents\Master 2\Semestre 9\Intelligence artificielle\Travel-Order-Resolver\ai\path_algorithm\dataset\stations_villes.csv"

    @staticmethod
    def verify_data_exists() -> None:
        """Verify if required data files exist."""
        if not os.path.exists(TravelPathFinder.TIMETABLE_PATH):
            raise FileNotFoundError("Timetable file is missing.")

        if not os.path.exists(TravelPathFinder.GRAPH_PATH):
            TravelPathFinder.create_graph()

    @staticmethod
    def create_graph() -> None:
        """Create and save the graph (connections between stations) from the timetable data."""
        timetable_df = pd.read_csv(TravelPathFinder.TIMETABLE_PATH, sep=";", encoding="utf-8")
        graph = TravelPathFinder.build_graph_from_timetable(timetable_df)

        try:
            graph_df = TravelPathFinder.convert_graph_to_dataframe(graph)
            TravelPathFinder.save_graph_to_parquet(graph_df)
        except IOError:
            raise IOError("Unable to save the graph to a Parquet file.")

    @staticmethod
    def build_graph_from_timetable(timetable_df: pd.DataFrame) -> dict:
        """Build the graph dictionary from the timetable data."""
        graph = {}

        for _, row in timetable_df.iterrows():
            # Default to 0 if duration is missing or NaN
            duration = row["duree"] if pd.notna(row["duree"]) else 0

            # Add connections in both directions
            TravelPathFinder.add_connection_to_graph(graph, row["gare_a_city"], row["gare_b_city"], duration)
            TravelPathFinder.add_connection_to_graph(graph, row["gare_b_city"], row["gare_a_city"], duration)

        return graph

    @staticmethod
    def add_connection_to_graph(graph: dict, station_a: str, station_b: str, duration: int) -> None:
        """Add a connection between two stations in the graph."""
        if station_a not in graph:
            graph[station_a] = {}
        graph[station_a][station_b] = duration

    @staticmethod
    def convert_graph_to_dataframe(graph: dict) -> pd.DataFrame:
        """Convert the graph dictionary to a pandas DataFrame."""
        graph_data = []

        for station, connections in graph.items():
            for connected_station, duration in connections.items():
                graph_data.append({
                    'station': station,
                    'connected_station': connected_station,
                    'duration': duration
                })

        return pd.DataFrame(graph_data)

    @staticmethod
    def save_graph_to_parquet(graph_df: pd.DataFrame) -> None:
        """Save the graph DataFrame as a Parquet file."""
        table = pa.Table.from_pandas(graph_df)
        pq.write_table(table, TravelPathFinder.GRAPH_PATH)

    @staticmethod
    def create_station_city_csv() -> None:
        """Create and save the stations and cities CSV."""
        timetable_df = pd.read_csv(TravelPathFinder.TIMETABLE_PATH, sep=";", encoding="utf-8")
        station_city_df = TravelPathFinder.extract_station_city_data(timetable_df)
        TravelPathFinder.save_station_city_csv(station_city_df)

    @staticmethod
    def extract_station_city_data(timetable_df: pd.DataFrame) -> pd.DataFrame:
        """Extract the unique stations and their associated cities."""
        df_a = timetable_df[["gare_a", "gare_a_city"]]
        df_b = timetable_df[["gare_b", "gare_b_city"]]

        df_a["gare_a"] = df_a["gare_a"].str.upper()
        df_b["gare_b"] = df_b["gare_b"].str.upper()

        df_a.columns = ["station", "city"]
        df_b.columns = ["station", "city"]

        station_city_df = pd.concat([df_a, df_b]).drop_duplicates()
        return station_city_df

    @staticmethod
    def save_station_city_csv(station_city_df: pd.DataFrame) -> None:
        """Save the station-city DataFrame to a CSV file."""
        station_city_df.to_csv(TravelPathFinder.STATIONS_CITIES_PATH, sep=";", index=False)

    @staticmethod
    def load_graph() -> dict:
        """Load the graph from the Parquet file."""
        graph_df = pd.read_parquet(TravelPathFinder.GRAPH_PATH)
        return TravelPathFinder.convert_dataframe_to_graph(graph_df)

    @staticmethod
    def convert_dataframe_to_graph(graph_df: pd.DataFrame) -> dict:
        """Convert the graph DataFrame to a dictionary."""
        graph = {}
        for _, row in graph_df.iterrows():
            if row['station'] not in graph:
                graph[row['station']] = {}
            graph[row['station']][row['connected_station']] = row['duration']
        return graph

    @staticmethod
    def generate_response(path: list = None, durations: list = None, total_duration: int = 0) -> dict:
        """Generate the response dictionary for the trip."""
        return {
            "path": path or [],
            "departure": path[0] if path else None,
            "arrival": path[-1] if path else None,
            "duration_between_stations": durations or [],
            "total_duration": total_duration
        }

    @staticmethod
    def calculate_shortest_path(graph: dict, start: str, end: str) -> dict:
        """Calculate the shortest path from start to end using Dijkstra's algorithm."""
        distances = {station: float('inf') for station in graph}
        distances[start] = 0

        priority_queue = [(0, start)]
        previous_station = {station: None for station in graph}

        while priority_queue:
            current_distance, current_station = heapq.heappop(priority_queue)

            if current_station == end:
                return TravelPathFinder.reconstruct_path(previous_station, graph, start, end, distances[end])

            if current_distance > distances[current_station]:
                continue

            for neighbor, weight in graph[current_station].items():
                new_distance = current_distance + weight
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous_station[neighbor] = current_station
                    heapq.heappush(priority_queue, (new_distance, neighbor))

        return TravelPathFinder.generate_response(["UNKNOWN"])

    @staticmethod
    def reconstruct_path(previous_station: dict, graph: dict, start: str, end: str, total_duration: int) -> dict:
        """Reconstruct the path from the start to end and return the response dictionary."""
        path = []
        durations = [None]
        current_station = end

        while current_station is not None:
            path.append(current_station)
            prev_station = previous_station[current_station]
            if prev_station:
                durations.append(graph[current_station][prev_station])
            current_station = prev_station

        path.reverse()
        durations.reverse()

        return TravelPathFinder.generate_response(path, durations, total_duration)

    @staticmethod
    def convert_minutes_to_hours(minutes: int) -> str:
        """Convert minutes to hours and minutes in a formatted string."""
        hours = str(minutes // 60).zfill(2)
        mins = str(minutes % 60).zfill(2)
        return f"{hours}h{mins}"

    @staticmethod
    def find_alternative_city(city: str) -> str:
        """Find an alternative city name based on the station name."""
        station_city_df = pd.read_csv(TravelPathFinder.STATIONS_CITIES_PATH, sep=";", encoding="utf-8")
        city_match = station_city_df[station_city_df["station"] == city]

        return city if city_match.empty else city_match["city"].iloc[0]

    @staticmethod
    def get_shortest_route(trip: list, handle_error: bool = True) -> Union[list, None]:
        """Find the shortest route for the given trip by calculating paths between each consecutive station pair."""
        results = []

        try:
            TravelPathFinder.verify_data_exists()

            trip = [station.upper() for station in trip]
            trip_pairs = [trip[i:i + 2] for i in range(len(trip) - 1)]

            if not trip_pairs:
                return [TravelPathFinder.generate_response(["UNKNOWN"])] if handle_error else None

            for pair in trip_pairs:
                pair = [TravelPathFinder.find_alternative_city(station) for station in pair]

                for city in pair:
                    if city not in TravelPathFinder.load_graph():
                        if handle_error:
                            return [TravelPathFinder.generate_response(["UNKNOWN"])]
                        break
                results.append(TravelPathFinder.calculate_shortest_path(TravelPathFinder.load_graph(), pair[0], pair[1]))

            return results

        except FileNotFoundError:
            return [TravelPathFinder.generate_response(["UNKNOWN"])] if handle_error else None

        except Exception:
            return [TravelPathFinder.generate_response(["UNKNOWN"])] if handle_error else None


if __name__ == "__main__":
    TravelPathFinder.create_graph()
    TravelPathFinder.create_station_city_csv()