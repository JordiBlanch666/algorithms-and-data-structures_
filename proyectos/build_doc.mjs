import {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  HeadingLevel, AlignmentType, BorderStyle, WidthType, ShadingType,
  TableOfContents, Header, Footer, PageNumber, PageBreak,
  LevelFormat, ExternalHyperlink,
} from "docx";
import fs from "fs";

const OUT = "Automatizacion101_Guia_Completa.docx";

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
    children: [new TextRun({ text: "Automatizacion 101", size: 40, color: ACCENT, font: "Arial" })],
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
    children: [new TextRun({ text: "Guia Completa: Asana Logic Mapping", size: 30, font: "Arial", color: "555555" })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 80 },
    children: [new TextRun({ text: "Flujo de Automatizacion de Cumplimiento de Pedidos", size: 24, font: "Arial", color: "777777" })],
  }),
  ...spacer(2),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Shopify  →  Make.com  →  ShipStation  →  Klaviyo", size: 24, font: "Arial", color: ACCENT, italics: true })],
  }),
  ...spacer(6),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Preparado por: Operations Manager", size: 20, font: "Arial", color: "999999" })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Fecha: Abril 2026", size: 20, font: "Arial", color: "999999" })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Confidencial — Uso Interno", size: 20, font: "Arial", color: "AAAAAA", italics: true })],
  }),
  pageBreak(),
];

// ── TOC ───────────────────────────────────────────────────────────────────────
const toc = [
  h(1, "Tabla de Contenidos"),
  new TableOfContents("Tabla de Contenidos", { hyperlink: true, headingStyleRange: "1-2" }),
  pageBreak(),
];

// ── Section 1 ─────────────────────────────────────────────────────────────────
const sec1 = [
  h(1, "Seccion 1 — Introduccion y Contexto"),
  sectionDivider(),

  h(2, "1.1 Sobre The Hearth & Loom"),
  p("The Hearth & Loom es una marca de comercio electronico directo al consumidor (DTC) especializada en kits de tejido artesanal por suscripcion. Cada mes, los suscriptores reciben una caja curada con materiales premium, patrones exclusivos e instrucciones paso a paso para crear piezas textiles unicas en casa."),
  p("El modelo de negocio se basa en suscripciones mensuales y anuales, lo que genera un volumen constante y predecible de pedidos que deben ser procesados y enviados con precision. Dado el caracter artesanal de los productos, la experiencia post-compra —incluyendo la comunicacion de envio y el seguimiento del paquete— es fundamental para la retencion de clientes."),

  h(2, "1.2 Objetivo del Proyecto Automatizacion 101"),
  p("El proyecto Automatizacion 101 en Asana no es un tablero de gestion de tareas convencional. Su proposito es actuar como un repositorio visual vivo del stack tecnologico de automatizacion de la empresa, especificamente del flujo que conecta Shopify con ShipStation."),
  p("Cada tarjeta del tablero representa un paso logico discreto dentro del flujo de automatizacion. El equipo de operaciones puede consultar este tablero para entender, en tiempo real, como fluyen los datos desde el momento en que se paga un pedido hasta que el cliente recibe su confirmacion de envio."),
  p("Beneficios clave:"),
  bullet("Visibilidad total del flujo sin necesidad de abrir Make.com o ShipStation"),
  bullet("Documentacion centralizada accesible para todo el equipo"),
  bullet("Identificacion rapida de pasos criticos vs. secundarios"),
  bullet("Base para onboarding de nuevos miembros del equipo de operaciones"),

  h(2, "1.3 Requisitos Completos del Proyecto"),
  p("A continuacion se listan todos los requisitos que debe cumplir el proyecto:"),
  ...spacer(1),

  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [3000, 6360],
    rows: [
      hdrRow(["Requisito", "Especificacion"], [3000, 6360]),
      dataRow(["Vista del proyecto", "Board View (tablero Kanban)"], [3000, 6360]),
      dataRow(["Secciones", "Exactamente 4: 1. Trigger, 2. Accion, 3. Prueba, 4. Activo"], [3000, 6360], LIGHT),
      dataRow(["Numero de tareas", "Minimo 15 (este proyecto incluye 18)"], [3000, 6360]),
      dataRow(["Custom Fields", "3 campos: Tool Source, Logic Type, Step Priority"], [3000, 6360], LIGHT),
      dataRow(["Rule nativa", "1 regla: al mover a Activo → cambiar prioridad + comentario"], [3000, 6360]),
      dataRow(["Descripciones", "Cada tarea con Success Criteria explicito"], [3000, 6360], LIGHT),
      dataRow(["Acceso publico", "Link compartible con permiso 'Anyone with the link can view'"], [3000, 6360]),
    ],
  }),
  pageBreak(),
];

