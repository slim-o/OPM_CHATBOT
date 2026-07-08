import discord
from discord.ui import Modal, TextInput, View, Button
from openai import OpenAI
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
#from func_general_functions import *
#from variables_general import *
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

message_text = """**🏆 OPM Squid Games – Trading Challenge is LIVE! 🦑**  

Think you have what it takes to survive the markets?  
From **now until Saturday**, compete in the **OPM Squid Games** and prove your trading skills!  

**📋 How It Works:**  \n
1️⃣ Start with a **£10,000 Vantage demo account** → [Get One Here](<https://www.vantagemarkets.com/open-demo-account/?affid=MTg5MDAxNA==>)

2️⃣ **Goal:** Hit **+10% profit** without exceeding **5% max drawdown** over at least **3 days of trading**

3️⃣ First to complete the challenge wins! 🏅  

**🎁 Prizes Include:**  \n
💰 Real **funded trading accounts**  
🤖 Exclusive **access to OPM-AI**  
🎉 Other special rewards for top performers  

**📢 Rules:**  \n
- Must use a **fresh [demo account](<https://www.vantagemarkets.com/open-demo-account/?affid=MTg5MDAxNA==>)**  
- Must post **daily trade updates & setups** in the `#📈trade-talk` channel  
- Breaking rules or exceeding drawdown = disqualification  
- **[Read the Full Terms & Conditions](<https://opiumfx.notion.site/OPM-Squid-Games-Terms-Conditions-f14232c126184f2c97a173004fa2ddd3>)**  

**🕒 Deadline:**  \n
Complete your target by **Saturday**  
🏆 Winners announced **live** at our stand!  

**⬇️ Click the button below to register and join the challenge!**"""

myMongoClient = MongoClient(os.getenv('MONGO_CLIENT'))
#myMongoClient = AsyncIOMotorClient(os.getenv('MONGO_CLIENT'))

db = myMongoClient['OPM_AI_CHATBOT']
conversations = db['conversations']
threads = db['threads']
users = db['users']


CHANNEL_IDS = [1294435170799325217, 1294435279175684096, 1294435458402750564, 1294435561024786503, 1294432399622672406, 1294432321063227492, 1294432215123497070]
#TARGET_CHANNEL_ID = 1405554556695347250  # Channel with the reaction message
#TARGET_MESSAGE_ID = 1405919131911327774  # The message ID to watch

TARGET_CHANNEL_ID = 1294435170799325217 # trade-talk
TARGET_MESSAGE_ID = 1406441888520605809
ROLE_ID = 1405561759779127426 # SQUID ID

class RegistrationModal(Modal, title="OPM Squid Games Registration"):
    name = TextInput(label="Name", placeholder="John Smith", required=True)
    email = TextInput(label="Email Address", placeholder="you@example.com", required=True)
    account_number = TextInput(label="Vantage Demo Account Number", placeholder="12345678", required=True)
    account_pass = TextInput(label="Vantage Demo Account Password (Demo Only)", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        discord_username = f"{interaction.user.name}#{interaction.user.discriminator}"
        discord_id = interaction.user.id

        #reset_and_initialize_account(terminal_path, self.account_number, self.account_pass, "C:/Users/ikema/Documents/CODE/OPM_CHATBOT/accounts.dat")
        # Save to file (or DB / Google Sheets)
        with open("registrations.csv", "a") as f:
            f.write(f"{self.name.value},{self.email.value},{discord_username},{discord_id},{self.account_number.value},{self.account_pass.value}\n")

        role = interaction.guild.get_role(ROLE_ID)  # ROLE_ID = your Contestant role ID
        if role:
            await interaction.user.add_roles(role)

        await interaction.response.send_message("✅ Registered successfully!", ephemeral=True)
        """
        try:
            success = reset_and_initialize_account(terminal_path, self.account_number, self.account_pass, "C:/Users/ikema/Documents/CODE/OPM_CHATBOT/accounts.dat")
            time.sleep(15)
            if success:

                # Save to file (or DB / Google Sheets)
                with open("registrations.csv", "a") as f:
                    f.write(f"{self.name.value},{self.email.value},{discord_username},{discord_id},{self.account_number.value},{self.account_pass.value}\n")

                role = interaction.guild.get_role(ROLE_ID)  # ROLE_ID = your Contestant role ID
                if role:
                    await interaction.user.add_roles(role)

                await interaction.response.send_message("✅ Registered successfully!", ephemeral=True)
        except Exception as e:
            # Construct and send an error message
            await interaction.response.send_message(
                f"❌ Failed to initialize account {self.account_number}.\nError: {str(e)}",
                ephemeral=True
            )"""
            

class RegisterView(View):
    def __init__(self):
        super().__init__(timeout=None)  # Persistent view

        button = Button(label="Register Now", style=discord.ButtonStyle.green)

        async def button_callback(interaction: discord.Interaction):
            await interaction.response.send_modal(RegistrationModal())

        button.callback = button_callback
        self.add_item(button)


async def send_long_message(channel, text):
    max_length = 2000
    chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
    for chunk in chunks:
        await channel.send(chunk)

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'✅ Bot is online as {self.user}!')
        

        # Fetch the channel and message
        channel = self.get_channel(TARGET_CHANNEL_ID)
        message = await channel.fetch_message(TARGET_MESSAGE_ID)
        #await send_long_message(channel, message_text)


        # Edit message to add the button
        await message.edit(content=message_text ,view=RegisterView())

        print("✅ Button added to existing message")


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
intents.reactions = True
intents.members = True

client = MyClient(intents=intents)
client.run(TOKEN)