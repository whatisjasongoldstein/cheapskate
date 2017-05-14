// Link selectors
document.addEventListener("change", function(e) {
  if (e.target.getAttribute("data-widget") === "url-selector") {
    let url = e.target.value;
    if (!url.startsWith("http://") && !url.startsWith("https://")) {
      url = `${window.location.protocol}//${window.location.host}${url}`;
    }
    window.location.href = url;
  }
});

document.addEventListener("change", function(e) {
  if (e.target.getAttribute("data-widget") === "anchor-selector") {
    window.location.hash = e.target.value;
  }
});

document.addEventListener("click", function(e) {
  if (e.target.getAttribute("data-widget") === "confirm-button") {
    let message = e.target.getAttribute("data-confirm-message") || "Are you sure?";
    if (window.confirm(message)) {
      return;
    } else {
      e.preventDefault();
      e.stopPropagation();
    }
  }
});

// Toggles elements that match a selector
document.addEventListener("click", function(e) {
  if (e.target.getAttribute("data-widget") === "toggler") {
    let selector = e.target.getAttribute("data-target");
    let els = document.querySelectorAll(selector);
    els.forEach(function(el) {
      let display = el.style.display;
      el.style.display = (display === "none") ? "block" : "none";
    });
    e.preventDefault();
    e.stopPropagation();
  }
});