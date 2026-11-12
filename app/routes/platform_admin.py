import hmac
import logging

from django.conf import settings
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.db.models import Count, Q
from django.middleware.csrf import rotate_token
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_http_methods, require_POST
from werkzeug.security import check_password_hash

from app.decorators import platform_admin_required
from app.frontend import render_react, serialize
from app.models.activity_log import ActivityLog
from app.models.client_account import ClientAccount
from app.models.client_invite import ClientInvite
from app.models.customer import Customer
from app.models.department import Department
from app.models.employee import Employee
from app.models.invoice import Invoice, InvoiceItem
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.subscription import Subscription
from app.models.tenant import Tenant
from app.models.ticket import SupportTicket
from app.models.user import User


WORKSPACE_MODELS = {
    "Staff accounts": User,
    "Customer accounts": ClientAccount,
    "Customers": Customer,
    "Products": Product,
    "Orders": Order,
    "Order items": OrderItem,
    "Invoices": Invoice,
    "Invoice items": InvoiceItem,
    "Support tickets": SupportTicket,
    "Subscriptions": Subscription,
    "Employees": Employee,
    "Departments": Department,
    "Activity entries": ActivityLog,
    "Pending invites": ClientInvite,
}

logger = logging.getLogger(__name__)


def workspace_counts(tenant):
    return {
        label: model.objects.filter(tenant=tenant).count()
        for label, model in WORKSPACE_MODELS.items()
    }


def password_matches(submitted):
    expected = settings.PLATFORM_ADMIN_PASSWORD
    return bool(expected) and hmac.compare_digest(
        submitted.encode("utf-8"), expected.encode("utf-8")
    )


@platform_admin_required
def dashboard(request):
    search = request.GET.get("q", "").strip()
    query = Tenant.objects.all()
    if search:
        query = query.filter(Q(name__icontains=search) | Q(slug__icontains=search))
    tenants = list(query.order_by("-created_at", "-id"))

    def counts(model):
        return {
            row["tenant_id"]: row["total"]
            for row in model.objects.values("tenant_id").annotate(total=Count("id"))
        }

    return render_react(
        request,
        "platform_dashboard",
        {
            "tenants": serialize(tenants),
            "search": search,
            "user_counts": counts(User),
            "customer_counts": counts(Customer),
            "order_counts": counts(Order),
            "title": "Platform workspaces",
        },
    )


@require_http_methods(["GET", "POST"])
def login(request):
    configured = bool(settings.PLATFORM_ADMIN_USERNAME and settings.PLATFORM_ADMIN_PASSWORD)
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        if (
            configured
            and hmac.compare_digest(
                username.encode("utf-8"), settings.PLATFORM_ADMIN_USERNAME.encode("utf-8")
            )
            and password_matches(password)
        ):
            request.session.flush()
            rotate_token(request)
            request.session["platform_admin_username"] = settings.PLATFORM_ADMIN_USERNAME
            return redirect("platform_dashboard")
        messages.error(
            request,
            "Platform admin access is not configured."
            if not configured else "Username or password is incorrect.",
        )
    return render_react(
        request,
        "platform_login",
        {"configured": configured, "title": "Platform admin"},
        body_class="login-page",
    )


@require_POST
def logout(request):
    request.session.flush()
    return redirect("platform_login")


@platform_admin_required
def workspace_detail(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)
    users = list(User.objects.filter(tenant=tenant).order_by("id"))
    return render_react(
        request,
        "platform_workspace",
        {
            "tenant": serialize(tenant),
            "users": serialize(users),
            "counts": workspace_counts(tenant),
            "title": f"{tenant.name} · Platform admin",
        },
    )


@platform_admin_required
@require_POST
def approve_workspace(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)
    if tenant.is_approved:
        messages.info(request, "This workspace is already approved.")
    else:
        tenant.is_approved = True
        tenant.save(update_fields=["is_approved"])
        messages.success(request, f"{tenant.name} is approved and ready to use.")
    return redirect("platform_workspace", tenant_id=tenant.id)


@platform_admin_required
@require_POST
def update_workspace(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)
    name = request.POST.get("name", "").strip()
    if not name:
        messages.error(request, "Workspace name is required.")
        return redirect("platform_workspace", tenant_id=tenant.id)
    tenant.name = name[:150]
    tenant.industry = request.POST.get("industry", "").strip()[:80] or None
    tenant.address = request.POST.get("address", "").strip()[:255] or None
    try:
        tenant.save(update_fields=["name", "industry", "address"])
    except IntegrityError:
        messages.error(request, "Workspace details could not be saved.")
    else:
        messages.success(request, "Workspace details updated.")
    return redirect("platform_workspace", tenant_id=tenant.id)


@platform_admin_required
@require_POST
def delete_workspace(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)
    if request.POST.get("confirmation", "").strip() != tenant.slug:
        messages.error(request, "Workspace slug did not match. Nothing was deleted.")
        return redirect("platform_workspace", tenant_id=tenant.id)
    if not password_matches(request.POST.get("admin_password", "")):
        messages.error(request, "Platform admin password is incorrect. Nothing was deleted.")
        return redirect("platform_workspace", tenant_id=tenant.id)

    deletion_order = (
        OrderItem,
        InvoiceItem,
        ClientInvite,
        ClientAccount,
        ActivityLog,
        SupportTicket,
        Invoice,
        Order,
        Employee,
        Subscription,
        Department,
        Customer,
        Product,
        User,
    )
    try:
        with transaction.atomic():
            for model in deletion_order:
                model.objects.filter(tenant=tenant).delete()
            tenant.delete()
    except Exception:
        logger.exception("Workspace deletion failed for tenant %s", tenant_id)
        messages.error(request, "Workspace deletion failed. No changes were saved.")
        return redirect("platform_workspace", tenant_id=tenant_id)
    messages.success(request, "Workspace and its associated data were permanently deleted.")
    return redirect("platform_dashboard")
