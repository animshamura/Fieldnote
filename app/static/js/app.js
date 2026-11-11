import React, { useState } from "https://esm.sh/react@18.3.1";
import { createRoot } from "https://esm.sh/react-dom@18.3.1/client";
import htm from "https://esm.sh/htm@3.1.1";

const html = htm.bind(React.createElement);
const bootstrap = JSON.parse(document.getElementById("fieldnote-bootstrap").textContent);
const { page, props, flashes, csrfToken } = bootstrap;

const currency = (amount) => new Intl.NumberFormat(undefined, {
  style: "currency",
  currency: "USD",
}).format(Number(amount || 0));

const dateLabel = (value, options = { month: "short", day: "numeric", year: "numeric" }) => {
  if (!value) return "—";
  const date = new Date(value.length === 10 ? `${value}T00:00:00` : value);
  return Number.isNaN(date.getTime()) ? "—" : date.toLocaleDateString(undefined, options);
};

const statusClass = (value) => String(value || "").toLowerCase().replaceAll(" ", "-");
const csrf = () => html`<input type="hidden" name="csrfmiddlewaretoken" value=${csrfToken} />`;
const flashesView = () => flashes?.length
  ? html`<div className="flash-stack">${flashes.map(([category, message], i) => html`<div key=${i} className=${`flash ${category}`}>${message}</div>`)}</div>`
  : null;
const Brand = ({ href = "/" }) => html`
  <a className="brand" href=${href} aria-label="Fieldnote home">
    <span className="brand-mark" aria-hidden="true">
      <svg viewBox="0 0 32 32" focusable="false">
        <path className="brand-page" d="M9 5.75h9l5.5 5.5v13A2.75 2.75 0 0 1 20.75 27h-11A2.75 2.75 0 0 1 7 24.25v-15A3.5 3.5 0 0 1 9 5.75Z" />
        <path className="brand-fold" d="M18 6v5.5h5.5" />
        <path className="brand-line" d="M10.5 17.25c2.2-1.6 4.2-1.6 6.1 0 1.8 1.6 3.5 1.6 5.2 0M10.5 21c2.2-1.6 4.2-1.6 6.1 0 1.8 1.6 3.5 1.6 5.2 0" />
        <circle className="brand-seed" cx="12" cy="12.25" r="1.15" />
      </svg>
    </span>
    <span>fieldnote</span>
  </a>`;
function AuthLanding() {
  return html`
    <main className="auth-layout">
      <section className="auth-story">
        <div className="story-topline"><${Brand} /><span className="story-edition">A FIELD GUIDE TO RUNNING THINGS <b>NO. 01</b></span></div>
        <div className="story-copy"><div className="eyebrow"><span></span> CUSTOMERS, ORDERS, AND WHAT COMES NEXT.</div><h1>From first hello<br />to final invoice,<br /><em>stay in sync.</em></h1><p>Bring customer relationships, orders, invoices, and support into one workspace—so the important details stay connected.</p><div className="story-proof"><span>✳</span> One clear place for the work behind your business</div></div>
        <div className="story-foot"><span>FROM CUSTOMER HELLO TO WORK WELL DONE.</span><span>MADE FOR THE EVERYDAY RUNNING OF THINGS</span></div>
        <div className="story-art" aria-hidden="true">
          <div className="art-sun"></div><div className="art-ring ring-one"></div><div className="art-ring ring-two"></div>
          <svg className="art-bloom" viewBox="0 0 220 220"><path d="M111 194c1-43 0-73-2-106m0 62c-25-23-44-31-66-31m67 9c26-27 46-37 69-40m-70 2c-9-26-8-45 0-70" /><path d="M109 145c-14-19-28-25-47-26 7 19 22 29 47 26Zm1-3c12-23 27-33 48-37-4 23-19 35-48 37Zm-1-51c-15-13-21-26-19-45 18 10 24 24 19 45Z" /><circle cx="109" cy="82" r="13" /></svg>
          <div className="art-note"><span>FIELDNOTE / 001</span><strong>The details<br />make a business.</strong><i>↗</i></div>
          <div className="art-sticker">PEOPLE<br />AT WORK <span>✳</span></div>
          <span className="art-caption">CUSTOMERS · SALES · SUPPORT</span>
        </div>
      </section>
      <section className="auth-panel">
        <div className="mobile-brand"><${Brand} /></div>
        <div className="auth-form-wrap">
          <div className="auth-heading"><span className="kicker">SET UP YOUR WORKSPACE</span><h2>Put the pieces in one place.</h2><p>Create a home for your customers, orders, invoices, and team.</p></div>
          ${flashesView()}
          <form className="form-stack" method="post" action="/register">
            ${csrf()}
            <label>Company name<input name="company" autoComplete="organization" placeholder="Northwind Studio" required maxLength="150" /></label>
            <div className="form-row"><label>Your name<input name="username" autoComplete="name" placeholder="Jordan Lee" required maxLength="80" /></label><label>Industry <span className="optional">OPTIONAL</span><input name="industry" placeholder="Design, retail…" maxLength="80" /></label></div>
            <label>Work email<input type="email" name="email" autoComplete="email" placeholder="you@company.com" required maxLength="160" /></label>
            <label>Password <span className="field-hint">8 characters minimum</span><input type="password" name="password" autoComplete="new-password" placeholder="Create a password" minLength="8" required /></label>
            <button className="button button-primary button-wide" type="submit">Create workspace <span>↗</span></button>
          </form>
          <div className="auth-footnote"><strong>Already have a workspace?</strong><form className="workspace-lookup" method="post" action="/workspace">${csrf()}<input name="slug" placeholder="Enter your workspace name" aria-label="Workspace name" required /><button type="submit" aria-label="Open workspace sign in">→</button></form></div>
        </div>
        <div className="panel-footer"><span>LESS SCATTER. MORE FOLLOW-THROUGH.</span><a href="/platform-admin/login">PLATFORM ADMIN ↗</a></div>
      </section>
    </main>`;
}

