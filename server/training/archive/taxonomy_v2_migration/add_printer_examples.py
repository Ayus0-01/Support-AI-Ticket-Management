import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

SOURCE_PATH = (
    BASE_DIR / "category_seed_data_application_expanded.json"
)

OUTPUT_PATH = (
    BASE_DIR / "category_seed_data_printer_expanded.json"
)


PRINTER_EXAMPLES = [
    # -------------------------------------------------
    # NOT PRINTING
    # -------------------------------------------------

    {
        "subject": "Printer not printing",
        "description": "The office printer is not printing documents I send to it.",
        "category": "PRINTER",
        "subcategory": "Not printing",
    },
    {
        "subject": "Cannot print from workstation",
        "description": "My computer sends the document but the printer does not print it.",
        "category": "PRINTER",
        "subcategory": "Not printing",
    },
    {
        "subject": "Office printer stopped printing",
        "description": "The company printer has stopped producing printed documents.",
        "category": "PRINTER",
        "subcategory": "Not printing",
    },
    {
        "subject": "Printer not responding to print jobs",
        "description": "The printer receives the job but does not print anything.",
        "category": "PRINTER",
        "subcategory": "Not printing",
    },
    {
        "subject": "Unable to print document",
        "description": "I cannot print a document to the office printer.",
        "category": "PRINTER",
        "subcategory": "Not printing",
    },
    {
        "subject": "Printer does not produce output",
        "description": "Print jobs are sent successfully but no paper is produced.",
        "category": "PRINTER",
        "subcategory": "Not printing",
    },
    {
        "subject": "Work printer not printing",
        "description": "The printer at my workstation is not printing any files.",
        "category": "PRINTER",
        "subcategory": "Not printing",
    },
    {
        "subject": "Print command does nothing",
        "description": "Selecting print does not result in any printed output.",
        "category": "PRINTER",
        "subcategory": "Not printing",
    },
    {
        "subject": "Printer output missing",
        "description": "Documents sent to the company printer are not being printed.",
        "category": "PRINTER",
        "subcategory": "Not printing",
    },
    {
        "subject": "Cannot print to office printer",
        "description": "My workstation is unable to produce a printed document using the office printer.",
        "category": "PRINTER",
        "subcategory": "Not printing",
    },
    {
        "subject": "Printer job not producing pages",
        "description": "The printer accepts jobs but no pages come out.",
        "category": "PRINTER",
        "subcategory": "Not printing",
    },
    {
        "subject": "Company printer unavailable for printing",
        "description": "The office printer is available but will not print my documents.",
        "category": "PRINTER",
        "subcategory": "Not printing",
    },
    {
        "subject": "Printer not producing documents",
        "description": "My print request completes but the printer produces nothing.",
        "category": "PRINTER",
        "subcategory": "Not printing",
    },
    {
        "subject": "Document will not print",
        "description": "A document refuses to print through the assigned office printer.",
        "category": "PRINTER",
        "subcategory": "Not printing",
    },
    {
        "subject": "Office print failure",
        "description": "Printing from my work computer is failing.",
        "category": "PRINTER",
        "subcategory": "Not printing",
    },
    {
        "subject": "Printer stopped responding",
        "description": "The office printer has stopped responding to print requests.",
        "category": "PRINTER",
        "subcategory": "Not printing",
    },
    {
        "subject": "Print job sent but nothing prints",
        "description": "The document is sent to the printer but no printed output appears.",
        "category": "PRINTER",
        "subcategory": "Not printing",
    },
    {
        "subject": "Workstation printing problem",
        "description": "I cannot get documents to print from my company workstation.",
        "category": "PRINTER",
        "subcategory": "Not printing",
    },

    # -------------------------------------------------
    # DRIVER
    # -------------------------------------------------

    {
        "subject": "Printer driver missing",
        "description": "The required printer driver is not installed on my workstation.",
        "category": "PRINTER",
        "subcategory": "Driver",
    },
    {
        "subject": "Printer driver error",
        "description": "The printer driver reports an error when I try to print.",
        "category": "PRINTER",
        "subcategory": "Driver",
    },
    {
        "subject": "Install printer driver",
        "description": "I need the approved driver installed for the office printer.",
        "category": "PRINTER",
        "subcategory": "Driver",
    },
    {
        "subject": "Printer driver not recognized",
        "description": "My computer does not recognize the installed printer driver.",
        "category": "PRINTER",
        "subcategory": "Driver",
    },
    {
        "subject": "Printer driver installation failure",
        "description": "The printer driver installation fails on my workstation.",
        "category": "PRINTER",
        "subcategory": "Driver",
    },
    {
        "subject": "Wrong printer driver",
        "description": "The installed driver does not match the company printer model.",
        "category": "PRINTER",
        "subcategory": "Driver",
    },
    {
        "subject": "Update printer driver",
        "description": "The printer requires an updated driver on my company computer.",
        "category": "PRINTER",
        "subcategory": "Driver",
    },
    {
        "subject": "Printer driver unavailable",
        "description": "The required driver for the office printer cannot be found on my system.",
        "category": "PRINTER",
        "subcategory": "Driver",
    },
    {
        "subject": "Driver prevents printing",
        "description": "A printer driver problem is preventing documents from being printed.",
        "category": "PRINTER",
        "subcategory": "Driver",
    },
    {
        "subject": "Printer software driver issue",
        "description": "The printer driver on my workstation is malfunctioning.",
        "category": "PRINTER",
        "subcategory": "Driver",
    },
    {
        "subject": "Printer driver compatibility problem",
        "description": "The installed driver is not working correctly with the office printer.",
        "category": "PRINTER",
        "subcategory": "Driver",
    },
    {
        "subject": "Printer driver setup problem",
        "description": "I am unable to complete the printer driver setup.",
        "category": "PRINTER",
        "subcategory": "Driver",
    },
    {
        "subject": "Printer driver keeps failing",
        "description": "The printer driver repeatedly fails when I send a print job.",
        "category": "PRINTER",
        "subcategory": "Driver",
    },
    {
        "subject": "Corporate printer driver request",
        "description": "Please install the correct company printer driver on my workstation.",
        "category": "PRINTER",
        "subcategory": "Driver",
    },
    {
        "subject": "Printer driver not working",
        "description": "The installed printer driver is preventing normal printing.",
        "category": "PRINTER",
        "subcategory": "Driver",
    },
    {
        "subject": "Printer driver configuration issue",
        "description": "The printer driver settings are not working correctly.",
        "category": "PRINTER",
        "subcategory": "Driver",
    },
    {
        "subject": "Printer driver needs reinstall",
        "description": "The printer driver needs to be reinstalled on my work computer.",
        "category": "PRINTER",
        "subcategory": "Driver",
    },
    {
        "subject": "Printer driver update failure",
        "description": "Updating the office printer driver fails on my workstation.",
        "category": "PRINTER",
        "subcategory": "Driver",
    },

    # -------------------------------------------------
    # QUEUE STUCK
    # -------------------------------------------------

    {
        "subject": "Printer queue stuck",
        "description": "A document is stuck in the printer queue and will not print.",
        "category": "PRINTER",
        "subcategory": "Queue stuck",
    },
    {
        "subject": "Print job stuck in queue",
        "description": "My print job remains queued and never reaches the printer.",
        "category": "PRINTER",
        "subcategory": "Queue stuck",
    },
    {
        "subject": "Printer queue not clearing",
        "description": "The print queue is not clearing after I cancel the job.",
        "category": "PRINTER",
        "subcategory": "Queue stuck",
    },
    {
        "subject": "Multiple jobs stuck in printer queue",
        "description": "Several print jobs are stuck in the office printer queue.",
        "category": "PRINTER",
        "subcategory": "Queue stuck",
    },
    {
        "subject": "Cannot remove queued print job",
        "description": "A print job is stuck and cannot be removed from the queue.",
        "category": "PRINTER",
        "subcategory": "Queue stuck",
    },
    {
        "subject": "Printer queue frozen",
        "description": "The printer queue appears frozen and new jobs cannot process.",
        "category": "PRINTER",
        "subcategory": "Queue stuck",
    },
    {
        "subject": "Print jobs waiting indefinitely",
        "description": "Documents remain in the printer queue without being processed.",
        "category": "PRINTER",
        "subcategory": "Queue stuck",
    },
    {
        "subject": "Printer spool queue stuck",
        "description": "The print queue is stuck in a waiting state.",
        "category": "PRINTER",
        "subcategory": "Queue stuck",
    },
    {
        "subject": "Queued document will not print",
        "description": "A document remains in the printer queue and does not print.",
        "category": "PRINTER",
        "subcategory": "Queue stuck",
    },
    {
        "subject": "Printer jobs cannot leave queue",
        "description": "Print jobs are accumulating in the queue and are not being processed.",
        "category": "PRINTER",
        "subcategory": "Queue stuck",
    },
    {
        "subject": "Office printer queue blocked",
        "description": "The printer queue is blocked by a stuck print job.",
        "category": "PRINTER",
        "subcategory": "Queue stuck",
    },
    {
        "subject": "Print queue remains pending",
        "description": "My print request stays pending in the queue indefinitely.",
        "category": "PRINTER",
        "subcategory": "Queue stuck",
    },
    {
        "subject": "Printer spooler queue issue",
        "description": "Jobs are stuck in the printer queue and the spooler is not processing them.",
        "category": "PRINTER",
        "subcategory": "Queue stuck",
    },
    {
        "subject": "Queue full of stuck jobs",
        "description": "The printer queue contains several jobs that cannot complete.",
        "category": "PRINTER",
        "subcategory": "Queue stuck",
    },
    {
        "subject": "Cannot clear printer queue",
        "description": "I cannot clear the queue because a print job remains stuck.",
        "category": "PRINTER",
        "subcategory": "Queue stuck",
    },
    {
        "subject": "Print request stuck",
        "description": "The print request remains in the queue without being processed.",
        "category": "PRINTER",
        "subcategory": "Queue stuck",
    },
    {
        "subject": "Queued print document frozen",
        "description": "A document is frozen in the printer queue and cannot be completed.",
        "category": "PRINTER",
        "subcategory": "Queue stuck",
    },
    {
        "subject": "Printer queue processing failure",
        "description": "Jobs remain in the printer queue and are not moving forward.",
        "category": "PRINTER",
        "subcategory": "Queue stuck",
    },

    # -------------------------------------------------
    # QUALITY
    # -------------------------------------------------

    {
        "subject": "Printer output quality is poor",
        "description": "Printed documents have poor quality and are difficult to read.",
        "category": "PRINTER",
        "subcategory": "Quality",
    },
    {
        "subject": "Printer produces faded pages",
        "description": "The office printer is producing very faint printed documents.",
        "category": "PRINTER",
        "subcategory": "Quality",
    },
    {
        "subject": "Printer prints streaks",
        "description": "Printed pages contain repeated streaks and lines.",
        "category": "PRINTER",
        "subcategory": "Quality",
    },
    {
        "subject": "Print quality problem",
        "description": "The quality of documents printed from the company printer has deteriorated.",
        "category": "PRINTER",
        "subcategory": "Quality",
    },
    {
        "subject": "Printer output has smudges",
        "description": "Documents printed by the office printer have visible smudges.",
        "category": "PRINTER",
        "subcategory": "Quality",
    },
    {
        "subject": "Uneven printer printing",
        "description": "The printer produces pages with uneven or inconsistent print quality.",
        "category": "PRINTER",
        "subcategory": "Quality",
    },
    {
        "subject": "Printer pages are blurry",
        "description": "Printed text and images are coming out blurry.",
        "category": "PRINTER",
        "subcategory": "Quality",
    },
    {
        "subject": "Printer has poor image quality",
        "description": "Images printed by the office printer are distorted or low quality.",
        "category": "PRINTER",
        "subcategory": "Quality",
    },
    {
        "subject": "Lines appearing on printed pages",
        "description": "Printed pages contain unwanted horizontal or vertical lines.",
        "category": "PRINTER",
        "subcategory": "Quality",
    },
    {
        "subject": "Printouts have missing areas",
        "description": "Parts of the printed document are missing or too faint.",
        "category": "PRINTER",
        "subcategory": "Quality",
    },
    {
        "subject": "Printer color quality issue",
        "description": "Color documents are not being printed with the expected quality.",
        "category": "PRINTER",
        "subcategory": "Quality",
    },
    {
        "subject": "Poor print resolution",
        "description": "The office printer is producing documents with poor print resolution.",
        "category": "PRINTER",
        "subcategory": "Quality",
    },
    {
        "subject": "Printer leaves marks on paper",
        "description": "Printed pages contain unwanted marks and defects.",
        "category": "PRINTER",
        "subcategory": "Quality",
    },
    {
        "subject": "Printer output is too light",
        "description": "The printed documents are much lighter than expected.",
        "category": "PRINTER",
        "subcategory": "Quality",
    },
    {
        "subject": "Printer prints distorted text",
        "description": "Text printed by the company printer appears distorted.",
        "category": "PRINTER",
        "subcategory": "Quality",
    },
    {
        "subject": "Print quality deteriorated",
        "description": "The printer has recently started producing lower quality documents.",
        "category": "PRINTER",
        "subcategory": "Quality",
    },
    {
        "subject": "Printer pages have streaks and fading",
        "description": "Printed documents contain streaks and areas with very faint ink or toner.",
        "category": "PRINTER",
        "subcategory": "Quality",
    },
    {
        "subject": "Unreadable printer output",
        "description": "The output from the office printer is difficult to read because of poor print quality.",
        "category": "PRINTER",
        "subcategory": "Quality",
    },

    # -------------------------------------------------
    # SCAN
    # -------------------------------------------------

    {
        "subject": "Printer scanner not working",
        "description": "The scanner on the office printer is not working.",
        "category": "PRINTER",
        "subcategory": "Scan",
    },
    {
        "subject": "Cannot scan documents",
        "description": "I cannot scan a document using the multifunction printer.",
        "category": "PRINTER",
        "subcategory": "Scan",
    },
    {
        "subject": "Printer scan failure",
        "description": "Scanning a document from the office printer fails.",
        "category": "PRINTER",
        "subcategory": "Scan",
    },
    {
        "subject": "Scanner not detected",
        "description": "My computer cannot detect the scanner built into the office printer.",
        "category": "PRINTER",
        "subcategory": "Scan",
    },
    {
        "subject": "Scanned document not created",
        "description": "The printer scanner does not create a digital copy of the document.",
        "category": "PRINTER",
        "subcategory": "Scan",
    },
    {
        "subject": "Multifunction printer scan issue",
        "description": "The scanning function on the office multifunction printer is not working.",
        "category": "PRINTER",
        "subcategory": "Scan",
    },
    {
        "subject": "Cannot scan to computer",
        "description": "I cannot scan documents from the printer to my workstation.",
        "category": "PRINTER",
        "subcategory": "Scan",
    },
    {
        "subject": "Printer scanner error",
        "description": "An error appears whenever I try to scan a document.",
        "category": "PRINTER",
        "subcategory": "Scan",
    },
    {
        "subject": "Scan function unavailable",
        "description": "The scan function on the company printer is unavailable.",
        "category": "PRINTER",
        "subcategory": "Scan",
    },
    {
        "subject": "Document scanning problem",
        "description": "The office printer cannot scan the documents I place on it.",
        "category": "PRINTER",
        "subcategory": "Scan",
    },
    {
        "subject": "Printer scan to email not working",
        "description": "The printer cannot scan a document and send it to the configured email destination.",
        "category": "PRINTER",
        "subcategory": "Scan",
    },
    {
        "subject": "Scan job fails at printer",
        "description": "Scanning from the multifunction printer fails before the document is created.",
        "category": "PRINTER",
        "subcategory": "Scan",
    },
    {
        "subject": "Scanner function stopped working",
        "description": "The scanning function of the office printer has stopped working.",
        "category": "PRINTER",
        "subcategory": "Scan",
    },
    {
        "subject": "Cannot use printer scanner",
        "description": "I am unable to use the scanner attached to the office printer.",
        "category": "PRINTER",
        "subcategory": "Scan",
    },
    {
        "subject": "Printer scan connection problem",
        "description": "The printer scanner cannot communicate with my workstation.",
        "category": "PRINTER",
        "subcategory": "Scan",
    },
    {
        "subject": "Scanning documents fails",
        "description": "Every attempt to scan a document from the office printer fails.",
        "category": "PRINTER",
        "subcategory": "Scan",
    },
    {
        "subject": "Multifunction printer scanning issue",
        "description": "The scanning capability of the multifunction printer is not functioning correctly.",
        "category": "PRINTER",
        "subcategory": "Scan",
    },
    {
        "subject": "Printer scan error",
        "description": "The printer displays an error when I try to scan a document.",
        "category": "PRINTER",
        "subcategory": "Scan",
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
        "New PRINTER examples:",
        len(PRINTER_EXAMPLES),
    )

    if len(PRINTER_EXAMPLES) != 90:
        raise ValueError(
            "Expected exactly 90 PRINTER examples."
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
        for example in PRINTER_EXAMPLES
        if (
            example["subject"].strip().lower(),
            example["description"].strip().lower(),
        ) in existing_keys
    ]

    if duplicate_examples:
        raise ValueError(
            "Duplicate PRINTER examples found."
        )

    new_tickets = (
        existing + PRINTER_EXAMPLES
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
        "\nPRINTER EXPANSION COMPLETE"
    )

    print(
        "Total tickets:",
        len(new_tickets),
    )

    print(
        "PRINTER total:",
        sum(
            ticket["category"] == "PRINTER"
            for ticket in new_tickets
        ),
    )

    print(
        "Output:",
        OUTPUT_PATH,
    )

    print(
        "\nOriginal APPLICATION-expanded dataset "
        "was NOT modified."
    )


if __name__ == "__main__":
    main()