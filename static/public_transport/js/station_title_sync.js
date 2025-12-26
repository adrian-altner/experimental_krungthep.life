(() => {
    const slugify = (value) => {
        return value
            .toLowerCase()
            .trim()
            .replace(/[^a-z0-9]+/g, "-")
            .replace(/^-+|-+$/g, "");
    };

    const bindSync = () => {
        const stationSelect = document.querySelector('select[name$="station"]');
        const titleInput =
            document.querySelector('input[name="title"]') ||
            document.querySelector("#id_title");
        const slugInput =
            document.querySelector('input[name="slug"]') ||
            document.querySelector("#id_slug");

        if (!stationSelect || !titleInput || !slugInput) {
            return;
        }

        stationSelect.addEventListener("change", (event) => {
            const option = event.target.selectedOptions[0];
            if (!option || !option.textContent) {
                return;
            }
            const stationLabel = option.textContent.trim();
            if (!stationLabel) {
                return;
            }
            titleInput.value = stationLabel;
            if (!slugInput.value) {
                slugInput.value = slugify(stationLabel) || slugInput.value;
            }
        });
    };

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", bindSync);
    } else {
        bindSync();
    }

    document.addEventListener("wagtail:ready", bindSync);
})();
