(() => {
    const dataEl = document.getElementById("poi-map-data");
    const mapEl = document.getElementById("poi-map");
    if (!dataEl || !mapEl) {
        return;
    }

    let data = [];
    try {
        data = JSON.parse(dataEl.textContent);
    } catch (error) {
        mapEl.textContent = "Map data unavailable.";
        return;
    }

    if (!data.length) {
        mapEl.textContent = mapEl.dataset.empty || "No locations available.";
        return;
    }

    const lats = data.map((item) => item.lat);
    const lngs = data.map((item) => item.lng);
    const minLat = Math.min(...lats);
    const maxLat = Math.max(...lats);
    const minLng = Math.min(...lngs);
    const maxLng = Math.max(...lngs);
    const latRange = maxLat - minLat || 1;
    const lngRange = maxLng - minLng || 1;

    const fragment = document.createDocumentFragment();
    data.forEach((item) => {
        const x = ((item.lng - minLng) / lngRange) * 100;
        const y = ((maxLat - item.lat) / latRange) * 100;

        const marker = document.createElement("div");
        marker.className = "poi-map__marker";
        marker.style.left = `${x}%`;
        marker.style.top = `${y}%`;

        const link = document.createElement("a");
        link.className = "poi-map__marker-link";
        link.href = item.url;
        link.setAttribute("aria-label", `${item.title} (${item.category})`);

        const dot = document.createElement("span");
        dot.className = "poi-map__marker-dot";

        const label = document.createElement("span");
        label.className = "poi-map__marker-label";
        label.textContent = `${item.title} — ${item.category}`;

        link.appendChild(dot);
        link.appendChild(label);
        marker.appendChild(link);
        fragment.appendChild(marker);
    });

    mapEl.appendChild(fragment);
})();
