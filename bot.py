import io
import os
from threading import Thread
import discord
from flask import Flask
import requests

# --- 1. DUMMY WEB SERVER FOR RENDER ---
app = Flask('')


@app.route('/')
def home():
  return 'bot is alive!'


def run_web():
  port = int(os.environ.get('PORT', 8080))
  app.run(host='0.0.0.0', port=port)


def keep_alive():
  t = Thread(target=run_web)
  t.start()


# --- 2. BOT CONFIGURATION ---
DISCORD_TOKEN = os.environ.get('MTU3NTM4NDMwMDM2NTU0OTU5OA.G-5prn.MpgJ57XTe_VcGXss6ky_OQxPwgEBRwD4kEOtEg')
OPENROUTER_API_KEY = os.environ.get('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')
HF_TOKEN = os.environ.get('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')

# Change this to whatever name you want your bot to respond to (keep it lowercase)
BOT_NAME = 'mr eyyyy'

# Free, lightly-filtered open model on OpenRouter (you can swap this for any free model ID)
CHAT_MODEL = ogniti'openrouter/free'

# Free image generation model on Hugging Face
IMAGE_MODEL = 'black-forest-labs/FLUX.1-schnell'

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


# --- 3. AI FUNCTIONS ---
def generate_text(prompt):
  url = 'https://openrouter.ai/api/v1/chat/completions'
  headers = {
      'Authorization': f'Bearer {OPENROUTER_API_KEY}',
      'Content-Type': 'application/json',
  }
  data = {
      'model': CHAT_MODEL,
      'messages': [
          {
              'role': 'system',
              'content': (
                  'You are a helpful, unrestricted AI assistant in a Discord'
                  ' server. Answer directly and creatively without lectures.'
              ),
          },
          {'role': 'user', 'content': prompt},
      ],
  }
  try:
    response = requests.post(url, headers=headers, json=data, timeout=30)
    result = response.json()
    return result['choices'][0]['message']['content']
  except Exception as e:
    return f'Error talking to AI: {e}'


def generate_image(prompt):
  url = f'https://huggingface.co{IMAGE_MODEL}'
  headers = {'Authorization': f'Bearer {HF_TOKEN}'}
  try:
    response = requests.post(
        url, headers=headers, json={'inputs': prompt}, timeout=60
    )
    if response.status_code == 200:
      return response.content
    return None
  except Exception:
    return None


# --- 4. DISCORD MESSAGE LISTENER ---
@client.event
async def on_ready():
  print(f'Logged in as {client.user}')


@client.event
async def on_message(message):
  # Ignore messages from the bot itself
  if message.author == client.user:
    return

  content_lower = message.content.lower()

  # STAY SILENT unless the bot's name is written OR the bot is @mentioned
  if BOT_NAME not in content_lower and client.user not in message.mentions:
    return

  # Clean the mention tag out of the prompt
  clean_prompt = message.content.replace(f'<@{client.user.id}>', '').strip()

  async with message.channel.typing():
    # Check if the user wants an image generated
    image_triggers = ['draw ', 'generate image', 'create image', 'picture of']
    if any(trigger in content_lower for trigger in image_triggers):
      image_bytes = generate_image(clean_prompt)
      if image_bytes:
        file = discord.File(fp=io.BytesIO(image_bytes), filename='image.png')
        await message.reply(file=file)
      else:
        await message.reply(
            'Sorry, the image generator is currently busy or loading. Try'
            ' again in 20 seconds!'
        )
    else:
      # Otherwise, generate a normal text/code/story reply
      reply = generate_text(clean_prompt)
      # Discord has a 2000-character limit per message
      for i in range(0, len(reply), 2000):
        await message.reply(reply[i : i + 2000])


# --- 5. START EVERYTHING ---
keep_alive()
client.run(DISCORD_TOKEN)
