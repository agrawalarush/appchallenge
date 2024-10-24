from django.urls import path
from . import views

urlpatterns = [
    path("", views.all_products),
    path("<int:product_id>/", views.view_product)
]