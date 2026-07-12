"""Smoke test for the agent_data_tool.py CLI wrapper.

Verifies every subcommand delegates to the correct underlying function and
returns non-empty text for a known-good input, without making real network
calls. Follows the mocking pattern used in test_vendor_routing.py.
"""
import runpy
import sys
from pathlib import Path
from unittest import mock

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "agent_data_tool.py"

sys.path.insert(0, str(REPO_ROOT))

from scripts import agent_data_tool  # noqa: E402


def _run(argv, capsys):
    exit_code = agent_data_tool.main(argv)
    captured = capsys.readouterr()
    return exit_code, captured.out, captured.err


@pytest.mark.unit
class TestAgentDataToolCli:
    def test_stock(self, capsys):
        with mock.patch(
            "tradingagents.agents.utils.core_stock_tools.route_to_vendor",
            return_value="STOCK_DATA",
        ):
            code, out, _ = _run(
                ["stock", "--ticker", "AAPL", "--start-date", "2026-01-01", "--end-date", "2026-01-10"],
                capsys,
            )
        assert code == 0
        assert "STOCK_DATA" in out

    def test_indicators(self, capsys):
        with mock.patch(
            "tradingagents.agents.utils.technical_indicators_tools.route_to_vendor",
            return_value="INDICATOR_DATA",
        ):
            code, out, _ = _run(
                ["indicators", "--ticker", "AAPL", "--indicator", "rsi", "--curr-date", "2026-01-10"],
                capsys,
            )
        assert code == 0
        assert "INDICATOR_DATA" in out

    def test_fundamentals(self, capsys):
        with mock.patch(
            "tradingagents.agents.utils.fundamental_data_tools.route_to_vendor",
            return_value="FUNDAMENTALS_DATA",
        ):
            code, out, _ = _run(
                ["fundamentals", "--ticker", "AAPL", "--curr-date", "2026-01-10"], capsys
            )
        assert code == 0
        assert "FUNDAMENTALS_DATA" in out

    def test_balance_sheet(self, capsys):
        with mock.patch(
            "tradingagents.agents.utils.fundamental_data_tools.route_to_vendor",
            return_value="BALANCE_SHEET_DATA",
        ):
            code, out, _ = _run(["balance-sheet", "--ticker", "AAPL"], capsys)
        assert code == 0
        assert "BALANCE_SHEET_DATA" in out

    def test_cashflow(self, capsys):
        with mock.patch(
            "tradingagents.agents.utils.fundamental_data_tools.route_to_vendor",
            return_value="CASHFLOW_DATA",
        ):
            code, out, _ = _run(["cashflow", "--ticker", "AAPL"], capsys)
        assert code == 0
        assert "CASHFLOW_DATA" in out

    def test_income_statement(self, capsys):
        with mock.patch(
            "tradingagents.agents.utils.fundamental_data_tools.route_to_vendor",
            return_value="INCOME_STATEMENT_DATA",
        ):
            code, out, _ = _run(["income-statement", "--ticker", "AAPL"], capsys)
        assert code == 0
        assert "INCOME_STATEMENT_DATA" in out

    def test_news(self, capsys):
        with mock.patch(
            "tradingagents.agents.utils.news_data_tools.route_to_vendor",
            return_value="NEWS_DATA",
        ):
            code, out, _ = _run(
                ["news", "--ticker", "AAPL", "--start-date", "2026-01-01", "--end-date", "2026-01-10"],
                capsys,
            )
        assert code == 0
        assert "NEWS_DATA" in out

    def test_global_news(self, capsys):
        with mock.patch(
            "tradingagents.agents.utils.news_data_tools.route_to_vendor",
            return_value="GLOBAL_NEWS_DATA",
        ):
            code, out, _ = _run(["global-news", "--curr-date", "2026-01-10"], capsys)
        assert code == 0
        assert "GLOBAL_NEWS_DATA" in out

    def test_insider_transactions(self, capsys):
        with mock.patch(
            "tradingagents.agents.utils.news_data_tools.route_to_vendor",
            return_value="INSIDER_DATA",
        ):
            code, out, _ = _run(["insider-transactions", "--ticker", "AAPL"], capsys)
        assert code == 0
        assert "INSIDER_DATA" in out

    def test_macro(self, capsys):
        with mock.patch(
            "tradingagents.agents.utils.macro_data_tools.route_to_vendor",
            return_value="MACRO_DATA",
        ):
            code, out, _ = _run(["macro", "--indicator", "cpi", "--curr-date", "2026-01-10"], capsys)
        assert code == 0
        assert "MACRO_DATA" in out

    def test_prediction_markets(self, capsys):
        with mock.patch(
            "tradingagents.agents.utils.prediction_markets_tools.route_to_vendor",
            return_value="PREDICTION_MARKETS_DATA",
        ):
            code, out, _ = _run(["prediction-markets", "--topic", "Fed rate cut"], capsys)
        assert code == 0
        assert "PREDICTION_MARKETS_DATA" in out

    def test_verified_snapshot(self, capsys):
        with mock.patch(
            "scripts.agent_data_tool.get_verified_market_snapshot",
            return_value="VERIFIED_SNAPSHOT_DATA",
        ):
            code, out, _ = _run(
                ["verified-snapshot", "--ticker", "AAPL", "--curr-date", "2026-01-10"], capsys
            )
        assert code == 0
        assert "VERIFIED_SNAPSHOT_DATA" in out

    def test_reddit(self, capsys):
        with mock.patch(
            "scripts.agent_data_tool.fetch_reddit_posts", return_value="REDDIT_DATA"
        ):
            code, out, _ = _run(["reddit", "--ticker", "AAPL"], capsys)
        assert code == 0
        assert "REDDIT_DATA" in out

    def test_stocktwits(self, capsys):
        with mock.patch(
            "scripts.agent_data_tool.fetch_stocktwits_messages", return_value="STOCKTWITS_DATA"
        ):
            code, out, _ = _run(["stocktwits", "--ticker", "AAPL"], capsys)
        assert code == 0
        assert "STOCKTWITS_DATA" in out

    def test_failure_exits_nonzero_with_stderr_message(self, capsys):
        with mock.patch(
            "tradingagents.agents.utils.fundamental_data_tools.route_to_vendor",
            side_effect=RuntimeError("boom"),
        ):
            code, out, err = _run(
                ["fundamentals", "--ticker", "BADTICKER", "--curr-date", "2026-01-10"], capsys
            )
        assert code == 1
        assert out == ""
        assert "boom" in err
