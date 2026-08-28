from pathlib import Path
import shutil


TRAINING_DIR = Path(__file__).resolve().parent

DATASETS_DIR = TRAINING_DIR / "datasets"
ARCHIVE_DIR = (
    TRAINING_DIR
    / "archive"
    / "taxonomy_v2_migration"
)

DATASETS_DIR.mkdir(exist_ok=True)
ARCHIVE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ---------------------------------------------------------
# Files we want in the datasets directory
# ---------------------------------------------------------

DATASET_FILES = {
    "category_seed_data.json",
    "category_seed_data_v2_final.json",
    "severity_seed_data.json",
    "unseen_category_test_data.json",
    "unseen_severity_test_data.json",
}


# ---------------------------------------------------------
# Intermediate migration files/scripts
# ---------------------------------------------------------

ARCHIVE_FILES = {
    # Migration datasets
    "category_seed_data_migrated.json",
    "category_seed_data_access_expanded.json",
    "category_seed_data_network_expanded.json",
    "category_seed_data_vpn_expanded.json",
    "category_seed_data_hardware_expanded.json",
    "category_seed_data_email_expanded.json",
    "category_seed_data_security_expanded.json",
    "category_seed_data_application_expanded.json",
    "category_seed_data_printer_expanded.json",
    "category_seed_data_v2.json",
    "category_seed_data_v2_base.json",
    "category_seed_data_v2_curated.json",
    "category_seed_data_v2_deduped.json",
    "resolved_review_tickets.json",
    "taxonomy_review_queue.json",
    "taxonomy_review_report.json",

    # Migration / audit scripts
    "add_access_examples.py",
    "add_application_examples.py",
    "add_email_examples.py",
    "add_hardware_examples.py",
    "add_network_examples.py",
    "add_printer_examples.py",
    "add_security_balance.py",
    "add_security_examples.py",
    "add_vpn_examples.py",
    "audit_migrated_dataset.py",
    "audit_taxonomy.py",
    "build_final_v2_dataset.py",
    "curate_unclassified.py",
    "migrate_safe_taxonomy.py",
    "remove_final_duplicates.py",
    "resolve_review_queue.py",
    "review_queue_report.py",
    "review_taxonomy_tickets.py",
    "review_unclassified.py",
    "taxonomy_mapping.py",
}


def move_file(
    source: Path,
    destination_dir: Path,
):
    if not source.exists():
        return

    destination = (
        destination_dir / source.name
    )

    if destination.exists():
        raise FileExistsError(
            f"Destination already exists:\n"
            f"{destination}"
        )

    shutil.move(
        str(source),
        str(destination),
    )

    print(
        f"MOVED: {source.name}"
    )


def main():

    print("=" * 90)
    print("TRAINING FOLDER CLEANUP")
    print("=" * 90)

    print("\nMoving datasets...")

    for filename in sorted(DATASET_FILES):

        move_file(
            TRAINING_DIR / filename,
            DATASETS_DIR,
        )

    print("\nArchiving migration files...")

    for filename in sorted(ARCHIVE_FILES):

        move_file(
            TRAINING_DIR / filename,
            ARCHIVE_DIR,
        )

    # Remove Python cache from training/
    pycache = TRAINING_DIR / "__pycache__"

    if pycache.exists():
        shutil.rmtree(pycache)
        print("REMOVED: training/__pycache__")

    print("\n" + "=" * 90)
    print("CLEANUP COMPLETE")
    print("=" * 90)

    print(
        "\nDatasets:",
        DATASETS_DIR,
    )

    print(
        "Archive:",
        ARCHIVE_DIR,
    )

    print(
        "\nActive training scripts were NOT moved."
    )

    print(
        "Model artifacts were NOT touched."
    )


if __name__ == "__main__":
    main()