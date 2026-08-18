import json
from pathlib import Path

import lightgbm as lgb


BASE_DIR = Path(__file__).resolve().parents[1]

ARTIFACTS_DIR = BASE_DIR / "training" / "artifacts"

MODEL_PATH = ARTIFACTS_DIR / "severity_model.txt"
LABELS_PATH = ARTIFACTS_DIR / "severity_labels.json"

UNSEEN_TICKETS = [


    {
        "name": "Personal software inconvenience",
        "affected_scope": "JUST_ME",
        "work_blocked": "NO",
        "urgent_feeling": "LOW",
        "workaround_available": True,
        "category": "SOFTWARE",
        "severity": "LOW",
    },

    {
        "name": "Minor email issue",
        "affected_scope": "JUST_ME",
        "work_blocked": "NO",
        "urgent_feeling": "LOW",
        "workaround_available": False,
        "category": "EMAIL",
        "severity": "LOW",
    },

    {
        "name": "VPN slightly inconvenient",
        "affected_scope": "JUST_ME",
        "work_blocked": "PARTIALLY",
        "urgent_feeling": "LOW",
        "workaround_available": True,
        "category": "VPN",
        "severity": "LOW",
    },

    {
        "name": "Minor hardware problem",
        "affected_scope": "JUST_ME",
        "work_blocked": "NO",
        "urgent_feeling": "MEDIUM",
        "workaround_available": True,
        "category": "HARDWARE",
        "severity": "LOW",
    },

    {
        "name": "Small application inconvenience",
        "affected_scope": "JUST_ME",
        "work_blocked": "PARTIALLY",
        "urgent_feeling": "LOW",
        "workaround_available": False,
        "category": "APPLICATION",
        "severity": "LOW",
    },

    {
        "name": "Access request with workaround",
        "affected_scope": "JUST_ME",
        "work_blocked": "NO",
        "urgent_feeling": "MEDIUM",
        "workaround_available": True,
        "category": "ACCESS",
        "severity": "LOW",
    },

    {
        "name": "Minor network problem",
        "affected_scope": "JUST_ME",
        "work_blocked": "NO",
        "urgent_feeling": "LOW",
        "workaround_available": True,
        "category": "NETWORK",
        "severity": "LOW",
    },

    {
        "name": "Non-urgent email inconvenience",
        "affected_scope": "JUST_ME",
        "work_blocked": "PARTIALLY",
        "urgent_feeling": "MEDIUM",
        "workaround_available": True,
        "category": "EMAIL",
        "severity": "LOW",
    },

    {
        "name": "Low impact application issue",
        "affected_scope": "JUST_ME",
        "work_blocked": "NO",
        "urgent_feeling": "HIGH",
        "workaround_available": True,
        "category": "APPLICATION",
        "severity": "LOW",
    },

    {
        "name": "Low impact network issue",
        "affected_scope": "JUST_ME",
        "work_blocked": "PARTIALLY",
        "urgent_feeling": "MEDIUM",
        "workaround_available": False,
        "category": "NETWORK",
        "severity": "LOW",
    },

    {
        "name": "Individual application completely blocked",
        "affected_scope": "JUST_ME",
        "work_blocked": "YES",
        "urgent_feeling": "MEDIUM",
        "workaround_available": True,
        "category": "APPLICATION",
        "severity": "MEDIUM",
    },

    {
        "name": "Team software disruption",
        "affected_scope": "TEAM",
        "work_blocked": "PARTIALLY",
        "urgent_feeling": "LOW",
        "workaround_available": False,
        "category": "SOFTWARE",
        "severity": "MEDIUM",
    },

    {
        "name": "Team VPN degradation",
        "affected_scope": "TEAM",
        "work_blocked": "NO",
        "urgent_feeling": "MEDIUM",
        "workaround_available": False,
        "category": "VPN",
        "severity": "MEDIUM",
    },

    {
        "name": "Team email disruption",
        "affected_scope": "TEAM",
        "work_blocked": "PARTIALLY",
        "urgent_feeling": "HIGH",
        "workaround_available": True,
        "category": "EMAIL",
        "severity": "MEDIUM",
    },

    {
        "name": "Team hardware issue",
        "affected_scope": "TEAM",
        "work_blocked": "PARTIALLY",
        "urgent_feeling": "MEDIUM",
        "workaround_available": False,
        "category": "HARDWARE",
        "severity": "MEDIUM",
    },

    {
        "name": "Individual access completely blocked",
        "affected_scope": "JUST_ME",
        "work_blocked": "YES",
        "urgent_feeling": "HIGH",
        "workaround_available": True,
        "category": "ACCESS",
        "severity": "MEDIUM",
    },

    {
        "name": "Department software slowdown",
        "affected_scope": "DEPARTMENT",
        "work_blocked": "NO",
        "urgent_feeling": "MEDIUM",
        "workaround_available": True,
        "category": "SOFTWARE",
        "severity": "MEDIUM",
    },

    {
        "name": "Department network degradation",
        "affected_scope": "DEPARTMENT",
        "work_blocked": "PARTIALLY",
        "urgent_feeling": "LOW",
        "workaround_available": True,
        "category": "NETWORK",
        "severity": "MEDIUM",
    },

    {
        "name": "Department application disruption",
        "affected_scope": "DEPARTMENT",
        "work_blocked": "PARTIALLY",
        "urgent_feeling": "HIGH",
        "workaround_available": True,
        "category": "APPLICATION",
        "severity": "MEDIUM",
    },

    {
        "name": "Team access disruption",
        "affected_scope": "TEAM",
        "work_blocked": "YES",
        "urgent_feeling": "LOW",
        "workaround_available": True,
        "category": "ACCESS",
        "severity": "MEDIUM",
    },


    {
        "name": "Team network outage",
        "affected_scope": "TEAM",
        "work_blocked": "YES",
        "urgent_feeling": "HIGH",
        "workaround_available": False,
        "category": "NETWORK",
        "severity": "HIGH",
    },

    {
        "name": "Department VPN outage",
        "affected_scope": "DEPARTMENT",
        "work_blocked": "YES",
        "urgent_feeling": "HIGH",
        "workaround_available": False,
        "category": "VPN",
        "severity": "HIGH",
    },

    {
        "name": "Department application blocked",
        "affected_scope": "DEPARTMENT",
        "work_blocked": "YES",
        "urgent_feeling": "MEDIUM",
        "workaround_available": False,
        "category": "APPLICATION",
        "severity": "HIGH",
    },

    {
        "name": "Team software completely blocked",
        "affected_scope": "TEAM",
        "work_blocked": "YES",
        "urgent_feeling": "MEDIUM",
        "workaround_available": False,
        "category": "SOFTWARE",
        "severity": "HIGH",
    },

    {
        "name": "Department email outage",
        "affected_scope": "DEPARTMENT",
        "work_blocked": "YES",
        "urgent_feeling": "HIGH",
        "workaround_available": True,
        "category": "EMAIL",
        "severity": "HIGH",
    },

    {
        "name": "Department hardware failure",
        "affected_scope": "DEPARTMENT",
        "work_blocked": "YES",
        "urgent_feeling": "HIGH",
        "workaround_available": False,
        "category": "HARDWARE",
        "severity": "HIGH",
    },

    {
        "name": "Team access failure",
        "affected_scope": "TEAM",
        "work_blocked": "PARTIALLY",
        "urgent_feeling": "HIGH",
        "workaround_available": False,
        "category": "ACCESS",
        "severity": "HIGH",
    },

    {
        "name": "Department network outage",
        "affected_scope": "DEPARTMENT",
        "work_blocked": "YES",
        "urgent_feeling": "MEDIUM",
        "workaround_available": True,
        "category": "NETWORK",
        "severity": "HIGH",
    },

    {
        "name": "Team VPN completely unavailable",
        "affected_scope": "TEAM",
        "work_blocked": "YES",
        "urgent_feeling": "MEDIUM",
        "workaround_available": False,
        "category": "VPN",
        "severity": "HIGH",
    },

    {
        "name": "Department software failure",
        "affected_scope": "DEPARTMENT",
        "work_blocked": "PARTIALLY",
        "urgent_feeling": "HIGH",
        "workaround_available": False,
        "category": "SOFTWARE",
        "severity": "HIGH",
    },


    {
        "name": "Organisation network outage",
        "affected_scope": "ORGANISATION",
        "work_blocked": "YES",
        "urgent_feeling": "HIGH",
        "workaround_available": False,
        "category": "NETWORK",
        "severity": "CRITICAL",
    },

    {
        "name": "Organisation VPN unavailable",
        "affected_scope": "ORGANISATION",
        "work_blocked": "YES",
        "urgent_feeling": "MEDIUM",
        "workaround_available": False,
        "category": "VPN",
        "severity": "CRITICAL",
    },

    {
        "name": "Organisation application outage",
        "affected_scope": "ORGANISATION",
        "work_blocked": "YES",
        "urgent_feeling": "HIGH",
        "workaround_available": False,
        "category": "APPLICATION",
        "severity": "CRITICAL",
    },

    {
        "name": "Organisation email disruption",
        "affected_scope": "ORGANISATION",
        "work_blocked": "PARTIALLY",
        "urgent_feeling": "HIGH",
        "workaround_available": False,
        "category": "EMAIL",
        "severity": "CRITICAL",
    },

    {
        "name": "Organisation software outage",
        "affected_scope": "ORGANISATION",
        "work_blocked": "YES",
        "urgent_feeling": "MEDIUM",
        "workaround_available": False,
        "category": "SOFTWARE",
        "severity": "CRITICAL",
    },

    {
        "name": "Organisation hardware failure",
        "affected_scope": "ORGANISATION",
        "work_blocked": "YES",
        "urgent_feeling": "HIGH",
        "workaround_available": True,
        "category": "HARDWARE",
        "severity": "CRITICAL",
    },

    {
        "name": "Organisation access failure",
        "affected_scope": "ORGANISATION",
        "work_blocked": "YES",
        "urgent_feeling": "MEDIUM",
        "workaround_available": False,
        "category": "ACCESS",
        "severity": "CRITICAL",
    },

    {
        "name": "Organisation network partially unavailable",
        "affected_scope": "ORGANISATION",
        "work_blocked": "PARTIALLY",
        "urgent_feeling": "HIGH",
        "workaround_available": True,
        "category": "NETWORK",
        "severity": "CRITICAL",
    },

    {
        "name": "Organisation application disruption",
        "affected_scope": "ORGANISATION",
        "work_blocked": "PARTIALLY",
        "urgent_feeling": "MEDIUM",
        "workaround_available": False,
        "category": "APPLICATION",
        "severity": "CRITICAL",
    },

    {
        "name": "Organisation VPN outage with workaround",
        "affected_scope": "ORGANISATION",
        "work_blocked": "YES",
        "urgent_feeling": "HIGH",
        "workaround_available": True,
        "category": "VPN",
        "severity": "CRITICAL",
    },
]

