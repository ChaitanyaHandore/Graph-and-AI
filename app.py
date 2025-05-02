import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from neo4jdb.Dart import DartExecution
from neo4jdb.Bus import BusExecution
from neo4jdb.Luas import LuasExecution
from utils.visualization import TransportVisualization
from neo4j import GraphDatabase

# Dynamically locate the dataset paths
base_path = os.path.dirname(os.path.abspath(__file__))
bus_data_path = os.path.join(base_path, "data", "BUS_Dataset.csv")
dart_data_path = os.path.join(base_path, "data", "DART_Dataset.csv")
luas_data_path = os.path.join(base_path, "data", "LUAS_Dataset.csv")

URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "9820065151"
bus_executor = BusExecution(URI, USER, PASSWORD)
dart_executor = DartExecution(URI, USER, PASSWORD)
luas_executor = LuasExecution(URI, USER, PASSWORD)

bus_data = pd.read_csv(bus_data_path, encoding="latin1")
dart_data = pd.read_csv(dart_data_path, encoding="latin1")
luas_data = pd.read_csv(luas_data_path, encoding="latin1")

# Initialize the visualization class
visualization = TransportVisualization(bus_data, dart_data, luas_data)

# Centrality Visualization Class
class CentralityVisualizationApp:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def execute_query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record for record in result]

    def fetch_degree_centrality(self, category):
        query = f"""
        MATCH (s:Station)-[r:CONNECTED_BY_ROUTE]-(t:Station)
        WHERE EXISTS {{ MATCH (category:Category {{name: '{category}'}})-[:HAS_STATION]->(s) }}
        RETURN s.name AS station, COUNT(r) AS DegreeCentrality
        ORDER BY DegreeCentrality DESC
        """
        return self.execute_query(query)

centrality_app = CentralityVisualizationApp(URI, USER, PASSWORD)

# Streamlit App UI
st.title("Irish Transport System - Data Visualization")

# Sidebar Options
st.sidebar.header("Transport Selection")
transport_option = st.sidebar.selectbox("Select a Transport Type", ["DART", "LUAS", "BUS"])
analysis_option = st.sidebar.selectbox("Select Analysis Type", ["Degree Centrality", "Shortest Path", "PageRank"])

# Display graphs for the selected transport type
if transport_option == "BUS":
    st.subheader("BUS Dataset Visualizations")
    visualization.plot_frequency_vs_duration()
    visualization.plot_top_routes_by_landmarks()
    visualization.plot_heatmap_landmarks()

elif transport_option == "DART":
    st.subheader("DART Dataset Visualizations")
    visualization.plot_facilities_availability()
    visualization.plot_weekend_operational_stations()
    visualization.plot_routes_serviced_per_station()
    visualization.plot_treemap_facilities()

elif transport_option == "LUAS":
    st.subheader("LUAS Dataset Visualizations")
    visualization.plot_footfall_by_line()
    # visualization.plot_footfall_trends()
    visualization.plot_parking_availability()
    visualization.plot_accessibility_comparison()
    visualization.plot_nearby_landmarks()
    visualization.plot_station_zone_relationship()
    # visualization.plot_accessibility_sunburst()

results = None  # Initialize results to ensure it's always defined

# Degree Centrality Analysis
if analysis_option == "Degree Centrality":
    st.subheader(f"Degree Centrality for {transport_option}")

    # Fetch centrality data using the new class
    centrality_data = centrality_app.fetch_degree_centrality(transport_option)

    if centrality_data:
        try:
            # Convert results to DataFrame
            df = pd.DataFrame(centrality_data)
            df.columns = ["Station", "Degree Centrality"]

            # Display data and plot bar chart
            st.dataframe(df)
            fig = px.bar(df, x="Station", y="Degree Centrality", title=f"{transport_option} Station Degree Centrality", labels={"Degree Centrality": "Degree Centrality"})
            st.plotly_chart(fig)
        except Exception as e:
            st.error(f"An error occurred while processing the results: {e}")
    else:
        st.warning("No results were returned from the centrality calculation.")

# Shortest Path Analysis
elif analysis_option == "Shortest Path":
    st.subheader(f"Shortest Path for {transport_option}")

    start_station = st.text_input("Enter Start Station")
    end_station = st.text_input("Enter End Station")

    if st.button("Calculate Shortest Path"):
     try:
        if transport_option == "BUS":
            results = bus_executor.find_shortest_path(start_station, end_station)
        elif transport_option == "DART":
             results = dart_executor.calculate_shortest_path(start_station, end_station)
        elif transport_option == "LUAS":
             results = luas_executor.calculate_shortest_path(start_station, end_station)

        if results:
            for record in results:
                    st.write(f"Path: {' -> '.join(record['path'])}")
                    st.write(f"Total Distance: {record['totalDistance']} km")
            else:
                st.warning("Shortest Path Calculated")
     except Exception as e:
            st.error(f"An error occurred while calculating the shortest path: {e}")

# PageRank Analysis
elif analysis_option == "PageRank":
    st.subheader(f"PageRank for {transport_option}")

    if transport_option == "BUS":
        node_label = "Route"
        relationship_type = "CONNECTED_TO"
        bus_executor.calculate_pagerank(node_label, relationship_type)
    elif transport_option == "DART":
        node_label = "Station"
        relationship_type = "CONNECTED_BY_ROUTE"
        dart_executor.calculate_pagerank(node_label, relationship_type)
    elif transport_option == "LUAS":
        node_label = "Station"
        relationship_type = "CONNECTED_BY_LINE"
        # luas_executor.calculate_pagerank(node_label, relationship_type)

    results_query = f"""
    MATCH (n:{node_label})
    RETURN n.name AS Name, n.rank AS PageRank
    ORDER BY PageRank DESC
    """
    if transport_option == "BUS":
        results = bus_executor.execute_query(results_query)
    elif transport_option == "DART":
        results = dart_executor.execute_query(results_query)
    elif transport_option == "LUAS":
        results = luas_executor.execute_query(results_query)

    if results:
        df = pd.DataFrame(results)
        st.dataframe(df)
        st.bar_chart(df.set_index("Name")[["PageRank"]])

# Close Neo4j connections
bus_executor.close()
dart_executor.close()
luas_executor.close()
centrality_app.close()
