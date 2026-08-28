import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

SOURCE_PATH = (
    BASE_DIR / "category_seed_data_vpn_expanded.json"
)

OUTPUT_PATH = (
    BASE_DIR / "category_seed_data_hardware_expanded.json"
)


HARDWARE_EXAMPLES = [
    # -------------------------------------------------
    # DESKTOP
    # -------------------------------------------------

    {
        "subject": "Desktop computer not starting",
        "description": "My company desktop does not power on when I press the power button.",
        "category": "HARDWARE",
        "subcategory": "Desktop",
    },
    {
        "subject": "Desktop hardware failure",
        "description": "The office desktop has stopped working and will not start.",
        "category": "HARDWARE",
        "subcategory": "Desktop",
    },
    {
        "subject": "Workstation desktop problem",
        "description": "My desktop workstation is not functioning correctly.",
        "category": "HARDWARE",
        "subcategory": "Desktop",
    },
    {
        "subject": "Desktop screen not working",
        "description": "The company desktop starts but does not display anything on the connected screen.",
        "category": "HARDWARE",
        "subcategory": "Desktop",
    },
    {
        "subject": "Office desktop failure",
        "description": "The desktop assigned to my desk has stopped operating.",
        "category": "HARDWARE",
        "subcategory": "Desktop",
    },
    {
        "subject": "Desktop power issue",
        "description": "My work desktop does not power on even though it is connected to power.",
        "category": "HARDWARE",
        "subcategory": "Desktop",
    },
    {
        "subject": "Desktop workstation unavailable",
        "description": "I cannot use my assigned desktop because the computer is not working.",
        "category": "HARDWARE",
        "subcategory": "Desktop",
    },
    {
        "subject": "Desktop computer keeps shutting down",
        "description": "The company desktop repeatedly powers off while I am working.",
        "category": "HARDWARE",
        "subcategory": "Desktop",
    },
    {
        "subject": "Desktop hardware problem",
        "description": "My office desktop has developed a hardware problem and is not usable.",
        "category": "HARDWARE",
        "subcategory": "Desktop",
    },
    {
        "subject": "Desktop will not boot",
        "description": "The assigned desktop does not boot into the operating system.",
        "category": "HARDWARE",
        "subcategory": "Desktop",
    },
    {
        "subject": "Company desktop stopped working",
        "description": "My company desktop has suddenly stopped functioning.",
        "category": "HARDWARE",
        "subcategory": "Desktop",
    },
    {
        "subject": "Desktop workstation power failure",
        "description": "The desktop workstation has no power and will not start.",
        "category": "HARDWARE",
        "subcategory": "Desktop",
    },
    {
        "subject": "Office PC not functioning",
        "description": "The office desktop computer is no longer functioning normally.",
        "category": "HARDWARE",
        "subcategory": "Desktop",
    },
    {
        "subject": "Desktop computer hardware issue",
        "description": "There appears to be a hardware failure with my company desktop.",
        "category": "HARDWARE",
        "subcategory": "Desktop",
    },
    {
        "subject": "Desktop system unavailable",
        "description": "My assigned desktop cannot be used because the computer has failed.",
        "category": "HARDWARE",
        "subcategory": "Desktop",
    },
    {
        "subject": "Desktop machine not responding",
        "description": "The office desktop is powered on but is not responding to input.",
        "category": "HARDWARE",
        "subcategory": "Desktop",
    },
    {
        "subject": "Desktop workstation failure",
        "description": "My desktop workstation has stopped functioning during normal work.",
        "category": "HARDWARE",
        "subcategory": "Desktop",
    },
    {
        "subject": "Corporate desktop problem",
        "description": "The corporate desktop assigned to me is experiencing a hardware failure.",
        "category": "HARDWARE",
        "subcategory": "Desktop",
    },

    # -------------------------------------------------
    # DOCKING STATION
    # -------------------------------------------------

    {
        "subject": "Docking station not detecting devices",
        "description": "My docking station is connected but does not detect the attached devices.",
        "category": "HARDWARE",
        "subcategory": "Docking station",
    },
    {
        "subject": "Docking station not working",
        "description": "The docking station at my desk is no longer functioning correctly.",
        "category": "HARDWARE",
        "subcategory": "Docking station",
    },
    {
        "subject": "Laptop dock connection issue",
        "description": "My laptop dock is not connecting to the external devices properly.",
        "category": "HARDWARE",
        "subcategory": "Docking station",
    },
    {
        "subject": "Dock displays not detected",
        "description": "The docking station is connected but the external displays are not detected.",
        "category": "HARDWARE",
        "subcategory": "Docking station",
    },
    {
        "subject": "Docking station power problem",
        "description": "The docking station is not providing power or connectivity to my laptop.",
        "category": "HARDWARE",
        "subcategory": "Docking station",
    },
    {
        "subject": "USB devices missing from dock",
        "description": "Devices connected through my docking station are not being recognized.",
        "category": "HARDWARE",
        "subcategory": "Docking station",
    },
    {
        "subject": "External monitor not working through dock",
        "description": "My external monitor does not work when connected through the docking station.",
        "category": "HARDWARE",
        "subcategory": "Docking station",
    },
    {
        "subject": "Docking station connection failure",
        "description": "The company docking station cannot establish a proper connection with my laptop.",
        "category": "HARDWARE",
        "subcategory": "Docking station",
    },
    {
        "subject": "Work laptop dock issue",
        "description": "The docking station for my work laptop is not functioning correctly.",
        "category": "HARDWARE",
        "subcategory": "Docking station",
    },
    {
        "subject": "Dock not recognizing peripherals",
        "description": "My keyboard and mouse are not detected when connected through the docking station.",
        "category": "HARDWARE",
        "subcategory": "Docking station",
    },
    {
        "subject": "Docking station intermittently disconnects",
        "description": "The docking station repeatedly disconnects from my laptop during work.",
        "category": "HARDWARE",
        "subcategory": "Docking station",
    },
    {
        "subject": "Dock external devices unavailable",
        "description": "External devices connected to my dock are unavailable.",
        "category": "HARDWARE",
        "subcategory": "Docking station",
    },
    {
        "subject": "Dock station display issue",
        "description": "The docking station is not passing the display signal to my external screen.",
        "category": "HARDWARE",
        "subcategory": "Docking station",
    },
    {
        "subject": "Docking station USB problem",
        "description": "The USB ports on my docking station are not recognizing connected equipment.",
        "category": "HARDWARE",
        "subcategory": "Docking station",
    },
    {
        "subject": "Laptop dock unavailable",
        "description": "My assigned docking station has stopped working with the company laptop.",
        "category": "HARDWARE",
        "subcategory": "Docking station",
    },
    {
        "subject": "Docking station not connecting",
        "description": "The laptop does not recognize the connected docking station.",
        "category": "HARDWARE",
        "subcategory": "Docking station",
    },
    {
        "subject": "Dock setup problem",
        "description": "The docking station is not providing the expected connections for my workstation.",
        "category": "HARDWARE",
        "subcategory": "Docking station",
    },
    {
        "subject": "Office docking station failure",
        "description": "The docking station at my workstation is not functioning properly.",
        "category": "HARDWARE",
        "subcategory": "Docking station",
    },

    # -------------------------------------------------
    # MOBILE DEVICE
    # -------------------------------------------------

    {
        "subject": "Company mobile device not working",
        "description": "My assigned company phone is not functioning correctly.",
        "category": "HARDWARE",
        "subcategory": "Mobile device",
    },
    {
        "subject": "Work phone hardware issue",
        "description": "The company mobile device issued to me has developed a hardware problem.",
        "category": "HARDWARE",
        "subcategory": "Mobile device",
    },
    {
        "subject": "Corporate phone not powering on",
        "description": "My company mobile phone does not power on.",
        "category": "HARDWARE",
        "subcategory": "Mobile device",
    },
    {
        "subject": "Work tablet problem",
        "description": "The company tablet assigned to me is not functioning correctly.",
        "category": "HARDWARE",
        "subcategory": "Mobile device",
    },
    {
        "subject": "Mobile device screen failure",
        "description": "The screen on my company mobile device is no longer working.",
        "category": "HARDWARE",
        "subcategory": "Mobile device",
    },
    {
        "subject": "Company phone battery problem",
        "description": "The battery on my work phone is failing and the device shuts down unexpectedly.",
        "category": "HARDWARE",
        "subcategory": "Mobile device",
    },
    {
        "subject": "Corporate smartphone not responding",
        "description": "My company smartphone has stopped responding to input.",
        "category": "HARDWARE",
        "subcategory": "Mobile device",
    },
    {
        "subject": "Mobile hardware failure",
        "description": "The hardware on my assigned mobile device is no longer functioning normally.",
        "category": "HARDWARE",
        "subcategory": "Mobile device",
    },
    {
        "subject": "Work phone charging issue",
        "description": "My company phone is not charging properly.",
        "category": "HARDWARE",
        "subcategory": "Mobile device",
    },
    {
        "subject": "Company tablet will not start",
        "description": "The tablet issued for work does not start when I press the power button.",
        "category": "HARDWARE",
        "subcategory": "Mobile device",
    },
    {
        "subject": "Mobile device hardware problem",
        "description": "My assigned mobile device has a hardware fault.",
        "category": "HARDWARE",
        "subcategory": "Mobile device",
    },
    {
        "subject": "Corporate smartphone hardware issue",
        "description": "The work smartphone has stopped functioning due to a hardware problem.",
        "category": "HARDWARE",
        "subcategory": "Mobile device",
    },
    {
        "subject": "Work phone display problem",
        "description": "The display on my company mobile phone is malfunctioning.",
        "category": "HARDWARE",
        "subcategory": "Mobile device",
    },
    {
        "subject": "Company tablet hardware failure",
        "description": "My company tablet has experienced a hardware failure.",
        "category": "HARDWARE",
        "subcategory": "Mobile device",
    },
    {
        "subject": "Mobile device power failure",
        "description": "My assigned corporate mobile device will not power on.",
        "category": "HARDWARE",
        "subcategory": "Mobile device",
    },
    {
        "subject": "Work smartphone problem",
        "description": "The smartphone supplied by the company is not working properly.",
        "category": "HARDWARE",
        "subcategory": "Mobile device",
    },
    {
        "subject": "Corporate mobile device unavailable",
        "description": "I cannot use my company mobile device because of a hardware problem.",
        "category": "HARDWARE",
        "subcategory": "Mobile device",
    },
    {
        "subject": "Mobile hardware issue",
        "description": "My company-issued mobile device has stopped functioning normally.",
        "category": "HARDWARE",
        "subcategory": "Mobile device",
    },
]