function LoginPage({ portal = false }) {
  const tenant = props.tenant;
  return html`
    <${Brand} href="/" />
    <main className="login-card">
      <div className="login-emblem">${tenant.name.slice(0, 1).toUpperCase()}</div><span className="kicker">${tenant.name}${portal ? " CUSTOMER PORTAL" : ""}</span><h1>Welcome back.</h1>
      <p>${portal ? "Sign in to view your orders, invoices, and support requests." : "Sign in to your company workspace."}</p>
      ${flashesView()}
      <form className="form-stack" method="post">
        ${csrf()}
        ${portal
          ? html`<label>Email address<input type="email" name="email" autoComplete="username" required autoFocus /></label>`
          : html`<label>Username<input name="username" autoComplete="username" placeholder="Your username" required autoFocus /></label>`}
        <label>Password<input type="password" name="password" autoComplete="current-password" required /></label>
        <button className="button button-primary button-wide" type="submit">Sign in <span>↗</span></button>
      </form>
      ${portal ? null : html`<a className="back-link" href="/">← Create a new workspace</a>`}
    </main>
    <div className="login-caption">${portal ? "FIELDNOTE CUSTOMER PORTAL" : "A LITTLE MORE CLARITY, EVERY DAY."}</div>`;
}

const staffNav = [
  ["customers", "Customers", "◉"], ["orders", "Orders", "↗"], ["invoices", "Invoices", "▤"],
  ["products", "Products", "◇"], ["tickets", "Support", "◌"], ["subscriptions", "Plans", "⟳"],
  ["employees", "Team", "♧"], ["departments", "Departments", "⊞"],
];

