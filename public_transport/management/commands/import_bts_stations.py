import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from home.models import HomePage
from wagtail.models import Page
from public_transport.models import (
    PublicTransportCategoryPage,
    PublicTransportIndexPage,
    PublicTransportPage,
)


class Command(BaseCommand):
    help = "Import BTS stations from a JSON file into PublicTransportPage entries."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default="data/import/bangkok_transit_stations_wikidata.json",
            help="Path to the BTS stations JSON file.",
        )
        parser.add_argument(
            "--index-slug",
            default="public-transport",
            help="Slug for the Public Transport index page.",
        )
        parser.add_argument(
            "--index-title",
            default="Public Transport",
            help="Title for the Public Transport index page (if created).",
        )
        parser.add_argument(
            "--category",
            default="BTS",
            help="Category value to apply to imported pages.",
        )
        parser.add_argument(
            "--category-slug",
            default="bts",
            help="Slug for the category page under the index.",
        )
        parser.add_argument(
            "--category-id",
            type=int,
            help="ID of an existing Public Transport category page to import into.",
        )
        parser.add_argument(
            "--system",
            default="BTS",
            help="Transit system to import from the JSON file.",
        )
        parser.add_argument(
            "--index-id",
            type=int,
            help="ID of an existing Public Transport index page to import into.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be imported without creating pages.",
        )

    def handle(self, *args, **options):
        path = Path(options["path"])
        if not path.exists():
            raise CommandError(f"File not found: {path}")

        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            raise CommandError(f"Invalid JSON: {exc}") from exc

        if not isinstance(data, list):
            raise CommandError("Expected a list of station records.")

        index_page = self._get_or_create_index_page(
            slug=options["index_slug"],
            title=options["index_title"],
            index_id=options["index_id"],
            dry_run=options["dry_run"],
        )
        category_page = self._get_or_create_category_page(
            index_page=index_page,
            slug=options["category_slug"],
            title=options["category"],
            system=options["system"],
            category_id=options["category_id"],
            dry_run=options["dry_run"],
        )

        existing_pages_by_wikidata = {
            page.wikidata_id: page
            for page in PublicTransportPage.objects.exclude(wikidata_id="")
        }
        if category_page.pk:
            taken_slugs = set(
                category_page.get_children().values_list("slug", flat=True)
            )
        else:
            taken_slugs = set()
        seen_wikidata_ids = set()

        created = 0
        updated = 0
        skipped = 0
        candidates = 0

        if options["dry_run"]:
            self.stdout.write("Dry run: no pages will be created.")

        with transaction.atomic():
            for item in data:
                if item.get("system") and item.get("system") != options["system"]:
                    continue

                candidates += 1
                wikidata_id = item.get("wikidata_id") or ""

                title = item.get("name") or "Unnamed station"
                station_code = item.get("station_code") or ""
                line = item.get("line") or ""

                if wikidata_id:
                    existing_page = existing_pages_by_wikidata.get(wikidata_id)
                    if existing_page:
                        merged = self._merge_lines(existing_page.line, line)
                        if merged != (existing_page.line or ""):
                            existing_page.line = merged
                            existing_page.save_revision().publish()
                            updated += 1
                        skipped += 1
                        continue
                    if wikidata_id in seen_wikidata_ids:
                        skipped += 1
                        continue
                slug = self._unique_slug(
                    title=title,
                    station_code=station_code,
                    wikidata_id=wikidata_id,
                    taken_slugs=taken_slugs,
                )
                taken_slugs.add(slug)
                seen_wikidata_ids.add(wikidata_id)

                page = PublicTransportPage(
                    title=title,
                    slug=slug,
                    category=options["category"],
                    system=item.get("system") or "",
                    line=line,
                    station_code=station_code,
                    latitude=self._quantize_coord(item.get("lat")),
                    longitude=self._quantize_coord(item.get("lon")),
                    wikidata_id=wikidata_id,
                    wikidata_url=item.get("wikidata_url") or "",
                )

                if options["dry_run"]:
                    created += 1
                    continue

                category_page.add_child(instance=page)
                page.save_revision().publish()
                created += 1
                if wikidata_id:
                    existing_pages_by_wikidata[wikidata_id] = page

            if options["dry_run"]:
                transaction.set_rollback(True)

        self.stdout.write(
            "Candidates: {candidates}, created: {created}, "
            "updated: {updated}, skipped: {skipped}".format(
                candidates=candidates,
                created=created,
                updated=updated,
                skipped=skipped,
            )
        )

    def _get_or_create_index_page(self, slug, title, index_id, dry_run):
        if index_id:
            index_page = PublicTransportIndexPage.objects.filter(id=index_id).first()
            if not index_page:
                raise CommandError(
                    f"No PublicTransportIndexPage found with id {index_id}."
                )
            return index_page

        index_page = PublicTransportIndexPage.objects.filter(slug=slug).first()
        if index_page:
            return index_page

        home_page = (
            HomePage.objects.live().first()  # type: ignore[attr-defined]
            or HomePage.objects.first()
        )
        if not home_page:
            raise CommandError("No HomePage found. Create one before importing.")

        if Page.objects.child_of(home_page).filter(slug=slug).exists():  # type: ignore[attr-defined]
            raise CommandError(
                f"Slug '{slug}' already exists under the HomePage. "
                "Pass --index-id to import into an existing index page, "
                "or choose a different --index-slug."
            )

        index_page = PublicTransportIndexPage(title=title, slug=slug)

        if dry_run:
            return index_page

        home_page.add_child(instance=index_page)
        index_page.save_revision().publish()
        return index_page

    def _unique_slug(self, title, station_code, wikidata_id, taken_slugs):
        base = slugify(title) or "station"
        candidates = [base]

        if station_code:
            candidates.append(f"{base}-{slugify(station_code)}")
        if wikidata_id:
            candidates.append(f"{base}-{wikidata_id.lower()}")

        for candidate in candidates:
            if candidate not in taken_slugs:
                return candidate

        counter = 2
        while True:
            candidate = f"{base}-{counter}"
            if candidate not in taken_slugs:
                return candidate
            counter += 1

    def _quantize_coord(self, value):
        if value in (None, ""):
            return None
        return Decimal(str(value)).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)

    def _merge_lines(self, existing, incoming):
        existing = (existing or "").strip()
        incoming = (incoming or "").strip()
        if not incoming:
            return existing
        if not existing:
            return incoming
        existing_parts = [p.strip() for p in existing.split(",") if p.strip()]
        if incoming in existing_parts:
            return existing
        return ", ".join(existing_parts + [incoming])

    def _get_or_create_category_page(
        self, index_page, slug, title, system, category_id, dry_run
    ):
        if category_id:
            category_page = PublicTransportCategoryPage.objects.filter(
                id=category_id
            ).first()
            if not category_page:
                raise CommandError(
                    f"No PublicTransportCategoryPage found with id {category_id}."
                )
            return category_page

        if index_page.pk:
            category_page = (
                PublicTransportCategoryPage.objects.child_of(index_page)  # type: ignore[attr-defined]
                .filter(slug=slug)
                .first()
            )
            if category_page:
                return category_page

        category_page = PublicTransportCategoryPage(
            title=title,
            slug=slug,
            category=title,
            system=system,
        )

        if dry_run:
            return category_page

        index_page.add_child(instance=category_page)
        category_page.save_revision().publish()
        return category_page