SCOPE_MAP = {
    "JUST_ME": 0,
    "TEAM": 1,
    "DEPARTMENT": 2,
    "ORGANISATION": 3,
}

BLOCKED_MAP = {
    "NO": 0,
    "PARTIALLY": 1,
    "YES": 2,
}

URGENCY_MAP = {
    "LOW": 0,
    "MEDIUM": 1,
    "HIGH": 2,
}

CATEGORY_MAP = {
    "ACCESS": 0,
    "APPLICATION": 1,
    "EMAIL": 2,
    "HARDWARE": 3,
    "NETWORK": 4,
    "SOFTWARE": 5,
    "VPN": 6,
}


def encode_ticket(ticket):
    return [
        SCOPE_MAP.get(
            ticket["affected_scope"],
            0,
        ),
        BLOCKED_MAP.get(
            ticket["work_blocked"],
            0,
        ),
        URGENCY_MAP.get(
            ticket["urgent_feeling"],
            0,
        ),
        int(
            ticket["workaround_available"]
        ),
        CATEGORY_MAP.get(
            ticket["category"],
            0,
        ),
    ]

print("=" * 90)
print("UNSEEN SEVERITY CLASSIFIER TEST")
print("=" * 90)

if not MODEL_PATH.exists():
    print("\nERROR: Severity model not found.")
    print(f"Expected: {MODEL_PATH}")
    print("\nRun this first:")
    print("python training\\train_severity_model.py")
    raise SystemExit(1)


