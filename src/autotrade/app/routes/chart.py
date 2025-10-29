"""User facing chart interface endpoints."""

from __future__ import annotations

import asyncio
import json
import math
import random
from typing import AsyncIterator

from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse, StreamingResponse

from autotrade.core.clock import now

router = APIRouter(tags=["chart"])

# Minimal HTML template providing a real-time chart using Chart.js and SSE.
_CHART_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>AutoTrade Live Chart</title>
    <script src=\"https://cdn.jsdelivr.net/npm/chart.js\"></script>
    <style>
      body { font-family: sans-serif; margin: 2rem; background: #0f172a; color: #e2e8f0; }
      h1 { margin-bottom: 1.5rem; }
      #chart-container { background: #1e293b; padding: 1.5rem; border-radius: 1rem; }
      canvas { width: 100%; max-width: 960px; height: 480px; }
      #status { margin-top: 1rem; font-size: 0.9rem; color: #94a3b8; }
    </style>
  </head>
  <body>
    <h1>Real-time price for <span id=\"symbol\"></span></h1>
    <div id=\"chart-container\">
      <canvas id=\"price-chart\"></canvas>
      <div id=\"status\">Connecting…</div>
    </div>
    <script>
      const params = new URLSearchParams(window.location.search);
      const symbol = params.get("symbol") || "BTC";
      const interval = params.get("interval") || "1";
      document.getElementById("symbol").textContent = symbol;

      const ctx = document.getElementById("price-chart");
      const chart = new Chart(ctx, {
        type: "line",
        data: {
          labels: [],
          datasets: [{
            label: symbol + " price",
            data: [],
            borderColor: "#38bdf8",
            backgroundColor: "rgba(56, 189, 248, 0.25)",
            tension: 0.25,
            fill: true,
            pointRadius: 0,
          }],
        },
        options: {
          animation: false,
          scales: {
            x: { display: true, ticks: { color: "#cbd5f5" } },
            y: { display: true, ticks: { color: "#cbd5f5" } },
          },
          plugins: {
            legend: { labels: { color: "#e2e8f0" } },
          },
        },
      });

      const status = document.getElementById("status");
      const source = new EventSource(`/chart/stream?symbol=${encodeURIComponent(symbol)}&interval=${encodeURIComponent(interval)}`);

      source.onopen = () => {
        status.textContent = "Live connection established.";
      };

      source.onerror = (event) => {
        status.textContent = "Connection lost, retrying…";
      };

      source.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (!payload.timestamp || payload.price === undefined) {
            return;
          }
          chart.data.labels.push(new Date(payload.timestamp).toLocaleTimeString());
          chart.data.datasets[0].data.push(payload.price);
          if (chart.data.labels.length > 120) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
          }
          chart.update();
        } catch (error) {
          console.error("Malformed payload", error);
        }
      };
    </script>
  </body>
</html>
"""


async def _price_event_stream(
    symbol: str,
    interval: float,
    *,
    window: int = 120,
    limit: int | None = None,
) -> AsyncIterator[str]:
    """Generate server-sent events with pseudo real-time pricing data."""

    base = random.uniform(25000, 35000)
    step = 0
    history: list[float] = []
    emitted = 0

    try:
        while True:
            snapshot = now()
            # Produce a gently fluctuating price signal for demonstration purposes.
            seasonal = math.sin(step / 12) * 250
            noise = random.uniform(-40, 40)
            price = round(base + seasonal + noise, 2)
            history.append(price)
            if len(history) > window:
                history.pop(0)

            payload = {
                "symbol": symbol,
                "timestamp": snapshot.utc.isoformat(),
                "price": price,
                "window": history[-window:],
            }
            data = json.dumps(payload, separators=(",", ":"))
            yield f"data: {data}\n\n"
            emitted += 1
            if limit is not None and emitted >= limit:
                break
            step += 1
            await asyncio.sleep(interval)
    except asyncio.CancelledError:  # pragma: no cover - cooperative cancellation
        raise


@router.get("/chart", response_class=HTMLResponse)
async def chart_page(symbol: str = Query(default="BTC")) -> str:
    """Return a minimal HTML page hosting the live chart UI."""

    return _CHART_PAGE_TEMPLATE


@router.get("/chart/stream")
async def chart_stream(
    symbol: str = Query(default="BTC", min_length=1, max_length=32),
    interval: float = Query(default=1.0, ge=0.2, le=60.0),
    limit: int | None = Query(default=None, ge=1, le=1000),
) -> StreamingResponse:
    """Stream pseudo real-time price updates as Server Sent Events."""

    generator = _price_event_stream(
        symbol=symbol.upper(),
        interval=interval,
        limit=limit,
    )
    return StreamingResponse(generator, media_type="text/event-stream")


__all__ = ["router", "chart_page", "chart_stream"]
