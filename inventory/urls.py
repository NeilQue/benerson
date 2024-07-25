from django.urls import path
from . import views

urlpatterns = [
    path('inventory/', views.home, name='Home'),
    path('additem/', views.addItem, name='AddItem'),
    path('searchreceipt/', views.searchReceipt, name='SearchReceipt'),
    path('r<int:id>/', views.showReceipt, name='ShowReceipt'),
    path('i<int:id>/', views.showItem, name='ShowItem'),
    path('', views.addReceipt, name='AddReceipt'),
]