# PLANNING.md

> Prompt to AI: **“Use the structure and decisions outlined in PLANNING.md.”**
> Context: Proyecto open‑source, local‑first, para auditar sitios web a través de un **servidor MCP** que expone herramientas de rendimiento, SEO, accesibilidad, seguridad y responsividad para asistentes de codificación.

## 1. Visión y Objetivos

* **Visión:** Un **MCP único y local** que permita a cualquier agente de codificación ejecutar auditorías web de extremo a extremo sin depender de APIs de pago.
* **Objetivos principales:**

  1. Exponer tools MCP coherentes (inputs/outputs JSON) para **Lighthouse**, **axe+Playwright**, **webhint**, **security headers**, **ZAP Baseline** y **responsive audit**.
  2. Ejecutar **offline/local** (excepto cuando el usuario opte por herramientas remotas).
  3. Entregar **reportes unificados** (JSON/HTML) con puntajes y recomendaciones.
  4. Diseñar contratos estables para que otros puedan **reusar/extender** el MCP.
* **No-objetivos (por ahora):** CI/CD, integración con Jules, crawling a gran escala, SAST completo, visual-diff avanzado (opcional futuro).

## 2. Alcance inicial

* URLs únicas o lista pequeña de URLs dadas por el usuario.
* Dispositivos: **mobile** y **desktop** (perfiles predefinidos).
* Análisis incluidos: Performance, SEO, Best Practices, **A11y (WCAG)**, **Headers de seguridad**, **DAST pasivo** (ZAP baseline), **heurísticas de responsividad** (overflow/tap targets) y **screenshots**.

## 3. Arquitectura

### 3.1 Diagrama lógico (texto)

**Clientes/Agentes AI** ⇄ **MCP Server (Python FastMCP)** ⇄ **Runners Node** ⇄ Navegadores (Playwright/Chromium) & Docker(ZAP)

### 3.2 Componentes

* **Servidor MCP (Python + FastMCP)**

  * Expone tools: `audit_lighthouse`, `scan_axe`, `scan_wave`, `webhint_scan`, `security_headers`, `responsive_audit`, `zap_baseline`, `report_merge`, `cdp_*` (Chrome DevTools).
  * Orquesta procesos, consolida resultados y aplica budgets.
  * **Modo de transporte**: STDIO (recomendado, estable), HTTP (en desarrollo).
* **Runners Node**

  * Scripts finos: `axe-playwright.js`, `security-headers.js`, `responsive.js`.
  * Dependencias: `lighthouse` (npx auto-install), `playwright`, `@axe-core/playwright`, `hint`.
* **Docker (opcional)**: `owasp/zap2docker-stable` para `zap_baseline`.

## 4. Stack técnico y dependencias

* **Lenguaje principal del MCP:** Python **3.12+** (FastMCP 2.12.3).
* **Runners:** Node **22+** con Playwright/axe/Lighthouse/webhint.
* **SO objetivo:** Linux/macOS/Windows (x86_64/ARM64; Playwright soportado).
* **Gestión de entornos:** venv + npm. Scripts: `quick-start.sh`, `quick-start.ps1`.

## 5. Contratos de Tools (I/O)

> Todos los tools usan **JSON** y devuelven **status/ok** o error con mensaje claro.

* **audit_lighthouse(url, device)** → `{categoryScores:{performance,accessibility,seo,bestPractices}, audits:{...}, raw:LH_JSON}`
* **scan_axe(url, device)** → `{violations:[...], passes:[...], incomplete:[...], raw:AXE_JSON}`
* **webhint_scan(url)** → `{hints:[{hintId,severity,message,resource}], raw:WEBHINT_JSON}`
* **security_headers(url)** → `{csp,hsts,xfo,xcto,referrer,permissions, raw:HEADERS}`
* **responsive_audit(url, viewports[])** → `{url, summaries:[{viewport, overflow, badTapTargets, screenshotPath}]}`
* **zap_baseline(url, minutes)** → `{alerts:[{risk,alert,instances:[...]}], raw:ZAP_JSON}`
* **report_merge(items, budgets?)** → `{score:{perf,a11y,seo,security,responsive,global}, findings:[...], htmlReportPath, jsonReportPath}`

## 6. Budgets y scoring (versión 1)

