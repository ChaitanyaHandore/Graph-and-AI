
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from neo4j import GraphDatabase
import os
import csv

class DartExecution:
    def __init__(self, uri, user, password):
        """Initialize the Neo4j connection"""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        DART_CSV_FILE_PATH = os.path.join(PROJECT_ROOT, "data","DART_Dataset.csv")
    def close(self):
        """Close the Neo4j connection"""
        if self.driver:
            self.driver.close()

    def execute_query(self, query, parameters=None):
        """Execute a given Cypher query."""
        with self.driver.session() as session:
            try:
                result = session.run(query, parameters)
                return [record for record in result]
            except Exception as e:
                print(f"Query execution failed: {e}")

    def import_station_data(self, csv_file_path):
        """
        Import station data for the DART node from a CSV file.
        """
        if not os.path.exists(csv_file_path):
            print(f"CSV file not found at path: {csv_file_path}")
            return

        with open(csv_file_path, mode='r', encoding='latin1') as file:
            reader = csv.DictReader(file)
            for row in reader:
                query = """
                MATCH (dart:Category {name: 'DART'})
                CREATE (station:Station {
                    name: $StationName,
                    operational: $Operational,
                    location: $Location,
                    address: $StationAddress,
                    eircode: $Eircode,
                    atm: $ATM,
                    weekend_working: $WeekendWorking,
                    wifi: $WiFiAccess,
                    refreshments: $Refreshments,
                    phone_charging: $PhoneCharging,
                    ticket_machine: $TicketVendingMachine,
                    smart_card_enabled: $SmartCardEnabled,
                    routes_serviced: $RoutesServiced
                })
                CREATE (dart)-[:HAS_STATION]->(station)
                """
                self.execute_query(
                    query,
                    parameters={
                        "StationName": row["StationName"],
                        "Operational": row["Operational"],
                        "Location": row["Location"],
                        "StationAddress": row["Station Address"],
                        "Eircode": row["Eircode"],
                        "ATM": row["ATM"],
                        "WeekendWorking": row["Weekend Working"],
                        "WiFiAccess": row["Wi-Fi & Internet Access"],
                        "Refreshments": row["Refreshments"],
                        "PhoneCharging": row["Phone Charging"],
                        "TicketVendingMachine": row["Ticket Vending Machine"],
                        "SmartCardEnabled": row["Smart Card Enabled"],
                        "RoutesServiced": row["Routes Serviced"],
                    },
                )
        print("DART imported successfully!")

    def create_custom_relationships_from_csv(self, csv_file_path):
        """
        Create relationships based on routes serviced, customized for shortest path and centrality analysis.
        """
        if not os.path.exists(csv_file_path):
            print(f"CSV file not found at path: {csv_file_path}")
            return

        with open(csv_file_path, mode='r', encoding='latin1') as file:
            reader = csv.DictReader(file)

            stations = []
            routes_map = {}

            # Collect stations and their routes
            for row in reader:
                station_name = row["StationName"]
                stations.append(station_name)
                routes = [r.strip() for r in row["Routes Serviced"].split(',')]

                for route in routes:
                    if route not in routes_map:
                        routes_map[route] = []
                    routes_map[route].append((station_name, float(row["Distance_km"])))

            # Create relationships
            for route, stations_in_route in routes_map.items():
                for i in range(len(stations_in_route) - 1):
                    station1, distance1 = stations_in_route[i]
                    station2, distance2 = stations_in_route[i + 1]

                    query = """
                    MATCH (station1:Station {name: $Station1}),
                          (station2:Station {name: $Station2})
                    MERGE (station1)-[r:CONNECTED_BY_ROUTE {
                        route: $Route,
                        distance_km: $Distance
                    }]->(station2)
                    """
                    self.execute_query(
                        query,
                        parameters={
                            "Station1": station1,
                            "Station2": station2,
                            "Route": route,
                            "Distance": (distance1 + distance2) / 2,  # Average distance
                        },
                    )
        print("Customized relationships created successfully!")

    def calculate_degree_centrality(self):
        """
        Calculate degree centrality for all stations using plain Cypher queries.
        """
        degree_centrality_query = """
        MATCH (s:Station)-[r:CONNECTED_BY_ROUTE]-(t:Station)
        RETURN s.name AS station, COUNT(r) AS DegreeCentrality
        ORDER BY DegreeCentrality DESC
        """
        try:
            result = self.execute_query(degree_centrality_query)
            print("Degree centrality calculated successfully.")
            return result
        except Exception as e:
            print(f"Degree centrality calculation failed: {e}")

    def calculate_shortest_path(self, start_station, end_station):
        """
        Calculate the shortest path between two stations using plain Cypher queries.
        """
        shortest_path_query = """
        MATCH (start:Station {name: $StartStation}), (end:Station {name: $EndStation})
        MATCH p = shortestPath((start)-[:CONNECTED_BY_ROUTE*]-(end))
        RETURN [node IN nodes(p) | node.name] AS path, 
               reduce(totalDistance = 0, r IN relationships(p) | totalDistance + r.distance_km) AS totalDistance;
        """
        try:
            result = self.execute_query(shortest_path_query, {
                "StartStation": start_station,
                "EndStation": end_station
            })
            print("Shortest path calculation successful.")
            return result
        except Exception as e:
            print(f"Shortest path calculation failed: {e}")

    def calculate_pagerank(self, node_label, relationship_type):
        """
        Calculate PageRank for given node labels and relationships in Neo4j Community Edition.
        """
        # Step 1: Initialize ranks
        initialize_query = f"""
        MATCH (n:{node_label})
        SET n.rank = 1.0;
        """

        # Step 2: Calculate contributions
        contribution_query = f"""
        MATCH (n:{node_label})-[r:{relationship_type}]->(m:{node_label})
        WITH m, n.rank AS rank, COUNT(r) AS outgoingCount
        WITH m, SUM(rank / outgoingCount) AS contribution
        SET m.rank = contribution;
        """

        # Execute the queries separately
        try:
            self.execute_query(initialize_query)
            print(f"Rank initialization for {node_label} completed successfully.")

            self.execute_query(contribution_query)
            print(f"PageRank calculation for {node_label} completed successfully.")
        except Exception as e:
            print(f"PageRank calculation failed: {e}")

