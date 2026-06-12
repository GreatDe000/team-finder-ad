from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

from projects.views import project_list

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", lambda request: redirect("/project/list/"), name="home"),
    path("project/list/", project_list, name="project_list"),
    path("project/list", project_list),
    path("projects/", include("projects.urls")),
    path("users/", include("users.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
