from django.urls import path

from . import views

urlpatterns = [
    path("api/liens", views.link_list),
    path("api/liens/<str:code>", views.link_detail),
    path("r/<str:code>", views.redirect_to_url),
]