
# GLOBAL_RULES.md

## 🔄 Project Awareness & Context

* **Siempre lee `PLANNING.md`** al inicio de cada conversación para mantener alineación con visión, arquitectura y contratos de tools.
* **Revisa `TASK.md`** antes de comenzar algo. Si la tarea no existe, **añádela** con fecha y descripción breve.
* **Usa los contratos de I/O** definidos en PLANNING para cualquier llamada de tools.

## 🧱 Code Structure & Modularity

* **Máx. 500 líneas por archivo.** Divide en módulos (`mcp/tools/*`, `node-tools/*`).
* Importaciones claras y consistentes. Mantén funciones puras donde sea posible.
* Los scripts Node deben ser **pequeños y de propósito único** (un runner por tool).

## 🧪 Testing & Reliability

* **Python (MCP):** usa **pytest**. Para cada tool, mínimo: caso esperado, edge case, error.
* **Node runners:** tests con **vitest/jest** (uno por script, al menos happy-path + error).
* Tests en `/tests` reflejando la estructura del código.

## ✅ Task Completion

# GLOBAL_RULES.md

## 🔄 Project Awareness & Context

* **Siempre lee `PLANNING.md`** al inicio de cada conversación para mantener alineación con visión, arquitectura y contratos de tools.
* **Revisa `TASK.md`** antes de comenzar algo. Si la tarea no existe, **añádela** con fecha y descripción breve.
* **Consulta CHANGELOG.md** para conocer el estado actual del proyecto y cambios recientes.
* **Usa los contratos de I/O** definidos en PLANNING para cualquier llamada de tools.
* **Nombre del proyecto**: WebAuditMCP (renombrado desde "MCP Auditor Local" en v1.2.0).

## 🧱 Code Structure & Modularity

* **Máx. 500 líneas por archivo.** Divide en módulos (`mcp/tools/*`, `node-tools/*`).
* Importaciones claras y consistentes. Mantén funciones puras donde sea posible.
* Los scripts Node deben ser **pequeños y de propósito único** (un runner por tool).
* **Manejo de errores**: Siempre retornar `{"status": "error", "message": "..."}` en fallos.
* **Validación de entrada**: Usar `pydantic` para validación de parámetros complejos.

## 🧪 Testing & Reliability

* **Python (MCP):** usa **pytest**. Para cada tool, mínimo: caso esperado, edge case, error.
* **Node runners:** tests con **vitest/jest** (uno por script, al menos happy-path + error).
* Tests en `/tests` reflejando la estructura del código.
* **Tests de producción**: Validar herramientas con sitios reales antes de marcar como estables.
* **Mocks inteligentes**: Solo para dependencias externas (Docker, APIs), no para lógica interna.

## ✅ Task Completion

* **Marca tareas** en `TASK.md` al completar y **agrega subtareas** descubiertas bajo "Tareas Descubiertas…".
* **Actualiza CHANGELOG.md** con todos los cambios significativos (Added/Changed/Fixed/Validated/Known Issues).
* **Roadmap tracking**: Usa las tablas del roadmap en TASK.md para planificación a largo plazo.

## 📎 Style & Conventions

* **Servidor MCP en Python.** Sigue **PEP8**, tipado, formatea con **black**.
* **Validación** con `pydantic` para entradas complejas (p.ej., arrays de viewports).
* **Node:** estilo consistente con **Biome** (reemplazó ESLint + Prettier en v1.1.0).
* **Docstrings** (Google style) en funciones Python. Comentarios `# Reason:` cuando el porqué no sea obvio.
* **Mensajes de error**: Siempre incluir contexto y pasos de resolución sugeridos.

## 📚 Documentation & Explainability

* **README.md multilingüe**: Mantén 4 idiomas sincronizados (English, Español, Português, 中文).
* **Actualiza `README.md`** cuando cambie el setup/flows/dependencias.
* **Explica decisiones técnicas** y trade-offs en comentarios o en PLANNING.
* **Prompts profesionales**: Toda nueva funcionalidad debe tener prompt correspondiente en `/prompts`.
* **Documentación de estado**: Mantener métricas de calidad actualizadas en TASK.md.

