import json
import os
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "AIticket.settings",
)

import django

django.setup()


from apps.knowledge_base.generator import (
    generate_resolution,
)


print("=" * 80)
print("M2 GENERATOR REFUSAL TEST")
print("=" * 80)


resolution = generate_resolution(
    subject="Unknown IT issue",
    description="Something is not working.",
    category="UNCLASSIFIED",
    subcategory="General",
    already_tried="Restarted the computer.",
    severity="MEDIUM",
    packed_context="",
    retrieval_results=[],
    classification_confidence=0.0,
)


print("\nRESULT:")
print(
    json.dumps(
        resolution,
        indent=2,
    )
)


print("\n" + "-" * 80)
print("ASSERTIONS")
print("-" * 80)


assert resolution["sufficient_context"] is False

assert resolution["steps"] == []

assert resolution["sources"] == []

assert resolution["escalation_recommended"] is True

assert resolution["confidence"] == 0.0

print("sufficient_context = FALSE: PASS")
print("steps = []: PASS")
print("sources = []: PASS")
print("escalation_recommended = TRUE: PASS")
print("confidence = 0.0: PASS")


print("\n" + "=" * 80)
print("GENERATOR REFUSAL TEST: PASS")
print("=" * 80)