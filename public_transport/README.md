# Public Transport

## Overview
The `public_transport` app provides Wagtail page types and snippets for
public transportation systems, lines, and stations, plus import and sync
commands.

Key concepts:
- **TransportStation (snippet)**: the raw station data imported from GeoJSON.
- **Index page**: top-level entry that lists selected systems.
- **System page**: lists lines or stations (when enabled).
- **Line page**: lists stations for a line.
- **Station page**: optional detail page per station (manual selection).

## Page Types
### PublicTransportIndexPage
- Select systems via `system_filters` (checkboxes in admin).
- Lists systems.
- Parent: `HomePage`

### PublicTransportSystemPage
- Fields: `system_label`, `system_qid`
- Option: **Show stations** (if enabled, the system page shows stations directly).
- Child pages: `PublicTransportLinePage` and `PublicTransportStationPage`
- If **Show stations** is enabled, station detail pages can be routed directly at:
  `/public-transport/<system-slug>/<station-slug>/`

### PublicTransportLinePage
- Fields: `line_label`, `line_qid`, `system_label`
- Lists stations for the line
- Child pages: `PublicTransportStationPage`

### PublicTransportStationPage
- Manual station selection (chooses a `TransportStation` snippet).
- Stores and displays the parent line/system context.
- When a station detail page exists, station cards link to it; otherwise they
  fall back to the map link when coordinates exist.

## Snippets
### TransportStation
Raw station data imported from GeoJSON. This is the base dataset used for
system/line/station listings.

Fields include:
- station_label, station_qid
- system_label, system_qid
- line_label, line_qid
- opening, station_codes
- latitude, longitude
- raw_properties (includes coordinates)

## Import & Sync Commands
### Import unified transport data (GeoJSON)
```
python manage.py import_unified_transportation
```

### Sync system/line pages from snippets
```
python manage.py sync_transport_pages --index-id <INDEX_PAGE_ID>
```

Options:
- `--all-systems`: ignore index filters and include all systems
- `--dry-run`: show counts without writing

## Map Links
Station cards link to `/map/transport/?lat=...&lng=...&title=...&system=...&line=...`
when a station detail page does not exist. The map page renders a single marker.

## Notes
- Station detail pages can exist under system pages (if show-stations is enabled)
  or under line pages.
- When a station detail page exists, station cards show a “Detail page” badge.
