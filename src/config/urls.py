"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from src.apps.demosite import views as demosite_views
from src.apps.backend import views as backend_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('backend/v1/share', backend_views.share_data, name='backend.v1.share'),
    path('backend/v1/analyze', backend_views.tls_info, name='backend.v1.analyze'),
    path('backend/v1/initial', backend_views.initial, name='backend.v1.initial'),
    path('backend/v1/token', backend_views.generate_token, name='backend.v1.token'),
    path('backend/v1/info', backend_views.analyze_token, name='backend.v1.info'),
    path('share', demosite_views.share, name='share'),
    path('analyze', demosite_views.analyze, name='analyze')
]
