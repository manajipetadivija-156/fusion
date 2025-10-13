from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name="home"),
    path('login/',views.login,name="login"),
    path('register/',views.register,name="register"),
    path('create/',views.create,name="create"),
    path('post/<int:pk>/', views.read, name="read"),
    path('posts/', views.posts, name="posts"),
    path('profile/', views.profile, name="profile"),
    path('post/<int:pk>/edit',views.edit,name="edit"),
    path('post/<int:pk>/delete',views.delete,name="delete"),
    path('logout/',views.logout,name="logout"),
]