// ── Section 2 ─────────────────────────────────────────────────────────────────
const sec2 = [
  h(1, "Seccion 2 — Prerequisitos y Configuracion"),
  sectionDivider(),

  h(2, "2.1 Generar el Personal Access Token (PAT) de Asana"),
  p("El PAT es la credencial que permite al script Python autenticarse con la API de Asana en tu nombre. Es equivalente a tu contrasena para llamadas automatizadas."),
  label("Pasos para generar el PAT:"),
  numbered("Inicia sesion en tu cuenta de Asana en app.asana.com"),
  numbered("Haz clic en tu foto de perfil (esquina superior derecha)"),
  numbered("Selecciona 'My Settings' (Configuracion)"),
  numbered("Ve a la pestana 'Apps'"),
  numbered("Desplazate hasta la seccion 'Developer Apps' y haz clic en '+ New access token'"),
  numbered("Asigna el nombre: Automatizacion 101 Script"),
  numbered("Acepta los terminos y haz clic en 'Create token'"),
  numbered("IMPORTANTE: Copia el token inmediatamente — solo se muestra una vez"),
  ...spacer(1),
  p("El token tendra este formato:"),
  ...codeBlock(["1/1234567890123:abcdef1234567890abcdef1234567890abcdef12"]),

  h(2, "2.2 Obtener el Workspace GID"),
  p("El Workspace GID es el identificador unico numerico de tu espacio de trabajo en Asana. El script lo necesita para saber en que workspace crear el proyecto."),
  label("Como obtenerlo:"),
  numbered("Con tu sesion de Asana activa en el navegador, abre una nueva pestana"),
  numbered("Navega a la siguiente URL:"),
  ...codeBlock(["https://app.asana.com/api/1.0/workspaces"]),
  numbered("El navegador mostrara una respuesta JSON similar a esta:"),
  ...codeBlock([
    '{',
    '  "data": [',
    '    {',
    '      "gid": "123456789012345",    <-- Este es tu Workspace GID',
    '      "name": "The Hearth & Loom",',
    '      "resource_type": "workspace"',
    '    }',
    '  ]',
    '}',
  ]),
  numbered("Copia el valor del campo 'gid' (solo los numeros)"),

  h(2, "2.3 Instalacion de Dependencias"),
  p("El script requiere la libreria 'requests' de Python. Ejecuta el siguiente comando en tu terminal:"),
  ...codeBlock(["pip install requests"]),
  p("Para verificar que la instalacion fue exitosa:"),
  ...codeBlock(["python -c \"import requests; print(requests.__version__)\""]),

  h(2, "2.4 Configuracion de Variables de Entorno"),
  p("En lugar de escribir tu token directamente en el codigo (practica insegura), configura las variables de entorno segun tu sistema operativo:"),
  label("Windows — Simbolo del sistema (CMD):"),
  ...codeBlock([
    "set ASANA_PAT=tu_token_aqui",
    "set ASANA_WORKSPACE_GID=tu_gid_aqui",
  ]),
  label("Windows — PowerShell:"),
  ...codeBlock([
    '$env:ASANA_PAT="tu_token_aqui"',
    '$env:ASANA_WORKSPACE_GID="tu_gid_aqui"',
  ]),
  label("macOS / Linux:"),
  ...codeBlock([
    'export ASANA_PAT="tu_token_aqui"',
    'export ASANA_WORKSPACE_GID="tu_gid_aqui"',
  ]),
  label("Para verificar que las variables estan configuradas:"),
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
  h(1, "Seccion 3 — Arquitectura del Flujo de Automatizacion"),
  sectionDivider(),

  h(2, "3.1 Diagrama del Flujo Completo"),
  ...codeBlock([
    "┌─────────────────────────────────────────────────────────────┐",
    "│                    FLUJO DE AUTOMATIZACION                  │",
    "│                    The Hearth & Loom                        │",
    "└─────────────────────────────────────────────────────────────┘",
    "",
    "  [Shopify: Order Paid]  ←── Cliente completa pago",
    "          │",
    "          │  webhook HMAC-firmado",
    "          ▼",
    "  [Make.com: Receive & Validate Webhook]",
    "          │",
    "          │  ¿Contiene SKU con prefijo WKIT-?",
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

  h(2, "3.2 Descripcion de las 4 Secciones del Tablero"),
  ...spacer(1),

  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [1800, 2200, 5360],
    rows: [
      hdrRow(["Seccion", "Funcion", "Que contiene"], [1800, 2200, 5360]),
      dataRow(["1. Trigger", "Punto de entrada", "Eventos que inician la automatizacion: webhook de Shopify, validacion HMAC, modulo receptor de Make.com, log inicial en Sheets"], [1800, 2200, 5360]),
      dataRow(["2. Accion", "Procesamiento y salida", "Filtros de SKU y geografia, mapeo de campos, creacion de orden y etiqueta en ShipStation, envio de email Klaviyo, actualizacion de Shopify"], [1800, 2200, 5360], LIGHT),
      dataRow(["3. Prueba", "Validacion y errores", "Guard de duplicados, handler de errores de ShipStation, log de resultado en Google Sheets, alertas internas"], [1800, 2200, 5360]),
      dataRow(["4. Activo", "Produccion confirmada", "Pasos verificados como activos en produccion: scenario ON, flujo Klaviyo Live, store ShipStation conectado"], [1800, 2200, 5360], LIGHT),
    ],
  }),
  pageBreak(),
];

