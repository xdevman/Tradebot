from aiogram.types import InlineKeyboardButton,InlineKeyboardMarkup



def confirm_keyboard(data) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Confirm", callback_data=f"{data}:confirm"),
        InlineKeyboardButton(text="❌ Cancel",  callback_data=f"{data}:cancel"),
    ]])