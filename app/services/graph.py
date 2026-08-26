from __future__ import annotations

from typing import Any

from neo4j import GraphDatabase

from app.config import settings

DEMO_PROJECTS = [
    {"id": "p1", "name": "Climate Atlas", "domain": "Climate & Energy", "summary": "Open datasets and high-resolution spatial models for coastal climate risk mapping."},
    {"id": "p2", "name": "Civic Lens", "domain": "Civic Tech", "summary": "Public data pipelines and interactive tools making local municipal budgets transparent."},
    {"id": "p3", "name": "CareGraph", "domain": "Healthcare", "summary": "Knowledge graph connecting community clinics, social services, and patient support networks."},
    {"id": "p4", "name": "NeuroFlow", "domain": "AI & BioTech", "summary": "Open-source neural signal processing and brain-computer interface telemetry library."},
    {"id": "p5", "name": "GridPulse", "domain": "Climate & Energy", "summary": "Real-time renewable energy load forecasting and microgrid balancing engine."},
    {"id": "p6", "name": "OmniMesh", "domain": "Decentralized Systems", "summary": "Resilient peer-to-peer mesh networking protocols for emergency disaster relief."},
    {"id": "p7", "name": "BioSynthese", "domain": "Healthcare", "summary": "Generative protein folding analysis and open drug repurposing discovery workbench."},
    {"id": "p8", "name": "PolicyEcho", "domain": "Civic Tech", "summary": "NLP-powered legislative tracking and cross-jurisdiction policy comparison engine."},
]
DEMO_PEOPLE = [
    {"id": "a1", "name": "Maya Chen", "role": "Data journalist & Lead", "org": "Signal Lab"},
    {"id": "a2", "name": "Jon Bell", "role": "Product designer", "org": "Northstar Systems"},
    {"id": "a3", "name": "Dr. Priya Shah", "role": "Climate researcher", "org": "Open Earth Institute"},
    {"id": "a4", "name": "Theo Martins", "role": "Civic technologist", "org": "Common Ground"},
    {"id": "a5", "name": "Elena Rostova", "role": "Distributed systems engineer", "org": "Hyperion Network"},
    {"id": "a6", "name": "Dr. Tariq Vance", "role": "Computational biologist", "org": "BioFrontiers Lab"},
    {"id": "a7", "name": "Sora Takahashi", "role": "ML research engineer", "org": "Aether AI"},
    {"id": "a8", "name": "Amara Okafor", "role": "Energy systems analyst", "org": "CleanGrid Initiative"},
]
DEMO_TOPICS = [
    {"id": "t1", "name": "Open Data"},
    {"id": "t2", "name": "Climate Resilience"},
    {"id": "t3", "name": "Public Health"},
    {"id": "t4", "name": "Machine Learning"},
    {"id": "t5", "name": "Decentralized Networks"},
    {"id": "t6", "name": "Community Infrastructure"},
    {"id": "t7", "name": "Neural Interfaces"},
]
DEMO_WORKS_ON = [
    ("a1", "p1"), ("a1", "p2"), ("a1", "p8"),
    ("a2", "p2"), ("a2", "p4"),
    ("a3", "p1"), ("a3", "p5"),
    ("a4", "p2"), ("a4", "p3"), ("a4", "p6"),
    ("a5", "p5"), ("a5", "p6"),
    ("a6", "p3"), ("a6", "p7"),
    ("a7", "p4"), ("a7", "p7"), ("a7", "p8"),
    ("a8", "p1"), ("a8", "p5"),
]
DEMO_FOCUSES_ON = [
    ("p1", "t1"), ("p1", "t2"),
    ("p2", "t1"), ("p2", "t6"),
    ("p3", "t3"), ("p3", "t6"),
    ("p4", "t4"), ("p4", "t7"),
    ("p5", "t2"), ("p5", "t5"),
    ("p6", "t5"), ("p6", "t6"),
    ("p7", "t3"), ("p7", "t4"),
    ("p8", "t1"), ("p8", "t4"),
]
DEMO_LINKS = DEMO_WORKS_ON