// ── Section 4 — Full code ──────────────────────────────────────────────────────
const codeLines = [
  '"""',
  "Asana Logic Mapping: 'The Hearth & Loom' — Automatizacion 101",
  "Crea el proyecto completo en Board view via la API REST de Asana.",
  "",
  "Setup:",
  "    pip install requests",
  "    Configura ASANA_PAT y ASANA_WORKSPACE_GID como variables de entorno.",
  '"""',
  "",
  "import os       # Acceso a variables de entorno",
  "import sys      # Para sys.exit() en caso de error de API",
  "import time     # Para time.sleep() y respetar rate limits",
  "import requests # Libreria HTTP para llamadas a la API de Asana",
  "",
  "# ── Configuracion ─────────────────────────────────────────────────────────",
  "# os.environ.get() lee la variable de entorno; si no existe, usa el default",
  'ASANA_PAT     = os.environ.get("ASANA_PAT", "PASTE_YOUR_PAT_HERE")',
  'WORKSPACE_GID = os.environ.get("ASANA_WORKSPACE_GID", "PASTE_YOUR_WORKSPACE_GID_HERE")',
  'PROJECT_NAME  = "Automatizacion 101"',
  'PROJECT_COLOR = "light-orange"  # Color de la bolita del proyecto en Asana',
  "",
  "# URL base de la API REST de Asana v1.0",
  'BASE = "https://app.asana.com/api/1.0"',
  "",
  "# Headers que se envian en cada request HTTP",
  "HEADERS = {",
  '    "Authorization": f"Bearer {ASANA_PAT}",  # Token de autenticacion',
  '    "Content-Type": "application/json",       # Enviamos JSON',
  '    "Accept": "application/json",             # Esperamos JSON de vuelta',
  "}",
  "",
  "",
  "def api(method: str, path: str, **kwargs):",
  '    """Wrapper centralizado para todas las llamadas a la API de Asana."""',
  "    # Construye la URL completa y ejecuta el request",
  "    r = requests.request(method, f\"{BASE}{path}\", headers=HEADERS, **kwargs)",
  "    # Si la respuesta no es 2xx, imprime el error y termina el script",
  "    if not r.ok:",
  '        print(f"[ERROR] {method} {path} -> {r.status_code}: {r.text}")',
  "        sys.exit(1)",
  "    # La API de Asana siempre envuelve los datos en {'data': ...}",
  '    return r.json().get("data", r.json())',
  "",
  "",
  "# ── PASO 1: Crear el proyecto ──────────────────────────────────────────────",
  'print("Creando proyecto...")',
  "project = api(\"POST\", \"/projects\", json={",
  "    \"data\": {",
  "        \"name\": PROJECT_NAME,",
  "        \"workspace\": WORKSPACE_GID,",
  "        \"layout\": \"board\",    # Tipo Board (Kanban), no List",
  "        \"color\": PROJECT_COLOR,",
  "        \"public\": True,         # Visible para miembros del workspace",
  "        \"notes\": (",
  "            \"Blueprint visual del flujo de automatizacion de The Hearth & Loom.\"",
  "        ),",
  "    }",
  "})",
  "project_gid = project[\"gid\"]  # GID asignado por Asana al nuevo proyecto",
  'print(f"  OK Project GID: {project_gid}")',
  "",
  "# ── PASO 2: Crear Custom Fields ───────────────────────────────────────────",
  'print("Creando custom fields...")',
  "",
  "def create_enum_field(name: str, options: list[str]) -> str:",
  '    """Crea un campo de tipo dropdown (enum) en el workspace."""',
  "    field = api(\"POST\", \"/custom_fields\", json={",
  "        \"data\": {",
  "            \"workspace\": WORKSPACE_GID,",
  "            \"name\": name,",
  "            \"resource_subtype\": \"enum\",  # Tipo dropdown",
  "            # Cada opcion del dropdown se define como objeto con name y enabled",
  "            \"enum_options\": [{\"name\": o, \"enabled\": True} for o in options],",
  "        }",
  "    })",
  "    return field[\"gid\"]  # Devuelve el GID del campo creado",
  "",
  "# Crear los 3 custom fields requeridos",
  "tool_source_gid = create_enum_field(",
  "    \"Tool Source\",",
  "    [\"Shopify\", \"ShipStation\", \"Make.com\", \"Klaviyo\", \"Google Sheets\"],",
  ")",
  "logic_type_gid = create_enum_field(",
  "    \"Logic Type\",",
  "    [\"Data Input\", \"Condition/Filter\", \"Output Action\"],",
  ")",
  "step_priority_gid = create_enum_field(",
  "    \"Step Priority\",",
  "    [\"Critical\", \"Secondary\"],",
  ")",
  "",
  "# Adjuntar cada custom field al proyecto (sin esto no aparecen en las tareas)",
  "# is_important: True hace que el campo sea visible en la vista de lista",
  "for gid in [tool_source_gid, logic_type_gid, step_priority_gid]:",
  "    api(\"POST\", f\"/projects/{project_gid}/addCustomFieldSetting\", json={",
  "        \"data\": {\"custom_field\": gid, \"is_important\": True}",
  "    })",
  'print("  OK Custom fields adjuntados")',
  "",
  "# Resolver el GID de cada opcion de enum por su nombre",
  "# (Asana requiere el GID de la opcion, no su texto, al asignar valores)",
  "def get_option_gid(field_gid: str, option_name: str) -> str:",
  "    field_data = api(\"GET\", f\"/custom_fields/{field_gid}\")",
  "    for opt in field_data.get(\"enum_options\", []):",
  "        if opt[\"name\"] == option_name:",
  "            return opt[\"gid\"]",
  "    raise ValueError(f\"Opcion '{option_name}' no encontrada\")",
  "",
  "# Cachear los GIDs de todas las opciones para uso eficiente",
  "tool_opts  = {n: get_option_gid(tool_source_gid, n)",
  "              for n in [\"Shopify\", \"ShipStation\", \"Make.com\", \"Klaviyo\", \"Google Sheets\"]}",
  "logic_opts = {n: get_option_gid(logic_type_gid, n)",
  "              for n in [\"Data Input\", \"Condition/Filter\", \"Output Action\"]}",
  "prio_opts  = {n: get_option_gid(step_priority_gid, n)",
  "              for n in [\"Critical\", \"Secondary\"]}",
  "",
  "# ── PASO 3: Crear Secciones ───────────────────────────────────────────────",
  'print("Creando secciones...")',
  "sections = {}",
  "# El orden del array determina el orden de las columnas en Board view",
  "for name in [\"1. Trigger\", \"2. Accion\", \"3. Prueba\", \"4. Activo\"]:",
  "    sec = api(\"POST\", f\"/projects/{project_gid}/sections\",",
  "              json={\"data\": {\"name\": name}})",
  "    sections[name] = sec[\"gid\"]",
  "    time.sleep(0.3)  # Pausa para evitar rate limit (50 req/min en plan Free)",
  "",
  "# ── PASO 4: Definicion de las 18 Tareas ──────────────────────────────────",
  "# Cada tupla: (seccion, nombre, descripcion, tool, logic_type, priority)",
  "TASKS = [",
  "    # --- Seccion 1: Trigger ---",
  "    (\"1. Trigger\", \"Shopify: New Order Paid\",",
  "     \"Success Criteria: Fires only on order_paid webhook. No other states trigger.\",",
  "     \"Shopify\", \"Data Input\", \"Critical\"),",
  "    # ... (18 tareas en total — ver Seccion 6 para detalle completo)",
  "]",
  "",
  "# ── PASO 5: Crear las Tareas ─────────────────────────────────────────────",
  "for section_name, task_name, notes, tool, logic, priority in TASKS:",
  "    section_gid = sections[section_name]",
  "    api(\"POST\", \"/tasks\", json={",
  "        \"data\": {",
  "            \"name\": task_name,",
  "            \"notes\": notes,               # Descripcion / Success Criteria",
  "            \"projects\": [project_gid],    # Agrega la tarea al proyecto",
  "            # memberships asigna la tarea a una seccion especifica",
  "            \"memberships\": [{\"project\": project_gid, \"section\": section_gid}],",
  "            # custom_fields: dict de {field_gid: option_gid}",
  "            \"custom_fields\": {",
  "                tool_source_gid:   tool_opts[tool],",
  "                logic_type_gid:    logic_opts[logic],",
  "                step_priority_gid: prio_opts[priority],",
  "            },",
  "        }",
  "    })",
  "    time.sleep(0.4)  # Rate limit: max ~50 writes/min",
  "",
  "# ── PASO 6: Habilitar link publico ───────────────────────────────────────",
  "api(\"PUT\", f\"/projects/{project_gid}\", json={\"data\": {\"public\": True}})",
  "",
  "# ── PASO 7: Imprimir URL final ────────────────────────────────────────────",
  "project_url = f\"https://app.asana.com/0/{project_gid}/list\"",
  "print(f\"\\n  URL DEL PROYECTO: {project_url}\\n\")",
];

