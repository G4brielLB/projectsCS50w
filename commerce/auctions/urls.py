from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:category>", views.listing_category, name="listing_category"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("listing/bid/<int:listing_id>", views.bid, name="bid"),
    path("listing/comment/<int:listing_id>", views.comment, name="comment"),
    path("listing/close/<int:listing_id>", views.close_listing, name="close_listing"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register")
]