function StaffShell({ children, active = "" }) {
  const tenant = props.tenant;
  const user = props.user;
  return html`
    <div className="app-shell">
      <aside className="sidebar">
        <${Brand} href=${`/t/${tenant.slug}/`} />
        <div className="workspace-label">WORKSPACE</div>
        <div className="workspace-switch"><span className="workspace-dot"></span><span>${tenant.name}</span><span className="chevron">⌄</span></div>
        <nav className="main-nav" aria-label="Main navigation">
          <a className=${`nav-link ${active === "overview" ? "active" : ""}`} href=${`/t/${tenant.slug}/`}><span className="nav-icon">▦</span>Overview</a>
          <span className="nav-caption">OPERATIONS</span>
          ${staffNav.slice(0, 6).map(([key, label, icon]) => html`<a key=${key} className=${`nav-link ${active === key ? "active" : ""}`} href=${`/t/${tenant.slug}/${key}`}><span className="nav-icon">${icon}</span>${label}</a>`)}
          <span className="nav-caption">ORGANIZATION</span>
          ${staffNav.slice(6).map(([key, label, icon]) => html`<a key=${key} className=${`nav-link ${active === key ? "active" : ""}`} href=${`/t/${tenant.slug}/${key}`}><span className="nav-icon">${icon}</span>${label}</a>`)}
        </nav>
        <div className="sidebar-bottom">
          <div className="profile"><div className="avatar">${user.username.slice(0, 1).toUpperCase()}</div><div className="profile-copy"><strong>${user.username}</strong><span>${user.role.slice(0, 1).toUpperCase()}${user.role.slice(1)}</span></div></div>
          <form method="post" action=${`/t/${tenant.slug}/logout`}>${csrf()}<button className="signout" type="submit" aria-label="Sign out" title="Sign out">↗</button></form>
        </div>
      </aside>
      <main className="main-content">
        <header className="topbar"><div className="breadcrumb">${tenant.name} <span>/</span> ${active === "overview" ? "Overview" : (staffNav.find(([key]) => key === active)?.[1] || "Customers")}</div><div className="topbar-right"><span className="live-dot"></span><span>Workspace live</span><span className="topbar-date">${new Date().toLocaleDateString(undefined, { weekday: "long", month: "long", day: "2-digit" })}</span></div></header>
        <div className="page-content">${flashesView()}${children}</div>
      </main>
    </div>`;
}

function Dashboard() {
  const { tenant, user, customers, products, employees, orders, invoices, tickets, subscriptions, logs, revenue, total_orders } = props;
  const openOrders = orders.filter((item) => !["Completed", "Cancelled"].includes(item.status)).length;
  const openTickets = tickets.filter((item) => !["Resolved", "Closed"].includes(item.status)).length;
  const metrics = [
    ["Revenue", currency(revenue), `From ${invoices.length} invoice${invoices.length === 1 ? "" : "s"}`, "↗", "metric-ink", ""],
    ["Customers", customers.length, "In your address book", "◉", "", "mint"],
    ["Open orders", openOrders, `${currency(total_orders)} total order value`, "↗", "", "coral"],
    ["Support queue", openTickets, `${tickets.length} total ticket${tickets.length === 1 ? "" : "s"}`, "◌", "", "gold"],
  ];
  return html`<${StaffShell} active="overview">
    <section className="page-heading dashboard-heading"><div><span className="kicker">YOUR FIELD GUIDE · TODAY</span><h1>${props.welcome}</h1><p>Here’s what’s happening across ${tenant.name}.</p></div><div className="dashboard-hero-aside">    <div className="dashboard-orbit" aria-hidden="true"><svg viewBox="0 0 80 80" focusable="false"><path d="M40 68V35m0 21c-9-11-18-14-28-14 4 11 13 17 28 14Zm0-11c9-11 17-15 28-17-2 12-11 17-28 17Zm0-18c-8-7-11-14-9-24 10 5 13 13 9 24Z" /><circle cx="40" cy="31" r="5" /></svg></div><a className="button button-primary" href=${`/t/${tenant.slug}/customers`}>Add a customer <span>＋</span></a><span className="dashboard-date">${new Date().toLocaleDateString(undefined, { weekday: "long", month: "short", day: "numeric" })}</span></div></section>
    <section className="metric-grid" aria-label="Business summary">${metrics.map(([label, amount, note, mark, extra, color]) => html`<article key=${label} className=${`metric-card ${extra}`}><div className="metric-top"><span>${label}</span><span className=${`metric-mark ${color}`}>${mark}</span></div><strong>${amount}</strong><small>${note}</small><div className=${`metric-rule ${color ? `${color}-rule` : ""}`}></div></article>`)}</section>
    <div className="dashboard-grid">
      <section className="panel recent-panel"><div className="panel-heading"><div><span className="kicker">THE LATEST</span><h2>Recent orders</h2></div><a className="text-link" href=${`/t/${tenant.slug}/orders`}>All orders <span>→</span></a></div>
        ${orders.length ? html`<div className="table-wrap"><table><thead><tr><th>ORDER</th><th>CUSTOMER</th><th>STATUS</th><th className="align-right">TOTAL</th></tr></thead><tbody>${orders.slice(0, 6).map((order) => html`<tr key=${order.id}><td><strong className="table-primary">${order.order_number}</strong></td><td>${order.customer_name || "—"}</td><td><span className=${`status-pill ${statusClass(order.status)}`}>${order.status}</span></td><td className="align-right amount">${currency(order.total_amount)}</td></tr>`)}</tbody></table></div>`
          : html`<div className="empty-state"><span className="empty-icon">↗</span><strong>Your first order starts here.</strong><p>Keep a record of what’s moving through your business.</p><a className="text-link" href=${`/t/${tenant.slug}/orders`}>Create an order →</a></div>`}
      </section>
      <section className="panel activity-panel"><div className="panel-heading"><div><span className="kicker">WORKSPACE PULSE</span><h2>Recent activity</h2></div><span className="activity-count">${logs.length} EVENTS</span></div>
        ${logs.length ? html`<div className="activity-list">${logs.map((log) => html`<div key=${log.id} className="activity-item"><span className="activity-dot"></span><div><strong>${log.action}</strong><p>${log.details || "Workspace updated"}</p></div><time>${dateLabel(log.created_at, { month: "short", day: "2-digit" })}</time></div>`)}</div>`
          : html`<div className="empty-state compact-empty"><span className="empty-icon">✳</span><strong>A fresh start.</strong><p>Actions across your workspace will show up here.</p></div>`}
      </section>
    </div>
    <section className="quick-links"><div className="quick-intro"><span className="kicker">KEEP THINGS MOVING</span><h2>Jump back in.</h2></div><div className="quick-link-grid">
      ${[["invoices", "▤", "coral-bg", "Invoices", `${invoices.length} records`], ["products", "◇", "green-bg", "Products", `${products.length} in catalog`], ["employees", "♧", "yellow-bg", "Your team", `${employees.length} people`], ["subscriptions", "⟳", "blue-bg", "Plans", `${subscriptions.length} subscriptions`]].map(([key, icon, color, label, count]) => html`<a key=${key} href=${`/t/${tenant.slug}/${key}`}><span className=${`quick-icon ${color}`}>${icon}</span><strong>${label}</strong><small>${count}</small><span className="quick-arrow">↗</span></a>`)}
    </div></section>
  </${StaffShell}>`;
}

