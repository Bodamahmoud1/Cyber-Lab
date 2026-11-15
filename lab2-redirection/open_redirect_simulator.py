#!/usr/bin/env python3
"""
=============================================================================
  LAB 2 - TOOL B: Open Redirect Vulnerability Simulator
=============================================================================
  Course : Cybersecurity - Lecture 6: Social Engineering (Slides 28-29)
  Purpose: Demonstrates how attackers abuse open redirect vulnerabilities
           on trusted websites to redirect users to malicious pages.
  
  How it works:
    - A "trusted" login portal runs on http://127.0.0.1:8081
    - It has an unvalidated ?redirect= parameter
    - An attacker crafts a URL: http://127.0.0.1:8081/login?redirect=http://127.0.0.1:9090/evil
    - After "login", the user is sent to the attacker's page
  
  Usage  : python open_redirect_simulator.py
           Open: http://127.0.0.1:8081/login?redirect=http://127.0.0.1:9090/evil
=============================================================================
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import sys

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PART 1: THE "TRUSTED" PORTAL (Vulnerable to Open Redirect)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TRUSTED_LOGIN_PAGE = """<!DOCTYPE html>
<html>
<head><title>University Portal - Login</title>
<style>
    body {{ font-family: Arial; background: #f5f5f5; }}
    .header {{ background: #003366; color: white; padding: 15px; text-align: center; }}
    .container {{ max-width: 400px; margin: 40px auto; background: white;
                  padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
    input {{ width: 100%; padding: 10px; margin: 8px 0; border: 1px solid #ddd;
             border-radius: 4px; box-sizing: border-box; }}
    button {{ width: 100%; padding: 12px; background: #003366; color: white;
              border: none; border-radius: 4px; font-size: 16px; cursor: pointer; }}
    .url-bar {{ background: #e8e8e8; padding: 8px; border-radius: 4px;
                font-family: monospace; font-size: 12px; word-break: break-all;
                margin-bottom: 20px; }}
    .safe-badge {{ color: green; font-weight: bold; }}
</style>
</head>
<body>
<div class="header">
    <h2>🎓 Ain Shams University — Student Portal</h2>
</div>
<div class="container">
    <div class="url-bar">
        <span class="safe-badge">🔒 Trusted URL:</span><br/>
        127.0.0.1:8081/login?redirect={redirect_url}
    </div>
    <p>Please log in to continue:</p>
    <form method="POST" action="/do-login?redirect={redirect_url}">
        <input type="text" name="username" placeholder="University Email" value="student@cis.asu.edu.eg">
        <input type="password" name="password" placeholder="Password" value="password123">
        <button type="submit">🔐 Log In</button>
    </form>
    <p style="font-size: 11px; color: #999;">
        [LAB NOTE: Notice the ?redirect= parameter in the URL above.
        The portal will redirect you there after login WITHOUT validation.]
    </p>
</div>
</body>
</html>"""

REDIRECT_NOTICE = """<!DOCTYPE html>
<html><head><title>Redirecting...</title>
<meta http-equiv="refresh" content="2;url={url}">
</head>
<body style="font-family: Arial; text-align: center; padding: 50px;">
<h2>✅ Login Successful!</h2>
<p>Redirecting you to your requested page...</p>
<p style="font-family: monospace; color: #666;">→ {url}</p>
<p style="font-size: 12px;">If not redirected automatically, <a href="{url}">click here</a>.</p>
</body></html>"""


class TrustedPortalHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        redirect_url = params.get('redirect', ['http://127.0.0.1:8081/dashboard'])[0]
        
        if parsed.path == '/login':
            page = TRUSTED_LOGIN_PAGE.format(redirect_url=redirect_url)
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(page.encode())
        elif parsed.path == '/dashboard':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<h1>University Dashboard (Safe Page)</h1>")
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        redirect_url = params.get('redirect', ['http://127.0.0.1:8081/dashboard'])[0]
        
        # VULNERABILITY: No validation of redirect URL!
        # In a real fix, you would whitelist allowed redirect domains.
        print(f"\n  [TRUSTED PORTAL] Login submitted. Redirecting to: {redirect_url}")
        
        page = REDIRECT_NOTICE.format(url=redirect_url)
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(page.encode())
    
    def log_message(self, format, *args):
        pass


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PART 2: THE ATTACKER'S EVIL PAGE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EVIL_PAGE = """<!DOCTYPE html>
<html>
<head><title>Session Expired</title>
<style>
    body { font-family: Arial; background: #f5f5f5; }
    .header { background: #003366; color: white; padding: 15px; text-align: center; }
    .container { max-width: 400px; margin: 40px auto; background: white;
                 padding: 30px; border-radius: 8px; }
    input { width: 100%; padding: 10px; margin: 8px 0; border: 1px solid #ddd;
            border-radius: 4px; box-sizing: border-box; }
    button { width: 100%; padding: 12px; background: #cc0000; color: white;
             border: none; border-radius: 4px; cursor: pointer; }
    .evil-notice { background: #ffe6e6; border: 2px solid red; padding: 15px;
                   border-radius: 5px; margin-top: 20px; }
</style>
</head>
<body>
<div class="header">
    <h2>🎓 Ain Shams University — Session Expired</h2>
</div>
<div class="container">
    <p>⚠️ Your session has expired. Please re-enter your credentials.</p>
    <input type="text" placeholder="University Email">
    <input type="password" placeholder="Password">
    <button>🔐 Re-authenticate</button>
    
    <div class="evil-notice">
        <h3>🚨 LAB ALERT: THIS IS THE ATTACKER'S PAGE!</h3>
        <p>You were redirected here from the <b>trusted portal</b> via an
        <b>Open Redirect vulnerability</b>.</p>
        <p>Notice: The URL bar now shows <b>127.0.0.1:9090</b> (attacker's server),
        NOT <b>127.0.0.1:8081</b> (trusted portal).</p>
        <p><b>Attack Flow:</b></p>
        <ol>
            <li>Attacker crafts link: trusted-site.com/login?redirect=evil-site.com</li>
            <li>Victim sees trusted domain, clicks the link</li>
            <li>Victim logs in on the REAL site</li>
            <li>After login, victim is silently redirected to attacker's clone page</li>
            <li>Victim re-enters credentials on the fake "session expired" page</li>
        </ol>
        <p><b>🛡️ Fix:</b> Validate redirect URLs against a whitelist of allowed domains.</p>
    </div>
</div>
</body>
</html>"""


class EvilPageHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(f"\n  [EVIL SERVER] Victim arrived at attacker's page!")
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(EVIL_PAGE.encode())
    
    def log_message(self, format, *args):
        pass


def main():
    print("=" * 70)
    print("  🔄 OPEN REDIRECT LAB SIMULATOR")
    print("=" * 70)
    print(f"  Trusted Portal  : http://127.0.0.1:8081/login")
    print(f"  Attacker's Page : http://127.0.0.1:9090/evil")
    print(f"")
    print(f"  📋 TEST STEPS:")
    print(f"  1. Open this SAFE link (no redirect attack):")
    print(f"     http://127.0.0.1:8081/login")
    print(f"")
    print(f"  2. Now open this MALICIOUS link (with open redirect):")
    print(f"     http://127.0.0.1:8081/login?redirect=http://127.0.0.1:9090/evil")
    print(f"")
    print(f"  3. Log in on both — see where you end up!")
    print(f"")
    print(f"  Press Ctrl+C to stop.")
    print("=" * 70)
    
    # Start both servers
    trusted = HTTPServer(('127.0.0.1', 8081), TrustedPortalHandler)
    evil = HTTPServer(('127.0.0.1', 9090), EvilPageHandler)
    
    t1 = threading.Thread(target=trusted.serve_forever, daemon=True)
    t2 = threading.Thread(target=evil.serve_forever, daemon=True)
    t1.start()
    t2.start()
    
    try:
        t1.join()
    except KeyboardInterrupt:
        print("\n  Servers stopped.")
        trusted.server_close()
        evil.server_close()


if __name__ == '__main__':
    main()
