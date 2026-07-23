#!/usr/bin/env python3
"""
Drag & Drop Server - Serves visual editor and auto-builds

Run: python editor_server.py
Open: http://localhost:5000

- Serves visual_editor.html
- POST /api/build receives JSON spec -> generates Android project -> tries to build APK
"""
import json
import sys
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse

# Import builder functions - V3 Compose
from builder import create_project, attempt_build, load_config
# alias for backward compat
create_android_project = create_project

PORT = 5000
ROOT = Path(__file__).parent

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.path = "/visual_editor.html"
        return super().do_GET()

    def do_POST(self):
        if self.path == "/api/build":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                config = json.loads(body)
                # Save spec
                spec_path = ROOT / "app_spec.json"
                spec_path.write_text(json.dumps(config, indent=2))
                print(f"\n📩 Received new spec from editor: {config['app_name']}")

                # Generate project
                output_dir = ROOT / "GeneratedAndroidApp"
                create_android_project(config, output_dir)

                # Attempt auto build
                built = attempt_build(output_dir)
                apk_path = None
                if built:
                    dist_apk = ROOT / "dist" / f"{output_dir.name}.apk"
                    if dist_apk.exists():
                        apk_path = str(dist_apk.resolve())
                else:
                    apk_search = list((output_dir / "app/build").rglob("*.apk"))
                    if apk_search:
                        apk_path = str(apk_search[0])

                resp = {
                    "status": "success" if built else "generated",
                    "message": f"✅ Project generated{' & APK built!' if built else ' (Install JDK/Android SDK to auto-build APK)'}",
                    "project_path": str(output_dir.resolve()),
                    "spec_path": str(spec_path.resolve()),
                    "apk_path": apk_path,
                    "next_steps": "Open GeneratedAndroidApp in Android Studio or run with --build"
                }
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(resp).encode())
                
            except Exception as e:
                import traceback
                traceback.print_exc()
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status":"error","message":str(e)}).encode())
        else:
            self.send_error(404)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

if __name__ == "__main__":
    print(f"""
╔══════════════════════════════════════════════════╗
║  PYTHON ANDROID FACTORY - Drag & Drop + Auto Build
╠══════════════════════════════════════════════════╣
║  Editor:  http://localhost:{PORT}
║  Builder: python builder.py --spec app_spec.json --build
║
║  1. Open the editor in browser
║  2. Drag widgets to phone
║  3. Click "Save & Auto-Build APK"
║  4. Project -> GeneratedAndroidApp/
║     APK (if SDK installed) -> dist/*.apk
╚══════════════════════════════════════════════════╝
    """)
    # Try to check for existing spec and generate once
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
