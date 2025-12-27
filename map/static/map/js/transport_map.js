(() => {
    const dataEl = document.getElementById("transport-map-data");
    const mapEl = document.getElementById("transport-map");
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

    if (!window.L) {
        mapEl.textContent = "Map library unavailable.";
        return;
    }

    const map = window.L.map(mapEl, { scrollWheelZoom: "center", zoomControl: true });
    map.options.wheelPxPerZoomLevel = 120;
    window.L.control.scale({ position: "bottomleft" }).addTo(map);

    window.L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors",
    }).addTo(map);

    const bounds = [];
    data.forEach((item) => {
        const marker = window.L.marker([item.lat, item.lng]).addTo(map);
        const subtitle = item.subtitle ? `<br>${item.subtitle}` : "";
        marker.bindPopup(`<strong>${item.title}</strong>${subtitle}`);
        bounds.push([item.lat, item.lng]);
    });

    if (bounds.length === 1) {
        map.setView(bounds[0], 14);
    } else {
        map.fitBounds(bounds, { padding: [30, 30] });
    }
})();
