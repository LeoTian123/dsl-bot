from django.urls import path
from . import views

urlpatterns = [
    path('api/chat/', views.chat),
    path('api/chat_init/', views.chat_init),
    path('api/chat_destroy/', views.chat_destroy)
]