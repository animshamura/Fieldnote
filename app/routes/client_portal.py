import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.db import IntegrityError, transaction
from django.middleware.csrf import rotate_token
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST
from werkzeug.security import check_password_hash

from app.decorators import client_required, tenant_required
from app.frontend import render_react, serialize
from app.models.client_account import ClientAccount
from app.models.client_invite import ClientInvite
from app.models.customer import Customer
from app.models.invoice import Invoice
from app.models.order import Order
from app.models.tenant import Tenant
from app.models.ticket import SupportTicket


INVITE_LIFETIME = timedelta(hours=72)


def token_digest(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def find_valid_invite(slug, token):
    tenant = get_object_or_404(Tenant, slug=slug)
    invite = ClientInvite.objects.filter(
        tenant=tenant,
        token_hash=token_digest(token),
        used_at__isnull=True,
    ).first()
    if (
        invite is None
        or invite.expires_at <= utc_now()
        or ClientAccount.objects.filter(tenant=tenant, customer_id=invite.customer_id).exists()
    ):
        return tenant, None
    return tenant, invite


@tenant_required
@require_POST
def create_invite(request, slug, customer_id):
    customer = get_object_or_404(Customer, id=customer_id, tenant=request.tenant)
    email = (customer.email or "").strip().lower()
    if not email:
        messages.error(request, "Add an email address to this customer before creating a portal invite.")
        return redirect("resource_page", slug=slug, resource_key="customers")
    if ClientAccount.objects.filter(tenant=request.tenant, customer=customer).exists():
        messages.error(request, "This customer already has a portal account.")
        return redirect("resource_page", slug=slug, resource_key="customers")

    token = secrets.token_urlsafe(32)
    invite = ClientInvite(
        tenant=request.tenant,
        customer=customer,
        email=email,
        token_hash=token_digest(token),
        expires_at=utc_now() + INVITE_LIFETIME,
    )
    try:
        with transaction.atomic():
            ClientInvite.objects.filter(
                tenant=request.tenant, customer=customer, used_at__isnull=True
            ).delete()
            invite.save()
    except IntegrityError:
        messages.error(request, "Could not create an invite. Please try again.")
        return redirect("resource_page", slug=slug, resource_key="customers")

    invite_url = request.build_absolute_uri(
        reverse("accept_invite", kwargs={"slug": slug, "token": token})
    )
    return render_react(
        request,
        "invite_created",
        {
            "tenant": serialize(request.tenant),
            "user": serialize(request.staff_user),
            "customer": serialize(customer),
            "invite_url": invite_url,
            "expires_at": serialize(invite.expires_at),
            "title": "Invite ready to share",
        },
    )


@require_http_methods(["GET", "POST"])
def accept_invite(request, slug, token):
    tenant, invite = find_valid_invite(slug, token)
    if invite is None:
        return render_react(
            request, "invite_invalid",
            {"tenant": serialize(tenant), "title": "Invite unavailable"},
            status=404, body_class="login-page",
        )
    if request.method == "POST":
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")
        if len(password) < 8:
            messages.error(request, "Use a password with at least 8 characters.")
        elif password != confirm_password:
            messages.error(request, "The passwords do not match.")
        else:
            try:
                with transaction.atomic():
                    account = ClientAccount.objects.create(
                        tenant_id=invite.tenant_id,
                        customer_id=invite.customer_id,
                        email=invite.email,
                        password_hash=make_password(password),
                    )
                    invite.used_at = utc_now()
                    invite.save(update_fields=["used_at"])
            except IntegrityError:
                return render_react(
                    request, "invite_invalid",
                    {"tenant": serialize(tenant), "title": "Invite unavailable"},
                    status=409, body_class="login-page",
                )
            request.session.flush()
            rotate_token(request)
            request.session["client_account_id"] = account.id
            return redirect("client_home", slug=slug)

    return render_react(
        request,
        "invite_accept",
        {
            "tenant": serialize(tenant),
            "invite": serialize(invite),
            "title": f"Set up your portal · {tenant.name}",
        },
        body_class="login-page",
    )


@require_http_methods(["GET", "POST"])
def login(request, slug):
    tenant = get_object_or_404(Tenant, slug=slug)
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        account = ClientAccount.objects.filter(
            tenant=tenant, email=email, is_active=True
        ).first()
        if account and (
            check_password(password, account.password_hash)
            or check_password_hash(account.password_hash, password)
        ):
            if not account.password_hash.startswith("pbkdf2_sha256$"):
                account.password_hash = make_password(password)
                account.save(update_fields=["password_hash"])
            request.session.flush()
            rotate_token(request)
            request.session["client_account_id"] = account.id
            return redirect("client_home", slug=slug)
        messages.error(request, "Email or password is incorrect.")
    return render_react(
        request,
        "client_login",
        {"tenant": serialize(tenant), "title": f"Customer sign in · {tenant.name}"},
        body_class="login-page",
    )


@client_required
def home(request, slug):
    customer_filter = {"tenant": request.tenant, "customer_id": request.client.id}
    orders = Order.objects.filter(**customer_filter).order_by("-id")
    invoices = Invoice.objects.filter(**customer_filter).order_by("-id")
    tickets = SupportTicket.objects.filter(**customer_filter).order_by("-id")
    return render_react(
        request,
        "client_portal",
        {
            "tenant": serialize(request.tenant),
            "account": serialize(request.client_account),
            "customer": serialize(request.client),
            "orders": serialize(list(orders)),
            "invoices": serialize(list(invoices)),
            "tickets": serialize(list(tickets)),
            "title": f"Customer portal · {request.tenant.name}",
        },
    )


@require_POST
def logout(request, slug):
    request.session.pop("client_account_id", None)
    messages.success(request, "You have been signed out.")
    return redirect("client_login", slug=slug)
