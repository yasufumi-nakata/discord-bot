import os
import discord
from discord.ext import commands
import random
import asyncio
import functools
import typing
from dotenv import load_dotenv

import config
import llm_service

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Decorator to run blocking jobs in a thread
def to_thread(func: typing.Callable) -> typing.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper

@to_thread
def get_summary(paper):
    """Generate detailed 5-point summary and APA citation using local LLM."""
    system_prompt = "あなたは優秀な研究助手です。論文の内容を日本語で分かりやすく、指定されたフォーマットで正確に要約・翻訳してください。"

    user_prompt = f"""与えられた論文の要点を以下のフォーマットで日本語で出力してください。タイトルは**で囲み，本文は``で囲んでください。
また、提供されたメタデータを使用してAPA形式の引用（翻訳せず英語のまま）を作成してください。

【メタデータ】
タイトル: {paper['title']}
著者: {paper['authors']}
公開日: {paper['published']}
DOI: {paper['doi']}
URL: {paper['url']}
要約 (Abstract): {paper['summary']}

出力フォーマット:
**タイトルの日本語訳**
``・どんなもの?``
（回答）
``・先行研究と比べてどこがすごい?``
（回答）
``・技術や手法のキモはどこ?``
（回答）
``・どうやって有効だと検証した?``
（回答）
``・議論はある?``
（回答）

【APA引用】
（ここにAPA形式の引用文。DOIやURLも含めること。この項目のみ英語のままで出力してください）
"""
    return llm_service.get_detailed_summary_with_custom_prompt(paper, system_prompt, user_prompt)

# Bot Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    print(f'Scopus Bot logged in as {bot.user}')

@bot.command(name='query')
async def query(ctx, *args):
    """Replicates sample/dbot.py: Search Scopus and summarize 1 random paper."""
    if not args:
        await ctx.send("使用法: `$query <検索ワード>`")
        return

    query_arg = ' '.join(args)
    print(f"Scopus query: {query_arg}")
    await ctx.send(f"Scopusで「{query_arg}」を検索しています...")

    try:
        # Fetch status
        papers = llm_service.fetch_elsevier(config.ELSEVIER_API_KEY, query_arg, count=25)

        if not papers:
            await ctx.send(f"「{query_arg}」に一致する論文は見つかりませんでした。")
            return

        # Select 1 paper randomly
        paper = random.choice(papers)
        print(f"Processing Scopus paper: {paper['title']}")
        await ctx.send(f"Processing Scopus result: {paper['title']}")

        try:
            summary = await get_summary(paper)
            message = f"**{query_arg}の論文です！**\n"
            message += f"発行日: {paper['published']}\n{paper['url']}\n\n{summary}"

            # Length check
            if len(message) > 2000:
                for part in [message[i:i+1900] for i in range(0, len(message), 1900)]:
                    await ctx.send(part)
            else:
                await ctx.send(message)
        except Exception as e:
            print(f"Error processing paper: {e}")
            await ctx.send(f"論文の処理中にエラーが発生しました。")

    except Exception as e:
        await ctx.send(f"Scopus検索エラー: {e}")

if __name__ == "__main__":
    if DISCORD_TOKEN:
        bot.run(DISCORD_TOKEN)
    else:
        print("DISCORD_TOKEN not found.")
