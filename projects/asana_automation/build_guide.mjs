import {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  HeadingLevel, AlignmentType, BorderStyle, WidthType, ShadingType,
  TableOfContents, Header, Footer, PageNumber, PageBreak,
  LevelFormat, ExternalHyperlink,
} from "docx";
import fs from "fs";

const OUT = "Automation101_Complete_Guide.docx";

// ── Helpers ───────────────────────────────────────────────────────────────────
const BRAND   = "2E4057";   // dark navy
const ACCENT  = "1B998B";   // teal
const LIGHT   = "F0F4F8";   // light grey fill
const WHITE   = "FFFFFF";
const BORDER  = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const BORDERS = { top: BORDER, bottom: BORDER, left: BORDER, right: BORDER };
const NO_BORDER = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const NO_BORDERS = { top: NO_BORDER, bottom: NO_BORDER, left: NO_BORDER, right: NO_BORDER };

function h(level, text, bookmark) {
  const map = {
    1: HeadingLevel.HEADING_1,
    2: HeadingLevel.HEADING_2,
    3: HeadingLevel.HEADING_3,
  };
  return new Paragraph({
    heading: map[level],
    spacing: { before: level === 1 ? 400 : 240, after: 160 },
    children: [new TextRun({ text, bold: level <= 2 })],
  });
}

function p(text, opts = {}) {
  return new Paragraph({
    spacing: { before: 80, after: 120 },
    ...opts,
    children: [new TextRun({ text, size: 22, ...opts.run })],
  });
}

function bullet(text, level = 0) {
  return new Paragraph({
    numbering: { reference: "bullets", level },
    spacing: { before: 60, after: 60 },
    children: [new TextRun({ text, size: 22 })],
  });
}

function numbered(text, level = 0) {
  return new Paragraph({
    numbering: { reference: "numbers", level },
    spacing: { before: 60, after: 60 },
    children: [new TextRun({ text, size: 22 })],
  });
}

function codeBlock(lines) {
  return lines.map(line =>
    new Paragraph({
      style: "CodeBlock",
      children: [new TextRun({ text: line, font: "Courier New", size: 18, color: "1A1A2E" })],
    })
  );
}

function spacer(n = 1) {
  return Array.from({ length: n }, () => new Paragraph({ children: [new TextRun("")] }));
}

function pageBreak() {
  return new Paragraph({ children: [new PageBreak()] });
}

function cell(text, opts = {}) {
  const { fill = WHITE, bold = false, width = 2340 } = opts;
  return new TableCell({
    borders: BORDERS,
    width: { size: width, type: WidthType.DXA },
    shading: { fill, type: ShadingType.CLEAR },
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    children: [new Paragraph({
      children: [new TextRun({ text, size: 18, bold, font: "Arial" })],
    })],
  });
}

function headerRow(cols, widths) {
  return new TableRow({
    tableHeader: true,
    children: cols.map((t, i) => cell(t, { fill: BRAND.replace(/^/, ""), bold: true, width: widths[i] })),
  });
}

// Override headerRow to use white text on dark background
function hdrRow(cols, widths) {
  return new TableRow({
    tableHeader: true,
    children: cols.map((t, i) =>
      new TableCell({
        borders: BORDERS,
        width: { size: widths[i], type: WidthType.DXA },
        shading: { fill: "2E4057", type: ShadingType.CLEAR },
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        children: [new Paragraph({
          children: [new TextRun({ text: t, size: 18, bold: true, color: "FFFFFF", font: "Arial" })],
        })],
      })
    ),
  });
}

function dataRow(cols, widths, shade = WHITE) {
  return new TableRow({
    children: cols.map((t, i) => cell(t, { fill: shade, width: widths[i] })),
  });
}

function sectionDivider() {
  return new Paragraph({
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: ACCENT, space: 1 } },
    spacing: { before: 0, after: 240 },
    children: [new TextRun("")],
  });
}

function label(text) {
  return new Paragraph({
    spacing: { before: 160, after: 60 },
    children: [new TextRun({ text, bold: true, size: 22, color: BRAND })],
  });
}

// ── Cover page ────────────────────────────────────────────────────────────────
const cover = [
  ...spacer(4),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 80 },
    children: [new TextRun({ text: "THE HEARTH & LOOM", size: 52, bold: true, color: BRAND, font: "Arial" })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 240 },
    children: [new TextRun({ text: "Automation 101", size: 40, color: ACCENT, font: "Arial" })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: ACCENT } },
    spacing: { before: 0, after: 320 },
    children: [new TextRun("")],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 120 },
    children: [new TextRun({ text: "Complete Guide: Asana Logic Mapping", size: 30, font: "Arial", color: "555555" })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 80 },
    children: [new TextRun({ text: "Order Fulfillment Automation Flow", size: 24, font: "Arial", color: "777777" })],
  }),
  ...spacer(2),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Shopify  →  Make.com  →  ShipStation  →  Klaviyo", size: 24, font: "Arial", color: ACCENT, italics: true })],
  }),
  ...spacer(6),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Prepared by: Operations Manager", size: 20, font: "Arial", color: "999999" })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Date: April 2026", size: 20, font: "Arial", color: "999999" })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Confidential — Internal Use", size: 20, font: "Arial", color: "AAAAAA", italics: true })],
  }),
  pageBreak(),
];

