"""
Social Engineering Labs - Web UI
================================
Interactive web-based labs for Cybersecurity Lecture 6: Social Engineering
By : Abdelrahman Hanfy — Ain Shams University

Run: python app.py
Open: http://127.0.0.1:5500
"""

from flask import Flask, request, jsonify, render_template, make_response, redirect
import secrets, json, re, os, email as email_lib, socket, platform, getpass, datetime, html as html_lib, subprocess
from email import policy
from email.parser import BytesParser
from collections import OrderedDict

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
HOSTS_FILE_PATH = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32", "drivers", "etc", "hosts")

# ═══════════════════════════════════════════════════════════════
#  DATA: Psychological Triggers (Slide 5)
# ═══════════════════════════════════════════════════════════════
TRIGGER_KEYWORDS = {
    "Authority":    ["CEO", "CFO", "Director", "IT Department", "Security Department",
                     "Management", "Executive", "President", "authorized", "official",
                     "law enforcement", "attorney", "legal counsel", "senior partner"],
    "Intimidation": ["suspended", "terminated", "disabled", "legal action",
                     "permanently", "violation", "consequences", "penalty",
                     "compliance", "failure to comply", "law enforcement"],
    "Urgency":      ["immediately", "urgent", "ASAP", "right away", "act fast",
                     "within 30 minutes", "within 24 hours", "within 48 hours",
                     "before end of business", "time-sensitive", "expires"],
    "Consensus":    ["everyone has", "all department", "all employees",
                     "already completed", "others have", "company-wide"],
    "Scarcity":     ["limited time", "only available", "last chance",
                     "exclusive", "remaining", "running out"],
    "Familiarity":  ["as we discussed", "following up on our", "per our conversation",
                     "you know me", "as you recall"],
    "Trust":        ["verified", "official", "secure", "legitimate", "trusted",
                     "certified", "authenticated", "confirm your identity"]
}

# Keyboard adjacency map for typosquatting
ADJACENT_KEYS = {
    'a':'qwsz','b':'vghn','c':'xdfv','d':'serfcx','e':'wrsdf','f':'drtgvc',
    'g':'ftyhbv','h':'gyujnb','i':'ujklo','j':'huiknm','k':'jiolm','l':'kop',
    'm':'njk','n':'bhjm','o':'iklp','p':'ol','q':'wa','r':'edft','s':'awedxz',
    't':'rfgy','u':'yhjik','v':'cfgb','w':'qase','x':'zsdc','y':'tghu','z':'asx'
}

HOMOGLYPHS = {
    'a':['а','ɑ'],'c':['с','ϲ'],'e':['е','ε'],'i':['і','1','l'],
    'l':['1','ⅼ'],'o':['о','0','ο'],'p':['р','ρ'],'s':['ѕ','ş'],
    'x':['х','χ'],'y':['у','ý'],'d':['ԁ'],'g':['ɡ'],'h':['һ'],
    'k':['κ'],'m':['м'],'n':['п'],'r':['г'],'t':['τ'],'w':['ω']
}