function ResourceField({ item }) {
  if (item.type === "textarea") return html`<textarea name=${item.name} rows="3" defaultValue=${item.value ?? ""} required=${item.required || undefined} />`;
  if (item.type === "select" || item.type === "customer" || item.type === "department") {
    const options = item.type === "select" ? item.choices : item.options.map((option) => [String(option.id), option.name]);
    const selected = item.value == null ? "" : String(item.value);
    return html`<select name=${item.name} defaultValue=${selected} required=${item.required || undefined}><option value="">${item.type === "customer" ? "Choose a customer…" : item.type === "department" ? "No department" : "Choose…"}</option>${options.map((option) => {
      const value = Array.isArray(option) ? option[0] : option;
      const label = Array.isArray(option) ? option[1] : option;
      return html`<option key=${value} value=${value}>${label}</option>`;
    })}</select>`;
  }
  const type = ["number", "integer"].includes(item.type) ? "number" : item.type;
  return html`<input name=${item.name} type=${type} defaultValue=${item.value ?? ""} min=${type === "number" || item.type === "integer" ? "0" : undefined} step=${item.type === "integer" ? "1" : type === "number" ? "0.01" : undefined} required=${item.required || undefined} />`;
}

function ResourcePage() {
  const { tenant, resource, resource_key, records, fields, columns, record, errors } = props;
  const singular = resource.singular;
  const action = record ? `/t/${tenant.slug}/${resource_key}/${record.id}/edit` : `/t/${tenant.slug}/${resource_key}`;
  const accounts = new Set(props.client_account_ids || []);
  return html`<${StaffShell} active=${resource_key}>
    <section className="page-heading resource-heading"><div><span className="kicker">WORKSPACE RECORDS</span><h1>${resource.label}</h1><p>Keep your ${singular} details clear and up to date.</p></div><a className="button button-primary" href="#record-form">Add ${singular} <span>＋</span></a></section>
    <div className="resource-layout">
      <section className="panel records-panel"><div className="panel-heading records-title"><div><span className="kicker">${records.length} RECORD${records.length === 1 ? "" : "S"}</span><h2>All ${resource.label.toLowerCase()}</h2></div></div>
        ${records.length ? html`<div className="table-wrap"><table><thead><tr>${columns.map((column) => html`<th key=${column.name}>${column.label.toUpperCase()}</th>`)}<th className="actions-heading">ACTIONS</th></tr></thead><tbody>
          ${records.map((item) => html`<tr key=${item.id}>${columns.map((column, index) => html`<td key=${column.name}>${index === 0 ? html`<strong className="table-primary">${item.display[column.name]}</strong>` : item.display[column.name]}</td>`)}
            <td className="row-actions">
              ${resource_key === "customers" ? accounts.has(item.id) ? html`<span className="account-state">Portal active</span>` : html`<form method="post" action=${`/t/${tenant.slug}/customers/${item.id}/invite`}>${csrf()}<button className="client-invite-button" type="submit">Invite</button></form>` : null}
              <a className="icon-action" title=${`Edit ${singular}`} aria-label=${`Edit ${singular}`} href=${`/t/${tenant.slug}/${resource_key}/${item.id}/edit`}>↗</a>
              <form method="post" action=${`/t/${tenant.slug}/${resource_key}/${item.id}/delete`} onSubmit=${(event) => {
                if (!window.confirm(`Delete this ${singular}${resource_key === "customers" && accounts.has(item.id) ? " and their portal account" : ""}?`)) event.preventDefault();
              }}>${csrf()}<button className="icon-action delete-action" type="submit" title=${`Delete ${singular}`} aria-label=${`Delete ${singular}`}>×</button></form>
            </td></tr>`)}
        </tbody></table></div>` : html`<div className="empty-state"><span className="empty-icon">◇</span><strong>No ${resource.label.toLowerCase()} yet.</strong><p>Add your first ${singular} using the form.</p></div>`}
      </section>
      <section className="panel form-panel" id="record-form"><div className="panel-heading"><div><span className="kicker">${record ? "EDIT RECORD" : "NEW RECORD"}</span><h2>${record ? "Update" : "Add a"} ${singular}</h2></div></div>
        ${errors.length ? html`<div className="form-errors" role="alert">${errors.map((error, i) => html`<p key=${i}>${error}</p>`)}</div>` : null}
        <form className="form-stack record-form" method="post" action=${action}>${csrf()}
          ${fields.map((item) => html`<label key=${item.name}>${item.label}${item.required ? html`<span className="required-mark">*</span>` : null}<${ResourceField} item=${item} /></label>`)}
          <div className="form-actions"><button className="button button-primary button-wide" type="submit">${record ? "Save changes" : `Add ${singular}`} <span>↗</span></button>${record ? html`<a className="cancel-link" href=${`/t/${tenant.slug}/${resource_key}`}>Cancel</a>` : null}</div>
        </form>
      </section>
    </div>
  </${StaffShell}>`;
}

