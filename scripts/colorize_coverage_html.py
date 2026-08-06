#!/usr/bin/env python3
"""Post-process coverage HTML: badge colors by percentage + legend."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTMLCOV = ROOT / "htmlcov"
JS_NAME = "cov_colors.js"

JS = r"""
(function () {
  function band(pct) {
    if (pct >= 90) return "cov-high";
    if (pct >= 70) return "cov-mid";
    if (pct >= 40) return "cov-low";
    return "cov-none";
  }

  function pctFromRatio(el) {
    const raw = el.getAttribute("data-ratio");
    if (!raw) return null;
    const parts = raw.trim().split(/\s+/).map(Number);
    if (parts.length !== 2 || parts.some(Number.isNaN)) return null;
    const [hit, total] = parts;
    if (total === 0) return 100;
    return (100 * hit) / total;
  }

  function pctFromText(el) {
    const m = String(el.textContent || "").match(/([\d.]+)\s*%/);
    return m ? Number(m[1]) : null;
  }

  document.querySelectorAll("td[data-ratio], span.pc_cov").forEach((el) => {
    const pct = pctFromRatio(el) ?? pctFromText(el);
    if (pct === null || Number.isNaN(pct)) return;
    el.classList.remove("cov-high", "cov-mid", "cov-low", "cov-none");
    el.classList.add(band(pct));
  });

  const header = document.querySelector("header .content");
  if (header && !header.querySelector(".cov-legend")) {
    const legend = document.createElement("p");
    legend.className = "cov-legend";
    legend.innerHTML =
      '<span class="cov-high">&ge;90%</span>' +
      '<span class="cov-mid">70–89%</span>' +
      '<span class="cov-low">40–69%</span>' +
      '<span class="cov-none">&lt;40%</span>';
    header.appendChild(legend);
  }
})();
"""

SCRIPT_TAG = f'<script src="{JS_NAME}"></script>'


def main() -> None:
    if not HTMLCOV.is_dir():
        raise SystemExit(f"Missing {HTMLCOV}; run coverage HTML report first.")

    (HTMLCOV / JS_NAME).write_text(JS, encoding="utf-8")

    for path in HTMLCOV.glob("*.html"):
        html = path.read_text(encoding="utf-8")
        if JS_NAME in html:
            continue
        if "</body>" in html:
            html = html.replace("</body>", f"  {SCRIPT_TAG}\n</body>", 1)
        else:
            html += f"\n{SCRIPT_TAG}\n"
        path.write_text(html, encoding="utf-8")

    print(f"Colorized coverage HTML in {HTMLCOV}")


if __name__ == "__main__":
    main()
