
from django.urls import path, include
from . import views
urlpatterns = [
    path("available",views.available_rooms),
    path("book",views.book_reservation),
    path("pay",views.payment_received),
]
