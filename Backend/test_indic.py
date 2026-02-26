import subprocess
import sys

# Ensure regex module is loaded
try:
    from app.compliance.title_quality_validator import TitleQualityValidator
except Exception as e:
    print(f"Error loading: {e}")
    sys.exit(1)

v = TitleQualityValidator()
cases = [
    "Pratidhwani",
    "प्रतिध्वनि",
    "ସମ୍ବାଦ",
    "Samachar Times",
    "asdasd",
    "qwrtyplm",
    "90021909210",
    "808012012hi"
]

for c in cases:
    is_low, violations, risk = v.validate(c)
    print(f"Title: {c}")
    print(f"  Low Quality: {is_low}")
    print(f"  Risk: {risk}")
    if violations:
        print(f"  Violations: {violations}")
    print("-" * 20)
