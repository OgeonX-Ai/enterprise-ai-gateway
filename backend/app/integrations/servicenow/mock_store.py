import random
import time
from typing import Dict, List, Optional


class MockIncidentStore:
    def __init__(self) -> None:
        self._incidents: Dict[str, Dict] = {}
        self._seed()

    def _seed(self) -> None:
        seeds = [
            {
                "number": "INC0012345",
                "sys_id": "sys-0012345",
                "short_description": "VPN connectivity issues for remote worker",
                "description": "User cannot connect to corporate VPN from home network.",
                "state": "New",
                "priority": "2 - High",
                "assigned_to": "alex.jones",
                "assignment_group": "Network Ops",
                "work_notes": ["Ticket created"],
            },
            {
                "number": "INC0012346",
                "sys_id": "sys-0012346",
                "short_description": "Email delivery delays",
                "description": "Reports of delayed outbound emails to customers.",
                "state": "In Progress",
                "priority": "3 - Moderate",
                "assigned_to": "casey.lee",
                "assignment_group": "Messaging",
                "work_notes": ["Monitoring mail queues"],
            },
            {
                "number": "INC0012347",
                "sys_id": "sys-0012347",
                "short_description": "Laptop blue screen after update",
                "description": "BSOD observed after latest Windows patch.",
                "state": "In Progress",
                "priority": "2 - High",
                "assigned_to": "fernando.garcia",
                "assignment_group": "EUC",
                "work_notes": ["User provided minidump"],
            },
            {
                "number": "INC0012348",
                "sys_id": "sys-0012348",
                "short_description": "Service degradation in payments API",
                "description": "Elevated error rates detected in payment processing.",
                "state": "New",
                "priority": "1 - Critical",
                "assigned_to": "oncall.engineer",
                "assignment_group": "Payments",
                "work_notes": ["Pager triggered"],
            },
            {
                "number": "INC0012349",
                "sys_id": "sys-0012349",
                "short_description": "Badge readers offline in HQ",
                "description": "Multiple doors not recognizing employee badges.",
                "state": "Awaiting Assignment",
                "priority": "3 - Moderate",
                "assigned_to": None,
                "assignment_group": "Facilities",
                "work_notes": ["Security notified"],
            },
        ]
        self._incidents = {item["number"]: item for item in seeds}

    def _find_incident(self, ticket: Dict[str, Optional[str]]) -> Optional[Dict]:
        number = ticket.get("number")
        sys_id = ticket.get("sys_id")
        if number and number in self._incidents:
            return self._incidents[number]
        if sys_id:
            for inc in self._incidents.values():
                if inc.get("sys_id") == sys_id:
                    return inc
        return None

    def search(self, query: str, limit: int = 5) -> List[Dict]:
        keywords = query.lower().split()
        results = []
        for incident in self._incidents.values():
            haystack = f"{incident['short_description']} {incident['description']}".lower()
            if all(k in haystack for k in keywords):
                results.append(incident)
            if len(results) >= limit:
                break
        return results

    def get(self, ticket: Dict[str, Optional[str]]) -> Optional[Dict]:
        return self._find_incident(ticket)

    def update(self, ticket: Dict[str, Optional[str]], fields: Dict, reason: str) -> Optional[Dict]:
        incident = self._find_incident(ticket)
        if not incident:
            return None
        incident.update(fields)
        incident.setdefault("audit", []).append(
            {
                "reason": reason,
                "fields": fields,
                "timestamp": time.time(),
            }
        )
        return incident

    def add_work_note(
        self, ticket: Dict[str, Optional[str]], note: str, visibility: str
    ) -> Optional[Dict]:
        incident = self._find_incident(ticket)
        if not incident:
            return None
        incident.setdefault("work_notes", []).append(f"[{visibility}] {note}")
        return incident

    def notify_resolver(self, ticket: Dict[str, Optional[str]], message: str, channel: str, urgency: str) -> Dict:
        number = ticket.get("number") or "INC{0:07d}".format(random.randint(1000000, 9999999))
        return {
            "number": number,
            "status": "queued",
            "channel": channel,
            "urgency": urgency,
            "message": message,
        }
