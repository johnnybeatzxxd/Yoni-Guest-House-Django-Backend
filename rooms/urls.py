
from django.urls import path, include
from . import views
urlpatterns = [
    path("available",views.available_rooms),
]
