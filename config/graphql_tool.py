from functools import wraps

import graphene
from graphene import ResolveInfo
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import NotAuthenticated


class SchemaRegistry:
    def __init__(self):
        self.queries = []
        self.mutations = []

    def register_query(self, query):
        self.queries.append(query)

    def register_mutation(self, mutation):
        self.mutations.append(mutation)

    def get_schema(self):
        class Query(*self.queries, graphene.ObjectType):
            pass

        class Mutation(*self.mutations, graphene.ObjectType):
            pass

        return graphene.Schema(query=Query, mutation=Mutation)


def context(f):
    def decorator(func):
        def wrapper(*args, **kwargs):
            info = next(arg for arg in args if isinstance(arg, ResolveInfo))
            return func(info.context, *args, **kwargs)

        return wrapper

    return decorator


def user_passes_test(test_func, exc=NotAuthenticated):
    def decorator(f):
        @wraps(f)
        @context(f)
        def wrapper(context, *args, **kwargs):
            if test_func(context.user):
                return f(*args, **kwargs)
            raise exc

        return wrapper

    return decorator


login_required = user_passes_test(lambda u: u.is_authenticated)


class GraphqlMiddleware(TokenAuthentication):
    keyword = "Bearer"

    def resolve(self, next, root, info, **args):
        auth = self.authenticate(info.context)

        if auth:
            user, token = auth
            info.context.user = user

        return next(root, info, **args)
