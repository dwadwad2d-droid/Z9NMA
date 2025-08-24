#!/usr/bin/env python3
"""
Discord Bot Module
Automatically joins Discord servers and matches users with Roblox accounts
"""

import discord
from discord.ext import commands
import asyncio
import re
import random
import string
from typing import Dict, List, Optional, Tuple
import json
import time

class RobloxDiscordBot:
    def __init__(self):
        self.bot = None
        self.is_running = False
        self.matched_users = []
        self.target_guild = None
        self.roblox_users = {}  # Store roblox username -> user_id mapping
        
    async def create_bot_account(self) -> str:
        """Create a new Discord bot token (placeholder - requires actual Discord app)"""
        # Note: In reality, you'd need to create a Discord application at https://discord.com/developers/applications
        # This is a placeholder that shows the structure
        print("⚠️  Discord Bot Token Required:")
        print("1. Go to https://discord.com/developers/applications")
        print("2. Create a New Application")
        print("3. Go to Bot section and create a bot")
        print("4. Copy the bot token")
        
        # For demo purposes, return a placeholder
        return "YOUR_BOT_TOKEN_HERE"
    
    def setup_bot(self, token: str):
        """Setup the Discord bot with the given token"""
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        
        self.bot = commands.Bot(command_prefix='!', intents=intents)
        
        @self.bot.event
        async def on_ready():
            print(f'🤖 Discord bot logged in as {self.bot.user}')
            print(f'📊 Bot is in {len(self.bot.guilds)} servers')
        
        @self.bot.event
        async def on_guild_join(guild):
            print(f'🎉 Joined guild: {guild.name} (ID: {guild.id})')
            self.target_guild = guild
            # Start user matching process
            await self.match_users_in_guild(guild)
        
        return token
    
    async def join_server_from_invite(self, invite_url: str) -> bool:
        """Join a Discord server using an invite link"""
        try:
            if not self.bot:
                raise Exception("Bot not initialized")
            
            # Extract invite code from URL
            invite_code = self.extract_invite_code(invite_url)
            if not invite_code:
                raise Exception("Invalid invite URL")
            
            print(f"🔗 Attempting to join server with invite: {invite_code}")
            
            # Get invite info
            invite = await self.bot.fetch_invite(invite_code)
            guild = invite.guild
            
            print(f"📋 Server: {guild.name} ({guild.member_count} members)")
            
            # Note: Bots can't use invite links directly, they need to be added by server admins
            # This is a limitation of Discord's API for security reasons
            print("⚠️  Bot accounts cannot join servers via invite links")
            print("   The bot must be invited by a server administrator")
            print(f"   Invite the bot using: https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=2048&scope=bot")
            
            return False
            
        except Exception as e:
            print(f"❌ Failed to join server: {e}")
            return False
    
    def extract_invite_code(self, invite_url: str) -> Optional[str]:
        """Extract invite code from Discord invite URL"""
        patterns = [
            r'discord\.gg/([a-zA-Z0-9]+)',
            r'discord\.com/invite/([a-zA-Z0-9]+)',
            r'discordapp\.com/invite/([a-zA-Z0-9]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, invite_url)
            if match:
                return match.group(1)
        
        return None
    
    async def match_users_in_guild(self, guild: discord.Guild) -> List[Dict]:
        """Match Discord users with Roblox users in the guild"""
        matches = []
        
        try:
            print(f"🔍 Searching for user matches in {guild.name}")
            
            # Get all members in the guild
            members = []
            async for member in guild.fetch_members(limit=None):
                members.append(member)
            
            print(f"👥 Found {len(members)} Discord members")
            
            # Match each Discord user with potential Roblox users
            for member in members:
                if member.bot:
                    continue  # Skip bot accounts
                
                roblox_matches = self.find_roblox_matches(member)
                
                if roblox_matches:
                    for roblox_user in roblox_matches:
                        matches.append({
                            'discord_user': {
                                'id': member.id,
                                'username': member.name,
                                'display_name': member.display_name,
                                'discriminator': member.discriminator if hasattr(member, 'discriminator') else None
                            },
                            'roblox_user': roblox_user,
                            'match_confidence': roblox_user.get('confidence', 'medium'),
                            'match_method': roblox_user.get('method', 'username_similarity')
                        })
            
            print(f"✅ Found {len(matches)} potential matches")
            self.matched_users = matches
            return matches
            
        except Exception as e:
            print(f"❌ Error matching users: {e}")
            return []
    
    def find_roblox_matches(self, discord_member: discord.Member) -> List[Dict]:
        """Find potential Roblox matches for a Discord member"""
        matches = []
        
        # Get Discord user info
        discord_username = discord_member.name.lower()
        discord_display = discord_member.display_name.lower() if discord_member.display_name else discord_username
        
        # Check against known Roblox users
        for roblox_username, roblox_data in self.roblox_users.items():
            roblox_lower = roblox_username.lower()
            
            # Exact match
            if discord_username == roblox_lower or discord_display == roblox_lower:
                matches.append({
                    'username': roblox_username,
                    'user_id': roblox_data.get('user_id'),
                    'confidence': 'high',
                    'method': 'exact_match'
                })
                continue
            
            # Similar usernames (fuzzy matching)
            similarity = self.calculate_similarity(discord_username, roblox_lower)
            if similarity > 0.8:  # 80% similarity threshold
                matches.append({
                    'username': roblox_username,
                    'user_id': roblox_data.get('user_id'),
                    'confidence': 'medium',
                    'method': 'fuzzy_match',
                    'similarity': similarity
                })
            
            # Check display name similarity
            if discord_display != discord_username:
                similarity = self.calculate_similarity(discord_display, roblox_lower)
                if similarity > 0.8:
                    matches.append({
                        'username': roblox_username,
                        'user_id': roblox_data.get('user_id'),
                        'confidence': 'medium',
                        'method': 'display_name_match',
                        'similarity': similarity
                    })
        
        return matches
    
    def calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings using simple algorithm"""
        if str1 == str2:
            return 1.0
        
        # Remove common variations
        str1_clean = re.sub(r'[^a-z0-9]', '', str1)
        str2_clean = re.sub(r'[^a-z0-9]', '', str2)
        
        if str1_clean == str2_clean:
            return 0.95
        
        # Simple character overlap calculation
        set1 = set(str1_clean)
        set2 = set(str2_clean)
        
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def set_roblox_users(self, wealth_data: List[Dict]):
        """Set the list of Roblox users to match against"""
        self.roblox_users = {}
        for user in wealth_data:
            username = user.get('username')
            if username:
                self.roblox_users[username] = {
                    'user_id': user.get('user_id'),
                    'total_value': user.get('total_value', 0),
                    'limiteds': user.get('limiteds', []),
                    'profile_url': user.get('profile_url')
                }
        
        print(f"📊 Loaded {len(self.roblox_users)} Roblox users for matching")
    
    async def start_bot(self, token: str) -> bool:
        """Start the Discord bot"""
        try:
            if token == "YOUR_BOT_TOKEN_HERE":
                print("❌ Please provide a valid Discord bot token")
                return False
            
            self.setup_bot(token)
            
            # Start bot in background
            self.bot_task = asyncio.create_task(self.bot.start(token))
            self.is_running = True
            
            # Wait a bit for bot to connect
            await asyncio.sleep(2)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start Discord bot: {e}")
            return False
    
    async def stop_bot(self):
        """Stop the Discord bot"""
        try:
            if self.bot and not self.bot.is_closed():
                await self.bot.close()
            
            if hasattr(self, 'bot_task'):
                self.bot_task.cancel()
            
            self.is_running = False
            print("🛑 Discord bot stopped")
            
        except Exception as e:
            print(f"❌ Error stopping bot: {e}")
    
    def get_matched_users(self) -> List[Dict]:
        """Get the list of matched users"""
        return self.matched_users
    
    def get_bot_invite_url(self, client_id: str) -> str:
        """Generate bot invite URL"""
        permissions = 2048  # Read messages permission
        return f"https://discord.com/api/oauth2/authorize?client_id={client_id}&permissions={permissions}&scope=bot"

# Helper function to create and manage the bot
async def create_discord_bot_session(invite_url: str, roblox_users: List[Dict]) -> Tuple[RobloxDiscordBot, List[Dict]]:
    """Create a Discord bot session and attempt to match users"""
    bot = RobloxDiscordBot()
    
    # Set Roblox users for matching
    bot.set_roblox_users(roblox_users)
    
    # Create bot token (in reality, user would provide this)
    token = bot.create_bot_account()
    
    if token == "YOUR_BOT_TOKEN_HERE":
        print("📋 Discord Bot Setup Required:")
        print("   Due to Discord's security requirements, bots cannot join servers automatically")
        print("   You need to:")
        print("   1. Create a Discord application at https://discord.com/developers/applications")
        print("   2. Create a bot and get the token")
        print("   3. Invite the bot to the target server using the OAuth2 URL")
        print("   4. Then the bot can analyze members")
        
        return bot, []
    
    # Start the bot
    success = await bot.start_bot(token)
    
    if success:
        # Try to join the server
        joined = await bot.join_server_from_invite(invite_url)
        
        if joined and bot.target_guild:
            # Match users
            matches = await bot.match_users_in_guild(bot.target_guild)
            return bot, matches
    
    return bot, []