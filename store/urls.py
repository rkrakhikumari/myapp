from django.urls import path
from . import views
from .views import register, user_login, user_logout
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('', views.home, name="home"),
    
    path('product/<int:product_id>/', views.product_detail, name="product_detail"), 
    path("cart/",views.cart_view, name="cart"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/<int:cart_id>/<str:action>/", views.update_cart, name="update_cart"),
    path("cart/remove/<int:cart_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("cart/update/<int:cart_item_id>/", views.update_cart_quantity, name="update_cart_quantity"),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('place-order/', views.place_order, name='place_order'),
    path('about/', views.about_us, name='about_us'),
    # path('contact-success/', views.contact_success, name='contact_success'), 
    path('order-success/<int:order_id>/', views.order_success, name='order-success'),
    path('cart/history/', views.order_history, name='cart_history'),
    # path('send-otp/', views.send_otp, name='send-otp'),
    # path('verify-otp/', views.verify_otp, name='verify-otp'),
    path('delete-review/<int:review_id>/', views.delete_review, name='delete_review'),



]