# ═══════════════════════════════════════════════════════════════
#  DATA: Hoax / Disinformation Scenarios (Slides 33-34)
# ═══════════════════════════════════════════════════════════════
HOAX_SCENARIOS = [
    {"id":1,"title":"Deadly Virus Hoax","source":"Email chain forward",
     "message":"⚠️ URGENT WARNING ⚠️\n\nA deadly virus called \"SULFNBK.EXE\" is spreading through the Internet!\nIf you find this file on your computer, DELETE IT IMMEDIATELY!\nIt will activate on December 25th and erase your entire hard drive.\nForward this to everyone you know! Microsoft has confirmed this threat.",
     "classification":"Disinformation","triggers":["Urgency","Authority (fake Microsoft claim)","Intimidation (data loss)","Consensus (forward to everyone)"],
     "explanation":"SULFNBK.EXE is a legitimate Windows system file. This hoax tricks users into deleting important system files."},
    {"id":2,"title":"Fake Critical Update","source":"Pop-up notification",
     "message":"🔒 CRITICAL SECURITY UPDATE REQUIRED\n\nYour Windows has 47 critical vulnerabilities.\nYour system is exposed to remote attacks.\n\nDownload this urgent patch: Security_Patch_KB5034441.exe\n\nFailure to install within 24 hours may result in data loss.\n\n- Microsoft Windows Security Team",
     "classification":"Disinformation","triggers":["Authority (Microsoft branding)","Urgency (24-hour deadline)","Intimidation (data loss)","Trust (looks official)"],
     "explanation":"Fake updates deliver malware. Real Windows updates come through Windows Update, not pop-up downloads."},
    {"id":3,"title":"Free WiFi Safety Tip","source":"Social media post",
     "message":"⚡ PSA: IMPORTANT WiFi SAFETY TIP ⚡\n\nHold your phone's WiFi button for 10 seconds to enable \"Enhanced Security Mode\" which protects you from ALL hackers on public WiFi!\n\nConfirmed by Apple and Google engineers.\nShare with friends and family! 🛡️",
     "classification":"Misinformation","triggers":["Authority (claimed expert confirmation)","Trust (appears helpful)","Consensus (share with everyone)"],
     "explanation":"No such 'Enhanced Security Mode' exists. Misinformation — the poster may believe it. Use a VPN on public WiFi instead."},
    {"id":4,"title":"Ransomware Phone Scam","source":"Phone call (Vishing)",
     "message":"[Phone rings]\n\n\"This is Agent Johnson from the Cybercrime Division. Your computer's IP address has been used in illegal activities. A warrant has been issued for your arrest.\n\nTo resolve this without prosecution, purchase $500 in Google Play gift cards and read me the card numbers.\n\nThis call is being recorded.\"",
     "classification":"Disinformation","triggers":["Authority (law enforcement)","Intimidation (arrest threat)","Urgency (immediate action)","Trust (caller ID spoofing)"],
     "explanation":"Classic vishing scam. Law enforcement NEVER demands payment via gift cards. Hang up and call police on their official number."},
    {"id":5,"title":"Chain Email Charity","source":"WhatsApp forward",
     "message":"🙏 Please Read and Share! 🙏\n\nFor every forward of this message, WhatsApp will donate $1 to children's cancer research. Mark Zuckerberg confirmed this.\n\nSo far shared 2.3 million times, raising $2.3M!\n\nDon't break the chain — a child's life depends on you. ❤️\nShare with at least 10 people!",
     "classification":"Misinformation","triggers":["Consensus (millions shared)","Trust (CEO attribution)","Familiarity (emotional appeal)"],
     "explanation":"No platform donates per-forward. Well-meaning but false. Check fact-checking sites like Snopes."}
]

# ═══════════════════════════════════════════════════════════════
#  DATA: Pretexting Scenarios (Slides 23-26, 45)
# ═══════════════════════════════════════════════════════════════
PRETEXTING_SCENARIOS = [
    {"id":1,"role":"IT Support Technician",
     "pretext":"Hi, this is Khaled from IT Support. We're doing emergency maintenance on the email server. I need your username and password to migrate your mailbox before we shut down the old server in 15 minutes.",
     "triggers":["Authority (IT Support)","Urgency (15 minutes)","Intimidation (lose email)"],
     "defense":["Ask for caller's employee ID","Call IT Help Desk on official number","IT never needs your password","Report the call to security"]},
    {"id":2,"role":"Bank Security Officer",
     "pretext":"Hello, I'm calling from your bank's fraud detection team. We've noticed suspicious transactions on your account. I need to verify your identity by confirming your account number, last 4 digits of your national ID, and your SMS OTP code.",
     "triggers":["Authority (bank)","Urgency (suspicious activity)","Trust (fraud prevention)","Intimidation (financial loss)"],
     "defense":["Hang up and call number on back of your bank card","Banks never ask for OTP codes by phone","Check your bank app directly","Report to bank's fraud department"]},
    {"id":3,"role":"Company CEO (Whaling/BEC)",
     "pretext":"This is Dr. Mohamed Kamal, the CFO. I'm in a meeting with our acquisition partners and I need you to process an urgent wire transfer of $157,000 immediately. This is highly confidential — do not discuss with anyone.",
     "triggers":["Authority (CFO)","Urgency (in meeting NOW)","Intimidation (confidential)","Trust (known executive name)"],
     "defense":["Dual-approval required for wire transfers","Call CFO on known official number","Follow approval procedures","'Don't tell anyone' is a MAJOR red flag"]},
    {"id":4,"role":"Vendor / Supplier",
     "pretext":"Hi, this is Sarah from ACME Suppliers. We've updated our banking details. Please update payment info in your system. Outstanding invoice of $42,750 needs payment to the new account within 48 hours.",
     "triggers":["Trust (known vendor)","Urgency (48-hour deadline)","Familiarity (existing relationship)"],
     "defense":["Call vendor on number in existing records","Verify through known contact at vendor","Callback procedure for payment changes","Check email domain for typosquatting"]}
]