function InviteCreated() {
  const { tenant, customer, invite_url, expires_at } = props;
  const [copied, setCopied] = useState(false);
  const [copyError, setCopyError] = useState("");
  const copyLink = async () => {
    try {
      await navigator.clipboard.writeText(invite_url);
      setCopied(true);
      setCopyError("");
    } catch (error) {
      setCopyError(`Could not copy this link: ${error.message}`);
    }
  };
  return html`<${StaffShell} active="customers">
    <section className="page-heading"><div><span className="kicker">CUSTOMER PORTAL</span><h1>Invite ready to share</h1><p>${customer.name} can use this secure link to create a portal password.</p></div></section>
    <section className="panel invite-panel"><div className="invite-symbol">↗</div><span className="kicker">INVITE FOR ${customer.email.toUpperCase()}</span><h2>Send this link to your customer</h2><p>The link works once and expires in 72 hours. Fieldnote does not send email automatically, so share it with ${customer.name} using your usual secure channel.</p>
      <div className="copy-row"><input type="text" value=${invite_url} readOnly aria-label="Customer invitation link" /><button className="button button-primary" type="button" onClick=${copyLink}>${copied ? "Copied" : "Copy link"}</button></div>
      ${copyError ? html`<p role="alert">${copyError}</p>` : null}
      <div className="invite-meta"><span>EXPIRES</span><strong>${dateLabel(expires_at, { month: "short", day: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit", timeZone: "UTC" })} UTC</strong></div>
      <div className="invite-actions"><a className="text-link" href=${`/t/${tenant.slug}/portal/login`}>Customer sign-in page ↗</a><a className="cancel-link" href=${`/t/${tenant.slug}/customers`}>Back to customers</a></div>
    </section>
  </${StaffShell}>`;
}

