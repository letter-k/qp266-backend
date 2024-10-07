import apps.auths.schema
from config.graphql_tool import SchemaRegistry

schema = SchemaRegistry()

schema.register_query(apps.auths.schema.Query)
schema.register_mutation(apps.auths.schema.Mutation)
