import discord
from discord.ext import commands
from twitchAPI.twitch import Twitch 
from discord.ext import task 

##############################################
#                 GLOBALS                    #
##############################################


STREAMERS = []

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



##############################################
#                  ROLES                     #
##############################################
@bot.event
async def on_raw_reaction_add(payload):
    """Assign role when a user adds a reaction"""
    # Debug: Print what Discord actually sends
    if payload.emoji.is_custom_emoji():
        emoji_str = f"<:{payload.emoji.name}:{payload.emoji.id}>"
        print(f"Custom emoji received - Name: '{payload.emoji.name}', ID: {payload.emoji.id}")
        print(f"Formatted as: {emoji_str}")
    else:
        emoji_str = str(payload.emoji)
        print(f"Standard emoji received - {emoji_str}")
    
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

    # Convert emoji to the format used in ROLE_MAPPING
    if payload.emoji.is_custom_emoji():
        # Format custom emoji as <:name:id>
        emoji_key = f"<:{payload.emoji.name}:{payload.emoji.id}>"
    else:
        emoji_key = str(payload.emoji)

    print(f"Looking for emoji key: '{emoji_key}'")
    print(f"Available keys: {list(ROLE_MAPPING.keys())}")

    if emoji_key not in ROLE_MAPPING:
        print(f"⚠️ Emoji '{emoji_key}' not found in mapping!")
        return

    role_name = ROLE_MAPPING[emoji_key]
    role = discord.utils.get(guild.roles, name=role_name)

    if role is None:
        print(f"⚠️ Role '{role_name}' not found in server")
        # List available roles for debugging
        available_roles = [r.name for r in guild.roles]
        print(f"Available roles: {available_roles}")
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
        print(f"   Make sure: 1) Bot role is above target role, 2) Bot has 'Manage Roles' permission")
    except Exception as e:
        print(f"❌ Error: {e}")


@bot.command(name="setup_roles")
@commands.has_permissions(administrator=True)
async def setup_roles(ctx):
    """Sends a message with reaction options (run once)"""
    description = "**React to get your role :**\n"

    for emoji, role_name in ROLE_MAPPING.items():
        description += f"\n{emoji} → `{role_name}`"
    
    embed = discord.Embed(
        title="Choose Your Role",
        description=description,
        color=discord.Color.blue()
    )
    msg = await ctx.send(embed=embed)
    
    # Add all reaction emojis
    failed_emojis = []
    for emoji in ROLE_MAPPING.keys():
        try:
            await msg.add_reaction(emoji)
            print(f"✓ Added reaction: {emoji}")
        except discord.HTTPException as e:
            if e.code == 10014:  # Unknown Emoji error
                await ctx.send(f"⚠️ Failed to add reaction `{emoji}` - Invalid emoji format!")
                print(f"❌ Invalid emoji: {emoji}")
                failed_emojis.append(emoji)
            else:
                raise e
    
    if failed_emojis:
        await ctx.send(f"⚠️ Could not add {len(failed_emojis)} emoji(s). Check emoji formats.")
    
    await ctx.send(f"✅ Reaction role message created! Message ID: `{msg.id}`")
    print(f"📝 Save this MESSAGE_ID: {msg.id}")
    
    # Update the global MESSAGE_ID
    global MESSAGE_ID
    MESSAGE_ID = msg.id


##############################################
#                  RULES                     #
##############################################
def in_rules_channel():
    async def predicate(ctx):
        if ctx.channel.id != RULES_CHANNEL_ID:
            await ctx.send(f"❌ This command can only be used in <#{RULES_CHANNEL_ID}>", delete_after=5)
            await ctx.message.delete()
            return False
        return True 
    return commands.check(predicate)

