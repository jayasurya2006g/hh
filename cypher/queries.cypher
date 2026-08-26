// Pathfinder graph model
// (:Person)-[:WORKS_ON {since}]->(:Project)-[:FOCUSES_ON]->(:Topic)
// (:Person)-[:KNOWS]->(:Person)

CREATE CONSTRAINT project_id IF NOT EXISTS FOR (p:Project) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT person_id IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT topic_id IF NOT EXISTS FOR (t:Topic) REQUIRE t.id IS UNIQUE;

// 1-hop: project detail
MATCH (p:Project {id: $project_id})
OPTIONAL MATCH (person:Person)-[:WORKS_ON]->(p)
OPTIONAL MATCH (p)-[:FOCUSES_ON]->(topic:Topic)
RETURN p, collect(DISTINCT person), collect(DISTINCT topic);

// 2-hop: projects connected by shared contributors
MATCH (source:Project {id: $project_id})<-[:WORKS_ON]-(person:Person)-[:WORKS_ON]->(related:Project)
WHERE source <> related
RETURN related, count(DISTINCT person) AS shared_people
ORDER BY shared_people DESC;

// Graph-native recommendation: people who could bridge a project to a topic
MATCH (p:Project {id: $project_id})<-[:WORKS_ON]-(person:Person)-[:WORKS_ON]->(other:Project)-[:FOCUSES_ON]->(topic:Topic)
WHERE NOT (p)-[:FOCUSES_ON]->(topic)
RETURN topic.name AS topic, collect(DISTINCT person.name) AS bridge_people, count(DISTINCT other) AS supporting_projects
ORDER BY supporting_projects DESC;
