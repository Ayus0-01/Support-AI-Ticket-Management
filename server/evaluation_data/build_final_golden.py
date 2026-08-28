from __future__ import annotations

import json
import os
import sys
from collections import Counter
from pathlib import Path


# ============================================================
# PROJECT / DJANGO SETUP
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# Make the server/project root importable when this file is
# executed directly with:
#   python evaluation_data\build_final_golden.py
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "AIticket.settings",
)

import django

django.setup()

from AIticket.db import knowledge_articles_collection


# ============================================================
# OUTPUT
# ============================================================

OUTPUT = BASE_DIR / "evaluation_data" / "retrieval_golden.json"


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
OUTPUT = BASE_DIR / "retrieval_golden.json"


# ============================================================
# FINAL PRODUCTION TAXONOMY
# ============================================================

FINAL_TAXONOMY = {
    "ACCESS": [
        "Password reset",
        "MFA",
        "Permissions",
        "Account lockout",
        "Onboarding",
    ],
    "APPLICATION": [
        "Performance",
        "ERP",
        "CRM",
        "Internal tool",
        "Integration failure",
    ],
    "EMAIL": [
        "Mailbox",
        "Spam",
        "Calendar",
        "Distribution list",
        "Storage quota",
    ],
    "HARDWARE": [
        "Laptop",
        "Peripheral",
        "Desktop",
        "Docking station",
        "Mobile device",
    ],
    "NETWORK": [
        "Connectivity",
        "WiFi",
        "LAN",
        "DNS",
        "Bandwidth",
    ],
    "PRINTER": [
        "Not printing",
        "Driver",
        "Queue stuck",
        "Quality",
        "Scan",
    ],
    "SECURITY": [
        "Phishing report",
        "Suspicious activity",
        "Malware",
        "Data request",
    ],
    "SOFTWARE": [
        "Crash",
        "Licensing",
        "Installation",
        "Update",
        "Compatibility",
    ],
    "VPN": [
        "Timeout",
        "Certificate",
    ],
    "UNCLASSIFIED": [
        "General",
        "Triage",
    ],
}


DEPARTMENTS = [
    "Finance",
    "HR",
    "Operations",
    "Sales",
    "Engineering",
]


# ============================================================
# EXPECTED ARTICLE TITLES
#
# We resolve IDs from Mongo instead of hard-coding Mongo IDs.
# This prevents stale IDs when an article gets replaced.
# ============================================================

ARTICLE_TITLES = {
    "ACCESS/Password reset":
        "Password and Account Recovery",

    "ACCESS/MFA":
        "MFA and Access Permission Troubleshooting",

    "ACCESS/Permissions":
        "Access Permissions Troubleshooting",

    "ACCESS/Account lockout":
        "Account Lockout Troubleshooting",

    "ACCESS/Onboarding":
        "New User Onboarding Access Troubleshooting",

    "APPLICATION/Performance":
        "Application Performance Troubleshooting",

    "APPLICATION/ERP":
        "ERP Application Troubleshooting",

    "APPLICATION/CRM":
        "CRM Application Troubleshooting",

    "APPLICATION/Internal tool":
        "Internal Tool Troubleshooting",

    "APPLICATION/Integration failure":
        "Application Integration Failure Troubleshooting",

    "EMAIL/Mailbox":
        "Email Mailbox Access and Synchronization Troubleshooting",

    "EMAIL/Spam":
        "Email Delivery and Spam Troubleshooting",

    "EMAIL/Calendar":
        "Email Calendar Troubleshooting",

    "EMAIL/Distribution list":
        "Email Distribution List Troubleshooting",

    "EMAIL/Storage quota":
        "Email Storage Quota Troubleshooting",

    "HARDWARE/Laptop":
        "Laptop Hardware Troubleshooting",

    "HARDWARE/Peripheral":
        "Peripheral and Input Device Troubleshooting",

    "HARDWARE/Desktop":
        "Desktop Hardware Troubleshooting",

    "HARDWARE/Docking station":
        "Docking Station Troubleshooting",

    "HARDWARE/Mobile device":
        "Mobile Device Hardware Troubleshooting",

    "NETWORK/Connectivity":
        "Network Connectivity Troubleshooting",

    "NETWORK/WiFi":
        "Wi-Fi Troubleshooting",

    "NETWORK/LAN":
        "LAN Troubleshooting",

    "NETWORK/DNS":
        "DNS Troubleshooting",

    "NETWORK/Bandwidth":
        "Network Bandwidth Troubleshooting",

    "PRINTER/Not printing":
        "Printer Not Printing Troubleshooting",

    "PRINTER/Driver":
        "Printer Driver Troubleshooting",

    "PRINTER/Queue stuck":
        "Printer Printing and Queue Troubleshooting",

    "PRINTER/Quality":
        "Printer Print Quality Troubleshooting",

    "PRINTER/Scan":
        "Printer Scanning Troubleshooting",

    "SECURITY/Phishing report":
        "Phishing Report Troubleshooting",

    "SECURITY/Suspicious activity":
        "Suspicious Activity Troubleshooting",

    "SECURITY/Malware":
        "Malware and Unauthorized Activity Response",

    "SECURITY/Data request":
        "Security Data Request Troubleshooting",

    "SOFTWARE/Crash":
        "Software Crash Troubleshooting",

    "SOFTWARE/Licensing":
        "Software Licensing Troubleshooting",

    "SOFTWARE/Installation":
        "Software Installation and Configuration Troubleshooting",

    "SOFTWARE/Update":
        "Software Update Troubleshooting",

    "SOFTWARE/Compatibility":
        "Software Compatibility Troubleshooting",

    "VPN/Timeout":
        "VPN Connection and Timeout Troubleshooting",

    "VPN/Certificate":
        "VPN Client, Certificate and Authentication Troubleshooting",

    # UNCLASSIFIED / General has TWO published articles.
    "UNCLASSIFIED/General":
        "General and Ambiguous Support Request Troubleshooting",

    "UNCLASSIFIED/Triage":
        "Unclassified Issue Triage",
}