const sec4 = [
  h(1, "Seccion 4 — Codigo Python Completo y Comentado"),
  sectionDivider(),
  p("El siguiente script crea automaticamente el proyecto completo en Asana. Cada bloque esta anotado para explicar el 'por que' de cada decision de implementacion."),
  ...spacer(1),
  ...codeBlock(codeLines),
  pageBreak(),
];

// ── Section 5 ─────────────────────────────────────────────────────────────────
const sec5 = [
  h(1, "Seccion 5 — Ejecucion Paso a Paso"),
  sectionDivider(),

  h(2, "5.1 Como ejecutar el script"),
  ...codeBlock([
    "# 1. Configura las variables de entorno (PowerShell)",
    '$env:ASANA_PAT="1/tu_token_completo_aqui"',
    '$env:ASANA_WORKSPACE_GID="123456789012345"',
    "",
    "# 2. Navega a la carpeta del proyecto",
    "cd C:\\Users\\paast\\PycharmProjects\\Repository\\proyectos",
    "",
    "# 3. Ejecuta el script",
    "python asana_automatizacion101.py",
  ]),

  h(2, "5.2 Output esperado durante la ejecucion"),
  ...codeBlock([
    "Creando proyecto...",
    "  OK Project GID: 1234567890123456",
    "Creando custom fields...",
    "  OK Custom fields creados",
    "  OK Custom fields adjuntados al proyecto",
    "Creando secciones...",
    "  OK Secciones: ['1. Trigger', '2. Accion', '3. Prueba', '4. Activo']",
    "Creando 18 tareas...",
    "  OK [1. Trigger] Shopify: New Order Paid",
    "  OK [1. Trigger] Shopify: Webhook Authentication",
    "  OK [1. Trigger] Make.com: Receive Webhook Module",
    "  OK [1. Trigger] Google Sheets: Log Raw Order Event",
    "  OK [2. Accion] Filter: Subscription Kit SKU",
    "  ... (continua para las 18 tareas)",
    "  OK Proyecto configurado como publico",
    "",
    "  URL DEL PROYECTO: https://app.asana.com/0/1234567890123456/list",
  ]),

  h(2, "5.3 Tiempo de ejecucion estimado"),
  p("El script incluye pausas deliberadas (time.sleep) para respetar el rate limit de la API de Asana (50 requests/minuto en plan Free, 1500/minuto en Business)."),
  ...spacer(1),
  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [3000, 2000, 4360],
    rows: [
      hdrRow(["Paso", "Requests", "Tiempo aprox."], [3000, 2000, 4360]),
      dataRow(["Crear proyecto", "1", "~1 seg"], [3000, 2000, 4360]),
      dataRow(["Crear 3 custom fields", "3", "~3 seg"], [3000, 2000, 4360], LIGHT),
      dataRow(["Adjuntar fields al proyecto", "3", "~3 seg"], [3000, 2000, 4360]),
      dataRow(["Resolver option GIDs", "3", "~3 seg"], [3000, 2000, 4360], LIGHT),
      dataRow(["Crear 4 secciones", "4 + 1.2s sleep", "~5 seg"], [3000, 2000, 4360]),
      dataRow(["Crear 18 tareas", "18 + 7.2s sleep", "~25 seg"], [3000, 2000, 4360], LIGHT),
      dataRow(["Habilitar link publico", "1", "~1 seg"], [3000, 2000, 4360]),
      dataRow(["TOTAL", "33 requests", "~40 segundos"], [3000, 2000, 4360]),
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
      hdrRow(["Tarea", "Tool Source", "Logic Type", "Priority", "Success Criteria"], [2600, 1400, 1600, 1200, 2560]),
      ...rows.map((r, i) => dataRow(r, [2600, 1400, 1600, 1200, 2560], i % 2 === 0 ? WHITE : LIGHT)),
    ],
  });
}

