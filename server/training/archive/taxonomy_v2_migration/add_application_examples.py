import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

SOURCE_PATH = (
    BASE_DIR / "category_seed_data_security_expanded.json"
)

OUTPUT_PATH = (
    BASE_DIR / "category_seed_data_application_expanded.json"
)


APPLICATION_EXAMPLES = [
    # -------------------------------------------------
    # ERP
    # -------------------------------------------------

    {
        "subject": "ERP application not opening",
        "description": "The company's ERP system does not open on my workstation.",
        "category": "APPLICATION",
        "subcategory": "ERP",
    },
    {
        "subject": "ERP transaction error",
        "description": "I receive an error when trying to complete a transaction in the ERP system.",
        "category": "APPLICATION",
        "subcategory": "ERP",
    },
    {
        "subject": "ERP login issue",
        "description": "I cannot access the corporate ERP application.",
        "category": "APPLICATION",
        "subcategory": "ERP",
    },
    {
        "subject": "ERP report problem",
        "description": "The ERP system is not generating the report I requested.",
        "category": "APPLICATION",
        "subcategory": "ERP",
    },
    {
        "subject": "ERP data not updating",
        "description": "Changes made in the ERP system are not appearing correctly.",
        "category": "APPLICATION",
        "subcategory": "ERP",
    },
    {
        "subject": "ERP workflow failure",
        "description": "The ERP workflow fails when I try to submit the required business process.",
        "category": "APPLICATION",
        "subcategory": "ERP",
    },
    {
        "subject": "ERP screen error",
        "description": "An error appears on the ERP screen when I perform a business operation.",
        "category": "APPLICATION",
        "subcategory": "ERP",
    },
    {
        "subject": "ERP module unavailable",
        "description": "A required module in the corporate ERP system is unavailable.",
        "category": "APPLICATION",
        "subcategory": "ERP",
    },
    {
        "subject": "ERP record update failure",
        "description": "I cannot update a record in the company ERP application.",
        "category": "APPLICATION",
        "subcategory": "ERP",
    },
    {
        "subject": "ERP processing error",
        "description": "The ERP application reports an error while processing a request.",
        "category": "APPLICATION",
        "subcategory": "ERP",
    },
    {
        "subject": "ERP business process problem",
        "description": "A business process cannot be completed in the ERP system.",
        "category": "APPLICATION",
        "subcategory": "ERP",
    },
    {
        "subject": "ERP application failure",
        "description": "The company ERP application stops working during normal use.",
        "category": "APPLICATION",
        "subcategory": "ERP",
    },
    {
        "subject": "ERP invoice issue",
        "description": "The ERP system is failing while I try to process an invoice.",
        "category": "APPLICATION",
        "subcategory": "ERP",
    },
    {
        "subject": "ERP order processing problem",
        "description": "I cannot complete an order process in the ERP application.",
        "category": "APPLICATION",
        "subcategory": "ERP",
    },
    {
        "subject": "ERP module error",
        "description": "A required ERP module shows an unexpected error.",
        "category": "APPLICATION",
        "subcategory": "ERP",
    },
    {
        "subject": "ERP business record problem",
        "description": "The ERP application is not saving a business record correctly.",
        "category": "APPLICATION",
        "subcategory": "ERP",
    },
    {
        "subject": "ERP system issue",
        "description": "I am experiencing an application problem in the corporate ERP system.",
        "category": "APPLICATION",
        "subcategory": "ERP",
    },
    {
        "subject": "ERP functionality unavailable",
        "description": "A required ERP function is currently unavailable to me.",
        "category": "APPLICATION",
        "subcategory": "ERP",
    },

    # -------------------------------------------------
    # CRM
    # -------------------------------------------------

    {
        "subject": "CRM application not loading",
        "description": "The company CRM application is not loading correctly.",
        "category": "APPLICATION",
        "subcategory": "CRM",
    },
    {
        "subject": "CRM customer record problem",
        "description": "I cannot update a customer record in the CRM system.",
        "category": "APPLICATION",
        "subcategory": "CRM",
    },
    {
        "subject": "CRM report error",
        "description": "The CRM system returns an error when I generate a customer report.",
        "category": "APPLICATION",
        "subcategory": "CRM",
    },
    {
        "subject": "CRM application failure",
        "description": "The corporate CRM application stops working during normal use.",
        "category": "APPLICATION",
        "subcategory": "CRM",
    },
    {
        "subject": "CRM customer data not updating",
        "description": "Changes to customer information are not being saved in the CRM system.",
        "category": "APPLICATION",
        "subcategory": "CRM",
    },
    {
        "subject": "CRM contact issue",
        "description": "I cannot create or update a contact in the company CRM.",
        "category": "APPLICATION",
        "subcategory": "CRM",
    },
    {
        "subject": "CRM workflow problem",
        "description": "The customer management workflow fails in the CRM application.",
        "category": "APPLICATION",
        "subcategory": "CRM",
    },
    {
        "subject": "CRM record error",
        "description": "An unexpected error appears when opening a customer record.",
        "category": "APPLICATION",
        "subcategory": "CRM",
    },
    {
        "subject": "CRM module unavailable",
        "description": "A required CRM function is not available.",
        "category": "APPLICATION",
        "subcategory": "CRM",
    },
    {
        "subject": "CRM customer update failure",
        "description": "The CRM application does not save changes to customer records.",
        "category": "APPLICATION",
        "subcategory": "CRM",
    },
    {
        "subject": "CRM search problem",
        "description": "The CRM application is not returning the expected customer records in search.",
        "category": "APPLICATION",
        "subcategory": "CRM",
    },
    {
        "subject": "CRM application error",
        "description": "I receive an application error while using the company CRM system.",
        "category": "APPLICATION",
        "subcategory": "CRM",
    },
    {
        "subject": "CRM case management issue",
        "description": "I cannot complete a case management task in the CRM application.",
        "category": "APPLICATION",
        "subcategory": "CRM",
    },
    {
        "subject": "CRM customer history unavailable",
        "description": "The CRM system is not displaying the expected customer history.",
        "category": "APPLICATION",
        "subcategory": "CRM",
    },
    {
        "subject": "CRM task processing failure",
        "description": "A task cannot be completed in the customer management application.",
        "category": "APPLICATION",
        "subcategory": "CRM",
    },
    {
        "subject": "CRM dashboard error",
        "description": "The CRM dashboard shows an unexpected error.",
        "category": "APPLICATION",
        "subcategory": "CRM",
    },
    {
        "subject": "CRM business process failure",
        "description": "A customer management process is failing in the CRM system.",
        "category": "APPLICATION",
        "subcategory": "CRM",
    },
    {
        "subject": "CRM system issue",
        "description": "I am experiencing an application problem in the corporate CRM system.",
        "category": "APPLICATION",
        "subcategory": "CRM",
    },

    # -------------------------------------------------
    # INTERNAL TOOL
    # -------------------------------------------------

    {
        "subject": "Internal company tool not working",
        "description": "An internal company application used by our team is not functioning.",
        "category": "APPLICATION",
        "subcategory": "Internal tool",
    },
    {
        "subject": "Internal tool error",
        "description": "Our internal business tool displays an unexpected error.",
        "category": "APPLICATION",
        "subcategory": "Internal tool",
    },
    {
        "subject": "Internal application unavailable",
        "description": "A company-built internal application is currently unavailable.",
        "category": "APPLICATION",
        "subcategory": "Internal tool",
    },
    {
        "subject": "Company portal problem",
        "description": "The internal company portal is not working correctly.",
        "category": "APPLICATION",
        "subcategory": "Internal tool",
    },
    {
        "subject": "Internal workflow tool failure",
        "description": "The internal tool used by our team fails during a workflow.",
        "category": "APPLICATION",
        "subcategory": "Internal tool",
    },
    {
        "subject": "Internal business application issue",
        "description": "An internal business application is showing an unexpected problem.",
        "category": "APPLICATION",
        "subcategory": "Internal tool",
    },
    {
        "subject": "Company-built tool not responding",
        "description": "The internal tool developed for our organization is not responding.",
        "category": "APPLICATION",
        "subcategory": "Internal tool",
    },
    {
        "subject": "Internal tool access problem",
        "description": "The internal company tool is not functioning when I try to use it.",
        "category": "APPLICATION",
        "subcategory": "Internal tool",
    },
    {
        "subject": "Internal dashboard failure",
        "description": "The company's internal dashboard application is not working properly.",
        "category": "APPLICATION",
        "subcategory": "Internal tool",
    },
    {
        "subject": "Internal request tool issue",
        "description": "The internal tool used for submitting requests is failing.",
        "category": "APPLICATION",
        "subcategory": "Internal tool",
    },
    {
        "subject": "Internal application error",
        "description": "An error appears in one of our internally developed applications.",
        "category": "APPLICATION",
        "subcategory": "Internal tool",
    },
    {
        "subject": "Company internal system problem",
        "description": "The internal system used by our department is not behaving correctly.",
        "category": "APPLICATION",
        "subcategory": "Internal tool",
    },
    {
        "subject": "Internal application stopped working",
        "description": "The internal company application has stopped working during normal use.",
        "category": "APPLICATION",
        "subcategory": "Internal tool",
    },
    {
        "subject": "Internal service interface problem",
        "description": "The user interface for an internal company service is not working correctly.",
        "category": "APPLICATION",
        "subcategory": "Internal tool",
    },
    {
        "subject": "Department internal tool failure",
        "description": "The internal tool used by our department is failing during normal operation.",
        "category": "APPLICATION",
        "subcategory": "Internal tool",
    },
    {
        "subject": "Internal tool processing issue",
        "description": "The internal application does not complete the requested operation.",
        "category": "APPLICATION",
        "subcategory": "Internal tool",
    },
    {
        "subject": "Internal company software problem",
        "description": "A company-specific internal application is experiencing a problem.",
        "category": "APPLICATION",
        "subcategory": "Internal tool",
    },
    {
        "subject": "Internal application malfunction",
        "description": "An internally developed business application is malfunctioning.",
        "category": "APPLICATION",
        "subcategory": "Internal tool",
    },

    # -------------------------------------------------
    # INTEGRATION FAILURE
    # -------------------------------------------------

    {
        "subject": "System integration failure",
        "description": "Data is not transferring correctly between two connected company systems.",
        "category": "APPLICATION",
        "subcategory": "Integration failure",
    },
    {
        "subject": "Application integration not working",
        "description": "The integration between our business applications is failing.",
        "category": "APPLICATION",
        "subcategory": "Integration failure",
    },
    {
        "subject": "Data synchronization failure",
        "description": "A connected system is not receiving data from the source application.",
        "category": "APPLICATION",
        "subcategory": "Integration failure",
    },
    {
        "subject": "ERP CRM integration problem",
        "description": "Data is not syncing correctly between the ERP and CRM systems.",
        "category": "APPLICATION",
        "subcategory": "Integration failure",
    },
    {
        "subject": "Application data interface failure",
        "description": "The interface between two company applications is not transferring data.",
        "category": "APPLICATION",
        "subcategory": "Integration failure",
    },
    {
        "subject": "System connection between applications failed",
        "description": "A configured connection between two business applications has stopped working.",
        "category": "APPLICATION",
        "subcategory": "Integration failure",
    },
    {
        "subject": "Integration stopped processing",
        "description": "The integration service is no longer processing data between connected applications.",
        "category": "APPLICATION",
        "subcategory": "Integration failure",
    },
    {
        "subject": "Application synchronization problem",
        "description": "Two integrated systems are no longer synchronizing information correctly.",
        "category": "APPLICATION",
        "subcategory": "Integration failure",
    },
    {
        "subject": "Business system integration error",
        "description": "An integration error is preventing two business systems from exchanging information.",
        "category": "APPLICATION",
        "subcategory": "Integration failure",
    },
    {
        "subject": "Integration data transfer issue",
        "description": "Data transfers between connected applications are failing.",
        "category": "APPLICATION",
        "subcategory": "Integration failure",
    },
    {
        "subject": "Connected application failure",
        "description": "A connected application is not receiving the information sent by another system.",
        "category": "APPLICATION",
        "subcategory": "Integration failure",
    },
    {
        "subject": "System interface integration problem",
        "description": "The interface between two internal systems is generating errors.",
        "category": "APPLICATION",
        "subcategory": "Integration failure",
    },
    {
        "subject": "API integration failure",
        "description": "An application integration is failing when one system calls the connected service.",
        "category": "APPLICATION",
        "subcategory": "Integration failure",
    },
    {
        "subject": "Application integration error",
        "description": "An error is preventing two business applications from communicating.",
        "category": "APPLICATION",
        "subcategory": "Integration failure",
    },
    {
        "subject": "Data exchange failure",
        "description": "Connected applications are unable to exchange required business data.",
        "category": "APPLICATION",
        "subcategory": "Integration failure",
    },
    {
        "subject": "Integration pipeline stopped",
        "description": "The process that transfers data between company systems has stopped.",
        "category": "APPLICATION",
        "subcategory": "Integration failure",
    },
    {
        "subject": "Application connector problem",
        "description": "The configured connector between two internal systems is failing.",
        "category": "APPLICATION",
        "subcategory": "Integration failure",
    },
    {
        "subject": "Cross-system synchronization failure",
        "description": "Information is not synchronizing correctly between two connected business applications.",
        "category": "APPLICATION",
        "subcategory": "Integration failure",
    },
]


def load_json(path):
    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def main():
    data = load_json(SOURCE_PATH)

    existing = data["tickets"]

    print(
        "Existing tickets:",
        len(existing),
    )

    print(
        "New APPLICATION examples:",
        len(APPLICATION_EXAMPLES),
    )

    if len(APPLICATION_EXAMPLES) != 72:
        raise ValueError(
            "Expected exactly 72 APPLICATION examples."
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
        for example in APPLICATION_EXAMPLES
        if (
            example["subject"].strip().lower(),
            example["description"].strip().lower(),
        ) in existing_keys
    ]

    if duplicate_examples:
        raise ValueError(
            "Duplicate APPLICATION examples found."
        )

    new_tickets = (
        existing + APPLICATION_EXAMPLES
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
        "\nAPPLICATION EXPANSION COMPLETE"
    )

    print(
        "Total tickets:",
        len(new_tickets),
    )

    print(
        "APPLICATION total:",
        sum(
            ticket["category"] == "APPLICATION"
            for ticket in new_tickets
        ),
    )

    print(
        "Output:",
        OUTPUT_PATH,
    )

    print(
        "\nOriginal SECURITY-expanded dataset "
        "was NOT modified."
    )


if __name__ == "__main__":
    main()