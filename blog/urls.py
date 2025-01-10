from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.homePage, name='home'),
    path('tag/<slug:tag_slug>/', views.homePage, name='products_by_tag'),  # Added trailing slash
    path('product/<int:pk>/<slug:slug>/', views.productDetail, name='product_detail'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('update-item/', views.updateItem, name='update_item'),
    path('register/', views.registerPage.as_view(), name='register'),
    path('login/', views.loginPage.as_view(), name='login'),
    path('logout/', views.logoutPage, name='logout'),
    path('account/', views.accountPage, name='account'),
    path('search/', views.post_search, name='search'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-error/', views.payment_error, name='payment_error'),
   
    
    # Added payment error route
    # path('payment-callback/', views.payment_callback, name='payment_callback'),  # Added payment callback route
]