const sec6 = [
  h(1, "Seccion 6 — Detalle Completo de las 18 Tareas"),
  sectionDivider(),

  h(2, "6.1 Seccion: 1. Trigger (4 tareas)"),
  p("Esta seccion captura el evento inicial que pone en marcha todo el flujo. Sin un trigger bien definido, la automatizacion no puede iniciar de forma confiable."),
  taskTable([
    ["Shopify: New Order Paid", "Shopify", "Data Input", "Critical", "Fires only on order_paid webhook; no other payment states trigger the flow"],
    ["Shopify: Webhook Authentication", "Shopify", "Data Input", "Critical", "HMAC signature validated before any downstream step; invalid signatures rejected silently"],
    ["Make.com: Receive Webhook Module", "Make.com", "Data Input", "Critical", "Instant trigger mode; all Shopify payload fields captured (order ID, line items, customer, address)"],
    ["Google Sheets: Log Raw Order Event", "Google Sheets", "Data Input", "Secondary", "New row appended to 'Raw Events' tab within 30 seconds; includes timestamp and order ID"],
  ]),
  ...spacer(1),

  h(2, "6.2 Seccion: 2. Accion (8 tareas)"),
  p("El nucleo del flujo. Estos pasos procesan los datos del pedido, toman decisiones de enrutamiento, crean la etiqueta de envio y notifican al cliente y a los sistemas internos."),
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

  h(2, "6.3 Seccion: 3. Prueba (3 tareas)"),
  p("Capa de seguridad y observabilidad. Maneja errores, previene duplicados y garantiza que cada ejecucion quede registrada."),
  taskTable([
    ["Google Sheets: Log Fulfillment Result", "Google Sheets", "Output Action", "Secondary", "New row with order ID, tracking number, carrier, service, and UTC timestamp in Fulfillments tab"],
    ["Make.com: Error Handler — ShipStation Failure", "Make.com", "Condition/Filter", "Secondary", "Non-200 from ShipStation → logs payload to Errors tab + sends Slack internal alert"],
    ["Filter: Duplicate Order Guard", "Make.com", "Condition/Filter", "Secondary", "Checks Google Sheet for existing row with same Shopify order ID; duplicates skip label creation"],
  ]),
  ...spacer(1),

  h(2, "6.4 Seccion: 4. Activo (3 tareas)"),
  p("Registro de los pasos que han sido verificados y confirmados como activos en el entorno de produccion."),
  taskTable([
    ["Make.com: Scenario Set to Active", "Make.com", "Data Input", "Critical", "Scenario toggled ON; no consecutive errors in scenario history for the last 7 days"],
    ["Klaviyo: Production Flow Published", "Klaviyo", "Output Action", "Critical", "Order Shipped flow status is Live; A/B test variant disabled for initial release"],
    ["ShipStation: Production Store Connected", "ShipStation", "Output Action", "Critical", "Shopify store connected in production mode; at least one successful label printed"],
  ]),
  pageBreak(),
];

