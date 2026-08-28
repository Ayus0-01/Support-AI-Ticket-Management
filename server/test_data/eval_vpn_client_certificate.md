# VPN Client, Certificate and Authentication Troubleshooting

## Symptoms

Use this guide when the VPN client is installed but authentication
fails, a required certificate is rejected, or the client reports
a certificate-related problem.

## Verify the VPN Client

Confirm that the approved VPN client is installed and that the
installed version is supported by the organization.

Record the client version when available.

## Check the Authentication Method

Confirm that the user is attempting authentication through the
organization's approved sign-in method.

Record the exact authentication error before retrying.

## Check Certificate Status

If the client reports a certificate problem, record the certificate
error and determine whether the certificate is expired, missing,
or rejected by the approved VPN service.

Do not install an unknown certificate or bypass certificate
validation.

## Check Client Configuration

Verify that the VPN client is configured with the approved gateway
and authentication settings.

Do not change undocumented security settings.

## Retry Authentication

Close and reopen the approved VPN client.

Retry authentication after confirming the certificate and client
configuration.

## Escalation

Escalate when the certificate remains invalid, required credentials
cannot be verified, or authentication fails after the documented
client and certificate checks.

Include the VPN client version, authentication method, exact
certificate or authentication error, configured gateway, and
actions already completed.