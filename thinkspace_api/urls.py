"""thinkspace_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
from api import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'user-courses', views.CourseViewSet)
router.register(r'projects', views.ProjectViewSet)
router.register(r'project-categories', views.ProjectCategoryViewSet)
router.register(r'project-join-requests', views.ProjectJoinRequestViewSet)
router.register(r'project-comments', views.ProjectCommentViewSet)
router.register(r'project-posts', views.ProjectPostViewSet)
router.register(r'project-tags', views.ProjectTagViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^docs/', include_docs_urls(title='Thinkspace API', public=False)),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                            document_root=settings.STATIC_ROOT)
