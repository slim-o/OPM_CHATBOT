import discord
from openai import OpenAI

from dotenv import load_dotenv
load_dotenv()
import os
TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

openClient = OpenAI(
    api_key=OPENAI_API_KEY
)

CHANNEL_IDS = [1294435170799325217, 1294435279175684096, 1294435458402750564, 1294435561024786503, 1294432399622672406, 1294432321063227492, 1294432215123497070]

async def send_long_message(channel, text):
    max_length = 2000
    chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
    for chunk in chunks:
        await channel.send(chunk)

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'✅ Bot is online as {self.user}!')

    async def on_message(self, message):
        if message.author == client.user:
            return
        #print(message.channel)
        
        if message.channel.id in CHANNEL_IDS:
            return

        if message.channel.type == discord.ChannelType.public_thread:
            print(1)
            thread = message.channel
            thread_creator = message.channel.owner
            print(thread_creator)
        else:
            print(2)
            thread_name = f"{message.author.display_name}'s GPT Session"
            thread = await message.channel.create_thread(
                name=thread_name, type=discord.ChannelType.public_thread, message=message
            )
            thread_creator = self.user  
        

        if message.attachments:
            await thread.send(f"{message.author.mention} Attachment received — processing coming soon!")
            return

        print(f'Message from {message.author}: {message.content}')
        
        '''if message.author != thread_creator:
            #await message.delete()
            await thread.send(f"You're not allowed to post in this thread.")
            return
        '''
        response = openClient.responses.create(
            model="gpt-4.1",
            input=message.content,
            prompt={
                "id": "pmpt_68531715d3508190a33b08d476c59a6c008e6e9899bed362",
                "version": "3"
            }
        )

        await send_long_message(thread, response.output_text)


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(TOKEN)