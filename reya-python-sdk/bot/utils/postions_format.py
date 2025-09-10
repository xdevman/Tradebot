

def format_positions(positions: list[dict]) -> str:
    return "\n\n".join(format_position(p) for p in positions)

def format_position(pos: dict) -> str:
    side = "long" if pos["side"] == "B" else "short"
    return (
        f"📌 Symbol: {pos['symbol']}\n"
        f"📈 Side: {side}\n"
        f"🔢 Quantity: {pos['qty']}\n"
        f"💵 Entry Price: {pos['avgEntryPrice']}"
    )

def format_positions(positions_data: list[dict]) -> str:
    return "\n\n".join(format_position(pos) for pos in positions_data)