// ── TOC ───────────────────────────────────────────────────────────────────────
const toc = [
  h(1, "Table of Contents"),
  new TableOfContents("Table of Contents", { hyperlink: true, headingStyleRange: "1-2" }),
  pageBreak(),
];

// ── Section 1 ─────────────────────────────────────────────────────────────────
const sec1 = [
  h(1, "Section 1 — Introduction and Context"),
  sectionDivider(),

  h(2, "1.1 About The Hearth & Loom"),
  p("The Hearth & Loom is a direct-to-consumer (DTC) e-commerce brand that specializes in subscription craft weaving kits. Every month, subscribers receive a curated box with premium materials, exclusive patterns and step-by-step instructions for making unique textile pieces at home."),
  p("The business runs on monthly and annual subscriptions, which produce a steady, predictable volume of orders that must be processed and shipped accurately. Because the products are handmade, the post-purchase experience —including shipping communication and package tracking— is key to keeping customers."),

  h(2, "1.2 Goal of the Automation 101 Project"),
  p("The Automation 101 project in Asana is not a conventional task-management board. Its purpose is to act as a living visual repository of the company's automation tech stack, specifically the flow that connects Shopify with ShipStation."),
  p("Each card on the board represents one discrete logical step in the automation flow. The operations team can check this board to understand, in real time, how data flows from the moment an order is paid until the customer receives their shipping confirmation."),
  p("Key benefits:"),
  bullet("Full visibility of the flow without opening Make.com or ShipStation"),
  bullet("Centralized documentation the whole team can access"),
  bullet("Quick identification of critical vs. secondary steps"),
  bullet("A starting point for onboarding new operations team members"),

  h(2, "1.3 Full Project Requirements"),
  p("These are all the requirements the project must meet:"),
  ...spacer(1),

  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [3000, 6360],
    rows: [
      hdrRow(["Requirement", "Specification"], [3000, 6360]),
      dataRow(["Project view", "Board View (Kanban board)"], [3000, 6360]),
      dataRow(["Sections", "Exactly 4: 1. Trigger, 2. Action, 3. Test, 4. Live"], [3000, 6360], LIGHT),
      dataRow(["Number of tasks", "At least 15 (this project includes 18)"], [3000, 6360]),
      dataRow(["Custom Fields", "3 fields: Tool Source, Logic Type, Step Priority"], [3000, 6360], LIGHT),
      dataRow(["Native rule", "1 rule: on move to Live → change priority + comment"], [3000, 6360]),
      dataRow(["Descriptions", "Every task has explicit Success Criteria"], [3000, 6360], LIGHT),
      dataRow(["Public access", "Shareable link with 'Anyone with the link can view' permission"], [3000, 6360]),
    ],
  }),
  pageBreak(),
];

