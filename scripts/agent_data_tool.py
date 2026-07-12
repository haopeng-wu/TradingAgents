#!/usr/bin/env python3
"""Thin CLI wrapper exposing existing TradingAgents data-retrieval functions.

Per Constitution Principle V (Reuse Python Scripts as Tools), Copilot agents
MUST NOT reimplement data retrieval, vendor routing, or validation logic.
Instead they invoke this script via their terminal tool. This wrapper does
nothing but parse CLI arguments and call the existing `@tool`-decorated
functions / plain helper functions already defined under
``tradingagents/agents/utils/`` and ``tradingagents/dataflows/``.

Usage:
    python TradingAgents/scripts/agent_data_tool.py <subcommand> [options]

On success: prints the underlying formatted string to stdout, exit code 0.
On failure: prints a clear error message to stderr, exit code 1. No output is
fabricated on failure.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure the TradingAgents package is importable when this script is invoked
# directly (python TradingAgents/scripts/agent_data_tool.py ...) from the
# repository root or any other cwd.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# Load TradingAgents/.env explicitly. tradingagents/__init__.py also calls
# load_dotenv(find_dotenv(usecwd=True)), but find_dotenv only walks *upward*
# from the current working directory -- it never finds this .env when the
# script is invoked from the parent repo root (e.g. `uv run --project
# TradingAgents python TradingAgents/scripts/agent_data_tool.py ...`), which
# is exactly the documented invocation pattern. Loading it here by absolute
# path makes API keys (FRED_API_KEY, etc.) available regardless of cwd.
try:
    from dotenv import load_dotenv

    load_dotenv(_REPO_ROOT / ".env")
except ImportError:
    pass

from tradingagents.agents.utils.core_stock_tools import get_stock_data
from tradingagents.agents.utils.technical_indicators_tools import get_indicators
from tradingagents.agents.utils.fundamental_data_tools import (
    get_balance_sheet,
    get_cashflow,
    get_fundamentals,
    get_income_statement,
)
from tradingagents.agents.utils.news_data_tools import (
    get_global_news,
    get_insider_transactions,
    get_news,
)
from tradingagents.agents.utils.macro_data_tools import get_macro_indicators
from tradingagents.agents.utils.prediction_markets_tools import get_prediction_markets
from tradingagents.agents.utils.market_data_validation_tools import (
    get_verified_market_snapshot,
)
from tradingagents.dataflows.reddit import fetch_reddit_posts
from tradingagents.dataflows.stocktwits import fetch_stocktwits_messages


def _cmd_stock(args: argparse.Namespace) -> str:
    return get_stock_data.func(args.ticker, args.start_date, args.end_date)


def _cmd_indicators(args: argparse.Namespace) -> str:
    return get_indicators.func(
        args.ticker, args.indicator, args.curr_date, args.look_back_days
    )


def _cmd_fundamentals(args: argparse.Namespace) -> str:
    return get_fundamentals.func(args.ticker, args.curr_date)


def _cmd_balance_sheet(args: argparse.Namespace) -> str:
    return get_balance_sheet.func(args.ticker, args.freq, args.curr_date)


def _cmd_cashflow(args: argparse.Namespace) -> str:
    return get_cashflow.func(args.ticker, args.freq, args.curr_date)


def _cmd_income_statement(args: argparse.Namespace) -> str:
    return get_income_statement.func(args.ticker, args.freq, args.curr_date)


def _cmd_news(args: argparse.Namespace) -> str:
    return get_news.func(args.ticker, args.start_date, args.end_date)


def _cmd_global_news(args: argparse.Namespace) -> str:
    return get_global_news.func(args.curr_date, args.look_back_days, args.limit)


def _cmd_insider_transactions(args: argparse.Namespace) -> str:
    return get_insider_transactions.func(args.ticker)


def _cmd_macro(args: argparse.Namespace) -> str:
    return get_macro_indicators.func(args.indicator, args.curr_date, args.look_back_days)


def _cmd_prediction_markets(args: argparse.Namespace) -> str:
    return get_prediction_markets.func(args.topic, args.limit)


def _cmd_verified_snapshot(args: argparse.Namespace) -> str:
    return get_verified_market_snapshot.func(args.ticker, args.curr_date, args.look_back_days)


def _cmd_reddit(args: argparse.Namespace) -> str:
    return fetch_reddit_posts(args.ticker, limit_per_sub=args.limit_per_sub)


def _cmd_stocktwits(args: argparse.Namespace) -> str:
    return fetch_stocktwits_messages(args.ticker, limit=args.limit)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent_data_tool.py",
        description="Thin CLI wrapper around existing TradingAgents data-retrieval tools.",
    )
    sub = parser.add_subparsers(dest="subcommand", required=True)

    p = sub.add_parser("stock", help="Retrieve OHLCV stock price data")
    p.add_argument("--ticker", required=True)
    p.add_argument("--start-date", required=True)
    p.add_argument("--end-date", required=True)
    p.set_defaults(func=_cmd_stock)

    p = sub.add_parser("indicators", help="Retrieve a technical indicator")
    p.add_argument("--ticker", required=True)
    p.add_argument("--indicator", required=True)
    p.add_argument("--curr-date", required=True)
    p.add_argument("--look-back-days", type=int, default=30)
    p.set_defaults(func=_cmd_indicators)

    p = sub.add_parser("fundamentals", help="Retrieve comprehensive fundamental data")
    p.add_argument("--ticker", required=True)
    p.add_argument("--curr-date", required=True)
    p.set_defaults(func=_cmd_fundamentals)

    p = sub.add_parser("balance-sheet", help="Retrieve balance sheet data")
    p.add_argument("--ticker", required=True)
    p.add_argument("--freq", default="quarterly")
    p.add_argument("--curr-date", default=None)
    p.set_defaults(func=_cmd_balance_sheet)

    p = sub.add_parser("cashflow", help="Retrieve cash flow statement data")
    p.add_argument("--ticker", required=True)
    p.add_argument("--freq", default="quarterly")
    p.add_argument("--curr-date", default=None)
    p.set_defaults(func=_cmd_cashflow)

    p = sub.add_parser("income-statement", help="Retrieve income statement data")
    p.add_argument("--ticker", required=True)
    p.add_argument("--freq", default="quarterly")
    p.add_argument("--curr-date", default=None)
    p.set_defaults(func=_cmd_income_statement)

    p = sub.add_parser("news", help="Retrieve ticker-specific news")
    p.add_argument("--ticker", required=True)
    p.add_argument("--start-date", required=True)
    p.add_argument("--end-date", required=True)
    p.set_defaults(func=_cmd_news)

    p = sub.add_parser("global-news", help="Retrieve global/macro news")
    p.add_argument("--curr-date", required=True)
    p.add_argument("--look-back-days", type=int, default=None)
    p.add_argument("--limit", type=int, default=None)
    p.set_defaults(func=_cmd_global_news)

    p = sub.add_parser("insider-transactions", help="Retrieve insider transaction data")
    p.add_argument("--ticker", required=True)
    p.set_defaults(func=_cmd_insider_transactions)

    p = sub.add_parser("macro", help="Retrieve a macroeconomic indicator series")
    p.add_argument("--indicator", required=True)
    p.add_argument("--curr-date", required=True)
    p.add_argument("--look-back-days", type=int, default=None)
    p.set_defaults(func=_cmd_macro)

    p = sub.add_parser("prediction-markets", help="Retrieve prediction-market probabilities")
    p.add_argument("--topic", required=True)
    p.add_argument("--limit", type=int, default=None)
    p.set_defaults(func=_cmd_prediction_markets)

    p = sub.add_parser("verified-snapshot", help="Retrieve a deterministic market data snapshot")
    p.add_argument("--ticker", required=True)
    p.add_argument("--curr-date", required=True)
    p.add_argument("--look-back-days", type=int, default=30)
    p.set_defaults(func=_cmd_verified_snapshot)

    p = sub.add_parser("reddit", help="Retrieve recent Reddit posts mentioning a ticker")
    p.add_argument("--ticker", required=True)
    p.add_argument("--limit-per-sub", type=int, default=5)
    p.set_defaults(func=_cmd_reddit)

    p = sub.add_parser("stocktwits", help="Retrieve recent StockTwits messages for a ticker")
    p.add_argument("--ticker", required=True)
    p.add_argument("--limit", type=int, default=30)
    p.set_defaults(func=_cmd_stocktwits)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.func(args)
    except Exception as exc:  # noqa: BLE001 - surface any failure verbatim, never fabricate
        print(f"agent_data_tool.py: {args.subcommand} failed: {exc}", file=sys.stderr)
        return 1
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
