from apps.tickets.classification.category_classifier import (
    predict_category,
)


TEST_TICKETS = [
    {
        "subject": "VPN connection failing",
        "description": "I cannot connect to the company VPN from my laptop.",
        "expected_category": "VPN",
    },
    {
        "subject": "Request new monitor",
        "description": "I need a new monitor for my workstation.",
        "expected_category": "HARDWARE",
    },
    {
        "subject": "Mailbox unavailable",
        "description": "I cannot access my company email inbox.",
        "expected_category": "EMAIL",
    },
    {
        "subject": "DNS lookup failure",
        "description": "DNS resolution is failing for internal websites.",
        "expected_category": "NETWORK",
    },
    {
        "subject": "License activation problem",
        "description": "My software license will not activate.",
        "expected_category": "SOFTWARE",
    },
    {
        "subject": "Request access to resource",
        "description": "I need permission to access a company resource.",
        "expected_category": "ACCESS",
    },
    {
        "subject": "Application crashed",
        "description": "The business application crashes whenever I open it.",
        "expected_category": "APPLICATION",
    },
]


def main():
    print("\nCATEGORY INFERENCE TEST")
    print("=" * 80)

    correct = 0

    for ticket in TEST_TICKETS:

        result = predict_category(
            ticket["subject"],
            ticket["description"],
        )

        actual = ticket["expected_category"]
        predicted = result["category"]
        confidence = result["confidence"]
        route = result["route"]

        is_correct = predicted == actual

        if is_correct:
            correct += 1
            status = "✓"
        else:
            status = "✗"

        print(
            f"{status} "
            f"{ticket['subject']:<35} "
            f"Expected: {actual:<12} "
            f"Predicted: {predicted:<12} "
            f"Confidence: {confidence:.3f} "
            f"Route: {route}"
        )

    print("\n" + "=" * 80)

    accuracy = (
        correct / len(TEST_TICKETS)
    ) * 100

    print(
        f"Inference accuracy: "
        f"{correct}/{len(TEST_TICKETS)} "
        f"({accuracy:.2f}%)"
    )


if __name__ == "__main__":
    main()