// ── Section 2 ─────────────────────────────────────────────────────────────────
const sec2 = [
  h(1, "Section 2 — Prerequisites and Setup"),
  sectionDivider(),

  h(2, "2.1 Generate the Asana Personal Access Token (PAT)"),
  p("The PAT is the credential that lets the Python script authenticate with the Asana API on your behalf. It works like your password for automated calls."),
  label("Steps to generate the PAT:"),
  numbered("Sign in to your Asana account at app.asana.com"),
  numbered("Click your profile picture (top-right corner)"),
  numbered("Select 'My Settings'"),
  numbered("Go to the 'Apps' tab"),
  numbered("Scroll to the 'Developer Apps' section and click '+ New access token'"),
  numbered("Name it: Automation 101 Script"),
  numbered("Accept the terms and click 'Create token'"),
  numbered("IMPORTANT: Copy the token right away — it is only shown once"),
  ...spacer(1),
  p("The token looks like this:"),
  ...codeBlock(["1/1234567890123:abcdef1234567890abcdef1234567890abcdef12"]),

  h(2, "2.2 Get the Workspace GID"),
  p("The Workspace GID is the unique numeric ID of your Asana workspace. The script needs it to know which workspace to create the project in."),
  label("How to get it:"),
  numbered("While signed in to Asana in your browser, open a new tab"),
  numbered("Go to this URL:"),
  ...codeBlock(["https://app.asana.com/api/1.0/workspaces"]),
  numbered("The browser shows a JSON response like this one:"),
  ...codeBlock([
    '{',
    '  "data": [',
    '    {',
    '      "gid": "123456789012345",    <-- This is your Workspace GID',
    '      "name": "The Hearth & Loom",',
    '      "resource_type": "workspace"',
    '    }',
    '  ]',
    '}',
  ]),
  numbered("Copy the value of the 'gid' field (just the numbers)"),

  h(2, "2.3 Installing Dependencies"),
  p("The script needs the Python 'requests' library. Run this command in your terminal:"),
  ...codeBlock(["pip install requests"]),
  p("To check that the installation worked:"),
  ...codeBlock(["python -c \"import requests; print(requests.__version__)\""]),

  h(2, "2.4 Setting Environment Variables"),
  p("Instead of writing your token directly in the code (an unsafe practice), set environment variables for your operating system:"),
  label("Windows — Command Prompt (CMD):"),
  ...codeBlock([
    "set ASANA_PAT=your_token_here",
    "set ASANA_WORKSPACE_GID=your_gid_here",
  ]),
  label("Windows — PowerShell:"),
  ...codeBlock([
    '$env:ASANA_PAT="your_token_here"',
    '$env:ASANA_WORKSPACE_GID="your_gid_here"',
  ]),
  label("macOS / Linux:"),
  ...codeBlock([
    'export ASANA_PAT="your_token_here"',
    'export ASANA_WORKSPACE_GID="your_gid_here"',
  ]),
  label("To check that the variables are set:"),
  ...codeBlock([
    "# CMD",
    "echo %ASANA_PAT%",
    "",
    "# PowerShell",
    "echo $env:ASANA_PAT",
    "",
    "# macOS/Linux",
    "echo $ASANA_PAT",
  ]),
  pageBreak(),
];

// ── Section 3 ─────────────────────────────────────────────────────────────────
const sec3 = [
  h(1, "Section 3 — Automation Flow Architecture"),
  sectionDivider(),

  h(2, "3.1 Full Flow Diagram"),
  ...codeBlock([
    "┌─────────────────────────────────────────────────────────────┐",
    "│                      AUTOMATION FLOW                        │",
    "│                    The Hearth & Loom                        │",
    "└─────────────────────────────────────────────────────────────┘",
    "",
    "  [Shopify: Order Paid]  ←── Customer completes payment",
    "          │",
    "          │  HMAC-signed webhook",
    "          ▼",
    "  [Make.com: Receive & Validate Webhook]",
    "          │",
    "          │  Contains a SKU with the WKIT- prefix?",
    "          ├── NO ──► HALT (no action)",
    "          │",
    "          │  YES",
    "          ▼",
    "  [Make.com: Filter Domestic vs. International]",
    "          ├── INTL ──► Manual Review Queue",
    "          │",
    "          │  DOMESTIC",
    "          ▼",
    "  [Make.com: Map Fields → ShipStation Schema]",
    "          │",
    "          ▼",
    "  [ShipStation: Create Shipment Order]",
    "          │",
    "          ▼",
    "  [ShipStation: Create Shipping Label]",
    "          │",
    "          │  tracking_number",
    "          ▼",
    "  [Make.com: Parse Tracking Number]",
    "          │",
    "    ┌──────┼──────────┐",
    "    ▼      ▼          ▼",
    "[Shopify  [Klaviyo   [Google Sheets",
    "Fulfill]  Email]     Log Result]",
  ]),

  h(2, "3.2 The 4 Board Sections"),
  ...spacer(1),

  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [1800, 2200, 5360],
    rows: [
      hdrRow(["Section", "Role", "What it holds"], [1800, 2200, 5360]),
      dataRow(["1. Trigger", "Entry point", "Events that start the automation: Shopify webhook, HMAC validation, Make.com receiver module, initial log in Sheets"], [1800, 2200, 5360]),
      dataRow(["2. Action", "Processing and output", "SKU and region filters, field mapping, ShipStation order and label creation, Klaviyo email, Shopify update"], [1800, 2200, 5360], LIGHT),
      dataRow(["3. Test", "Validation and errors", "Duplicate guard, ShipStation error handler, result log in Google Sheets, internal alerts"], [1800, 2200, 5360]),
      dataRow(["4. Live", "Confirmed in production", "Steps verified as live in production: scenario ON, Klaviyo flow Live, ShipStation store connected"], [1800, 2200, 5360], LIGHT),
    ],
  }),
  pageBreak(),
];

// ── Section 4 — Full code ──────────────────────────────────────────────────────
// Embed the real script so the guide always matches the code
const codeLines = fs.readFileSync("asana_board_setup.py", "utf8").replace(/\r\n/g, "\n").split("\n");