# Special selector for the second UNCLASSIFIED/General article.
UNCLASSIFIED_AUTH_TITLE = (
    "Application Authentication and Login Triage"
)


# ============================================================
# TICKET SPECIFICATION
#
# Each tuple:
#
# (
#     category,
#     subcategory,
#     subject,
#     description,
#     affected_system,
#     severity,
#     already_tried,
#     affected_scope,
#     work_blocked,
#     article_selector
# )
#
# article_selector defaults to category/subcategory.
# ============================================================

TICKETS = [
    # --------------------------------------------------------
    # ACCESS — 10
    # --------------------------------------------------------

    (
        "ACCESS",
        "Password reset",
        "I forgot my company password",
        "I cannot sign in because I forgot the password for my corporate account.",
        "Corporate Account",
        "MEDIUM",
        "Retried the login twice.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "ACCESS",
        "Password reset",
        "My work password needs recovery",
        "My corporate password is no longer known to me and I need the approved recovery process.",
        "Corporate Identity",
        "HIGH",
        "Confirmed the username and retried the login.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "ACCESS",
        "MFA",
        "MFA verification is failing",
        "My password is accepted but the MFA verification step does not complete.",
        "MFA Authentication",
        "HIGH",
        "Requested a new MFA challenge twice.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "ACCESS",
        "MFA",
        "Two-factor authentication is not completing",
        "The company account accepts my password but the required MFA challenge fails.",
        "MFA Authentication",
        "HIGH",
        "Retried the MFA challenge and checked the registered device.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "ACCESS",
        "Permissions",
        "Access denied to an internal resource",
        "I can sign in successfully but my account is not authorized to access a required corporate resource.",
        "Internal Resource",
        "MEDIUM",
        "Signed out and signed back in.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "ACCESS",
        "Permissions",
        "I need access to a restricted application",
        "The application is reachable but my account does not have the required permission.",
        "Corporate Application",
        "MEDIUM",
        "Retried the application after signing in again.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "ACCESS",
        "Account lockout",
        "My corporate account is locked",
        "My work account became locked after repeated unsuccessful sign-in attempts.",
        "Corporate Account",
        "HIGH",
        "Waited and retried the login once.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "ACCESS",
        "Account lockout",
        "Unable to sign in after failed attempts",
        "The corporate account is locked and normal sign-in is no longer accepted.",
        "Corporate Identity",
        "HIGH",
        "Retried the login and confirmed the username.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "ACCESS",
        "Onboarding",
        "New employee cannot access required systems",
        "A newly onboarded employee cannot access the corporate systems needed for work.",
        "Corporate Access",
        "HIGH",
        "Retried sign-in and confirmed the user account exists.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "ACCESS",
        "Onboarding",
        "New starter access is incomplete",
        "A new employee can sign in but cannot access required approved applications.",
        "Corporate Access",
        "MEDIUM",
        "Signed out and signed back in.",
        "JUST_ME",
        "YES",
        None,
    ),

    # --------------------------------------------------------
    # APPLICATION — 10
    # --------------------------------------------------------

    (
        "APPLICATION",
        "Performance",
        "Business application is very slow",
        "The business application takes a long time to respond during normal work.",
        "Business Application",
        "MEDIUM",
        "Closed and reopened the application.",
        "JUST_ME",
        "NO",
        None,
    ),
    (
        "APPLICATION",
        "Performance",
        "Application freezes during use",
        "The approved application becomes unresponsive while performing normal actions.",
        "Business Application",
        "MEDIUM",
        "Restarted the application once.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "APPLICATION",
        "ERP",
        "ERP transaction is failing",
        "A required ERP transaction is failing with an application error.",
        "ERP Application",
        "HIGH",
        "Retried the transaction once.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "APPLICATION",
        "ERP",
        "ERP process does not complete",
        "The ERP application opens but a normal business transaction does not complete.",
        "ERP Application",
        "MEDIUM",
        "Restarted the ERP application.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "APPLICATION",
        "CRM",
        "CRM customer action is failing",
        "A normal customer-record action in the CRM application returns an error.",
        "CRM Application",
        "MEDIUM",
        "Retried the action and reopened the application.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "APPLICATION",
        "CRM",
        "Unable to update a customer in CRM",
        "The CRM application is available but a customer update does not complete.",
        "CRM Application",
        "MEDIUM",
        "Retried the update once.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "APPLICATION",
        "Internal tool",
        "Internal business tool is failing",
        "An approved internal tool returns an unexpected error during normal use.",
        "Internal Business Tool",
        "MEDIUM",
        "Closed and reopened the tool.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "APPLICATION",
        "Internal tool",
        "Company internal tool is not behaving normally",
        "A supported internal tool is available but a routine operation is failing.",
        "Internal Business Tool",
        "MEDIUM",
        "Restarted the tool and repeated the operation.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "APPLICATION",
        "Integration failure",
        "Application data transfer failed",
        "An approved application cannot complete a required data transfer to another service.",
        "Application Integration",
        "HIGH",
        "Retried the transfer once.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "APPLICATION",
        "Integration failure",
        "Application integration is not synchronizing",
        "Data is not moving correctly between the approved applications.",
        "Application Integration",
        "HIGH",
        "Restarted the application and retried the synchronization.",
        "JUST_ME",
        "YES",
        None,
    ),

    # --------------------------------------------------------
    # EMAIL — 10
    # --------------------------------------------------------

    (
        "EMAIL",
        "Mailbox",
        "Mailbox is not synchronizing",
        "Recent messages are not appearing in the approved corporate email client.",
        "Corporate Email",
        "MEDIUM",
        "Restarted the email client.",
        "JUST_ME",
        "NO",
        None,
    ),
    (
        "EMAIL",
        "Mailbox",
        "Cannot open the work mailbox",
        "The corporate mailbox does not open correctly from the approved email client.",
        "Corporate Email",
        "HIGH",
        "Restarted the workstation and retried.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "EMAIL",
        "Spam",
        "Legitimate email is going to junk",
        "Messages from a trusted sender are repeatedly being placed in the spam folder.",
        "Corporate Email",
        "MEDIUM",
        "Moved one message from junk to the inbox.",
        "JUST_ME",
        "NO",
        None,
    ),
    (
        "EMAIL",
        "Spam",
        "Outgoing email is not being delivered",
        "A message sent from the company mailbox returned a delivery failure.",
        "Corporate Email",
        "HIGH",
        "Checked the recipient address and retried.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "EMAIL",
        "Calendar",
        "Corporate calendar is not updating",
        "New calendar events are not appearing in the approved corporate calendar.",
        "Corporate Calendar",
        "MEDIUM",
        "Closed and reopened the email client.",
        "JUST_ME",
        "NO",
        None,
    ),
    (
        "EMAIL",
        "Calendar",
        "Calendar synchronization is failing",
        "Recent calendar changes are not synchronizing correctly.",
        "Corporate Calendar",
        "MEDIUM",
        "Restarted the email application.",
        "JUST_ME",
        "NO",
        None,
    ),
    (
        "EMAIL",
        "Distribution list",
        "Message to distribution list failed",
        "A message sent to an approved distribution list was not delivered successfully.",
        "Corporate Email",
        "MEDIUM",
        "Retried the message once.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "EMAIL",
        "Distribution list",
        "I am not receiving distribution-list mail",
        "Expected messages from an approved distribution list are not arriving.",
        "Corporate Email",
        "MEDIUM",
        "Checked the mailbox and waited for another message.",
        "JUST_ME",
        "NO",
        None,
    ),
    (
        "EMAIL",
        "Storage quota",
        "Mailbox storage quota exceeded",
        "The mailbox reports that storage capacity has been exceeded and new mail is affected.",
        "Corporate Email",
        "HIGH",
        "Reviewed the mailbox for unnecessary large messages.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "EMAIL",
        "Storage quota",
        "Mailbox is almost full",
        "The corporate mailbox is showing repeated storage-quota warnings.",
        "Corporate Email",
        "MEDIUM",
        "Reviewed mailbox usage and large attachments.",
        "JUST_ME",
        "NO",
        None,
    ),

    # --------------------------------------------------------
    # HARDWARE — 10
    # --------------------------------------------------------

    (
        "HARDWARE",
        "Laptop",
        "Company laptop hardware problem",
        "A hardware component of the company laptop is not functioning normally.",
        "Company Laptop",
        "HIGH",
        "Restarted the laptop once.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "HARDWARE",
        "Laptop",
        "Laptop hardware component is failing",
        "A physical component of the corporate laptop appears to be malfunctioning.",
        "Company Laptop",
        "HIGH",
        "Restarted the laptop and checked visible connections.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "HARDWARE",
        "Peripheral",
        "Keyboard is not responding",
        "The keyboard is connected but keystrokes are not being detected.",
        "Keyboard",
        "MEDIUM",
        "Disconnected and reconnected the keyboard.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "HARDWARE",
        "Peripheral",
        "Mouse is not working",
        "The mouse is connected but does not respond to movement or clicks.",
        "Mouse",
        "MEDIUM",
        "Reconnected the mouse.",
        "JUST_ME",
        "NO",
        None,
    ),
    (
        "HARDWARE",
        "Desktop",
        "Desktop workstation hardware failure",
        "A physical component of the company desktop is not functioning correctly.",
        "Company Desktop",
        "HIGH",
        "Restarted the workstation and checked power.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "HARDWARE",
        "Desktop",
        "Desktop hardware stopped responding",
        "The corporate desktop is running but an affected hardware component is not responding.",
        "Company Desktop",
        "MEDIUM",
        "Power-cycled the workstation.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "HARDWARE",
        "Docking station",
        "Docking station is not detected",
        "The laptop does not consistently detect the approved docking station.",
        "Docking Station",
        "MEDIUM",
        "Disconnected and reconnected the dock.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "HARDWARE",
        "Docking station",
        "External displays through the dock are unavailable",
        "The docking station connects but attached external displays are unavailable.",
        "Docking Station",
        "MEDIUM",
        "Restarted the laptop and reconnected the dock.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "HARDWARE",
        "Mobile device",
        "Company mobile device hardware problem",
        "A managed mobile device is showing a persistent hardware-related fault.",
        "Mobile Device",
        "HIGH",
        "Restarted the device.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "HARDWARE",
        "Mobile device",
        "Mobile device component is not responding",
        "A physical component on the company-managed mobile device is not functioning.",
        "Mobile Device",
        "MEDIUM",
        "Restarted the device and checked for visible damage.",
        "JUST_ME",
        "NO",
        None,
    ),

    # --------------------------------------------------------
    # NETWORK — 10
    # --------------------------------------------------------

    (
        "NETWORK",
        "Connectivity",
        "Corporate network is unreachable",
        "The workstation cannot reach approved internal or external network resources.",
        "Corporate Network",
        "HIGH",
        "Restarted the computer and reconnected the network.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "NETWORK",
        "Connectivity",
        "No network access from my workstation",
        "The company workstation cannot access approved network services.",
        "Corporate Network",
        "HIGH",
        "Restarted the workstation.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "NETWORK",
        "WiFi",
        "Corporate Wi-Fi keeps disconnecting",
        "The device repeatedly loses its connection to the approved corporate Wi-Fi network.",
        "Corporate Wi-Fi",
        "MEDIUM",
        "Disconnected and reconnected to Wi-Fi.",
        "JUST_ME",
        "NO",
        None,
    ),
    (
        "NETWORK",
        "WiFi",
        "Unable to connect to office Wi-Fi",
        "The device cannot establish a connection to the approved corporate wireless network.",
        "Corporate Wi-Fi",
        "HIGH",
        "Retried the wireless connection.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "NETWORK",
        "LAN",
        "Wired LAN connection is unavailable",
        "The workstation cannot maintain an approved wired LAN connection.",
        "Office LAN",
        "HIGH",
        "Checked the network cable and reconnected the port.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "NETWORK",
        "LAN",
        "Office LAN port is not providing connectivity",
        "The wired workstation shows no usable connection through the approved LAN port.",
        "Office LAN",
        "HIGH",
        "Tried another approved port.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "NETWORK",
        "DNS",
        "Corporate hostname will not resolve",
        "The network is connected but an approved corporate hostname cannot be resolved.",
        "Corporate DNS",
        "MEDIUM",
        "Retried the connection and restarted the workstation.",
        "JUST_ME",
        "NO",
        None,
    ),
    (
        "NETWORK",
        "DNS",
        "DNS resolution fails for an internal service",
        "An internal hostname does not resolve even though basic network connectivity is available.",
        "Corporate DNS",
        "MEDIUM",
        "Restarted the network connection.",
        "JUST_ME",
        "NO",
        None,
    ),
    (
        "NETWORK",
        "Bandwidth",
        "Network performance is unusually slow",
        "Approved network activities are experiencing unusually low throughput.",
        "Corporate Network",
        "MEDIUM",
        "Retried the affected network activity.",
        "JUST_ME",
        "NO",
        None,
    ),
    (
        "NETWORK",
        "Bandwidth",
        "File transfers are taking much longer than normal",
        "Approved file transfers are significantly slower than expected.",
        "Corporate Network",
        "MEDIUM",
        "Retried a small transfer.",
        "JUST_ME",
        "NO",
        None,
    ),

    # --------------------------------------------------------
    # PRINTER — 10
    # --------------------------------------------------------

    (
        "PRINTER",
        "Not printing",
        "Printer is not printing",
        "The selected approved printer is available but a normal print job produces no output.",
        "Corporate Printer",
        "HIGH",
        "Submitted a small test document.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "PRINTER",
        "Not printing",
        "Print job produces no output",
        "The printer accepts the job but nothing is printed successfully.",
        "Corporate Printer",
        "HIGH",
        "Checked the printer status and retried.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "PRINTER",
        "Driver",
        "Printer driver error appears",
        "The approved printer reports a driver-related issue during printing.",
        "Corporate Printer",
        "MEDIUM",
        "Restarted the print application.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "PRINTER",
        "Driver",
        "Printer driver may be incorrect",
        "The printer is detected but the installed driver may not match the printer model.",
        "Corporate Printer",
        "MEDIUM",
        "Checked the installed driver version.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "PRINTER",
        "Queue stuck",
        "Print queue job is stuck",
        "A document remains pending in the operating-system print queue.",
        "Corporate Printer",
        "MEDIUM",
        "Checked the queue and retried a small job.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "PRINTER",
        "Queue stuck",
        "Print job remains in error state",
        "A submitted print job stays in an error state and does not leave the queue.",
        "Corporate Printer",
        "HIGH",
        "Opened the print queue and checked the error message.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "PRINTER",
        "Quality",
        "Printed output is faded",
        "The printer produces output but the page is faded and has visible quality defects.",
        "Corporate Printer",
        "MEDIUM",
        "Printed a test page.",
        "JUST_ME",
        "NO",
        None,
    ),
    (
        "PRINTER",
        "Quality",
        "Printer output has streaks",
        "A test page contains visible streaks and other print-quality defects.",
        "Corporate Printer",
        "MEDIUM",
        "Checked paper settings and printed a test page.",
        "JUST_ME",
        "NO",
        None,
    ),
    (
        "PRINTER",
        "Scan",
        "Printer scanner is not detected",
        "The scanning function of the approved multifunction printer is not available.",
        "Multifunction Printer",
        "MEDIUM",
        "Reopened the scanning application.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "PRINTER",
        "Scan",
        "Scan job fails to complete",
        "The scanner is detected but a simple approved scan does not complete successfully.",
        "Multifunction Printer",
        "MEDIUM",
        "Retried a simple scan.",
        "JUST_ME",
        "YES",
        None,
    ),

    # --------------------------------------------------------
    # SECURITY — 10
    # --------------------------------------------------------

    (
        "SECURITY",
        "Phishing report",
        "Suspicious email should be reported",
        "I received a suspicious message that may be phishing and need to report it safely.",
        "Corporate Email",
        "HIGH",
        "Did not click the link and preserved the message.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "SECURITY",
        "Phishing report",
        "Possible credential phishing message",
        "An unexpected email asks me to enter company credentials using a linked page.",
        "Corporate Email",
        "HIGH",
        "Did not enter credentials and kept the message.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "SECURITY",
        "Phishing report",
        "Unexpected attachment in a suspicious message",
        "An email contains an unexpected attachment and appears to impersonate a known sender.",
        "Corporate Email",
        "HIGH",
        "Did not open the attachment.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "SECURITY",
        "Suspicious activity",
        "Unexpected login activity",
        "I received a login notification for activity that I do not recognize.",
        "Corporate Identity",
        "HIGH",
        "Recorded the alert details and did not continue interacting.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "SECURITY",
        "Suspicious activity",
        "Unfamiliar system activity",
        "An unfamiliar application or security event appeared on my company device.",
        "Corporate Workstation",
        "HIGH",
        "Recorded the alert and stopped interacting with the unfamiliar activity.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "SECURITY",
        "Suspicious activity",
        "Account activity I cannot explain",
        "There is unusual account activity that I cannot confirm as expected behavior.",
        "Corporate Identity",
        "HIGH",
        "Recorded the time and alert details.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "SECURITY",
        "Malware",
        "Malware warning on company computer",
        "The company device displays a malware or security warning during normal use.",
        "Corporate Workstation",
        "HIGH",
        "Stopped interacting with the suspicious application.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "SECURITY",
        "Malware",
        "Security alert suggests possible malware",
        "A security control reports suspicious software behavior on the workstation.",
        "Corporate Workstation",
        "CRITICAL",
        "Stopped risky activity and recorded the alert.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "SECURITY",
        "Data request",
        "Request for restricted security data",
        "A requester is asking for security information that may require authorization.",
        "Security Data",
        "HIGH",
        "Did not provide the requested restricted information.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "SECURITY",
        "Data request",
        "Request for account or system security records",
        "A business request asks for controlled security records and the required approval is unclear.",
        "Security Data",
        "HIGH",
        "Paused the request pending the approved process.",
        "JUST_ME",
        "YES",
        None,
    ),

    # --------------------------------------------------------
    # SOFTWARE — 10
    # --------------------------------------------------------

    (
        "SOFTWARE",
        "Crash",
        "Application keeps crashing",
        "An approved corporate application closes unexpectedly during normal use.",
        "Corporate Application",
        "HIGH",
        "Restarted the application and repeated the action.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "SOFTWARE",
        "Crash",
        "Software freezes after launch",
        "The supported application becomes unresponsive shortly after it starts.",
        "Corporate Application",
        "HIGH",
        "Restarted the workstation and reopened the application.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "SOFTWARE",
        "Licensing",
        "Software license activation failed",
        "The approved application reports that activation or licensing is unavailable.",
        "Corporate Application",
        "HIGH",
        "Retried activation through the approved process.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "SOFTWARE",
        "Licensing",
        "Application says license is expired",
        "A supported application reports an invalid or expired license.",
        "Corporate Application",
        "HIGH",
        "Confirmed the installed application version.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "SOFTWARE",
        "Installation",
        "Approved application installation failed",
        "The approved installer fails before the application can be used.",
        "Corporate Application",
        "MEDIUM",
        "Retried the approved installer once.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "SOFTWARE",
        "Installation",
        "Application cannot be configured after installation",
        "The approved application installed but required configuration cannot be completed.",
        "Corporate Application",
        "MEDIUM",
        "Checked the documented configuration values.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "SOFTWARE",
        "Update",
        "Application update failed",
        "The approved software update fails and the application remains on the current version.",
        "Corporate Application",
        "MEDIUM",
        "Retried the approved update once.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "SOFTWARE",
        "Update",
        "Software update is required",
        "The supported application requires an update before normal use can continue.",
        "Corporate Application",
        "HIGH",
        "Checked for an approved update.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "SOFTWARE",
        "Compatibility",
        "Application compatibility error",
        "The application reports that its version is not compatible with the current environment.",
        "Corporate Application",
        "MEDIUM",
        "Recorded the application and operating-system versions.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "SOFTWARE",
        "Compatibility",
        "Software and operating system versions do not match",
        "The approved application does not support the workstation's current operating-system version.",
        "Corporate Application",
        "MEDIUM",
        "Checked the approved application version.",
        "JUST_ME",
        "YES",
        None,
    ),

    # --------------------------------------------------------
    # VPN — 10
    # --------------------------------------------------------

    (
        "VPN",
        "Timeout",
        "VPN connection keeps timing out",
        "The corporate VPN connection repeatedly times out before a stable session is established.",
        "Corporate VPN",
        "HIGH",
        "Retried the VPN connection twice.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "VPN",
        "Timeout",
        "VPN disconnects during connection",
        "The approved VPN client repeatedly fails to maintain the connection.",
        "Corporate VPN",
        "HIGH",
        "Restarted the VPN client and retried.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "VPN",
        "Timeout",
        "Corporate VPN is slow and times out",
        "The VPN session does not complete reliably and times out during connection.",
        "Corporate VPN",
        "MEDIUM",
        "Retried the connection and restarted the client.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "VPN",
        "Timeout",
        "VPN cannot establish a stable session",
        "The VPN client repeatedly fails before a stable corporate session is available.",
        "Corporate VPN",
        "HIGH",
        "Restarted the client and retried.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "VPN",
        "Timeout",
        "VPN connection fails intermittently",
        "The corporate VPN sometimes connects but drops or times out during use.",
        "Corporate VPN",
        "HIGH",
        "Reconnected and restarted the workstation.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "VPN",
        "Certificate",
        "VPN certificate authentication failed",
        "The approved VPN client reports a certificate-related authentication failure.",
        "Corporate VPN",
        "HIGH",
        "Retried the connection after restarting the VPN client.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "VPN",
        "Certificate",
        "VPN client cannot validate the certificate",
        "The VPN connection fails because the client cannot complete certificate validation.",
        "Corporate VPN",
        "HIGH",
        "Restarted the VPN client and retried.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "VPN",
        "Certificate",
        "Corporate VPN certificate appears invalid",
        "The approved VPN client reports that the certificate cannot be accepted.",
        "Corporate VPN",
        "HIGH",
        "Recorded the certificate-related error.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "VPN",
        "Certificate",
        "VPN certificate authentication problem",
        "The client reaches authentication but the certificate check fails.",
        "Corporate VPN",
        "HIGH",
        "Retried the authentication process.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "VPN",
        "Certificate",
        "VPN client certificate is not accepted",
        "The corporate VPN client rejects the configured certificate during connection.",
        "Corporate VPN",
        "HIGH",
        "Restarted the client and retried.",
        "JUST_ME",
        "YES",
        None,
    ),

    # --------------------------------------------------------
    # UNCLASSIFIED — 10
    #
    # 7 General/Triage cases go to the matching generic
    # article.
    #
    # 3 application-authentication cases intentionally go to
    # the separate Application Authentication and Login Triage
    # article, which is also UNCLASSIFIED / General.
    # --------------------------------------------------------

    (
        "UNCLASSIFIED",
        "General",
        "I need help with an IT issue",
        "I am experiencing a company IT problem but the affected service is not yet clear.",
        "Unknown",
        "MEDIUM",
        "Restarted the computer.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "UNCLASSIFIED",
        "General",
        "Something is not working",
        "A corporate IT service is not behaving as expected but the affected area is unclear.",
        "Unknown",
        "MEDIUM",
        "Retried the operation once.",
        "JUST_ME",
        "NO",
        None,
    ),
    (
        "UNCLASSIFIED",
        "General",
        "General support request",
        "I need assistance with a company technology issue but cannot identify the service yet.",
        "Unknown",
        "LOW",
        "Checked the issue again.",
        "JUST_ME",
        "NO",
        None,
    ),
    (
        "UNCLASSIFIED",
        "General",
        "IT problem with unclear symptoms",
        "There is an issue affecting my work but there is not enough information to identify the technical domain.",
        "Unknown",
        "MEDIUM",
        "Restarted the workstation.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "UNCLASSIFIED",
        "Triage",
        "Unclassified issue needs investigation",
        "The issue cannot yet be classified confidently and requires initial troubleshooting and triage.",
        "Unknown",
        "MEDIUM",
        "Recorded the observable symptoms.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "UNCLASSIFIED",
        "Triage",
        "Unknown technical problem",
        "A company IT problem is occurring but the affected category remains unclear.",
        "Unknown",
        "MEDIUM",
        "Retried the failing action.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "UNCLASSIFIED",
        "Triage",
        "Issue category is unclear",
        "The available symptoms do not clearly map the request to a specific technical category.",
        "Unknown",
        "MEDIUM",
        "Restarted the affected application.",
        "JUST_ME",
        "YES",
        None,
    ),
    (
        "UNCLASSIFIED",
        "General",
        "Business application login problem",
        "The internal business application is reachable but the corporate login is rejected.",
        "Business Application",
        "HIGH",
        "Restarted the application and retried.",
        "JUST_ME",
        "YES",
        UNCLASSIFIED_AUTH_TITLE,
    ),
    (
        "UNCLASSIFIED",
        "General",
        "Application rejects corporate credentials",
        "The internal application is available but the normal corporate account cannot complete application authentication.",
        "Business Application",
        "HIGH",
        "Retried authentication after reopening the application.",
        "JUST_ME",
        "YES",
        UNCLASSIFIED_AUTH_TITLE,
    ),
    (
        "UNCLASSIFIED",
        "General",
        "Cannot authenticate to internal business application",
        "The business application opens but the company account cannot complete application authentication.",
        "Internal Application",
        "HIGH",
        "Restarted the browser session and tried again.",
        "JUST_ME",
        "YES",
        UNCLASSIFIED_AUTH_TITLE,
    ),
]


