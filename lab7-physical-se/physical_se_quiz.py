#!/usr/bin/env python3
"""
=============================================================================
  LAB 7: Physical Social Engineering Awareness Quiz
=============================================================================
  Course : Cybersecurity - Lecture 6: Social Engineering (Slides 38-41)
  Purpose: Interactive quiz covering physical SE techniques:
           - Tailgating & Piggybacking (Slide 40)
           - Shoulder Surfing (Slide 41)
           - Dumpster Diving (Slide 38)
           - Baiting (Slide 39)
  
  Usage  : python physical_se_quiz.py
=============================================================================
"""

import sys
import random

SCENARIOS = [
    # ── TAILGATING / PIGGYBACKING ──
    {
        "category": "Tailgating & Piggybacking (Slide 40)",
        "scenario": """You're entering the server room through a badge-access door.
A person in a delivery uniform carrying several large boxes says:
"Hey, could you hold the door? My hands are full and my badge is in my pocket."
They have a delivery company logo on their shirt.""",
        "question": "What should you do?",
        "options": [
            "Hold the door open — they're clearly a delivery person",
            "Ask them to put down the boxes and badge in themselves",
            "Politely decline, close the door, and direct them to reception to get escorted",
            "Ask to see their badge and let them in if they show one"
        ],
        "correct": 2,
        "explanation": """CORRECT: Politely decline and direct to reception.
• Tailgating = following someone through a secured door without authorization
• Piggybacking = the person ASKS to be let through (like this scenario)
• A delivery uniform and carrying boxes are classic social engineering props
• The correct procedure is: ALL visitors must badge in or be escorted
• Never feel pressured by politeness or sympathy — that's the exploit!"""
    },
    {
        "category": "Tailgating & Piggybacking (Slide 40)",
        "scenario": """You're leaving the building and notice someone walking quickly
behind you. As you push through the exit door, they grab it before it closes
and walk through behind you. They're wearing business attire and talking
on their phone, seeming busy and preoccupied.""",
        "question": "What should you do?",
        "options": [
            "Nothing — they look like they belong here",
            "Confront them aggressively about not badging in",
            "Politely ask if they have their badge, and if not, direct them to security",
            "Ignore it since you're leaving, not entering"
        ],
        "correct": 2,
        "explanation": """CORRECT: Politely verify.
• Looking busy/professional is a social engineering tactic
• Talking on the phone makes it awkward to interrupt — by design!
• Exit-side tailgating is less common but can be used to access areas
  accessible from the lobby
• Security awareness applies in ALL directions of door travel
• A simple "excuse me, do you have your badge?" is sufficient"""
    },
    # ── SHOULDER SURFING ──
    {
        "category": "Shoulder Surfing (Slide 41)",
        "scenario": """You're at a coffee shop working on your laptop. You need to log into
your company's VPN. The shop is busy, and there are people sitting at tables
behind and beside you.""",
        "question": "What's the safest way to enter your credentials?",
        "options": [
            "Type normally — no one is paying attention",
            "Use a privacy screen filter, angle your laptop away, and use a password manager (autofill)",
            "Wait until no one is nearby, then type quickly",
            "Ask the people near you to look away"
        ],
        "correct": 1,
        "explanation": """CORRECT: Use multiple defenses together.
• Privacy screen filters limit viewing angles to directly in front
• Password managers auto-fill credentials without typing them visibly
• Positioning your screen away from foot traffic reduces exposure
• Camera-based shoulder surfing can capture from a distance!
• In airports, ATMs, and offices — always assume someone could be watching"""
    },
    {
        "category": "Shoulder Surfing (Slide 41)",
        "scenario": """At the ATM, you notice someone standing very close behind you
in the queue. They're looking at their phone but their phone camera
could be pointed at the keypad.""",
        "question": "What should you do?",
        "options": [
            "Proceed normally — they're just on their phone",
            "Shield the keypad with your other hand while entering your PIN",
            "Ask them to step back, shield the keypad, and check for skimming devices",
            "Cancel the transaction and find another ATM"
        ],
        "correct": 2,
        "explanation": """CORRECT: Ask for space, shield PIN entry, check for skimmers.
• Phone cameras can record PIN entry from behind
• Physical shielding is essential — cover the keypad with your hand
• Ask for personal space — most people will comply if asked politely
• Also check for card skimming devices (loose card slots, hidden cameras)
• If anything feels wrong, use a different ATM and report it"""
    },
    # ── DUMPSTER DIVING ──
    {
        "category": "Dumpster Diving (Slide 38)",
        "scenario": """Your manager asks you to dispose of old project documents including
printed network diagrams, employee directories, meeting notes with
client names, and old access cards.""",
        "question": "What's the correct disposal procedure?",
        "options": [
            "Put everything in the regular recycling bin",
            "Tear papers in half and throw them in the trash",
            "Cross-cut shred all documents, physically destroy access cards, and use secure disposal bins",
            "Keep them in a filing cabinet 'just in case'"
        ],
        "correct": 2,
        "explanation": """CORRECT: Cross-cut shred + secure disposal.
• Regular recycling and regular trash are accessible to dumpster divers
• Tearing in half still leaves readable information
• Cross-cut shredders create confetti-like pieces (much harder to reassemble)
• Access cards should be physically destroyed (cut, degauss)
• Organizations should have designated secure disposal bins with locks
• Discarded network diagrams can reveal sensitive information."""
    },
    # ── BAITING ──
    {
        "category": "Baiting (Slide 39)",
        "scenario": """You find a USB drive in the parking lot labeled:
"CONFIDENTIAL — HR Salary Review 2025"
You're curious about whether anyone got a raise.""",
        "question": "What should you do?",
        "options": [
            "Plug it into your work computer to check the contents",
            "Plug it into your personal computer instead (safer than work)",
            "Turn it in to the IT/Security department WITHOUT plugging it in",
            "Plug it into a computer that's not connected to the network"
        ],
        "correct": 2,
        "explanation": """CORRECT: Turn it in to IT/Security, never plug it in.
• This is a classic USB baiting attack (Slide 39)
• The enticing label triggers CURIOSITY — one of the psychological triggers
• Malware can execute the moment a USB is plugged in (autorun, firmware-level)
• Even 'air-gapped' or offline computers can be compromised
• USB attacks can: install keyloggers, ransomware, backdoors, or
  phone home via cellular modem embedded in the USB device
• IT/Security has sandboxed environments to safely analyze found devices"""
    },
    # ── COMBINED ──
    {
        "category": "Combined Physical SE (All Slides)",
        "scenario": """A person in a technician's uniform arrives at your office saying:
"Hi, I'm from the ISP. We received reports of slow internet on this floor.
I need access to the server closet to check the fiber connection.
Can you badge me in? I left my visitor pass at the front desk."

They have tools, an ISP-branded shirt, and seem professional.""",
        "question": "How should you respond?",
        "options": [
            "Badge them in — they look legitimate and have the right equipment",
            "Escort them personally to the server room",
            "Tell them to go to reception to get a visitor pass, then verify with your ISP that they sent a technician",
            "Ask for their employee ID and let them in if they have one"
        ],
        "correct": 2,
        "explanation": """CORRECT: Visitor pass + independent verification.
This scenario combines MULTIPLE social engineering techniques:
• PRETEXTING: Fabricated story about internet issues
• IMPERSONATION: ISP uniform and tools (Authority trigger)
• TAILGATING: Asking to be badged in
• FAMILIARITY: Acting casual and professional

The defense checklist:
1. ALL visitors must have a visitor pass from reception
2. Call your ISP on their OFFICIAL number (not a number the visitor gives)
3. Verify that a technician was actually dispatched
4. Escort all third-party technicians at all times
5. Never let someone pressure you into bypassing physical security"""
    }
]