if not LABELS_PATH.exists():
    print("\nERROR: Severity labels not found.")
    print(f"Expected: {LABELS_PATH}")
    print("\nRun this first:")
    print("python training\\train_severity_model.py")
    raise SystemExit(1)


model = lgb.Booster(
    model_file=str(MODEL_PATH)
)


with open(
    LABELS_PATH,
    "r",
    encoding="utf-8",
) as file:
    label_data = json.load(file)


LABEL_TO_SEVERITY = {
    int(label): severity
    for label, severity
    in label_data["label_to_severity"].items()
}

print(
    f"\nLoaded {len(UNSEEN_TICKETS)} unseen severity tickets."
)

print(
    "Model: severity_model.txt"
)

print("\n")


correct = 0
results = []

severity_totals = {}
severity_correct = {}

for ticket in UNSEEN_TICKETS:

    features = [
        encode_ticket(ticket)
    ]

    probabilities = model.predict(
        features
    )[0]

    predicted_label = int(
        probabilities.argmax()
    )

    predicted_severity = LABEL_TO_SEVERITY[
        predicted_label
    ]

    confidence = float(
        probabilities[predicted_label]
    )

    actual_severity = ticket["severity"]

    is_correct = (
        predicted_severity
        == actual_severity
    )

    if is_correct:
        correct += 1

    severity_totals.setdefault(
        actual_severity,
        0
    )

    severity_correct.setdefault(
        actual_severity,
        0
    )

    severity_totals[
        actual_severity
    ] += 1

    if is_correct:
        severity_correct[
            actual_severity
        ] += 1

    results.append({
        "ticket": ticket,
        "predicted": predicted_severity,
        "confidence": confidence,
        "correct": is_correct,
    })


