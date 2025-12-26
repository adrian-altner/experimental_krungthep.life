import json
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from public_transport.models import TransportStation


class Command(BaseCommand):
    help = "Import unified transportation GeoJSON into TransportStation snippets."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default="data/import/tbl_unified_transportation.geojson",
            help="Path to the GeoJSON file.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be imported without writing to the database.",
        )

    def handle(self, *args, **options):
        path = Path(options["path"])
        if not path.exists():
            raise CommandError(f"File not found: {path}")

        try:
            payload = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            raise CommandError(f"Invalid JSON: {exc}") from exc

        if payload.get("type") != "FeatureCollection":
            raise CommandError("Expected a GeoJSON FeatureCollection.")

        features = payload.get("features") or []
        created = 0
        updated = 0
        skipped = 0

        if options["dry_run"]:
            self.stdout.write("Dry run: no rows will be written.")

        with transaction.atomic():
            for feature in features:
                props = feature.get("properties") or {}
                geometry = feature.get("geometry") or {}
                if geometry.get("type") != "Point":
                    skipped += 1
                    continue

                station_qid = (props.get("stationQid") or "").strip()
                line_qid = (props.get("lineQid") or "").strip()
                if not station_qid or not line_qid:
                    skipped += 1
                    continue

                coordinates = geometry.get("coordinates")
                longitude, latitude = self._parse_coordinates(coordinates)

                defaults = {
                    "station_label": props.get("stationLabel") or "",
                    "system_label": props.get("systemLabel") or "",
                    "system_qid": props.get("systemQid") or "",
                    "line_label": props.get("lineLabel") or "",
                    "opening": self._parse_opening(props.get("opening")),
                    "station_codes": props.get("stationCodes") or "",
                    "latitude": latitude,
                    "longitude": longitude,
                    "raw_properties": self._merge_raw_properties(props, coordinates),
                }

                if options["dry_run"]:
                    created += 1
                    continue

                obj, was_created = TransportStation.objects.update_or_create(
                    station_qid=station_qid,
                    line_qid=line_qid,
                    defaults=defaults,
                )
                if was_created:
                    created += 1
                else:
                    updated += 1

            if options["dry_run"]:
                transaction.set_rollback(True)

        self.stdout.write(
            "Processed: {total}, created: {created}, updated: {updated}, skipped: {skipped}".format(
                total=len(features),
                created=created,
                updated=updated,
                skipped=skipped,
            )
        )

    def _parse_opening(self, value):
        if not value:
            return None
        try:
            if isinstance(value, date):
                return value
            text = str(value).replace("Z", "+00:00")
            return datetime.fromisoformat(text).date()
        except ValueError:
            return None

    def _parse_coordinates(self, coords):
        if not coords or len(coords) < 2:
            return None, None
        lon, lat = coords[0], coords[1]
        return self._quantize_coord(lon), self._quantize_coord(lat)

    def _quantize_coord(self, value):
        if value in (None, ""):
            return None
        return Decimal(str(value)).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)

    def _merge_raw_properties(self, props, coordinates):
        merged = dict(props or {})
        if coordinates:
            merged["coordinates"] = coordinates
        return merged
