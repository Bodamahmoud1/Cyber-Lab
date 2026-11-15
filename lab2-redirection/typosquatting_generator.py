#!/usr/bin/env python3
"""
=============================================================================
  LAB 2 - TOOL A: Typosquatting Domain Generator & Analyzer
=============================================================================
  Course : Cybersecurity - Lecture 6: Social Engineering (Slides 28-29)
  Purpose: Generate typosquatting variations of a domain name to demonstrate
           how attackers create look-alike domains.
  
  Techniques simulated:
    1. Character omission     (amazn.com)
    2. Adjacent key swap      (amaxon.com)
    3. Character duplication   (amazzon.com)
    4. Character swap          (amzaon.com)
    5. Homoglyph substitution  (аmazon.com — Cyrillic 'а')
    6. TLD variation           (amazon.org, amazon.net)
    7. Hyphenation             (ama-zon.com)
    8. Subdomain trick         (amazon.com.evil.com)
  
  Usage  : python typosquatting_generator.py amazon.com
           python typosquatting_generator.py cis.asu.edu.eg
=============================================================================
"""

import sys
import itertools

# Keyboard adjacency map (QWERTY)
ADJACENT_KEYS = {
    'a': 'qwsz', 'b': 'vghn', 'c': 'xdfv', 'd': 'serfcx',
    'e': 'wrsdf', 'f': 'drtgvc', 'g': 'ftyhbv', 'h': 'gyujnb',
    'i': 'ujklo', 'j': 'huiknm', 'k': 'jiolm', 'l': 'kop',
    'm': 'njk', 'n': 'bhjm', 'o': 'iklp', 'p': 'ol',
    'q': 'wa', 'r': 'edft', 's': 'awedxz', 't': 'rfgy',
    'u': 'yhjik', 'v': 'cfgb', 'w': 'qase', 'x': 'zsdc',
    'y': 'tghu', 'z': 'asx'
}

# Homoglyph map (Latin → visually similar Unicode characters)
HOMOGLYPHS = {
    'a': ['а', 'ɑ', 'α'],       # Cyrillic a, Latin alpha, Greek alpha
    'c': ['с', 'ϲ'],             # Cyrillic es, Greek lunate sigma
    'd': ['ԁ', 'ɗ'],             # Cyrillic de
    'e': ['е', 'ё', 'ε'],        # Cyrillic ie, Greek epsilon
    'g': ['ɡ', 'ǵ'],
    'h': ['һ', 'ħ'],             # Cyrillic ha
    'i': ['і', 'ι', '1', 'l'],   # Cyrillic i, Greek iota, digit 1, letter l
    'k': ['κ', 'ⱪ'],             # Greek kappa
    'l': ['1', 'ⅼ', 'ı'],        # Digit 1, Roman numeral l
    'm': ['м', 'ⅿ'],             # Cyrillic em
    'n': ['п', 'ñ'],             # Cyrillic pe
    'o': ['о', '0', 'ο'],        # Cyrillic o, digit 0, Greek omicron
    'p': ['р', 'ρ'],             # Cyrillic er, Greek rho
    'r': ['г', 'ɾ'],             # Cyrillic ghe
    's': ['ѕ', 'ş'],             # Cyrillic dze
    't': ['τ', 'ţ'],             # Greek tau
    'u': ['υ', 'ц'],             # Greek upsilon
    'w': ['ω', 'ẃ'],             # Greek omega
    'x': ['х', 'χ'],             # Cyrillic kha, Greek chi
    'y': ['у', 'ý'],             # Cyrillic u
    'z': ['ź', 'ż'],
}

COMMON_TLDS = ['.com', '.net', '.org', '.co', '.info', '.biz', '.xyz', '.site',
               '.online', '.io', '.app', '.dev']


def split_domain(domain):
    """Split domain into name and TLD parts."""
    parts = domain.rsplit('.', 1)
    if len(parts) == 2:
        name, tld = parts[0], '.' + parts[1]
    else:
        name, tld = domain, ''
    
    # Handle multi-level TLDs like .edu.eg, .co.uk
    for multi_tld in ['.edu.eg', '.co.uk', '.co.jp', '.com.au', '.com.br', '.ac.uk']:
        if domain.endswith(multi_tld):
            name = domain[:-len(multi_tld)]
            tld = multi_tld
            break
    
    return name, tld


def generate_omission(name, tld):
    """Remove one character at a time."""
    results = []
    for i in range(len(name)):
        variant = name[:i] + name[i+1:]
        if variant and variant != name:
            results.append((variant + tld, "Character omission", f"removed '{name[i]}' at pos {i}"))
    return results


def generate_adjacent_swap(name, tld):
    """Replace each character with an adjacent keyboard key."""
    results = []
    for i in range(len(name)):
        ch = name[i].lower()
        if ch in ADJACENT_KEYS:
            for adj in ADJACENT_KEYS[ch][:2]:  # Limit to 2 per position
                variant = name[:i] + adj + name[i+1:]
                results.append((variant + tld, "Adjacent key swap", f"'{name[i]}'→'{adj}' at pos {i}"))
    return results


