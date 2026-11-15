#!/usr/bin/env python3
"""
=============================================================================
  LAB 1 - TOOL A: Email Header Forensic Analyzer
=============================================================================
  Course : Cybersecurity - Lecture 6: Social Engineering
  Author : Lab Environment (Ain Shams University)
  Purpose: Parse .eml files and flag suspicious senders, mismatched
           reply addresses, psychological triggers, and suspicious URLs.
  
  Usage  : python header_analyzer.py <path_to_eml_file>
           python header_analyzer.py --all    (analyze all .eml in cwd)
=============================================================================
"""

import email
import re
import sys
import os
import glob
from email import policy
from email.parser import BytesParser
from collections import OrderedDict


# ── Psychological trigger keywords from Lecture Slide 5 ──────────────────
TRIGGER_KEYWORDS = {
    "Authority":    ["CEO", "CFO", "Director", "IT Department", "Security Department",
                     "Management", "Executive", "President", "authorized", "official",
                     "law enforcement", "attorney", "legal counsel", "senior partner"],
    "Intimidation": ["suspended", "terminated", "disabled", "legal action",
                     "permanently", "violation", "consequences", "penalty",
                     "compliance", "failure to comply", "law enforcement"],
    "Urgency":      ["immediately", "urgent", "ASAP", "right away", "act fast",
                     "within 30 minutes", "within 24 hours", "within 48 hours",
                     "before end of business", "time-sensitive", "expires",
                     "do not delay", "as soon as possible"],
    "Consensus":    ["everyone has", "all department", "all employees",
                     "already completed", "others have", "company-wide",
                     "all staff", "team has already"],
    "Scarcity":     ["limited time", "only available", "last chance",
                     "exclusive", "remaining", "running out", "few spots"],
    "Familiarity":  ["as we discussed", "following up on our", "per our conversation",
                     "you know me", "as you recall", "remember when"],
    "Trust":        ["verified", "official", "secure", "legitimate", "trusted",
                     "certified", "authenticated", "confirm your identity"]
}


def parse_eml(filepath):
    """Parse an .eml file and return the email message object."""
    with open(filepath, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)
    return msg


def extract_headers(msg):
    """Extract key forensic headers into an ordered dict."""
    headers = OrderedDict()
    key_headers = [
        'From', 'Reply-To', 'To', 'Subject', 'Date',
        'Return-Path', 'Message-ID', 'X-Mailer', 'X-Priority', 'Received'
    ]
    for h in key_headers:
        values = msg.get_all(h, [])
        if values:
            if h == 'Received':
                headers[h] = [str(v) for v in values]
            else:
                headers[h] = str(values[0]) if len(values) == 1 else [str(v) for v in values]
    return headers


def check_domain_mismatch(msg):
    """Check if From, Reply-To, Return-Path domains differ (spoofing indicator)."""
    flags = []
    
    def extract_domain(header_val):
        if not header_val:
            return None
        match = re.search(r'@([\w\-\.]+)', str(header_val))
        return match.group(1).lower() if match else None
    
    from_domain = extract_domain(msg.get('From', ''))
    reply_domain = extract_domain(msg.get('Reply-To', ''))
    return_domain = extract_domain(msg.get('Return-Path', ''))
    
    if from_domain and reply_domain and from_domain != reply_domain:
        flags.append(f"🚨 DOMAIN MISMATCH: From=@{from_domain}  vs  Reply-To=@{reply_domain}")
        flags.append("   → Replies go to a DIFFERENT server than the apparent sender!")
    
    if from_domain and return_domain and from_domain != return_domain:
        flags.append(f"🚨 DOMAIN MISMATCH: From=@{from_domain}  vs  Return-Path=@{return_domain}")
        flags.append("   → Bounce messages go to a DIFFERENT domain!")
    
    # Check for typosquatting in domains
    if from_domain:
        # Look for suspicious patterns: double letters, number substitution
        if re.search(r'(\w)\1{2,}', from_domain):  # triple letters
            flags.append(f"⚠️  Suspicious domain pattern in From: {from_domain}")
        if re.search(r'[01]', from_domain.replace('.com', '')):  # numbers in domain name
            flags.append(f"⚠️  Numbers in domain name (possible typosquatting): {from_domain}")
    
    return flags, from_domain, reply_domain, return_domain