# ═══════════════════════════════════════════════════════════════
#  DATA: SOC Alerts for Lab 8 (Slides 44-45)
# ═══════════════════════════════════════════════════════════════
SOC_ALERTS = [
    {"id":"ALERT-001","time":"08:23","source":"Email Gateway","severity":"HIGH","type":"Phishing",
     "desc":"Email impersonating the IT Department urges 47 students to avoid account suspension by opening a suspicious link.",
     "details":{"From":"ITDept@cis-asu.edu.eg","Link":"cis-asu-edu-eg.secur1ty-update.com/verify","Recipients":"47 students"},
     "actions":["Block sender IP at email gateway","Quarantine all 47 emails","Block phishing domain in DNS","Alert recipients","Report domain for takedown"]},
    {"id":"ALERT-002","time":"09:45","source":"Finance Report","severity":"CRITICAL","type":"BEC (CEO Fraud)",
     "desc":"Email from j.smith@compaany.com (typosquatting!) requesting urgent $157,000 wire transfer to 'RS Enterprise'.",
     "details":{"From":"j.smith@compaany.com","Real domain":"company.com","Amount":"$157,000","Cues":"'act fast', 'do NOT discuss'"},
     "actions":["Call real CEO on known number","DO NOT process transfer","Block typosquatted domain","Alert all finance staff","Implement dual-approval"]},
    {"id":"ALERT-003","time":"10:12","source":"EDR Alert","severity":"HIGH","type":"Pharming",
     "desc":"Hosts file modified on WS-FINANCE-03. New entry: 91.234.56.78 → portal.university.edu. USB connected 3 min prior.",
     "details":{"Workstation":"WS-FINANCE-03","File":"hosts","Entry":"91.234.56.78 portal.university.edu","Trigger":"USB device"},
     "actions":["Isolate workstation","Remove malicious hosts entry","Full malware scan","Quarantine USB","Check other machines","Reset credentials"]},
    {"id":"ALERT-004","time":"11:30","source":"Awareness Team","severity":"MEDIUM","type":"Disinformation",
     "desc":"Multiple employees forwarded hoax email claiming 'deadly virus SULFNBK.EXE'. Two employees already deleted the legitimate system file.",
     "details":{"Subject":"DELETE SULFNBK.EXE NOW!","Claim":"Microsoft confirmed deadly virus","Affected":"2 deletions, 23 forwards"},
     "actions":["Company-wide alert: KNOWN HOAX","Restore deleted files from backup","Block further forwarding","Micro-learning session","Update email gateway rules"]},
    {"id":"ALERT-005","time":"13:15","source":"Physical Security","severity":"MEDIUM","type":"Tailgating",
     "desc":"CCTV: Unknown person in technician uniform followed employee through badge-access door to server room. No visitor badge.",
     "details":{"Location":"Server Room B, 3rd Floor","Duration":"10 minutes","Description":"ISP uniform, toolbox","Let in by":"Ahmed Hassan"},
     "actions":["Dispatch security immediately","Audit server room for tampering","Interview Ahmed Hassan","Verify with ISP","Physical security retraining"]},
    {"id":"ALERT-006","time":"14:00","source":"IDS/Web Proxy","severity":"HIGH","type":"Watering Hole",
     "desc":"Suspicious JS on research-blog.university.edu: browser fingerprinting + hidden iframe loading exploit kit from evil-exploit-kit.com.",
     "details":{"Site":"research-blog.university.edu","Injection":"<script> + hidden <iframe>","Affected":"~120 visitors in 48h"},
     "actions":["Block compromised blog and exploit-kit domain","Notify blog admins","Use antimalware/EDR to scan affected visitors","Review IDS/IPS alerts","Deploy CSP headers"]}
]

