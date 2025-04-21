import fitz  # PyMuPDF
import re

def analyze_resume(resume_path):
    doc = fitz.open(resume_path)
    text = ""
    for page in doc:
        text += page.get_text()

    analysis = {
        "name": None,
        "bias_flags": [],
        "skills_detected": [],
        "fairness_score": 100
    }

    # --- Bias detection ---
    gendered_terms = ["he", "she", "his", "her", "male", "female"]
    for word in gendered_terms:
        if re.search(r'\b' + word + r'\b', text, re.IGNORECASE):
            analysis["bias_flags"].append(f"Found potentially biased word: {word}")
            analysis["fairness_score"] -= 5

    # --- Skill detection ---
    core_skills = ["python", "data analysis", "communication", "teamwork", "html", "css"]
    for skill in core_skills:
        if skill in text.lower():
            analysis["skills_detected"].append(skill)

    # --- Name detection ---
    # Basic heuristic: first non-empty line with alphabetic characters
    for line in text.strip().split('\n'):
        if line.strip() and re.match(r'^[A-Za-z\s]+$', line.strip()):
            analysis["name"] = line.strip()
            break

    return analysis

