from neo4j import GraphDatabase
import os
import csv

class BusExecution:
    def __init__(self, uri, user, password):
        """Initialize the Neo4j connection"""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

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

    def import_bus_data(self, csv_file_path):
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
                        MATCH (category:Category {name: 'BUS'})
                        CREATE (route:Route {
                            `Route Number`: $Route_Number,
                             From: $From,
                             To: $To,
                            `Route Type`: $Route_Type,
                            Frequency: $Frequency,
                            Duration: $Duration,
                            `Key Landmarks`: $Key_Landmarks,
                            `Peak Hours`: $Peak_Hours,
                            Operator: $Operator,
                            `Primary Areas Served`: $Primary_Areas_Served
                        })
                        CREATE (category)-[:HAS_ROUTE]->(route)
                        """

                # Map CSV columns to query parameters
                self.execute_query(
                    query,
                    parameters={
                        "Route_Number": row["Route Number"],
                        "From": row["From"],
                        "To": row["To"],
                        "Route_Type": row["Route Type"],
                        "Frequency": row["Frequency"],
                        "Duration": row["Duration"],
                        "Key_Landmarks": row["Key Landmarks"],
                        "Peak_Hours": row["Peak Hours"],
                        "Operator": row["Operator"],
                        "Primary_Areas_Served": row["Primary Areas Served"],
                    },
                )
        print("BUS imported successfully")

    def create_route_relationships(self):
        """
        Create relationships between bus routes based on shared areas and landmarks.
        """
        query = """
           MATCH (route1:Route), (route2:Route)
           WHERE route1 <> route2
           AND ANY(landmark IN split(route1.`Key Landmarks`, ', ') 
                   WHERE landmark IN split(route2.`Key Landmarks`, ', '))
           CREATE (route1)-[:SHARES_LANDMARK]->(route2)
           """
        self.execute_query(query)
        print("Relationships based on shared landmarks created.")

    def create_route_connections(self):
        """
        Create relationships between bus routes that share starting or ending points.
        """
        query = """
           MATCH (route1:Route), (route2:Route)
           WHERE route1 <> route2
           AND (route1.From = route2.From OR route1.To = route2.To)
           CREATE (route1)-[:CONNECTED_TO]->(route2)
           """
        self.execute_query(query)
        print("Route connections created based on shared start or end points.")

    def calculate_degree_centrality(self):
        """
        Calculate degree centrality for all stops using plain Cypher queries.
        """
        degree_centrality_query = """
        MATCH (s:Stop)-[r:CONNECTS]-(t:Stop)
        RETURN s.name AS stop, COUNT(r) AS DegreeCentrality
        ORDER BY DegreeCentrality DESC
        """
        try:
            result = self.execute_query(degree_centrality_query)
            print("Degree centrality calculated successfully.")
            for record in result:
                print(f"Stop: {record['stop']}, Centrality: {record['DegreeCentrality']}")
        except Exception as e:
            print(f"Degree centrality calculation failed: {e}")

    def find_shortest_path(self, start_stop, end_stop):
        """
        Calculate the shortest path between two stops using plain Cypher queries.
        """
        shortest_path_query = """
        MATCH (start:Route {From: $StartStop}), (end:Route {To: $EndStop})
        MATCH p = shortestPath((start)-[:CONNECTED_TO*]-(end))
        RETURN [node IN nodes(p) | node.`Route Number`] AS path, 
               reduce(totalDistance = 0, r IN relationships(p) | totalDistance + r.distance_kms) AS totalDistance
        """
        try:
            result = self.execute_query(shortest_path_query, {
                "StartStop": start_stop,
                "EndStop": end_stop
            })
            print("Shortest path calculation successful.")
            for record in result:
                print(f"Path: {record['path']}, Total Distance: {record['totalDistance']}")
        except Exception as e:
            print(f"Shortest path calculation failed: {e}")

    def calculate_pagerank(self, node_label, relationship_type):
        """
        Calculate PageRank for BUS nodes and relationships.
        """
        query = f"""
        CALL algo.pageRank.stream(
            '{node_label}', 
            '{relationship_type}', 
            {{iterations:20, dampingFactor:0.85}})
        YIELD nodeId, score
        RETURN algo.getNodeById(nodeId).name AS name, score
        ORDER BY score DESC
        """
        try:
            result = self.execute_query(query)
            print("PageRank calculation for BUS completed successfully.")
            return result
        except Exception as e:
            print(f"PageRank calculation failed: {e}")
