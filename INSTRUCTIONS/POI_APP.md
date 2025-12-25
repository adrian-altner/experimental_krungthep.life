# Agent Instruction: POI App (Wagtail / Django)

## Project Context
Project: KrungThep.life  
Framework: Django + Wagtail CMS  
Domain: City guide / Places / Points of Interest (POI)  
Stack assumptions:
- Wagtail Pages are used for public content
- PostGIS / Leaflet may be used now or later
- No external CDN scripts
- SEO, extensibility and clean content structure are critical

---

## Goal
Implement a **POI (Point of Interest) App** that allows editors to manage places such as restaurants, cafés, temples, markets, viewpoints, BTS/MRT stations, etc.

Each POI must:
- Be a first-class **Wagtail Page**
- Have its own URL and detail page
- Be listed on an index page with filters
- Appear on a map if coordinates are available
- Be future-proof for reviews, events, routing, and community features

---

## Naming Convention (IMPORTANT)
Internal technical naming MUST use POI terminology.

- Django App: `poi`
- Index Page: `POIIndexPage`
- Detail Page: `POIPage`
- Category Snippet: `POICategory`
- Feature Snippet: `POIFeature`

Public labels (e.g. navigation title “Places”) may differ, but internal names must stay consistent.

---

## Wagtail Content Architecture

### Page Types
1. **POIIndexPage**
   - Acts as the overview/listing page
   - Provides filtering, search, and map integration
   - Only allowed parent: Home (or a defined root page)

2. **POIPage**
   - Represents a single Point of Interest
   - Only allowed parent: POIIndexPage
   - Each POI has exactly one detail page

Enforce parent/child rules strictly via Wagtail page type restrictions.

---

## POIPage: Required Content Fields (Conceptual)

### Identity & Classification
- Title / Name
- Category (reference to POICategory)
- Short description (for cards, previews, SEO)
- Full description (editorial content)
- Tags or attributes (via POIFeature relations)

### Location & Geography
- Human-readable address
- Area / district (e.g. neighborhood)
- City and country (default values allowed)
- Geographic coordinates (lat/lng or geo point)
- Optional landmark reference (e.g. “near BTS Asok”)

Coordinates are mandatory for map display but not for saving the page.

### Contact & Presence
- Website URL
- Phone number
- Optional social links (Instagram, Facebook, etc.)

### Media
- Hero image
- Image gallery
- Optional logo or symbol

### Quality & Status
- Verified flag (editorial trust indicator)
- Optional price level
- Optional notes for editors

### Meta / Editorial
- Draft / published state (standard Wagtail)
- SEO title and description
- Created / updated timestamps (standard)

---

## Snippets

### POICategory
Used to classify POIs (e.g. Restaurant, Café, Temple, Market).

Fields:
- Title
- Slug (unique, stable, filter-safe)
- Optional icon or ordering field

Rules:
- Categories must NOT be free text
- Used for filtering and navigation

### POIFeature
Used for attributes or characteristics.

Examples:
- Vegan options
- Rooftop
- WiFi
- Air conditioning
- Wheelchair accessible
- Cash only

Fields:
- Title
- Slug
- Optional group (e.g. Food, Accessibility, Payment)

---

## POIIndexPage: Listing & Filtering

The index page must:
- Display a paginated list of POIs
- Provide filters via query parameters:
  - Category (single select)
  - Features (multi-select)
  - Text search (name / description)
  - Optional: verified only
- Combine filters server-side

Sorting:
- Default: editorial choice (e.g. newest or alphabetical)
- Prepare structure for later “nearest” sorting

---

## Map Integration (Leaflet)

- Display a map on the index page
- Show markers for all currently filtered POIs with coordinates
- Marker popup must include:
  - Name
  - Category
  - Link to detail page

Data delivery:
- Either inline JSON rendered by the template
- Or a small JSON endpoint associated with the index page

The chosen approach must:
- Respect active filters
- Be documented in the app README

POIs without coordinates:
- Are listed normally
- Are NOT shown on the map

---

## POI Detail Page (POIPage)

The detail page should include:
- Hero image
- Name and category
- Feature badges
- Full description
- Address and external map link
- Contact information
- Image gallery

Prepare placeholders/hooks (no full logic required yet) for:
- Reviews
- Nearby POIs
- Related blog posts or events

The page must degrade gracefully if optional data is missing.

---

## URL & Query Behavior

- POI pages use standard Wagtail page URLs
- Index page supports filtering via query parameters
- Filters must be bookmarkable and shareable
- No JavaScript-only filtering

---

## Search Integration

If Wagtail search is enabled:
- POIPage must be searchable by:
  - Name
  - Short description
  - Full description
  - Address
  - Category title

Search must integrate cleanly with filters.

---

## Permissions & Editorial Workflow

- Use standard Wagtail draft/publish workflow
- Design so that community edits or suggestions can be added later
- Verified flag should be editable only by trusted roles (if possible; otherwise document as TODO)

---

## Data Quality Rules

- Categories and features must be controlled via snippets
- No free-text classification
- Coordinates must be validated logically
- Slugs should be stable and not auto-regenerated on edits

---

## Initial Data (Optional but Recommended)

Provide initial categories and features via fixtures or data migration, e.g.:

Categories:
- Restaurant
- Café
- Bar
- Temple
- Market
- Viewpoint
- Hotel
- BTS / MRT Station

Features:
- WiFi
- Vegan options
- Rooftop
- Air conditioning
- Cash only
- Wheelchair accessible

---

## Tests (Minimum Expectations)

- POIIndexPage can be created
- POIPage can only be created under POIIndexPage
- Category and feature snippets can be created
- Filter logic returns expected POIs
- Map data output includes required fields when coordinates exist

---

## Documentation

Create a short README inside the `poi` app explaining:
- How to create the POIIndexPage
- How editors add POIs
- How categories and features are managed
- How filtering and map data work
- Which query parameters are supported

---

## Definition of Done

The task is complete when:
- Editors can manage POIs fully via Wagtail Admin
- `/poi/` (or public equivalent) lists POIs with filters and map
- Each POI has a working detail page
- Structure is extensible for reviews, routing, and community features
- No external CDN dependencies are used