@bot.command(name='rules')
@in_rules_channel()
@commands.has_permissions(administrator=True)
async def rules(ctx):        
    embed = discord.Embed(
        title="Server Rules & Code of Conduct",
        description="## 1. Respect the Circle\n"
                    "• **Honor All Nations:** Discrimination, hate speech, or disrespect regarding tribal affiliations, race, gender, or identity will not be tolerated.\n"
                    "• **Keep It Friendly:** No toxicity, personal attacks, or targeted harassment.\n"
                    "---\n\n"
                    "## 2. Content & Chat Guidelines\n"
                    "• **Keep it Clean:**keep main text and voice channels SFW (Safe For Work).\n"
                    "• **No Spamming:** Avoid flooding chat with walls of text, excessive emojis, or irrelevant links.\n"
                    "• **No Self-Promo:** Do not advertise external streams, servers, or products without moderator approval.\n\n"
                    "---\n\n"
                    "## 3. Safety & Privacy\n"
                    "• **Protect Identity:** Do not share anyone's real-life personal information (doxxing).\n"
                    f"• **Report Issues:** Let {ctx.author.name} know if you see any.\n\n"
                    "---\n\n",
        color=discord.Color.blue()
    )
    embed.set_footer(text="Last Updated: June 16 2026")
    
    await ctx.send(embed=embed)


##############################################
#                 Welcome                    #
##############################################

@bot.event
async def on_member_join(member):
    """Ping new member and direct them to the pinned welcome message"""
    
    welcome_channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if not welcome_channel:
        print("❌ Could not find welcome channel")
        return
    
    try:
        # Send a temporary ping to the new member
        temp_msg = await welcome_channel.send(
            f"👋 Welcome <@{member.id}>! "
            f"Please check the **pinned message** above for rules and roles information!"
        )
        
        # Auto-delete after 30 seconds to keep the channel clean
        await temp_msg.delete(delay=30)
        
        # Also send a DM for good measure (optional)
        try:
            dm_embed = discord.Embed(
                title="👋 Welcome to the Server!",
                description="Please check the pinned message in the welcome channel for important information!",
                color=discord.Color.gold()
            )
            rules_channel = bot.get_channel(RULES_CHANNEL_ID)
            roles_channel = bot.get_channel(ROLES_CHANNEL_ID)
            
            if rules_channel and roles_channel:
                dm_embed.add_field(
                    name="Quick Links",
                    value=f"📋 Rules: {rules_channel.mention}\n"
                          f"🎯 Roles: {roles_channel.mention}",
                    inline=False
                )
            
            await member.send(embed=dm_embed)
        except discord.Forbidden:
            pass  # DMs blocked, that's fine
            
    except Exception as e:
        print(f"❌ Error sending welcome ping: {e}")

@bot.command(name='setup_welcome')
@commands.has_permissions(administrator=True)
async def setup_welcome(ctx):
    """Create a pinned welcome message with instructions"""
    
    # Create the welcome embed
    embed = discord.Embed(
        title="📌 Welcome New Members!",
        description="Welcome to the community! Please follow these steps to get started:",
        color=discord.Color.gold()
    )
    
    # Get channel mentions
    rules_channel = bot.get_channel(RULES_CHANNEL_ID)
    roles_channel = bot.get_channel(ROLES_CHANNEL_ID)
    
    embed.add_field(
        name="1️⃣ Read the Rules",
        value=f"Review our community guidelines in {rules_channel.mention}",
        inline=False
    )
    
    embed.add_field(
        name="2️⃣ Choose Your Role",
        value=f"React to the message in {roles_channel.mention} to select your team role",
        inline=False
    )
    
    embed.add_field(
        name="3️⃣ Introduce Yourself",
        value="Feel free to say hello in the general chat!",
        inline=False
    )
    
    embed.set_footer(text="Pinned for easy access • Updated: June 2026")
    
    # Send the message
    msg = await ctx.send(embed=embed)
    
    # Pin it
    await msg.pin()
    
    # Store the message ID for reference
    global WELCOME_PINNED_MESSAGE_ID
    WELCOME_PINNED_MESSAGE_ID = msg.id
    
    await ctx.send(f"✅ Welcome message pinned! Message ID: `{msg.id}`")
    await ctx.send("ℹ️ New members will now be pinged and directed to this pinned message.")

