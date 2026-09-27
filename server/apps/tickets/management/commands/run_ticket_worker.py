import time

from django.core.management.base import BaseCommand

from apps.tickets.services import claim_ticket_job, run_ticket_job


class Command(BaseCommand):
    help = "Run the durable MongoDB-backed ticket processing worker."

    def add_arguments(self, parser):
        parser.add_argument("--poll-seconds", type=float, default=2.0)
        parser.add_argument("--once", action="store_true")

    def handle(self, *args, **options):
        poll_seconds = max(0.2, options["poll_seconds"])
        self.stdout.write("Ticket worker started; waiting for queued jobs.")
        while True:
            job = claim_ticket_job()
            if job:
                run_ticket_job(job)
            elif options["once"]:
                return
            else:
                time.sleep(poll_seconds)
