from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path(r"ht/", include("health_check.urls")),
    path(
        "api/",
        include(
            [
                path("auth/", include("apps.auths.urls"), name="auth"),
                path(
                    "schema/",
                    include(
                        [
                            path("", SpectacularAPIView.as_view(), name="schema"),
                            path(
                                "swagger/",
                                SpectacularSwaggerView.as_view(url_name="schema"),
                                name="swagger",
                            ),
                            path(
                                "redoc/",
                                SpectacularRedocView.as_view(url_name="schema"),
                                name="redoc",
                            ),
                        ],
                    ),
                ),
            ],
        ),
    ),
]