# ═══════════════════════════════════════════════════════════════
#  DATA: Physical SE Quiz (Slides 38-41)
# ═══════════════════════════════════════════════════════════════
PHYSICAL_QUIZ = [
    {"id":1,"cat":"Tailgating & Piggybacking (Slide 40)",
     "scenario":"You're entering the server room. A person in a delivery uniform carrying boxes says: \"Hey, hold the door? My badge is in my pocket.\"",
     "options":["Hold the door — they're clearly a delivery person","Ask them to put down boxes and badge in themselves","Politely decline, close door, direct them to reception","Ask to see their badge and let them in if shown"],
     "correct":2,"explanation":"ALL visitors must badge in or be escorted. Carrying boxes and wearing uniforms are classic social engineering props."},
    {"id":2,"cat":"Shoulder Surfing (Slide 41)",
     "scenario":"You're at a coffee shop logging into your company VPN. People are sitting at tables behind and beside you.",
     "options":["Type normally — no one is paying attention","Use privacy screen filter + password manager autofill","Wait until no one is nearby, then type quickly","Ask people near you to look away"],
     "correct":1,"explanation":"Privacy screens limit viewing angles. Password managers auto-fill without visible typing. Always assume someone could be watching."},
    {"id":3,"cat":"Dumpster Diving (Slide 38)",
     "scenario":"You find an old invoice and an employee list in an unlocked recycling bin beside the office printer.",
     "options":["Read through them and leave them there","Put them in the regular recycling bin","Move them to a locked disposal bin for shredding","Take them home to shred later"],
     "correct":2,"explanation":"Sensitive printouts should go into locked bins or be shredded so dumpster divers cannot recover them."},
    {"id":4,"cat":"Baiting (Slide 39)",
     "scenario":"You find a USB drive in the parking lot labeled: \"CONFIDENTIAL — HR Salary Review 2025\"",
     "options":["Plug it into your work computer","Plug it into your personal computer","Turn it in to IT/Security WITHOUT plugging it in","Plug into an offline computer"],
     "correct":2,"explanation":"NEVER plug in unknown USB drives. Malware can execute instantly (autorun, firmware-level). IT has sandboxed environments for analysis."},
    {"id":5,"cat":"Combined Physical SE",
     "scenario":"A person in ISP technician uniform arrives: \"I'm from the ISP. Slow internet reports on this floor. Can you badge me into the server closet? Left my visitor pass at reception.\"",
     "options":["Badge them in — they look legitimate","Escort them personally to the server room","Tell them to get visitor pass from reception, then verify with ISP","Ask for their employee ID and let them in"],
     "correct":2,"explanation":"Combines pretexting + impersonation + tailgating. ALL visitors need passes. Call ISP on their OFFICIAL number to verify."}
]