const sec4 = [
  h(1, "Section 4 — Full Python Script"),
  sectionDivider(),
  p("The following script creates the whole Asana project automatically. Each block is commented to explain what it does."),
  ...spacer(1),
  ...codeBlock(codeLines),
  pageBreak(),
];

// ── Section 5 ─────────────────────────────────────────────────────────────────
const sec5 = [
  h(1, "Section 5 — Running It Step by Step"),
  sectionDivider(),

  h(2, "5.1 How to run the script"),
  ...codeBlock([
    "# 1. Set the environment variables (PowerShell)",
    '$env:ASANA_PAT="1/your_full_token_here"',
    '$env:ASANA_WORKSPACE_GID="123456789012345"',
    "",
    "# 2. Go to the project folder",
    "cd algorithms-and-data-structures_\\projects\\asana_automation",
    "",
    "# 3. Run the script",
    "python asana_board_setup.py",
  ]),

  h(2, "5.2 Expected output while it runs"),
  ...codeBlock([
    "Creating project…",
    "  ✓ Project GID: 1234567890123456",
    "Creating custom fields…",
    "  ✓ Custom fields created",
    "  ✓ Custom fields attached to project",
    "Creating sections…",
    "  ✓ Sections: ['1. Trigger', '2. Action', '3. Test', '4. Live']",
    "Creating 18 tasks…",
    "  ✓ [1. Trigger] Shopify: New Order Paid",
    "  ✓ [1. Trigger] Shopify: Webhook Authentication",
    "  ✓ [1. Trigger] Make.com: Receive Webhook Module",
    "  ✓ [1. Trigger] Google Sheets: Log Raw Order Event",
    "  ✓ [2. Action] Filter: Subscription Kit SKU",
    "  ... (continues for all 18 tasks)",
    "Enabling public link…",
    "  ✓ Project set to public",
    "",
    "  PROJECT URL  →  https://app.asana.com/0/1234567890123456/list",
  ]),

  h(2, "5.3 Estimated run time"),
  p("The script includes deliberate pauses (time.sleep) to respect the Asana API rate limit (50 requests/minute on the Free plan, 1,500/minute on Business)."),
  ...spacer(1),
  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [3000, 2000, 4360],
    rows: [
      hdrRow(["Step", "Requests", "Approx. time"], [3000, 2000, 4360]),
      dataRow(["Create project", "1", "~1 sec"], [3000, 2000, 4360]),
      dataRow(["Create 3 custom fields", "3", "~3 sec"], [3000, 2000, 4360], LIGHT),
      dataRow(["Attach fields to the project", "3", "~3 sec"], [3000, 2000, 4360]),
      dataRow(["Resolve option GIDs", "10", "~5 sec"], [3000, 2000, 4360], LIGHT),
      dataRow(["Create 4 sections", "4 + 1.2s sleep", "~5 sec"], [3000, 2000, 4360]),
      dataRow(["Create 18 tasks", "18 + 7.2s sleep", "~25 sec"], [3000, 2000, 4360], LIGHT),
      dataRow(["Enable public link", "1", "~1 sec"], [3000, 2000, 4360]),
      dataRow(["TOTAL", "40 requests", "~45 seconds"], [3000, 2000, 4360]),
    ],
  }),
  pageBreak(),
];

// ── Section 6 ─────────────────────────────────────────────────────────────────
function taskTable(rows) {
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2600, 1400, 1600, 1200, 2560],
    rows: [
      hdrRow(["Task", "Tool Source", "Logic Type", "Priority", "Success Criteria"], [2600, 1400, 1600, 1200, 2560]),
      ...rows.map((r, i) => dataRow(r, [2600, 1400, 1600, 1200, 2560], i % 2 === 0 ? WHITE : LIGHT)),
    ],
  });
}

