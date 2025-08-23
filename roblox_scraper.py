#!/usr/bin/env python3
"""
Roblox Scraper Module
Handles authentication, community scraping, and wealth analysis
"""

import requests
import json
import time
import re
from typing import Dict, List, Optional, Callable
from fake_useragent import UserAgent
import threading
from datetime import datetime

class RobloxScraper:
    def __init__(self, cookie: str):
        self.cookie = cookie
        self.session = requests.Session()
        self.user_agent = UserAgent()
        self.stop_analysis = False  # Flag to stop analysis
        
        # Setup session headers
        self.session.headers.update({
            'User-Agent': self.user_agent.random,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Setup cookies
        self.session.cookies.set('.ROBLOSECURITY', cookie, domain='.roblox.com')
        
        # Cache for API responses
        self.cache = {}
        self.rate_limit_delay = 0.5  # Delay between requests
        
        # Get CSRF token
        self.csrf_token = self._get_csrf_token()
        if self.csrf_token:
            self.session.headers['X-CSRF-TOKEN'] = self.csrf_token
    
    def _get_csrf_token(self) -> Optional[str]:
        """Get CSRF token for authenticated requests"""
        try:
            response = self.session.post('https://auth.roblox.com/v2/logout')
            return response.headers.get('x-csrf-token')
        except Exception:
            return None
    
    def _make_request(self, url: str, method: str = 'GET', **kwargs) -> Optional[Dict]:
        """Make rate-limited request with error handling"""
        time.sleep(self.rate_limit_delay)
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, **kwargs)
            elif method.upper() == 'POST':
                response = self.session.post(url, **kwargs)
            else:
                return None
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:  # Rate limited
                time.sleep(2)
                return self._make_request(url, method, **kwargs)
            else:
                print(f"Request failed: {response.status_code} - {url}")
                return None
                
        except Exception as e:
            print(f"Request error: {e}")
            return None
    
    def validate_auth(self) -> bool:
        """Validate the authentication cookie"""
        try:
            url = "https://users.roblox.com/v1/users/authenticated"
            response = self._make_request(url)
            return response is not None and 'id' in response
        except Exception:
            return False
    
    def get_user_info(self) -> Optional[Dict]:
        """Get current authenticated user info"""
        url = "https://users.roblox.com/v1/users/authenticated"
        return self._make_request(url)
    
    def get_community_info(self, community_id: str) -> Dict:
        """Get community information including social links"""
        try:
            # Get basic community info
            url = f"https://groups.roblox.com/v1/groups/{community_id}"
            community_data = self._make_request(url)
            
            if not community_data:
                raise Exception("Failed to fetch community data")
            
            # Get social links
            social_url = f"https://groups.roblox.com/v1/groups/{community_id}/social-links"
            social_data = self._make_request(social_url)
            
            result = {
                'id': community_data.get('id'),
                'name': community_data.get('name'),
                'description': community_data.get('description'),
                'member_count': community_data.get('memberCount'),
                'owner': community_data.get('owner', {}).get('username'),
                'created': community_data.get('created'),
                'social_links': social_data.get('data', []) if social_data else []
            }
            
            return result
            
        except Exception as e:
            raise Exception(f"Failed to get community info: {e}")
    
    def get_community_members(self, community_id: str, max_members: int = 1000) -> List[Dict]:
        """Get community members with pagination"""
        members = []
        cursor = ""
        
        try:
            while len(members) < max_members:
                url = f"https://groups.roblox.com/v1/groups/{community_id}/users"
                params = {
                    'sortOrder': 'Asc',
                    'limit': 100
                }
                
                if cursor:
                    params['cursor'] = cursor
                
                response = self._make_request(url, params=params)
                
                if not response or 'data' not in response:
                    break
                
                batch_members = response['data']
                if not batch_members:
                    break
                
                members.extend(batch_members)
                
                cursor = response.get('nextPageCursor')
                if not cursor:
                    break
                
                # Limit to prevent excessive requests
                if len(members) >= max_members:
                    members = members[:max_members]
                    break
            
            return members
            
        except Exception as e:
            raise Exception(f"Failed to get community members: {e}")
    
    def get_user_inventory(self, user_id: int) -> List[Dict]:
        """Get user's limited items inventory"""
        try:
            limiteds = []
            cursor = ""
            
            # Get collectible items (limiteds)
            while True:
                url = f"https://inventory.roblox.com/v1/users/{user_id}/assets/collectibles"
                params = {
                    'sortOrder': 'Asc',
                    'limit': 100
                }
                
                if cursor:
                    params['cursor'] = cursor
                
                response = self._make_request(url, params=params)
                
                if not response or 'data' not in response:
                    break
                
                batch_items = response['data']
                if not batch_items:
                    break
                
                for item in batch_items:
                    if item.get('assetDetails', {}).get('itemType') in ['Asset', 'Bundle']:
                        limiteds.append({
                            'id': item.get('assetId'),
                            'name': item.get('name'),
                            'recent_average_price': item.get('recentAveragePrice', 0),
                            'user_asset_id': item.get('userAssetId'),
                            'serial_number': item.get('serialNumber')
                        })
                
                cursor = response.get('nextPageCursor')
                if not cursor:
                    break
                
                # Limit to prevent excessive requests
                if len(limiteds) >= 500:
                    break
            
            return limiteds
            
        except Exception as e:
            print(f"Failed to get inventory for user {user_id}: {e}")
            return []
    
    def get_asset_value(self, asset_id: int) -> int:
        """Get current market value of an asset"""
        try:
            # Try to get recent sales data
            url = f"https://economy.roblox.com/v1/assets/{asset_id}/resale-data"
            response = self._make_request(url)
            
            if response and 'recentAveragePrice' in response:
                return response['recentAveragePrice'] or 0
            
            # Fallback: get asset details
            url = f"https://api.roblox.com/marketplace/productinfo?assetId={asset_id}"
            response = self._make_request(url)
            
            if response and 'PriceInRobux' in response:
                return response['PriceInRobux'] or 0
            
            return 0
            
        except Exception:
            return 0
    
    def analyze_member_wealth(self, members: List[Dict], progress_callback: Optional[Callable] = None) -> List[Dict]:
        """Analyze wealth of community members based on limiteds"""
        wealth_data = []
        total_members = len(members)
        
        for i, member in enumerate(members):
            # Check if analysis should be stopped
            if self.stop_analysis:
                print("Analysis stopped by user")
                break
                
            try:
                user_id = member.get('user', {}).get('userId')
                username = member.get('user', {}).get('username')
                
                if not user_id or not username:
                    continue
                
                # Get user's limiteds
                limiteds = self.get_user_inventory(user_id)
                
                # Calculate total value
                total_value = 0
                limited_names = []
                
                for limited in limiteds:
                    value = limited.get('recent_average_price', 0)
                    if value > 0:
                        total_value += value
                        limited_names.append(limited.get('name', 'Unknown'))
                
                # Get user profile info
                profile_url = f"https://www.roblox.com/users/{user_id}/profile"
                
                user_info = {
                    'user_id': user_id,
                    'username': username,
                    'total_value': total_value,
                    'limiteds': limited_names,
                    'limited_count': len(limiteds),
                    'profile_url': profile_url
                }
                
                wealth_data.append(user_info)
                
                # Update progress with user info for real-time display
                if progress_callback:
                    progress_callback(i + 1, total_members, user_info)
                
                # Rate limiting
                time.sleep(self.rate_limit_delay)
                
            except Exception as e:
                print(f"Error analyzing member {member}: {e}")
                continue
        
        return wealth_data
    
    def get_user_profile_data(self, user_id: int) -> Dict:
        """Get user profile data including about section"""
        try:
            # Get basic user info
            url = f"https://users.roblox.com/v1/users/{user_id}"
            user_data = self._make_request(url)
            
            if not user_data:
                return {}
            
            # Try to get about section (this might require different approach)
            # Note: Roblox has restrictions on accessing full profile data
            result = {
                'id': user_data.get('id'),
                'username': user_data.get('name'),
                'display_name': user_data.get('displayName'),
                'description': user_data.get('description', ''),
                'created': user_data.get('created'),
                'profile_url': f"https://www.roblox.com/users/{user_id}/profile"
            }
            
            return result
            
        except Exception as e:
            print(f"Failed to get profile data for user {user_id}: {e}")
            return {}
    
    def search_discord_in_profile(self, user_id: int) -> Optional[str]:
        """Search for Discord information in user profile"""
        try:
            profile_data = self.get_user_profile_data(user_id)
            description = profile_data.get('description', '').lower()
            
            # Common Discord patterns
            discord_patterns = [
                r'discord[:\s]*([a-zA-Z0-9_]{2,32}#\d{4})',  # Discord tag
                r'discord[:\s]*([a-zA-Z0-9_]{2,32})',        # Discord username
                r'@([a-zA-Z0-9_]{2,32})',                    # @username
                r'dc[:\s]*([a-zA-Z0-9_]{2,32})',            # dc: username
            ]
            
            for pattern in discord_patterns:
                match = re.search(pattern, description)
                if match:
                    return match.group(1)
            
            return None
            
        except Exception:
            return None