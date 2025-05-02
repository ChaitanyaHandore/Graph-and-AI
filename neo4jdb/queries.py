#*******************************************************************************************************************************************************************
# Unit Title: Data Mining
# Unit Code: B9AI101
# Unit Leader: Terri Hoare
# Assessment Title: Graph Algorithm Application
# Category: Exercise 2 (Group)
# Expectation:
#    - CRISP-DM data mining methodology to analyse the data.
#    - Business Understanding
#    - Data Understanding
#    - Data Preparation
#    - Modelling
#    - Evaluation
#    - Deployments
# Authors: @Aniket Pathare (20050492) ,Chaitanya handore(20040465),Shubham Solse(20042764)
#*********************************************************************************************************************************************************************

# Import the essential Classes and Libraries
from neo4j import GraphDatabase
import os
import streamlit as st

from neo4jdb.Bus import BusExecution
from neo4jdb.Dart import DartExecution
from neo4jdb.Luas import LuasExecution
from neo4jdb.Master_Node import MasterNode
from utils.data_processing import IrishTransportData
import subprocess
import logging

class Neo4jExecution:
    def __init__(self, uri, user, password):
        """Initialize the Neo4j connection."""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """Close the Neo4j connection."""
        if self.driver:
            self.driver.close()

    def iconnect(self):
        """Test if the connection to the Neo4j server is established."""
        try:
            with self.driver.session() as session:
                session.run("RETURN 1")
            print("Connection to Neo4j established successfully!")
        except Exception as e:
            print(f"Failed to connect to Neo4j: {e}")

    def execute_query(self, query, parameters=None):
        """Execute a given Cypher query."""
        with self.driver.session() as session:
            try:
                result = session.run(query, parameters)
                return [record for record in result]
            except Exception as e:
                print(f"Query execution failed: {e}")
                return None

    def run_streamlit_app(self):
        """Execute the Streamlit app."""
        try:
            # Command to run Streamlit app
            app_path = r"C:\Users\Autom\PycharmProjects\B9AI101\app.py"
            if not os.path.exists(app_path):
                print(f"Error: The file '{app_path}' does not exist.")
                return

            # Run the Streamlit app
            result = subprocess.run(
                ["streamlit", "run", app_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode != 0:
                print(f"Error occurred while running the Streamlit app: {result.stderr}")
            else:
                print("Streamlit app is running successfully.")
        except FileNotFoundError:
            print("Streamlit executable not found. Please ensure Streamlit is installed.")
        except Exception as e:
            print(f"Unexpected error occurred: {e}")


# Main Execution
if __name__ == "__main__":
    # Define Neo4j connection details
    URI = "bolt://localhost:7687"
    USER = "neo4j"
    PASSWORD = "9820065151"

    # Initialize Neo4j Execution
    neo4j_exec = Neo4jExecution(URI, USER, PASSWORD)

     # Path to the CSV file
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DART_CSV_FILE_PATH = os.path.join(PROJECT_ROOT, "data","DART_Dataset.csv")
    LUAS_CSV_FILE_PATH = os.path.join(PROJECT_ROOT, "data", "LUAS_Dataset.csv")
    BUS_CSV_FILE_PATH = os.path.join(PROJECT_ROOT, "data", "BUS_Dataset.csv")
    try:
        # Test connection to Neo4j
        neo4j_exec.iconnect()

        # Load and clean data
        print("Initializing data cleaning...")
        iclean = IrishTransportData()
        iclean.load_data()
        iclean.check_missing_values()
        iclean.handle_missing_values()
        iclean.clean_data()

        # Perform exploratory data analysis
        print("Performing Exploratory Data Analysis...")
        iclean.exploratory_data_analysis(iclean.dart_data)
        iclean.exploratory_data_analysis(iclean.luas_data)
        iclean.exploratory_data_analysis(iclean.bus_data)

        # Run Streamlit app
        print("Launching Streamlit app...")

         # Test the connection
        neo4j_exec.iconnect()
        # Create master-parent-child nodes
        imaster = MasterNode(URI, USER, PASSWORD)
        imaster.create_master_parent_child_node()

        # Import station data from CSV
        iDart=DartExecution(URI, USER, PASSWORD)
        iDart.import_station_data(DART_CSV_FILE_PATH)
        iDart.create_custom_relationships_from_csv(DART_CSV_FILE_PATH)
        iDart.calculate_degree_centrality()
        iDart.calculate_shortest_path("Adamstown","Ballybrophy")
        iDart.calculate_pagerank("Station","CONNECTED_TO")
        print("********************************************************************************************************************************************")
        iluas=LuasExecution(URI, USER, PASSWORD)
        iluas.import_luas_data(LUAS_CSV_FILE_PATH)
        iluas.create_luas_relationships(LUAS_CSV_FILE_PATH)
        iluas.calculate_degree_centrality()
        iluas.calculate_shortest_path("Tallaght","Belgard")
        iluas.calculate_pagerank("Station","CONNECTED_BY_LINE")
        print("********************************************************************************************************************************************")
        ibus=BusExecution(URI, USER, PASSWORD)
        ibus.import_bus_data(BUS_CSV_FILE_PATH)
        ibus.create_route_relationships()
        ibus.create_route_connections()
        ibus.calculate_degree_centrality()
        ibus.find_shortest_path("Santry (Shanard Rd.)", "Shankill")
        ibus.calculate_pagerank("Route","CONNECTED_TO")

        print("********************************************************************************************************************************************")
        iDart.calculate_pagerank("Station", "CONNECTED_BY_ROUTE")
        iDart.calculate_pagerank("Station", "CONNECTED_BY_LINE")
        iDart.calculate_pagerank("Route", "CONNECTED_TO")
        neo4j_exec.run_streamlit_app()
    finally:
        # Close the Neo4j connection
        print("Closing Neo4j connection...")
        neo4j_exec.close()
