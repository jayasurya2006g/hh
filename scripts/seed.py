"""Seed Pathfinder into CognoDB.

Usage:
  COGNODB_URI=bolt+s://... COGNODB_PASSWORD=... python scripts/seed.py
"""
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.getenv("COGNODB_URI") or os.getenv("NEO4J_URI")
PASSWORD = os.getenv("COGNODB_PASSWORD") or os.getenv("NEO4J_PASSWORD")
USER = os.getenv("COGNODB_USER", "cognodb")

if not URI or not PASSWORD:
    raise SystemExit("Error: COGNODB_URI and COGNODB_PASSWORD must be configured in .env or environment variables to seed CognoDB.")

people = [
    {"id": "a1", "name": "Maya Chen", "role": "Data journalist & Lead", "org": "Signal Lab"},
    {"id": "a2", "name": "Jon Bell", "role": "Product designer", "org": "Northstar Systems"},
    {"id": "a3", "name": "Dr. Priya Shah", "role": "Climate researcher", "org": "Open Earth Institute"},
    {"id": "a4", "name": "Theo Martins", "role": "Civic technologist", "org": "Common Ground"},
    {"id": "a5", "name": "Elena Rostova", "role": "Distributed systems engineer", "org": "Hyperion Network"},
    {"id": "a6", "name": "Dr. Tariq Vance", "role": "Computational biologist", "org": "BioFrontiers Lab"},
    {"id": "a7", "name": "Sora Takahashi", "role": "ML research engineer", "org": "Aether AI"},
    {"id": "a8", "name": "Amara Okafor", "role": "Energy systems analyst", "org": "CleanGrid Initiative"},
]

projects = [
    {"id": "p1", "name": "Climate Atlas", "domain": "Climate & Energy", "summary": "Open datasets and high-resolution spatial models for coastal climate risk mapping."},
    {"id": "p2", "name": "Civic Lens", "domain": "Civic Tech", "summary": "Public data pipelines and interactive tools making local municipal budgets transparent."},
    {"id": "p3", "name": "CareGraph", "domain": "Healthcare", "summary": "Knowledge graph connecting community clinics, social services, and patient support networks."},
    {"id": "p4", "name": "NeuroFlow", "domain": "AI & BioTech", "summary": "Open-source neural signal processing and brain-computer interface telemetry library."},
    {"id": "p5", "name": "GridPulse", "domain": "Climate & Energy", "summary": "Real-time renewable energy load forecasting and microgrid balancing engine."},
    {"id": "p6", "name": "OmniMesh", "domain": "Decentralized Systems", "summary": "Resilient peer-to-peer mesh networking protocols for emergency disaster relief."},
    {"id": "p7", "name": "BioSynthese", "domain": "Healthcare", "summary": "Generative protein folding analysis and open drug repurposing discovery workbench."},
    {"id": "p8", "name": "PolicyEcho", "domain": "Civic Tech", "summary": "NLP-powered legislative tracking and cross-jurisdiction policy comparison engine."},
]

topics = [
    {"id": "t1", "name": "Open Data"},
    {"id": "t2", "name": "Climate Resilience"},
    {"id": "t3", "name": "Public Health"},
    {"id": "t4", "name": "Machine Learning"},
    {"id": "t5", "name": "Decentralized Networks"},
    {"id": "t6", "name": "Community Infrastructure"},
    {"id": "t7", "name": "Neural Interfaces"},
]

works_on = [
    ("a1", "p1"), ("a1", "p2"), ("a1", "p8"),
    ("a2", "p2"), ("a2", "p4"),
    ("a3", "p1"), ("a3", "p5"),
    ("a4", "p2"), ("a4", "p3"), ("a4", "p6"),
    ("a5", "p5"), ("a5", "p6"),
    ("a6", "p3"), ("a6", "p7"),
    ("a7", "p4"), ("a7", "p7"), ("a7", "p8"),
    ("a8", "p1"), ("a8", "p5"),
]

focuses_on = [
    ("p1", "t1"), ("p1", "t2"),
    ("p2", "t1"), ("p2", "t6"),
    ("p3", "t3"), ("p3", "t6"),
    ("p4", "t4"), ("p4", "t7"),
    ("p5", "t2"), ("p5", "t5"),
    ("p6", "t5"), ("p6", "t6"),
    ("p7", "t3"), ("p7", "t4"),
    ("p8", "t1"), ("p8", "t4"),
]

with GraphDatabase.driver(URI, auth=(USER, PASSWORD)) as driver:
    with driver.session() as session:
        session.run("CREATE CONSTRAINT project_id IF NOT EXISTS FOR (p:Project) REQUIRE p.id IS UNIQUE")
        session.run("CREATE CONSTRAINT person_id IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE")
        session.run("CREATE CONSTRAINT topic_id IF NOT EXISTS FOR (t:Topic) REQUIRE t.id IS UNIQUE")
        session.run("UNWIND $people AS x MERGE (p:Person {id:x.id}) SET p.name=x.name, p.role=x.role, p.org=x.org", people=people)
        session.run("UNWIND $projects AS x MERGE (p:Project {id:x.id}) SET p.name=x.name, p.domain=x.domain, p.summary=x.summary", projects=projects)
        session.run("UNWIND $topics AS x MERGE (t:Topic {id:x.id}) SET t.name=x.name", topics=topics)
        session.run("UNWIND $links AS x MATCH (a:Person {id:x[0]}), (p:Project {id:x[1]}) MERGE (a)-[:WORKS_ON]->(p)", links=works_on)
        session.run("UNWIND $links AS x MATCH (p:Project {id:x[0]}), (t:Topic {id:x[1]}) MERGE (p)-[:FOCUSES_ON]->(t)", links=focuses_on)
print(f"Seed complete: {len(people)} people, {len(projects)} projects, {len(topics)} topics, and {len(works_on) + len(focuses_on)} relationships loaded.")
