from __future__ import annotations

import argparse
import asyncio
import tempfile
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from playwright.async_api import async_playwright

from .models import CardCollection, ProphetCollection


async def html_to_pdf(html: str, output_pdf: Path, page_width: str | None = None, page_height: str | None = None) -> None:
    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".html", delete=False) as tmp:
        tmp.write(html)
        tmp_path = Path(tmp.name)

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(tmp_path.as_uri(), wait_until="networkidle")

            pdf_options: dict[str, object] = {
                "path": str(output_pdf),
                "print_background": True,
                "prefer_css_page_size": True,
            }
            if page_width and page_height:
                pdf_options["width"] = page_width
                pdf_options["height"] = page_height

            await page.pdf(**pdf_options)
            await browser.close()
    finally:
        tmp_path.unlink(missing_ok=True)


def make_environment(template_dir: Path) -> Environment:
    return Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


async def render_cards(base_dir: Path, env: Environment) -> int:
    """Expand all cards by their copy count, then render a single multi-page sheet PDF."""
    cards_data = CardCollection.model_validate(load_yaml(base_dir / "data" / "cards.yaml"))
    template = env.get_template("card.html")

    # Expand: repeat each card `copies` times, injecting copy_num
    expanded: list[dict] = []
    for card in cards_data.cards:
        base = card.model_dump()
        if base.get("art"):
            base["art"] = (base_dir / base["art"]).resolve().as_uri()
        for copy_num in range(1, card.copies + 1):
            instance = dict(base)
            instance["copy_num"] = copy_num
            expanded.append(instance)

    html = template.render(cards=expanded)
    output = base_dir / "output" / "cards" / "cards_sheet.pdf"
    await html_to_pdf(html, output)
    return len(expanded)


async def render_placemats(base_dir: Path, env: Environment) -> int:
    placemat_data = ProphetCollection.model_validate(load_yaml(base_dir / "data" / "placemats.yaml"))
    template = env.get_template("placemat.html")

    count = 0
    for prophet in placemat_data.prophets:
        d = prophet.model_dump()
        if d.get("portrait_image"):
            d["portrait_image"] = (base_dir / d["portrait_image"]).resolve().as_uri()
        html = template.render(prophet=d)
        output = base_dir / "output" / "placemats" / f"{prophet.id}.pdf"
        await html_to_pdf(html, output)
        count += 1
    return count


async def run(base_dir: Path, cards_only: bool, placemats_only: bool) -> None:
    template_dir = base_dir / "templates"
    env = make_environment(template_dir)

    rendered_cards = 0
    rendered_placemats = 0

    if not placemats_only:
        rendered_cards = await render_cards(base_dir, env)

    if not cards_only:
        rendered_placemats = await render_placemats(base_dir, env)

    print(f"Rendered {rendered_cards} card instances across sheet(s) and {rendered_placemats} placemats.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render Drink the Koolaid assets to PDF")
    parser.add_argument("--cards-only", action="store_true", help="Render only cards")
    parser.add_argument("--placemats-only", action="store_true", help="Render only placemats")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.cards_only and args.placemats_only:
        raise SystemExit("Choose only one of --cards-only or --placemats-only.")

    base_dir = Path(__file__).resolve().parents[2]
    asyncio.run(run(base_dir=base_dir, cards_only=args.cards_only, placemats_only=args.placemats_only))


if __name__ == "__main__":
    main()