# ═══════════════════════════════════════════════════════════════
#  HELPER: Email Analysis
# ═══════════════════════════════════════════════════════════════
def analyze_eml(filepath):
    """Full forensic analysis of an .eml file."""
    with open(filepath, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)

    result = {"headers":{},"domain_flags":[],"triggers":{},"urls":[],"hops":[]}

    # Headers
    for h in ['From','Reply-To','To','Subject','Date','Return-Path','Message-ID','X-Mailer','X-Priority']:
        v = msg.get(h)
        if v: result["headers"][h] = str(v)

    # Domain mismatch
    def get_domain(hdr):
        v = msg.get(hdr,'')
        m = re.search(r'@([\w\-\.]+)', str(v))
        return m.group(1).lower() if m else None

    from_d = get_domain('From')
    reply_d = get_domain('Reply-To')
    return_d = get_domain('Return-Path')
    result["domains"] = {"from":from_d,"reply_to":reply_d,"return_path":return_d}
    if from_d and reply_d and from_d != reply_d:
        result["domain_flags"].append(f"From=@{from_d} vs Reply-To=@{reply_d}")
    if from_d and return_d and from_d != return_d:
        result["domain_flags"].append(f"From=@{from_d} vs Return-Path=@{return_d}")

    # Hops
    for recv in msg.get_all('Received',[]):
        ip_m = re.search(r'\((?:[\w\-\.]+\s+)?\[?(\d+\.\d+\.\d+\.\d+)\]?\)', str(recv))
        from_m = re.search(r'from\s+([\w\-\.]+)', str(recv), re.I)
        by_m = re.search(r'by\s+([\w\-\.]+)', str(recv), re.I)
        result["hops"].append({"from":from_m.group(1) if from_m else "?","by":by_m.group(1) if by_m else "?","ip":ip_m.group(1) if ip_m else "?"})

    # Triggers
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() in ('text/plain','text/html'):
                p = part.get_payload(decode=True)
                if p: body += p.decode('utf-8',errors='replace')
    else:
        p = msg.get_payload(decode=True)
        if p: body = p.decode('utf-8',errors='replace')

    channel = "sms" if re.search(r'\[SMS\]|SIMULATED SMS MESSAGE', str(msg.get('Subject', '')) + " " + body, re.I) else "email"
    sms_sender = re.search(r'=== SIMULATED SMS MESSAGE.*?===\s*From:\s*([^\r\n]+)', body, re.I | re.S) if channel == "sms" else None
    sms_time = re.search(r'\bTime:\s*([^\r\n]+)', body, re.I) if channel == "sms" else None
    sms_body = re.search(r'\bTime:\s*[^\r\n]+\s*(.*?)(?=\r?\n(?:Reply STOP[^\r\n]*|=== END OF SMS ===))', body, re.I | re.S) if channel == "sms" else None
    analysis_body = sms_body.group(1).strip() if sms_body else body
    clean = re.sub(r'<[^>]+>',' ', str(msg.get('Subject',''))+" "+analysis_body)
    # Return a safe text-only preview for the mock mail client. Never render
    # untrusted email HTML or execute its links/scripts in the learning UI.
    preview = re.sub(r'(?is)<(script|style).*?>.*?</\1>', ' ', analysis_body)
    preview = re.sub(r'(?i)<br\s*/?>|</p>|</div>|</h[1-6]>', '\n', preview)
    preview = re.sub(r'<[^>]+>', ' ', preview)
    preview = html_lib.unescape(preview)
    result["message"] = {
        "from": sms_sender.group(1).strip() if sms_sender else str(msg.get('From', 'Unknown sender')),
        "to": str(msg.get('To', 'Unknown recipient')),
        "subject": str(msg.get('Subject', '(no subject)')),
        "date": sms_time.group(1).strip() if sms_time else str(msg.get('Date', '')),
        "body": '\n'.join(re.sub(r'[ \t]+', ' ', line).strip() for line in preview.splitlines() if line.strip())
    }
    result["channel"] = channel
    for trigger, kws in TRIGGER_KEYWORDS.items():
        found = [kw for kw in kws if re.search(re.escape(kw), clean, re.I)]
        if found: result["triggers"][trigger] = found

    # URLs
    result["urls"] = list(set(re.findall(r'href=["\']([^"\']+)["\']', analysis_body, re.I) + re.findall(r'https?://[^\s<>"\']+', analysis_body)))

    return result

# ═══════════════════════════════════════════════════════════════
#  HELPER: Typosquatting Generator
# ═══════════════════════════════════════════════════════════════
def generate_typosquats(domain):
    """Generate typosquatting variants."""
    # Split domain
    name, tld = domain, ''
    for mt in ['.edu.eg','.co.uk','.co.jp','.com.au']:
        if domain.endswith(mt):
            name, tld = domain[:-len(mt)], mt
            break
    if not tld:
        parts = domain.rsplit('.',1)
        if len(parts)==2: name, tld = parts[0], '.'+parts[1]

    variants = []
    # Omission
    for i in range(len(name)):
        v = name[:i]+name[i+1:]
        if v and v!=name: variants.append({"domain":v+tld,"type":"Omission","detail":f"removed '{name[i]}'"})
    # Adjacent swap
    for i in range(len(name)):
        ch = name[i].lower()
        if ch in ADJACENT_KEYS:
            for adj in ADJACENT_KEYS[ch][:2]:
                variants.append({"domain":name[:i]+adj+name[i+1:]+tld,"type":"Adjacent Key","detail":f"'{name[i]}'→'{adj}'"})
    # Duplication
    for i in range(len(name)):
        if name[i].isalpha():
            v = name[:i]+name[i]+name[i:]
            if v!=name: variants.append({"domain":v+tld,"type":"Duplication","detail":f"doubled '{name[i]}'"})
    # Swap
    for i in range(len(name)-1):
        v = name[:i]+name[i+1]+name[i]+name[i+2:]
        if v!=name: variants.append({"domain":v+tld,"type":"Swap","detail":f"'{name[i]}{name[i+1]}'→'{name[i+1]}{name[i]}'"})
    # Homoglyphs
    for i in range(len(name)):
        ch = name[i].lower()
        if ch in HOMOGLYPHS:
            h = HOMOGLYPHS[ch][0]
            variants.append({"domain":name[:i]+h+name[i+1:]+tld,"type":"Homoglyph","detail":f"'{name[i]}'→'{h}'"})
    # TLD
    for alt in ['.com','.net','.org','.co','.info','.xyz']:
        if alt!=tld: variants.append({"domain":name+alt,"type":"TLD Change","detail":f"{tld}→{alt}"})

    return variants[:60]

