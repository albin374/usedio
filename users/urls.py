from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_view, name='register'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    
    # Generic sell and listing routes
    path('sell/<str:category_name>/', views.sell_product, name='sell_product'),
    path('<str:category_name>_listing/', views.product_listing, name='product_listing'),

    # Buying route
    path('buy/<int:product_id>/', views.buy_product, name='buy_product'),
    path('payment/<int:product_id>/', views.payment_page, name='payment_page'),
    path('user_purchased/', views.user_purchased_products, name='user_purchased_products'),
    path('user_added/', views.user_added_products, name='user_added_products'),
    path('update-product/<int:product_id>/', views.update_product, name='update_product'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('change-password/', views.change_password, name='change_password'),
    path('about/', views.about, name='about'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
