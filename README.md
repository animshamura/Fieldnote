# Fieldnote

Fieldnote is a multi-tenant business workspace for keeping customer and operational records together. Each company gets its own workspace to manage customers, products, orders, invoices, support tickets, subscriptions, employees, and departments. Customers can get a separate, private portal for viewing their own orders, invoices, and support requests.

The interface is a React app served by Django. The current frontend loads React, React DOM, and HTM as pinned ES modules from `esm.sh`; it does not need a Node.js build step. A browser needs internet access to load those modules and the Google Fonts used by the interface.

## Screenshots

These screenshots use fictional sample data and show the main parts of the app.

### Landing page and workspace registration

Create a company workspace and its first staff account.

![Fieldnote landing page and workspace registration](docs/screenshots/landing.png)

### Staff dashboard

See workspace totals, recent orders, recent activity, and shortcuts to frequently used records.

![Fieldnote staff dashboard](docs/screenshots/dashboard.png)

### Customer records

Add, edit, and remove customer records, and invite customers to their portal.

![Fieldnote customer management](docs/screenshots/customers.png)

### Customer portal

Customers see only the orders, invoices, and support requests associated with their account.

![Fieldnote customer portal](docs/screenshots/customer-portal.png)

### Platform administration

Find workspaces, review their record counts, update workspace details, or permanently remove a workspace.

![Fieldnote platform administration](docs/screenshots/platform-admin.png)

## What Fieldnote does

### Company workspaces

- Register a company with its name, industry (optional), and the first staff username, email, and password.
- Each workspace has a unique URL slug, such as `/t/northwind-studio/`.
- A workspace's customers, orders, invoices, products, support tickets, subscriptions, employees, and departments are scoped to that workspace.
- The first registered staff account is assigned the `admin` role.
- Staff sign in at `/t/<workspace-slug>/login`. The landing page also has a workspace-name lookup to find the sign-in page.

### Dashboard

The staff dashboard provides a quick view of:

- **Revenue:** the sum of invoice totals in the workspace.
- **Customers:** the number of customer records.
- **Open orders:** orders whose status is not `Completed` or `Cancelled`.
- **Support queue:** tickets whose status is not `Resolved` or `Closed`.
- **Recent orders:** up to six orders, with customer, status, and total.
- **Recent activity:** the ten latest logged create, update, and delete actions.
- **Shortcuts:** links to invoices, products, team members, and subscriptions.

The totals are summaries of the records currently stored in Fieldnote. They are not accounting reports or payment processor balances.

### Business records

Staff can create, edit, and delete records from the workspace navigation. Record forms validate required fields and related customer or department selections against the current workspace.

| Section | Information stored | Required fields and choices |
| --- | --- | --- |
| **Customers** | Name, company, email, phone, and address | Name is required. Email is optional unless you want to send a portal invitation. |
| **Products** | Name, SKU, unit price, stock quantity, and description | Name, SKU, price, and stock quantity are required. |
| **Orders** | Order number, customer, status, and total amount | All fields are required. Status: `Pending`, `Processing`, `Completed`, or `Cancelled`. |
| **Invoices** | Invoice number, customer, status, subtotal, tax, total, issue date, and due date | All fields are required. Status: `Draft`, `Sent`, `Paid`, or `Overdue`. |
| **Support** | Customer, subject, priority, status, and message | All fields are required. Priority: `Low`, `Medium`, `High`, or `Urgent`. Status: `Open`, `In progress`, `Resolved`, or `Closed`. |
| **Plans** | Subscription/plan name, price, billing cycle, and status | All fields are required. Billing cycle: `Monthly`, `Quarterly`, or `Yearly`. Status: `Active`, `Paused`, or `Cancelled`. |
| **Team** | Employee name, email, phone, position, department, and salary | Name and salary are required. Department is optional. |
| **Departments** | Department name and description | Department name is required. |

Orders and invoices are currently single records with a total; the interface does not provide line-item editing, invoice PDF generation, or payment collection. Products have a stock field, but Fieldnote does not automatically deduct inventory when an order is added. Subscription entries are records only; there is no recurring billing integration.

When a record is linked to other records, the app may prevent deleting it to avoid leaving broken references. Changes made through the staff record forms are added to the workspace activity feed.

### Customer portal

The customer portal is an optional, separate sign-in for customers:

