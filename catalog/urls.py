from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.home, name="home"),
    path("healthz/", views.healthz, name="healthz"),
    path("titles/<slug:slug>/", views.title_detail, name="title_detail"),
    path("genres/<slug:slug>/", views.genre_detail, name="genre_detail"),
    path("titles/<slug:slug>/watch/", views.title_watch, name="title_watch"),
]
