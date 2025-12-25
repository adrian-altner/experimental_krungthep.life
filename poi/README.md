# POI App

## Overview
The `poi` app provides Point of Interest (POI) pages and an index listing with
filters and a lightweight map visualization (no external CDN scripts).

## Create the POIIndexPage
1. In Wagtail Admin, add a new page of type **POIIndexPage** under the HomePage.
2. Publish the page. It will serve as the POI listing.

## Add POIs
1. Under the POIIndexPage, add **POIPage** entries.
2. Choose a **POICategory**, add descriptions, and optionally provide coordinates.
3. If coordinates are set, the POI will appear on the map.

## Categories & Features (Snippets)
- **POICategory** and **POIFeature** are snippets.
- Manage them in Wagtail Admin → Snippets.

## Filters & Query Parameters
The index page supports bookmarkable filters:
- `category=<id>` (single select)
- `feature=<slug>` (multi-select, repeat parameter)
- `q=<text>` (search)
- `verified=1` (verified only)
- `page=<number>` (pagination)

## Category-locked index pages
Each POIIndexPage can optionally be locked to a single category via the
`category` field on the page. When set, the listing only shows that category
and the category filter is read-only.
When a category is selected, the page slug is auto-set to the category title,
and the same category cannot be used by another POIIndexPage.

## Map Data
Map points are rendered from inline JSON using `map_pois` in the template.
Leaflet assets are stored locally under `poi/static/poi/vendor/leaflet/`.
POIs without coordinates are listed but not shown on the map.

## Files
- Templates: `poi/templates/poi/`
- Styles: `poi/static/poi/css/poi.css`
- Map JS: `poi/static/poi/js/poi_map.js`
