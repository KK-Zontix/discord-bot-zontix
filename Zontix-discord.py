import discord
from discord.ext import commands

# ===== CONFIGURATION =====
TOKEN = "YOUR_BOT_TOKEN_HERE"
GUILD_ID = 123456789012345678  # Your server ID
CHANNEL_ID = 123456789012345678  # Channel where reaction message lives
MESSAGE_ID = 123456789012345678  # The message users react to

# Mapping: emoji -> role_name (or role_id)
ROLE_MAPPING = {
    "<:CCCC_Wolves_:1514794816029065436>": "CCCC-Wolves",
    "<:CMN_Ravens:1514794872119234581>": "CMN-Ravens",
    "<:FPCC_buffalo_chasers:1514794986284257490>": "FPCC-buffalo-chasers",
    "<:HINU:1514795056463089665>": "HINU",
    "<:OLC_bravehearts:1514795124213678131>": "OLC-bravehearts",
    "<:RLNC_Migizi:1514795178295169104>": "RLNC-Migizi",
    "<:SBC_Suns:1514795283236782230>": "SBC-Suns",
    "<:SCC_BearPaws:1514795355185741984>": "SCC-BearPaws",
    "<:TOCC_Jegos:1514795474983456910>": "TOCC-Jegos",
    "<:TMC_Mikinocks:1514795425679540354>": "TMC-Mikinocks",
    "🤝": "Supporters"
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



@bot.command()
@commands.has_permissions(administrator=True)
async def rules(ctx):
    embed = discord.Embed(
        title="Server Rules & Code of Conduct",
        description="## 1. Respect the Circle\n"
                    "• **Honor All Nations:** Discrimination, hate speech, or disrespect regarding tribal affiliations, race, gender, or identity will result in an immediate ban.\n"
                    "• **Keep It Friendly:** No toxicity, personal attacks, or targeted harassment.\n"
                    "• **Respect the Admins:** Follow directions given by server moderators and tournament organizers.\n\n"
                    "---\n\n"
                    "## 2. Competitive Integrity\n"
                    "• **Play Fair:** Cheating, hacking, smurfing, or exploiting bugs in competitive matches is strictly forbidden.\n"
                    "• **Good Sportsmanship:** Win with humility; lose with grace. No excessive trash-talking, toxic behavior, or 'GG EZ' spamming.\n"
                    "• **Represent Well:** Remember that you are representing your specific Tribal College or University (TCU) when you play.\n\n"
                    "---\n\n"
                    "## 3. Content & Chat Guidelines\n"
                    "• **Keep it Clean:** This is a school-affiliated space; keep main text and voice channels PG-13/SFW (Safe For Work).\n"
                    "• **No Spamming:** Avoid flooding chat with walls of text, excessive emojis, or irrelevant links.\n"
                    "• **No Self-Promo:** Do not advertise external streams, servers, or products without moderator approval.\n\n"
                    "---\n\n"
                    "## 4. Safety & Privacy\n"
                    "• **Protect Identity:** Do not share anyone's real-life personal information (doxxing).\n"
                    "• **Report Issues:** Use the reporting channel or DM a moderator if you witness toxic behavior or rule-breaking.\n\n"
                    "---\n\n",
        color=discord.Color.blue()  # 0x3498db
    )
    embed.set_footer(text="Last Updated: June 2026")
    
    await ctx.send(embed=embed)

if __name__ == "__main__":
    bot.run(TOKEN)