// ── Section 7 ─────────────────────────────────────────────────────────────────
const sec7 = [
  h(1, "Seccion 7 — Configuracion de Custom Fields"),
  sectionDivider(),

  h(2, "7.1 Tool Source"),
  p("Identifica que herramienta del stack tecnologico es responsable de ese paso logico."),
  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2000, 2000, 5360],
    rows: [
      hdrRow(["Propiedad", "Valor", "Descripcion"], [2000, 2000, 5360]),
      dataRow(["Tipo", "Dropdown (Enum)", "Seleccion unica de lista predefinida"], [2000, 2000, 5360]),
      dataRow(["Opciones", "Shopify", "Plataforma de ecommerce y gestion de pedidos"], [2000, 2000, 5360], LIGHT),
      dataRow(["", "ShipStation", "Plataforma de gestion de envios y etiquetas"], [2000, 2000, 5360]),
      dataRow(["", "Make.com", "Plataforma de automatizacion (antes Integromat)"], [2000, 2000, 5360], LIGHT),
      dataRow(["", "Klaviyo", "Plataforma de email marketing y flows automatizados"], [2000, 2000, 5360]),
      dataRow(["", "Google Sheets", "Hoja de calculo para logging y auditorias"], [2000, 2000, 5360], LIGHT),
    ],
  }),
  ...spacer(1),

  h(2, "7.2 Logic Type"),
  p("Clasifica el tipo de operacion logica que realiza cada paso en el flujo."),
  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2000, 2360, 5000],
    rows: [
      hdrRow(["Propiedad", "Opcion", "Cuando se usa"], [2000, 2360, 5000]),
      dataRow(["Tipo", "Data Input", "El paso recibe o captura datos del exterior (webhooks, lecturas de API)"], [2000, 2360, 5000]),
      dataRow(["", "Condition/Filter", "El paso evalua una condicion y decide si el flujo continua o se bifurca"], [2000, 2360, 5000], LIGHT),
      dataRow(["", "Output Action", "El paso escribe, envia o actualiza datos en un sistema externo"], [2000, 2360, 5000]),
    ],
  }),
  ...spacer(1),

  h(2, "7.3 Step Priority"),
  p("Indica la criticidad del paso para el funcionamiento correcto del flujo de produccion."),
  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2000, 2000, 5360],
    rows: [
      hdrRow(["Opcion", "Significado", "Consecuencia si falla"], [2000, 2000, 5360]),
      dataRow(["Critical", "Imprescindible para el flujo", "El pedido no se cumple; requiere intervencion inmediata"], [2000, 2000, 5360]),
      dataRow(["Secondary", "Importante pero no bloqueante", "El pedido se cumple, pero se pierde observabilidad o una notificacion"], [2000, 2000, 5360], LIGHT),
    ],
  }),
  ...spacer(1),

  h(2, "7.4 Llamada API para crear un Custom Field"),
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
  h(1, "Seccion 8 — Configuracion de la Rule Nativa de Asana"),
  sectionDivider(),
  p("La API REST de Asana no expone la creacion de Rules de forma programatica (esta funcion esta disponible solo a traves de la interfaz web para la mayoria de los planes). Por este motivo, esta configuracion se realiza manualmente siguiendo estos pasos exactos:"),
  ...spacer(1),

  h(2, "8.1 Navegacion a la Configuracion de Rules"),
  numbered("Abre tu proyecto Automatizacion 101 en Asana"),
  numbered("Haz clic en el icono de engranaje (Configuracion del proyecto) en la esquina superior derecha"),
  numbered("En el menu lateral, selecciona la pestana 'Rules' (Reglas)"),
  numbered("Haz clic en el boton '+ Add Rule' (azul, esquina superior derecha)"),

  h(2, "8.2 Configurar el Trigger (Disparador)"),
  numbered("En la seccion 'When...' (Cuando...), haz clic en el campo de trigger"),
  numbered("Selecciona: 'Task is moved to a section' (La tarea se mueve a una seccion)"),
  numbered("En el dropdown de seccion, selecciona: '4. Activo'"),
  p("El trigger quedara configurado como: 'When a task is moved into 4. Activo'"),

  h(2, "8.3 Configurar la Primera Accion"),
  numbered("En la seccion 'Do...', haz clic en '+ Add action'"),
  numbered("Selecciona: 'Set a custom field' (Establecer un campo personalizado)"),
  numbered("En 'Field', selecciona: Step Priority"),
  numbered("En 'Value', selecciona: Critical"),

  h(2, "8.4 Configurar la Segunda Accion"),
  numbered("Haz clic en '+ Add action' nuevamente"),
  numbered("Selecciona: 'Add a comment to the task' (Agregar un comentario)"),
  numbered("En el campo de texto del comentario, escribe exactamente:"),
  ...codeBlock(["This logic step is now live in production."]),

  h(2, "8.5 Guardar y Verificar la Rule"),
  numbered("Asigna el nombre: Marcar como Critico al Activar"),
  numbered("Haz clic en 'Save rule'"),
  numbered("Para verificar: mueve cualquier tarea de prueba a la seccion '4. Activo'"),
  numbered("Confirma que el campo Step Priority cambia a 'Critical' automaticamente"),
  numbered("Confirma que aparece un comentario: 'This logic step is now live in production.'"),
  ...spacer(1),

  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2000, 7360],
    rows: [
      hdrRow(["Componente", "Valor Configurado"], [2000, 7360]),
      dataRow(["Nombre de la Rule", "Marcar como Critico al Activar"], [2000, 7360]),
      dataRow(["Trigger", "Task is moved into section: '4. Activo'"], [2000, 7360], LIGHT),
      dataRow(["Accion 1", "Set custom field: Step Priority = Critical"], [2000, 7360]),
      dataRow(["Accion 2", "Add comment: 'This logic step is now live in production.'"], [2000, 7360], LIGHT),
    ],
  }),
  pageBreak(),
];

