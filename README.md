# Telegram Trade Bot

A Python-based Telegram bot for trading on Reya Network, using the included [reya-python-sdk](https://github.com/Reya-Labs/reya-python-sdk). Supports placing long and short trades, closing positions, and GTC limit orders. All commands are **admin-only**.

---

## Features

- Open **long** positions  
- Open **short** positions  
- **Close active positions**  
- Place **GTC limit orders** (long/short)  
- Admin-only commands for security

---

## Commands

- `/long <ticker> <amount>` – Open a long position  
- `/short <ticker> <amount>` – Open a short position  
- `/limit <ticker> <side> <amount> <price>` – Open a limit order (GTC)  
- `/close <ticker>` – Close an active position  

### Examples

```text
/long SOL 0.5       → Open a long position of 0.5 SOL
/short BTC 1        → Open a short position of 1 BTC
/close SOL          → Close the active SOL position
/limit ETH short 2  → Place a GTC limit order for 2 ETH
```
## Installation

1. **Clone the repository and navigate to the SDK folder:**

```bash
git clone https://github.com/xdevman/Tradebot.git
cd Tradebot/reya-python-sdk
```
2. Create a virtual environment and install dependencies using Poetry:

```bash
poetry install
```

3. Activate the virtual environment:

```bash
source $(poetry env info --path)/bin/activate
```
4. Set up your `.env` file and Fill in the following values in .env:
```bash
PRIVATE_KEY=your_private_key_here\n
ACCOUNT_ID=your_account_id_here
WALLET_ADDRESS=your_wallet_address_here
BOT_TOKEN=your_telegram_bot_token_here
TID=your_telegram_userid_here
```
5. Run the bot:
```bash
python -m bot.main
```

## Finding Your Account ID

Before setting up your environment, you'll need to find your Reya account ID:

1. Replace `<your_wallet_address>` with your Ethereum wallet address in this URL:
   ```
   https://api.reya.xyz/v2/wallet/<your_wallet_address>/accounts
   ```

2. Open the URL in your browser. You'll see a JSON response containing your account information.

3. Note the `account_id` field from the response. This is your account ID needed for the environment setup.

For example, the response might look like:
```json
[
  {
    "account_id": "123456",
    "name": "Margin Account 1",
    "status": "OPEN",
    "updated_timestamp_ms": "1753799229000",
    "source": "reya"
  }
]
```
## Notes

- Only the Telegram user ID set in the `TID` variable in your `.env` file can execute commands. You can find your user ID using this bot: t.me/userinfobot
- Amounts are in token size (not USD).  
- Limit orders are **Good-Til-Cancelled (GTC)**.


