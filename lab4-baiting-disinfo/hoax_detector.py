#!/usr/bin/env python3
"""
=============================================================================
  LAB 4 - TOOL B: Disinformation / Hoax Detection Exercise
=============================================================================
  Course : Cybersecurity - Lecture 6: Social Engineering (Slides 33-34)
  Purpose: Presents students with simulated hoax messages and asks them
           to classify each as Misinformation or Disinformation, identify
           the psychological triggers, and write a detection rule.
  
  Usage  : python hoax_detector.py
=============================================================================
"""

import json
import sys

HOAX_SCENARIOS = [
    {
        "id": 1,
        "title": "Deadly Virus Hoax",
        "source": "Email chain forward",
        "message": """⚠️ URGENT WARNING ⚠️

A deadly virus called "SULFNBK.EXE" is spreading through the Internet!

If you find a file named SULFNBK.EXE on your computer, DELETE IT IMMEDIATELY!
It is a trojan that will activate on December 25th and erase your entire hard drive.

Forward this message to everyone you know to protect them!

Microsoft has confirmed this threat. Act NOW before it's too late!""",
        "classification": "Disinformation",
        "explanation": "SULFNBK.EXE is a legitimate Windows system file (used for restoring long filenames). This is a classic hoax designed to trick users into deleting important system files, potentially causing system instability.",
        "triggers": ["Urgency", "Authority (fake Microsoft claim)", "Intimidation (data loss threat)", "Consensus (forward to everyone)"],
        "defense": "Verify with official Microsoft sources. Check file properties. Never delete system files based on email forwards."
    },
    {
        "id": 2,
        "title": "Fake Critical Update",
        "source": "Pop-up notification",
        "message": """🔒 CRITICAL SECURITY UPDATE REQUIRED

Your Windows installation has 47 critical vulnerabilities.
Your system is currently exposed to remote attacks.

Download this urgent update patch to protect your data:
>> Download_Security_Patch_KB5034441.exe <<

This update is mandatory for all users. Failure to install 
within 24 hours may result in data loss.

- Microsoft Windows Security Team""",
        "classification": "Disinformation",
        "explanation": "Fake update notifications that deliver malware. Real Windows updates come through Windows Update, not pop-up downloads. The file KB5034441 number mimics real KB article numbers to appear legitimate.",
        "triggers": ["Authority (Microsoft branding)", "Urgency (24-hour deadline)", "Intimidation (data loss)", "Trust (looks official)"],
        "defense": "Only install updates from Windows Update (Settings → Update). Never download .exe files from pop-ups. Verify KB numbers on Microsoft's official website."
    },
    {
        "id": 3,
        "title": "Free WiFi Warning",
        "source": "Social media post",
        "message": """⚡ PSA: IMPORTANT WiFi SAFETY TIP ⚡

Did you know? If you hold your phone's WiFi button for 10 seconds, it enables
"Enhanced Security Mode" which protects you from ALL hackers on public WiFi!

This hidden feature was confirmed by Apple and Google engineers.
Share this with your friends and family to keep them safe! 🛡️

#CyberSecurity #WiFiSafety #LifeHack""",
        "classification": "Misinformation",
        "explanation": "This is technically misinformation (false info shared without malicious intent to damage systems). There is no 'Enhanced Security Mode' activated by holding the WiFi button. The poster may genuinely believe this. While not directly harmful, it gives a false sense of security.",
        "triggers": ["Authority (claimed expert confirmation)", "Trust (appears helpful)", "Consensus (share with everyone)"],
        "defense": "Use a VPN on public WiFi. Verify claims through official documentation. Be skeptical of 'hidden features' shared on social media."
    },
    {
        "id": 4,
        "title": "Ransomware Phone Call",
        "source": "Phone call (Vishing)",
        "message": """[Phone rings]

Caller: "Hello, this is Agent Johnson from the Cybercrime Division of the 
Federal Police. We have detected that your computer's IP address has been 
used in illegal activities including downloading prohibited content.

A warrant has been issued for your arrest. However, if you cooperate now, 
we can resolve this without prosecution.

I need you to go to the nearest pharmacy and purchase $500 in Google Play 
gift cards. Read me the card numbers to pay the administrative fine. 
This call is being recorded for legal purposes."

[Caller ID shows: "Federal Police +1-800-555-0199"]""",
        "classification": "Disinformation (Vishing + Pretexting)",
        "explanation": "Classic vishing scam combining pretexting (fake law enforcement identity) with disinformation (fake warrant). Law enforcement NEVER demands payment via gift cards. The spoofed caller ID adds false legitimacy.",
        "triggers": ["Authority (law enforcement)", "Intimidation (arrest threat)", "Urgency (immediate action)", "Trust (caller ID spoofing)"],
        "defense": "Hang up. Call the police on their OFFICIAL published number to verify. Law enforcement never requests gift card payments. Report to anti-fraud authorities."
    },
    {
        "id": 5,
        "title": "Chain Email Charity Hoax",
        "source": "WhatsApp forward",
        "message": """🙏 Please Read and Share! 🙏

For every forward of this message, Facebook/WhatsApp will donate $1 to 
children's cancer research. Mark Zuckerberg personally confirmed this 
in a press conference yesterday.

So far this message has been shared 2.3 million times and raised $2.3M!

Don't break the chain — every share counts! A child's life depends on you.

❤️ Share with at least 10 people ❤️""",
        "classification": "Misinformation",
        "explanation": "While not directly harmful to systems, this is false information spread by well-meaning people. WhatsApp/Facebook have no mechanism to track message forwards or donate per-forward. It wastes bandwidth and conditions users to share without verifying.",
        "triggers": ["Consensus (millions have shared)", "Trust (CEO attribution)", "Familiarity (emotional appeal)", "Intimidation (guilt — 'a child's life')"],
        "defense": "Verify claims on official channels. No platform donates per-forward. Check fact-checking sites (Snopes, etc). Don't forward unverified chains."
    }
]