# ============================================================
# ARTICLE LOOKUP
# ============================================================

def build_article_lookup() -> dict[str, str]:
    """
    Build a lookup of published articles.

    Normal categories are keyed by:
        CATEGORY/subcategory

    Titles are also indexed so the special second
    UNCLASSIFIED/General article can be selected safely.
    """

    docs = list(
        knowledge_articles_collection.find(
            {"status": "PUBLISHED"},
            {
                "_id": 1,
                "title": 1,
                "category": 1,
                "sub_category": 1,
            },
        )
    )

    by_taxonomy: dict[str, str] = {}
    by_title: dict[str, str] = {}

    for doc in docs:
        article_id = str(doc["_id"])
        title = doc.get("title")
        category = doc.get("category")
        subcategory = doc.get("sub_category")

        if title:
            if title in by_title:
                raise RuntimeError(
                    f"Duplicate published article title: {title}"
                )

            by_title[title] = article_id

        if category and subcategory:
            key = f"{category}/{subcategory}"

            # UNCLASSIFIED/General intentionally has two
            # production articles, so it is not unique by taxonomy.
            if key == "UNCLASSIFIED/General":
                continue

            if key in by_taxonomy:
                raise RuntimeError(
                    f"Duplicate published article for "
                    f"{key}: {by_taxonomy[key]} and {article_id}"
                )

            by_taxonomy[key] = article_id

    # Add the chosen generic General article explicitly.
    general_title = ARTICLE_TITLES["UNCLASSIFIED/General"]

    if general_title not in by_title:
        raise RuntimeError(
            f"Published article not found: {general_title}"
        )

    by_taxonomy["UNCLASSIFIED/General"] = by_title[
        general_title
    ]

    return {
        **by_taxonomy,
        **{
            f"TITLE::{title}": article_id
            for title, article_id in by_title.items()
        },
    }


