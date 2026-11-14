"""
Frontend Smoke Test
Verifies that:
1. Production dist build exists with index.html, JS bundles, and CSS stylesheets.
2. index.html contains necessary mount points (#root) and font links.
3. Bundle assets are valid and non-empty.
"""

import os
import sys

FRONTEND_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(FRONTEND_DIR, "dist")
INDEX_HTML = os.path.join(DIST_DIR, "index.html")
ASSETS_DIR = os.path.join(DIST_DIR, "assets")

def test_build_artifacts():
    print("Testing frontend build artifacts...")
    assert os.path.exists(DIST_DIR), f"Dist folder {DIST_DIR} not found. Run npm run build."
    assert os.path.exists(INDEX_HTML), f"Index HTML {INDEX_HTML} not found."
    assert os.path.exists(ASSETS_DIR), f"Assets folder {ASSETS_DIR} not found."

    with open(INDEX_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    assert '<div id="root"></div>' in html, "Missing #root mount point in index.html"
    assert "VibeCheck" in html, "Missing app title in index.html"
    assert "JetBrains+Mono" in html, "Missing JetBrains Mono font link in index.html"

    assets = os.listdir(ASSETS_DIR)
    js_files = [f for f in assets if f.endswith(".js")]
    css_files = [f for f in assets if f.endswith(".css")]

    assert len(js_files) > 0, "No compiled JS bundle found in dist/assets"
    assert len(css_files) > 0, "No compiled CSS bundle found in dist/assets"

    js_path = os.path.join(ASSETS_DIR, js_files[0])
    css_path = os.path.join(ASSETS_DIR, css_files[0])

    assert os.path.getsize(js_path) > 100000, f"JS bundle size unexpectedly small ({os.path.getsize(js_path)} bytes)"
    assert os.path.getsize(css_path) > 5000, f"CSS bundle size unexpectedly small ({os.path.getsize(css_path)} bytes)"

    print(f"PASS: index.html verified ({len(html)} chars)")
    print(f"PASS: JS bundle verified ({js_files[0]}, {os.path.getsize(js_path):,} bytes)")
    print(f"PASS: CSS bundle verified ({css_files[0]}, {os.path.getsize(css_path):,} bytes)")
    print("Frontend smoke test successfully PASSED!")

if __name__ == "__main__":
    test_build_artifacts()