function InviteAccept() {
  const { tenant, invite } = props;
  return html`<main className="login-card"><div className="login-emblem">${tenant.name.slice(0, 1).toUpperCase()}</div><span className="kicker">${tenant.name} CUSTOMER PORTAL</span><h1>Set your password.</h1><p>Create a password to access your customer portal as ${invite.email}.</p>${flashesView()}
    <form className="form-stack" method="post">${csrf()}<label>Password <span className="field-hint">8 characters minimum</span><input type="password" name="password" autoComplete="new-password" minLength="8" required autoFocus /></label><label>Confirm password<input type="password" name="confirm_password" autoComplete="new-password" minLength="8" required /></label><button className="button button-primary button-wide" type="submit">Create account <span>↗</span></button></form>
  </main><div className="login-caption">FIELDNOTE CUSTOMER PORTAL</div>`;
}

function InviteInvalid() {
  return html`<main className="login-card"><div className="login-emblem">!</div><span className="kicker">${props.tenant.name}</span><h1>This invite isn’t available.</h1><p>It may have expired, already been used, or been replaced by a newer invitation. Ask your contact for a fresh invite link.</p><a className="button button-primary button-wide" href=${`/t/${props.tenant.slug}/portal/login`}>Go to customer sign in <span>↗</span></a></main><div className="login-caption">FIELDNOTE CUSTOMER PORTAL</div>`;
}

function ClientPortal() {
  const { tenant, account, customer, orders, invoices, tickets } = props;
  const firstName = customer.name.split(" ")[0];
  return html`<div className="client-shell">
    <header className="client-topbar"><${Brand} href=${`/t/${tenant.slug}/portal/`} /><div className="client-top-right"><span>${tenant.name} portal</span><form method="post" action=${`/t/${tenant.slug}/portal/logout`}>${csrf()}<button className="client-signout" type="submit">Sign out <span>↗</span></button></form></div></header>
    <main className="client-content">
      <section className="client-welcome"><div><span className="kicker">YOUR CUSTOMER PORTAL</span><h1>Welcome, ${firstName}.</h1><p>Your orders, invoices, and support updates in one place.</p></div><div className="client-profile"><span className="client-avatar">${customer.name.slice(0, 1).toUpperCase()}</span><div><strong>${customer.name}</strong><span>${account.email}</span></div></div></section>
      <section className="client-stats"><div><span>ORDERS</span><strong>${orders.length}</strong></div><div><span>INVOICES</span><strong>${invoices.length}</strong></div><div><span>SUPPORT REQUESTS</span><strong>${tickets.length}</strong></div></section>
      <section className="client-records-grid">
        <article className="panel client-record-panel"><div className="panel-heading"><div><span className="kicker">PURCHASES</span><h2>Your orders</h2></div></div>${orders.length ? html`<div className="table-wrap"><table><thead><tr><th>ORDER</th><th>STATUS</th><th className="align-right">TOTAL</th></tr></thead><tbody>${orders.map((order) => html`<tr key=${order.id}><td><strong className="table-primary">${order.order_number}</strong></td><td><span className=${`status-pill ${statusClass(order.status)}`}>${order.status}</span></td><td className="align-right amount">${currency(order.total_amount)}</td></tr>`)}</tbody></table></div>` : html`<div className="client-empty"><span>↗</span><p>No orders to show yet.</p></div>`}</article>
        <article className="panel client-record-panel"><div className="panel-heading"><div><span className="kicker">BILLING</span><h2>Your invoices</h2></div></div>${invoices.length ? html`<div className="table-wrap"><table><thead><tr><th>INVOICE</th><th>DUE DATE</th><th className="align-right">TOTAL</th></tr></thead><tbody>${invoices.map((invoice) => html`<tr key=${invoice.id}><td><div className="invoice-cell"><strong className="table-primary">${invoice.invoice_number}</strong><span className=${`status-pill ${statusClass(invoice.status)}`}>${invoice.status}</span></div></td><td>${dateLabel(invoice.due_date)}</td><td className="align-right amount">${currency(invoice.total)}</td></tr>`)}</tbody></table></div>` : html`<div className="client-empty"><span>▤</span><p>No invoices to show yet.</p></div>`}</article>
        <article className="panel client-record-panel client-support-panel"><div className="panel-heading"><div><span className="kicker">HELP & SUPPORT</span><h2>Your support requests</h2></div></div>${tickets.length ? html`<div className="client-ticket-list">${tickets.map((ticket) => html`<div key=${ticket.id} className="client-ticket"><div><strong>${ticket.subject}</strong><span>${dateLabel(ticket.created_at)} · ${ticket.priority} priority</span></div><span className=${`status-pill ${statusClass(ticket.status)}`}>${ticket.status}</span></div>`)}</div>` : html`<div className="client-empty"><span>◌</span><p>No support requests to show yet.</p></div>`}</article>
      </section>
      <footer className="client-footer"><span>${tenant.name}</span><span>Signed in as ${account.email}</span></footer>
    </main>
  </div>`;
}

