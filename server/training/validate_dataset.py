import json
from pathlib import Path


DATASET_PATH = Path(__file__).parent / "category_seed_data.json"


def load_dataset():
    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def validate_taxonomy(data):
    errors = []

    if "taxonomy_version" not in data:
        errors.append("Missing taxonomy_version")

    if "categories" not in data:
        errors.append("Missing categories")
        return errors

    if "tickets" not in data:
        errors.append("Missing tickets")

    categories = data["categories"]

    if not categories:
        errors.append("No categories found")

    category_names = set()

    for category in categories:
        name = category.get("name")

        if not name:
            errors.append("Category without a name")
            continue

        if name in category_names:
            errors.append(f"Duplicate category: {name}")

        category_names.add(name)

        subcategories = category.get("subcategories", [])

        if not subcategories:
            errors.append(
                f"Category '{name}' has no subcategories"
            )

        if len(subcategories) != len(set(subcategories)):
            errors.append(
                f"Category '{name}' has duplicate subcategories"
            )

    return errors


def main():
    data = load_dataset()

    errors = validate_taxonomy(data)

    if errors:
        print("❌ Taxonomy validation failed:")

        for error in errors:
            print(f" - {error}")

        raise SystemExit(1)

    print("✅ Taxonomy validation passed.")

    print(
        f"Categories: {len(data['categories'])}"
    )

    total_subcategories = sum(
        len(category["subcategories"])
        for category in data["categories"]
    )

    print(
        f"Subcategories: {total_subcategories}"
    )

    print(
        f"Training tickets: {len(data['tickets'])}"
    )


if __name__ == "__main__":
    main()