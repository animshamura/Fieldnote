from datetime import datetime

from django.contrib import messages
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_http_methods, require_POST

from app.decorators import tenant_required
from app.frontend import render_react, serialize
from app.models.activity_log import ActivityLog
from app.models.client_account import ClientAccount
from app.models.client_invite import ClientInvite
from app.models.customer import Customer
from app.models.department import Department
from app.models.employee import Employee
from app.models.invoice import Invoice
from app.models.order import Order
from app.models.product import Product
from app.models.subscription import Subscription
from app.models.ticket import SupportTicket


def field(name, label, kind="text", required=False, choices=None):
    return {
        "name": name,
        "label": label,
        "type": kind,
        "required": required,
        "choices": choices or (),
    }


RESOURCES = {
    "customers": {
        "label": "Customers", "singular": "customer", "model": Customer,
        "fields": [
            field("name", "Name", required=True), field("company", "Company"),
            field("email", "Email", "email"), field("phone", "Phone", "tel"),
            field("address", "Address"),
        ],
    },
    "products": {
        "label": "Products", "singular": "product", "model": Product,
        "fields": [
            field("name", "Name", required=True), field("sku", "SKU", required=True),
            field("price", "Unit price", "number", True), field("stock", "In stock", "integer", True),
            field("description", "Description", "textarea"),
        ],
    },
    "orders": {
        "label": "Orders", "singular": "order", "model": Order,
        "fields": [
            field("order_number", "Order number", required=True),
            field("customer_id", "Customer", "customer", True),
            field("status", "Status", "select", True, ("Pending", "Processing", "Completed", "Cancelled")),
            field("total_amount", "Order total", "number", True),
        ],
    },
    "invoices": {
        "label": "Invoices", "singular": "invoice", "model": Invoice,
        "fields": [
            field("invoice_number", "Invoice number", required=True),
            field("customer_id", "Customer", "customer", True),
            field("status", "Status", "select", True, ("Draft", "Sent", "Paid", "Overdue")),
            field("subtotal", "Subtotal", "number", True), field("tax", "Tax", "number", True),
            field("total", "Total", "number", True), field("issue_date", "Issue date", "date", True),
            field("due_date", "Due date", "date", True),
        ],
    },
    "tickets": {
        "label": "Support", "singular": "ticket", "model": SupportTicket,
        "fields": [
            field("customer_id", "Customer", "customer", True), field("subject", "Subject", required=True),
            field("priority", "Priority", "select", True, ("Low", "Medium", "High", "Urgent")),
            field("status", "Status", "select", True, ("Open", "In progress", "Resolved", "Closed")),
            field("message", "Message", "textarea", True),
        ],
    },
    "subscriptions": {
        "label": "Subscriptions", "singular": "subscription", "model": Subscription,
        "fields": [
            field("name", "Plan name", required=True), field("price", "Price", "number", True),
            field("billing_cycle", "Billing cycle", "select", True, ("Monthly", "Quarterly", "Yearly")),
            field("status", "Status", "select", True, ("Active", "Paused", "Cancelled")),
        ],
    },
    "employees": {
        "label": "Team", "singular": "team member", "model": Employee,
        "fields": [
            field("name", "Name", required=True), field("email", "Email", "email"),
            field("phone", "Phone", "tel"), field("position", "Position"),
            field("department_id", "Department", "department"), field("salary", "Salary", "number", True),
        ],
    },
    "departments": {
        "label": "Departments", "singular": "department", "model": Department,
        "fields": [field("name", "Department name", required=True), field("description", "Description", "textarea")],
    },
}


def related_options(field_spec, tenant):
    if field_spec["type"] == "customer":
        return list(Customer.objects.filter(tenant=tenant).order_by("name"))
    if field_spec["type"] == "department":
        return list(Department.objects.filter(tenant=tenant).order_by("name"))
    return []


def record_value(record, field_spec):
    value = getattr(record, field_spec["name"], None)
    if field_spec["type"] == "customer":
        return record.customer.name if record.customer_id else ""
    if field_spec["type"] == "department":
        return record.department.name if record.department_id else ""
    if field_spec["type"] == "date" and value:
        return value.strftime("%b %d, %Y")
    if field_spec["type"] == "number" and value is not None:
        return f"{value:,.2f}"
    return "—" if value is None or value == "" else value


def render_resource(request, slug, key, config, record=None, values=None, errors=None, status=200):
    tenant = request.tenant
    fields = config["fields"]
    related_fields = [
        {"customer_id": "customer", "department_id": "department"}.get(item["name"])
        for item in fields
    ]
    select_related = [name for name in related_fields if name]
    query = config["model"].objects.filter(tenant=tenant)
    if select_related:
        query = query.select_related(*select_related)
    records = list(query.order_by("-id"))
    form_fields = []
    for spec in fields:
        item = dict(spec)
        item["value"] = (values or {}).get(
            spec["name"],
            getattr(record, spec["name"], "") if record else "",
        )
        item["options"] = related_options(spec, tenant)
        form_fields.append(item)
    columns = [
        {"label": spec["label"], "name": spec["name"]}
        for spec in fields
        if spec["name"] not in ("message", "description", "address")
    ]
    client_accounts = {}
    if key == "customers":
        client_accounts = {
            account.customer_id: account
            for account in ClientAccount.objects.filter(tenant=tenant)
        }
    fields_by_name = {item["name"]: item for item in fields}
    return render_react(
        request,
        "resource",
        {
            "tenant": serialize(tenant),
            "user": serialize(request.staff_user),
            "resource_key": key,
            "resource": {"label": config["label"], "singular": config["singular"]},
            "records": [
                {
                    "id": item.id,
                    "display": {
                        column["name"]: record_value(item, fields_by_name[column["name"]])
                        for column in columns
                    },
                }
                for item in records
            ],
            "fields": form_fields,
            "columns": columns,
            "record": {"id": record.id} if record else None,
            "errors": errors or [],
            "client_account_ids": list(client_accounts),
            "title": f"{config['label']} · {tenant.name}",
        },
        status=status,
    )


