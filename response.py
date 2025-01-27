from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    filters,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
)
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputMedia
from requests import Session
import re
import os

from tmdb import get_movie_info, get_tv_info, parse_movie_info, parse_tv_info

TG_TOKEN = os.getenv("tg_token")


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="我不会这个哦~"
    )


async def watched(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    message_id = update.effective_message.message_id
    effective_message = update.effective_message.text
    print(f"received message: {effective_message}")
    res = re.match(r"最近在看 (?P<tmdbid>\S*)( (?P<season>\S*))?", effective_message)
    query_d = res.groupdict()
    tmdbid = query_d.get("tmdbid")
    season = query_d.get("season")
    if season is None:
        try:
            info = get_movie_info(tmdbid)
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=info["poster_path"],
                caption="最近在看：" + parse_movie_info(info),
            )
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception as e:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"找不到这个电影哦~ \n\n{repr(e)}",
            )
    else:
        try:
            info = get_tv_info(tmdbid, season=int(season))
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=info["poster_path"],
                caption="最近在看：" + parse_tv_info(info),
            )
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception as e:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"找不到这个电视剧哦~ \n\n{repr(e)}",
            )


def search_request(query: str, page=1):
    TMDB_TOKEN = os.getenv("tmdb_token")
    s = Session()
    headers = {"accept": "application/json", "Authorization": f"Bearer {TMDB_TOKEN}"}
    s.headers.update(headers)
    url = f"https://api.themoviedb.org/3/search/multi?query={query}&include_adult=false&language=zh-CN&page={page}"
    search_res = s.get(url).json().get("results")
    return search_res


def parse_button(search_res: list[dict], query: str, more=True):
    buttons = [
        [
            InlineKeyboardButton(
                text=f"{r.get('title', r.get('name'))} ({r.get('original_title', r.get('original_name'))}, {r.get('media_type')}-{r.get('id')})",
                callback_data=f"{r.get('media_type')}-{r.get('id')}",
            )
        ]
        for r in search_res
        if r.get("media_type") in ["movie", "tv"]
    ] + [
        [
            (
                InlineKeyboardButton(text="更多", callback_data=("more: " + query))
                if more
                else InlineKeyboardButton(text="返回", callback_data=("less: " + query))
            ),
            InlineKeyboardButton(text="OK", callback_data="ok"),
            InlineKeyboardButton(text="取消", callback_data="cancel"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_message = update.effective_message.text
    query = " ".join(context.args)
    print(f"received message: {effective_message}")
    search_res = search_request(query, page=1)
    if search_res is None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="找不到这个电影哦~"
        )
    else:
        button_markup = parse_button(search_res, query)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=effective_message,
            reply_markup=button_markup,
        )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "cancel":
        await query.answer()
        await query.delete_message()
    elif query.data == "ok":
        await query.answer()
        if update.effective_message.text is not None:
            await query.edit_message_text(update.effective_message.text)
        else:
            await query.edit_message_caption(caption=query.message.caption)
    elif query.data.startswith("more"):
        search_string = query.data.split(": ")[1]
        await query.answer()
        button_markup = parse_button(
            search_request(query=search_string, page=2), query=search_string, more=False
        )
        if update.effective_message.text is not None:
            await query.edit_message_text(
                text=f"/s {search_string}",
                reply_markup=button_markup,
            )
        else:
            await query.edit_message_caption(
                caption=f"/s {search_string}",
                reply_markup=button_markup,
            )
    elif query.data.startswith("less"):
        search_string = query.data.split(": ")[1]
        await query.answer()
        button_markup = parse_button(
            search_request(query=search_string, page=1), query=search_string, more=True
        )
        await query.edit_message_caption(
            text=f"/s {search_string}",
            reply_markup=button_markup,
        )
    else:
        media_type, tmdbid = query.data.split("-")
        await query.answer()
        info = get_movie_info(tmdbid) if media_type == "movie" else get_tv_info(tmdbid)
        await query.edit_message_media(
            media=InputMedia(
                media_type="photo",
                media=info.get("poster_path"),
                caption=(
                    parse_movie_info(get_movie_info(tmdbid))
                    if media_type == "movie"
                    else parse_tv_info(get_tv_info(tmdbid))
                )
                + "\n\n"
                + query.data,
            ),
            reply_markup=update.effective_message.reply_markup,
        )


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "你好~我是TMbot"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


hello_handler = CommandHandler("start", hello)
search_handler = CommandHandler("s", search)
unknown_handler = MessageHandler(filters.COMMAND, unknown)
watched_reg = filters.Regex("最近在看 (.*?)")
watched_handler = MessageHandler(watched_reg, watched)

if __name__ == "__main__":
    application = ApplicationBuilder().token(TG_TOKEN).build()
    application.add_handler(search_handler)
    application.add_handler(hello_handler)
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(watched_handler)
    application.add_handler(unknown_handler)
    # run!
    application.run_polling()
