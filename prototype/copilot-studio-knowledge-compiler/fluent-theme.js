const provider = document.querySelector("#fluentProvider");
const darkMode = window.matchMedia("(prefers-color-scheme: dark)");
let fluentLoadError = null;

try {
  const {
    StandardLuminance,
    accentStrokeControlActive,
    accentStrokeControlFocus,
    accentStrokeControlHover,
    accentStrokeControlRest,
    baseLayerLuminance,
  } = await import(
    "./vendor/fluent-web-components-2.6.1.min.js"
  );

  function applyColorScheme() {
    const scheme = darkMode.matches ? "dark" : "light";
    baseLayerLuminance.setValueFor(
      provider,
      darkMode.matches ? StandardLuminance.DarkMode : StandardLuminance.LightMode,
    );
    document.documentElement.dataset.colorScheme = scheme;
  }

  applyColorScheme();
  darkMode.addEventListener("change", applyColorScheme);
  await new Promise((resolve) => requestAnimationFrame(resolve));
  for (const token of [
    accentStrokeControlRest,
    accentStrokeControlHover,
    accentStrokeControlActive,
    accentStrokeControlFocus,
  ]) {
    token.setValueFor(provider, "transparent");
  }
} catch (error) {
  fluentLoadError = error;
  document.documentElement.dataset.fluentUnavailable = "true";
  console.error("The Microsoft Fluent control library could not be loaded.", error);
}

await import("./app.js?v=20260913-fluent-product-v8");

if (fluentLoadError) {
  const alert = document.querySelector("#alert");
  alert.textContent =
    "Microsoft Fluent controls could not load. Check the content security and network policy, then reload.";
  alert.hidden = false;
  alert.focus();
}
