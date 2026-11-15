#!/usr/bin/env python3
"""
=============================================================================
  LAB 3: Pharming Attack Simulator (Local Hosts File + DNS Analysis)
=============================================================================
  Course : Cybersecurity - Lecture 6: Social Engineering (Slides 30-31)
  Purpose: Demonstrates pharming by showing how hosts file tampering
           redirects legitimate URLs to attacker-controlled IPs,
           and provides DNS verification commands.
  
  ⚠️  EDUCATIONAL USE ONLY — Uses a SIMULATED hosts file, does NOT
      modify your real system hosts file.
  
  Usage  : python pharming_simulator.py
=============================================================================
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import os
import sys
import platform

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Simulated hosts file entries (what malware would add)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NORMAL_HOSTS = """# Normal /etc/hosts or C:\\Windows\\System32\\drivers\\etc\\hosts
#
# localhost name resolution
127.0.0.1       localhost
::1             localhost

# Nothing else — DNS resolution works normally via your ISP's DNS server.
"""

COMPROMISED_HOSTS = """# COMPROMISED hosts file (modified by malware)
#
127.0.0.1       localhost
::1             localhost

# ──── MALICIOUS ENTRIES ADDED BY MALWARE ────────────────────────────────
# These entries override DNS resolution BEFORE the system queries any
# DNS server. The browser will connect to 185.99.44.33 (attacker's IP)
# when the user types these legitimate URLs:

185.99.44.33    www.mybank.com
185.99.44.33    mybank.com
185.99.44.33    login.mybank.com
185.99.44.33    portal.university.edu
185.99.44.33    mail.company.com

