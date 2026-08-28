from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RetrievalTicket:
    evaluation_ticket_id: str
    subject: str
    description: str
    category: str
    subcategory: str
    department: str
    affected_system: str
    severity: str
    already_tried: str
    affected_scope: str
    work_blocked: str

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "RetrievalTicket":
        required = (
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
        )

        missing = [
            key
            for key in required
            if key not in data
        ]

        if missing:
            raise ValueError(
                "Evaluation ticket missing required fields: "
                + ", ".join(missing)
            )

        return cls(
            evaluation_ticket_id=str(
                data["evaluation_ticket_id"]
            ),
            subject=str(data["subject"]),
            description=str(data["description"]),
            category=str(data["category"]),
            subcategory=str(data["subcategory"]),
            department=str(data["department"]),
            affected_system=str(data["affected_system"]),
            severity=str(data["severity"]),
            already_tried=str(data["already_tried"]),
            affected_scope=str(data["affected_scope"]),
            work_blocked=str(data["work_blocked"]),
        )

    def to_ticket_dict(self) -> dict[str, Any]:
        return {
            "ticket_id": self.evaluation_ticket_id,
            "subject": self.subject,
            "description": self.description,
            "category": self.category,
            "subcategory": self.subcategory,
            "department": self.department,
            "affected_system": self.affected_system,
            "severity": self.severity,
            "already_tried": self.already_tried,
            "affected_scope": self.affected_scope,
            "work_blocked": self.work_blocked,
        }


@dataclass(frozen=True)
class RetrievalCase:
    case_id: str
    ticket: RetrievalTicket
    expected_article_ids: tuple[str, ...]

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "RetrievalCase":
        required = (
            "id",
            "ticket",
            "expected_article_ids",
        )

        missing = [
            key
            for key in required
            if key not in data
        ]

        if missing:
            raise ValueError(
                "Retrieval case missing required fields: "
                + ", ".join(missing)
            )

        expected = tuple(
            str(value)
            for value in data["expected_article_ids"]
        )

        if not expected:
            raise ValueError(
                f"Retrieval case {data['id']} "
                "must contain at least one expected article id."
            )

        return cls(
            case_id=str(data["id"]),
            ticket=RetrievalTicket.from_dict(
                data["ticket"]
            ),
            expected_article_ids=expected,
        )