const sec6 = [
  h(1, "Section 6 — All 18 Tasks in Detail"),
  sectionDivider(),

  h(2, "6.1 Section: 1. Trigger (4 tasks)"),
  p("This section captures the initial event that starts the whole flow. Without a well-defined trigger, the automation can't start reliably."),
  taskTable([
    ["Shopify: New Order Paid", "Shopify", "Data Input", "Critical", "Fires only on order_paid webhook; no other payment states trigger the flow"],
    ["Shopify: Webhook Authentication", "Shopify", "Data Input", "Critical", "HMAC signature validated before any downstream step; invalid signatures rejected silently"],
    ["Make.com: Receive Webhook Module", "Make.com", "Data Input", "Critical", "Instant trigger mode; all Shopify payload fields captured (order ID, line items, customer, address)"],
    ["Google Sheets: Log Raw Order Event", "Google Sheets", "Data Input", "Secondary", "New row appended to 'Raw Events' tab within 30 seconds; includes timestamp and order ID"],
  ]),
  ...spacer(1),

  h(2, "6.2 Section: 2. Action (8 tasks)"),
  p("The core of the flow. These steps process the order data, make routing decisions, create the shipping label and notify the customer and internal systems."),
  taskTable([
    ["Filter: Subscription Kit SKU", "Make.com", "Condition/Filter", "Critical", "Only SKUs with prefix WKIT- pass through; all others halt without error"],
    ["Filter: Domestic vs. International", "Make.com", "Condition/Filter", "Secondary", "US addresses → standard ShipStation flow; international → manual review queue"],
    ["Make.com: Map Order Fields to ShipStation Schema", "Make.com", "Data Input", "Critical", "All required ShipStation fields populated correctly before create-label call"],
    ["ShipStation: Create Shipment Order", "ShipStation", "Output Action", "Critical", "HTTP 200 returned with valid shipment ID; shipment appears in Awaiting Shipment queue"],
    ["ShipStation: Create Shipping Label", "ShipStation", "Output Action", "Critical", "USPS/UPS label PDF generated; tracking number returned in API response"],
    ["Make.com: Parse Tracking Number", "Make.com", "Data Input", "Critical", "Tracking number extracted from ShipStation response and stored in Make.com variable"],
    ["Klaviyo: Send Shipping Confirmation", "Klaviyo", "Output Action", "Critical", "Order Shipped flow triggered with email, order ID, tracking; delivers within 5 minutes"],
    ["Shopify: Update Order Fulfillment Status", "Shopify", "Output Action", "Critical", "Order transitions unfulfilled → fulfilled; tracking visible on customer order status page"],
  ]),
  ...spacer(1),

  h(2, "6.3 Section: 3. Test (3 tasks)"),
  p("The safety and observability layer. It handles errors, prevents duplicates and makes sure every run is logged."),
  taskTable([
    ["Google Sheets: Log Fulfillment Result", "Google Sheets", "Output Action", "Secondary", "New row with order ID, tracking number, carrier, service, and UTC timestamp in Fulfillments tab"],
    ["Make.com: Error Handler — ShipStation Failure", "Make.com", "Condition/Filter", "Secondary", "Non-200 from ShipStation → logs payload to Errors tab + sends Slack internal alert"],
    ["Filter: Duplicate Order Guard", "Make.com", "Condition/Filter", "Secondary", "Checks Google Sheet for existing row with same Shopify order ID; duplicates skip label creation"],
  ]),
  ...spacer(1),

  h(2, "6.4 Section: 4. Live (3 tasks)"),
  p("A record of the steps that have been verified and confirmed as live in production."),
  taskTable([
    ["Make.com: Scenario Set to Active", "Make.com", "Data Input", "Critical", "Scenario toggled ON; no consecutive errors in scenario history for the last 7 days"],
    ["Klaviyo: Production Flow Published", "Klaviyo", "Output Action", "Critical", "Order Shipped flow status is Live; A/B test variant disabled for initial release"],
    ["ShipStation: Production Store Connected", "ShipStation", "Output Action", "Critical", "Shopify store connected in production mode; at least one successful label printed"],
  ]),
  pageBreak(),
];