# ============================================================
# CASE BUILDER
# ============================================================

def resolve_article_id(
    *,
    category: str,
    subcategory: str,
    selector: str | None,
    lookup: dict[str, str],
) -> str:
    if selector:
        title_key = f"TITLE::{selector}"

        if title_key not in lookup:
            raise RuntimeError(
                f"Published article not found by title: {selector}"
            )

        return lookup[title_key]

    taxonomy_key = f"{category}/{subcategory}"

    if taxonomy_key not in lookup:
        raise RuntimeError(
            f"Published article not found for "
            f"{taxonomy_key}"
        )

    return lookup[taxonomy_key]


def build_cases() -> list[dict]:
    lookup = build_article_lookup()

    cases = []

    for index, row in enumerate(
        TICKETS,
        start=1,
    ):
        (
            category,
            subcategory,
            subject,
            description,
            affected_system,
            severity,
            already_tried,
            affected_scope,
            work_blocked,
            article_selector,
        ) = row

        article_id = resolve_article_id(
            category=category,
            subcategory=subcategory,
            selector=article_selector,
            lookup=lookup,
        )

        department = DEPARTMENTS[
            (index - 1) % len(DEPARTMENTS)
        ]

        cases.append(
            {
                "id": f"R{index:03d}",
                "ticket": {
                    "evaluation_ticket_id":
                        f"EVAL-{index:04d}",
                    "subject": subject,
                    "description": description,
                    "category": category,
                    "subcategory": subcategory,
                    "department": department,
                    "affected_system": affected_system,
                    "severity": severity,
                    "already_tried": already_tried,
                    "affected_scope": affected_scope,
                    "work_blocked": work_blocked,
                },
                "expected_article_ids": [
                    article_id
                ],
            }
        )

    return cases


