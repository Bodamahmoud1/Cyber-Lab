#!/usr/bin/env python3
"""
=============================================================================
  LAB 8: Comprehensive Social Engineering Detection & Defense Dashboard
=============================================================================
  Course : Cybersecurity - Lecture 6: Social Engineering (Slides 44-45)
  Purpose: A comprehensive defense lab that brings together all previous
           labs. Students act as SOC analysts reviewing alerts from
           simulated attacks and must classify, analyze, and respond.
  
  Usage  : python defense_dashboard.py
=============================================================================
"""

import json
import datetime
import sys
import random

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Simulated SOC Alert Feed
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ALERTS = [
    {
        "id": "ALERT-001",
        "timestamp": "2025-11-15 08:23:15",
        "source": "Email Gateway",
        "severity": "HIGH",
        "description": "Email impersonating the IT Department uses urgency and a suspicious sign-in link. It was sent to 47 students in the Faculty of CIS.",
        "details": {
            "From": "ITDept@cis-asu.edu.eg",
            "Subject": "URGENT! Your University Account Will Be Disabled!",
            "Link": "http://cis-asu-edu-eg.secur1ty-update.com/verify",
            "Recipients": "47 students in Faculty of CIS"
        },
        "attack_type": "Phishing",
        "correct_classification": "Phishing (mass email targeting university students)",
        "correct_actions": [
            "BLOCK the sender IP (185.243.99.12) at the email gateway",
            "QUARANTINE all 47 emails before they reach inboxes",
            "BLOCK the phishing domain (secur1ty-update.com) in DNS/proxy",
            "Send ALERT to all 47 recipients: 'Do not click links from this email'",
            "Report the phishing domain to the registrar for takedown",
            "Check if any recipients already clicked (proxy/firewall logs)"
        ],
        "lecture_ref": "Slides 7-9 (Phishing + Psychological Triggers)"
    },
    {
        "id": "ALERT-002",
        "timestamp": "2025-11-15 09:45:00",
        "source": "Finance Department Report",
        "severity": "CRITICAL",
        "description": "Finance officer received email from CEO requesting urgent wire transfer of $157,000. Email came from j.smith@compaany.com (note: double 'a' in company name).",
        "details": {
            "From": "j.smith@compaany.com (typosquatting: compaany vs company)",
            "To": "judy.brown@acme-corp.com",
            "Request": "Wire $157,000 to 'RS Enterprise' escrow account",
            "Urgency Cues": "'Meeting starts in 5 minutes', 'act fast', 'do NOT discuss'"
        },
        "attack_type": "BEC (CEO Fraud)",
        "correct_classification": "Business Email Compromise — CEO/Executive Fraud (Slide 20)",
        "correct_actions": [
            "IMMEDIATELY call the real CEO on their known phone number to verify",
            "DO NOT process the wire transfer",
            "Flag the typosquatted domain (compaany.com) for blocking",
            "Alert all finance staff about this specific BEC attempt",
            "Implement dual-approval requirement for wire transfers > $10,000",
            "Preserve the email as evidence for potential law enforcement report"
        ],
        "lecture_ref": "Slides 18-20 (BEC, CEO Fraud)"
    },
    {
        "id": "ALERT-003",
        "timestamp": "2025-11-15 10:12:30",
        "source": "Endpoint Detection (EDR)",
        "severity": "HIGH",
        "description": "EDR alert: hosts file modification detected on workstation WS-FINANCE-03. New entry maps 'portal.university.edu' to external IP 91.234.56.78.",
        "details": {
            "Workstation": "WS-FINANCE-03 (Judy Brown's machine)",
            "File Modified": "C:\\Windows\\System32\\drivers\\etc\\hosts",
            "Entry Added": "91.234.56.78  portal.university.edu",
            "Process": "svchost.exe (suspicious — legitimate svchost doesn't modify hosts)",
            "Timeline": "Modification occurred 3 minutes after USB device was connected"
        },
        "attack_type": "Pharming (hosts file tampering)",
        "correct_classification": "Pharming Attack via malware (Slide 30) — likely from USB baiting",
        "correct_actions": [
            "ISOLATE the workstation from the network immediately",
            "Remove the malicious hosts file entry",
            "Scan the workstation for malware (full EDR scan)",
            "Identify and quarantine the USB device that was connected",
            "Check other workstations for similar hosts file modifications",
            "Reset the user's credentials (they may have been harvested)",
            "Flush DNS cache: ipconfig /flushdns"
        ],
        "lecture_ref": "Slides 30-31 (Pharming) + Slide 39 (Baiting)"
    },
    {
        "id": "ALERT-004",
        "timestamp": "2025-11-15 11:30:00",
        "source": "Security Awareness Team",
        "severity": "MEDIUM",
        "description": "Multiple employees forwarded an email claiming a 'deadly virus' is spreading and users should delete SULFNBK.EXE from their systems. Two employees already deleted the file.",
        "details": {
            "Subject": "URGENT VIRUS WARNING — DELETE SULFNBK.EXE NOW!",
            "Claims": "Microsoft confirmed deadly virus activating Dec 25",
            "Action Taken": "2 employees deleted the legitimate Windows system file",
            "Forward Count": "Email was forwarded internally 23 times"
        },
        "attack_type": "Disinformation (Hoax)",
        "correct_classification": "Disinformation/Hoax Attack (Slide 33)",
        "correct_actions": [
            "Send company-wide alert: This is a KNOWN HOAX — do NOT delete files",
            "Restore SULFNBK.EXE on the 2 affected machines from backup",
            "Block the email from further internal forwarding",
            "Conduct a micro-learning session on disinformation recognition",
            "Update the email gateway rules to flag 'delete this file' patterns",
            "Track which employees forwarded it for targeted training"
        ],
        "lecture_ref": "Slides 33-34 (Disinformation & Misinformation)"
    },
    {
        "id": "ALERT-005",
        "timestamp": "2025-11-15 13:15:00",
        "source": "Physical Security / CCTV",
        "severity": "MEDIUM",
        "description": "CCTV shows unknown individual in technician uniform followed an employee through the badge-access door to the server room. No visitor badge was issued.",
        "details": {
            "Location": "Server Room B, 3rd Floor",
            "Time": "13:05 — 13:15 (10 minutes inside)",
            "Description": "Male, ISP-branded uniform, carrying toolbox",
            "Employee Who Let In": "Ahmed Hassan (Finance Department)",
            "Visitor Badge": "NONE — no visitor log entry exists"
        },
        "attack_type": "Tailgating + Pretexting",
        "correct_classification": "Physical SE: Tailgating (Slide 40) + Pretexting (Slide 24)",
        "correct_actions": [
            "IMMEDIATELY dispatch security to the server room",
            "Check server room access logs and camera footage",
            "Audit all server room equipment for tampering (rogue devices, USB, network taps)",
            "Interview Ahmed Hassan (the employee who held the door)",
            "Verify with the ISP whether they dispatched a technician",
            "Conduct physical security retraining for all staff",
            "Consider implementing mantrap/airlock entry for server rooms"
        ],
        "lecture_ref": "Slides 24-25 (Pretexting) + Slide 40 (Tailgating)"
    },
    {
        "id": "ALERT-006",
        "timestamp": "2025-11-15 14:00:00",
        "source": "Web Proxy / IDS",
        "severity": "HIGH",
        "description": "IDS detected suspicious JavaScript execution on research-blog.university.edu. The blog appears to have been compromised: browser fingerprinting code and a hidden iframe loading an external exploit kit detected.",
        "details": {
            "Compromised Site": "research-blog.university.edu (academic research blog)",
            "Injection Type": "Injected <script> for browser fingerprinting + hidden <iframe>",
            "Exploit Kit URL": "evil-exploit-kit.com/deliver?target=university",
            "Affected Users": "~120 faculty/student visitors in the past 48 hours",
            "Detection Method": "IDS signature match on known exploit kit pattern"
        },
        "attack_type": "Watering Hole Attack",
        "correct_classification": "Watering Hole Attack (Slide 36)",
        "correct_actions": [
            "BLOCK the exploit kit domain (evil-exploit-kit.com) at proxy/DNS",
            "BLOCK access to the compromised blog until it's cleaned",
            "Notify the blog administrators to clean the injected code",
            "Scan all 120 visitors' machines with EDR for compromise indicators",
            "Check proxy logs for any successful exploit kit downloads",
            "Deploy browser-level protections (CSP, plugin updates)",
            "Alert all users to avoid the blog until further notice"
        ],
        "lecture_ref": "Slide 36 (Watering Hole Attack)"
    }
]