1. Add a customer and an email address under **Customers**.
2. Select **Invite** for that customer.
3. Copy the generated invitation URL and send it to the customer through your usual secure channel.
4. The customer opens the one-time link and creates a password of at least eight characters.
5. After setup, the customer signs in at `/t/<workspace-slug>/portal/login`.

Invitation links expire after 72 hours, can only be used once, and are stored as token hashes. A new invite replaces an unused invite for the same customer. Fieldnote does **not** send invitation email automatically.

After signing in, a customer can view their own orders, invoices, and support requests. The portal does not currently let customers create support tickets, edit records, or make payments. The server filters portal records by both workspace and customer account.

### Platform administration

The optional platform admin area is at `/platform-admin/login`. It is separate from staff accounts and is configured with environment variables:

- Search all workspaces by name or slug.
- Review staff, customer, and order counts.
- Update a workspace's name, industry, and address.
- Open the staff sign-in page for a workspace.
- Permanently delete a workspace and its associated records.

Deleting a workspace is destructive. The admin must enter both the exact workspace slug and the configured platform admin password. Deleted workspace data cannot be recovered unless you have a database backup.

### Security and application behavior

- Django handles routing, forms, sessions, CSRF checks, validation, and database access.
- Staff and customer records are scoped to a workspace; customer portal queries are additionally scoped to the signed-in customer.
- New passwords are stored using Django's password hashing. Existing Werkzeug password hashes are checked at sign-in and upgraded to Django hashes after a successful login.
- Invitation tokens are stored as SHA-256 digests, not as the original token.
- Registration, record edits, portal sign-in, and admin actions use server-side Django views; the browser frontend does not replace server-side authorization or validation.

## Requirements

- Python 3.10 or later.
- `pip`.
- Windows, macOS, or Linux.
- Internet access in the browser to load React modules from `esm.sh` and hosted Google Fonts.

The Python dependencies are listed in [`requirements.txt`](requirements.txt). Node.js is not required for the current app.

## Run locally

The checked-out local `.env` file supplies development settings. To enable the local platform-admin login, set both `PLATFORM_ADMIN_USERNAME` and `PLATFORM_ADMIN_PASSWORD` in that file; they are blank by default. It is ignored by Git and excluded from Vercel deployments. The commands below use the default SQLite database at `instance/business.db` and start Django's development server on `127.0.0.1:5000`.

### Windows (PowerShell)

Open PowerShell in the project folder:

```powershell
cd C:\path\to\fieldnote
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 127.0.0.1:5000
```

