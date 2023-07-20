from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='Home'),
    path('additem/', views.addItem, name='AddItem'),
    path('searchreceipt/', views.searchReceipt, name='SearchReceipt'),
    path('r<int:id>/', views.addReceipt, name='AddReceipt'),
    path('i<int:id>/', views.showItem, name='ShowItem'),
]