## 🧠 AI Behavior Rules

* **No asumas contexto faltante.** Pregunta cuando sea necesario.
* **No alucines librerías o rutas.** Verifica paquetes y paths.
* **No sobrescribas código existente** a menos que la tarea lo indique.
* **Respeta los contratos JSON** de cada tool y valida entradas.
* **Consulta métricas de producción**: Antes de modificar una herramienta estable, revisa su tasa de éxito en TASK.md.
* **Valida con agentes reales**: Simula ejecución de prompts para detectar fallos antes de commit.

## 🔐 Seguridad

* Mantén por defecto **ZAP en baseline** (pasivo). Advierte antes de cualquier escaneo activo.
* No expongas datos de usuario fuera del entorno local.
* **Gestión de secretos**: Variables de entorno en `.env`, nunca hardcodear API keys.
* **Lighthouse localhost**: Usar flags de seguridad solo para desarrollo, documentar riesgos.

## 🧰 Ejecución local (resumen)

* **Modo recomendado**: STDIO (local Python) vía VS Code MCP.
* Arranque: `python mcp/server.py`.
* Requisitos: Python 3.12+, Node 22+, Playwright instalado (`npx playwright install --with-deps`).
* Docker: Opcional, solo para `zap_baseline`. HTTP mode en desarrollo (ver roadmap TASK.md).

## 🎯 Quality Standards

* **Tasa de éxito mínima**: 90% para marcar herramienta como "Production Ready ✅".
* **Cobertura de tests**: Objetivo 80% Python, 70% Node.js.
* **Documentación obligatoria**: README, prompts, CHANGELOG, TASK.md deben estar sincronizados.
* **Zero-tolerance para silent failures**: Todo error debe tener mensaje claro y logging.

## 🚦 Estado Actual (Referencia Rápida)

**Herramientas Estables (Production Ready ✅)**:
- Axe Accessibility (97% success rate)
- Security Headers (100% accuracy)
- Responsive Audit (100% functional)
- Chrome DevTools MCP (100% functional)
- Report Merge (100% functional)

**Herramientas en Desarrollo**:
- Lighthouse (npx dependency issue)
- WebHint (not tested)
- WAVE API (requires configuration)
- OWASP ZAP (requires Docker)

**Infraestructura**:
- ✅ STDIO mode (VS Code MCP integration)
- ⚠️ Docker HTTP mode (planned, see roadmap)
- ✅ Multilingual documentation (4 languages)
- ✅ Professional audit prompts (7 templates)

## 📎 Style & Conventions

* **Servidor MCP en Python.** Sigue **PEP8**, tipado, formatea con **black**.
* **Validación** con `pydantic` para entradas complejas (p.ej., arrays de viewports).
* **Node:** estilo consistente, `prettier` y `eslint` básico.
* **Docstrings** (Google style) en funciones Python. Comentarios `# Reason:` cuando el porqué no sea obvio.

## 📚 Documentation & Explainability

* **Actualiza `README.md`** cuando cambie el setup/flows/depencias.
* **Explica decisiones técnicas** y trade-offs en comentarios o en PLANNING.

## 🧠 AI Behavior Rules

* **No asumas contexto faltante.** Pregunta cuando sea necesario.
* **No alucines librerías o rutas.** Verifica paquetes y paths.
* **No sobrescribas código existente** a menos que la tarea lo indique.
* **Respeta los contratos JSON** de cada tool y valida entradas.

## 🔐 Seguridad

* Mantén por defecto **ZAP en baseline** (pasivo). Advierte antes de cualquier escaneo activo.
* No expongas datos de usuario fuera del entorno local.

## 🧰 Ejecución local (resumen)

* Arranque: `python mcp/server.py`.
* Requisitos: Python 3.10+, Node 18/20, Playwright instalado (`npx playwright install --with-deps`).
* Docker solo para `zap_baseline`.