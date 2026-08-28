from pathlib import Path
from datetime import datetime, timezone

from bs4 import BeautifulSoup
from docx import Document
from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {
    ".md",
    ".markdown",
    ".html",
    ".htm",
    ".docx",
    ".pdf",
}


def _utc_now():
    return datetime.now(
        timezone.utc
    )


def _base_result(
    *,
    path,
    text,
    title="",
    headings=None,
    source_url=None,
    source_updated_at=None,
):
    file_path = Path(path)

    return {
        "text": text.strip(),
        "title": (
            title.strip()
            if title
            else file_path.stem
        ),
        "headings": headings or [],
        "source_url": source_url,
        "source_updated_at": (
            source_updated_at
            or _utc_now()
        ),
        "source_path": str(
            file_path
        ),
    }


def load_markdown(
    path,
    *,
    source_url=None,
    source_updated_at=None,
):
    path = Path(path)

    text = path.read_text(
        encoding="utf-8"
    )

    headings = []

    for line in text.splitlines():
        stripped = line.strip()

        if stripped.startswith("#"):
            level = len(
                stripped
            ) - len(
                stripped.lstrip("#")
            )

            heading_text = (
                stripped[level:]
                .strip()
            )

            if heading_text:
                headings.append(
                    {
                        "level": level,
                        "text": heading_text,
                    }
                )

    title = (
        headings[0]["text"]
        if headings
        and headings[0]["level"] == 1
        else path.stem
    )

    return _base_result(
        path=path,
        text=text,
        title=title,
        headings=headings,
        source_url=source_url,
        source_updated_at=source_updated_at,
    )


def load_html(
    path,
    *,
    source_url=None,
    source_updated_at=None,
):
    path = Path(path)

    html = path.read_text(
        encoding="utf-8"
    )

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    for element in soup(
        [
            "script",
            "style",
            "nav",
            "footer",
            "header",
        ]
    ):
        element.decompose()

    headings = []

    for level in range(1, 7):
        for heading in soup.find_all(
            f"h{level}"
        ):
            text = heading.get_text(
                " ",
                strip=True,
            )

            if text:
                headings.append(
                    {
                        "level": level,
                        "text": text,
                    }
                )

    title_tag = soup.find("title")

    title = (
        title_tag.get_text(
            strip=True
        )
        if title_tag
        else path.stem
    )

    text = soup.get_text(
        "\n",
        strip=True,
    )

    return _base_result(
        path=path,
        text=text,
        title=title,
        headings=headings,
        source_url=source_url,
        source_updated_at=source_updated_at,
    )


def load_docx(
    path,
    *,
    source_url=None,
    source_updated_at=None,
):
    path = Path(path)

    document = Document(
        str(path)
    )

    lines = []
    headings = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()

        if not text:
            continue

        style_name = (
            paragraph.style.name
            if paragraph.style
            else ""
        )

        if style_name.startswith(
            "Heading"
        ):
            try:
                level = int(
                    style_name.split(
                        " "
                    )[-1]
                )
            except ValueError:
                level = 1

            headings.append(
                {
                    "level": level,
                    "text": text,
                }
            )

        lines.append(text)

    title = (
        headings[0]["text"]
        if headings
        else path.stem
    )

    return _base_result(
        path=path,
        text="\n".join(lines),
        title=title,
        headings=headings,
        source_url=source_url,
        source_updated_at=source_updated_at,
    )


def load_pdf(
    path,
    *,
    source_url=None,
    source_updated_at=None,
):
    path = Path(path)

    reader = PdfReader(
        str(path)
    )

    pages = []

    for page in reader.pages:
        text = page.extract_text() or ""

        if text.strip():
            pages.append(
                text.strip()
            )

    text = "\n\n".join(
        pages
    )

    return _base_result(
        path=path,
        text=text,
        title=path.stem,
        headings=[],
        source_url=source_url,
        source_updated_at=source_updated_at,
    )


def load_document(
    path,
    *,
    source_url=None,
    source_updated_at=None,
):
    extension = (
        Path(path)
        .suffix
        .lower()
    )

    if extension in {
        ".md",
        ".markdown",
    }:
        return load_markdown(
            path,
            source_url=source_url,
            source_updated_at=source_updated_at,
        )

    if extension in {
        ".html",
        ".htm",
    }:
        return load_html(
            path,
            source_url=source_url,
            source_updated_at=source_updated_at,
        )

    if extension == ".docx":
        return load_docx(
            path,
            source_url=source_url,
            source_updated_at=source_updated_at,
        )

    if extension == ".pdf":
        return load_pdf(
            path,
            source_url=source_url,
            source_updated_at=source_updated_at,
        )

    raise ValueError(
        f"Unsupported document type: {extension}"
    )