def analyze_received_chain(received_headers):
    """Trace the Received: chain to map the email's true origin path."""
    hops = []
    for i, recv in enumerate(received_headers):
        # Extract source IP
        ip_match = re.search(r'\((?:[\w\-\.]+\s+)?\[?(\d+\.\d+\.\d+\.\d+)\]?\)', recv)
        ip = ip_match.group(1) if ip_match else "unknown"
        
        # Extract from/by hostnames
        from_match = re.search(r'from\s+([\w\-\.]+)', recv, re.IGNORECASE)
        by_match = re.search(r'by\s+([\w\-\.]+)', recv, re.IGNORECASE)
        
        hop = {
            "hop": len(received_headers) - i,
            "from": from_match.group(1) if from_match else "unknown",
            "by": by_match.group(1) if by_match else "unknown",
            "ip": ip
        }
        hops.append(hop)
    return hops


def scan_triggers(msg):
    """Scan email body and subject for psychological trigger keywords."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            ct = part.get_content_type()
            if ct in ('text/plain', 'text/html'):
                payload = part.get_payload(decode=True)
                if payload:
                    body += payload.decode('utf-8', errors='replace')
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            body = payload.decode('utf-8', errors='replace')
    
    subject = str(msg.get('Subject', ''))
    full_text = subject + " " + body
    
    # Strip HTML tags for keyword matching
    clean_text = re.sub(r'<[^>]+>', ' ', full_text)
    
    found_triggers = {}
    for trigger, keywords in TRIGGER_KEYWORDS.items():
        matches = []
        for kw in keywords:
            if re.search(re.escape(kw), clean_text, re.IGNORECASE):
                matches.append(kw)
        if matches:
            found_triggers[trigger] = matches
    
    return found_triggers


def extract_urls(msg):
    """Extract all URLs from the email body."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            ct = part.get_content_type()
            if ct in ('text/plain', 'text/html'):
                payload = part.get_payload(decode=True)
                if payload:
                    body += payload.decode('utf-8', errors='replace')
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            body = payload.decode('utf-8', errors='replace')
    
    # Find href URLs and plain-text URLs
    href_urls = re.findall(r'href=["\']([^"\']+)["\']', body, re.IGNORECASE)
    text_urls = re.findall(r'https?://[^\s<>"\']+', body)
    
    all_urls = list(set(href_urls + text_urls))
    return all_urls


