# config.py

# Configuration for Neo4j connection
NEO4J_CONFIG = {
    "uri": "bolt://localhost:7687",
    "username": "neo4j",
    "password": "9820065151",
}

def get_neo4j_config():
    """
    Returns the Neo4j configuration settings.

    :return: Dictionary containing Neo4j connection details.
    """
    return NEO4J_CONFIG

# Example usage (for debugging, remove in production):
if __name__ == "__main__":
    config = get_neo4j_config()
    print("Neo4j Configuration:")
    for key, value in config.items():
        print(f"{key}: {value}")