# ──── END MALICIOUS ENTRIES ─────────────────────────────────────────────
# The user sees the correct URL in the browser but connects to the attacker.
# If the attacker also has a valid-looking SSL certificate, even HTTPS won't help!
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PART 1: LEGITIMATE BANK PAGE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LEGIT_BANK_PAGE = """<!DOCTYPE html>
<html><head><title>MyBank - Secure Online Banking</title>
<style>
    body { font-family: Arial; background: #f0f8ff; margin: 0; }
    .header { background: #006633; color: white; padding: 20px; text-align: center; }
    .container { max-width: 450px; margin: 30px auto; background: white;
                 padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    .badge { background: #d4edda; border: 1px solid #28a745; padding: 10px;
             border-radius: 4px; text-align: center; color: #155724; }
    input { width: 100%; padding: 10px; margin: 8px 0; border: 1px solid #ddd;
            border-radius: 4px; box-sizing: border-box; }
    button { width: 100%; padding: 12px; background: #006633; color: white;
             border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
</style></head>
<body>
<div class="header"><h2>🏦 MyBank — Secure Online Banking</h2></div>
<div class="container">
    <div class="badge">✅ LEGITIMATE BANK SERVER (127.0.0.1:8082)</div>
    <h3>Welcome to MyBank Online</h3>
    <p>This is the <b>real</b> bank server. In normal conditions, when you type
    www.mybank.com, DNS resolves it to this server's IP.</p>
    <input type="text" placeholder="Account Number">
    <input type="password" placeholder="PIN">
    <button>Log In to Banking</button>
</div>
</body></html>"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PART 2: ATTACKER'S PHARMING CLONE PAGE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PHARMING_CLONE_PAGE = """<!DOCTYPE html>
<html><head><title>MyBank - Secure Online Banking</title>
<style>
    body { font-family: Arial; background: #f0f8ff; margin: 0; }
    .header { background: #006633; color: white; padding: 20px; text-align: center; }
    .container { max-width: 450px; margin: 30px auto; background: white;
                 padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    input { width: 100%; padding: 10px; margin: 8px 0; border: 1px solid #ddd;
            border-radius: 4px; box-sizing: border-box; }
    button { width: 100%; padding: 12px; background: #006633; color: white;
             border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
    .evil-reveal { background: #1a1a2e; color: #e94560; padding: 20px;
                   border-radius: 5px; margin-top: 20px; border: 2px solid #e94560; }
    .evil-reveal h3 { color: #ffd700; }
    .dns-compare { display: flex; gap: 15px; margin: 15px 0; }
    .dns-box { flex: 1; padding: 12px; border-radius: 5px; font-family: monospace; font-size: 13px; }
    .dns-legit { background: #d4edda; border: 1px solid #28a745; }
    .dns-evil { background: #ffe6e6; border: 1px solid #e94560; }
</style></head>
<body>
<div class="header"><h2>🏦 MyBank — Secure Online Banking</h2></div>
<div class="container">
    <p style="color: #999; font-size: 12px;">[This page looks IDENTICAL to the real bank]</p>
    <h3>Welcome to MyBank Online</h3>
    <input type="text" placeholder="Account Number">
    <input type="password" placeholder="PIN">
    <button onclick="document.getElementById('reveal').style.display='block'">Log In to Banking</button>
    
    <div id="reveal" style="display:none;" class="evil-reveal">
        <h3>🚨 PHARMING ATTACK — YOU ARE ON THE ATTACKER'S SERVER!</h3>
        <p>This page is served from <b>127.0.0.1:9091</b> (attacker's IP), NOT
        the real bank at <b>127.0.0.1:8082</b>.</p>
        
        <p><b>How the attack works (Lecture Slide 30):</b></p>
        <ol style="color: #e8e8e8; line-height: 1.8;">
            <li>Malware modifies the system's <code>hosts</code> file</li>
            <li>The entry maps <code>www.mybank.com → 185.99.44.33</code> (attacker's IP)</li>
            <li>User types the <b>correct URL</b> in the browser</li>
            <li>OS checks hosts file <b>BEFORE</b> querying DNS</li>
            <li>Browser connects to attacker's clone page instead</li>
            <li>User sees correct URL but is on a fake server</li>
        </ol>
        
        <div class="dns-compare">
            <div class="dns-box dns-legit">
                <b>✅ Normal Resolution:</b><br/>
                www.mybank.com<br/>→ DNS query<br/>→ 93.184.216.34 (real bank)
            </div>
            <div class="dns-box dns-evil">
                <b>❌ Pharmed Resolution:</b><br/>
                www.mybank.com<br/>→ hosts file override<br/>→ 185.99.44.33 (attacker!)
            </div>
        </div>
        
        <p style="color: #00d2ff;"><b>🛡️ Defense (Slide 31): DNSSEC</b><br/>
        DNSSEC adds cryptographic signatures to DNS records, ensuring responses
        are authentic and untampered. But it cannot prevent local hosts file attacks —
        that requires endpoint protection (antimalware, file integrity monitoring).</p>
    </div>
</div>
</body></html>"""


class LegitBankHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(LEGIT_BANK_PAGE.encode())
    def log_message(self, fmt, *args): pass


class PharmingCloneHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(PHARMING_CLONE_PAGE.encode())
    def log_message(self, fmt, *args): pass


def print_hosts_comparison():
    """Show students the difference between normal and compromised hosts files."""
    
    # Show the actual system hosts file location
    if platform.system() == 'Windows':
        hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
    else:
        hosts_path = "/etc/hosts"
    
    print(f"\n{'='*70}")
    print(f"  📂 HOSTS FILE ANALYSIS")
    print(f"  System hosts file location: {hosts_path}")
    print(f"{'='*70}")
    
    print(f"\n  ┌─── NORMAL HOSTS FILE ────────────────────────────────────────┐")
    for line in NORMAL_HOSTS.strip().split('\n'):
        print(f"  │  {line}")
    print(f"  └────────────────────────────────────────────────────────────────┘")
    
    print(f"\n  ┌─── COMPROMISED HOSTS FILE (after malware infection) ────────┐")
    for line in COMPROMISED_HOSTS.strip().split('\n'):
        color_line = line
        if '185.99.44.33' in line:
            color_line = f">>> {line}  <<<  MALICIOUS!"
        print(f"  │  {color_line}")
    print(f"  └────────────────────────────────────────────────────────────────┘")
    
    print(f"\n  📋 DNS VERIFICATION COMMANDS (run these to detect pharming):")
    print(f"  ─────────────────────────────────────────────────────────────────")
    
    if platform.system() == 'Windows':
        print(f"  # View your current hosts file:")
        print(f"  > type C:\\Windows\\System32\\drivers\\etc\\hosts")
        print(f"")
        print(f"  # Check DNS cache for suspicious entries:")
        print(f"  > ipconfig /displaydns")
        print(f"")
        print(f"  # Compare hosts file vs actual DNS resolution:")
        print(f"  > nslookup www.mybank.com")
        print(f"  > ping www.mybank.com")
        print(f"")
        print(f"  # Flush DNS cache to remove poisoned entries:")
        print(f"  > ipconfig /flushdns")
    else:
        print(f"  # View your current hosts file:")
        print(f"  $ cat /etc/hosts")
        print(f"")
        print(f"  # Compare hosts file vs actual DNS resolution:")
        print(f"  $ dig www.mybank.com +short")
        print(f"  $ nslookup www.mybank.com")
        print(f"  $ host www.mybank.com")
        print(f"")
        print(f"  # Check DNSSEC validation:")
        print(f"  $ dig www.mybank.com +dnssec +short")
        print(f"")
        print(f"  # Flush DNS cache:")
        print(f"  $ sudo systemd-resolve --flush-caches   # Linux")
        print(f"  $ sudo dscacheutil -flushcache           # macOS")


def main():
    print("=" * 70)
    print("  💊 PHARMING ATTACK LAB SIMULATOR")
    print("  Lecture 6: Slides 30-31 (Pharming, DNS Poisoning, DNSSEC)")
    print("=" * 70)
    
    # Show hosts file comparison
    print_hosts_comparison()
    
    print(f"\n{'='*70}")
    print(f"  🌐 STARTING WEB SERVERS")
    print(f"{'='*70}")
    print(f"  Legitimate Bank : http://127.0.0.1:8082  (real bank server)")
    print(f"  Attacker Clone  : http://127.0.0.1:9091  (pharming clone)")
    print(f"")
    print(f"  📋 EXERCISE:")
    print(f"  1. Open http://127.0.0.1:8082 — This is the REAL bank")
    print(f"  2. Open http://127.0.0.1:9091 — This is the ATTACKER's clone")
    print(f"  3. Notice they look IDENTICAL!")
    print(f"  4. Click 'Log In' on the attacker's page to see the reveal")
    print(f"  5. Run the DNS commands above to practice detection")
    print(f"")
    print(f"  In a real pharming attack, the hosts file makes BOTH URLs")
    print(f"  point to the attacker's IP — the user types the correct URL")
    print(f"  but lands on the clone.")
    print(f"")
    print(f"  Press Ctrl+C to stop.")
    print("=" * 70)
    
    # Start both servers
    legit = HTTPServer(('127.0.0.1', 8082), LegitBankHandler)
    evil = HTTPServer(('127.0.0.1', 9091), PharmingCloneHandler)
    
    t1 = threading.Thread(target=legit.serve_forever, daemon=True)
    t2 = threading.Thread(target=evil.serve_forever, daemon=True)
    t1.start()
    t2.start()
    
    try:
        t1.join()
    except KeyboardInterrupt:
        print("\n  Servers stopped.")
        legit.server_close()
        evil.server_close()


if __name__ == '__main__':
    main()