// ── Section 7 ─────────────────────────────────────────────────────────────────
const sec7 = [
  h(1, "Section 7 — Custom Field Setup"),
  sectionDivider(),

  h(2, "7.1 Tool Source"),
  p("Identifies which tool in the tech stack is responsible for that logical step."),
  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2000, 2000, 5360],
    rows: [
      hdrRow(["Property", "Value", "Description"], [2000, 2000, 5360]),
      dataRow(["Type", "Dropdown (Enum)", "Single choice from a predefined list"], [2000, 2000, 5360]),
      dataRow(["Options", "Shopify", "E-commerce and order management platform"], [2000, 2000, 5360], LIGHT),
      dataRow(["", "ShipStation", "Shipping and label management platform"], [2000, 2000, 5360]),
      dataRow(["", "Make.com", "Automation platform (formerly Integromat)"], [2000, 2000, 5360], LIGHT),
      dataRow(["", "Klaviyo", "Email marketing and automated flows platform"], [2000, 2000, 5360]),
      dataRow(["", "Google Sheets", "Spreadsheet for logging and audits"], [2000, 2000, 5360], LIGHT),
    ],
  }),
  ...spacer(1),

  h(2, "7.2 Logic Type"),
  p("Classifies the kind of logical operation each step performs in the flow."),
  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2000, 2360, 5000],
    rows: [
      hdrRow(["Property", "Option", "When it's used"], [2000, 2360, 5000]),
      dataRow(["Type", "Data Input", "The step receives or captures outside data (webhooks, API reads)"], [2000, 2360, 5000]),
      dataRow(["", "Condition/Filter", "The step evaluates a condition and decides whether the flow continues or branches"], [2000, 2360, 5000], LIGHT),
      dataRow(["", "Output Action", "The step writes, sends or updates data in an external system"], [2000, 2360, 5000]),
    ],
  }),
  ...spacer(1),

  h(2, "7.3 Step Priority"),
  p("Shows how critical the step is for the production flow to work correctly."),
  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2000, 2000, 5360],
    rows: [
      hdrRow(["Option", "Meaning", "Impact if it fails"], [2000, 2000, 5360]),
      dataRow(["Critical", "Essential to the flow", "The order isn't fulfilled; needs immediate attention"], [2000, 2000, 5360]),
      dataRow(["Secondary", "Important but not blocking", "The order is fulfilled, but observability or a notification is lost"], [2000, 2000, 5360], LIGHT),
    ],
  }),
  ...spacer(1),

  h(2, "7.4 API call to create a Custom Field"),
  ...codeBlock([
    "POST https://app.asana.com/api/1.0/custom_fields",
    "",
    "Body:",
    "{",
    '  "data": {',
    '    "workspace": "WORKSPACE_GID",',
    '    "name": "Tool Source",',
    '    "resource_subtype": "enum",',
    '    "enum_options": [',
    '      {"name": "Shopify",       "enabled": true},',
    '      {"name": "ShipStation",   "enabled": true},',
    '      {"name": "Make.com",      "enabled": true},',
    '      {"name": "Klaviyo",       "enabled": true},',
    '      {"name": "Google Sheets", "enabled": true}',
    "    ]",
    "  }",
    "}",
    "",
    "Response:",
    "{",
    '  "data": {',
    '    "gid": "1234567890123456",',
    '    "name": "Tool Source",',
    '    "resource_subtype": "enum",',
    '    "enum_options": [',
    '      {"gid": "111111111111", "name": "Shopify", ...},',
    '      ...',
    "    ]",
    "  }",
    "}",
  ]),
  pageBreak(),
];

// ── Section 8 ─────────────────────────────────────────────────────────────────
const sec8 = [
  h(1, "Section 8 — Setting Up the Native Asana Rule"),
  sectionDivider(),
  p("The Asana REST API doesn't expose Rule creation programmatically (on most plans it's only available in the web interface). That's why this setup is done by hand, following these exact steps:"),
  ...spacer(1),

  h(2, "8.1 Opening the Rules settings"),
  numbered("Open your Automation 101 project in Asana"),
  numbered("Click the gear icon (Project settings) in the top-right corner"),
  numbered("In the side menu, select the 'Rules' tab"),
  numbered("Click the blue '+ Add Rule' button (top-right corner)"),

  h(2, "8.2 Set up the Trigger"),
  numbered("In the 'When...' section, click the trigger field"),
  numbered("Select: 'Task is moved to a section'"),
  numbered("In the section dropdown, select: '4. Live'"),
  p("The trigger will read: 'When a task is moved into 4. Live'"),

  h(2, "8.3 Set up the First Action"),
  numbered("In the 'Do...' section, click '+ Add action'"),
  numbered("Select: 'Set a custom field'"),
  numbered("In 'Field', select: Step Priority"),
  numbered("In 'Value', select: Critical"),

  h(2, "8.4 Set up the Second Action"),
  numbered("Click '+ Add action' again"),
  numbered("Select: 'Add a comment to the task'"),
  numbered("In the comment text field, type exactly:"),
  ...codeBlock(["This logic step is now live in production."]),

  h(2, "8.5 Save and Test the Rule"),
  numbered("Name it: Mark as Critical When Live"),
  numbered("Click 'Save rule'"),
  numbered("To test it: move any test task to the '4. Live' section"),
  numbered("Confirm that the Step Priority field changes to 'Critical' automatically"),
  numbered("Confirm that this comment appears: 'This logic step is now live in production.'"),
  ...spacer(1),

  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2000, 7360],
    rows: [
      hdrRow(["Component", "Configured value"], [2000, 7360]),
      dataRow(["Rule name", "Mark as Critical When Live"], [2000, 7360]),
      dataRow(["Trigger", "Task is moved into section: '4. Live'"], [2000, 7360], LIGHT),
      dataRow(["Action 1", "Set custom field: Step Priority = Critical"], [2000, 7360]),
      dataRow(["Action 2", "Add comment: 'This logic step is now live in production.'"], [2000, 7360], LIGHT),
    ],
  }),
  pageBreak(),
];

