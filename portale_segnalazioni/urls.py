# -*- coding: utf-8 -*-
"""portale_segnalazioni URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.gis import admin
admin.autodiscover()

admin.site.site_title = 'Segnalazioni criticità'
admin.site.site_header = 'Segnalazioni criticità'

urlpatterns = [
    url(r'^grappelli/', include('grappelli.urls')), # grappelli URLS
    url('', admin.site.urls),
    url(r'^chaining/', include('smart_selects.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
