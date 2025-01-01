from django.urls import path, include
from .views.user_views import (
    DashboardView,
    UserLoginView,
    UserSignupView,
    forgot_password,
    logout_view,
    add_address,
    update_address,
    delete_address,
    ProfileView,
    OrderListView,
    WishlistView,
    AddressListView,
    ChangePasswordView,
    toggle_wishlist,
)
from django.views.decorators.http import require_http_methods
from .views import admin_views

app_name = "users"

urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("signup/", UserSignupView.as_view(), name="signup"),
    path("logout/", require_http_methods(["POST"])(logout_view), name="logout"),
    path("forgot-password/", forgot_password, name="forgot-password"),
    path(
        "api/",
        include(
            [
                path("address/add/", add_address, name="add_address"),
                path("address/update/", update_address, name="update_address"),
                path("address/delete/", delete_address, name="delete_address"),
                path("wishlist/toggle/", toggle_wishlist, name="toggle_wishlist"),
            ]
        ),
    ),
    path(
        "dashboard/",
        include(
            [
                path("", DashboardView.as_view(), name="dashboard.index"),
                path("profile/", ProfileView.as_view(), name="dashboard.profile"),
                path("orders/", OrderListView.as_view(), name="dashboard.orders"),
                path("wishlist/", WishlistView.as_view(), name="dashboard.wishlist"),
                path(
                    "addresses/", AddressListView.as_view(), name="dashboard.addresses"
                ),
                path("change-password/", ChangePasswordView.as_view(), name="dashboard.change_password"),
            ]
        ),
    ),
    path("admin/", include("users.admin_urls")),
]
