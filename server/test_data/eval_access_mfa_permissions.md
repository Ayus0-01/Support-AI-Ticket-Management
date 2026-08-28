# MFA and Access Permission Troubleshooting

## Overview

This article provides troubleshooting guidance for company accounts that are unable to complete multi-factor authentication.

Use this guidance when the user can reach the authentication stage but cannot complete the required MFA verification.

## Symptoms

Common symptoms include:

- MFA verification fails
- A verification code is rejected
- The MFA challenge does not complete
- The registered MFA device is not accepted
- The user can enter credentials but cannot complete MFA
- Repeated MFA prompts prevent successful sign-in

## Troubleshooting Steps

### 1. Confirm the authentication stage

Determine whether the user's primary corporate credentials are accepted and whether the failure occurs specifically during MFA verification.

Do not treat a general password failure as an MFA issue.

### 2. Confirm the intended MFA method

Verify that the user is attempting MFA with the approved registered authentication method.

If multiple authentication methods are available, confirm that the expected method is being used.

### 3. Retry the MFA challenge

Retry the authentication challenge using the approved MFA method.

If a verification code is required, use the current code rather than a previously generated or expired code.

### 4. Check the registered MFA device

Confirm that the expected registered device or authentication method is available to the user.

If the registered method is unavailable, follow the organization's approved MFA recovery process.

### 5. Re-authenticate

Sign out of the affected application or authentication session and start a fresh sign-in attempt.

Complete the MFA challenge again.

### 6. Avoid repeated failed attempts

Do not repeatedly submit unsuccessful MFA challenges.

Repeated failures may trigger additional account protection controls.

### 7. Escalate MFA registration or recovery issues

Escalate to the appropriate access-management or identity-support team when:

- The registered MFA method is unavailable
- The MFA device needs to be replaced
- MFA registration is incorrect
- The user cannot complete the approved MFA recovery process
- MFA continues to fail after normal user-level troubleshooting

## Important Safety Notes

Do not bypass MFA.

Do not disable authentication controls.

Do not instruct users to weaken or circumvent organizational security requirements.

Do not register an unauthorized authentication method.

## Resolution Outcome

The expected outcome is successful completion of MFA using the user's approved registered authentication method.

## Escalation

Escalation is recommended when MFA registration, recovery, or administrative identity changes are required.