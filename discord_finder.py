#!/usr/bin/env python3
"""
Discord Finder Module
Handles Discord server discovery and user matching
"""

import re
import requests
import time
from typing import Dict, List, Optional
from urllib.parse import urlparse, parse_qs

class DiscordFinder:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Discord invite patterns
        self.discord_patterns = [
            r'discord\.gg/([a-zA-Z0-9]+)',
            r'discord\.com/invite/([a-zA-Z0-9]+)',
            r'discordapp\.com/invite/([a-zA-Z0-9]+)',
        ]
    
    def find_discord_server(self, community_info: Dict) -> Optional[Dict]:
        """Find Discord server from community social links"""
        try:
            social_links = community_info.get('social_links', [])
            
            for link in social_links:
                url = link.get('url', '')
                link_type = link.get('type', '').lower()
                
                # Check if it's a Discord link
                if 'discord' in url.lower() or 'discord' in link_type:
                    discord_info = self.extract_discord_info(url)
                    if discord_info:
                        return discord_info
                
                # Check other social links for Discord mentions
                discord_info = self.search_discord_in_url(url)
                if discord_info:
                    return discord_info
            
            # Check community description for Discord links
            description = community_info.get('description', '')
            discord_info = self.search_discord_in_text(description)
            if discord_info:
                return discord_info
            
            return None
            
        except Exception as e:
            print(f"Error finding Discord server: {e}")
            return None
    
    def extract_discord_info(self, url: str) -> Optional[Dict]:
        """Extract Discord server information from URL"""
        try:
            for pattern in self.discord_patterns:
                match = re.search(pattern, url)
                if match:
                    invite_code = match.group(1)
                    
                    # Try to get server info from Discord API
                    server_info = self.get_discord_server_info(invite_code)
                    
                    return {
                        'invite_code': invite_code,
                        'invite_url': f"https://discord.gg/{invite_code}",
                        'server_info': server_info
                    }
            
            return None
            
        except Exception as e:
            print(f"Error extracting Discord info from URL: {e}")
            return None
    
    def search_discord_in_url(self, url: str) -> Optional[Dict]:
        """Search for Discord links in a given URL's content"""
        try:
            if not url or 'discord' not in url.lower():
                return None
            
            # Try to fetch the page content
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                content = response.text
                return self.search_discord_in_text(content)
            
            return None
            
        except Exception:
            return None
    
    def search_discord_in_text(self, text: str) -> Optional[Dict]:
        """Search for Discord invite links in text content"""
        try:
            for pattern in self.discord_patterns:
                match = re.search(pattern, text)
                if match:
                    invite_code = match.group(1)
                    
                    # Try to get server info
                    server_info = self.get_discord_server_info(invite_code)
                    
                    return {
                        'invite_code': invite_code,
                        'invite_url': f"https://discord.gg/{invite_code}",
                        'server_info': server_info
                    }
            
            return None
            
        except Exception:
            return None
    
    def get_discord_server_info(self, invite_code: str) -> Optional[Dict]:
        """Get Discord server information from invite code"""
        try:
            # Discord API endpoint for invite info
            url = f"https://discord.com/api/v9/invites/{invite_code}?with_counts=true"
            
            response = self.session.get(url)
            if response.status_code == 200:
                data = response.json()
                
                guild = data.get('guild', {})
                return {
                    'name': guild.get('name'),
                    'id': guild.get('id'),
                    'member_count': data.get('approximate_member_count'),
                    'online_count': data.get('approximate_presence_count'),
                    'description': guild.get('description'),
                    'icon': guild.get('icon'),
                    'banner': guild.get('banner'),
                    'verification_level': guild.get('verification_level'),
                    'features': guild.get('features', [])
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting Discord server info: {e}")
            return None
    
    def match_discord_users(self, wealth_data: List[Dict], discord_info: Dict) -> List[Dict]:
        """Match Roblox users with Discord users based on profile information"""
        matches = []
        
        try:
            # For each wealthy user, try to find their Discord
            for user_data in wealth_data[:20]:  # Check top 20 wealthy users
                user_id = user_data.get('user_id')
                username = user_data.get('username')
                
                if not user_id or not username:
                    continue
                
                # Try to find Discord info in their profile
                discord_username = self.find_discord_in_roblox_profile(user_data)
                
                if discord_username:
                    matches.append({
                        'roblox_user_id': user_id,
                        'roblox_username': username,
                        'discord_username': discord_username,
                        'discord_id': None,  # Would need Discord bot for this
                        'wealth': user_data.get('total_value', 0),
                        'source': 'roblox_profile',
                        'confidence': 'medium'
                    })
                
                time.sleep(0.5)  # Rate limiting
            
            return matches
            
        except Exception as e:
            print(f"Error matching Discord users: {e}")
            return []
    
    def find_discord_in_roblox_profile(self, user_data: Dict) -> Optional[str]:
        """Find Discord username in Roblox profile data"""
        try:
            # This would require accessing the user's profile description
            # which might be limited by Roblox's privacy settings
            
            # For now, we'll simulate finding Discord usernames
            # In a real implementation, you'd need to scrape the profile page
            # or use a more advanced method
            
            username = user_data.get('username', '')
            
            # Common patterns people use for Discord in Roblox profiles
            discord_patterns = [
                f"{username}#\\d{{4}}",  # Same username with discriminator
                f"{username.lower()}#\\d{{4}}",  # Lowercase version
                f"dc\\s*:?\\s*{username}",  # dc: username
                f"discord\\s*:?\\s*{username}",  # discord: username
            ]
            
            # This is a simplified version - in reality you'd need to
            # fetch and parse the actual profile page
            profile_description = self.get_profile_description(user_data.get('user_id'))
            
            if profile_description:
                for pattern in discord_patterns:
                    match = re.search(pattern, profile_description, re.IGNORECASE)
                    if match:
                        return match.group(0)
            
            return None
            
        except Exception:
            return None
    
    def get_profile_description(self, user_id: int) -> Optional[str]:
        """Get user's profile description (simplified version)"""
        try:
            # This is a placeholder - you'd need to implement
            # actual profile scraping here
            
            # For demonstration, return None
            # In a real implementation, this would scrape the profile page
            return None
            
        except Exception:
            return None
    
    def validate_discord_invite(self, invite_code: str) -> bool:
        """Validate if a Discord invite is still active"""
        try:
            url = f"https://discord.com/api/v9/invites/{invite_code}"
            response = self.session.get(url)
            return response.status_code == 200
            
        except Exception:
            return False
    
    def get_discord_user_info(self, user_id: str) -> Optional[Dict]:
        """Get Discord user information (requires bot token)"""
        # This would require a Discord bot token and proper API access
        # For now, return None as it's beyond the scope of this scraper
        return None
    
    def search_common_discord_usernames(self, roblox_username: str) -> List[str]:
        """Generate common Discord username variations"""
        variations = []
        
        # Common patterns people use
        base_username = roblox_username.lower()
        
        variations.extend([
            roblox_username,
            base_username,
            f"{base_username}_",
            f"_{base_username}",
            f"{base_username}123",
            f"{base_username}2023",
            f"{base_username}2024",
            f"roblox_{base_username}",
            f"{base_username}_roblox"
        ])
        
        # Add discriminator variations
        variations.extend([f"{base_username}#{i:04d}" for i in range(1, 10)])
        
        return variations
    
    def extract_social_handles(self, text: str) -> Dict[str, List[str]]:
        """Extract various social media handles from text"""
        handles = {
            'discord': [],
            'twitter': [],
            'instagram': [],
            'youtube': [],
            'tiktok': []
        }
        
        try:
            # Discord patterns
            discord_matches = re.findall(r'discord[:\s]*([a-zA-Z0-9_]{2,32}#?\d{0,4})', text, re.IGNORECASE)
            handles['discord'].extend(discord_matches)
            
            # Twitter patterns
            twitter_matches = re.findall(r'(?:twitter\.com/|@)([a-zA-Z0-9_]{1,15})', text, re.IGNORECASE)
            handles['twitter'].extend(twitter_matches)
            
            # Instagram patterns
            instagram_matches = re.findall(r'(?:instagram\.com/|ig[:\s]*)([a-zA-Z0-9_.]{1,30})', text, re.IGNORECASE)
            handles['instagram'].extend(instagram_matches)
            
            # YouTube patterns
            youtube_matches = re.findall(r'(?:youtube\.com/(?:c/|channel/|@)|yt[:\s]*)([a-zA-Z0-9_-]{1,100})', text, re.IGNORECASE)
            handles['youtube'].extend(youtube_matches)
            
            # TikTok patterns
            tiktok_matches = re.findall(r'(?:tiktok\.com/@|tt[:\s]*)([a-zA-Z0-9_.]{1,24})', text, re.IGNORECASE)
            handles['tiktok'].extend(tiktok_matches)
            
            return handles
            
        except Exception:
            return handles