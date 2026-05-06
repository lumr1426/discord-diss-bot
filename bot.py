import os
import discord
import anthropic
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_KEY"))


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if not message.content.startswith("!디스"):
        return

    if not message.mentions:
        await message.channel.send("디스할 사람을 멘션해줘! 예: `!디스 @친구`")
        return

    target = message.mentions[0]

    history = []
    async for msg in message.channel.history(limit=30):
        if msg.author == target and msg.content:
            history.append(msg.content)

    if not history:
        await message.channel.send(f"{target.display_name}은 최근에 아무 말도 안 했네. 디스할 게 없어!")
        return

    recent_messages = "\n".join(reversed(history[:10]))

    prompt = f"""너는 친구들끼리 장난으로 서로 디스하는 디스코드 봇이야.
아래는 {target.display_name}이 최근에 한 말들이야:

{recent_messages}

이걸 바탕으로 {target.display_name}을 재미있고 창의적으로 디스해줘.
친구들끼리 하는 장난스러운 톤으로, 한국어로만 답해줘. 2-3문장으로 끝내줘."""

    response = claude.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )

    await message.channel.send(response.content[0].text)


client.run(os.getenv("DISCORD_TOKEN"))
