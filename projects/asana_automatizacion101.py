"""
Asana Logic Mapping: 'The Hearth & Loom' — Automatización 101
Creates the full board-view project via the Asana REST API.

Setup:
    pip install requests
    Set ASANA_PAT and ASANA_WORKSPACE_GID below (or as env vars).
"""

import os
import sys
import time
import requests

# ── Config ────────────────────────────────────────────────────────────────────
ASANA_PAT          = os.environ.get("ASANA_PAT", "PASTE_YOUR_PAT_HERE")
WORKSPACE_GID      = os.environ.get("ASANA_WORKSPACE_GID", "PASTE_YOUR_WORKSPACE_GID_HERE")
PROJECT_NAME       = "Automatización 101"
PROJECT_COLOR      = "light-orange"
# ──────────────────────────────────────────────────────────────────────────────

BASE = "https://app.asana.com/api/1.0"
HEADERS = {
    "Authorization": f"Bearer {ASANA_PAT}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}


def api(method: str, path: str, **kwargs):
    r = requests.request(method, f"{BASE}{path}", headers=HEADERS, **kwargs)
    if not r.ok:
        print(f"[ERROR] {method} {path} → {r.status_code}: {r.text}")
        sys.exit(1)
    return r.json().get("data", r.json())


# ── 1. Create project ─────────────────────────────────────────────────────────
print("Creating project…")
project = api("POST", "/projects", json={
    "data": {
        "name": PROJECT_NAME,
        "workspace": WORKSPACE_GID,
        "layout": "board",
        "color": PROJECT_COLOR,
        "public": True,
        "notes": (
            "Blueprint visual del flujo de automatización de cumplimiento de pedidos "
            "de The Hearth & Loom. Cada tarjeta representa un paso lógico de Shopify → ShipStation."
        ),
    }
})
project_gid = project["gid"]
print(f"  ✓ Project GID: {project_gid}")

# ── 2. Create custom fields ───────────────────────────────────────────────────
print("Creating custom fields…")

def create_enum_field(name: str, options: list[str], color="none") -> str:
    field = api("POST", "/custom_fields", json={
        "data": {
            "workspace": WORKSPACE_GID,
            "name": name,
            "resource_subtype": "enum",
            "enum_options": [{"name": o, "enabled": True, "color": color} for o in options],
        }
    })
    return field["gid"]

tool_source_gid = create_enum_field(
    "Tool Source",
    ["Shopify", "ShipStation", "Make.com", "Klaviyo", "Google Sheets"],
)
logic_type_gid = create_enum_field(
    "Logic Type",
    ["Data Input", "Condition/Filter", "Output Action"],
)
step_priority_gid = create_enum_field(
    "Step Priority",
    ["Critical", "Secondary"],
)
print("  ✓ Custom fields created")

# Attach custom fields to project
for gid in [tool_source_gid, logic_type_gid, step_priority_gid]:
    api("POST", f"/projects/{project_gid}/addCustomFieldSetting", json={
        "data": {"custom_field": gid, "is_important": True}
    })
print("  ✓ Custom fields attached to project")

# Helper: resolve enum option gid by name
def get_option_gid(field_gid: str, option_name: str) -> str:
    field_data = api("GET", f"/custom_fields/{field_gid}")
    for opt in field_data.get("enum_options", []):
        if opt["name"] == option_name:
            return opt["gid"]
    raise ValueError(f"Option '{option_name}' not found in field {field_gid}")

# Cache option GIDs
tool_opts  = {n: get_option_gid(tool_source_gid, n)  for n in ["Shopify", "ShipStation", "Make.com", "Klaviyo", "Google Sheets"]}
logic_opts = {n: get_option_gid(logic_type_gid, n)   for n in ["Data Input", "Condition/Filter", "Output Action"]}
prio_opts  = {n: get_option_gid(step_priority_gid, n) for n in ["Critical", "Secondary"]}

# ── 3. Create sections ────────────────────────────────────────────────────────
print("Creating sections…")
sections = {}
for name in ["1. Trigger", "2. Acción", "3. Prueba", "4. Activo"]:
    sec = api("POST", f"/projects/{project_gid}/sections", json={"data": {"name": name}})
    sections[name] = sec["gid"]
    time.sleep(0.3)
print("  ✓ Sections:", list(sections.keys()))

# ── 4. Task definitions ───────────────────────────────────────────────────────
# (section, name, description, tool, logic_type, priority)
TASKS = [
    # ── 1. Trigger
    (
        "1. Trigger",
        "Shopify: New Order Paid",
        "Success Criteria: The automation fires only when Shopify emits the 'order_paid' webhook event. "
        "No other payment states (pending, authorized) should trigger the flow.",
        "Shopify", "Data Input", "Critical",
    ),
    (
        "1. Trigger",
        "Shopify: Webhook Authentication",
        "Success Criteria: The incoming webhook HMAC signature is validated before any downstream step "
        "executes. Invalid signatures must be rejected silently.",
        "Shopify", "Data Input", "Critical",
    ),
    (
        "1. Trigger",
        "Make.com: Receive Webhook Module",
        "Success Criteria: Make.com scenario is set to 'instant' trigger mode and successfully "
        "captures all Shopify payload fields (order ID, line items, customer, shipping address).",
        "Make.com", "Data Input", "Critical",
    ),
    (
        "1. Trigger",
        "Google Sheets: Log Raw Order Event",
        "Success Criteria: Every triggered order is appended as a new row in the 'Raw Events' tab "
        "within 30 seconds of the webhook firing. Row includes timestamp and order ID.",
        "Google Sheets", "Data Input", "Secondary",
    ),

    # ── 2. Acción
    (
        "2. Acción",
        "Filter: Subscription Kit SKU",
        "Success Criteria: Only orders containing at least one line item with SKU prefix 'WKIT-' "
        "pass through. All other orders halt the scenario without error.",
        "Make.com", "Condition/Filter", "Critical",
    ),
    (
        "2. Acción",
        "Filter: Domestic vs. International Shipping",
        "Success Criteria: Orders with a US shipping address route to the standard ShipStation flow; "
        "international orders are diverted to a separate manual-review path.",
        "Make.com", "Condition/Filter", "Secondary",
    ),
    (
        "2. Acción",
        "Make.com: Map Order Fields to ShipStation Schema",
        "Success Criteria: All required ShipStation fields (recipient name, address, weight, "
        "dimensions, service code) are populated correctly before the create-label call.",
        "Make.com", "Data Input", "Critical",
    ),
    (
        "2. Acción",
        "ShipStation: Create Shipment Order",
        "Success Criteria: ShipStation returns HTTP 200 with a valid shipment ID. The shipment "
        "appears in the 'Awaiting Shipment' queue within ShipStation.",
        "ShipStation", "Output Action", "Critical",
    ),
    (
        "2. Acción",
        "ShipStation: Create Shipping Label",
        "Success Criteria: A USPS/UPS label PDF is generated and the tracking number is returned "
        "in the API response. Label must match the selected service level.",
        "ShipStation", "Output Action", "Critical",
    ),
    (
        "2. Acción",
        "Make.com: Parse Tracking Number from Response",
        "Success Criteria: The tracking number string is extracted from the ShipStation response "
        "and stored in a Make.com variable for downstream Klaviyo and Sheets steps.",
        "Make.com", "Data Input", "Critical",
    ),
    (
        "2. Acción",
        "Klaviyo: Send Shipping Confirmation",
        "Success Criteria: The 'Order Shipped' Klaviyo flow is triggered with the customer's email, "
        "order ID, and tracking number. Email delivers within 5 minutes of label creation.",
        "Klaviyo", "Output Action", "Critical",
    ),
    (
        "2. Acción",
        "Shopify: Update Order Fulfillment Status",
        "Success Criteria: The Shopify order transitions from 'unfulfilled' to 'fulfilled' and the "
        "tracking number is visible to the customer in their order status page.",
        "Shopify", "Output Action", "Critical",
    ),

    # ── 3. Prueba
    (
        "3. Prueba",
        "Google Sheets: Log Fulfillment Result",
        "Success Criteria: After a successful label creation, the 'Fulfillments' tab receives a new "
        "row with order ID, tracking number, carrier, service, and UTC timestamp.",
        "Google Sheets", "Output Action", "Secondary",
    ),
    (
        "3. Prueba",
        "Make.com: Error Handler — ShipStation Failure",
        "Success Criteria: If ShipStation returns a non-200 response, the error handler logs the "
        "payload to the 'Errors' Google Sheet tab and sends an internal Slack alert.",
        "Make.com", "Condition/Filter", "Secondary",
    ),
    (
        "3. Prueba",
        "Filter: Duplicate Order Guard",
        "Success Criteria: Before creating a ShipStation order, the scenario checks the Google Sheet "
        "for an existing row with the same Shopify order ID. Duplicates skip label creation.",
        "Make.com", "Condition/Filter", "Secondary",
    ),

    # ── 4. Activo
    (
        "4. Activo",
        "Make.com: Scenario Set to Active & Scheduled",
        "Success Criteria: The Make.com scenario is toggled ON and has no scheduling gaps. "
        "Scenario history shows no consecutive errors in the last 7 days.",
        "Make.com", "Data Input", "Critical",
    ),
    (
        "4. Activo",
        "Klaviyo: Production Flow Published",
        "Success Criteria: The 'Order Shipped' Klaviyo flow status is 'Live'. A/B test variant "
        "is disabled for the initial production release.",
        "Klaviyo", "Output Action", "Critical",
    ),
    (
        "4. Activo",
        "ShipStation: Production Store Connected",
        "Success Criteria: The Shopify store is connected to ShipStation in production mode (not "
        "sandbox). At least one successful label has been printed under the production credentials.",
        "ShipStation", "Output Action", "Critical",
    ),
]

# ── 5. Create tasks ───────────────────────────────────────────────────────────
print(f"Creating {len(TASKS)} tasks…")
for section_name, task_name, notes, tool, logic, priority in TASKS:
    section_gid = sections[section_name]
    task = api("POST", "/tasks", json={
        "data": {
            "name": task_name,
            "notes": notes,
            "projects": [project_gid],
            "memberships": [{"project": project_gid, "section": section_gid}],
            "custom_fields": {
                tool_source_gid:   tool_opts[tool],
                logic_type_gid:    logic_opts[logic],
                step_priority_gid: prio_opts[priority],
            },
        }
    })
    print(f"  ✓ [{section_name}] {task_name}")
    time.sleep(0.4)  # respect rate limits

# ── 6. Enable public sharing ──────────────────────────────────────────────────
print("Enabling public link…")
# Asana's REST API exposes public link via project settings
share = api("PUT", f"/projects/{project_gid}", json={
    "data": {"public": True}
})
print("  ✓ Project set to public")

# ── 7. Print shareable URL ────────────────────────────────────────────────────
project_url = f"https://app.asana.com/0/{project_gid}/list"
print("\n" + "═" * 60)
print(f"  PROJECT URL  →  {project_url}")
print("═" * 60)
print(
    "\nNext steps:\n"
    "  1. Open the URL above and verify all tasks + custom fields.\n"
    "  2. Go to Project Settings → Rules → Add Rule to configure\n"
    "     the native automation (see RULE_INSTRUCTIONS below).\n"
    "  3. Switch to Board view and take the required screenshots.\n"
    "  4. Copy the shareable link from Project Settings → Sharing.\n"
)
print("""
RULE_INSTRUCTIONS (manual step — Asana Rules API is workspace-plan-locked):
─────────────────────────────────────────────────────────────────────────────
Trigger : Task is moved to section  →  "4. Activo"
Action 1: Set custom field          →  Step Priority = "Critical"
Action 2: Add comment               →  "This logic step is now live in production."
─────────────────────────────────────────────────────────────────────────────
""")
