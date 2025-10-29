import json

from fastapi.testclient import TestClient

from autotrade.app.main import app


client = TestClient(app)


def test_chart_page_returns_html():
    response = client.get("/chart")
    assert response.status_code == 200
    assert "chart.js" in response.text.lower()
    assert "EventSource" in response.text


def test_chart_stream_emits_events():
    with client.stream(
        "GET",
        "/chart/stream",
        params={"symbol": "btc", "interval": 0.2, "limit": 1},
    ) as response:
        assert response.status_code == 200
        lines: list[str] = []
        for line in response.iter_lines():
            if line:
                lines.append(line)
            if len(lines) >= 1:
                break
    assert lines, "No streaming payload received"
    first = lines[0]
    assert first.startswith("data: ")
    payload = json.loads(first.removeprefix("data: "))
    assert payload["symbol"] == "BTC"
    assert "timestamp" in payload
    assert "price" in payload