# ============================================================
# VALIDATION
# ============================================================

def validate_cases(
    cases: list[dict],
) -> None:

    if len(cases) != 100:
        raise RuntimeError(
            f"Expected 100 cases, got {len(cases)}"
        )

    case_ids = [
        case["id"]
        for case in cases
    ]

    if case_ids != [
        f"R{i:03d}"
        for i in range(1, 101)
    ]:
        raise RuntimeError(
            "Case IDs are not exactly R001-R100."
        )

    ticket_ids = [
        case["ticket"]["evaluation_ticket_id"]
        for case in cases
    ]

    if ticket_ids != [
        f"EVAL-{i:04d}"
        for i in range(1, 101)
    ]:
        raise RuntimeError(
            "Evaluation ticket IDs are not exactly "
            "EVAL-0001-EVAL-0100."
        )

    if len(set(case_ids)) != 100:
        raise RuntimeError(
            "Duplicate case IDs detected."
        )

    if len(set(ticket_ids)) != 100:
        raise RuntimeError(
            "Duplicate evaluation ticket IDs detected."
        )

    category_counts = Counter(
        case["ticket"]["category"]
        for case in cases
    )

    expected_category_counts = {
        "ACCESS": 10,
        "APPLICATION": 10,
        "EMAIL": 10,
        "HARDWARE": 10,
        "NETWORK": 10,
        "PRINTER": 10,
        "SECURITY": 10,
        "SOFTWARE": 10,
        "VPN": 10,
        "UNCLASSIFIED": 10,
    }

    if dict(category_counts) != expected_category_counts:
        raise RuntimeError(
            "Unexpected category distribution: "
            + str(dict(category_counts))
        )

    unique_article_ids = {
        article_id
        for case in cases
        for article_id in case["expected_article_ids"]
    }

    # The final 100 cases intentionally exercise all 44
    # currently published production articles.
    if len(unique_article_ids) != 44:
        raise RuntimeError(
            f"Expected 44 unique article IDs, "
            f"got {len(unique_article_ids)}"
        )

    # Every expected article must correspond to a current
    # published article.
    current_ids = {
        str(doc["_id"])
        for doc in knowledge_articles_collection.find(
            {"status": "PUBLISHED"},
            {"_id": 1},
        )
    }

    stale_ids = unique_article_ids - current_ids

    if stale_ids:
        raise RuntimeError(
            "Golden set contains stale article IDs: "
            + ", ".join(sorted(stale_ids))
        )

    # Validate required ticket fields.
    required_fields = {
        "evaluation_ticket_id",
        "subject",
        "description",
        "category",
        "subcategory",
        "department",
        "affected_system",
        "severity",
        "already_tried",
        "affected_scope",
        "work_blocked",
    }

    for case in cases:
        ticket_fields = set(
            case["ticket"].keys()
        )

        missing = required_fields - ticket_fields

        if missing:
            raise RuntimeError(
                f"{case['id']} is missing ticket fields: "
                + ", ".join(sorted(missing))
            )

        if not case["expected_article_ids"]:
            raise RuntimeError(
                f"{case['id']} has no expected article IDs."
            )


# ============================================================
# MAIN
# ============================================================

def main():
    cases = build_cases()

    validate_cases(cases)

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            {
                "cases": cases
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    unique_articles = {
        article_id
        for case in cases
        for article_id in case["expected_article_ids"]
    }

    category_counts = Counter(
        case["ticket"]["category"]
        for case in cases
    )

    print("=" * 70)
    print("FINAL RETRIEVAL GOLDEN SET BUILT")
    print("=" * 70)
    print("OUTPUT:", OUTPUT)
    print("CASES:", len(cases))
    print("FIRST:", cases[0]["id"])
    print("LAST:", cases[-1]["id"])
    print(
        "UNIQUE TICKETS:",
        len({
            case["ticket"]["evaluation_ticket_id"]
            for case in cases
        }),
    )
    print(
        "UNIQUE ARTICLES:",
        len(unique_articles),
    )
    print(
        "CATEGORY COUNTS:",
        dict(category_counts),
    )
    print("=" * 70)


if __name__ == "__main__":
    main()