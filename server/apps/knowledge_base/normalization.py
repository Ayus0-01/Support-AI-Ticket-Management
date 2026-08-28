import re


def normalize_whitespace(
    text,
):
    if not text:
        return ""

    text = text.replace(
        "\r\n",
        "\n",
    )

    text = text.replace(
        "\r",
        "\n",
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    lines = [
        line.strip()
        for line in text.splitlines()
    ]

    return "\n".join(
        lines
    ).strip()


def normalize_tables(
    text,
):
    """
    Convert simple Markdown-style tables
    into labelled readable lines.
    """

    if not text:
        return ""

    lines = text.splitlines()
    output = []

    index = 0

    while index < len(lines):
        line = lines[index].strip()

        # Detect a markdown table header.
        if (
            "|" in line
            and index + 1 < len(lines)
            and re.match(
                r"^\s*\|?\s*:?-{3,}",
                lines[index + 1],
            )
        ):
            headers = [
                cell.strip()
                for cell in line.strip("|").split("|")
            ]

            index += 2

            while index < len(lines):
                row = lines[index].strip()

                if "|" not in row:
                    break

                values = [
                    cell.strip()
                    for cell in row.strip("|").split("|")
                ]

                fields = []

                for position, value in enumerate(
                    values
                ):
                    if position < len(headers):
                        fields.append(
                            f"{headers[position]}: {value}"
                        )
                    elif value:
                        fields.append(value)

                if fields:
                    output.append(
                        "Table row — "
                        + "; ".join(fields)
                    )

                index += 1

            continue

        output.append(line)
        index += 1

    return "\n".join(output)


def normalize_document(
    document,
):
    """
    Normalize a loader result while preserving
    heading markers and readable structure.

    Expected document keys:
        text
        title
        headings
        source_url
        source_updated_at
        source_path
    """

    text = normalize_whitespace(
        document.get(
            "text",
            "",
        )
    )

    text = normalize_tables(
        text
    )

    return {
        **document,
        "text": text,
        "title": (
            document.get(
                "title",
                "",
            )
            or ""
        ).strip(),
    }