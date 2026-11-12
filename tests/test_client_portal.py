import json
import re
import unittest
from datetime import date, datetime, timedelta, timezone
from urllib.parse import urlparse
from unittest.mock import patch

from django.test import Client, TestCase, override_settings
from app.routes.client_portal import verified_google_identity

from app.models.client_account import ClientAccount
from app.models.customer import Customer
from app.models.invoice import Invoice
from app.models.order import Order
from app.models.product import Product
from app.models.tenant import Tenant
from app.models.user import User
from werkzeug.security import generate_password_hash


@override_settings(
    PLATFORM_ADMIN_USERNAME="platform-owner",
    PLATFORM_ADMIN_PASSWORD="platform-secret-for-tests",
)
class ClientPortalFlowTest(TestCase):
    def setUp(self):
        self.staff = Client()

    def create_workspace(self, company="Test Company"):
        response = self.staff.post(
            "/register",
            data={
                "company": company,
                "username": "owner",
                "email": "owner@example.test",
                "password": "password123",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        tenant = Tenant.objects.get(slug=company.lower().replace(" ", "-"))
        response = self.staff.post(
            f"/t/{tenant.slug}/login",
            data={"username": "owner", "password": "password123"},
            follow=True,
        )
        self.assertIn(b'"page": "dashboard"', response.content)
        return tenant

    @staticmethod
    def bootstrap(response):
        match = re.search(
            rb'<script id="fieldnote-bootstrap" type="application/json">([^<]+)</script>',
            response.content,
        )
        if not match:
            raise AssertionError("React bootstrap payload was not rendered")
        return json.loads(match.group(1))

    def test_registration_requires_django_csrf_token(self):
        browser = Client(enforce_csrf_checks=True)
        response = browser.get("/")
        token = self.bootstrap(response)["csrfToken"]
        response = browser.post(
            "/register",
            data={
                "company": "CSRF Workspace",
                "username": "owner",
                "email": "owner@example.test",
                "password": "password123",
                "csrfmiddlewaretoken": token,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Tenant.objects.filter(slug="csrf-workspace").exists())

    def test_existing_werkzeug_staff_password_is_upgraded_on_login(self):
        tenant = Tenant.objects.create(name="Legacy Workspace", slug="legacy-workspace")
        user = User.objects.create(
            tenant=tenant,
            username="legacy-owner",
            email="legacy@example.test",
            password_hash=generate_password_hash("legacy-password"),
            role="admin",
        )
        response = self.staff.post(
            f"/t/{tenant.slug}/login",
            data={"username": user.username, "password": "legacy-password"},
            follow=True,
        )
        self.assertIn(b'"page": "dashboard"', response.content)
        user.refresh_from_db()
        self.assertTrue(user.password_hash.startswith("pbkdf2_sha256$"))

    def test_customer_invite_and_private_portal_records(self):
        tenant = self.create_workspace()
        self.staff.post(
            f"/t/{tenant.slug}/customers",
            data={
                "name": "Taylor Customer",
                "email": "taylor@example.test",
                "company": "Taylor Co",
                "phone": "",
                "address": "",
            },
        )
        customer = Customer.objects.get(tenant=tenant, email="taylor@example.test")
        other = Customer.objects.create(tenant=tenant, name="Another Customer")
        Order.objects.create(
            tenant=tenant, customer=customer, order_number="OWN-100",
            status="Processing", total_amount=125.0,
        )
        Order.objects.create(
            tenant=tenant, customer=other, order_number="PRIVATE-999",
            status="Pending", total_amount=999.0,
        )

        response = self.staff.post(f"/t/{tenant.slug}/customers/{customer.id}/invite")
        self.assertEqual(response.status_code, 200)
        invite_props = self.bootstrap(response)["props"]
        self.assertEqual(invite_props["title"], "Invite ready to share")
        invite_url = invite_props["invite_url"]
        accept_path = urlparse(invite_url).path

        customer_browser = Client()
        response = customer_browser.post(
            accept_path,
            data={"password": "clientpass123", "confirm_password": "clientpass123"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"OWN-100", response.content)
        self.assertNotIn(b"PRIVATE-999", response.content)
        self.assertIn(b"taylor@example.test", response.content)
        self.assertEqual(customer_browser.get(accept_path).status_code, 404)

        customer_browser.post(f"/t/{tenant.slug}/portal/logout")
        response = customer_browser.post(
            f"/t/{tenant.slug}/portal/login",
            data={"email": "taylor@example.test", "password": "clientpass123"},
            follow=True,
        )
        self.assertIn(b"OWN-100", response.content)
        self.assertNotIn(b"PRIVATE-999", response.content)

    def test_public_storefront_signup_and_checkout_decrements_stock(self):
        tenant = Tenant.objects.create(name="Market Shop", slug="market-shop")
        product = Product.objects.create(
            tenant=tenant,
            name="Field Bag",
            sku="BAG-1",
            price=24.5,
            stock=3,
            description="A useful everyday bag.",
        )
        response = self.staff.get(f"/t/{tenant.slug}/store/")
        store_props = self.bootstrap(response)
        self.assertEqual(store_props["page"], "store")
        self.assertEqual(store_props["props"]["products"][0]["name"], "Field Bag")

        customer_browser = Client()
        response = customer_browser.post(
            f"/t/{tenant.slug}/portal/signup",
            data={
                "name": "Morgan Customer",
                "email": "morgan@example.test",
                "password": "customer-password",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"page": "store"', response.content)

        response = customer_browser.post(
            f"/t/{tenant.slug}/portal/checkout",
            data={"cart": json.dumps([{"id": product.id, "quantity": 2}])},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"page": "client_portal"', response.content)
        order = Order.objects.get(tenant=tenant)
        self.assertEqual(order.customer.email, "morgan@example.test")
        self.assertEqual(order.status, "Pending")
        self.assertEqual(order.total_amount, 49.0)
        self.assertEqual(order.items.get().quantity, 2)
        product.refresh_from_db()
        self.assertEqual(product.stock, 1)

    def test_storefront_checkout_cannot_order_another_workspaces_product(self):
        tenant = Tenant.objects.create(name="Market Shop", slug="market-shop")
        other_tenant = Tenant.objects.create(name="Other Shop", slug="other-shop")
        customer = Customer.objects.create(
            tenant=tenant, name="Morgan Customer", email="morgan@example.test"
        )
        product = Product.objects.create(
            tenant=other_tenant, name="Private item", sku="PRIVATE", price=10, stock=5
        )
        account = ClientAccount.objects.create(
            tenant=tenant,
            customer=customer,
            email=customer.email,
            password_hash="test-hash",
        )
        customer_browser = Client()
        session = customer_browser.session
        session["client_account_id"] = account.id
        session.save()

        response = customer_browser.post(
            f"/t/{tenant.slug}/portal/checkout",
            data={"cart": json.dumps([{"id": product.id, "quantity": 1}])},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Order.objects.filter(tenant=tenant).exists())
        product.refresh_from_db()
        self.assertEqual(product.stock, 5)
        self.assertContains(response, "no longer available")

    @override_settings(GOOGLE_CLIENT_ID="test-google-client")
    def test_google_sign_in_creates_a_customer_account(self):
        tenant = Tenant.objects.create(name="Market Shop", slug="market-shop")
        customer_browser = Client()
        signup_response = customer_browser.get(f"/t/{tenant.slug}/portal/signup")
        nonce = self.bootstrap(signup_response)["props"]["google_nonce"]
        with patch(
            "app.routes.client_portal.verified_google_identity",
            return_value={
                "email": "google@example.test",
                "name": "Google Customer",
                "nonce": nonce,
            },
        ):
            response = customer_browser.post(
                f"/t/{tenant.slug}/portal/google",
                data={"credential": "verified-test-credential"},
            )

        self.assertRedirects(
            response, f"/t/{tenant.slug}/store/", fetch_redirect_response=False
        )
        account = ClientAccount.objects.get(tenant=tenant, email="google@example.test")
        self.assertEqual(account.customer.name, "Google Customer")
        self.assertEqual(customer_browser.session.get("client_account_id"), account.id)

    @override_settings(GOOGLE_CLIENT_ID="test-google-client")
    def test_google_identity_verification_checks_audience_and_verified_email(self):
        claims = {
            "aud": "test-google-client",
            "iss": "https://accounts.google.com",
            "email_verified": True,
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=5)).timestamp()),
            "email": "google@example.test",
        }
        with patch("app.routes.client_portal.urlopen") as token_info:
            response = token_info.return_value.__enter__.return_value
            response.read.return_value = json.dumps(claims).encode("utf-8")
            self.assertEqual(
                verified_google_identity("verified-token")["email"],
                "google@example.test",
            )
            claims["aud"] = "untrusted-client"
            response.read.return_value = json.dumps(claims).encode("utf-8")
            with self.assertRaises(ValueError):
                verified_google_identity("wrong-audience-token")

    def test_platform_admin_requires_confirmation_and_deletes_workspace_data(self):
        tenant = self.create_workspace("Delete Me")
        customer = Customer.objects.create(
            tenant=tenant, name="Customer", email="customer@example.test"
        )
        Product.objects.create(
            tenant=tenant, name="Item", sku="ITEM-1", price=10, stock=2
        )
        Order.objects.create(
            tenant=tenant, customer=customer, order_number="ORD-1",
            status="Pending", total_amount=10,
        )
        Invoice.objects.create(
            tenant=tenant, customer=customer, invoice_number="INV-1",
            status="Draft", subtotal=10, tax=1, total=11,
            issue_date=date.today(), due_date=date.today() + timedelta(days=30),
        )
        ClientAccount.objects.create(
            tenant=tenant,
            customer=customer,
            email="customer@example.test",
            password_hash="test-hash",
        )

        admin = Client()
        response = admin.post(
            "/platform-admin/login",
            data={"username": "platform-owner", "password": "platform-secret-for-tests"},
            follow=True,
        )
        self.assertIn(b'"page": "platform_dashboard"', response.content)
        response = admin.get(f"/platform-admin/workspaces/{tenant.id}")
        self.assertIn(b'"page": "platform_workspace"', response.content)

        response = admin.post(
            f"/platform-admin/workspaces/{tenant.id}/delete",
            data={"confirmation": tenant.slug, "admin_password": "wrong-password"},
            follow=True,
        )
        self.assertIn(b"Nothing was deleted", response.content)
        self.assertTrue(Tenant.objects.filter(id=tenant.id).exists())

        response = admin.post(
            f"/platform-admin/workspaces/{tenant.id}/delete",
            data={"confirmation": tenant.slug, "admin_password": "platform-secret-for-tests"},
            follow=True,
        )
        self.assertIn(b"permanently deleted", response.content)
        self.assertFalse(Tenant.objects.filter(id=tenant.id).exists())


if __name__ == "__main__":
    unittest.main()
