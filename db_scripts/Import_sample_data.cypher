// Import sample data
CALL apoc.load.json("file:/sample_neo4j.json") YIELD value
WITH value.graph.nodes AS nodes, value.graph.relationships AS rels
UNWIND nodes AS n
CALL apoc.create.node(n.labels, apoc.map.setKey(n.properties, 'id', n.id)) YIELD node
WITH rels, COLLECT({id: n.id, node: node, labels:labels(node)}) AS nMap
UNWIND rels AS r
MATCH (w{id:r.startNode})
MATCH (y{id:r.endNode})
CALL apoc.create.relationship(w, r.type, r.properties, y) YIELD rel
RETURN rel