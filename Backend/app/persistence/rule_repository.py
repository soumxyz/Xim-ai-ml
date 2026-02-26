class RuleRepository:
    def __init__(self):
        # Placeholder for DB session
        pass

    async def get_disallowed_words(self) -> list:
        # Fetch from DB table 'compliance_rules'
        return ["police", "army", "cbi", "cid"]

    async def get_restricted_prefixes(self) -> list:
        return ["test-", "prod-"]