def run_interactive_quiz():
    """Interactive exercise where students classify hoax messages."""
    
    print("\n" + "=" * 70)
    print("  📰 DISINFORMATION & MISINFORMATION DETECTION LAB")
    print("  Lecture 6: Slides 33-34")
    print("=" * 70)
    print("""
  📋 DEFINITIONS (from the lecture):
  
  • MISINFORMATION: False info spread WITHOUT intent to deceive.
    The sender may believe it is true. (Unintentional harm)
  
  • DISINFORMATION: False info DELIBERATELY crafted to deceive
    and cause harm. (Intentional — hoaxes, scams, manipulation)
  
  For each scenario below, you will:
  1. Classify it as Misinformation or Disinformation
  2. Identify the psychological triggers used
  3. Propose a defense strategy
""")
    
    score = 0
    total = len(HOAX_SCENARIOS)
    
    for scenario in HOAX_SCENARIOS:
        print(f"\n{'─'*70}")
        print(f"  SCENARIO {scenario['id']}: {scenario['title']}")
        print(f"  Source: {scenario['source']}")
        print(f"{'─'*70}")
        print()
        for line in scenario['message'].split('\n'):
            print(f"  │ {line}")
        print()
        
        # Question 1: Classification
        print("  ❓ Question: Is this MISINFORMATION or DISINFORMATION?")
        print("     [1] Misinformation (unintentional)")
        print("     [2] Disinformation (intentional/malicious)")
        
        try:
            answer = input("\n  Your answer (1 or 2): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n  Quiz ended early.")
            return
        
        correct_num = "2" if scenario['classification'].startswith("Dis") else "1"
        if answer == correct_num:
            print(f"  ✅ Correct! This is {scenario['classification']}.")
            score += 1
        else:
            print(f"  ❌ Incorrect. This is {scenario['classification']}.")
        
        print(f"\n  📖 Explanation: {scenario['explanation']}")
        print(f"\n  🎯 Psychological Triggers Used:")
        for trigger in scenario['triggers']:
            print(f"     • {trigger}")
        print(f"\n  🛡️ Defense: {scenario['defense']}")
        
        if scenario['id'] < total:
            try:
                input("\n  Press Enter for next scenario...")
            except (EOFError, KeyboardInterrupt):
                break
    
    print(f"\n{'='*70}")
    print(f"  📊 FINAL SCORE: {score}/{total} correct")
    if score == total:
        print("  🏆 Perfect score! Excellent threat classification skills!")
    elif score >= total * 0.6:
        print("  👍 Good job! Review the ones you missed.")
    else:
        print("  📚 Review Lecture Slides 33-34 on Mis/Disinformation.")
    print(f"{'='*70}\n")


def print_all_scenarios():
    """Print all scenarios with answers (instructor reference)."""
    print("\n  📋 INSTRUCTOR ANSWER KEY\n")
    for s in HOAX_SCENARIOS:
        print(f"  Scenario {s['id']}: {s['title']}")
        print(f"    Classification: {s['classification']}")
        print(f"    Triggers: {', '.join(s['triggers'])}")
        print()


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--answers':
        print_all_scenarios()
    else:
        run_interactive_quiz()


if __name__ == '__main__':
    main()
