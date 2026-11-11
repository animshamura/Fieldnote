from functools import wraps

from django.conf import settings
from django.shortcuts import get_object_or_404, redirect

from app.models.client_account import ClientAccount
from app.models.customer import Customer
from app.models.tenant import Tenant
from app.models.user import User


def tenant_required(view):
    @wraps(view)
    def wrapped(request, slug, *args, **kwargs):
        tenant = get_object_or_404(Tenant, slug=slug)
        user = User.objects.filter(
            id=request.session.get("user_id"),
            tenant_id=tenant.id,
        ).first()
        if user is None:
            request.session.flush()
            return redirect("login", slug=slug)
        request.tenant = tenant
        request.staff_user = user
        return view(request, slug, *args, **kwargs)

    return wrapped


def client_required(view):
    @wraps(view)
    def wrapped(request, slug, *args, **kwargs):
        tenant = get_object_or_404(Tenant, slug=slug)
        account = ClientAccount.objects.filter(
            id=request.session.get("client_account_id"),
            tenant_id=tenant.id,
            is_active=True,
        ).first()
        if account is None:
            request.session.pop("client_account_id", None)
            return redirect("client_login", slug=slug)
        request.tenant = tenant
        request.client_account = account
        request.client = get_object_or_404(
            Customer,
            id=account.customer_id,
            tenant_id=tenant.id,
        )
        return view(request, slug, *args, **kwargs)

    return wrapped


def platform_admin_required(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        configured_username = settings.PLATFORM_ADMIN_USERNAME
        configured_password = settings.PLATFORM_ADMIN_PASSWORD
        if not configured_username or not configured_password:
            return redirect("platform_login")
        if request.session.get("platform_admin_username") != configured_username:
            return redirect("platform_login")
        return view(request, *args, **kwargs)

    return wrapped
