from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.views import serve as serve_static
from django.urls import include, path, re_path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("casa.inventory.urls")),
]

if settings.DEBUG or settings.SERVE_STATIC:
    urlpatterns += [
        re_path(r"^static/(?P<path>.*)$", serve_static, {"insecure": True}),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
