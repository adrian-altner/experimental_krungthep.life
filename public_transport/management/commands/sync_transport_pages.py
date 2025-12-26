from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from public_transport.models import (
    PublicTransportIndexPage,
    PublicTransportLinePage,
    PublicTransportSystemPage,
    TransportStation,
)


class Command(BaseCommand):
    help = "Sync Public Transport system/line pages from TransportStation snippets."

    def add_arguments(self, parser):
        parser.add_argument(
            "--index-id",
            type=int,
            help="ID of the PublicTransportIndexPage to sync under.",
        )
        parser.add_argument(
            "--index-slug",
            help="Slug of the PublicTransportIndexPage to sync under.",
        )
        parser.add_argument(
            "--all-systems",
            action="store_true",
            help="Use all systems from TransportStation, ignoring index filters.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be created without writing.",
        )

    def handle(self, *args, **options):
        index_page = self._get_index_page(options)
        system_labels = self._get_system_labels(index_page, options["all_systems"])
        if not system_labels:
            self.stdout.write("No systems selected. Update the index page filters.")
            return

        system_slug_set = set(
            index_page.get_children().values_list("slug", flat=True)
        )

        created_systems = 0
        updated_systems = 0
        created_lines = 0
        updated_lines = 0

        if options["dry_run"]:
            self.stdout.write("Dry run: no pages will be written.")

        with transaction.atomic():
            for system_label in system_labels:
                system_qid = (
                    TransportStation.objects.filter(system_label=system_label)
                    .exclude(system_qid="")
                    .values_list("system_qid", flat=True)
                    .first()
                    or ""
                )
                system_page = PublicTransportSystemPage.objects.child_of(
                    index_page
                ).filter(system_label=system_label).first()

                if not system_page:
                    slug = self._unique_slug(slugify(system_label), system_slug_set)
                    system_slug_set.add(slug)
                    system_page = PublicTransportSystemPage(
                        title=system_label,
                        slug=slug,
                        system_label=system_label,
                        system_qid=system_qid,
                    )
                    if not options["dry_run"]:
                        index_page.add_child(instance=system_page)
                        system_page.save_revision().publish()
                    created_systems += 1
                else:
                    changed = False
                    if system_page.title != system_label:
                        system_page.title = system_label
                        changed = True
                    if system_page.system_qid != system_qid:
                        system_page.system_qid = system_qid
                        changed = True
                    if changed and not options["dry_run"]:
                        system_page.save_revision().publish()
                    if changed:
                        updated_systems += 1

                line_slug_set = set(
                    system_page.get_children().values_list("slug", flat=True)
                )
                lines = (
                    TransportStation.objects.filter(system_label=system_label)
                    .exclude(line_label="")
                    .values_list("line_label", "line_qid")
                    .distinct()
                    .order_by("line_label")
                )
                for line_label, line_qid in lines:
                    line_page = PublicTransportLinePage.objects.child_of(
                        system_page
                    ).filter(line_label=line_label).first()

                    if not line_page:
                        slug = self._unique_slug(slugify(line_label), line_slug_set)
                        line_slug_set.add(slug)
                        line_page = PublicTransportLinePage(
                            title=line_label,
                            slug=slug,
                            line_label=line_label,
                            line_qid=line_qid or "",
                            system_label=system_label,
                        )
                        if not options["dry_run"]:
                            system_page.add_child(instance=line_page)
                            line_page.save_revision().publish()
                        created_lines += 1
                    else:
                        changed = False
                        if line_page.title != line_label:
                            line_page.title = line_label
                            changed = True
                        if line_page.line_qid != (line_qid or ""):
                            line_page.line_qid = line_qid or ""
                            changed = True
                        if line_page.system_label != system_label:
                            line_page.system_label = system_label
                            changed = True
                        if changed and not options["dry_run"]:
                            line_page.save_revision().publish()
                        if changed:
                            updated_lines += 1

            if options["dry_run"]:
                transaction.set_rollback(True)

        self.stdout.write(
            "Systems created: {created_systems}, updated: {updated_systems}; "
            "lines created: {created_lines}, updated: {updated_lines}".format(
                created_systems=created_systems,
                updated_systems=updated_systems,
                created_lines=created_lines,
                updated_lines=updated_lines,
            )
        )

    def _get_index_page(self, options):
        if options["index_id"]:
            index_page = PublicTransportIndexPage.objects.filter(
                id=options["index_id"]
            ).first()
            if not index_page:
                raise CommandError(
                    f"No PublicTransportIndexPage found with id {options['index_id']}."
                )
            return index_page
        if options["index_slug"]:
            index_page = PublicTransportIndexPage.objects.filter(
                slug=options["index_slug"]
            ).first()
            if not index_page:
                raise CommandError(
                    f"No PublicTransportIndexPage found with slug '{options['index_slug']}'."
                )
            return index_page
        raise CommandError("Pass --index-id or --index-slug.")

    def _get_system_labels(self, index_page, all_systems):
        if all_systems:
            return list(
                TransportStation.objects.exclude(system_label="")
                .values_list("system_label", flat=True)
                .distinct()
                .order_by("system_label")
            )
        return list(index_page.system_filters or [])

    def _unique_slug(self, base, taken_slugs):
        base = base or "item"
        if base not in taken_slugs:
            return base
        counter = 2
        while True:
            candidate = f"{base}-{counter}"
            if candidate not in taken_slugs:
                return candidate
            counter += 1
