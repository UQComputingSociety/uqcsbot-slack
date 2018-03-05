from uqcsbot import bot, Command
import requests

API_URL = r"http://api.wolframalpha.com/v2/query?appid=UVKV2V-5XW2TETT69"

@bot.on_command("wolfram")
async def handle_wolfram(command: Command):
    search_query = command.arg
    http_response = await bot.run_async(requests.get, API_URL, params={'input': search_query})

    bot.post_message(command.channel, http_response.content)
