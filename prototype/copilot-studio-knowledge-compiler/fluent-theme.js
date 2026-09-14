const provider = document.querySelector("#fluentProvider");
let fluentLoadError = null;

try {
  const {
    accentBaseColor,
    baseLayerLuminance,
    neutralBaseColor,
    SwatchRGB,
  } = await import(
    "./vendor/fluent-web-components-2.6.1.min.js"
  );

  // shaper theme: near-black cool canvas with a cyan primary signal and lime success accent.
  baseLayerLuminance.setValueFor(provider, 0.06);
  accentBaseColor.setValueFor(
    provider,
    SwatchRGB.from({ r: 0.427, g: 0.878, b: 0.824 }),
  );
  neutralBaseColor.setValueFor(
    provider,
    SwatchRGB.from({ r: 0.51, g: 0.58, b: 0.62 }),
  );
  document.documentElement.dataset.colorScheme = "dark";
} catch (error) {
  fluentLoadError = error;
  document.documentElement.dataset.fluentUnavailable = "true";
  console.error("The Microsoft Fluent control library could not be loaded.", error);
}

await import("./app.js?v=20260914-shaper-v2");

if (fluentLoadError) {
  const alert = document.querySelector("#alert");
  alert.textContent =
    "Microsoft Fluent controls could not load. Check the content security and network policy, then reload.";
  alert.hidden = false;
  alert.focus();
}
