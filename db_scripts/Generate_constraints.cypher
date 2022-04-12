// Generate constraints
CREATE CONSTRAINT ON (n:Node) assert n.neo4jImportId IS UNIQUE;
CREATE CONSTRAINT ON (n:Ingredient) assert n.neo4jImportId IS UNIQUE;