def parse_values(request, config):
    values = {spec["name"]: request.POST.get(spec["name"], "").strip() for spec in config["fields"]}
    errors = []
    parsed = {}
    tenant = request.tenant
    for spec in config["fields"]:
        name, kind, value = spec["name"], spec["type"], values[spec["name"]]
        if spec["required"] and not value:
            errors.append(f"{spec['label']} is required.")
            continue
        if not value:
            parsed[name] = None if kind in ("customer", "department", "date") else ""
            continue
        try:
            if kind == "number":
                parsed[name] = float(value)
                if parsed[name] < 0:
                    raise ValueError
            elif kind == "integer":
                parsed[name] = int(value)
                if parsed[name] < 0:
                    raise ValueError
            elif kind == "date":
                parsed[name] = datetime.strptime(value, "%Y-%m-%d").date()
            elif kind == "select":
                if value not in spec["choices"]:
                    raise ValueError
                parsed[name] = value
            elif kind == "customer":
                related = Customer.objects.filter(id=int(value), tenant=tenant).first()
                if related is None:
                    raise ValueError
                parsed[name] = related.id
            elif kind == "department":
                related = Department.objects.filter(id=int(value), tenant=tenant).first()
                if related is None:
                    raise ValueError
                parsed[name] = related.id
            else:
                parsed[name] = value
        except (TypeError, ValueError):
            errors.append(f"Enter a valid {spec['label'].lower()}.")
    return values, parsed, errors


@tenant_required
@require_http_methods(["GET", "POST"])
def resource_page(request, slug, resource_key):
    config = RESOURCES.get(resource_key)
    if config is None:
        return HttpResponse("Not found", status=404)
    if request.method == "POST":
        values, parsed, errors = parse_values(request, config)
        if errors:
            return render_resource(request, slug, resource_key, config, values=values, errors=errors, status=400)
        try:
            with transaction.atomic():
                entity = config["model"](tenant=request.tenant, **parsed)
                entity.save()
                ActivityLog.objects.create(
                    tenant=request.tenant,
                    action=f"Added {config['singular']}",
                    details=(
                        values.get("name") or values.get("subject") or values.get("order_number")
                        or values.get("invoice_number") or values.get("plan_name") or "New record"
                    ),
                )
        except IntegrityError:
            return render_resource(
                request, slug, resource_key, config, values=values,
                errors=["That value is already in use."], status=400,
            )
        messages.success(request, f"{config['singular'].capitalize()} added.")
        return redirect("resource_page", slug=slug, resource_key=resource_key)
    return render_resource(request, slug, resource_key, config)


@tenant_required
@require_http_methods(["GET", "POST"])
def edit_record(request, slug, resource_key, record_id):
    config = RESOURCES.get(resource_key)
    if config is None:
        return HttpResponse("Not found", status=404)
    record = get_object_or_404(config["model"], id=record_id, tenant=request.tenant)
    if request.method == "GET":
        return render_resource(request, slug, resource_key, config, record=record)

    values, parsed, errors = parse_values(request, config)
    if errors:
        return render_resource(
            request, slug, resource_key, config, record=record, values=values, errors=errors, status=400,
        )
    try:
        with transaction.atomic():
            for name, value in parsed.items():
                setattr(record, name, value)
            record.save()
            ActivityLog.objects.create(
                tenant=request.tenant,
                action=f"Updated {config['singular']}",
                details=str(record.id),
            )
    except IntegrityError:
        return render_resource(
            request, slug, resource_key, config, record=record, values=values,
            errors=["That value is already in use."], status=400,
        )
    messages.success(request, f"{config['singular'].capitalize()} updated.")
    return redirect("resource_page", slug=slug, resource_key=resource_key)


@tenant_required
@require_POST
def delete_record(request, slug, resource_key, record_id):
    config = RESOURCES.get(resource_key)
    if config is None:
        return HttpResponse("Not found", status=404)
    record = get_object_or_404(config["model"], id=record_id, tenant=request.tenant)
    try:
        with transaction.atomic():
            if resource_key == "customers":
                ClientInvite.objects.filter(tenant=request.tenant, customer=record).delete()
                ClientAccount.objects.filter(tenant=request.tenant, customer=record).delete()
            ActivityLog.objects.create(
                tenant=request.tenant,
                action=f"Deleted {config['singular']}",
                details=str(record.id),
            )
            record.delete()
    except (IntegrityError, ProtectedError):
        messages.error(request, "This record is linked to other data and cannot be deleted.")
    else:
        messages.success(request, f"{config['singular'].capitalize()} deleted.")
    return redirect("resource_page", slug=slug, resource_key=resource_key)