class GraphRepository:
    def __init__(self) -> None:
        self.driver = None
        if not settings.demo_mode and settings.neo4j_uri and settings.neo4j_password:
            try:
                self.driver = GraphDatabase.driver(settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password))
            except Exception:
                self.driver = None

    def close(self) -> None:
        if self.driver:
            try:
                self.driver.close()
            except Exception:
                pass

    def health(self) -> dict[str, Any]:
        if settings.demo_mode or not self.driver:
            return {"connected": False, "mode": "demo", "message": "Using included demo data. Add CognoDB credentials to connect."}
        try:
            self.driver.verify_connectivity()
            return {"connected": True, "mode": "cognodb", "message": "Connected to CognoDB."}
        except Exception:
            return {"connected": False, "mode": "fallback", "message": "CognoDB is unreachable; showing demo data."}

    def _read(self, query: str, **params: Any) -> list[dict[str, Any]] | None:
        if not self.driver:
            return None
        try:
            with self.driver.session() as session:
                return [record.data() for record in session.run(query, **params)]
        except Exception:
            return None

    def projects(self, search: str = "") -> list[dict[str, Any]]:
        if not settings.demo_mode and self.driver:
            rows = self._read("""
                MATCH (p:Project)
                WHERE $search = ''
                   OR toLower(p.name) CONTAINS toLower($search)
                   OR toLower(p.domain) CONTAINS toLower($search)
                   OR toLower(p.summary) CONTAINS toLower($search)
                RETURN p.id AS id, p.name AS name, p.domain AS domain, p.summary AS summary
                ORDER BY p.name
            """, search=search)
            if rows is not None:
                return rows

        needle = search.lower().strip()
        return [p for p in DEMO_PROJECTS if not needle or needle in (p["name"] + p["domain"] + p["summary"]).lower()]

    def project(self, project_id: str) -> dict[str, Any] | None:
        if not settings.demo_mode and self.driver:
            rows = self._read("""
                MATCH (p:Project {id: $project_id})
                OPTIONAL MATCH (person:Person)-[:WORKS_ON]->(p)
                OPTIONAL MATCH (p)-[:FOCUSES_ON]->(topic:Topic)
                WITH p,
                     collect(DISTINCT person) AS raw_people,
                     collect(DISTINCT topic) AS raw_topics
                RETURN p.id AS id, p.name AS name, p.domain AS domain, p.summary AS summary,
                       [person IN raw_people WHERE person IS NOT NULL | {id: person.id, name: person.name, role: person.role, org: person.org}] AS people,
                       [topic IN raw_topics WHERE topic IS NOT NULL | {id: topic.id, name: topic.name}] AS topics
            """, project_id=project_id)
            if rows is not None:
                if not rows:
                    return None
                proj = rows[0]
                proj["people"] = [p for p in proj.get("people", []) if p and p.get("id")]
                proj["topics"] = [t for t in proj.get("topics", []) if t and t.get("id")]
                return proj

        projects = [p for p in DEMO_PROJECTS if p["id"] == project_id]
        if not projects:
            return None
        project = dict(projects[0])
        person_ids = {a for a, p in DEMO_WORKS_ON if p == project_id}
        topic_ids = {t for p, t in DEMO_FOCUSES_ON if p == project_id}
        project["people"] = [x for x in DEMO_PEOPLE if x["id"] in person_ids]
        project["topics"] = [x for x in DEMO_TOPICS if x["id"] in topic_ids]
        return project

    def connections(self, project_id: str) -> list[dict[str, Any]]:
        if not settings.demo_mode and self.driver:
            rows = self._read("""
                MATCH (source:Project {id: $project_id})<-[:WORKS_ON]-(person:Person)-[:WORKS_ON]->(related:Project)
                WHERE source <> related
                RETURN related.id AS id, related.name AS name, related.domain AS domain,
                       count(DISTINCT person) AS shared_people
                ORDER BY shared_people DESC, related.name
            """, project_id=project_id)
            if rows is not None:
                return rows

        person_ids = {a for a, p in DEMO_WORKS_ON if p == project_id}
        related = {p for a, p in DEMO_WORKS_ON if a in person_ids and p != project_id}
        results = []
        for p in DEMO_PROJECTS:
            if p["id"] in related:
                shared_count = len({a for a, q in DEMO_WORKS_ON if q == p["id"] and a in person_ids})
                results.append({
                    "id": p["id"],
                    "name": p["name"],
                    "domain": p["domain"],
                    "shared_people": shared_count
                })
        results.sort(key=lambda x: (-x["shared_people"], x["name"]))
        return results

    def stats(self) -> dict[str, int]:
        if not settings.demo_mode and self.driver:
            rows = self._read("""
                OPTIONAL MATCH (p:Project) WITH count(p) AS projects
                OPTIONAL MATCH (a:Person) WITH projects, count(a) AS people
                OPTIONAL MATCH (t:Topic) WITH projects, people, count(t) AS topics
                OPTIONAL MATCH ()-[r]->() RETURN projects, people, topics, count(r) AS relationships
            """)
            if rows is not None and rows:
                return rows[0]

        return {
            "projects": len(DEMO_PROJECTS),
            "people": len(DEMO_PEOPLE),
            "topics": len(DEMO_TOPICS),
            "relationships": len(DEMO_WORKS_ON) + len(DEMO_FOCUSES_ON),
        }