def print_report(filepath, msg):
    """Generate and print the full forensic analysis report."""
    print("\n" + "=" * 75)
    print(f"  📧 EMAIL FORENSIC ANALYSIS REPORT")
    print(f"  File: {os.path.basename(filepath)}")
    print("=" * 75)
    
    # ── 1. Key Headers ──
    headers = extract_headers(msg)
    print("\n┌─── 1. KEY HEADERS ────────────────────────────────────────────────┐")
    for key, val in headers.items():
        if key == 'Received':
            print(f"  {key}: ({len(val)} hops found)")
        else:
            print(f"  {key}: {val}")
    print("└──────────────────────────────────────────────────────────────────────┘")
    
    # ── 2. Domain Mismatch Check ──
    print("\n┌─── 2. DOMAIN MISMATCH ANALYSIS ───────────────────────────────────┐")
    domain_flags, from_d, reply_d, return_d = check_domain_mismatch(msg)
    print(f"  From domain     : {from_d or 'N/A'}")
    print(f"  Reply-To domain : {reply_d or 'N/A (same as From)'}")
    print(f"  Return-Path     : {return_d or 'N/A'}")
    if domain_flags:
        for flag in domain_flags:
            print(f"  {flag}")
    else:
        print("  ✅ No obvious domain mismatches detected.")
    print("└──────────────────────────────────────────────────────────────────────┘")
    
    # ── 3. Received Chain (Route Trace) ──
    print("\n┌─── 3. EMAIL ROUTE TRACE (Received Chain) ────────────────────────┐")
    received_headers = headers.get('Received', [])
    if isinstance(received_headers, str):
        received_headers = [received_headers]
    hops = analyze_received_chain(received_headers)
    for hop in hops:
        print(f"  Hop {hop['hop']}: {hop['from']} ({hop['ip']}) → {hop['by']}")
    if not hops:
        print("  ⚠️  No Received headers found.")
    print("└──────────────────────────────────────────────────────────────────────┘")
    
    # ── 4. Psychological Trigger Analysis ──
    print("\n┌─── 4. PSYCHOLOGICAL TRIGGER ANALYSIS (Lecture Slide 5) ──────────┐")
    triggers = scan_triggers(msg)
    if triggers:
        for trigger, keywords in triggers.items():
            print(f"  🎯 {trigger:15s} → Found: {', '.join(keywords)}")
        print(f"\n  ⚠️  {len(triggers)} out of 7 triggers detected!")
        print("  This email leverages MULTIPLE psychological manipulations.")
    else:
        print("  ✅ No obvious psychological trigger keywords detected.")
    print("└──────────────────────────────────────────────────────────────────────┘")
    
    # ── 5. URL Analysis ──
    print("\n┌─── 5. EMBEDDED URL ANALYSIS ──────────────────────────────────────┐")
    urls = extract_urls(msg)
    if urls:
        for url in urls:
            print(f"  🔗 {url}")
            # Check for suspicious patterns
            if re.search(r'\d+\.\d+\.\d+\.\d+', url):
                print(f"     🚨 Contains raw IP address!")
            if len(url) > 100:
                print(f"     ⚠️  Unusually long URL (obfuscation?)")
            domain_match = re.search(r'https?://([^/]+)', url)
            if domain_match:
                url_domain = domain_match.group(1)
                if re.search(r'[01]', url_domain.replace('.com', '').replace('.net', '')):
                    print(f"     ⚠️  Numbers in domain (typosquatting?): {url_domain}")
    else:
        print("  No URLs found in email body.")
    print("└──────────────────────────────────────────────────────────────────────┘")
    
    # ── Verdict ──
    total_flags = len(domain_flags) + len(triggers) + \
                  (1 if any(re.search(r'\d+\.\d+\.\d+\.\d+', u) for u in urls) else 0)
    print("\n" + "=" * 75)
    if total_flags >= 4:
        print("  🚨 VERDICT: HIGH RISK — LIKELY PHISHING / BEC")
    elif total_flags >= 2:
        print("  ⚠️  VERDICT: SUSPICIOUS — REQUIRES FURTHER INVESTIGATION")
    else:
        print("  ℹ️  VERDICT: LOW RISK — But always verify unusual requests!")
    print(f"  Total suspicious indicators found: {total_flags}")
    print("=" * 75 + "\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python header_analyzer.py <file.eml>")
        print("       python header_analyzer.py --all")
        sys.exit(1)
    
    if sys.argv[1] == '--all':
        eml_files = glob.glob('*.eml')
        if not eml_files:
            print("No .eml files found in current directory.")
            sys.exit(1)
        for f in sorted(eml_files):
            msg = parse_eml(f)
            print_report(f, msg)
    else:
        filepath = sys.argv[1]
        if not os.path.exists(filepath):
            print(f"Error: File '{filepath}' not found.")
            sys.exit(1)
        msg = parse_eml(filepath)
        print_report(filepath, msg)


if __name__ == '__main__':
    main()
