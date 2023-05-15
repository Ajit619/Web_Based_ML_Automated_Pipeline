"""MLRT URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path,include
from MLAPP import views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/',include('MLAPP.api.urls')),
    path("",views.MLRT.home),
    path('missing_value/',views.MLRT.missing_value),
    path('missing_value/<int:skip>',views.MLRT.missing_value),
    path('unwanted_column/',views.MLRT.unwanted_column),
    path('outliers/',views.MLRT.outliers),
    path('unwanted_column/<int:skip>',views.MLRT.unwanted_column),
    path('outliers/<int:skip>',views.MLRT.outliers),
    path('label_encoding/<int:skip>',views.MLRT.label_encoding),
    path('label_encoding/',views.MLRT.label_encoding),
    path('scaling/',views.MLRT.scaling),
    path('train_test/',views.MLRT.train_test),
    path('model_building/',views.MLRT.model_building),
    path('predict/',views.MLRT.predict),
    path('predict/<int:predict>',views.MLRT.predict),
    path('model_building/<int:predict>',views.MLRT.model_building),
    path('download/',views.MLRT.download),

]+ static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

