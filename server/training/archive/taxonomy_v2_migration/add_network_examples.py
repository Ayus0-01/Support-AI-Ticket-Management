import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

SOURCE_PATH = (
    BASE_DIR / "category_seed_data_access_expanded.json"
)

OUTPUT_PATH = (
    BASE_DIR / "category_seed_data_network_expanded.json"
)


NETWORK_EXAMPLES = [
    # -------------------------------------------------
    # WIFI
    # -------------------------------------------------

    {
        "subject": "Office WiFi not connecting",
        "description": "My laptop cannot connect to the office WiFi network.",
        "category": "NETWORK",
        "subcategory": "WiFi",
    },
    {
        "subject": "WiFi keeps disconnecting",
        "description": "The office WiFi connection repeatedly disconnects while I am working.",
        "category": "NETWORK",
        "subcategory": "WiFi",
    },
    {
        "subject": "Unable to join corporate WiFi",
        "description": "I cannot connect my work laptop to the corporate wireless network.",
        "category": "NETWORK",
        "subcategory": "WiFi",
    },
    {
        "subject": "Office wireless network unavailable",
        "description": "The WiFi network at the office is not available on my laptop.",
        "category": "NETWORK",
        "subcategory": "WiFi",
    },
    {
        "subject": "WiFi connection drops",
        "description": "My wireless connection keeps dropping several times during the day.",
        "category": "NETWORK",
        "subcategory": "WiFi",
    },
    {
        "subject": "Corporate WiFi authentication problem",
        "description": "My laptop cannot successfully connect to the company WiFi.",
        "category": "NETWORK",
        "subcategory": "WiFi",
    },
    {
        "subject": "WiFi signal keeps disappearing",
        "description": "The office wireless network disappears from the available network list.",
        "category": "NETWORK",
        "subcategory": "WiFi",
    },
    {
        "subject": "Laptop cannot detect office WiFi",
        "description": "The office WiFi network is not appearing on my work laptop.",
        "category": "NETWORK",
        "subcategory": "WiFi",
    },
    {
        "subject": "Wireless connection failure",
        "description": "I am unable to establish a connection to the company's wireless network.",
        "category": "NETWORK",
        "subcategory": "WiFi",
    },
    {
        "subject": "WiFi connectivity issue",
        "description": "My laptop connects to WiFi briefly and then loses the connection.",
        "category": "NETWORK",
        "subcategory": "WiFi",
    },
    {
        "subject": "Office wireless access problem",
        "description": "I cannot get reliable access to the office wireless network.",
        "category": "NETWORK",
        "subcategory": "WiFi",
    },
    {
        "subject": "WiFi disconnects during work",
        "description": "The corporate WiFi connection keeps disconnecting while I use internal systems.",
        "category": "NETWORK",
        "subcategory": "WiFi",
    },
    {
        "subject": "Cannot connect to company wireless",
        "description": "My work device is unable to connect to the company wireless network.",
        "category": "NETWORK",
        "subcategory": "WiFi",
    },
    {
        "subject": "WiFi network not visible",
        "description": "The expected office WiFi network is missing from the list of available networks.",
        "category": "NETWORK",
        "subcategory": "WiFi",
    },
    {
        "subject": "Wireless network connection problem",
        "description": "My laptop is having trouble maintaining a connection to office WiFi.",
        "category": "NETWORK",
        "subcategory": "WiFi",
    },
    {
        "subject": "Company WiFi keeps dropping",
        "description": "The corporate wireless connection repeatedly drops from my workstation.",
        "category": "NETWORK",
        "subcategory": "WiFi",
    },
    {
        "subject": "Work laptop WiFi problem",
        "description": "I cannot reliably connect my work laptop to the office wireless network.",
        "category": "NETWORK",
        "subcategory": "WiFi",
    },
    {
        "subject": "Wireless access failure",
        "description": "The office wireless network is not allowing my device to connect.",
        "category": "NETWORK",
        "subcategory": "WiFi",
    },

    # -------------------------------------------------
    # LAN
    # -------------------------------------------------

    {
        "subject": "LAN connection not working",
        "description": "My workstation cannot connect to the company network through the LAN cable.",
        "category": "NETWORK",
        "subcategory": "LAN",
    },
    {
        "subject": "Ethernet connection failure",
        "description": "The wired Ethernet connection to my workstation is not working.",
        "category": "NETWORK",
        "subcategory": "LAN",
    },
    {
        "subject": "Office LAN unavailable",
        "description": "My desktop cannot access the office network using the wired LAN connection.",
        "category": "NETWORK",
        "subcategory": "LAN",
    },
    {
        "subject": "Wired network connection problem",
        "description": "The network cable is connected but my workstation has no LAN connectivity.",
        "category": "NETWORK",
        "subcategory": "LAN",
    },
    {
        "subject": "Ethernet port not connecting",
        "description": "My workstation is unable to establish a wired network connection.",
        "category": "NETWORK",
        "subcategory": "LAN",
    },
    {
        "subject": "LAN connection keeps dropping",
        "description": "The wired network connection repeatedly disconnects while I am working.",
        "category": "NETWORK",
        "subcategory": "LAN",
    },
    {
        "subject": "Cannot access network over Ethernet",
        "description": "My computer cannot reach company network resources through its Ethernet connection.",
        "category": "NETWORK",
        "subcategory": "LAN",
    },
    {
        "subject": "Wired network unavailable",
        "description": "The wired office network is unavailable on my workstation.",
        "category": "NETWORK",
        "subcategory": "LAN",
    },
    {
        "subject": "Ethernet cable connection issue",
        "description": "My computer is not getting network connectivity through the Ethernet cable.",
        "category": "NETWORK",
        "subcategory": "LAN",
    },
    {
        "subject": "LAN access problem",
        "description": "I cannot access internal network resources through the office LAN.",
        "category": "NETWORK",
        "subcategory": "LAN",
    },
    {
        "subject": "Desktop wired network failure",
        "description": "The wired network connection on my desktop has stopped working.",
        "category": "NETWORK",
        "subcategory": "LAN",
    },
    {
        "subject": "Corporate Ethernet not working",
        "description": "My workstation cannot connect to the corporate network using Ethernet.",
        "category": "NETWORK",
        "subcategory": "LAN",
    },
    {
        "subject": "Wired connection disconnected",
        "description": "The LAN connection on my work computer keeps disconnecting.",
        "category": "NETWORK",
        "subcategory": "LAN",
    },
    {
        "subject": "Network cable connection failure",
        "description": "The network cable is connected but the workstation has no network access.",
        "category": "NETWORK",
        "subcategory": "LAN",
    },
    {
        "subject": "Office Ethernet connection issue",
        "description": "I am unable to use the wired office network from my workstation.",
        "category": "NETWORK",
        "subcategory": "LAN",
    },
    {
        "subject": "LAN connectivity problem",
        "description": "My wired connection to the internal network is not functioning correctly.",
        "category": "NETWORK",
        "subcategory": "LAN",
    },
    {
        "subject": "Wired office network unavailable",
        "description": "The office LAN is unavailable on my company computer.",
        "category": "NETWORK",
        "subcategory": "LAN",
    },
    {
        "subject": "Ethernet network access failure",
        "description": "My workstation cannot establish network access using the wired connection.",
        "category": "NETWORK",
        "subcategory": "LAN",
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

    print(
        "Existing tickets:",
        len(existing),
    )

    print(
        "New NETWORK examples:",
        len(NETWORK_EXAMPLES),
    )

    if len(NETWORK_EXAMPLES) != 36:
        raise ValueError(
            "Expected exactly 36 NETWORK examples."
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
        for example in NETWORK_EXAMPLES
        if (
            example["subject"].strip().lower(),
            example["description"].strip().lower(),
        )
        in existing_keys
    ]

    if duplicate_examples:
        raise ValueError(
            "Duplicate NETWORK examples found."
        )

    new_tickets = (
        existing + NETWORK_EXAMPLES
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
        "\nNETWORK EXPANSION COMPLETE"
    )

    print(
        "Total tickets:",
        len(new_tickets),
    )

    print(
        "NETWORK total:",
        sum(
            ticket["category"] == "NETWORK"
            for ticket in new_tickets
        ),
    )

    print(
        "Output:",
        OUTPUT_PATH,
    )

    print(
        "\nOriginal ACCESS-expanded dataset "
        "was NOT modified."
    )


if __name__ == "__main__":
    main()