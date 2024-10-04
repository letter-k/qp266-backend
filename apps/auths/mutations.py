import graphene
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token


class AuthArguments(graphene.InputObjectType):
    username = graphene.String(required=True)
    password = graphene.String(required=True)


class ObtainAuthToken(graphene.Mutation):
    class Arguments:
        credentials = AuthArguments()

    token = graphene.String()

    def mutate(cls, info, credentials):
        user = authenticate(username=credentials.username, password=credentials.password)
        if user is None:
            raise Exception("Invalid username or password")

        token, created = Token.objects.get_or_create(user=user)
        return ObtainAuthToken(token=token.key)
