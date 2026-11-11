from app.decorators import tenant_required
from app.frontend import render_react, serialize
from app.models.activity_log import ActivityLog
from app.models.customer import Customer
from app.models.employee import Employee
from app.models.invoice import Invoice
from app.models.order import Order
from app.models.product import Product
from app.models.subscription import Subscription
from app.models.ticket import SupportTicket


@tenant_required
def dashboard(request, slug):
    tenant = request.tenant
    user = request.staff_user
    customers = list(Customer.objects.filter(tenant=tenant))
    products = list(Product.objects.filter(tenant=tenant))
    employees = list(Employee.objects.filter(tenant=tenant))
    orders = list(Order.objects.filter(tenant=tenant).select_related("customer").order_by("-id"))
    invoices = list(Invoice.objects.filter(tenant=tenant))
    tickets = list(SupportTicket.objects.filter(tenant=tenant))
    subscriptions = list(Subscription.objects.filter(tenant=tenant))
    logs = list(ActivityLog.objects.filter(tenant=tenant).order_by("-id")[:10])

    return render_react(
        request,
        "dashboard",
        {
            "tenant": serialize(tenant),
            "user": serialize(user),
            "welcome": f"Good morning, {user.username}.",
            "customers": serialize(customers),
            "products": serialize(products),
            "employees": serialize(employees),
            "orders": [
                {**serialize(order), "customer_name": order.customer.name if order.customer else None}
                for order in orders
            ],
            "invoices": serialize(invoices),
            "tickets": serialize(tickets),
            "subscriptions": serialize(subscriptions),
            "logs": serialize(logs),
            "revenue": sum(invoice.total for invoice in invoices),
            "total_orders": sum(order.total_amount for order in orders),
            "title": f"Overview · {tenant.name}",
        },
    )
