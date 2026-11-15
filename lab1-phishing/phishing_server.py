#!/usr/bin/env python3
"""
=============================================================================
  LAB 1 - TOOL B: Local Phishing Page Simulator (Credential Harvester Demo)
=============================================================================
  Course : Cybersecurity - Lecture 6: Social Engineering
  Purpose: Demonstrates how a phishing page captures credentials.
           Runs ONLY on localhost (127.0.0.1:8080). No external access.
  
  ⚠️  EDUCATIONAL USE ONLY — Runs in an isolated lab environment.
  
  Usage  : python phishing_server.py
           Then open http://127.0.0.1:8080 in a browser.
=============================================================================
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
import datetime
import json
import os

PORT = 8080
LOG_FILE = "captured_credentials_log.json"

PHISHING_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>University Account Verification</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f0f2f5; margin: 0; }
        .header { background: #003366; color: white; padding: 20px; text-align: center; }
        .header h1 { margin: 0; font-size: 22px; }
        .container { max-width: 420px; margin: 40px auto; background: white;
                     padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .warning-box { background: #fff3cd; border: 1px solid #ffc107; padding: 12px;
                       border-radius: 4px; margin-bottom: 20px; font-size: 14px; color: #856404; }
        label { display: block; margin: 15px 0 5px; font-weight: bold; color: #333; }
        input[type="text"], input[type="password"] {
            width: 100%; padding: 10px; border: 1px solid #ddd;
            border-radius: 4px; box-sizing: border-box; font-size: 14px; }
        input[type="submit"] {
            width: 100%; padding: 12px; background: #cc0000; color: white;
            border: none; border-radius: 4px; font-size: 16px; cursor: pointer;
            margin-top: 20px; }
        input[type="submit"]:hover { background: #aa0000; }
        .footer { text-align: center; color: #999; font-size: 12px; margin-top: 20px; }
        .timer { color: red; font-weight: bold; text-align: center; font-size: 18px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎓 Ain Shams University — IT Security Portal</h1>
    </div>
    <div class="container">
        <div class="warning-box">
            ⚠️ <b>Security Alert:</b> Your account requires immediate verification
            due to a recent security incident. Failure to verify within
            <span class="timer" id="countdown">29:59</span> will result in
            permanent suspension.
        </div>
        <form method="POST" action="/capture">
            <label>University Email:</label>
            <input type="text" name="email" placeholder="student@cis.asu.edu.eg" required>
            
            <label>Password:</label>
            <input type="password" name="password" placeholder="Enter your password" required>
            
            <label>Student ID:</label>
            <input type="text" name="student_id" placeholder="e.g., 20231234">
            
            <input type="submit" value="🔒 Verify My Account Now">
        </form>
        <div class="footer">
            <p>Ain Shams University — Faculty of Computer &amp; Information Science</p>
            <p style="color: #cc0000; font-weight: bold;">[THIS IS A LAB SIMULATION — NOT A REAL PAGE]</p>
        </div>
    </div>
    <script>
        // Fake urgency countdown timer (Psychological Trigger: Urgency)
        let time = 1799;
        setInterval(() => {
            if (time <= 0) return;
            time--;
            let m = Math.floor(time / 60);
            let s = time % 60;
            document.getElementById('countdown').textContent =
                m.toString().padStart(2,'0') + ':' + s.toString().padStart(2,'0');
        }, 1000);
    </script>
</body>
</html>"""

CAPTURED_PAGE = """<!DOCTYPE html>
<html>
<head><title>Lab Alert</title>
<style>
    body { font-family: Arial; background: #1a1a2e; color: #e94560;
           display: flex; justify-content: center; align-items: center;
           min-height: 100vh; margin: 0; }
    .alert-box { background: #16213e; padding: 40px; border-radius: 10px;
                 border: 2px solid #e94560; max-width: 600px; text-align: center; }
    h1 { color: #e94560; }
    .captured { background: #0f3460; padding: 15px; border-radius: 5px;
                margin: 20px 0; text-align: left; font-family: monospace;
                color: #a8d8ea; }
    .lesson { color: #e8e8e8; line-height: 1.8; }
    .trigger-list { text-align: left; color: #ffd700; }
</style>
</head>
<body>
<div class="alert-box">
    <h1>🚨 YOU JUST GOT PHISHED! 🚨</h1>
    <p style="font-size: 18px; color: #ffd700;">This is a <b>LAB SIMULATION</b>.
    In a real attack, your credentials would now be in an attacker's hands.</p>
    
    <div class="captured">
        <p>📋 <b>What was captured:</b></p>
        <p>  Email    : {email}</p>
        <p>  Password : {password}</p>
        <p>  Student ID: {student_id}</p>
        <p>  Time     : {timestamp}</p>
        <p>  IP       : {ip}</p>
    </div>
    
    <div class="lesson">
        <h3 style="color: #00d2ff;">📚 Psychological Triggers Used on This Page:</h3>
        <div class="trigger-list">
            <p>🎯 <b>Authority</b> — University branding & "IT Security Portal"</p>
            <p>🎯 <b>Urgency</b> — Countdown timer & "immediate verification"</p>
            <p>🎯 <b>Intimidation</b> — "permanent suspension" threat</p>
            <p>🎯 <b>Trust</b> — Official-looking university design</p>
        </div>
        <br/>
        <h3 style="color: #00d2ff;">🛡️ How to Defend:</h3>
        <p>✅ Always check the URL bar — this was 127.0.0.1, not asu.edu.eg</p>
        <p>✅ Look for HTTPS certificate warnings</p>
        <p>✅ Verify requests through official channels (call IT directly)</p>
        <p>✅ Never enter credentials from links in emails</p>
    </div>
</div>
</body>
</html>"""


class PhishHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(PHISHING_PAGE.encode())
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode()
        params = parse_qs(body)
        
        email_val = params.get('email', [''])[0]
        pass_val = params.get('password', [''])[0]
        sid_val = params.get('student_id', [''])[0]
        timestamp = datetime.datetime.now().isoformat()
        ip = self.client_address[0]
        
        # Log the captured data (for lab review)
        entry = {
            "timestamp": timestamp,
            "ip": ip,
            "email": email_val,
            "password": pass_val,
            "student_id": sid_val
        }
        
        # Append to log file
        with open(LOG_FILE, 'a') as f:
            f.write(json.dumps(entry) + "\n")
        
        print(f"\n  [CAPTURED] {timestamp}")
        print(f"    Email : {email_val}")
        print(f"    Pass  : {'*' * len(pass_val)}")
        print(f"    SID   : {sid_val}")
        print(f"    IP    : {ip}\n")
        
        # Show the "You Got Phished" educational page
        response = CAPTURED_PAGE.format(
            email=email_val,
            password='*' * len(pass_val) + f" ({len(pass_val)} chars)",
            student_id=sid_val or 'N/A',
            timestamp=timestamp,
            ip=ip
        )
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(response.encode())
    
    def log_message(self, format, *args):
        pass  # Suppress default access logs


def main():
    print("=" * 65)
    print("  🎣 PHISHING LAB SERVER — EDUCATIONAL SIMULATION")
    print("=" * 65)
    print(f"  Server running on: http://127.0.0.1:{PORT}")
    print(f"  Credential log   : {os.path.abspath(LOG_FILE)}")
    print(f"  Press Ctrl+C to stop the server.")
    print("=" * 65)
    print("\n  Waiting for victims... (open the URL in a browser)\n")
    
    server = HTTPServer(('127.0.0.1', PORT), PhishHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
        server.server_close()


if __name__ == '__main__':
    main()
