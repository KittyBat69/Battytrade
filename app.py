from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import random
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


SignalAction = Literal["BUY", "SELL", "HOLD"]


@dataclass
class Asset:
    symbol: str
    name: str
    market: Literal["TH", "US", "FX"]
    last_price: float


@dataclass
class Signal:
    symbol: str
    action: SignalAction
    confidence: float
    score: float
    reason: str
    timestamp: str


class SignalEngine:
    def __init__(self) -> None:
        self.weights = {
            "momentum": 0.35,
            "trend": 0.30,
            "volatility": 0.20,
            "liquidity": 0.15,
        }

    def _features(self, symbol: str) -> dict[str, float]:
        seeded = random.Random(symbol + datetime.now(timezone.utc).strftime("%Y%m%d%H"))
        return {
            "momentum": seeded.uniform(-1, 1),
            "trend": seeded.uniform(-1, 1),
            "volatility": seeded.uniform(0, 1),
            "liquidity": seeded.uniform(0.3, 1),
        }

    def score(self, symbol: str) -> tuple[float, str]:
        features = self._features(symbol)
        raw = (
            features["momentum"] * self.weights["momentum"]
            + features["trend"] * self.weights["trend"]
            + (1 - features["volatility"]) * self.weights["volatility"]
            + features["liquidity"] * self.weights["liquidity"]
        )
        reason = (
            f"Momentum={features['momentum']:.2f}, Trend={features['trend']:.2f}, "
            f"Vol={features['volatility']:.2f}, Liq={features['liquidity']:.2f}"
        )
        return raw, reason

    def generate_signal(self, symbol: str) -> Signal:
        score, reason = self.score(symbol)
        if score >= 0.45:
            action: SignalAction = "BUY"
        elif score <= -0.2:
            action = "SELL"
        else:
            action = "HOLD"

        confidence = min(99.0, max(51.0, (abs(score) * 120)))
        return Signal(
            symbol=symbol,
            action=action,
            confidence=round(confidence, 2),
            score=round(score, 3),
            reason=reason,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )


class RiskAnalyzer:
    def analyze(self, asset: Asset, signal: Signal) -> dict[str, float | str]:
        if signal.action == "HOLD":
            return {
                "decision": "WAIT",
                "risk_level": "LOW",
                "entry": asset.last_price,
                "stop_loss": asset.last_price,
                "take_profit": asset.last_price,
                "rr_ratio": 0.0,
            }

        atr_proxy = max(asset.last_price * 0.008, 0.001)
        if signal.action == "BUY":
            entry = asset.last_price
            stop_loss = entry - atr_proxy * 1.8
            take_profit = entry + atr_proxy * 3.2
        else:
            entry = asset.last_price
            stop_loss = entry + atr_proxy * 1.8
            take_profit = entry - atr_proxy * 3.2

        risk = abs(entry - stop_loss)
        reward = abs(take_profit - entry)
        rr_ratio = reward / risk if risk else 0

        risk_level = "HIGH" if rr_ratio < 1.4 else "MEDIUM" if rr_ratio < 1.8 else "LOW"
        decision = "EXECUTE" if rr_ratio >= 1.5 and signal.confidence >= 60 else "FILTERED"

        return {
            "decision": decision,
            "risk_level": risk_level,
            "entry": round(entry, 5),
            "stop_loss": round(stop_loss, 5),
            "take_profit": round(take_profit, 5),
            "rr_ratio": round(rr_ratio, 3),
        }


WATCHLIST = [
    Asset("PTT.BK", "PTT Public Company", "TH", 34.75),
    Asset("AOT.BK", "Airports of Thailand", "TH", 61.50),
    Asset("CPALL.BK", "CP ALL", "TH", 55.25),
    Asset("AAPL", "Apple Inc.", "US", 214.10),
    Asset("MSFT", "Microsoft Corp.", "US", 428.40),
    Asset("NVDA", "NVIDIA Corp.", "US", 946.30),
    Asset("EURUSD", "Euro / US Dollar", "FX", 1.0842),
    Asset("USDJPY", "US Dollar / Japanese Yen", "FX", 154.21),
    Asset("XAUUSD", "Gold Spot", "FX", 2342.10),
]

engine = SignalEngine()
risk = RiskAnalyzer()

app = FastAPI(title="Battytrade Smart Trading Dashboard")

static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
def root() -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.get("/api/watchlist")
def get_watchlist() -> list[dict]:
    return [asdict(a) for a in WATCHLIST]


@app.get("/api/signals")
def get_signals() -> list[dict]:
    return [asdict(engine.generate_signal(a.symbol)) for a in WATCHLIST]


@app.get("/api/analysis/{symbol}")
def get_analysis(symbol: str) -> dict:
    asset = next((a for a in WATCHLIST if a.symbol == symbol), None)
    if not asset:
        raise HTTPException(status_code=404, detail="Symbol not found")
    signal = engine.generate_signal(symbol)
    return {
        "asset": asdict(asset),
        "signal": asdict(signal),
        "risk": risk.analyze(asset, signal),
    }


@app.get("/api/market-summary")
def market_summary() -> dict:
    signals = [engine.generate_signal(a.symbol) for a in WATCHLIST]
    buy = len([s for s in signals if s.action == "BUY"])
    sell = len([s for s in signals if s.action == "SELL"])
    hold = len([s for s in signals if s.action == "HOLD"])
    avg_conf = sum(s.confidence for s in signals) / len(signals)

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_assets": len(WATCHLIST),
        "buy_signals": buy,
        "sell_signals": sell,
        "hold_signals": hold,
        "avg_confidence": round(avg_conf, 2),
    }
