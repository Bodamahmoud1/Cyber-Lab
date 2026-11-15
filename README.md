# 🛡️ SE-Labs: Social Engineering Interactive Platform
## Cybersecurity — Lecture 6 | By : Abdelrahman Hanfy | Ain Shams University

A modern, comprehensive, hands-on laboratory environment designed specifically for computer science students to visualize and simulate social engineering attacks and defenses practically.

---

## ⚡ Quick Start: Modern Web Platform (Recommended)

1. Double-click **`RUN_WEB_UI.bat`** (or run `python app.py`)
2. Open your browser to **`http://127.0.0.1:5500`**
3. Access all 8 interactive labs directly from a web UI matching the dark cyber CTF theme!

Alternatively, double-click **`START_LABS.bat`** for a combined menu supporting both Web UI and standalone CLI/Terminal simulators.

---

## 🔬 Interactive Labs Overview

```
SE-Labs/
├── RUN_WEB_UI.bat                        ← One-click web platform launcher
├── START_LABS.bat                        ← All-in-one terminal & web launcher
├── app.py                                ← Flask web application backend
├── templates/                            ← Modern dark-theme UI templates
│   ├── base.html                         ← Navigation, status, responsive layout
│   ├── index.html                        ← Lab directory & hero dashboard
│   ├── lab1.html ... lab8.html           ← Individual lab interfaces
├── static/
│   ├── css/style.css                     ← Cyber dark glassmorphism theme
│   └── js/app.js                         ← Security helper utilities
│
├── lab1-phishing/                        ← Slides 5, 7–22
│   ├── header_analyzer.py               ← Sender, reply address, trigger, and link checks
│   ├── phishing_server.py               ← Localhost credential harvesting demo
│   └── *.eml                            ← 6 realistic attack samples (.eml)
│
├── lab2-redirection/                     ← Slides 28–29
│   ├── typosquatting_generator.py       ← Look-alike domain generator
│   └── open_redirect_simulator.py       ← Open redirect exploit & defense demo
│
├── lab3-pharming/                        ← Slides 30–31
│   └── pharming_simulator.py            ← Local hosts file & DNSSEC simulator
│
├── lab4-baiting-disinfo/                 ← Slides 33–34, 39
│   ├── canary_usb_simulator.py          ← USB bait drop & canary token listener
│   └── hoax_detector.py                 ← Misinformation vs Disinformation quiz
│
├── lab5-pretexting-osint/                ← Slides 23–26, 38, 45
│   └── pretexting_osint_lab.py          ← Help desk pretexting roleplay
│
├── lab6-watering-hole/                   ← Slide 36
│   └── watering_hole_simulator.py       ← Academic blog source diff & code review
│
├── lab7-physical-se/                     ← Slides 38–41
│   └── physical_se_quiz.py              ← Tailgating, shoulder surfing awareness
│
└── lab8-defense/                         ← Slides 44–45
    └── defense_dashboard.py             ← Tier-1 SOC analyst alert triage capstone
```

---

## 📑 Slide-to-Lab Curriculum Alignment

| Lab | Title | Lecture Slides | Interactive Capabilities |
|---|---|---|---|
| **Lab 1** | Phishing & Forensics | Slides 5, 7–22 | Generic and targeted phishing, realistic email/SMS previews, trigger cues, and URL inspection |
| **Lab 2** | Typosquatting & Redirection | Slides 28–29 | Look-alike previews and a real local HTTP 302 redirect to the mock sign-in page |
| **Lab 3** | Pharming & DNS Hijacking | Slides 30–31 | Compare local hosts-file changes and poisoned DNS; enable DNSSEC validation |
| **Lab 4** | Baiting & Disinformation | Slides 33–34, 39 | Hoax classification, free-offer bait, and a desktop USB simulation |
| **Lab 5** | Pretexting & Dumpster Diving | Slides 23–26, 38, 45 | Secure disposal choice plus phone/email/access-control roleplay scenarios |
| **Lab 6** | Watering Hole Attack | Slide 36 | Switch between a clean and compromised academic blog preview |
| **Lab 7** | Physical Security Awareness | Slides 38–41 | One physical security scenario at a time with a simple response choice |
| **Lab 8** | SOC Defense (Capstone) | Slides 44–45 | Alert triage plus a simulated awareness campaign and reporting metrics |

---

## 🔒 Safety & Ethics Guarantee
- Runs **100% locally** on `127.0.0.1`
- Zero external dependencies required (works with Python standard library or Flask)
- Completely sandboxed and safe for classroom demonstrations
"# Cyber-Lab" 
