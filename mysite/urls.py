from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("polls/", include("polls.urls")),
    path("accounts/", include("allauth.urls")),
    path("api/analytics/", include(("analytics.urls", "analytics"), namespace="analytics")),
]