for index, result in enumerate(
    results,
    start=1,
):

    ticket = result["ticket"]

    status = (
        "CORRECT"
        if result["correct"]
        else "WRONG"
    )

    print(
        f"{index:02d}. "
        f"{ticket['name']:<42} | "
        f"Actual: {ticket['severity']:<8} | "
        f"Predicted: {result['predicted']:<8} | "
        f"Confidence: {result['confidence']:.3f} | "
        f"{status}"
    )

total = len(
    UNSEEN_TICKETS
)

accuracy = (
    correct / total
    if total
    else 0
)

print("\n")
print("=" * 90)
print("UNSEEN SEVERITY TEST RESULTS")
print("=" * 90)

print(
    f"Total tickets:       {total}"
)

print(
    f"Correct predictions: {correct}"
)

print(
    f"Incorrect predictions: "
    f"{total - correct}"
)

print(
    f"Overall accuracy:    "
    f"{accuracy:.2%}"
)

wrong_predictions = [
    result
    for result in results
    if not result["correct"]
]

print("\n")
print("=" * 90)
print("WRONG PREDICTIONS")
print("=" * 90)

if not wrong_predictions:

    print("No wrong predictions.")

else:

    for result in wrong_predictions:

        ticket = result["ticket"]

        print(
            f"\nTicket:     {ticket['name']}"
        )

        print(
            f"Actual:     "
            f"{ticket['severity']}"
        )

        print(
            f"Predicted:  "
            f"{result['predicted']}"
        )

        print(
            f"Confidence: "
            f"{result['confidence']:.3f}"
        )

        print(
            f"Scope:      "
            f"{ticket['affected_scope']}"
        )

        print(
            f"Blocked:    "
            f"{ticket['work_blocked']}"
        )

        print(
            f"Urgency:    "
            f"{ticket['urgent_feeling']}"
        )

        print(
            f"Workaround: "
            f"{ticket['workaround_available']}"
        )

        print(
            f"Category:   "
            f"{ticket['category']}"
        )


print("\n")
print("=" * 90)
print("SEVERITY-WISE RESULTS")
print("=" * 90)

severity_order = [
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
]

for severity in severity_order:

    total_for_severity = (
        severity_totals.get(
            severity,
            0,
        )
    )

    correct_for_severity = (
        severity_correct.get(
            severity,
            0,
        )
    )

    severity_accuracy = (
        correct_for_severity
        / total_for_severity
        if total_for_severity
        else 0
    )

    print(
        f"{severity:<10} "
        f"{correct_for_severity}/"
        f"{total_for_severity} "
        f"({severity_accuracy:.2%})"
    )

print("\n")
print("=" * 90)
print("LOWEST CONFIDENCE PREDICTIONS")
print("=" * 90)

lowest_confidence = sorted(
    results,
    key=lambda result:
        result["confidence"],
)[:10]

for result in lowest_confidence:

    ticket = result["ticket"]

    status = (
        "CORRECT"
        if result["correct"]
        else "WRONG"
    )

    print(
        f"{ticket['name']:<42} | "
        f"{result['confidence']:.3f} | "
        f"{result['predicted']:<8} | "
        f"{status}"
    )

print("\n")
print("=" * 90)
print("TEST COMPLETE")
print("=" * 90)