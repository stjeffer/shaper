const provider = document.querySelector("#fluentProvider");
let fluentLoadError = null;

try {
  const {
    StandardLuminance,
    baseLayerLuminance,
  } = await import(
    "./vendor/fluent-web-components-2.6.1.min.js"
  );

  baseLayerLuminance.setValueFor(provider, StandardLuminance.LightMode);
  document.documentElement.dataset.colorScheme = "light";
} catch (error) {
  fluentLoadError = error;
  document.documentElement.dataset.fluentUnavailable = "true";
  console.error("The Microsoft Fluent control library could not be loaded.", error);
}

await import("./app.js?v=20260914-fluent2-v11");

if (fluentLoadError) {
  const alert = document.querySelector("#alert");
  alert.textContent =
    "Microsoft Fluent controls could not load. Check the content security and network policy, then reload.";
  alert.hidden = false;
  alert.focus();
}