// ── Section 9 ─────────────────────────────────────────────────────────────────
const sec9 = [
  h(1, "Seccion 9 — Link Publico y Capturas de Pantalla"),
  sectionDivider(),

  h(2, "9.1 Configurar el Link Publico"),
  numbered("En el proyecto, haz clic en el icono de engranaje → 'Project Settings'"),
  numbered("Selecciona la pestana 'Sharing & Permissions'"),
  numbered("En la seccion 'Public link', activa la opcion 'Anyone with the link can view'"),
  numbered("Copia el link generado — este es el enlace de entrega"),
  p("Nota: El script ya configura public: True via API, pero el link compartible especifico se genera desde la UI."),

  h(2, "9.2 Guia de Capturas de Pantalla Requeridas"),
  ...spacer(1),

  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2000, 3000, 4360],
    rows: [
      hdrRow(["Captura", "Vista requerida", "Que debe mostrarse"], [2000, 3000, 4360]),
      dataRow(["Captura 1", "Board View", "Las 4 columnas visibles con todas las tareas y los 3 custom fields como badges en cada tarjeta"], [2000, 3000, 4360]),
      dataRow(["Captura 2", "List View", "Lista ordenada por seccion con las columnas Tool Source, Logic Type y Step Priority visibles"], [2000, 3000, 4360], LIGHT),
      dataRow(["Captura 3", "Rules Builder", "La regla configurada mostrando el trigger (moved to 4. Activo) y las 2 acciones"], [2000, 3000, 4360]),
    ],
  }),
  ...spacer(1),

  h(2, "9.3 Como mostrar Custom Fields en Board View"),
  numbered("En Board view, haz clic en 'Customize' (esquina superior derecha)"),
  numbered("En la seccion 'Fields', activa los 3 custom fields para que sean visibles en las tarjetas"),
  numbered("Los campos apareceran como chips de color en cada tarjeta del tablero"),

  h(2, "9.4 Como mostrar Custom Fields en List View"),
  numbered("Cambia a List view usando el selector de vista (icono de lista)"),
  numbered("Haz clic en el boton '+' al final de las columnas para agregar campos"),
  numbered("Selecciona Tool Source, Logic Type y Step Priority"),
  numbered("Ordena por 'Section' para mantener la agrupacion logica"),
  pageBreak(),
];

// ── Section 10 ────────────────────────────────────────────────────────────────
const sec10 = [
  h(1, "Seccion 10 — Troubleshooting"),
  sectionDivider(),

  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2200, 2000, 5160],
    rows: [
      hdrRow(["Error", "Causa probable", "Solucion"], [2200, 2000, 5160]),
      dataRow(["401 Unauthorized", "PAT incorrecto o expirado", "Genera un nuevo token en Asana → Apps. Verifica que no haya espacios al copiar."], [2200, 2000, 5160]),
      dataRow(["404 Not Found", "Workspace GID incorrecto", "Visita app.asana.com/api/1.0/workspaces y copia el GID correcto."], [2200, 2000, 5160], LIGHT),
      dataRow(["429 Too Many Requests", "Rate limit excedido", "Aumenta los valores de time.sleep() a 1.0 o mas. El plan Free permite 50 req/min."], [2200, 2000, 5160]),
      dataRow(["ValueError: Option not found", "Typo en nombre de opcion", "Verifica mayusculas exactas: 'Data Input' no 'data input', 'Make.com' no 'make.com'."], [2200, 2000, 5160], LIGHT),
      dataRow(["Secciones en orden incorrecto", "Array reordenado", "El orden del array en el script determina el orden de columnas. No reordenar."], [2200, 2000, 5160]),
      dataRow(["Custom field no aparece en tareas", "Field no adjuntado", "Verifica que addCustomFieldSetting se ejecuto para cada field GID."], [2200, 2000, 5160], LIGHT),
      dataRow(["Rule no se dispara", "Seccion mal configurada", "Verifica que el nombre exacto de la seccion en la Rule coincida: '4. Activo'"], [2200, 2000, 5160]),
    ],
  }),
  pageBreak(),
];