* **Peso categorías:** Perf 30%, A11y 30%, SEO 20%, Security 15%, Responsive 5%.
* **Reglas iniciales:**

  * Lighthouse performance = score Perf.
  * A11y: penalizar por nº/criticidad de `violations` (axe).
  * Security: headers faltantes y nº/criticidad ZAP.
  * SEO: score Lighthouse SEO.
  * Responsive: overflow (−) y tap-targets pequeños (−).
* **Budgets (fallo duro opcional):** LCP>3s, CLS>0.1, TBT>300ms, `violations.critical>0`, falta de `CSP`/`HSTS`.

## 7. Seguridad, privacidad y ética

* **Local-first:** No enviar datos a terceros por defecto.
* **ZAP baseline:** Solo pasivo por defecto; advertir antes de escaneo activo.
* **Manejo de secretos:** Variables de entorno; no commit.
* **Screenshots:** Guardados localmente en `artifacts/`.

## 8. Rendimiento y confiabilidad

* Reutilizar navegadores Playwright cuando sea viable.
* Timeouts razonables y **reintentos** (1) en fallos transitorios de red.
* Salidas determinísticas y estables para uso por agentes.

## 9. Extensibilidad (futuro)

* **SAST** (ESLint/stylelint), **visual diff** (BackstopJS), **crawler** ligero, integración con otros MCP o servicios opcionales.

## 10. Estructura del repositorio

```
webscanMCP/
├─ mcp/
│  ├─ server.py
│  └─ tools/
│     ├─ lighthouse.py
│     ├─ axe_playwright.py
│     ├─ webhint.py
│     ├─ security_headers.py
│     ├─ responsive.py
│     ├─ zap.py
│     ├─ wave.py                  # ← NUEVO (API WAVE)
│     ├─ cdp_gateway.py           # ← NUEVO (cliente MCP Chrome)
│     └─ report_merge.py
├─ node-tools/
│  ├─ package.json
│  ├─ axe-playwright.js
│  ├─ security-headers.js
│  └─ responsive.js
├─ artifacts/
├─ docker/
│  └─ docker-compose.yml
├─ PLANNING.md
├─ TASK.md
└─ GLOBAL_RULES.md

```

## 11. Setup local (resumen)

* Python 3.12+: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
* Node 22+: `cd node-tools && npm install && cd ..`
* Playwright: `npx playwright install chromium --with-deps`
* Opcional ZAP: `docker pull owasp/zap2docker-stable`
* Ejecutar: `python mcp/server.py` (modo STDIO, recomendado)
* VS Code MCP config: Ver README.md sección "VS Code Configuration"

## 12. Riesgos y mitigaciones

* **Cambios API Playwright/Lighthouse:** bloquear versiones mínimas; tests de humo.
* **Permisos Docker/ZAP:** documentación clara y fallback sin ZAP.
* **Rendimiento en Windows:** guías de instalación Playwright.
* **Dependencias npx requieren internet**: Primera ejecución requiere conexión, luego cachea localmente.
* **Docker HTTP mode no documentado**: Actualmente en desarrollo, usar STDIO mode.

## 13. Estado de Producción (v1.2.0 - 2025-10-29)

### Herramientas Estables (Production Ready ✅)

| Tool                  | Success Rate | Last Tested | Notes                            |
| --------------------- | ------------ | ----------- | -------------------------------- |
| Axe Accessibility     | 97%          | 2025-10-29  | 36/37 rules passing              |
| Security Headers      | 100%         | 2025-10-29  | Accurate detection               |
| Responsive Audit      | 100%         | 2025-10-29  | Tap targets & overflow working   |
| Chrome DevTools MCP   | 100%         | 2025-10-29  | Screenshots & navigation working |
| Report Merge          | 100%         | 2025-10-27  | JSON/HTML consolidation working  |

### Herramientas en Desarrollo

| Tool        | Status              | Blocker                         |
| ----------- | ------------------- | ------------------------------- |
| Lighthouse  | ❌ Failing          | npx requires internet           |
| WebHint     | ⚠️ Not tested       | Pending validation              |
| WAVE API    | ⚠️ Partial          | Requires API key configuration  |
| OWASP ZAP   | ⚠️ Partial          | Requires Docker running         |

### Infraestructura

* **STDIO Mode (VS Code MCP)**: ✅ Fully functional, recommended
* **Docker HTTP Mode**: ⚠️ In development (see TASK.md roadmap R-D-01 to R-D-05)
* **Documentation**: ✅ Multilingual README (4 languages), 7 professional prompts
* **Testing**: 80% Python coverage, 30% Node.js coverage
