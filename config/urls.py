from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView

from config.graphql import schema

urlpatterns = [
    path("admin/", admin.site.urls),
    path("ht/", include("health_check.urls")),
    path(
        "graphql/",
        csrf_exempt(GraphQLView.as_view(graphiql=False, schema=schema.get_schema())),
        name="graphql",
    ),
]
