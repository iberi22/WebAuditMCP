# Changelog

All notable changes to WebAuditMCP will be documented in this file.

## [1.3.0] - 2025-10-30

### Added

- **lighthouse_fast Tool**: Ultra-fast Lighthouse auditing optimized for development
  - 20-45 second timeout for localhost URLs
  - Performance-only mode with minimal audits
  - Direct lighthouse command support (bypasses npx issues)
  - Optimized Chrome flags for maximum speed
- **url_check Tool**: Connectivity verification before running audits
  - Quick HEAD request validation
  - Helpful error messages for connection issues
  - Development server status checking
- **quick_audit Tool**: Combined fast auditing for immediate feedback
  - Security headers + responsive audit in under 30 seconds
  - Perfect for development workflows
- **Development Audit Prompt**: `prompts/development/localhost-audit.md`
  - Optimized workflow for localhost development
  - Fast feedback in under 1 minute
  - Structured development report format

### Enhanced

- **Axe Accessibility**: Complete functionality restoration
  - Fixed parsing of violations, passes, and incomplete results
  - Added comprehensive summary statistics
  - Enhanced error handling and reporting
  - Now returns detailed accessibility analysis (39 rules tested)
- **Lighthouse Tool**: Major performance improvements
  - Reduced timeout from 120s to 30-90s based on URL type
  - Added localhost-specific optimizations
  - Enhanced Chrome flags for stability
  - Better error messages for common issues
- **MCP Configuration**: Improved timeout and auto-approval settings
  - Increased MCP timeout to 10 minutes (600,000ms)
  - Added auto-approval for fast tools
  - Enhanced error handling for connection issues

### Fixed

- **npm Cache Issues**: Resolved corrupted npm cache causing Lighthouse failures
- **Lighthouse Installation**: Added global lighthouse installation support
- **Axe Results Parsing**: Fixed 0 violations/0 passes issue
- **Code Quality**: Fixed 27 Python linting errors with ruff
- **Node.js Formatting**: Fixed 3 JavaScript files with Biome
- **Import Organization**: Cleaned up Python imports and type annotations

### Validated

- **All Tools Status**: Comprehensive testing completed
  - ✅ **Security Headers**: 83.3/100 (Production Ready)
  - ✅ **Responsive Audit**: 100% functional (Production Ready)
  - ✅ **Lighthouse Fast**: 99/100 performance score (Production Ready)
  - ✅ **Axe Accessibility**: 0 violations, 39 passes (Production Ready)
  - ✅ **Quick Audit**: Combined tools working (Production Ready)
  - ✅ **URL Check**: Connectivity validation (Production Ready)
- **Test Suite**: All tests passing
  - Python: 19/20 tests passed (1 skipped for Docker)
  - Node.js: 10/10 tests passed
  - Linting: 0 errors after fixes

### Performance Metrics

Real application audit results (localhost:3000/login):

- **Performance**: 99/100 ⭐⭐⭐⭐⭐
  - FCP: 0.2s, LCP: 0.6s, Speed Index: 1.2s
  - TBT: 30ms, CLS: 0
- **Security**: 83.3/100 ⭐⭐⭐⭐
  - CSP, X-Frame-Options, X-Content-Type-Options: ✅
  - Only missing HSTS (normal for localhost)
- **Accessibility**: 39/40 rules ⭐⭐⭐⭐⭐
  - 0 violations, 1 incomplete (color contrast with gradients)
- **Responsive**: Excellent ⭐⭐⭐⭐
  - No overflow issues, 4 minor tap target improvements needed

### Resolved Issues

- 🔴 **Lighthouse Timeouts**: Resolved with lighthouse_fast tool
- 🔴 **Axe Not Working**: Resolved with enhanced parsing
- 🔴 **npm Cache Corruption**: Resolved with cache cleanup
- 🔴 **MCP Connection Issues**: Resolved with timeout increases
- 🟡 **Code Quality**: All linting errors fixed

## [1.2.0] - 2025-10-29

### Added

- **Professional Rebrand**: Renamed from "MCP Auditor Local" to "WebAuditMCP"
- **Multilingual README**: 4 languages (English, Spanish, Portuguese, Chinese)
- **Technology Badges**: 8 technology badges in README (Python, Node.js, FastMCP, Lighthouse, Playwright, axe, Docker, VS Code)
- **Professional Audit Prompts**: 7 categorized prompt templates for AI agents
  - `prompts/complete-audit.md`: Comprehensive website audit
  - `prompts/security/headers-audit.md`: HTTP security headers analysis
  - `prompts/security/vulnerabilities.md`: OWASP ZAP security scanning
  - `prompts/accessibility/wcag-compliance.md`: WCAG 2.1 AA compliance
  - `prompts/performance/core-web-vitals.md`: Core Web Vitals optimization
  - `prompts/visual/responsive-design.md`: Multi-viewport testing
  - `prompts/styles-layouts/color-contrast.md`: Color contrast validation
