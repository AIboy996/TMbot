from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    filters,
    MessageHandler,
)
from telegram import Update
import re
import os

from tmdb import get_movie_info, get_tv_info

TG_TOKEN = os.getenv("tg_token")


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="我不会这个哦~"
    )


async def watched(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    message_id = update.effective_message.message_id
    effective_message = update.effective_message.text
    res = re.match(r"最近在看 (?P<tmdbid>\S*)( (?P<season>\S*))?", effective_message)
    query_d = res.groupdict()
    tmdbid = query_d.get("tmdbid")
    season = query_d.get("season")
    if season is None:
        try:
            info = get_movie_info(tmdbid)
            effective_message = (
                f"最近在看：{info['title']} ({info['original_title']})\n\n"
                if info["original_title"] != info["title"]
                else f"最近在看：{info['title']}\n\n"
            )
            effective_message += f"上映日期: {info['release_date']}\n\n"
            effective_message += f"类型: {', '.join(info['genres'])}\n\n"
            effective_message += (
                f"简介：{info['overview']}"
                if len(info["overview"]) < 100
                else f"简介：{info['overview'][:100]}..."
            )
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=info["poster_path"],
                caption=effective_message,
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
            effective_message = (
                f"最近在看：{info['title']} ({info['original_title']})\n\n"
                if info["original_title"] != info["title"]
                else f"最近在看：{info['title']}\n\n"
            )
            effective_message += (
                f"第{info['season']}季 共{info['number_of_episodes']}集\n\n"
            )
            effective_message += f"开播日期: {info['release_date']}\n\n"
            effective_message += f"状态: {info['status']}\n\n"
            effective_message += f"类型: {', '.join(info['genres'])}\n\n"
            effective_message += (
                f"简介：{info['overview']}"
                if len(info["overview"]) < 100
                else f"简介：{info['overview'][:100]}..."
            )
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=info["poster_path"],
                caption=effective_message,
            )
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception as e:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"找不到这个电视剧哦~ \n\n{repr(e)}",
            )


unknown_handler = MessageHandler(filters.COMMAND, unknown)
watched_reg = filters.Regex("最近在看 (.*?)")
watched_handler = MessageHandler(watched_reg, watched)

if __name__ == "__main__":
    application = ApplicationBuilder().token(TG_TOKEN).build()
    application.add_handler(watched_handler)
    application.add_handler(unknown_handler)
    # run!
    application.run_polling()