function PlatformHeader() {
  return html`<header className="platform-topbar"><${Brand} href="/platform-admin/" /><div className="platform-top-right"><span className="admin-indicator">PLATFORM ADMIN</span><form method="post" action="/platform-admin/logout">${csrf()}<button className="client-signout" type="submit">Sign out <span>↗</span></button></form></div></header>`;
}

function PlatformLogin() {
  return html`<${Brand} href="/" /><main className="login-card"><div className="login-emblem">⌘</div><span className="kicker">PLATFORM ADMINISTRATION</span><h1>Workspace control.</h1><p>Sign in to manage Fieldnote workspaces.</p>
    ${props.configured ? null : html`<div className="flash error">Platform admin access is not configured. Set PLATFORM_ADMIN_USERNAME and PLATFORM_ADMIN_PASSWORD in the server environment, then restart the app.</div>`}${flashesView()}
    <form className="form-stack" method="post">${csrf()}<label>Username<input name="username" autoComplete="username" required autoFocus /></label><label>Password<input type="password" name="password" autoComplete="current-password" required /></label><button className="button button-primary button-wide" type="submit">Sign in <span>↗</span></button></form>
  </main><div className="login-caption">RESTRICTED ADMIN AREA</div>`;
}

function PlatformDashboard() {
  const { tenants, search, user_counts, customer_counts, order_counts } = props;
  return html`<div className="platform-shell"><${PlatformHeader} /><main className="platform-content">${flashesView()}
    <section className="page-heading"><div><span className="kicker">PLATFORM OVERVIEW</span><h1>Workspaces</h1><p>Review and manage company workspaces across Fieldnote.</p></div><div className="platform-total"><strong>${tenants.length}</strong><span>${search ? "MATCHING " : ""}WORKSPACE${tenants.length === 1 ? "" : "S"}</span></div></section>
    <section className="panel platform-list-panel"><div className="panel-heading platform-list-heading"><div><span className="kicker">DIRECTORY</span><h2>All workspaces</h2></div><form className="workspace-search" method="get"><label className="visually-hidden" htmlFor="workspace-search">Search workspaces</label><input id="workspace-search" name="q" defaultValue=${search} placeholder="Search name or slug" /><button type="submit" aria-label="Search workspaces">⌕</button>${search ? html`<a href="/platform-admin/" aria-label="Clear search">×</a>` : null}</form></div>
      ${tenants.length ? html`<div className="table-wrap"><table className="platform-table"><thead><tr><th>WORKSPACE</th><th>STAFF</th><th>CUSTOMERS</th><th>ORDERS</th><th>CREATED</th><th></th></tr></thead><tbody>${tenants.map((tenant) => html`<tr key=${tenant.id}><td><a className="workspace-name" href=${`/platform-admin/workspaces/${tenant.id}`}>${tenant.name}</a><span className="workspace-slug">${tenant.slug}</span></td><td>${user_counts[tenant.id] || 0}</td><td>${customer_counts[tenant.id] || 0}</td><td>${order_counts[tenant.id] || 0}</td><td>${dateLabel(tenant.created_at)}</td><td><a className="icon-action" href=${`/platform-admin/workspaces/${tenant.id}`} aria-label=${`Manage ${tenant.name}`} title="Manage workspace">↗</a></td></tr>`)}</tbody></table></div>` : html`<div className="empty-state"><span className="empty-icon">▦</span><strong>${search ? "No matching workspaces." : "No workspaces yet."}</strong><p>${search ? "Try another name or slug." : "New company registrations will appear here."}</p></div>`}
    </section>
    <footer className="client-footer"><span>FIELDNOTE PLATFORM ADMINISTRATION</span><span>Workspace removal permanently deletes its associated records.</span></footer>
  </main></div>`;
}

