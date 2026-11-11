from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.db import IntegrityError, transaction
from django.middleware.csrf import rotate_token
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_http_methods, require_POST
from werkzeug.security import check_password_hash

from app.frontend import render_react, serialize
from app.models.tenant import Tenant
from app.models.user import User
from app.utilis import slugify


def index(request):
    return render_react(
        request,
        "index",
        {"title": "Fieldnote · Keep your business details connected"},
        body_class="auth-page",
    )


@require_POST
def register(request):
    company_name = request.POST.get("company", "").strip()
    username = request.POST.get("username", "").strip()
    email = request.POST.get("email", "").strip().lower()
    password = request.POST.get("password", "")
    industry = request.POST.get("industry", "").strip()

    if not company_name or not username or not email or len(password) < 8:
        messages.error(request, "Fill all fields correctly and use at least 8-character password.")
        return redirect("index")

    slug = slugify(company_name)
    if not slug:
        messages.error(request, "Invalid company name.")
        return redirect("index")
    if Tenant.objects.filter(slug=slug).exists():
        messages.error(request, "This company already exists.")
        return redirect("index")

    try:
        with transaction.atomic():
            tenant = Tenant.objects.create(name=company_name, slug=slug, industry=industry or None)
            User.objects.create(
                tenant=tenant,
                username=username,
                email=email,
                password_hash=make_password(password),
                role="admin",
            )
    except IntegrityError:
        messages.error(request, "A workspace with those details already exists.")
        return redirect("index")

    messages.success(request, "Company created successfully.")
    return redirect("login", slug=slug)


@require_POST
def open_workspace(request):
    workspace_name = request.POST.get("slug", "").strip()
    slug = slugify(workspace_name)
    tenant = Tenant.objects.filter(slug=slug).first()
    if tenant is None and workspace_name:
        tenant = Tenant.objects.filter(name__iexact=workspace_name).first()
    if tenant is None:
        messages.error(request, "We could not find that workspace.")
        return redirect("index")
    return redirect("login", slug=tenant.slug)


@require_http_methods(["GET", "POST"])
def login(request, slug):
    tenant = get_object_or_404(Tenant, slug=slug)
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = User.objects.filter(tenant=tenant, username=username).first()
        if user and (
            check_password(password, user.password_hash)
            or check_password_hash(user.password_hash, password)
        ):
            if not user.password_hash.startswith("pbkdf2_sha256$"):
                user.password_hash = make_password(password)
                user.save(update_fields=["password_hash"])
            request.session.flush()
            rotate_token(request)
            request.session["user_id"] = user.id
            return redirect("dashboard", slug=slug)
        messages.error(request, "Invalid username or password.")

    return render_react(
        request,
        "login",
        {"tenant": serialize(tenant), "title": f"Sign in · {tenant.name}"},
        body_class="login-page",
    )


@require_POST
def logout(request, slug):
    request.session.flush()
    messages.success(request, "You have been signed out.")
    return redirect("login", slug=slug)
