// PWA: install button and update banner.
(function () {
  const installBtn = document.getElementById("install-btn");
  const iosHint = document.getElementById("ios-hint");
  const banner = document.getElementById("update-banner");
  const reloadBtn = document.getElementById("update-reload");

  const standalone =
    window.matchMedia("(display-mode: standalone)").matches ||
    window.navigator.standalone === true;

  // Install
  let deferred = null;
  window.addEventListener("beforeinstallprompt", (e) => {
    e.preventDefault();
    deferred = e;
    if (!standalone) installBtn.hidden = false;
  });
  installBtn.addEventListener("click", async () => {
    if (!deferred) return;
    deferred.prompt();
    await deferred.userChoice;
    deferred = null;
    installBtn.hidden = true;
  });
  window.addEventListener("appinstalled", () => {
    installBtn.hidden = true;
    iosHint.hidden = true;
  });
  const ua = navigator.userAgent;
  const isIOS = /iPad|iPhone|iPod/.test(ua) || (ua.includes("Mac") && navigator.maxTouchPoints > 1);
  if (isIOS && !standalone) iosHint.hidden = false;

  // Update
  if (!("serviceWorker" in navigator)) return;
  let reloading = false;
  navigator.serviceWorker.addEventListener("controllerchange", () => {
    if (reloading || !window.__hadController) return;
    reloading = true;
    location.reload();
  });
  window.__hadController = !!navigator.serviceWorker.controller;

  function showUpdate(worker) {
    banner.hidden = false;
    reloadBtn.onclick = () => worker.postMessage({ type: "SKIP_WAITING" });
  }
  function track(reg) {
    if (reg.waiting && navigator.serviceWorker.controller) showUpdate(reg.waiting);
    reg.addEventListener("updatefound", () => {
      const w = reg.installing;
      if (!w) return;
      w.addEventListener("statechange", () => {
        if (w.state === "installed" && navigator.serviceWorker.controller) showUpdate(w);
      });
    });
    reg.update().catch(() => {});
  }
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("sw.js").then(track).catch(() => {});
  });
})();
