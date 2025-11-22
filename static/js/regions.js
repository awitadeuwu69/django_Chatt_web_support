document.addEventListener("DOMContentLoaded", async () => {
  const regionSelect = document.getElementById("region");
  const comunaSelect = document.getElementById("comuna");
  if (!regionSelect || !comunaSelect) return;

  try {
    const res = await fetch("/static/data/regions.json");
    const data = await res.json();
    const regions = data.regions || [];

    // Populate region select
    regionSelect.innerHTML = '<option value="">Seleccione una región</option>';
    regions.forEach((r) => {
      const opt = document.createElement("option");
      opt.value = r.name;
      opt.textContent = r.name;
      regionSelect.appendChild(opt);
    });

    // Get current values from global vars set in template (if any)
    const currentRegion = window.currentRegion || "";
    const currentComuna = window.currentComuna || "";

    if (currentRegion) regionSelect.value = currentRegion;

    function populateComunas(regionName) {
      comunaSelect.innerHTML =
        '<option value="">Seleccione una comuna</option>';
      if (!regionName) return;
      const regionObj = regions.find((rr) => rr.name === regionName);
      if (!regionObj) return;
      regionObj.communes.forEach((c) => {
        const o = document.createElement("option");
        o.value = c.name;
        o.textContent = c.name;
        comunaSelect.appendChild(o);
      });
      if (currentComuna) comunaSelect.value = currentComuna;
    }

    // Initial population
    populateComunas(regionSelect.value);

    // Update comunas when region changes
    regionSelect.addEventListener("change", () => {
      // clear any previously selected comuna if region changed
      populateComunas(regionSelect.value);
    });
  } catch (err) {
    console.error("Error cargando regiones:", err);
  }
});
