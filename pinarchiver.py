import discord
import datetime
import usefulobjects
from discord.ext import commands

basecolor = 0x330091


class PinArchiver(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def archive_channel_id(self, after):
        available_channel_names = [channels.name for channels in after.guild.channels]
        available_channel_ids = [channels.id for channels in after.guild.channels]

        for In in range(len(available_channel_names)):
            if available_channel_names[In] == str('pin-archive'):
                archive_channel = available_channel_ids[In]
                return archive_channel  # Returns the channel id of the archive channel

    async def archive_message(self, message):
        name = message.author
        avatar = message.author.avatar_url
        pin_content = message.content
        emb = discord.Embed(color=basecolor, title=f"{name}'s message was pinned!")
        emb.set_thumbnail(url=avatar)
        emb.add_field(name="Message Content", value=pin_content, inline=False)
        emb.add_field(name="Message Channel", value=message.channel, inline=True)
        emb.add_field(name="Time", value=str(datetime.datetime.now()), inline=True)
        if message.attachments:
            emb.set_image(url=f"{message.attachments[0].url}")
        channel = self.bot.get_channel(# Log channel ID)
        await channel.send(embed=emb)

    async def confirm_message(self, after):
        """ Returns bool true if the channel the message was pinned in is not readable by all roles. """
        channel_perms = after.channel.overwrites  # Returns dictionary of overwrites in the current channel
        roles = after.guild.roles  # Returns all roles in the guild
        perm_roles = []
        perm_values = []

        for In in range(len(roles)):  # Filters roles which have specific channel permissions
            if roles[In] in channel_perms:
                perm_roles.append(roles[In])

        for j in range(len(perm_roles)):
            role_perms = channel_perms[perm_roles[j]].pair()  # Tuple containing the roles permission values
            allow, deny = role_perms
            perm_values.append(deny.value)

        if 1024 in perm_values:  # Permission value for READ_MESSAGES
            return True

    async def message_read_perms(self, message):
        user_roles = message.author.roles
        role_perms = []
        for In in range(len(user_roles)):
            perm_value = discord.Permissions(permissions=user_roles[In].permissions.value)

            if perm_value.manage_messages or perm_value.administrator or message.author.id == message.guild.owner_id:
                role_perms.append('True')
        if 'True' in role_perms:
            return True

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        channelpins = await before.channel.pins()
        pinned_ids = [message.id for message in channelpins]
        if after.pinned:
            if before.content == after.content and after.author != self.bot.user:
                if before.content == after.content and after.author != self.bot.user and len(pinned_ids) == 50:
                    oldest_pin = await after.channel.fetch_message(pinned_ids[-1])
                    await oldest_pin.unpin(reason="Automatically unpinned as channel has reached pin limit.")
                    author = oldest_pin.author
                    authorid = oldest_pin.author.id
                    channelid = oldest_pin.channel.id
                    content = oldest_pin.content
                    channel = self.bot.get_channel(# Log channel ID)
                    embed_var1 = discord.Embed(title=f"Message deleted in #{oldest_pin.channel}",
                                               description=f"<@!{authorid}> had one of their messages automatically unpinned in <#{channelid}>",
                                               color=0x330091)
                    embed_var1.set_thumbnail(url=author.avatar_url)
                    embed_var1.add_field(name="Message Content", value=f"{content}")
                    embed_var1.add_field(name="Time", value=str(datetime.datetime.now()))
                    await channel.send(embed=embed_var1)
                    await self.archive_message(after)
                else:
                    await self.archive_message(after)
        else:
            return

    @commands.command(pass_context=True)
    async def lastpin(self, ctx):
        channelpins = await ctx.message.channel.pins()
        if not channelpins:
            embed = usefulobjects.simplebed(f"There aren't any pinned messages.",
                                            f"There aren't any pins in this channel.")
            await ctx.send(embed=embed)
        else:
            lastpin = channelpins[0]
            pinned_name = lastpin.author
            pinned_avatar = lastpin.author.avatar_url
            pinned_content = lastpin.content
            attachments = lastpin.attachments

            embed = discord.Embed(color=basecolor, title=f"The last pinned message was from {pinned_name}!")
            embed.set_thumbnail(url=pinned_avatar)
            embed.add_field(name="Message Content", value=pinned_content, inline=False)
            embed.add_field(name="Message Channel", value=lastpin.channel, inline=True)
            embed.add_field(name="Time", value=str(datetime.datetime.now()), inline=True)
            if ctx.message.attachments:
                embed.set_image(url=attachments[0].url)
            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def archivepin(self, ctx, message):
        id_to_archive = message
        msg = await ctx.channel.fetch_message(int(id_to_archive))
        pins = await ctx.channel.pins()

        if msg in pins:
            await self.archive_message(msg)
            await ctx.send(embed=usefulobjects.simplebed("Message archived successfully!",
                                                         "It is now archived in the correct channel."))
        else:
            await ctx.send(embed=usefulobjects.simplebed("Oops!", "Seems like the message isn't pinned."))

    @archivepin.error
    async def archive_error(self, ctx, error):
        if isinstance(error, discord.errors.HTTPException):
            emb = discord.Embed(description='Error: Message not found in #{}, try again.', color=basecolor)
            await ctx.send(embed=emb)

def setup(bot):
    bot.add_cog(PinArchiver(bot))
