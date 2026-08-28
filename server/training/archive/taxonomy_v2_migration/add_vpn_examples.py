import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

SOURCE_PATH = (
    BASE_DIR / "category_seed_data_network_expanded.json"
)

OUTPUT_PATH = (
    BASE_DIR / "category_seed_data_vpn_expanded.json"
)


VPN_EXAMPLES = [
    # -------------------------------------------------
    # CLIENT INSTALL
    # -------------------------------------------------

    {
        "subject": "Install VPN client",
        "description": "I need the corporate VPN client installed on my work laptop.",
        "category": "VPN",
        "subcategory": "Client install",
    },
    {
        "subject": "VPN client installation request",
        "description": "Please install the approved VPN client on my company computer.",
        "category": "VPN",
        "subcategory": "Client install",
    },
    {
        "subject": "Need VPN software installed",
        "description": "My laptop does not have the corporate VPN application installed.",
        "category": "VPN",
        "subcategory": "Client install",
    },
    {
        "subject": "Set up VPN client",
        "description": "I need the company VPN client installed and configured on my workstation.",
        "category": "VPN",
        "subcategory": "Client install",
    },
    {
        "subject": "VPN application missing",
        "description": "The corporate VPN application is not installed on my work laptop.",
        "category": "VPN",
        "subcategory": "Client install",
    },
    {
        "subject": "Request corporate VPN client",
        "description": "Please provide and install the approved VPN client for my work device.",
        "category": "VPN",
        "subcategory": "Client install",
    },
    {
        "subject": "VPN software setup needed",
        "description": "I need the VPN software installed so I can connect remotely.",
        "category": "VPN",
        "subcategory": "Client install",
    },
    {
        "subject": "Install remote access VPN",
        "description": "Please install the corporate VPN software required for remote access.",
        "category": "VPN",
        "subcategory": "Client install",
    },
    {
        "subject": "VPN client not installed",
        "description": "My new work laptop does not have the required VPN client.",
        "category": "VPN",
        "subcategory": "Client install",
    },
    {
        "subject": "VPN setup on new laptop",
        "description": "I need the corporate VPN client installed on my new company laptop.",
        "category": "VPN",
        "subcategory": "Client install",
    },
    {
        "subject": "Configure VPN application",
        "description": "Please install the approved VPN application on my workstation.",
        "category": "VPN",
        "subcategory": "Client install",
    },
    {
        "subject": "Remote VPN software installation",
        "description": "I need the VPN software installed for remote work access.",
        "category": "VPN",
        "subcategory": "Client install",
    },
    {
        "subject": "VPN client deployment",
        "description": "The corporate VPN client needs to be installed on my work computer.",
        "category": "VPN",
        "subcategory": "Client install",
    },
    {
        "subject": "Corporate VPN application setup",
        "description": "Please set up the approved VPN client on my company device.",
        "category": "VPN",
        "subcategory": "Client install",
    },
    {
        "subject": "Need remote VPN client",
        "description": "I need the corporate VPN application installed before I can work remotely.",
        "category": "VPN",
        "subcategory": "Client install",
    },
    {
        "subject": "VPN installer request",
        "description": "Please install the approved VPN client required for corporate remote access.",
        "category": "VPN",
        "subcategory": "Client install",
    },
    {
        "subject": "New workstation VPN setup",
        "description": "The VPN client needs to be installed on my newly issued workstation.",
        "category": "VPN",
        "subcategory": "Client install",
    },
    {
        "subject": "VPN client required",
        "description": "I need the company VPN application installed on my device for remote connectivity.",
        "category": "VPN",
        "subcategory": "Client install",
    },

    # -------------------------------------------------
    # TIMEOUT
    # -------------------------------------------------

    {
        "subject": "VPN connection timeout",
        "description": "The VPN connection attempt times out before it can connect.",
        "category": "VPN",
        "subcategory": "Timeout",
    },
    {
        "subject": "VPN request keeps timing out",
        "description": "My VPN connection repeatedly times out while trying to establish a session.",
        "category": "VPN",
        "subcategory": "Timeout",
    },
    {
        "subject": "VPN server timeout",
        "description": "The VPN client reports a timeout when connecting to the corporate server.",
        "category": "VPN",
        "subcategory": "Timeout",
    },
    {
        "subject": "Remote VPN connection timeout",
        "description": "The remote VPN connection times out before authentication completes.",
        "category": "VPN",
        "subcategory": "Timeout",
    },
    {
        "subject": "VPN connection attempt times out",
        "description": "Every attempt to connect to the corporate VPN ends with a timeout.",
        "category": "VPN",
        "subcategory": "Timeout",
    },
    {
        "subject": "VPN gateway timeout",
        "description": "The VPN client cannot reach the gateway before the connection times out.",
        "category": "VPN",
        "subcategory": "Timeout",
    },
    {
        "subject": "VPN timeout error",
        "description": "A timeout error appears whenever I try to establish the VPN connection.",
        "category": "VPN",
        "subcategory": "Timeout",
    },
    {
        "subject": "VPN connection expires during setup",
        "description": "The VPN setup process times out before a connection is established.",
        "category": "VPN",
        "subcategory": "Timeout",
    },
    {
        "subject": "Corporate VPN timeout",
        "description": "The corporate VPN cannot complete the connection because the request times out.",
        "category": "VPN",
        "subcategory": "Timeout",
    },
    {
        "subject": "VPN keeps timing out",
        "description": "My VPN client repeatedly reaches a connection timeout.",
        "category": "VPN",
        "subcategory": "Timeout",
    },
    {
        "subject": "Timeout while connecting to VPN",
        "description": "The connection to the company VPN server times out every time.",
        "category": "VPN",
        "subcategory": "Timeout",
    },
    {
        "subject": "VPN connection deadline exceeded",
        "description": "The VPN client cannot establish the connection before the timeout period expires.",
        "category": "VPN",
        "subcategory": "Timeout",
    },
    {
        "subject": "VPN gateway not responding in time",
        "description": "The VPN gateway does not respond before the connection attempt times out.",
        "category": "VPN",
        "subcategory": "Timeout",
    },
    {
        "subject": "Remote access VPN timeout",
        "description": "My remote access VPN connection times out before it is established.",
        "category": "VPN",
        "subcategory": "Timeout",
    },
    {
        "subject": "VPN session initialization timeout",
        "description": "The VPN session cannot initialize because the connection request times out.",
        "category": "VPN",
        "subcategory": "Timeout",
    },
    {
        "subject": "VPN handshake timeout",
        "description": "The VPN handshake does not complete before the connection times out.",
        "category": "VPN",
        "subcategory": "Timeout",
    },
    {
        "subject": "VPN login connection timeout",
        "description": "The VPN connection times out while the client is trying to establish the session.",
        "category": "VPN",
        "subcategory": "Timeout",
    },
    {
        "subject": "VPN connection timed out",
        "description": "The corporate VPN connection repeatedly ends with a timeout message.",
        "category": "VPN",
        "subcategory": "Timeout",
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
        "New VPN examples:",
        len(VPN_EXAMPLES),
    )

    if len(VPN_EXAMPLES) != 36:
        raise ValueError(
            "Expected exactly 36 VPN examples."
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
        for example in VPN_EXAMPLES
        if (
            example["subject"].strip().lower(),
            example["description"].strip().lower(),
        )
        in existing_keys
    ]

    if duplicate_examples:
        raise ValueError(
            "Duplicate VPN examples found."
        )

    new_tickets = existing + VPN_EXAMPLES

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
        "\nVPN EXPANSION COMPLETE"
    )

    print(
        "Total tickets:",
        len(new_tickets),
    )

    print(
        "VPN total:",
        sum(
            ticket["category"] == "VPN"
            for ticket in new_tickets
        ),
    )

    print(
        "Output:",
        OUTPUT_PATH,
    )

    print(
        "\nOriginal NETWORK-expanded dataset "
        "was NOT modified."
    )


if __name__ == "__main__":
    main()