def run_quiz():
    print("\n" + "=" * 70)
    print("  🏢 PHYSICAL SOCIAL ENGINEERING AWARENESS QUIZ")
    print("  Lecture 6: Slides 38-41")
    print("=" * 70)
    print("""
  This quiz tests your ability to handle physical social engineering
  scenarios: Tailgating, Shoulder Surfing, Dumpster Diving, and Baiting.
  
  For each scenario, select the BEST response.
""")
    
    score = 0
    total = len(SCENARIOS)
    
    for i, s in enumerate(SCENARIOS):
        print(f"\n{'─'*70}")
        print(f"  📋 SCENARIO {i+1}/{total} — {s['category']}")
        print(f"{'─'*70}")
        print()
        for line in s['scenario'].strip().split('\n'):
            print(f"  {line.strip()}")
        print(f"\n  ❓ {s['question']}")
        for j, opt in enumerate(s['options']):
            print(f"     [{j}] {opt}")
        
        try:
            answer = input(f"\n  Your answer (0-{len(s['options'])-1}): ").strip()
            answer_num = int(answer)
        except (ValueError, EOFError, KeyboardInterrupt):
            print("\n  Quiz ended.")
            return
        
        if answer_num == s['correct']:
            print(f"  ✅ CORRECT!")
            score += 1
        else:
            print(f"  ❌ Incorrect. The best answer was [{s['correct']}].")
        
        print(f"\n  📖 Explanation:")
        for line in s['explanation'].strip().split('\n'):
            print(f"  {line}")
        
        if i < total - 1:
            try:
                input("\n  Press Enter for next scenario...")
            except (EOFError, KeyboardInterrupt):
                break
    
    pct = (score / total) * 100
    print(f"\n{'='*70}")
    print(f"  📊 FINAL SCORE: {score}/{total} ({pct:.0f}%)")
    if pct == 100:
        print("  🏆 Perfect! Outstanding physical security awareness!")
    elif pct >= 70:
        print("  👍 Good job! Review the scenarios you missed.")
    else:
        print("  📚 Review Slides 38-41 on physical SE techniques.")
    print(f"{'='*70}\n")


if __name__ == '__main__':
    run_quiz()
