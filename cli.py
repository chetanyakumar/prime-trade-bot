"""
cli.py — Binance Futures Testnet Trading Bot CLI
==================================================

Rich + Typer CLI providing a polished, production-grade terminal
experience for interacting with the Binance Futures Testnet.

Commands
--------
::

    place-order   Submit a MARKET / LIMIT / STOP_MARKET / TAKE_PROFIT_MARKET order
    account       Display wallet balances and unrealised PnL
    ping          Lightweight connectivity check to the testnet
    interactive   Launch a menu-driven trading session

Usage Examples
--------------
::

    # MARKET order
    python cli.py place-order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

    # LIMIT order
    python cli.py place-order --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 105000

    # STOP_MARKET order
    python cli.py place-order --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.001 --stop-price 60000

    # Account info
    python cli.py account

    # Connectivity check
    python cli.py ping

    # Interactive mode
    python cli.py interactive
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from typing import Any, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, FloatPrompt, Prompt
from rich.table import Table
from rich.text import Text

from bot import __version__
from bot.client import BinanceFuturesClient
from bot.config import Settings, load_settings
from bot.exceptions import TradingBotError, ValidationError
from bot.logging_config import get_logger, setup_logging
from bot.orders import OrderResult, OrderService
from bot.utils import (
    console,
    display_order,
    error_panel,
    print_banner,
    print_error,
    print_info,
    print_success,
    print_warning,
    separator,
    success_panel,
    utc_now_iso,
)


# ════════════════════════════════════════════════════════════
#  Typer Application
# ════════════════════════════════════════════════════════════

app = typer.Typer(
    name="trading-bot",
    help="🚀 Binance Futures Testnet Trading Bot (USDT-M Futures)",
    add_completion=False,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

log = get_logger(__name__)


# ════════════════════════════════════════════════════════════
#  Bootstrap Helpers
# ════════════════════════════════════════════════════════════

def _load_and_connect() -> tuple[Settings, BinanceFuturesClient]:
    """
    Load configuration and establish a connection to the testnet.

    Returns
    -------
    tuple[Settings, BinanceFuturesClient]
        The loaded settings and a connected client instance.

    Raises
    ------
    typer.Exit
        If configuration or connection fails (after printing
        a user-friendly error message).
    """
    try:
        settings = load_settings()
        setup_logging(log_level=settings.log_level)

        log.info("CLI bootstrap started — %s", utc_now_iso())

        client = BinanceFuturesClient(settings)
        client.connect()

        print_success(
            f"Connected to Binance Testnet "
            f"[dim](key: {settings.masked_key})[/dim]"
        )
        return settings, client

    except TradingBotError as exc:
        log.error("Bootstrap failed: %s", exc.message)
        error_panel("Connection Failed", exc.message)
        raise typer.Exit(code=1) from exc

    except Exception as exc:
        log.exception("Unexpected bootstrap error")
        error_panel("Unexpected Error", str(exc))
        raise typer.Exit(code=1) from exc


def _init_service() -> OrderService:
    """
    Full bootstrap: config → logging → connect → OrderService.

    This is the primary initialiser used by ``place-order`` and
    ``interactive`` commands.
    """
    _, client = _load_and_connect()
    return OrderService(client)


def _render_order_summary(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float | None,
    stop_price: float | None,
) -> None:
    """
    Render a pre-submission order summary panel so the user
    can see what's about to be sent.
    """
    side_color = "green" if side.upper() == "BUY" else "red"
    lines = [
        f"  [bold cyan]Symbol[/bold cyan]        {symbol.upper()}",
        f"  [bold cyan]Side[/bold cyan]          [{side_color}]{side.upper()}[/{side_color}]",
        f"  [bold cyan]Type[/bold cyan]          {order_type.upper()}",
        f"  [bold cyan]Quantity[/bold cyan]      {quantity}",
    ]
    if price is not None:
        lines.append(f"  [bold cyan]Price[/bold cyan]         {price:,.2f}")
    if stop_price is not None:
        lines.append(f"  [bold cyan]Stop Price[/bold cyan]    {stop_price:,.2f}")

    console.print()
    console.print(
        Panel(
            "\n".join(lines),
            title="[bold yellow]📋  Order Preview[/bold yellow]",
            border_style="yellow",
            padding=(1, 2),
        )
    )


def _render_account_table(info: dict[str, Any]) -> None:
    """
    Build and display a Rich table of non-zero account balances.

    Parameters
    ----------
    info : dict
        Raw ``/fapi/v2/account`` response.
    """
    table = Table(
        title="💰  Account Balances",
        title_style="bold cyan",
        border_style="bright_blue",
        show_lines=False,
        padding=(0, 1),
    )
    table.add_column("#", style="dim", justify="right", width=3)
    table.add_column("Asset", style="bold white", min_width=8)
    table.add_column("Wallet Balance", justify="right", style="green")
    table.add_column("Available", justify="right", style="yellow")
    table.add_column("Unrealised PnL", justify="right")

    row_idx = 0
    for asset in info.get("assets", []):
        balance = float(asset.get("walletBalance", 0))
        if balance == 0:
            continue
        row_idx += 1
        available = float(asset.get("availableBalance", 0))
        pnl = float(asset.get("unrealizedProfit", 0))
        pnl_color = "green" if pnl >= 0 else "red"

        table.add_row(
            str(row_idx),
            asset["asset"],
            f"{balance:,.4f}",
            f"{available:,.4f}",
            f"[{pnl_color}]{pnl:+,.4f}[/{pnl_color}]",
        )

    if row_idx == 0:
        table.add_row("—", "No balances found", "", "", "")

    console.print()
    console.print(table)
    console.print()


# ════════════════════════════════════════════════════════════
#  Command: place-order
# ════════════════════════════════════════════════════════════

@app.command("place-order")
def cmd_place_order(
    symbol: str = typer.Option(
        ...,
        "--symbol", "-s",
        help="Trading pair (e.g. BTCUSDT, ETHUSDT).",
    ),
    side: str = typer.Option(
        ...,
        "--side", "-S",
        help="Order side: BUY or SELL.",
    ),
    order_type: str = typer.Option(
        ...,
        "--type", "-t",
        help="Order type: MARKET, LIMIT, STOP_MARKET, or TAKE_PROFIT_MARKET.",
    ),
    quantity: float = typer.Option(
        ...,
        "--quantity", "-q",
        help="Order quantity (must be > 0).",
    ),
    price: Optional[float] = typer.Option(
        None,
        "--price", "-p",
        help="Limit price (required for LIMIT orders).",
    ),
    stop_price: Optional[float] = typer.Option(
        None,
        "--stop-price",
        help="Stop/trigger price (required for STOP_MARKET / TAKE_PROFIT_MARKET).",
    ),
    time_in_force: Optional[str] = typer.Option(
        None,
        "--tif",
        help="Time-in-force: GTC (default), IOC, or FOK.",
    ),
) -> None:
    """
    Place a futures order on the Binance Testnet.

    Supports MARKET, LIMIT, STOP_MARKET, and TAKE_PROFIT_MARKET
    order types with full input validation and Rich output.
    """
    # ── Banner + preview ────────────────────────────────────
    print_banner()
    separator()
    print_info(
        f"Preparing {order_type.upper()} {side.upper()} order for "
        f"[bold]{symbol.upper()}[/bold] …"
    )
    separator()

    _render_order_summary(symbol, side, order_type, quantity, price, stop_price)

    # ── Bootstrap ───────────────────────────────────────────
    svc = _init_service()

    # ── Execute ─────────────────────────────────────────────
    try:
        response = svc.place_order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
            time_in_force=time_in_force,
        )

        display_order(response)
        print_success("Order submitted to Binance Futures Testnet.")
        separator()

    except ValidationError as exc:
        log.warning("Validation failed: %s", exc.message)
        error_panel(
            "Validation Error",
            f"[bold]{exc.field}[/bold]: {exc.reason}",
        )
        raise typer.Exit(code=1) from exc

    except TradingBotError as exc:
        log.error("Order failed: %s", exc.message)
        error_panel("Order Failed", exc.message)
        raise typer.Exit(code=1) from exc


# ════════════════════════════════════════════════════════════
#  Command: account
# ════════════════════════════════════════════════════════════

@app.command("account")
def cmd_account() -> None:
    """
    Display futures account balances and unrealised PnL.
    """
    print_banner()
    separator()
    print_info("Fetching account information …")
    separator()

    try:
        _, client = _load_and_connect()
        info = client.get_account_info()

        _render_account_table(info)

        # ── Margin summary ──────────────────────────────────
        total_balance = float(info.get("totalWalletBalance", 0))
        total_pnl = float(info.get("totalUnrealizedProfit", 0))
        margin_balance = float(info.get("totalMarginBalance", 0))
        pnl_color = "green" if total_pnl >= 0 else "red"

        summary_lines = [
            f"  [bold cyan]Total Balance[/bold cyan]     {total_balance:,.4f} USDT",
            f"  [bold cyan]Margin Balance[/bold cyan]    {margin_balance:,.4f} USDT",
            f"  [bold cyan]Unrealised PnL[/bold cyan]    [{pnl_color}]{total_pnl:+,.4f} USDT[/{pnl_color}]",
        ]

        console.print(
            Panel(
                "\n".join(summary_lines),
                title="[bold cyan]📊  Account Summary[/bold cyan]",
                border_style="bright_blue",
                padding=(1, 2),
            )
        )
        console.print()
        print_success("Account information retrieved.")
        separator()

    except TradingBotError as exc:
        log.error("Account fetch failed: %s", exc.message)
        error_panel("Account Error", exc.message)
        raise typer.Exit(code=1) from exc


# ════════════════════════════════════════════════════════════
#  Command: ping
# ════════════════════════════════════════════════════════════

@app.command("ping")
def cmd_ping() -> None:
    """
    Test connectivity to the Binance Futures Testnet.
    """
    print_banner()
    separator()
    print_info("Pinging Binance Futures Testnet …")

    try:
        _, client = _load_and_connect()
        is_alive = client.ping()

        if is_alive:
            success_panel(
                "Connection OK",
                f"Binance Futures Testnet is reachable.\n"
                f"Connected at: {client.connected_at}",
            )
        else:
            error_panel("Ping Failed", "Server did not respond.")
            raise typer.Exit(code=1)

    except TradingBotError as exc:
        error_panel("Ping Failed", exc.message)
        raise typer.Exit(code=1) from exc


# ════════════════════════════════════════════════════════════
#  Command: interactive
# ════════════════════════════════════════════════════════════

@app.command("interactive")
def cmd_interactive() -> None:
    """
    Launch an interactive, menu-driven trading session.

    Step-by-step prompts guide you through placing orders
    and viewing account info.
    """
    print_banner()

    # ── Bootstrap ───────────────────────────────────────────
    try:
        svc = _init_service()
    except SystemExit:
        return

    # ── Welcome panel ───────────────────────────────────────
    console.print()
    console.print(
        Panel(
            "[bold cyan]Interactive Trading Mode[/bold cyan]\n\n"
            "[dim]Navigate through the menu to place orders or\n"
            "view your account. Press Ctrl+C to return to the\n"
            "menu at any time.[/dim]",
            border_style="bright_blue",
            padding=(1, 3),
        )
    )

    session_orders = 0

    # ── Main loop ───────────────────────────────────────────
    while True:
        console.print()
        separator("═", 60)
        console.print("[bold cyan]  📌  MAIN MENU[/bold cyan]")
        separator("─", 60)
        console.print("  [bold white][1][/bold white]  📈  Place an order")
        console.print("  [bold white][2][/bold white]  💰  View account balances")
        console.print("  [bold white][3][/bold white]  🏓  Ping testnet")
        console.print("  [bold white][4][/bold white]  🚪  Exit")
        separator("═", 60)

        choice = Prompt.ask(
            "\n  [bold]Select an option[/bold]",
            choices=["1", "2", "3", "4"],
            default="1",
        )

        # ── Exit ────────────────────────────────────────────
        if choice == "4":
            console.print()
            separator()
            console.print(
                Panel(
                    f"[bold green]Session complete![/bold green]\n\n"
                    f"  Orders placed: [bold]{session_orders}[/bold]\n"
                    f"  Session ended: {utc_now_iso()}",
                    title="[bold cyan]👋  Goodbye[/bold cyan]",
                    border_style="bright_blue",
                    padding=(1, 2),
                )
            )
            break

        # ── Account info ────────────────────────────────────
        if choice == "2":
            try:
                info = svc.client.get_account_info()
                _render_account_table(info)
                print_success("Account info refreshed.")
            except TradingBotError as exc:
                print_error(exc.message)
            continue

        # ── Ping ────────────────────────────────────────────
        if choice == "3":
            try:
                ok = svc.client.ping()
                if ok:
                    print_success("Testnet is reachable ✓")
                else:
                    print_warning("Ping failed — server did not respond.")
            except TradingBotError as exc:
                print_error(exc.message)
            continue

        # ── Place order (interactive prompts) ───────────────
        try:
            console.print()
            separator()
            console.print("[bold cyan]  📝  New Order[/bold cyan]")
            separator()

            # Symbol
            symbol = Prompt.ask(
                "  [bold]Symbol[/bold]",
                default="BTCUSDT",
            ).strip().upper()

            # Side
            side = Prompt.ask(
                "  [bold]Side[/bold]",
                choices=["BUY", "SELL"],
                default="BUY",
            )

            # Order type
            order_type = Prompt.ask(
                "  [bold]Order Type[/bold]",
                choices=["MARKET", "LIMIT", "STOP_MARKET", "TAKE_PROFIT_MARKET"],
                default="MARKET",
            )

            # Quantity
            quantity = FloatPrompt.ask("  [bold]Quantity[/bold]")

            # Conditional fields
            price: float | None = None
            stop_price: float | None = None

            if order_type == "LIMIT":
                price = FloatPrompt.ask("  [bold]Limit Price[/bold]")

            if order_type in ("STOP_MARKET", "TAKE_PROFIT_MARKET"):
                stop_price = FloatPrompt.ask("  [bold]Stop Price[/bold]")

            # ── Preview ─────────────────────────────────────
            _render_order_summary(
                symbol, side, order_type, quantity, price, stop_price,
            )

            # ── Confirmation ────────────────────────────────
            confirmed = Confirm.ask(
                "\n  [bold yellow]Submit this order?[/bold yellow]",
                default=True,
            )

            if not confirmed:
                print_warning("Order cancelled by user.")
                continue

            # ── Submit ──────────────────────────────────────
            separator()
            print_info(
                f"Submitting {order_type} {side} {symbol} "
                f"qty={quantity} …"
            )

            response = svc.place_order(
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price,
                stop_price=stop_price,
            )

            display_order(response)
            session_orders += 1
            print_success(
                f"Order placed! "
                f"[dim](session total: {session_orders})[/dim]"
            )

        except ValidationError as exc:
            error_panel("Validation Error", f"[bold]{exc.field}[/bold]: {exc.reason}")

        except TradingBotError as exc:
            error_panel("Order Error", exc.message)

        except KeyboardInterrupt:
            console.print()
            print_info("Interrupted — returning to menu …")

        except Exception as exc:
            log.exception("Unexpected error in interactive mode")
            error_panel("Unexpected Error", str(exc))


# ════════════════════════════════════════════════════════════
#  Version Callback
# ════════════════════════════════════════════════════════════

def _version_callback(value: bool) -> None:
    """Print version and exit when --version is passed."""
    if value:
        console.print(
            f"[bold cyan]Binance Futures Testnet Bot[/bold cyan] "
            f"v{__version__}"
        )
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version", "-V",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """
    🚀 Binance Futures Testnet Trading Bot — USDT-M Futures.

    A production-quality CLI for placing and managing futures
    orders on the Binance Testnet.
    """


# ════════════════════════════════════════════════════════════
#  Entrypoint
# ════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app()
