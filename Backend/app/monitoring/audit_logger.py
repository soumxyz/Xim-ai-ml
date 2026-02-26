import logging
import json
from datetime import datetime

class AuditLogger:
    def __init__(self):
        self.logger = logging.getLogger("metrixa.audit")

    def log_verification(self, title: str, result: dict):
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "submitted_title": title,
            "decision": result.get("decision"),
            "risk_tier": result.get("metadata", {}).get("risk_tier"),
            "confidence": result.get("metadata", {}).get("confidence_score"),
            "is_compliant": result.get("is_compliant")
        }
        self.logger.info(f"AUDIT_RECORD: {json.dumps(audit_entry)}")
        # In a real app, this would also write to an audit_logs SQL table
