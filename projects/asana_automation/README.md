# Asana Automation 101 — Logic Mapping Board

A Python script that builds a complete Asana board through the Asana REST API. The board documents an order fulfillment automation for a fictional DTC brand, *The Hearth & Loom*: Shopify → Make.com → ShipStation → Klaviyo.

Each card on the board is one logical step of the flow, tagged with three custom fields so the operations team can see what each step does and how critical it is.

## What the script creates

- A project in **Board view** with 4 sections: `1. Trigger`, `2. Action`, `3. Test`, `4. Live`
- 3 dropdown custom fields: **Tool Source**, **Logic Type** and **Step Priority**
- 18 tasks, each with explicit success criteria in its description
- Public sharing for the project

The native Asana rule (move to `4. Live` → set priority to Critical and add a comment) can't be created through the API, so the script prints the manual steps at the end.

## Requirements

- Python 3.9+
- `requests` (`pip install requests`)
- An Asana Personal Access Token and your workspace GID

## Usage

```bash
# PowerShell
$env:ASANA_PAT="1/your_token_here"
$env:ASANA_WORKSPACE_GID="123456789012345"

python asana_board_setup.py
```

The script respects the API rate limit with short pauses and takes about 45 seconds.

## Step-by-step guide (Word)

`build_guide.mjs` generates `Automation101_Complete_Guide.docx`, a 12-section guide covering setup, the flow architecture, the full script, every task, the custom fields, the manual rule, troubleshooting and a final checklist.

```bash
npm install
npm run build
```

## Files

```
asana_automation/
├── asana_board_setup.py             # Creates the board through the Asana API
├── build_guide.mjs                  # Generates the Word guide (docx library)
├── Automation101_Complete_Guide.docx
├── package.json
└── README.md
```

## Author

**Jordi Blanch**
