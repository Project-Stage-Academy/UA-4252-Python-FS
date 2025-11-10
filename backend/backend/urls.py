"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/common/", include("apps.common.urls")),
    path("api/auth/", include("apps.authentication.urls")),
    path("api/startups/", include("apps.startups.urls")),
    path("api/", include("api.authorization.urls")),
    path("common/", include("apps.common.urls")),
    path("api/", include("apps.projects.urls")),
    # path("api/projects/", include("apps.projects.urls")),
    path("api/investors/", include("apps.investors.urls")),
    path("api/users/", include("apps.users.urls")),
    path("api/messages/", include("apps.user_messages.urls")),
    path("api/search/", include("apps.search.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
