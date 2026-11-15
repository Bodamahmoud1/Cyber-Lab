import os

base_templates = r"K:\Desktop\Cyber Labs\SE-Labs\templates"
base_static_js = r"K:\Desktop\Cyber Labs\SE-Labs\static\js"
os.makedirs(base_templates, exist_ok=True)
os.makedirs(base_static_js, exist_ok=True)

# Lab 1 - Phishing
lab1_html = open(os.path.join(base_templates, "lab1.html"), encoding="utf-8").read()

# Lab 2 - Typosquatting & Redirection
lab2_html = open(os.path.join(base_templates, "lab2.html"), encoding="utf-8").read()

# Lab 3 - Pharming
lab3_html = open(os.path.join(base_templates, "lab3.html"), encoding="utf-8").read()

# Lab 4 - Baiting & Disinformation
lab4_html = open(os.path.join(base_templates, "lab4.html"), encoding="utf-8").read()

# Lab 5 - Pretexting & Dumpster Diving
lab5_html = open(os.path.join(base_templates, "lab5.html"), encoding="utf-8").read()

# Lab 6 - Watering Hole
lab6_html = open(os.path.join(base_templates, "lab6.html"), encoding="utf-8").read()

# Lab 7 - Physical SE
lab7_html = open(os.path.join(base_templates, "lab7.html"), encoding="utf-8").read()

# Lab 8 - SOC Defense
lab8_html = open(os.path.join(base_templates, "lab8.html"), encoding="utf-8").read()

files = {
    "lab1.html": lab1_html,
    "lab2.html": lab2_html,
    "lab3.html": lab3_html,
    "lab4.html": lab4_html,
    "lab5.html": lab5_html,
    "lab6.html": lab6_html,
    "lab7.html": lab7_html,
    "lab8.html": lab8_html,
}

for fname, content in files.items():
    p = os.path.join(base_templates, fname)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    print("Wrote template:", fname)

# Shared JS
app_js = open(os.path.join(base_static_js, "app.js"), encoding="utf-8").read()
with open(os.path.join(base_static_js, "app.js"), "w", encoding="utf-8") as f:
    f.write(app_js)
print("Wrote static/js/app.js")