def generate_duplication(name, tld):
    """Double each character."""
    results = []
    for i in range(len(name)):
        if name[i].isalpha():
            variant = name[:i] + name[i] + name[i:]
            if variant != name:
                results.append((variant + tld, "Character duplication", f"doubled '{name[i]}' at pos {i}"))
    return results


def generate_swap(name, tld):
    """Swap adjacent characters."""
    results = []
    for i in range(len(name) - 1):
        variant = name[:i] + name[i+1] + name[i] + name[i+2:]
        if variant != name:
            results.append((variant + tld, "Character swap", f"swapped '{name[i]}{name[i+1]}'→'{name[i+1]}{name[i]}'"))
    return results


def generate_homoglyphs(name, tld):
    """Replace characters with visually similar Unicode characters."""
    results = []
    for i in range(len(name)):
        ch = name[i].lower()
        if ch in HOMOGLYPHS:
            for homoglyph in HOMOGLYPHS[ch][:1]:  # Limit to 1 per char
                variant = name[:i] + homoglyph + name[i+1:]
                results.append((variant + tld, "Homoglyph substitution", f"'{name[i]}'→'{homoglyph}' at pos {i}"))
    return results


def generate_tld_variations(name, tld):
    """Try different TLDs."""
    results = []
    for alt_tld in COMMON_TLDS:
        if alt_tld != tld:
            results.append((name + alt_tld, "TLD variation", f"{tld}→{alt_tld}"))
    return results[:5]  # Limit


def generate_hyphenation(name, tld):
    """Insert hyphens at various positions."""
    results = []
    for i in range(1, len(name)):
        if name[i-1].isalpha() and name[i].isalpha():
            variant = name[:i] + '-' + name[i:]
            results.append((variant + tld, "Hyphenation", f"inserted '-' at pos {i}"))
    return results[:3]  # Limit


def generate_subdomain_tricks(domain):
    """Create misleading subdomain structures."""
    name, tld = split_domain(domain)
    tricks = [
        (f"{domain}.evil-site.com", "Subdomain trick", f"{domain} appears legitimate but is a subdomain of evil-site.com"),
        (f"login.{domain}.attacker.net", "Subdomain trick", f"login.{domain} under attacker.net"),
        (f"{name}-secure{tld}", "Word addition", f"Added '-secure' suffix"),
        (f"secure-{name}{tld}", "Word addition", f"Added 'secure-' prefix"),
        (f"{name}-login{tld}", "Word addition", f"Added '-login' suffix"),
    ]
    return tricks


def analyze_domain(domain):
    """Generate all typosquatting variations for a domain."""
    name, tld = split_domain(domain)
    
    print(f"\n{'='*75}")
    print(f"  🔍 TYPOSQUATTING ANALYSIS FOR: {domain}")
    print(f"     Name part: '{name}'  |  TLD: '{tld}'")
    print(f"{'='*75}\n")
    
    all_variants = []
    
    categories = [
        ("1. Character Omission", generate_omission(name, tld)),
        ("2. Adjacent Key Swap (QWERTY)", generate_adjacent_swap(name, tld)),
        ("3. Character Duplication", generate_duplication(name, tld)),
        ("4. Character Swap", generate_swap(name, tld)),
        ("5. Homoglyph Substitution (IDN)", generate_homoglyphs(name, tld)),
        ("6. TLD Variation", generate_tld_variations(name, tld)),
        ("7. Hyphenation", generate_hyphenation(name, tld)),
        ("8. Subdomain / Word Tricks", generate_subdomain_tricks(domain)),
    ]
    
    total = 0
    for cat_name, variants in categories:
        print(f"  ┌─── {cat_name} ({len(variants)} variants) ───")
        for variant, technique, detail in variants[:8]:  # Show max 8 per category
            print(f"  │  {variant:40s}  ← {detail}")
            total += 1
        if len(variants) > 8:
            print(f"  │  ... and {len(variants) - 8} more")
            total += len(variants) - 8
        print(f"  └{'─'*65}")
        print()
        all_variants.extend(variants)
    
    print(f"  📊 Total typosquatting variants generated: {total}")
    print(f"\n  ⚠️  In a real scenario, attackers register these domains and host")
    print(f"     clone pages to harvest credentials or distribute malware.\n")
    print(f"  🛡️  DEFENSE (Lecture Slide 29):")
    print(f"     • Organizations should defensively register common typos")
    print(f"     • Monitor Certificate Transparency logs for look-alike domains")
    print(f"     • Use DNS filtering / threat intelligence feeds")
    print(f"     • Train users to manually type URLs or use bookmarks\n")
    
    return all_variants


def main():
    if len(sys.argv) < 2:
        print("Usage: python typosquatting_generator.py <domain>")
        print("Example: python typosquatting_generator.py amazon.com")
        print("         python typosquatting_generator.py cis.asu.edu.eg")
        sys.exit(1)
    
    domain = sys.argv[1].lower().strip()
    analyze_domain(domain)


if __name__ == '__main__':
    main()
