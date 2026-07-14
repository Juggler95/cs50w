from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new", views.create_listing, name="new"),
    path("view/<str:title>", views.view_listing, name="view_listing"),
    path("AddToWatchlist", views.addToWatchlist, name="addToWatchlist"),
    path("watchlist", views.watchlist_view, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("category/<str:title>", views.category_view, name="category")
]
