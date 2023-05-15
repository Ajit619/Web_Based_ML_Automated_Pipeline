from django.urls import path,include
from rest_framework.routers import DefaultRouter
from MLAPP.api import views
# router=DefaultRouter()
# router.register('read_dataset/',views.read_dataset)
urlpatterns=[
    path('read_dataset/',views.read_dataset),
    path("read_dataset/<data>/",views.read_dataset),
    path("mean_value/",views.mean_value),
    path("mode_value/",views.mode_value),
    path("median_value/",views.median_value),
    path("zero_value/",views.zero_value),
    path("del_na_row/",views.del_na_row),
    path("check_null_values/",views.check_null_values),
    path("unwanted_column/",views.unwanted_column),
    path("detect_outliers/",views.detect_ouliers),
    path("remove_outliers/",views.remove_outliers),
    path("label_encoding/",views.label_encoding),
    path("scaling/",views.scaling),
    path("train_test/",views.train_test),
    path("model_building/",views.model_building),
    path("predict/",views.predict),
    path("track_file/",views.track_file),
    path("track_pdf/",views.track_pdf),
]