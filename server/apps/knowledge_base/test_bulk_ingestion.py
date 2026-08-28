from pathlib import Path
from tempfile import TemporaryDirectory

from apps.knowledge_base.ingestion import ingest_documents


def main():
    with TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)

        good_1 = temp / "vpn_guide_1.md"
        good_2 = temp / "vpn_guide_2.md"
        bad = temp / "broken.xyz"

        good_1.write_text(
            """
# VPN Guide One

## Timeout Errors

When a VPN connection times out, first verify that the device has
working network connectivity and that normal web access is available.
Confirm that the VPN client is connected to the correct company server
and that the configured gateway is reachable from the current network.

Check whether the organization firewall permits the required VPN
traffic and verify that the authentication settings are correct.
Confirm that the client is using the approved VPN protocol and that
the user account has not expired or been locked.

Clear stale cached credentials when appropriate, restart the VPN
client, and attempt the connection again. Record the exact timeout
message if the problem continues so that support can determine whether
the failure occurs before authentication or after the tunnel starts.

## Escalation

If the documented troubleshooting steps do not resolve the timeout,
collect the client logs, connection details, affected server name, and
the approximate time of failure. Escalate the issue to the appropriate
support team with those details so that the network and VPN systems can
be investigated together.
""".strip(),
            encoding="utf-8",
        )

        good_2.write_text(
            """
# VPN Guide Two

## Client Configuration

Verify the VPN client server address, protocol configuration,
authentication settings, certificates, and any required gateway
parameters. The configured server must match the approved corporate
VPN endpoint used by the organization.

Check whether the client is using the correct authentication method
and confirm that all required certificates are present and valid.
If credentials are cached locally, clear stale cached credentials
before retrying the connection.

Restart the VPN client after correcting configuration values and test
connectivity again. Confirm that the connection establishes normally
and that the user can reach the expected internal resources.

## Escalation

If configuration is correct and the VPN connection still fails,
collect the client logs, screenshots of the connection settings,
the server address being used, and the exact error message. Escalate
the case with that evidence so the support team can determine whether
the problem is client-side, network-side, or server-side.
""".strip(),
            encoding="utf-8",
        )

        bad.write_text(
            "This file has an unsupported extension.",
            encoding="utf-8",
        )

        result = ingest_documents(
            paths=[
                good_1,
                bad,
                good_2,
            ],
            source_ref="TEST-M2-BULK",
            triggered_by_name="Bulk Test",
            source_metadata={
                "category": "VPN",
                "sub_category": "Connection failure",
                "source_system": "TEST",
                "tags": [
                    "vpn",
                    "bulk-test",
                ],
            },
        )

        print(
            "JOB RESULT:",
            {
                "status": result["status"],
                "progress": result["progress"],
                "error_count": len(
                    result["errors"]
                ),
            },
        )

        print(
            "ERRORS:",
            result["errors"],
        )

        print(
            "SUCCESSFUL DOCUMENTS:",
            len(result["results"]),
        )

        assert (
            result["progress"]["total_documents"]
            == 3
        )

        assert (
            result["progress"]["processed"]
            == 2
        )

        assert (
            result["progress"]["failed"]
            == 1
        )

        assert len(
            result["errors"]
        ) == 1

        assert len(
            result["results"]
        ) == 2

        assert result["status"] == (
            "COMPLETED_WITH_ERRORS"
        )

        created_titles = [
            item["title"]
            for item in result["results"]
        ]

        assert (
            "VPN Guide One"
            in created_titles
        )

        assert (
            "VPN Guide Two"
            in created_titles
        )

        print(
            "BULK FAILURE ISOLATION: PASS"
        )


if __name__ == "__main__":
    main()