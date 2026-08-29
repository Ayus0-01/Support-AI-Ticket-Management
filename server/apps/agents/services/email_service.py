from datetime import datetime
from django.core.mail import send_mail
from django.conf import settings
from bson import ObjectId
from decouple import config

from AIticket.db import (
    email_logs_collection,
)

# Email config flags
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="no-reply@supportpilot.ai")
SUPPORT_TEAM_EMAIL = config("SUPPORT_TEAM_EMAIL", default="support-team@supportpilot.ai")

def _send_actual_or_mock_email(recipient, subject, body, ticket_id, email_type):
    """
    Sends email using Django's mail mechanism if SMTP is configured.
    Otherwise, logs to the console and records a 'SENT' status in DB.
    """
    ticket_id_str = str(ticket_id)
    sent_successfully = False
    
    # We can check if mail configurations are set in settings (Django setting is configured)
    # If not using a console or dummy backend
    if getattr(settings, "EMAIL_HOST", None) and settings.EMAIL_HOST != "localhost":
        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False
            )
            sent_successfully = True
        except Exception as e:
            print(f"SMTP Email delivery failed: {e}. Logging as failed delivery.")
    else:
        # Mock mode console log
        print(f"=== [MOCK EMAIL SENT] ===")
        print(f"Type: {email_type}")
        print(f"To: {recipient}")
        print(f"Subject: {subject}")
        print(f"Body:\n{body}")
        print(f"=========================")
        sent_successfully = True

    status_str = "SENT" if sent_successfully else "FAILED"
    
    log_entry = {
        "ticket_id": ticket_id_str,
        "recipient": recipient,
        "subject": subject,
        "email_type": email_type,
        "status": status_str,
        "sent_at": datetime.utcnow()
    }
    
    result = email_logs_collection.insert_one(log_entry)
    log_entry["_id"] = str(result.inserted_id)
    return log_entry

def send_ticket_created_email(ticket):
    """
    Send ticket creation confirmation email.
    """
    ticket_id = ticket["_id"]
    recipient = ticket.get("requester", {}).get("email") or "user@example.com"
    subject = f"SupportPilot Ticket Received: {ticket.get('subject')}"
    body = f"""Hi {ticket.get('requester', {}).get('username', 'Customer')},

We have successfully received your support request.

Ticket ID: {ticket.get('ticket_id')}
Subject: {ticket.get('subject')}
Severity: {ticket.get('severity')}

Our AI agents are currently diagnosing the issue. You will receive an update shortly.

Best regards,
SupportPilot Team
"""
    return _send_actual_or_mock_email(recipient, subject, body, ticket_id, "TICKET_CREATED")

def send_resolution_email(ticket, resolution_text):
    """
    Send troubleshoot / resolution email.
    """
    ticket_id = ticket["_id"]
    recipient = ticket.get("requester", {}).get("email") or "user@example.com"
    subject = f"SupportPilot Resolution Action Required: {ticket.get('subject')}"
    body = f"""Hi {ticket.get('requester', {}).get('username', 'Customer')},

Our AI-assistant has successfully analyzed your issue and generated a recommended resolution:

{resolution_text}

Please follow these troubleshooting steps and let us know if they resolve your issue.

Best regards,
SupportPilot Agent
"""
    return _send_actual_or_mock_email(recipient, subject, body, ticket_id, "RESOLUTION")

def send_escalation_email(ticket, reason):
    """
    Send escalation notice email to requester and the support team.
    """
    ticket_id = ticket["_id"]
    recipient = ticket.get("requester", {}).get("email") or "user@example.com"
    subject = f"SupportPilot Escalation Notice: {ticket.get('subject')}"
    
    # 1. Email to Requester
    requester_body = f"""Hi {ticket.get('requester', {}).get('username', 'Customer')},

We wanted to inform you that your request has been escalated to our human support team for deeper investigation.

Ticket ID: {ticket.get('ticket_id')}
Reason for Escalation: {reason}

A support engineer will contact you shortly.

Best regards,
SupportPilot Team
"""
    _send_actual_or_mock_email(recipient, subject, requester_body, ticket_id, "ESCALATION")

    # 2. Email to Support Team
    team_subject = f"[ALERT] Ticket Escalated: {ticket.get('ticket_id')}"
    team_body = f"""Hi Support Team,

A ticket has been escalated due to low confidence in AI resolution.

Ticket ID: {ticket.get('ticket_id')}
Subject: {ticket.get('subject')}
Severity: {ticket.get('severity')}
Escalation Reason: {reason}

Please review this ticket and contact the requester.

Link: http://localhost:5173/dashboard (Status: Escalated)
"""
    return _send_actual_or_mock_email(SUPPORT_TEAM_EMAIL, team_subject, team_body, ticket_id, "ESCALATION_TEAM")

def send_resolved_email(ticket):
    """
    Send confirmation of ticket resolution.
    """
    ticket_id = ticket["_id"]
    recipient = ticket.get("requester", {}).get("email") or "user@example.com"
    subject = f"SupportPilot Ticket Resolved: {ticket.get('subject')}"
    body = f"""Hi {ticket.get('requester', {}).get('username', 'Customer')},

Your support request has been marked as Resolved.

Ticket ID: {ticket.get('ticket_id')}
Subject: {ticket.get('subject')}

If you still experience issues, feel free to respond directly to this email to reopen the request.

Best regards,
SupportPilot Team
"""
    return _send_actual_or_mock_email(recipient, subject, body, ticket_id, "RESOLVED")

def get_email_logs(ticket_id):
    ticket_id_str = str(ticket_id)
    logs = list(email_logs_collection.find({"ticket_id": ticket_id_str}))
    # Convert ObjectIds to strings
    for log in logs:
        log["_id"] = str(log["_id"])
    return logs
