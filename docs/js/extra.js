/* docs/js/extra.js */

// ── Tab preference persistence ─────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  const STORAGE_KEY = "cb-selected-tab";

  function restoreTabs() {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (!saved) return;
    document.querySelectorAll(".tabbed-set label").forEach(label => {
      if (label.textContent.trim() === saved) label.click();
    });
  }

  function bindTabSave() {
    document.querySelectorAll(".tabbed-set label").forEach(label => {
      label.addEventListener("click", () => {
        localStorage.setItem(STORAGE_KEY, label.textContent.trim());
      });
    });
  }

  restoreTabs();
  bindTabSave();

  // ── Backend selector on Quick Start page ──────────────
  const selector = document.getElementById("cb-backend-selector");
  if (selector) {
    selector.addEventListener("change", e => {
      const chosen = e.target.value;
      document.querySelectorAll("[data-backend]").forEach(el => {
        el.style.display = el.dataset.backend === chosen || chosen === "all" ? "" : "none";
      });
    });
  }

  // ── Animated terminal demo ─────────────────────────────
  initTerminalDemo("cb-terminal-demo", [
    { text: "$ cb vault get myapp/database", cls: "prompt" },
    { text: '{\n  "user": "admin",\n  "pass": "••••••••"\n}', cls: "output", instant: true },
    { text: "$ cb env add DB_URL --secret DB_URL=postgres://localhost/mydb", cls: "prompt" },
    { text: "✓ Secret DB_URL added to .env", cls: "success", instant: true },
    { text: "$ cb keyring get api_key --service-name myapp", cls: "prompt" },
    { text: '{\n  "api_key": "sk-••••••••"\n}', cls: "output", instant: true },
  ]);
});

function initTerminalDemo(containerId, lines, delayMs) {
  delayMs = delayMs || 40;
  var el = document.getElementById(containerId);
  if (!el) return;

  var lineIndex = 0;
  var charIndex = 0;

  function typeNextChar() {
    if (lineIndex >= lines.length) {
      var cursor = document.createElement("span");
      cursor.className = "cursor";
      el.appendChild(cursor);
      return;
    }
    var line = lines[lineIndex];
    var text = line.text;
    var cls = line.cls || "";
    var instant = line.instant || false;

    var span = el.querySelector('[data-line="' + lineIndex + '"]');
    if (!span) {
      span = document.createElement("div");
      if (cls) span.className = cls;
      span.setAttribute("data-line", lineIndex);
      el.appendChild(span);
    }

    if (instant) {
      span.textContent = text;
      charIndex = 0;
      lineIndex++;
      setTimeout(typeNextChar, delayMs * 3);
    } else {
      if (charIndex < text.length) {
        span.textContent = text.slice(0, charIndex + 1);
        charIndex++;
        setTimeout(typeNextChar, delayMs);
      } else {
        charIndex = 0;
        lineIndex++;
        setTimeout(typeNextChar, delayMs * 3);
      }
    }
  }

  typeNextChar();
}