def main():
    with open(
        SOURCE_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    existing = data["tickets"]

    print("Existing tickets:", len(existing))
    print(
        "New HARDWARE examples:",
        len(HARDWARE_EXAMPLES),
    )

    if len(HARDWARE_EXAMPLES) != 54:
        raise ValueError(
            "Expected exactly 54 HARDWARE examples."
        )

    existing_keys = {
        (
            ticket["subject"].strip().lower(),
            ticket["description"].strip().lower(),
        )
        for ticket in existing
    }

    duplicate_examples = [
        example
        for example in HARDWARE_EXAMPLES
        if (
            example["subject"].strip().lower(),
            example["description"].strip().lower(),
        )
        in existing_keys
    ]

    if duplicate_examples:
        raise ValueError(
            "Duplicate HARDWARE examples found."
        )

    new_tickets = (
        existing + HARDWARE_EXAMPLES
    )

    output = {
        "taxonomy_version": "v2",
        "source_taxonomy_version": data.get(
            "source_taxonomy_version"
        ),
        "taxonomy": data.get(
            "taxonomy",
            []
        ),
        "tickets": new_tickets,
    }

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            output,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(
        "\nHARDWARE EXPANSION COMPLETE"
    )

    print(
        "Total tickets:",
        len(new_tickets),
    )

    print(
        "HARDWARE total:",
        sum(
            ticket["category"] == "HARDWARE"
            for ticket in new_tickets
        ),
    )

    print(
        "Output:",
        OUTPUT_PATH,
    )

    print(
        "\nOriginal VPN-expanded dataset "
        "was NOT modified."
    )


if __name__ == "__main__":
    main()