- **Prompts Index**: `prompts/README.md` with usage examples and workflow guidance
- **Enhanced Lighthouse**: 14 Chrome flags for localhost stability
- **Error Detection**: Improved error messages for connection refused and interstitials
- **Server Checker**: PowerShell script `check-server.ps1` for development server validation

### Changed

- **Project Name**: MCP Auditor Local → WebAuditMCP
- **Documentation Structure**: Completely rewritten README with focus on usage/configuration
- **Lighthouse Tool**: Enhanced with localhost URL detection and helpful logging
- **Installation Guides**: Separated local mode and Docker mode with clear examples
- **VS Code Integration**: Added STDIO transport mode configuration (primary)
- **Prompt Design**: All prompts generate single .md output optimized for AI iteration

### Fixed

- **Lighthouse Localhost**: Added flags to bypass security warnings on localhost URLs
- **Chrome Interstitials**: Detection and helpful error messages for interstitial pages
- **WebHint Dependencies**: Added dependency checking with install instructions
- **Health Check**: Enhanced with dependency version information display

### Validated

- **Axe Accessibility**: 36/37 rules passing (97% success rate) - Production Ready ✅
- **Security Headers**: 100% detection accuracy - Production Ready ✅
- **Responsive Audit**: Tap target and overflow detection working - Production Ready ✅
- **Chrome DevTools MCP**: Screenshots and navigation successful - Production Ready ✅
- **Report Merge**: JSON/HTML consolidation working - Production Ready ✅

### Known Issues

- **Lighthouse**: npx auto-install requires internet connection (pending local fallback)
- **WebHint**: Not tested in latest agent execution (low priority)
- **Docker HTTP Mode**: Configuration pending for `.vscode/mcp.json` URL endpoint
- **WAVE API**: Requires API key configuration
- **OWASP ZAP**: Requires Docker running

### Roadmap

- 🔴 CRITICAL: Complete Docker HTTP configuration for VS Code integration
- 🟡 HIGH: Resolve Lighthouse npx internet dependency
- 🟡 HIGH: Implement WebHint auto-installation with npx
- 🟢 MEDIUM: Update documentation with real audit results
- 🔵 LOW: Visual regression testing with BackstopJS

## [1.1.0] - 2025-10-27

### Added

- **Biome Integration**: Migrated from ESLint + Prettier to Biome for unified linting and formatting
- **Environment Variables**: Added `.env` and `.env.example` for configuration management
- **Quick Start Scripts**: Added `scripts/quick-start.sh` and `scripts/quick-start.ps1` for easy setup
- **Docker Support**: Fully functional Docker and Docker Compose configuration

### Changed

- **Linting**: Replaced ESLint and Prettier with Biome v2.3.1
- **Docker**: Fixed Dockerfile to use `npm install` instead of `npm ci`
- **Docker**: Fixed user UID conflict in Dockerfile
- **Docker Compose**: Removed obsolete `version` field
- **Scripts**: Updated npm scripts to use Biome commands
- **Documentation**: Updated README with environment variables and Docker instructions

### Fixed

- Docker build errors related to package-lock.json
- Docker user creation conflicts with existing UID 1000
- Biome configuration schema version mismatch
- Node.js import protocol warnings in responsive.js

### Removed

- ESLint configuration (`.eslintrc.json`)
- Prettier configuration (`.prettierrc`)
- ESLint and Prettier npm dependencies

## [1.0.0] - 2025-10-26

### Added

- Initial release of MCP Auditor Local
- Core audit tools: Lighthouse, axe, webhint, security headers, responsive
- Chrome DevTools Gateway integration
- WAVE API integration
- OWASP ZAP baseline scanning
- Unified reporting system with JSON and HTML output
- Comprehensive test suite with pytest and vitest
- Docker and Docker Compose support
- Complete documentation and examples

### Features

- 8 MCP tools for web auditing
- Multi-viewport responsive testing
- Security headers analysis
- Accessibility scanning with axe-core
- Performance auditing with Lighthouse
- SEO analysis
- Budget enforcement system
- Artifact generation (screenshots, reports)
