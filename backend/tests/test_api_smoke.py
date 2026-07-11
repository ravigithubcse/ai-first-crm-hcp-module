# =============================================================================
# AI-First CRM HCP Module - API Smoke Tests
# =============================================================================
# Author  : Ravi Kumar
# Version : 1.0.0
# Covers every non-LLM route end to end: HCP CRUD, Interaction CRUD, and
# Follow-up CRUD, plus the static /agent/tools listing. This is the layer
# that runs the same whether the AI is configured or not, so it's what CI
# (and a reviewer running `pytest` with no Groq key) can rely on.
# =============================================================================
from fastapi.testclient import TestClient

from app.main import app


def _client():
    return TestClient(app)


def test_root_and_health():
    with _client() as c:
        assert c.get("/").status_code == 200
        assert c.get("/health").json()["status"] == "healthy"


def test_hcp_crud():
    with _client() as c:
        created = c.post("/api/hcps", json={"full_name": "Dr. Anjali Sharma", "specialty": "Oncology"})
        assert created.status_code == 201
        hcp_id = created.json()["id"]

        listed = c.get("/api/hcps")
        assert listed.status_code == 200
        assert listed.json()["total"] == 1

        found = c.get("/api/hcps/search/by-name", params={"name": "Sharma"})
        assert found.status_code == 200
        assert any(h["id"] == hcp_id for h in found.json())

        updated = c.put(f"/api/hcps/{hcp_id}", json={"tier": "key_opinion_leader"})
        assert updated.status_code == 200
        assert updated.json()["tier"] == "key_opinion_leader"


def test_interaction_crud_and_follow_up():
    with _client() as c:
        hcp_id = c.post("/api/hcps", json={"full_name": "Dr. Rohan Smith"}).json()["id"]

        created = c.post("/api/interactions", json={
            "hcp_id": hcp_id,
            "interaction_type": "Meeting",
            "date": "2026-07-10T10:00:00",
            "topics_discussed": "OncoBoost Phase III efficacy",
            "sentiment": "positive",
        })
        assert created.status_code == 201
        interaction_id = created.json()["id"]

        listed = c.get("/api/interactions")
        assert listed.status_code == 200
        assert listed.json()["total"] == 1

        updated = c.put(f"/api/interactions/{interaction_id}", json={"sentiment": "neutral"})
        assert updated.status_code == 200
        assert updated.json()["sentiment"] == "neutral"

        history = c.get(f"/api/interactions/hcp/{hcp_id}/history")
        assert history.status_code == 200

        follow_up = c.post("/api/follow-ups", json={
            "interaction_id": interaction_id,
            "title": "Send OncoBoost Phase III PDF",
            "due_date": "2026-07-24",
        })
        assert follow_up.status_code == 201
        assert follow_up.json()["status"] == "pending"


def test_agent_tools_listing_is_static_and_needs_no_llm():
    with _client() as c:
        resp = c.get("/api/agent/tools")
        assert resp.status_code == 200
        names = {t["name"] for t in resp.json()["tools"]}
        assert names == {
            "log_interaction", "edit_interaction", "view_history",
            "generate_report", "schedule_follow_up",
        }
