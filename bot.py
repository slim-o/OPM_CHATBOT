import discord
from openai import OpenAI
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
#from motor.motor_asyncio import AsyncIOMotorClient

#import tiktoken
load_dotenv()
import os
gpt_version = "gpt-4.1"
#gpt_version = "ft:gpt-4.1-mini-2025-04-14:opminc:tradingassistant:BmJamUMX"

TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

openClient = OpenAI(
    api_key=OPENAI_API_KEY
)

myMongoClient = MongoClient(os.getenv('MONGO_CLIENT'))
#myMongoClient = AsyncIOMotorClient(os.getenv('MONGO_CLIENT'))

db = myMongoClient['OPM_AI_CHATBOT']
conversations = db['conversations']
threads = db['threads']
users = db['users']


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
            thread_id = str(message.channel.id)
            thread = message.channel
            thread_creator = message.channel.owner
            print(thread)
        '''else:
            print(2)
            thread_name = f"{message.author.display_name}'s GPT Session"
            thread = await message.channel.create_thread(
                name=thread_name, type=discord.ChannelType.public_thread, message=message
            )
            thread_creator = thread.owner 
            thread_id = thread.id
        '''

        print(3)
        convo = conversations.find_one({"thread_id": thread_id})
        history = [{"role": m["role"], "content": m["content"]} for m in convo["messages"]] if convo else []
        extra_history = convo["messages"] if convo else []
        print(3)
        # Add user message
        history.append({"role": "user", "content": message.content})
        extra_history.append({"role": "user", "user_name": message.author.name, "time_sent": str(datetime.utcnow()), "content": message.content})
        

        
        print(f'Message from {message.author}: {message.content}')
        
        '''if message.author != thread_creator:
            print(f"author: {message.author} thread creator: {thread_creator}")
            #await message.delete()
            await thread.send(f"You're not allowed to post in this thread.")
            return
        '''
        print(6)
        print(history)
        print()
        if message.attachments:
            #print(message)
            image_url = message.attachments[0].url
            await thread.send(f"{message.author.mention} Attachment received — processing now!")

            response = openClient.responses.create(
                model=gpt_version,
                input=[
                        {
                            "role": "user",
                            "content": [
                                { "type": "input_text", "text": message.content},
                                {
                                    "type": "input_image",
                                    "image_url": image_url 
                                }
                            ]
                        }
                    ]
            )
        else:
            response = openClient.responses.create(
                model=gpt_version,
                input=history,
                prompt={
                    "id": "pmpt_68531715d3508190a33b08d476c59a6c008e6e9899bed362",
                    "version": "9"
                }
            )
        print(7)
        
        

        history.append({"role": "assistant", "content": response.output_text})
        extra_history.append({"role": "assistant", "time_sent": datetime.now(), "content": response.output_text})

        print(8)
        usage = response.usage
        print(9)
        
        #print(thread_id)
        #print(history)

        #encoding = tiktoken.encoding_for_model("gpt-4o")
        #num_tokens = len(encoding.encode(history))
        #print(f"Estimated tokens: {num_tokens}")
        print('')
        print(f"📝 Input tokens: {usage.input_tokens}")
        print(f"📦 Cached tokens: {usage.input_tokens_details.cached_tokens}")
        print(f"💬 Output tokens: {usage.output_tokens}")
        print(f"📊 Total tokens: {usage.total_tokens}")
        print(10)

        # Upsert conversation
        conversations.update_one(
            {"thread_id": thread_id},
            {
                "$set": {"messages": history}
            },
            upsert=True
        )
        threads.update_one(
            {"thread_id": thread_id},
            {
                "$set": {"messages": extra_history},
                "$inc": {"total_tokens": usage.total_tokens}
            },
            upsert=True
        )
        # Ensure user exists
        users.update_one(
            {"user_id": message.author.id},
            {
                "$setOnInsert": {
                    "user_id": message.author.id,
                    "user_name": message.author.name,
                    "threads_opened": 0,
                    "total_tokens_used": 0,
                    "last_active": datetime.now()
                }
            },
            upsert=True
        )

        # Then increment tokens + update last_active
        users.update_one(
            {"user_id": message.author.id},
            {
                "$inc": {"total_tokens_used": usage.total_tokens},
                "$set": {"last_active": datetime.now()}
            }
        )

        await send_long_message(thread, response.output_text)


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(TOKEN)