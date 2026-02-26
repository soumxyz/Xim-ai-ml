import asyncio
from app.orchestration.metrixa_orchestrator import MetrixaOrchestrator

async def test_logic():
    orch = MetrixaOrchestrator()
    # Mocking the semantic calculation if it fails due to segfault
    print("Testing verification result structure...")
    try:
        res = await orch.verify("Sunrise Chronicle")
        print(f"Decision: {res.decision}")
        print(f"Risk Tier: {res.metadata['risk_tier']}")
        print(f"Confidence: {res.metadata['confidence_score']}")
        print(f"Structural Patterns: {res.metadata['structural_patterns']}")
    except Exception as e:
        print(f"Test failed with error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_logic())