function PlatformWorkspace() {
  const { tenant, users, counts } = props;
  return html`<div className="platform-shell"><${PlatformHeader} /><main className="platform-content">${flashesView()}
    <a className="back-link platform-back" href="/platform-admin/">← All workspaces</a><section className="page-heading platform-detail-heading"><div><span className="kicker">WORKSPACE DETAILS · ${tenant.slug}</span><h1>${tenant.name}</h1><p>Created ${dateLabel(tenant.created_at, { month: "long", day: "2-digit", year: "numeric" })}${tenant.industry ? ` · ${tenant.industry}` : ""}</p></div><a className="button button-primary" href=${`/t/${tenant.slug}/login`} target="_blank" rel="noopener">Open staff sign in <span>↗</span></a></section>
    <div className="platform-detail-grid"><section className="panel platform-edit-panel"><div className="panel-heading"><div><span className="kicker">WORKSPACE PROFILE</span><h2>Edit details</h2></div></div><form className="form-stack platform-form" method="post" action=${`/platform-admin/workspaces/${tenant.id}/settings`}>${csrf()}<label>Company name<input name="name" defaultValue=${tenant.name} maxLength="150" required /></label><label>Industry<input name="industry" defaultValue=${tenant.industry || ""} maxLength="80" /></label><label>Address<input name="address" defaultValue=${tenant.address || ""} maxLength="255" /></label><div className="slug-note">Workspace slug <strong>${tenant.slug}</strong> cannot be changed here.</div><button className="button button-primary" type="submit">Save workspace details <span>↗</span></button></form></section>
      <section className="panel platform-data-panel"><div className="panel-heading"><div><span className="kicker">DATA INVENTORY</span><h2>Records in this workspace</h2></div></div><div className="inventory-list">${Object.entries(counts).map(([label, amount]) => html`<div key=${label}><span>${label}</span><strong>${amount}</strong></div>`)}</div></section>
    </div>
    <section className="panel platform-users-panel"><div className="panel-heading"><div><span className="kicker">ACCESS</span><h2>Staff accounts</h2></div><span className="activity-count">${users.length} ACCOUNT${users.length === 1 ? "" : "S"}</span></div>${users.length ? html`<div className="table-wrap"><table><thead><tr><th>USERNAME</th><th>EMAIL</th><th>ROLE</th><th>CREATED</th></tr></thead><tbody>${users.map((account) => html`<tr key=${account.id}><td><strong className="table-primary">${account.username}</strong></td><td>${account.email}</td><td>${account.role}</td><td>${dateLabel(account.created_at)}</td></tr>`)}</tbody></table></div>` : html`<div className="empty-state"><strong>No staff accounts.</strong></div>`}</section>
    <section className="panel danger-zone"><div><span className="kicker">IRREVERSIBLE ACTION</span><h2>Delete this workspace</h2><p>This permanently removes the workspace, all staff and customer accounts, and every record listed above. This cannot be undone.</p></div><form className="form-stack danger-form" method="post" action=${`/platform-admin/workspaces/${tenant.id}/delete`} onSubmit=${(event) => {
      if (!window.confirm(`Permanently delete ${tenant.name} and all its data? This cannot be undone.`)) event.preventDefault();
    }}>${csrf()}<label>Type <strong>${tenant.slug}</strong> to confirm<input name="confirmation" autoComplete="off" required /></label><label>Platform admin password<input type="password" name="admin_password" autoComplete="current-password" required /></label><button className="button danger-button" type="submit">Delete workspace permanently <span>×</span></button></form></section>
  </main></div>`;
}

const pages = {
  index: AuthLanding,
  login: () => html`<${LoginPage} />`,
  dashboard: Dashboard,
  resource: ResourcePage,
  invite_created: InviteCreated,
  invite_accept: InviteAccept,
  invite_invalid: InviteInvalid,
  client_login: () => html`<${LoginPage} portal=${true} />`,
  client_portal: ClientPortal,
  platform_login: PlatformLogin,
  platform_dashboard: PlatformDashboard,
  platform_workspace: PlatformWorkspace,
};

const Page = pages[page];
if (!Page) throw new Error(`Unknown Fieldnote page: ${page}`);
document.title = props.title || "Fieldnote";
createRoot(document.getElementById("root")).render(html`<${Page} />`);
