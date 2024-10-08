from graphene import ObjectType, String

from apps.auths.mutations import ObtainAuthToken, UserRegister
from config.graphql_tool import login_required


class Mutation(ObjectType):
    obtainAuthToken = ObtainAuthToken.Field()
    userRegister = UserRegister.Field()


class Query(ObjectType):
    ping = String()

    @login_required
    def resolve_ping(self, info):
        return "PONG"
