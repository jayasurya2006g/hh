"""Clear all data from CognoDB.

Usage:
  python scripts/clear.py
"""
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.getenv("COGNODB_URI") or os.getenv("NEO4J_URI")
PASSWORD = os.getenv("COGNODB_PASSWORD") or os.getenv("NEO4J_PASSWORD")
USER = os.getenv("COGNODB_USER", "cognodb")

if not URI or not PASSWORD:
    raise SystemExit("Error: COGNODB_URI and COGNODB_PASSWORD must be configured in .env or environment variables.")

with GraphDatabase.driver(URI, auth=(USER, PASSWORD)) as driver:
    with driver.session() as session:
        result = session.run("MATCH (n) DETACH DELETE n")
        summary = result.consume()
        print(f"Cleared database: {summary.counters.nodes_deleted} nodes deleted, {summary.counters.relationships_deleted} relationships deleted.")