@bot.command(name='test_welcome_ping')
@commands.has_permissions(administrator=True)
async def test_welcome_ping(ctx, member: discord.Member = None):
    """Test the welcome ping for a specific member (admin only)"""
    if member is None:
        member = ctx.author
    
    welcome_channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if welcome_channel:
        await welcome_channel.send(
            f"🧪 **TEST**: Welcome <@{member.id}>! "
            f"Please check the **pinned message** above for rules and roles information!"
        )
        await ctx.send(f"✅ Test ping sent for {member.display_name}")
    else:
        await ctx.send("❌ Welcome channel not found!")

##############################################
#                 Twitch                    #
##############################################


twitch_client = None 
live_trackers = {streamer.lower(): False for streamer in STREAMERS }

@tasks.loop(seconds=60)
async def check_streams():
    global twitch_client
    if not twitch_client:
        return

    # Uses your bot variable to locate the notification channel
    channel = bot.get_channel(STREAMING_CHANNEL_ID)
    if not channel:
        return

    try:
        # Check active live streams
        async for stream in twitch_client.get_streams(user_login=list(live_trackers.keys())):
            streamer_name = stream.user_login.lower()
            
            if not live_trackers.get(streamer_name, False):
                live_trackers[streamer_name] = True
                
                # Build alert graphic
                embed = discord.Embed(
                    title=f"🔴 {stream.user_name} is LIVE!",
                    description=f"**Playing:** {stream.game_name}\n**Title:** {stream.title}",
                    url=f"https://twitch.tv{streamer_name}",
                    color=discord.Color.purple()
                )
                embed.set_thumbnail(url=stream.thumbnail_url.format(width=400, height=225))
                embed.add_field(name="Watch Here", value=f"[Click to watch stream](https://twitch.tv{streamer_name})")
                
                await channel.send(content=f"@everyone {stream.user_name} just went live!", embed=embed)
        
        # Reset tracking markers for channels that went offline
        active_live_streamers = []
        async for stream in twitch_client.get_streams(user_login=list(live_trackers.keys())):
            active_live_streamers.append(stream.user_login.lower())
                
        for streamer in live_trackers:
            if streamer not in active_live_streamers:
                live_trackers[streamer] = False

    except Exception as e:
        print(f"Error checking streams: {e}")


##############################################
#                Debugging                   #
##############################################

@bot.command(name='check_perms')
@commands.has_permissions(administrator=True)
async def check_permissions(ctx):
    """Check if bot has required permissions in this channel"""
    perms = ctx.channel.permissions_for(ctx.guild.me)
    
    required = [
        'manage_roles', 
        'read_messages', 
        'send_messages', 
        'add_reactions',
        'read_message_history'
    ]
    
    missing = [p for p in required if not getattr(perms, p)]
    
    if missing:
        await ctx.send(f"❌ Missing permissions: {', '.join(missing)}")
    else:
        await ctx.send("✅ Bot has all required permissions!")

##############################################
#       main bot integerity and log in       #
##############################################
intents = discord.Intents.default()
intents.members = True  # Required to assign roles
intents.message_content = True
intents.reactions = True
intents.guilds = True  # Make sure guilds intent is enabled

bot = commands.Bot(command_prefix="!", intents=intents)
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    # Fetch and store the target message at startup
    roles_channel = bot.get_channel(ROLES_CHANNEL_ID)
    global twitch_client 
    if twitch_client is None: 
        twitch_client = await Twitch(TWITCH_APP_ID,TWITCH_APP_SECRET)
        print("Twitch connected successfully")
 
    if not check_streams.is_running(): 
        check_streams.start()
        print("Monitering lives! loop started.")
    try:
        global TARGET_MESSAGE
        TARGET_MESSAGE = await roles_channel.fetch_message(MESSAGE_ID)
        print(f"🎯 Watching message {MESSAGE_ID} for reactions")
    except Exception as e:
        print(f"❌ Could not fetch message: {e}")

if __name__ == "__main__":
    bot.run(TOKEN)