from django.urls import path

from app.routes import auth, client_portal, dashboard, management, platform_admin

urlpatterns = [
    path("", auth.index, name="index"),
    path("register", auth.register, name="register"),
    path("workspace", auth.open_workspace, name="open_workspace"),
    path("t/<slug:slug>/login", auth.login, name="login"),
    path("t/<slug:slug>/logout", auth.logout, name="logout"),
    path("t/<slug:slug>/", dashboard.dashboard, name="dashboard"),
    path("t/<slug:slug>/customers/<int:customer_id>/invite", client_portal.create_invite, name="create_invite"),
    path("t/<slug:slug>/portal/accept/<str:token>", client_portal.accept_invite, name="accept_invite"),
    path("t/<slug:slug>/store/", client_portal.store, name="client_store"),
    path("customer-login", client_portal.portal_entry, name="client_portal_entry"),
    path("t/<slug:slug>/portal/signup", client_portal.signup, name="client_signup"),
    path("t/<slug:slug>/portal/google", client_portal.google_login, name="client_google_login"),
    path("t/<slug:slug>/portal/chat", client_portal.product_chat, name="client_product_chat"),
    path("t/<slug:slug>/portal/checkout", client_portal.checkout, name="client_checkout"),
    path("t/<slug:slug>/portal/login", client_portal.login, name="client_login"),
    path("t/<slug:slug>/portal/", client_portal.home, name="client_home"),
    path("t/<slug:slug>/portal/logout", client_portal.logout, name="client_logout"),
    path("t/<slug:slug>/<str:resource_key>/<int:record_id>/edit", management.edit_record, name="edit_record"),
    path("t/<slug:slug>/<str:resource_key>/<int:record_id>/delete", management.delete_record, name="delete_record"),
    path("t/<slug:slug>/<str:resource_key>", management.resource_page, name="resource_page"),
    path("platform-admin/", platform_admin.dashboard, name="platform_dashboard"),
    path("platform-admin/login", platform_admin.login, name="platform_login"),
    path("platform-admin/logout", platform_admin.logout, name="platform_logout"),
    path("platform-admin/workspaces/<int:tenant_id>", platform_admin.workspace_detail, name="platform_workspace"),
    path("platform-admin/workspaces/<int:tenant_id>/settings", platform_admin.update_workspace, name="update_workspace"),
    path("platform-admin/workspaces/<int:tenant_id>/delete", platform_admin.delete_workspace, name="delete_workspace"),
]
