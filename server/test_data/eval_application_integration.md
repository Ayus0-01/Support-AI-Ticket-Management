# Application Integration Failure Troubleshooting

## Overview

This article provides troubleshooting guidance for failures involving communication or data exchange between approved business applications or services.

## Symptoms

Common symptoms include:

- Data does not transfer between connected systems
- An integration reports an error
- A synchronization process fails
- One system does not receive expected information from another
- A connected workflow stops during data exchange

## Troubleshooting Steps

### 1. Identify the connected systems

Record the source application, destination application, and affected integration or workflow.

### 2. Capture the error

Record the exact integration or synchronization error message.

### 3. Determine when the failure occurs

Identify whether the failure happens during submission, synchronization, data transfer, or another integration stage.

### 4. Check whether the failure is repeatable

Retry the affected workflow when doing so is safe and does not create duplicate transactions.

### 5. Determine the scope

Identify whether one user, one workflow, or multiple users are affected.

### 6. Record the business impact

Document which business process cannot continue because the integration is failing.

### 7. Escalate integration failures

Escalate when the integration remains unavailable or requires service-level, configuration, or application-owner investigation.

## Important Safety Notes

Do not repeatedly submit transactions when duplicate records could be created.

Do not modify integration credentials, endpoints, or production configuration without authorization.

## Resolution Outcome

The expected outcome is restoration of the affected data exchange or escalation to the appropriate integration-support team.

## Escalation

Escalate persistent integration failures with the affected systems, workflow, error message, and business impact documented.