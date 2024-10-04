from apps.auths.schema import Mutation, Query
from config.graphql_tool import SchemaRegistry

schema = SchemaRegistry()
schema.register_query(Query)
schema.register_mutation(Mutation)