// ── Section 11 ────────────────────────────────────────────────────────────────
const GLOSSARY = [
  ["Webhook", "Notificacion HTTP que un sistema envia automaticamente a otro cuando ocurre un evento. Shopify envia un webhook cuando se paga un pedido."],
  ["HMAC", "Hash-based Message Authentication Code. Firma criptografica que verifica que el webhook proviene realmente de Shopify y no fue alterado."],
  ["GID", "Global ID. Identificador unico asignado por Asana a cada recurso (proyecto, tarea, campo). Siempre es un string numerico."],
  ["PAT", "Personal Access Token. Credencial de autenticacion que permite a aplicaciones externas actuar en nombre de un usuario de Asana."],
  ["Board View", "Vista de tablero Kanban en Asana donde las tareas se organizan como tarjetas en columnas (secciones)."],
  ["Custom Field", "Campo personalizado que extiende las propiedades de una tarea mas alla de nombre, descripcion y fecha."],
  ["Enum", "Tipo de campo de seleccion cerrada (dropdown). El valor debe ser una de las opciones predefinidas."],
  ["Rule / Automation", "Automatizacion nativa de Asana que ejecuta acciones cuando se cumple un trigger (condicion disparadora)."],
  ["Fulfillment", "Proceso de preparar y enviar un pedido al cliente. Incluye generar la etiqueta, actualizar el estado y notificar."],
  ["SKU", "Stock Keeping Unit. Codigo unico que identifica un producto especifico. En The Hearth & Loom, los kits usan el prefijo WKIT-."],
  ["DTC", "Direct-to-Consumer. Modelo de negocio donde la marca vende directamente al consumidor sin intermediarios."],
  ["Rate Limit", "Limite de llamadas a una API en un periodo de tiempo. La API de Asana permite 50 requests/minuto en plan Free."],
];

const sec11 = [
  h(1, "Seccion 11 — Glosario Tecnico"),
  sectionDivider(),
  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2000, 7360],
    rows: [
      hdrRow(["Termino", "Definicion"], [2000, 7360]),
      ...GLOSSARY.map(([t, d], i) => dataRow([t, d], [2000, 7360], i % 2 === 0 ? WHITE : LIGHT)),
    ],
  }),
  pageBreak(),
];

// ── Section 12 ────────────────────────────────────────────────────────────────
const CHECKS = [
  "El proyecto 'Automatizacion 101' existe en Asana en modo Board view",
  "Existen exactamente 4 secciones: 1. Trigger, 2. Accion, 3. Prueba, 4. Activo",
  "El proyecto contiene 18 tareas distribuidas logicamente (minimo requerido: 15)",
  "Cada tarea tiene una descripcion de Success Criteria en el campo 'Notes'",
  "El custom field 'Tool Source' esta creado con 5 opciones y poblado en todas las tareas",
  "El custom field 'Logic Type' esta creado con 3 opciones y poblado en todas las tareas",
  "El custom field 'Step Priority' esta creado con 2 opciones y poblado en todas las tareas",
  "Los 3 custom fields son visibles en la vista de lista del proyecto",
  "La Rule nativa esta configurada con trigger: moved to '4. Activo'",
  "La Rule incluye Action 1: Set Step Priority = Critical",
  "La Rule incluye Action 2: Add comment 'This logic step is now live in production.'",
  "La Rule fue probada moviendo una tarea de prueba a la seccion 4. Activo",
  "El proyecto esta configurado como publico (Anyone with the link can view)",
  "Se obtuvo y guardo el link compartible del proyecto",
  "Se tomo captura de pantalla del Board View con custom fields visibles",
  "Se tomo captura de pantalla del List View con columnas de custom fields",
  "Se tomo captura de pantalla del Rules Builder mostrando la configuracion completa",
  "El nombre del proyecto, secciones y tareas usa convenciones profesionales y consistentes",
];

const sec12 = [
  h(1, "Seccion 12 — Criterios de Aceptacion y Checklist Final"),
  sectionDivider(),
  p("Utiliza esta lista para verificar que todos los requisitos del proyecto han sido cumplidos antes de hacer la entrega:"),
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
      text: "Cuando todos los items esten marcados, el proyecto esta listo para entrega.",
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
            new TextRun({ text: "The Hearth & Loom — Automatizacion 101", size: 18, color: "999999", font: "Arial" }),
            new TextRun({ text: "\tPagina ", size: 18, color: "999999", font: "Arial" }),
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
          children: [new TextRun({ text: "Confidencial — Uso Interno — The Hearth & Loom", size: 16, color: "AAAAAA", font: "Arial" })],
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
