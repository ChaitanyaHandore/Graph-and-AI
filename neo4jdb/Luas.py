from neo4j import GraphDatabase
import os
import csv

class LuasExecution:
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

    def import_luas_data(self, csv_file_path):
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
                MATCH (luas:Category {name: 'LUAS'})
                 CREATE (station:Station 
                 {
                    name: $Station_Name,
                    Line: $Line,
                    Station_ID: $Station_ID,
                    Location: $Location,
                    Key_Features_Attractions: $Key_Features_Attractions,
                    Type: $Type,
                    Interchange: $Interchange,
                    Zone: $Zone,
                    Daily_Footfall: $Daily_Footfall,
                    Facilities: $Facilities,
                    Accessibility: $Accessibility,
                    Latitude: $Latitude,
                    Longitude: $Longitude,
                    Parking_Availability: $Parking_Availability,
                    Nearby_Landmarks: $Nearby_Landmarks,
                    First_Tram_Time: $First_Tram_Time,
                    Last_Tram_Time: $Last_Tram_Time
                })
                CREATE (luas)-[:HAS_STATION]->(station)
                """
                self.execute_query(
                    query,
                    parameters={
                        "Station_Name": row["Station Name"],
                        "Station_ID": row["Station_ID"],
                        "Line": row["Line"],
                        "Location": row["Location"],
                        "Key_Features_Attractions": row["Key Features/Attractions"],
                        "Type": row["Type (Terminus/Regular)"],
                        "Interchange": row["Interchange"],
                        "Zone": row["Zone"],
                        "Daily_Footfall": row["Daily Footfall"],
                        "Facilities": row["Facilities"],
                        "Accessibility": row["Accessibility"],
                        "Latitude": row["Latitude"],
                        "Longitude": row["Longitude"],
                        "Parking_Availability": row["Parking Availability"],
                        "Nearby_Landmarks": row["Nearby Landmarks"],
                        "First_Tram_Time": row["First Tram Time"],
                        "Last_Tram_Time": row["Last Tram Time"],
                    },
                )
        print("LUAS imported successfully!")

    def create_luas_relationships(self, csv_file_path):
        """
        Create relationships between LUAS stations based on the Line attribute.
        """
        if not os.path.exists(csv_file_path):
            print(f"CSV file not found at path: {csv_file_path}")
            return

        with open(csv_file_path, mode='r', encoding='latin1') as file:
            reader = csv.DictReader(file)
            lines_map = {}

            # Group stations by line
            for row in reader:
                line = row["Line"]
                station_name = row["Station Name"]
                if line not in lines_map:
                    lines_map[line] = []
                lines_map[line].append(station_name)

            # Create relationships along each line
            for line, stations in lines_map.items():
                for i in range(len(stations) - 1):
                    station1 = stations[i]
                    station2 = stations[i + 1]

                    query = """
                    MATCH (station1:Station {name: $Station1}),
                          (station2:Station {name: $Station2})
                    MERGE (station1)-[:CONNECTED_BY_LINE {line: $Line}]->(station2)
                    """
                    self.execute_query(
                        query,
                        parameters={
                            "Station1": station1,
                            "Station2": station2,
                            "Line": line,
                        },
                    )
        print("LUAS relationships created successfully!")

    def calculate_shortest_path(self, start_station, end_station):
        """
        Calculate the shortest path between two LUAS stations using plain Cypher queries.
        """
        query = """
        MATCH (start:Station {name: $StartStation}), (end:Station {name: $EndStation})
        MATCH p = shortestPath((start)-[:CONNECTED_BY_LINE*]-(end))
        RETURN [node IN nodes(p) | node.name] AS path, 
               reduce(totalDistance = 0, r IN relationships(p) | totalDistance + r.distance_km) AS totalDistance
        """
        try:
            result = self.execute_query(query, {
                "StartStation": start_station,
                "EndStation": end_station
            })
            print("Shortest path calculation successful.")
            return result
        except Exception as e:
            print(f"Shortest path calculation failed: {e}")

    def calculate_degree_centrality(self):
        """
        Calculate degree centrality for all LUAS stations using plain Cypher queries.
        """
        query = """
        MATCH (s:Station)-[r:CONNECTED_BY_LINE]-(t:Station)
        RETURN s.name AS station, COUNT(r) AS DegreeCentrality
        ORDER BY DegreeCentrality DESC
        """
        try:
            result = self.execute_query(query)
            print("Degree centrality calculation successful.")
            return result
        except Exception as e:
            print(f"Degree centrality calculation failed: {e}")

    def calculate_pagerank(self, node_label, relationship_type):
        """
        Calculate PageRank for LUAS nodes and relationships.
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
            print("PageRank calculation for LUAS completed successfully.")
            return result
        except Exception as e:
            print(f"PageRank calculation failed: {e}")