Then open [http://127.0.0.1:5000](http://127.0.0.1:5000).

If PowerShell script activation is disabled, use the virtual environment's Python executable directly instead:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:5000
```

If the `py` launcher is not installed, substitute `python` for `py` when creating the virtual environment.

### macOS or Linux

```bash
cd /path/to/fieldnote
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 127.0.0.1:5000
```

Then open [http://127.0.0.1:5000](http://127.0.0.1:5000).

### What each setup command does

1. `python -m venv .venv` creates an isolated Python environment in the project directory.
2. Activate that environment, or invoke its `python.exe` directly on Windows.
3. `pip install -r requirements.txt` installs the Python dependencies.
4. `python manage.py migrate` creates or updates the database tables.
5. `python manage.py runserver 127.0.0.1:5000` starts the local development server.

Keep the terminal running while you use the app. Press **Ctrl+C** in that terminal to stop the server. Run the same `runserver` command again to start it later.

The development server defaults to port 8000 if no address is supplied. The commands above explicitly use port 5000. If that port is already in use, choose another, for example `python manage.py runserver 127.0.0.1:5001`, and open that port in your browser.

## First use

1. Open the landing page and complete **Company name**, **Your name**, **Work email**, and **Password** (at least eight characters). Industry is optional.
2. Select **Create workspace**. Fieldnote creates the workspace and its first staff account.
3. Sign in with the username and password you registered.
4. Use the sidebar to open **Customers**, **Orders**, **Invoices**, **Products**, **Support**, **Plans**, **Team**, or **Departments**.
5. Add a customer before creating an order, invoice, or ticket, since those records require a customer.
6. Use **Sign out** in the sidebar when finished.

The workspace slug is generated from the company name. Existing staff can use the landing page's workspace lookup or go directly to `/t/<workspace-slug>/login`.

## Platform admin setup

Platform admin access is disabled until **both** `PLATFORM_ADMIN_USERNAME` and `PLATFORM_ADMIN_PASSWORD` are set. Configure them in the same terminal/session used to start Django.

### Windows (PowerShell)

```powershell
$env:PLATFORM_ADMIN_USERNAME = "choose-a-private-admin-name"
$env:PLATFORM_ADMIN_PASSWORD = "use-a-long-unique-password"
python manage.py runserver 127.0.0.1:5000
```

If using the virtual environment without activation:

```powershell
$env:PLATFORM_ADMIN_USERNAME = "choose-a-private-admin-name"
$env:PLATFORM_ADMIN_PASSWORD = "use-a-long-unique-password"
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:5000
```

### macOS or Linux

```bash
export PLATFORM_ADMIN_USERNAME="choose-a-private-admin-name"
export PLATFORM_ADMIN_PASSWORD="use-a-long-unique-password"
python manage.py runserver 127.0.0.1:5000
```

Open [http://127.0.0.1:5000/platform-admin/login](http://127.0.0.1:5000/platform-admin/login). These credentials are application environment settings, not a user account created in the database. Do not put real passwords in source control or share the platform admin URL and credentials publicly.

## Database and migrations

### Default database

SQLite is used by default. Fieldnote creates the `instance` directory if needed and stores the database at:

```text
instance/business.db
```

Models are in [`app/models/`](app/models/); migrations are in [`app/migrations/`](app/migrations/). After pulling a change that adds or changes a model, apply migrations with:

```powershell
python manage.py migrate
```

Replace `python` with `.\.venv\Scripts\python.exe` if the virtual environment is not activated on Windows.

### Existing Flask database

The Django models retain the existing SQLite table names to support adoption of a prior Flask database. **Back up the database first.** For an existing database whose tables match the initial Django migration, run:

```powershell
python manage.py migrate --fake-initial
```

Use the regular `python manage.py migrate` command for a new/empty database. `--fake-initial` is intended only for an existing schema with the expected tables; it does not repair an incompatible schema or validate that every column has the expected definition. Review the migration output and verify the app against a copy of the database before using an existing production database.

### Database URL

Set `DATABASE_URL` to select a database. The application parses SQLite, PostgreSQL, and MySQL URL schemes:

```text
SQLite:      sqlite:///C:/absolute/path/to/business.db
PostgreSQL:  postgresql://USER:PASSWORD@HOST:5432/DATABASE
MySQL:       mysql://USER:PASSWORD@HOST:3306/DATABASE
```

SQLite and PostgreSQL are supported by the repository's default dependencies. MySQL deployments need a compatible Django database driver installed in the environment. The URL parser is not a substitute for installing/configuring that driver.

## Deploy to Vercel

Vercel detects this Django project from `manage.py` and `WSGI_APPLICATION`. The `.python-version` file selects Python 3.13, and `STATIC_ROOT` lets Vercel collect static assets and serve them from its CDN. No Node.js build or custom Vercel routing configuration is required.

The local `.env` file is only for development. It is excluded from deployments and is not a way to configure Vercel. Set production variables in the Vercel project's **Settings → Environment Variables** instead. Vercel Functions have an ephemeral filesystem, so production must use a persistent PostgreSQL database; the local SQLite database is deliberately rejected when `DJANGO_DEBUG=false`. The `.vercelignore` file prevents the local database and development files from being included in deployments. Create a PostgreSQL database with a provider supported by your Vercel project, then add these variables in the Vercel project's **Settings → Environment Variables** for every environment you deploy:

Generate a signing key locally with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` and store it as a Vercel secret.

| Variable | Value |
| --- | --- |
| `SECRET_KEY` | A long, random, private Django signing key |
| `DJANGO_DEBUG` | `false` |
| `DATABASE_URL` | The provider's PostgreSQL connection URL |
| `ALLOWED_HOSTS` | Comma-separated Vercel and custom-domain hostnames, without `https://` |
| `PLATFORM_ADMIN_USERNAME` | Optional platform admin login name |
| `PLATFORM_ADMIN_PASSWORD` | Optional long, unique platform admin password |

Vercel's `VERCEL_URL` and `VERCEL_PROJECT_PRODUCTION_URL` are also accepted as hostnames. `CSRF_TRUSTED_ORIGINS` can optionally be set to comma-separated origins including `https://` when additional origins are needed. Do not commit credentials or database URLs.

Before the first deployment, and whenever a migration is added, apply migrations to the production database from a trusted local environment with the deployment settings:

```powershell
$env:SECRET_KEY = "the-same-private-key-configured-in-vercel"
$env:DJANGO_DEBUG = "false"
$env:DATABASE_URL = "the-postgresql-url-from-your-database-provider"
$env:ALLOWED_HOSTS = "your-project.vercel.app,your-custom-domain.example"
python manage.py migrate
```

Vercel automatically runs `collectstatic` during the build because `STATIC_ROOT` is configured. The tracked local SQLite database is not a production database; back up and migrate any existing data separately before moving an existing installation.

## Configuration

| Environment variable | Purpose | Default |
| --- | --- | --- |
| `SECRET_KEY` | Django session and CSRF signing key | Local-only development fallback; required when debug is disabled |
| `DATABASE_URL` | Select SQLite, PostgreSQL, or MySQL connection | SQLite at `instance/business.db` in local debug mode; required in production |
| `PLATFORM_ADMIN_USERNAME` | Platform admin login name | Empty (admin sign-in disabled) |
| `PLATFORM_ADMIN_PASSWORD` | Platform admin password | Empty (admin sign-in disabled) |
| `ALLOWED_HOSTS` | Comma-separated accepted host names | `*` locally; required in production (Vercel host variables are included automatically) |
| `CSRF_TRUSTED_ORIGINS` | Optional comma-separated trusted origins including scheme | Inferred from allowed host names |
| `DJANGO_DEBUG` | Enables Django debug mode when set to `1`, `true`, or `yes` | `true` locally; `false` on Vercel |

Example PowerShell settings for a local development session:

```powershell
$env:SECRET_KEY = "a-private-development-key"
$env:DJANGO_DEBUG = "true"
$env:ALLOWED_HOSTS = "127.0.0.1,localhost"
```

Environment variables set this way apply only to the current PowerShell session. For Vercel deployment, see [Deploy to Vercel](#deploy-to-vercel). `manage.py runserver` is for development only.

## URLs

| Page/action | URL |
| --- | --- |
| Landing and workspace registration | `/` |
| Register workspace (form submission) | `POST /register` |
| Find a workspace sign-in page (form submission) | `POST /workspace` |
| Staff sign-in | `/t/<workspace-slug>/login` |
| Staff dashboard | `/t/<workspace-slug>/` |
| Workspace records | `/t/<workspace-slug>/<section>` |
| Customer portal sign-in | `/t/<workspace-slug>/portal/login` |
| Customer portal | `/t/<workspace-slug>/portal/` |
| Platform admin sign-in | `/platform-admin/login` |
| Platform admin workspace list | `/platform-admin/` |

Workspace section names are `customers`, `orders`, `invoices`, `products`, `tickets`, `subscriptions`, `employees`, and `departments`.

## Testing and diagnostics

Run Django's configuration checks:

```powershell
python manage.py check
```

Run the integration tests:

```powershell
python manage.py test tests
```

The tests cover CSRF-protected registration, upgrading a legacy Werkzeug staff password after successful login, customer invitation and portal access, customer-to-customer record isolation, and password/slug-confirmed platform workspace deletion.

## Project layout

```text
.
|-- app/
|   |-- migrations/           # Django schema migrations
|   |-- models/               # Workspace, customer, order, invoice, and related models
|   |-- routes/               # Authentication, dashboard, records, portal, and admin views
|   |-- static/
|   |   |-- css/app.css       # Interface styles and responsive layouts
|   |   `-- js/app.js         # React pages and forms
|   `-- templates/react.html  # React bootstrap template
|-- docs/
|   `-- screenshots/          # Screenshots embedded in this README
|-- fieldnote/                # Django settings, root URLs, and WSGI entry point
|-- instance/                 # Local SQLite database
|-- tests/                    # Django integration tests
|-- manage.py                 # Django command-line entry point
`-- requirements.txt          # Python dependencies
```

## Current scope and known limitations

- Staff login is per workspace. The initial account has the `admin` role, but the app does not currently provide staff account creation, staff invitations, or role-based permissions.
- **Team** is an employee directory; employee records are not staff login accounts.
- Customer invitations are shared manually; no email delivery provider is connected.
- Customer portal access is read-only for orders, invoices, and support requests. Customers cannot open tickets from the portal.
- Orders and invoices have totals but no line-item editor, PDF/export workflow, or payment integration.
- Products store a stock number, but order creation does not update stock automatically.
- Subscription/plan records do not trigger recurring billing.
- The app uses Django's built-in development server in the local setup instructions. Vercel runs it as a Python Function and requires production environment variables and a persistent PostgreSQL database.
