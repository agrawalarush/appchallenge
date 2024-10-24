from django.urls import path
from . import views

urlpatterns = [
    path("sign_up/", views.sign_up),
    path("sign_in/", views.sign_in),
    path("sign_out/", views.sign_out),
    path("add_products/", views.add_product),
    path("active_user/<int:user_id>/", views.reactivate_user),
    path('update_item/', views.updateItem),
    path("cart/", views.view_cart),
    path("checkout/", views.checkout),
    path("", views.geocode_address_1)
]