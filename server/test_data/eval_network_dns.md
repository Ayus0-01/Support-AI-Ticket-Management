# DNS Troubleshooting

## Symptoms

Use this guide when network connectivity is available but corporate hostnames or approved services cannot be resolved.

## Confirm Basic Network Connectivity

Verify that the device has an active network connection.

Test an approved resource to determine whether the problem is specifically related to hostname resolution.

## Test the Affected Hostname

Record the exact corporate hostname that does not resolve.

Capture the DNS or name-resolution error shown by the operating system or approved diagnostic tool.

## Check Approved DNS Configuration

Verify that the device is using the organization's approved DNS configuration.

Do not replace corporate DNS settings with unapproved values.

## Retry Name Resolution

After correcting an approved DNS configuration issue, retry access to the affected corporate hostname.

## Compare With Another Approved Hostname

When appropriate, test another approved corporate hostname to determine whether the problem affects one name or broader DNS resolution.

## Determine the Scope

Check whether the DNS problem affects only the current device or multiple users or devices.

## Record Useful Information

Record:

- Device identifier when available
- Affected hostname
- DNS configuration
- Exact resolution error
- Whether normal IP connectivity works
- Whether other devices are affected

## Escalation

Escalate when approved DNS configuration appears correct but hostname resolution continues to fail.

Include the affected hostname, exact error, DNS configuration, device, and scope of the problem.