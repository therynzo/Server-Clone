import discord
import asyncio
import os
import sys
import requests

class ClonerClient(discord.Client):
    def __init__(self, source_id, target_id, wipe_target, clone_channels, clone_emojis, clone_roles, clone_info, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_id = source_id
        self.target_id = target_id
        self.wipe_target = wipe_target
        self.clone_channels = clone_channels
        self.clone_emojis = clone_emojis
        self.clone_roles = clone_roles
        self.clone_info = clone_info

    async def setup_hook(self):
        self.loop.create_task(self.start_cloning_process())

    async def on_ready(self):
        print(f"✅ Logged in as: {self.user} (ID: {self.user.id})")

    async def start_cloning_process(self):
        await self.wait_until_ready()
        
        source_guild = self.get_guild(self.source_id)
        target_guild = self.get_guild(self.target_id)

        if not source_guild:
            print(f"❌ Could not access Source Server ({self.source_id}). Make sure your account is in that server.")
            await self.close()
            return

        if not target_guild:
            print(f"❌ Could not access Target Server ({self.target_id}). Make sure your account is in that server.")
            await self.close()
            return

        # 0. Automatic Clear (Wipe Target Server)
        if self.wipe_target:
            print(f"\n🧹 Wiping existing items from Target Server: [{target_guild.name}]...")
            
            # Delete Channels
            for channel in target_guild.channels:
                try:
                    await channel.delete()
                    print(f"  ├─ Deleted Channel: {channel.name}")
                    await asyncio.sleep(0.8)
                except Exception as e:
                    print(f"  ├─ ⚠️ Couldn't delete channel {channel.name}: {e}")

            # Delete Roles
            for role in target_guild.roles:
                if not role.is_default() and not role.managed:
                    try:
                        await role.delete()
                        print(f"  ├─ Deleted Role: {role.name}")
                        await asyncio.sleep(0.8)
                    except Exception as e:
                        print(f"  ├─ ⚠️ Couldn't delete role {role.name}: {e}")

            # Delete Emojis
            for emoji in target_guild.emojis:
                try:
                    await emoji.delete()
                    print(f"  ├─ Deleted Emoji: {emoji.name}")
                    await asyncio.sleep(0.8)
                except Exception as e:
                    print(f"  ├─ ⚠️ Couldn't delete emoji {emoji.name}: {e}")

            print("✅ Server wipe complete!\n")

        print(f"🚀 Starting clean clone: [{source_guild.name}] ➡️ [{target_guild.name}]\n")

        # 1. Clone Server Info
        if self.clone_info:
            print("⚙️  Cloning Server Name and Icon...")
            try:
                icon_bytes = None
                if source_guild.icon:
                    icon_bytes = await source_guild.icon.read()
                await target_guild.edit(name=source_guild.name, icon=icon_bytes)
                print("✅ Server Info updated.")
            except Exception as e:
                print(f"⚠️ Failed to update Server Info: {e}")

        # 2. Clone Roles
        if self.clone_roles:
            print("\n🎭 Cloning Roles...")
            roles_to_clone = [r for r in reversed(source_guild.roles) if not r.is_default() and not r.managed]
            
            for role in roles_to_clone:
                try:
                    safe_perms = role.permissions
                    safe_perms.administrator = False
                    safe_perms.manage_roles = False
                    safe_perms.manage_channels = False
                    safe_perms.manage_guild = False

                    await target_guild.create_role(
                        name=role.name,
                        permissions=safe_perms,
                        color=role.color,
                        hoist=role.hoist,
                        mentionable=role.mentionable
                    )
                    print(f"  ├─ Created Role: {role.name}")
                    await asyncio.sleep(1.2)
                except Exception as e:
                    print(f"  ├─ ⚠️ Error creating role {role.name}: {e}")

        # 3. Clone Channels and Categories
        if self.clone_channels:
            print("\n📁 Cloning Categories and Channels (Stripped Permissions)...")
            category_mapping = {}

            # Clone Categories
            for category in sorted(source_guild.categories, key=lambda c: c.position):
                try:
                    new_cat = await target_guild.create_category(
                        name=category.name,
                        overwrites={}
                    )
                    category_mapping[category.id] = new_cat
                    print(f"  ├─ Created Category: {category.name}")
                    await asyncio.sleep(1.2)
                except Exception as e:
                    print(f"  ├─ ⚠️ Error creating category {category.name}: {e}")

            # Clone Text Channels
            for channel in sorted(source_guild.text_channels, key=lambda c: c.position):
                try:
                    target_cat = category_mapping.get(channel.category_id) if channel.category_id else None
                    await target_guild.create_text_channel(
                        name=channel.name,
                        category=target_cat,
                        topic=channel.topic,
                        nsfw=channel.nsfw,
                        overwrites={}
                    )
                    print(f"  ├─ Created Text Channel: #{channel.name}")
                    await asyncio.sleep(1.2)
                except Exception as e:
                    print(f"  ├─ ⚠️ Error creating text channel {channel.name}: {e}")

            # Clone Voice Channels
            for channel in sorted(source_guild.voice_channels, key=lambda c: c.position):
                try:
                    target_cat = category_mapping.get(channel.category_id) if channel.category_id else None
                    await target_guild.create_voice_channel(
                        name=channel.name,
                        category=target_cat,
                        user_limit=channel.user_limit,
                        overwrites={}
                    )
                    print(f"  ├─ Created Voice Channel: {channel.name}")
                    await asyncio.sleep(1.2)
                except Exception as e:
                    print(f"  ├─ ⚠️ Error creating voice channel {channel.name}: {e}")

        # 4. Clone Emojis
        if self.clone_emojis:
            print("\n😀 Cloning Emojis...")
            for emoji in source_guild.emojis:
                try:
                    img_data = requests.get(emoji.url).content
                    await target_guild.create_custom_emoji(name=emoji.name, image=img_data)
                    print(f"  ├─ Created Emoji: :{emoji.name}:")
                    await asyncio.sleep(1.5)
                except Exception as e:
                    print(f"  ├─ ⚠️ Error copying emoji :{emoji.name}: -> {e}")

        print("\n🎉 Cloning process complete!")
        await self.close()

def print_banner():
    print("\033[91m" + """
 ╔═════════════════════════════════════╗
 ║         T H E  R Y N Z O            ║
 ║      Discord Server Cloner v2       ║
 ╚═════════════════════════════════════╝
    """ + "\033[0m")

async def main():
    print_banner()

    user_token = input("🔑 Enter your Discord User Token: ").strip()
    if not user_token:
        print("❌ Token cannot be empty!")
        return

    try:
        source_id = int(input("📥 Enter Source Server ID (Copy FROM): ").strip())
        target_id = int(input("📤 Enter Target Server ID (Copy TO): ").strip())
    except ValueError:
        print("❌ Server IDs must be numbers!")
        return

    print("\n--- Cloning Menu ---")
    wipe_target = input("Clear/Delete EVERYTHING in Target Server before copying? (y/n): ").strip().lower() == 'y'
    clone_channels = input("Do you want to clone Categories & Channels? (y/n): ").strip().lower() == 'y'
    clone_roles = input("Do you want to clone Roles? (y/n): ").strip().lower() == 'y'
    clone_emojis = input("Do you want to clone Emojis? (y/n): ").strip().lower() == 'y'
    clone_info = input("Do you want to clone Server Info (Name & Icon)? (y/n): ").strip().lower() == 'y'

    if not (wipe_target or clone_channels or clone_roles or clone_emojis or clone_info):
        print("⚠️ No options selected. Exiting.")
        return

    client = ClonerClient(
        source_id=source_id,
        target_id=target_id,
        wipe_target=wipe_target,
        clone_channels=clone_channels,
        clone_emojis=clone_emojis,
        clone_roles=clone_roles,
        clone_info=clone_info
    )

    try:
        async with client:
            await client.start(user_token)
    except Exception as e:
        print(f"\n❌ Login failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
