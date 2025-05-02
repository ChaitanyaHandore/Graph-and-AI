from neo4j import GraphDatabase

class MasterNode:
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

    def create_master_parent_child_node(self):
        """
        Create Ireland as a parent node, add transport categories,
        and establish relationships between them.
        """

        self.execute_query("MATCH (n) DETACH DELETE n")
        # Step 1: Create the Parent Node (Ireland)
        self.execute_query("CREATE (Ireland:Country {name: 'Ireland'})")

        # Step 2: Create Transport Categories with Properties
        transport_categories = [
            {
                "name": "DART",
                "type": "Rail",
                "operator": "Irish Rail",
                "routes_count": 1,
                "description": "Dublin Area Rapid Transit",
            },
            {
                "name": "LUAS",
                "type": "Tram",
                "operator": "Transdev",
                "routes_count": 2,
                "description": "Dublin Light Rail System",
            },
            {
                "name": "BUS",
                "type": "Road",
                "operator": "Dublin Bus",
                "routes_count": 130,
                "description": "Dublin public bus service",
            },
        ]

        for category in transport_categories:
            self.execute_query(
                f"""
                CREATE (c:Category {{
                    name: '{category['name']}',
                    type: '{category['type']}',
                    operator: '{category['operator']}',
                    routes_count: {category['routes_count']},
                    description: '{category['description']}'
                }})
                """
            )

        # Step 3: Connect Transport Categories to Ireland
        self.execute_query(
            """
            MATCH (Ireland:Country {name: 'Ireland'}),
                  (dart:Category {name: 'DART'}),
                  (luas:Category {name: 'LUAS'}),
                  (bus:Category {name: 'BUS'})
            CREATE (Ireland)-[:HAS_TRANSPORT]->(dart),
                   (Ireland)-[:HAS_TRANSPORT]->(luas),
                   (Ireland)-[:HAS_TRANSPORT]->(bus)
            """
        )
