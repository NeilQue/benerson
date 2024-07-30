from django.urls import path
from . import views

urlpatterns = [
    path('', views.addReceipt, name='AddReceipt'),
    path('inventory/', views.home, name='Home'),
    path('additem-action=<str:action>/', views.addItem, name='AddItem'),
    path('i<int:id>/', views.showItem, name='ShowItem'),
    path('customersList/', views.customersList, name='CustomersList'),
    path('addcustomer-action=<str:action>/', views.addCustomer, name='AddCustomer'),
    path('c<int:id>/', views.showCustomer, name='ShowCustomer'),
    path('searchreceipt/', views.searchReceipt, name='SearchReceipt'),
    path('r<int:id>/', views.showReceipt, name='ShowReceipt')
]