// ── Section 9 ─────────────────────────────────────────────────────────────────
const sec9 = [
  h(1, "Section 9 — Public Link and Screenshots"),
  sectionDivider(),

  h(2, "9.1 Set up the Public Link"),
  numbered("In the project, click the gear icon → 'Project Settings'"),
  numbered("Select the 'Sharing & Permissions' tab"),
  numbered("In the 'Public link' section, turn on 'Anyone with the link can view'"),
  numbered("Copy the generated link — this is the link you hand in"),
  p("Note: The script already sets public: True through the API, but the specific shareable link is generated in the UI."),

  h(2, "9.2 Required Screenshots"),
  ...spacer(1),

  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2000, 3000, 4360],
    rows: [
      hdrRow(["Screenshot", "Required view", "What it must show"], [2000, 3000, 4360]),
      dataRow(["Screenshot 1", "Board View", "All 4 columns with every task and the 3 custom fields as badges on each card"], [2000, 3000, 4360]),
      dataRow(["Screenshot 2", "List View", "List sorted by section with the Tool Source, Logic Type and Step Priority columns visible"], [2000, 3000, 4360], LIGHT),
      dataRow(["Screenshot 3", "Rules Builder", "The configured rule showing the trigger (moved to 4. Live) and both actions"], [2000, 3000, 4360]),
    ],
  }),
  ...spacer(1),

  h(2, "9.3 Showing Custom Fields in Board View"),
  numbered("In Board view, click 'Customize' (top-right corner)"),
  numbered("In the 'Fields' section, turn on the 3 custom fields so they show on the cards"),
  numbered("The fields appear as colored chips on each card"),

  h(2, "9.4 Showing Custom Fields in List View"),
  numbered("Switch to List view with the view selector (list icon)"),
  numbered("Click the '+' button after the last column to add fields"),
  numbered("Select Tool Source, Logic Type and Step Priority"),
  numbered("Sort by 'Section' to keep the logical grouping"),
  pageBreak(),
];

// ── Section 10 ────────────────────────────────────────────────────────────────
const sec10 = [
  h(1, "Section 10 — Troubleshooting"),
  sectionDivider(),

  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2200, 2000, 5160],
    rows: [
      hdrRow(["Error", "Likely cause", "Fix"], [2200, 2000, 5160]),
      dataRow(["401 Unauthorized", "Wrong or expired PAT", "Generate a new token in Asana → Apps. Make sure no spaces were copied."], [2200, 2000, 5160]),
      dataRow(["404 Not Found", "Wrong Workspace GID", "Visit app.asana.com/api/1.0/workspaces and copy the correct GID."], [2200, 2000, 5160], LIGHT),
      dataRow(["429 Too Many Requests", "Rate limit exceeded", "Raise the time.sleep() values to 1.0 or more. The Free plan allows 50 req/min."], [2200, 2000, 5160]),
      dataRow(["ValueError: Option not found", "Typo in an option name", "Check the exact capitalization: 'Data Input' not 'data input', 'Make.com' not 'make.com'."], [2200, 2000, 5160], LIGHT),
      dataRow(["Sections in the wrong order", "Array was reordered", "The array order in the script sets the column order. Don't reorder it."], [2200, 2000, 5160]),
      dataRow(["Custom field missing on tasks", "Field not attached", "Check that addCustomFieldSetting ran for every field GID."], [2200, 2000, 5160], LIGHT),
      dataRow(["Rule doesn't fire", "Wrong section in the rule", "Check that the section name in the Rule matches exactly: '4. Live'"], [2200, 2000, 5160]),
    ],
  }),
  pageBreak(),
];

// ── Section 11 ────────────────────────────────────────────────────────────────
const GLOSSARY = [
  ["Webhook", "An HTTP notification one system sends to another automatically when an event happens. Shopify sends a webhook when an order is paid."],
  ["HMAC", "Hash-based Message Authentication Code. A cryptographic signature that proves the webhook really came from Shopify and wasn't altered."],
  ["GID", "Global ID. The unique ID Asana assigns to each resource (project, task, field). It's always a numeric string."],
  ["PAT", "Personal Access Token. An authentication credential that lets external apps act on behalf of an Asana user."],
  ["Board View", "Asana's Kanban board view, where tasks are organized as cards in columns (sections)."],
  ["Custom Field", "A custom field that extends a task's properties beyond name, description and date."],
  ["Enum", "A closed-choice field type (dropdown). The value must be one of the predefined options."],
  ["Rule / Automation", "A native Asana automation that runs actions when a trigger condition is met."],
  ["Fulfillment", "The process of preparing and shipping an order to the customer. It includes creating the label, updating the status and notifying."],
  ["SKU", "Stock Keeping Unit. A unique code that identifies a specific product. At The Hearth & Loom, kits use the WKIT- prefix."],
  ["DTC", "Direct-to-Consumer. A business model where the brand sells straight to the consumer with no middlemen."],
  ["Rate Limit", "A limit on API calls within a time period. The Asana API allows 50 requests/minute on the Free plan."],
];

