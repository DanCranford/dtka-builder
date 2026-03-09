# Drink the Koolaid Renderer

Template-driven PDF rendering pipeline for cards and player placemats.

## Stack

- Python + `uv`
- `Jinja2` for HTML templating
- `Playwright` (Chromium) for PDF rendering
- `Pydantic` + `PyYAML` for schema-validated content input

## Project Layout

- `templates/` - HTML print templates (`card.html`, `placemat.html`)
- `data/` - YAML content (`cards.yaml`, `placemats.yaml`)
- `src/drink_the_koolaid_renderer/` - renderer code
- `output/` - generated PDFs

## Quick Start

1. Install dependencies:

```powershell
uv sync
```

2. Install Chromium for Playwright:

```powershell
uv run playwright install chromium
```

3. Render all assets:

```powershell
uv run render-assets
```

## Optional Commands

Render only cards:

```powershell
uv run render-assets --cards-only
```

Render only placemats:

```powershell
uv run render-assets --placemats-only
```
