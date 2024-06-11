from django.urls import path
from carshop import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('ajax/load-car-models/', views.load_car_models, name='ajax_load_car_models'),
    path('catalog/', views.catalog, name='catalog'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('cart/', views.cart, name='cart'),
    path('add_to_cart/<int:car_id>/', views.add_to_cart, name='add_to_cart'),
    path('orders/', views.orders, name='orders'),
    path('order_success/', views.order_success, name='order_success'),
    path('all_orders/', views.all_orders, name='all_orders'),
    path('checkout/', views.checkout, name='checkout'),
    path('contacts/', views.contacts, name='contacts'),
    path('aboutus/', views.aboutus, name='aboutus'),
    path('edit/<int:car_id>/', views.edit_car, name='edit_car'),
    path('delete_car/<int:id>/', views.delete_car, name='delete_car'),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)