const sec11 = [
  h(1, "Section 11 — Technical Glossary"),
  sectionDivider(),
  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2000, 7360],
    rows: [
      hdrRow(["Term", "Definition"], [2000, 7360]),
      ...GLOSSARY.map(([t, d], i) => dataRow([t, d], [2000, 7360], i % 2 === 0 ? WHITE : LIGHT)),
    ],
  }),
  pageBreak(),
];

// ── Section 12 ────────────────────────────────────────────────────────────────
const CHECKS = [
  "The 'Automation 101' project exists in Asana in Board view",
  "There are exactly 4 sections: 1. Trigger, 2. Action, 3. Test, 4. Live",
  "The project has 18 logically distributed tasks (minimum required: 15)",
  "Every task has a Success Criteria description in the 'Notes' field",
  "The 'Tool Source' custom field exists with 5 options and is filled in on every task",
  "The 'Logic Type' custom field exists with 3 options and is filled in on every task",
  "The 'Step Priority' custom field exists with 2 options and is filled in on every task",
  "All 3 custom fields are visible in the project's list view",
  "The native Rule is set up with the trigger: moved to '4. Live'",
  "The Rule includes Action 1: Set Step Priority = Critical",
  "The Rule includes Action 2: Add comment 'This logic step is now live in production.'",
  "The Rule was tested by moving a test task to section 4. Live",
  "The project is set to public (Anyone with the link can view)",
  "The project's shareable link was copied and saved",
  "A screenshot of Board View with the custom fields visible was taken",
  "A screenshot of List View with the custom field columns was taken",
  "A screenshot of the Rules Builder showing the full setup was taken",
  "The project, section and task names follow consistent, professional conventions",
];

const sec12 = [
  h(1, "Section 12 — Acceptance Criteria and Final Checklist"),
  sectionDivider(),
  p("Use this list to check that every project requirement is met before you hand it in:"),
  ...spacer(1),
  ...CHECKS.map(text =>
    new Paragraph({
      numbering: { reference: "checklist", level: 0 },
      spacing: { before: 80, after: 80 },
      children: [new TextRun({ text, size: 22 })],
    })
  ),
  ...spacer(2),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    border: {
      top: { style: BorderStyle.SINGLE, size: 4, color: ACCENT, space: 1 },
      bottom: { style: BorderStyle.SINGLE, size: 4, color: ACCENT, space: 1 },
    },
    spacing: { before: 240, after: 240 },
    children: [new TextRun({
      text: "Once every item is checked, the project is ready to hand in.",
      size: 22, bold: true, color: BRAND, font: "Arial",
    })],
  }),
];

// ── Build document ────────────────────────────────────────────────────────────
const doc = new Document({
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "\u2022",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } },
        }],
      },
      {
        reference: "numbers",
        levels: [{
          level: 0, format: LevelFormat.DECIMAL, text: "%1.",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } },
        }],
      },
      {
        reference: "checklist",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "\u25A1",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } },
        }],
      },
    ],
  },
  styles: {
    default: {
      document: { run: { font: "Arial", size: 22, color: "333333" } },
    },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, font: "Arial", color: BRAND },
        paragraph: { spacing: { before: 480, after: 200 }, outlineLevel: 0 },
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial", color: ACCENT },
        paragraph: { spacing: { before: 320, after: 160 }, outlineLevel: 1 },
      },
      {
        id: "CodeBlock", name: "Code Block", basedOn: "Normal", next: "Normal",
        run: { font: "Courier New", size: 18, color: "1A1A2E" },
        paragraph: {
          spacing: { before: 60, after: 60, line: 276 },
          shading: { fill: "F5F5F5", type: ShadingType.CLEAR },
          indent: { left: 360 },
        },
      },
    ],
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
      },
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          children: [
            new TextRun({ text: "The Hearth & Loom — Automation 101", size: 18, color: "999999", font: "Arial" }),
            new TextRun({ text: "\tPage ", size: 18, color: "999999", font: "Arial" }),
            new TextRun({ children: [PageNumber.CURRENT], size: 18, color: "999999", font: "Arial" }),
          ],
          tabStops: [{ type: "right", position: 9360 }],
          border: { bottom: { style: BorderStyle.SINGLE, size: 2, color: "DDDDDD", space: 1 } },
        })],
      }),
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          border: { top: { style: BorderStyle.SINGLE, size: 2, color: "DDDDDD", space: 1 } },
          children: [new TextRun({ text: "Confidential — Internal Use — The Hearth & Loom", size: 16, color: "AAAAAA", font: "Arial" })],
        })],
      }),
    },
    children: [
      ...cover,
      ...toc,
      ...sec1,
      ...sec2,
      ...sec3,
      ...sec4,
      ...sec5,
      ...sec6,
      ...sec7,
      ...sec8,
      ...sec9,
      ...sec10,
      ...sec11,
      ...sec12,
    ],
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(OUT, buf);
  console.log("OK →", OUT);
});