def run_soc_exercise():
    """Interactive SOC analyst exercise."""
    
    print("\n" + "=" * 75)
    print("  🛡️  SECURITY OPERATIONS CENTER (SOC) — ALERT TRIAGE EXERCISE")
    print("  Lecture 6: Slides 44-45 (Detection & Defense)")
    print("=" * 75)
    print("""
  📋 SCENARIO:
  You are a SOC analyst at ACME Corporation. Over the course of one day,
  you receive a series of security alerts. For each alert, you must:
  
  1. CLASSIFY the attack type (from Lecture 6 categories)
  2. Assess the SEVERITY and determine priority
  3. Define the RESPONSE ACTIONS
  
  The goal: Turn humans from the weakest link into ACTIVE SENSORS (Slide 44).
""")
    
    score = 0
    total = len(ALERTS)
    
    attack_types = [
        "Phishing", "Spear Phishing", "Whaling", "BEC (CEO Fraud)",
        "BEC (Invoice Fraud)", "Vishing", "Smishing", "Pretexting",
        "Typosquatting", "Pharming", "Disinformation (Hoax)",
        "Baiting", "Watering Hole", "Tailgating", "Shoulder Surfing",
        "Dumpster Diving"
    ]
    
    for alert in ALERTS:
        print(f"\n{'━'*75}")
        print(f"  🚨 {alert['id']} | Severity: {alert['severity']} | {alert['timestamp']}")
        print(f"  Source: {alert['source']}")
        print(f"{'━'*75}")
        print(f"\n  📝 Description:")
        print(f"  {alert['description']}")
        
        print(f"\n  📋 Details:")
        for key, val in alert['details'].items():
            print(f"     {key}: {val}")
        
        # Question: Classify the attack
        print(f"\n  ❓ What type of social engineering attack is this?")
        # Show shuffled options including the correct one
        options = random.sample([t for t in attack_types if t != alert['attack_type']], 3)
        options.append(alert['attack_type'])
        random.shuffle(options)
        
        for i, opt in enumerate(options):
            print(f"     [{i+1}] {opt}")
        
        try:
            answer = input(f"\n  Your classification (1-4): ").strip()
            answer_idx = int(answer) - 1
            chosen = options[answer_idx]
        except (ValueError, IndexError, EOFError, KeyboardInterrupt):
            print("\n  Exercise ended.")
            return
        
        if chosen == alert['attack_type']:
            print(f"  ✅ CORRECT! This is: {alert['correct_classification']}")
            score += 1
        else:
            print(f"  ❌ Incorrect. This is: {alert['correct_classification']}")
        
        print(f"\n  📖 Lecture Reference: {alert['lecture_ref']}")
        
        print(f"\n  🛡️ Correct Response Actions:")
        for i, action in enumerate(alert['correct_actions'], 1):
            print(f"     {i}. {action}")
        
        if alert != ALERTS[-1]:
            try:
                input("\n  Press Enter for next alert...")
            except (EOFError, KeyboardInterrupt):
                break
    
    pct = (score / total) * 100
    print(f"\n{'='*75}")
    print(f"  📊 SOC ANALYST SCORE: {score}/{total} ({pct:.0f}%)")
    print(f"{'='*75}")
    if pct == 100:
        print("  🏆 Excellent! You correctly classified all attack types!")
    elif pct >= 60:
        print("  👍 Good performance. Review the attack types you missed.")
    else:
        print("  📚 Review all sections of Lecture 6 for attack classifications.")
    
    print(f"""
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📚 KEY DEFENSE STRATEGIES (Lecture Slides 44-45):
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
  1. SIMULATED CAMPAIGNS — Regular phishing tests to measure awareness
  2. MICRO-LEARNING — Short, focused lessons on new threats
  3. METRICS & REPORTING — Track click rates for targeted retraining
  4. SEPARATION OF DUTY — No single person controls sensitive processes
  5. APPROVAL PROCEDURES — Second verification for sensitive actions
  6. CALLBACK PROCEDURES — Verify using known, official numbers
  7. EMPOWER EMPLOYEES — Question urgent requests without fear
  
  GOAL: Turn humans from the weakest link into ACTIVE SENSORS! 🛡️
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")


if __name__ == '__main__':
    run_soc_exercise()
