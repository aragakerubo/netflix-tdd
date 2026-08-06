from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.home, name="home"),
    path("titles/<slug:slug>/", views.title_detail, name="title_detail"),
]
