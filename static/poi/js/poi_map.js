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

    if (!window.L) {
        mapEl.textContent = "Map library unavailable.";
        return;
    }

    const map = window.L.map(mapEl, { scrollWheelZoom: false });
    window.L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors",
    }).addTo(map);

    const bounds = [];
    data.forEach((item) => {
        const marker = window.L.marker([item.lat, item.lng]).addTo(map);
        marker.bindPopup(
            `<strong><a href="${item.url}">${item.title}</a></strong><br>${item.category}`
        );
        bounds.push([item.lat, item.lng]);
    });

    if (bounds.length === 1) {
        map.setView(bounds[0], 14);
    } else {
        map.fitBounds(bounds, { padding: [30, 30] });
    }
})();