# ═══════════════════════════════════════════════════════════════
#  PAGE ROUTES
# ═══════════════════════════════════════════════════════════════
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/lab/<int:num>")
def lab_page(num):
    templates = {1:"lab1.html",2:"lab2.html",3:"lab3.html",4:"lab4.html",
                 5:"lab5.html",6:"lab6.html",7:"lab7.html",8:"lab8.html"}
    if num not in templates: return "Lab not found", 404
    if num == 3:
        return render_template(templates[num], hosts_file_path=HOSTS_FILE_PATH)
    return render_template(templates[num])

@app.route("/api/open-hosts", methods=["POST"])
def api_open_hosts():
    """Open the real Windows hosts file in Notepad for the local demonstration."""
    if platform.system() != "Windows":
        return jsonify({"error": "Opening the local hosts file is available on Windows only."}), 501
    if request.remote_addr not in ("127.0.0.1", "::1"):
        return jsonify({"error": "This action is only available from the local computer."}), 403
    if request.headers.get("Origin") != f"{request.scheme}://{request.host}":
        return jsonify({"error": "Open the file from the local SE-Labs page."}), 403
    if not os.path.isfile(HOSTS_FILE_PATH):
        return jsonify({"error": "The Windows hosts file was not found."}), 404
    try:
        subprocess.Popen(["notepad.exe", HOSTS_FILE_PATH], close_fds=True)
    except OSError as error:
        return jsonify({"error": f"Could not open Notepad: {error}"}), 500
    return jsonify({"opened": True, "path": HOSTS_FILE_PATH})

@app.route("/sim/open-redirect")
def sim_open_redirect():
    """Send the browser through a real, local-only 302 redirect for Lab 2."""
    local_targets = {"account-check": "/sim/account-check"}
    destination = local_targets.get(request.args.get("next"), "/sim/account-check")
    return redirect(destination, code=302)

@app.route("/sim/account-check")
def sim_account_check():
    return render_template("sim_login.html")

# ═══════════════════════════════════════════════════════════════
#  API ROUTES
# ═══════════════════════════════════════════════════════════════
@app.route("/api/analyze-email", methods=["POST"])
def api_analyze_email():
    """Analyze an .eml file."""
    data = request.json
    sample = data.get("sample","sample_phish_generic")
    eml_dir = os.path.join(os.path.dirname(__file__), "lab1-phishing")
    filepath = os.path.join(eml_dir, sample + ".eml")
    if not os.path.exists(filepath):
        return jsonify({"error": f"Sample '{sample}' not found"}), 404
    result = analyze_eml(filepath)
    return jsonify(result)

@app.route("/api/list-emails")
def api_list_emails():
    eml_dir = os.path.join(os.path.dirname(__file__), "lab1-phishing")
    files = []
    if os.path.isdir(eml_dir):
        for f in sorted(os.listdir(eml_dir)):
            if f.endswith('.eml'):
                name = f.replace('.eml','')
                label = name.replace('sample_','').replace('_',' ').title()
                files.append({"value":name,"label":label})
    return jsonify(files)

@app.route("/api/typosquat", methods=["POST"])
def api_typosquat():
    domain = request.json.get("domain","amazon.com").lower().strip()
    if not domain or len(domain)>100: return jsonify({"error":"Invalid domain"}), 400
    variants = generate_typosquats(domain)
    return jsonify({"domain":domain,"count":len(variants),"variants":variants})

@app.route("/api/hoax-scenarios")
def api_hoax_scenarios():
    return jsonify(HOAX_SCENARIOS)

@app.route("/api/pretexting-scenarios")
def api_pretexting_scenarios():
    return jsonify(PRETEXTING_SCENARIOS)

@app.route("/api/physical-quiz")
def api_physical_quiz():
    return jsonify(PHYSICAL_QUIZ)

@app.route("/api/soc-alerts")
def api_soc_alerts():
    return jsonify(SOC_ALERTS)

# ═══════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("  🛡️  Social Engineering Labs — Web UI")
    print("  Cybersecurity Lecture 6 — By : Abdelrahman Hanfy")
    print("  Ain Shams University")
    print("=" * 60)
    print(f"  Running at: http://127.0.0.1:5500")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5500, debug=True)
