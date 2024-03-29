from django.contrib import admin
from django.urls import path, include
from rest_framework_swagger.views import get_swagger_view
from django.conf import settings
from django.conf.urls.static import static


schema_view = get_swagger_view(title="MyFairy API")
urlpatterns = [
    path("", schema_view),
    path("admin/", admin.site.urls),
    path("api/chat/", include("index.chat.urls", namespace="chat")),
    path("api/", include("index.urls")),
    path("api/", include("product.api.urls")),
    path("socket/", include("sio_app.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
