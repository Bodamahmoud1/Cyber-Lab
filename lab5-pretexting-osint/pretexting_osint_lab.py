#!/usr/bin/env python3
"""
=============================================================================
  LAB 5: Pretexting Defense Roleplay
=============================================================================
  Course : Cybersecurity - Lecture 6: Social Engineering (Slides 23-26, 38, 45)
  Purpose: Interactive pretexting scenarios for practicing verification
           and safe responses.
  
  Usage  : python pretexting_osint_lab.py
=============================================================================
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PART B: PRETEXTING DEFENSE ROLEPLAY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PRETEXTING_SCENARIOS = [
    {
        "id": 1,
        "attacker_role": "IT Support Technician",
        "pretext": "Hi, this is Khaled from IT Support. We're doing emergency maintenance on the email server. I need your username and password to migrate your mailbox before we shut down the old server in 15 minutes.",
        "triggers_used": ["Authority (IT Support)", "Urgency (15 minutes)", "Intimidation (lose email)"],
        "correct_response": "REFUSE and verify",
        "defense_actions": [
            "Ask for the caller's employee ID and department extension",
            "Tell them you'll call the IT Help Desk back on the OFFICIAL published number",
            "Never provide passwords over the phone — IT never needs your password",
            "Report the call to your security team"
        ]
    },
    {
        "id": 2,
        "attacker_role": "Bank Security Officer",
        "pretext": "Hello, I'm calling from your bank's fraud detection team. We've noticed suspicious transactions on your account. I need to verify your identity by confirming your account number, the last 4 digits of your national ID, and your SMS OTP code.",
        "triggers_used": ["Authority (bank)", "Urgency (suspicious activity)", "Trust (fraud prevention)", "Intimidation (financial loss)"],
        "correct_response": "REFUSE and verify",
        "defense_actions": [
            "Hang up and call the number on the BACK of your bank card",
            "Banks never ask for full credentials or OTP codes by phone",
            "OTP codes should only be entered on official bank apps/websites",
            "Check your bank app directly to see if there are real alerts"
        ]
    },
    {
        "id": 3,
        "attacker_role": "Company CEO (Whaling/BEC)",
        "pretext": "This is Dr. Mohamed Kamal, the CFO. I'm in a meeting with our acquisition partners and I need you to process an urgent wire transfer of $157,000 to the escrow account immediately. This is highly confidential — do not discuss with anyone until the deal is announced. Here are the bank details...",
        "triggers_used": ["Authority (CFO)", "Urgency (in a meeting NOW)", "Intimidation (confidential, don't question)", "Trust (known executive name)"],
        "correct_response": "REFUSE and verify",
        "defense_actions": [
            "Apply SEPARATION OF DUTY: wire transfers require dual approval",
            "Call the CFO on their known, official phone number to verify",
            "Follow the company's APPROVAL PROCEDURES for large transfers",
            "The 'don't tell anyone' instruction is a MAJOR red flag",
            "Report to the security team immediately"
        ]
    },
    {
        "id": 4,
        "attacker_role": "Vendor / Supplier",
        "pretext": "Hi, this is Sarah from ACME Suppliers. We've updated our banking details. Please update our payment information in your system. Here are the new account details for all future payments. We have an outstanding invoice of $42,750 that needs to be paid to the new account within 48 hours.",
        "triggers_used": ["Trust (known vendor name)", "Urgency (48-hour deadline)", "Familiarity (existing business relationship)"],
        "correct_response": "REFUSE and verify",
        "defense_actions": [
            "Call the vendor on the number in your EXISTING records (not the email)",
            "Verify bank detail changes through a KNOWN contact at the vendor",
            "Implement a CALLBACK PROCEDURE for payment detail changes",
            "Cross-reference the email domain (look for typosquatting!)",
            "Require management approval for payment detail changes"
        ]
    }
]


def run_pretexting_roleplay():
    """Interactive pretexting defense exercise."""
    
    print(f"\n{'='*70}")
    print(f"  🎭 PRETEXTING DEFENSE ROLEPLAY LAB")
    print(f"  Lecture 6: Slides 23-26 (Pretexting) & Slide 45 (Defense)")
    print(f"{'='*70}")
    print("""
  📋 SCENARIO SETUP:
  You are working at the IT Help Desk. For each incoming call/message,
  you must decide:
  
  1. Is this a legitimate request or a pretexting attack?
  2. What psychological triggers is the caller using?
  3. What defense procedure should you follow?
  
  🛡️ DEFENSE TOOLKIT (from Slide 45):
  • Separation of Duty — no single person controls a sensitive process
  • Approval Procedures — require second verification for sensitive actions
  • Callback Procedures — verify using known, official numbers
  • Empower employees to QUESTION urgent requests without fear
""")
    
    score = 0
    
    for scenario in PRETEXTING_SCENARIOS:
        print(f"\n{'─'*70}")
        print(f"  📞 INCOMING CALL — Scenario {scenario['id']}")
        print(f"  Caller claims to be: {scenario['attacker_role']}")
        print(f"{'─'*70}")
        print()
        
        # Display the pretext message
        for line in scenario['pretext'].split('. '):
            print(f"  📱 \"{line.strip()}.\"")
        print()
        
        print("  ❓ How do you respond?")
        print("     [1] Comply with the request (provide what they asked for)")
        print("     [2] REFUSE and verify through official channels")
        print("     [3] Forward to your supervisor without responding")
        
        try:
            answer = input("\n  Your response (1, 2, or 3): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n  Exercise ended early.")
            return
        
        if answer == "2":
            print("  ✅ CORRECT! Always refuse and verify independently.")
            score += 1
        elif answer == "3":
            print("  ⚠️  Partially correct. Forwarding helps, but YOU should also")
            print("     refuse the request and not leave the attacker waiting (they")
            print("     might call back to someone less trained).")
        else:
            print("  ❌ WRONG! You just fell for the pretexting attack!")
            print("     Never comply with unverified sensitive requests.")
        
        print(f"\n  🎯 Psychological Triggers Used:")
        for trigger in scenario['triggers_used']:
            print(f"     • {trigger}")
        
        print(f"\n  🛡️ Correct Defense Actions:")
        for action in scenario['defense_actions']:
            print(f"     ✓ {action}")
        
        if scenario['id'] < len(PRETEXTING_SCENARIOS):
            try:
                input("\n  Press Enter for next scenario...")
            except (EOFError, KeyboardInterrupt):
                break
    
    print(f"\n{'='*70}")
    print(f"  📊 SCORE: {score}/{len(PRETEXTING_SCENARIOS)}")
    if score == len(PRETEXTING_SCENARIOS):
        print("  🏆 Perfect! You're an excellent human firewall!")
    elif score >= 2:
        print("  👍 Good awareness. Review the callback verification procedures.")
    else:
        print("  📚 Review Slides 23-26 and 45 on pretexting defense.")
    print(f"{'='*70}\n")


def main():
    run_pretexting_roleplay()


if __name__ == '__main__':
    main()

