<p align="center">
  <br/>
  <strong style="font-size: 2em;">📈 Binance Futures Testnet Trading Bot</strong>
  <br/>
  <em>A production-quality Python CLI for USDT-M Futures on the Binance Testnet</em>
  <br/><br/>
  <code>Python 3.11+</code> · <code>Typer</code> · <code>Rich</code> · <code>python-binance</code>
  <br/><br/>
</p>

---

## 🎯 Project Overview

A **modular, interview-ready** command-line trading bot that places and manages USDT-M Futures orders on the [Binance Futures Testnet](https://testnet.binancefuture.com). Built with clean architecture principles, comprehensive error handling, and a polished terminal UI.

This project demonstrates:

- **Layered architecture** — CLI → Service → Client → Exchange
- **Typed Python** — type hints on every function, frozen dataclasses
- **Robust error handling** — 7-class exception hierarchy with structured messages
- **Professional UX** — coloured panels, tables, icons, and ASCII art via Rich
- **Production logging** — rotating file handler with full audit trail
- **Secure credential management** — `.env` loading, masked key display, placeholder detection

> ⚠️ **Testnet only** — This bot never connects to the Binance production API. All trades use virtual funds.

> **📌 Regional Access Note**
>
> This project is **fully configured** for the Binance Futures Testnet. The implementation — including HMAC-SHA256 request signing, input validation, structured logging, and Binance Futures REST endpoint integration — is **production-ready** and aligned with [Binance Futures Testnet documentation](https://testnet.binancefuture.com).
>
> However, due to **regional restrictions and/or account verification requirements** imposed by Binance, testnet API key generation and live order execution may not be available in all regions or for all account types. If you encounter issues generating API keys or placing orders, this is a **Binance-side restriction** — not a limitation of this codebase.
>
> The architecture, code quality, error handling, and integration patterns remain fully demonstrable and portfolio-ready regardless of testnet availability.

---

## ✨ Features

| Category | Feature | Details |
|---|---|---|
| **Order Types** | MARKET | Instant execution at best available price |
| | LIMIT | Execute at a specified price with GTC/IOC/FOK |
| | STOP_MARKET | Trigger a market order when stop price is reached |
| | TAKE_PROFIT_MARKET | Trigger a market order at take-profit price |
| **Order Sides** | BUY / SELL | Full support for both long and short positions |
| **CLI Commands** | `place-order` | Submit orders with flags (`--symbol`, `--side`, `--type`, etc.) |
| | `account` | View wallet balances, margin, and unrealised PnL |
| | `ping` | Lightweight connectivity check to the testnet |
| | `interactive` | Menu-driven session with step-by-step prompts |
| | `--version` | Display current bot version |
| **Validation** | Symbol | Regex-based format check (2–20 uppercase alphanumeric) |
| | Quantity | Positive, finite, above dust threshold (1e-8) |
| | Price | Required for LIMIT, sanity cap at 100M |
| | NaN/Inf guard | Rejects non-finite numeric inputs |
| **Error Handling** | 7 exception classes | `ValidationError`, `AuthenticationError`, `APIResponseError`, etc. |
| | Rate-limit detection | Auto-detects HTTP 429 / Binance code -1015 |
| | Rich error panels | User-friendly coloured error display |
| **Logging** | Dual handler | File (DEBUG+) + Console (WARNING+) |
| | Rotating files | 5 MB cap, 3 backups — no unbounded log growth |
| | Request timing | Every API call logged with round-trip ms |
| **Security** | Masked credentials | API keys shown as `abcd****mnop` in logs and CLI |
| | Placeholder detection | Prevents running with `.env.example` defaults |
| **UI** | ASCII banner | Styled startup banner with version |
| | Order preview | Yellow panel showing order details before submission |
| | Confirmation prompt | Interactive mode asks before submitting |
| | Session counter | Tracks orders placed per interactive session |

---

## 📁 Project Structure

```
trading_bot/
│
├── bot/                          # Core package
│   ├── __init__.py               # Package init + version (v1.0.0)
│   ├── client.py                 # Binance API gateway (testnet only)
│   ├── orders.py                 # OrderService + OrderResult dataclass
│   ├── validators.py             # Pure input validation functions
│   ├── config.py                 # Frozen Settings from .env
│   ├── exceptions.py             # 7-class exception hierarchy
│   ├── logging_config.py         # Rotating file + console handlers
│   └── utils.py                  # Banner, Rich helpers, display_order
│
├── logs/                         # Runtime logs (auto-created, gitignored)
│   └── trading_bot.log
│
├── cli.py                        # Typer CLI entry point (4 commands)
├── .env.example                  # Credential template
├── .gitignore                    # Git exclusions
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLI Layer (cli.py)                       │
│              Typer commands + Rich display + prompts             │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Service Layer (orders.py)                      │
│         Validate → Build params → Execute → Log result          │
│                                                                  │
│  ┌─────────────────┐    ┌──────────────┐    ┌───────────────┐   │
│  │  validators.py   │    │  OrderResult  │    │  OrderService │   │
│  │  (pure funcs)    │    │  (dataclass)  │    │  (facade)     │   │
│  └─────────────────┘    └──────────────┘    └───────────────┘   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Client Layer (client.py)                       │
│       python-binance SDK → Testnet API → Error translation      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              Binance Futures Testnet API (External)              │
│               https://testnet.binancefuture.com                  │
└─────────────────────────────────────────────────────────────────┘

Cross-cutting concerns:
  • config.py ──────── Frozen Settings dataclass from .env
  • exceptions.py ──── 7-class typed exception hierarchy
  • logging_config.py ─ Rotating file + stderr handlers
  • utils.py ────────── Rich panels, tables, formatters
```

---

## 🚀 Installation

### Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.11+ |
| pip | Latest |
| Binance Testnet Account | [Create free →](https://testnet.binancefuture.com) |

### Step-by-step Setup

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd trading_bot

# 2. Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## 🔑 Environment Setup

```bash
# 4. Copy the example env file
cp .env.example .env          # Linux / macOS
copy .env.example .env        # Windows

# 5. Open .env and add your Binance Futures Testnet credentials
```

**.env file contents:**

```env
BINANCE_API_KEY=your_actual_testnet_api_key
BINANCE_SECRET_KEY=your_actual_testnet_secret_key
BASE_URL=https://testnet.binancefuture.com
LOG_LEVEL=DEBUG
```

> 🔒 **Security**: The `.env` file is gitignored and never committed. API keys are displayed as masked values (`abcd****mnop`) in all logs and CLI output.

### How to Get Testnet API Keys

1. Visit [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Log in with your GitHub account
3. Navigate to **API Management** in the dashboard
4. Click **Create API** to generate a Key + Secret pair
5. Copy both values into your `.env` file

---

## 💻 Usage

### Check Version

```bash
python cli.py --version
```

### Test Connectivity

```bash
python cli.py ping
```

### Place a MARKET Order

```bash
python cli.py place-order \
  --symbol BTCUSDT \
  --side BUY \
  --type MARKET \
  --quantity 0.001
```

### Place a LIMIT Order

```bash
python cli.py place-order \
  --symbol BTCUSDT \
  --side SELL \
  --type LIMIT \
  --quantity 0.001 \
  --price 105000
```

### Place a STOP_MARKET Order

```bash
python cli.py place-order \
  --symbol ETHUSDT \
  --side SELL \
  --type STOP_MARKET \
  --quantity 0.05 \
  --stop-price 3200
```

### Place a TAKE_PROFIT_MARKET Order

```bash
python cli.py place-order \
  --symbol BTCUSDT \
  --side SELL \
  --type TAKE_PROFIT_MARKET \
  --quantity 0.001 \
  --stop-price 120000
```

### View Account Balances

```bash
python cli.py account
```

### Interactive Mode

```bash
python cli.py interactive
```

### Get Help

```bash
python cli.py --help
python cli.py place-order --help
```

---

## 📸 Example Terminal Output

### Startup Banner + MARKET Order

```
╭──────────────────────────────────────────────────────────────────╮
│                                                                  │
│  ╔══════════════════════════════════════════════════════════╗     │
│  ║   ____  _                              ____        _    ║     │
│  ║  | __ )(_)_ __   __ _ _ __   ___ ___ | __ )  ___ | |_  ║     │
│  ║  |  _ \| | '_ \ / _` | '_ \ / __/ _ \|  _ \ / _ \| __| ║     │
│  ║  | |_) | | | | | (_| | | | | (_|  __/| |_) | (_) | |_  ║     │
│  ║  |____/|_|_| |_|\__,_|_| |_|\___\___||____/ \___/ \__| ║     │
│  ║                                                          ║     │
│  ║        Futures Testnet Trading Bot  v1.0.0               ║     │
│  ╚══════════════════════════════════════════════════════════╝     │
│                     USDT-M Futures · Testnet Only                │
╰──────────────────────────────────────────────────────────────────╯

────────────────────────────────────────────────────────────
  ℹ  Preparing MARKET BUY order for BTCUSDT …
────────────────────────────────────────────────────────────

╭──── 📋  Order Preview ──────────────────────────────────────╮
│                                                              │
│  Symbol        BTCUSDT                                       │
│  Side          BUY                                           │
│  Type          MARKET                                        │
│  Quantity      0.001                                         │
│                                                              │
╰──────────────────────────────────────────────────────────────╯

  ✔  Connected to Binance Testnet (key: abcd****mnop)

╭──── ✔  Order Placed Successfully ───────────────────────────╮
│                                                              │
│  Order ID        8389765618968723536                         │
│  Symbol          BTCUSDT                                     │
│  Side            BUY ▲                                       │
│  Type            MARKET                                      │
│  Quantity        0.001                                       │
│  Price           MARKET                                      │
│  Stop Price      —                                           │
│  Status          FILLED                                      │
│  Executed Qty    0.001                                       │
│  Avg Price       103,250.50                                  │
│  Time            2026-05-09 08:48:12 UTC                     │
│                                                              │
╰──────────────────────────────────────────────────────────────╯

  ✔  Order submitted to Binance Futures Testnet.
────────────────────────────────────────────────────────────
```

### Account Balances

```
       💰  Account Balances
┌───┬───────┬────────────────┬────────────┬────────────────┐
│ # │ Asset │ Wallet Balance │  Available │ Unrealised PnL │
├───┼───────┼────────────────┼────────────┼────────────────┤
│ 1 │ USDT  │    10,000.0000 │  9,847.500 │      +12.5000  │
│ 2 │ BNB   │         1.0000 │      1.000 │       +0.0000  │
└───┴───────┴────────────────┴────────────┴────────────────┘

╭──── 📊  Account Summary ───────────────────────────────────╮
│                                                              │
│  Total Balance     10,001.0000 USDT                          │
│  Margin Balance     9,848.5000 USDT                          │
│  Unrealised PnL       +12.5000 USDT                         │
│                                                              │
╰──────────────────────────────────────────────────────────────╯

  ✔  Account information retrieved.
```

### Interactive Mode Menu

```
════════════════════════════════════════════════════════════
  📌  MAIN MENU
────────────────────────────────────────────────────────────
  [1]  📈  Place an order
  [2]  💰  View account balances
  [3]  🏓  Ping testnet
  [4]  🚪  Exit
════════════════════════════════════════════════════════════

  Select an option [1/2/3/4] (1):
```

### Error Output

```
╭──── ✖  Validation Error ───────────────────────────────────╮
│                                                              │
│  quantity: Quantity must be > 0, got -5.0.                   │
│                                                              │
╰──────────────────────────────────────────────────────────────╯
```

---

## 📋 Log File Output

Logs are written to `logs/trading_bot.log` with rotating files (5 MB max, 3 backups):

```
2026-05-09 08:48:10 | INFO     | trading_bot:setup_logging:131 — ════════════════════════════
  Logging initialised — file: logs/trading_bot.log | level: DEBUG | verbose: False
════════════════════════════════════════════════════════════
2026-05-09 08:48:10 | INFO     | trading_bot.bot.client:connect:123 — Connecting to Binance Futures Testnet → https://testnet.binancefuture.com (key: abcd****mnop)
2026-05-09 08:48:11 | INFO     | trading_bot.bot.client:connect:150 — Connected successfully — server time: 1746776891000 (2026-05-09 08:48:11 UTC)
2026-05-09 08:48:11 | INFO     | trading_bot.bot.orders:place_order:452 — Validated order → MARKET BUY BTCUSDT qty=0.001 price=None stop=None tif=None
2026-05-09 08:48:11 | DEBUG    | trading_bot.bot.orders:_build_params:537 — Built order params: {'symbol': 'BTCUSDT', 'side': 'BUY', 'type': 'MARKET', 'quantity': 0.001}
2026-05-09 08:48:11 | INFO     | trading_bot.bot.client:place_order:383 — Placing order → symbol=BTCUSDT side=BUY type=MARKET qty=0.001
2026-05-09 08:48:12 | INFO     | trading_bot.bot.client:place_order:399 — Order placed in 0.34s — orderId=8389765618968723536 status=FILLED executedQty=0.001 avgPrice=103250.50
2026-05-09 08:48:12 | INFO     | trading_bot.bot.orders:place_order:473 — Order #1 executed — FILLED BUY MARKET BTCUSDT qty=0.001 avg=103250.50 id=8389765618968723536 (342ms)
```

### Log Levels Used

| Level | When |
|---|---|
| `DEBUG` | Full API request/response payloads, param building, validator details |
| `INFO` | Connection events, order submissions, order results, account fetches |
| `WARNING` | Validation failures, ping failures, rate-limit warnings |
| `ERROR` | API errors, authentication failures, network errors |

---

## 🛡 Error Handling

Every failure mode maps to a specific exception class with a structured, user-friendly message:

```
TradingBotError                     ← base (catch-all)
├── ConfigurationError              ← .env missing, bad URL, invalid LOG_LEVEL
├── AuthenticationError             ← API key / secret rejected (-2014, -2015)
├── ValidationError                 ← bad symbol, side, quantity, price
│   └── .field, .reason, .value     ← detailed context for each failure
├── APIConnectionError              ← DNS, timeout, TLS, network errors
├── APIResponseError                ← Binance non-2xx response
│   └── .status_code, .binance_code, .binance_msg
├── RateLimitError                  ← HTTP 429 / code -1015
│   └── .retry_after
└── OrderError                      ← business failures (margin, lot size)
    └── .symbol
```

| Scenario | Exception | User Sees |
|---|---|---|
| Missing `.env` keys | `AuthenticationError` | Red panel with setup instructions |
| Invalid symbol format | `ValidationError` | Field name + reason in error panel |
| Binance rejects order | `APIResponseError` | HTTP status + Binance error code + message |
| Network timeout | `APIConnectionError` | Connection error with URL context |
| Rate limited | `RateLimitError` | Rate limit message with retry guidance |
| Unexpected crash | Caught at CLI level | Generic error panel + full traceback in log |

---

## ✅ Input Validation Rules

| Field | Rule | Example Failure |
|---|---|---|
| `symbol` | 2–20 uppercase alphanumeric | `"BTC@USDT"` → rejected |
| `side` | Must be `BUY` or `SELL` | `"HOLD"` → rejected |
| `type` | Must be `MARKET`, `LIMIT`, `STOP_MARKET`, or `TAKE_PROFIT_MARKET` | `"TRAILING"` → rejected |
| `quantity` | `> 0`, finite, above dust threshold (`1e-8`) | `0`, `-5`, `NaN` → rejected |
| `price` | Required for LIMIT, must be `> 0`, capped at `1e8` | `None` for LIMIT → rejected |
| `stop_price` | Required for STOP_MARKET / TAKE_PROFIT_MARKET | `None` for STOP_MARKET → rejected |
| `time_in_force` | `GTC`, `IOC`, or `FOK` (auto-defaults to `GTC` for LIMIT) | `"FOREVER"` → rejected |

---

## ⚙️ Configuration

All settings are loaded from environment variables via `.env`:

| Variable | Required | Default | Description |
|---|---|---|---|
| `BINANCE_API_KEY` | ✅ | — | Testnet API key |
| `BINANCE_SECRET_KEY` | ✅ | — | Testnet secret key |
| `BASE_URL` | ❌ | `https://testnet.binancefuture.com` | Testnet base URL |
| `LOG_LEVEL` | ❌ | `DEBUG` | File handler log level |

---

## 📐 Assumptions

1. **Testnet only** — The bot exclusively targets `testnet.binancefuture.com`. Production endpoints are never configured.
2. **Synchronous HTTP** — Uses `python-binance`'s synchronous client for simplicity and reliability.
3. **No database** — No persistent state; each CLI invocation is stateless (except log files).
4. **Symbol precision** — The testnet is lenient with precision; production would require exchange-info lookups for tick/lot sizes.
5. **Single-user** — Designed for local CLI use, not multi-tenant deployment.
6. **Virtual funds** — All testnet balances are virtual. No real money is involved.
7. **Regional API access** — Binance Testnet API key generation and live order execution may require additional account verification or may be restricted in certain regions/jurisdictions. The implementation (request signing, endpoint integration, validation flow, and logging) is fully production-ready and aligned with Binance Futures Testnet documentation regardless of regional availability.

---

## 🧰 Tech Stack

| Technology | Purpose |
|---|---|
| **Python 3.11+** | Core language with modern type hint support |
| **python-binance** | Binance API SDK (futures testnet client) |
| **Typer** | CLI framework with auto-generated help |
| **Rich** | Terminal UI: tables, panels, colours, prompts |
| **python-dotenv** | Secure `.env` file loading |
| **logging** | Standard library rotating file + console handlers |
| **dataclasses** | Frozen, slotted `Settings` and `OrderResult` |

---

## 🗂 Module Responsibilities

| Module | Lines | Responsibility |
|---|---|---|
| `cli.py` | 624 | Typer commands, Rich display, bootstrap, prompts |
| `bot/client.py` | 532 | API gateway, connection lifecycle, error translation |
| `bot/orders.py` | 585 | OrderService facade, OrderResult, convenience methods |
| `bot/validators.py` | 351 | 7 pure validation functions + bulk validator |
| `bot/exceptions.py` | 229 | 7-class typed exception hierarchy |
| `bot/config.py` | 212 | Frozen Settings, credential masking, URL validation |
| `bot/logging_config.py` | 186 | Rotating file handler, console handler, idempotent setup |
| `bot/utils.py` | 327 | Banner, formatters, Rich helpers, display_order |

**Total**: ~3,000+ lines of production-quality Python.

---

## 📄 License

This project is for **educational and demonstration purposes**. Built as a portfolio piece to showcase Python backend engineering, clean architecture, and quantitative systems design.

---

<p align="center">
  <em>Built with ❤️ using Python, Typer, Rich, and python-binance</em>
  <br/>
  <strong>⭐ Star this repo if you found it useful!</strong>
</p>
