import discord
from discord.ext import commands

# ===== CONFIGURATION =====
TOKEN = "YOUR_BOT_TOKEN_HERE"
GUILD_ID = 123456789012345678  # Your server ID
CHANNEL_ID = 123456789012345678  # Channel where reaction message lives
MESSAGE_ID = 123456789012345678  # The message users react to

# Mapping: emoji -> role_name (or role_id)
ROLE_MAPPING = {
    "🍎": "Apple Lover",
    "🍕": "Pizza Fan",
    "🎮": "Gamer",
    "📚": "Reader"
}
# =========================

intents = discord.Intents.default()
intents.members = True  # Required to assign roles
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    # Fetch and store the target message at startup
    channel = bot.get_channel(CHANNEL_ID)
    try:
        global TARGET_MESSAGE
        TARGET_MESSAGE = await channel.fetch_message(MESSAGE_ID)
        print(f"🎯 Watching message {MESSAGE_ID} for reactions")
    except Exception as e:
        print(f"❌ Could not fetch message: {e}")

@bot.event
async def on_raw_reaction_add(payload):
    """Assign role when a user adds a reaction"""
    await handle_reaction(payload, add=True)

@bot.event
async def on_raw_reaction_remove(payload):
    """Remove role when a user removes a reaction"""
    await handle_reaction(payload, add=False)

async def handle_reaction(payload, add: bool):
    # Ignore the bot's own reactions
    if payload.user_id == bot.user.id:
        return

    # Check if this is the right message
    if payload.message_id != MESSAGE_ID:
        return

    guild = bot.get_guild(payload.guild_id)
    if guild is None:
        return

    member = guild.get_member(payload.user_id)
    if member is None:
        return

    # Convert emoji to string (handles custom emojis too)
    emoji = str(payload.emoji)

    if emoji not in ROLE_MAPPING:
        return  # Unmapped emoji

    role_name = ROLE_MAPPING[emoji]
    role = discord.utils.get(guild.roles, name=role_name)

    if role is None:
        print(f"⚠️ Role '{role_name}' not found in server")
        return

    try:
        if add:
            await member.add_roles(role)
            print(f"➕ Added {role.name} to {member.name}")
        else:
            await member.remove_roles(role)
            print(f"➖ Removed {role.name} from {member.name}")
    except discord.Forbidden:
        print(f"❌ Bot lacks permission to manage {role.name}")
    except Exception as e:
        print(f"❌ Error: {e}")

# Optional: Command to set up the reaction message
@bot.command()
@commands.has_permissions(administrator=True)
async def setup_roles(ctx):
    """Sends a message with reaction options (run once)"""
    description = "**React to get your role:**\n"
    for emoji, role_name in ROLE_MAPPING.items():
        description += f"\n{emoji} → `{role_name}`"

    embed = discord.Embed(
        title="🎭 Choose Your Role",
        description=description,
        color=discord.Color.blue()
    )
    msg = await ctx.send(embed=embed)
    
    # Add all reaction emojis
    for emoji in ROLE_MAPPING.keys():
        await msg.add_reaction(emoji)
    
    await ctx.send(f"✅ Reaction role message created! Message ID: `{msg.id}`")
    print(f"📝 Save this MESSAGE_ID: {msg.id}")

if __name__ == "__main__":
    bot.run(TOKEN)
