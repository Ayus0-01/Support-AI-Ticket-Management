from pathlib import Path
from tempfile import TemporaryDirectory

from apps.knowledge_base.loaders import (
    load_document,
)


def main():
    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)

        markdown = root / "vpn.md"

        markdown.write_text(
            "# VPN Troubleshooting\n\n"
            "## Timeout Errors\n\n"
            "Verify network connectivity.\n\n"
            "### Client Configuration\n\n"
            "Verify VPN configuration.",
            encoding="utf-8",
        )

        result = load_document(
            markdown,
            source_url="https://example.com/vpn",
        )

        assert (
            result["title"]
            == "VPN Troubleshooting"
        )

        assert len(
            result["headings"]
        ) == 3

        assert result[
            "headings"
        ][1]["level"] == 2

        assert (
            "Verify network connectivity."
            in result["text"]
        )

        assert (
            result["source_url"]
            == "https://example.com/vpn"
        )

        print(
            "MARKDOWN LOADER: PASS"
        )


if __name__ == "__main__":
    main()