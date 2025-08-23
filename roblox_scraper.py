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
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor, as_completed
import math

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
        self.rate_limit_delay = 0.01  # Much faster for concurrent processing
        self._value_cache = {}  # Cache for asset values
        
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
        """Get user's limited items inventory using multiple API endpoints"""
        try:
            limiteds = []
            
            # Try multiple endpoints for better coverage
            endpoints = [
                f"https://inventory.roblox.com/v1/users/{user_id}/assets/collectibles",
                f"https://inventory.roblox.com/v2/users/{user_id}/inventory",
                f"https://api.roblox.com/users/{user_id}/inventory/limited"
            ]
            
            for endpoint in endpoints:
                try:
                    if "collectibles" in endpoint:
                        response = self._get_collectibles(user_id)
                    elif "v2/users" in endpoint:
                        response = self._get_inventory_v2(user_id)
                    else:
                        response = self._get_limited_inventory(user_id)
                    
                    if response:
                        limiteds.extend(response)
                        break  # Use first successful endpoint
                        
                except Exception as e:
                    continue
            
            # Remove duplicates based on asset ID
            seen_ids = set()
            unique_limiteds = []
            for item in limiteds:
                item_id = item.get('id') or item.get('assetId')
                if item_id and item_id not in seen_ids:
                    seen_ids.add(item_id)
                    unique_limiteds.append(item)
            
            return unique_limiteds[:100]  # Limit for performance
            
        except Exception as e:
            print(f"Failed to get inventory for user {user_id}: {e}")
            return []
    
    def _get_collectibles(self, user_id: int) -> List[Dict]:
        """Get collectibles using inventory API"""
        limiteds = []
        cursor = ""
        max_pages = 3  # Limit pages for speed
        
        for page in range(max_pages):
            url = f"https://inventory.roblox.com/v1/users/{user_id}/assets/collectibles"
            params = {'sortOrder': 'Desc', 'limit': 100}
            
            if cursor:
                params['cursor'] = cursor
            
            response = self._make_request(url, params=params)
            
            if not response or 'data' not in response:
                break
            
            batch_items = response['data']
            if not batch_items:
                break
            
            for item in batch_items:
                asset_details = item.get('assetDetails', {})
                if asset_details:
                    limiteds.append({
                        'id': item.get('assetId'),
                        'name': asset_details.get('name'),
                        'recent_average_price': item.get('recentAveragePrice', 0),
                        'user_asset_id': item.get('userAssetId'),
                        'serial_number': item.get('serialNumber'),
                        'asset_type': asset_details.get('assetType')
                    })
            
            cursor = response.get('nextPageCursor')
            if not cursor:
                break
        
        return limiteds
    
    def _get_inventory_v2(self, user_id: int) -> List[Dict]:
        """Get inventory using v2 API"""
        try:
            url = f"https://inventory.roblox.com/v2/users/{user_id}/inventory"
            params = {
                'assetTypes': 'Hat,Face,Gear,Package,Shirt,Pants,Decal,Head,TShirt',
                'limit': 100,
                'sortOrder': 'Desc'
            }
            
            response = self._make_request(url, params=params)
            
            if not response or 'data' not in response:
                return []
            
            limiteds = []
            for item in response['data']:
                if item.get('collectible') or item.get('assetDetails', {}).get('collectible'):
                    limiteds.append({
                        'id': item.get('assetId'),
                        'name': item.get('name'),
                        'recent_average_price': item.get('recentAveragePrice', 0),
                        'user_asset_id': item.get('userAssetId')
                    })
            
            return limiteds
            
        except Exception as e:
            return []
    
    def _get_limited_inventory(self, user_id: int) -> List[Dict]:
        """Get limited items using legacy API"""
        try:
            url = f"https://api.roblox.com/users/{user_id}/inventory/limited"
            response = self._make_request(url)
            
            if not response:
                return []
            
            limiteds = []
            items = response if isinstance(response, list) else response.get('data', [])
            
            for item in items:
                limiteds.append({
                    'id': item.get('AssetId') or item.get('assetId'),
                    'name': item.get('Name') or item.get('name'),
                    'recent_average_price': item.get('RecentAveragePrice', 0) or item.get('recentAveragePrice', 0),
                    'user_asset_id': item.get('UserAssetId') or item.get('userAssetId')
                })
            
            return limiteds
            
        except Exception as e:
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
        """Analyze wealth of community members with high-speed concurrent processing"""
        wealth_data = []
        total_members = len(members)
        
        # Limit to 500 members for 5-second target
        members_to_analyze = members[:500]
        
        print(f"Starting high-speed analysis of {len(members_to_analyze)} members...")
        
        # Use ThreadPoolExecutor for concurrent processing
        max_workers = min(50, len(members_to_analyze))  # Up to 50 concurrent threads
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_member = {}
            for i, member in enumerate(members_to_analyze):
                if self.stop_analysis:
                    break
                future = executor.submit(self._analyze_single_member, member, i)
                future_to_member[future] = (member, i)
            
            # Collect results as they complete
            completed = 0
            for future in as_completed(future_to_member):
                if self.stop_analysis:
                    break
                    
                member, index = future_to_member[future]
                completed += 1
                
                try:
                    user_info = future.result()
                    if user_info:
                        wealth_data.append(user_info)
                        
                        # Update progress with user info for real-time display
                        if progress_callback:
                            progress_callback(completed, len(members_to_analyze), user_info)
                            
                except Exception as e:
                    print(f"Error analyzing member {member}: {e}")
                    if progress_callback:
                        progress_callback(completed, len(members_to_analyze), None)
        
        print(f"Completed analysis of {len(wealth_data)} members")
        return wealth_data
    
    def _analyze_single_member(self, member: Dict, index: int) -> Optional[Dict]:
        """Analyze a single member's wealth - optimized for speed"""
        try:
            user_id = member.get('user', {}).get('userId')
            username = member.get('user', {}).get('username')
            
            if not user_id or not username:
                return None
            
            # Get user's limiteds with faster method
            limiteds = self._get_user_limiteds_fast(user_id)
            
            # Calculate total value
            total_value = 0
            limited_names = []
            
            for limited in limiteds:
                # Try multiple value fields for better accuracy
                value = (limited.get('recent_average_price', 0) or 
                        limited.get('recentAveragePrice', 0) or
                        limited.get('RecentAveragePrice', 0) or
                        self._get_asset_value_fast(limited.get('id')))
                
                if value and value > 0:
                    total_value += value
                    name = (limited.get('name') or 
                           limited.get('Name') or 
                           limited.get('assetName', 'Unknown Limited'))
                    limited_names.append(name)
            
            # Get user profile info
            profile_url = f"https://www.roblox.com/users/{user_id}/profile"
            
            return {
                'user_id': user_id,
                'username': username,
                'total_value': total_value,
                'limiteds': limited_names,
                'limited_count': len(limiteds),
                'profile_url': profile_url
            }
            
        except Exception as e:
            print(f"Error in _analyze_single_member for {member}: {e}")
            return None
    
    def _get_user_limiteds_fast(self, user_id: int) -> List[Dict]:
        """Fast method to get user limiteds - prioritize speed over completeness"""
        try:
            # Try the fastest endpoints first
            endpoints_priority = [
                f"https://api.roblox.com/users/{user_id}/inventory/limited",
                f"https://inventory.roblox.com/v1/users/{user_id}/assets/collectibles?limit=50",
                f"https://economy.roblox.com/v2/users/{user_id}/transactions?transactionType=Sale&limit=10"
            ]
            
            for endpoint in endpoints_priority:
                try:
                    if "inventory/limited" in endpoint:
                        response = self._make_request(endpoint)
                        if response:
                            items = response if isinstance(response, list) else response.get('data', [])
                            if items:
                                return self._parse_limited_items(items)
                    
                    elif "collectibles" in endpoint:
                        response = self._make_request(endpoint)
                        if response and response.get('data'):
                            return self._parse_collectible_items(response['data'])
                    
                    elif "transactions" in endpoint:
                        # Try to get from transaction history as backup
                        response = self._make_request(endpoint)
                        if response and response.get('data'):
                            return self._parse_transaction_items(response['data'])
                            
                except Exception:
                    continue
            
            return []
            
        except Exception as e:
            return []
    
    def _parse_limited_items(self, items: List[Dict]) -> List[Dict]:
        """Parse limited items from API response"""
        parsed = []
        for item in items[:20]:  # Limit for speed
            parsed.append({
                'id': item.get('AssetId') or item.get('assetId'),
                'name': item.get('Name') or item.get('name'),
                'recent_average_price': item.get('RecentAveragePrice', 0) or item.get('recentAveragePrice', 0),
                'user_asset_id': item.get('UserAssetId') or item.get('userAssetId')
            })
        return parsed
    
    def _parse_collectible_items(self, items: List[Dict]) -> List[Dict]:
        """Parse collectible items from API response"""
        parsed = []
        for item in items[:20]:  # Limit for speed
            asset_details = item.get('assetDetails', {})
            parsed.append({
                'id': item.get('assetId'),
                'name': asset_details.get('name') or item.get('name'),
                'recent_average_price': item.get('recentAveragePrice', 0),
                'user_asset_id': item.get('userAssetId'),
                'serial_number': item.get('serialNumber')
            })
        return parsed
    
    def _parse_transaction_items(self, transactions: List[Dict]) -> List[Dict]:
        """Parse items from transaction history"""
        parsed = []
        for transaction in transactions[:10]:  # Limit for speed
            details = transaction.get('details', {})
            if details.get('id'):
                parsed.append({
                    'id': details.get('id'),
                    'name': details.get('name', 'Limited Item'),
                    'recent_average_price': transaction.get('robuxAmount', 0),
                    'user_asset_id': transaction.get('id')
                })
        return parsed
    
    def _get_asset_value_fast(self, asset_id: int) -> int:
        """Fast asset value lookup with caching"""
        if not asset_id:
            return 0
            
        # Use cache if available
        cache_key = f"asset_value_{asset_id}"
        if hasattr(self, '_value_cache') and cache_key in self._value_cache:
            return self._value_cache[cache_key]
        
        if not hasattr(self, '_value_cache'):
            self._value_cache = {}
        
        try:
            # Try multiple fast endpoints
            endpoints = [
                f"https://economy.roblox.com/v1/assets/{asset_id}/resale-data",
                f"https://api.roblox.com/marketplace/productinfo?assetId={asset_id}"
            ]
            
            for endpoint in endpoints:
                try:
                    response = self._make_request(endpoint)
                    if response:
                        value = (response.get('recentAveragePrice') or 
                                response.get('PriceInRobux') or 
                                response.get('price', 0))
                        if value and value > 0:
                            self._value_cache[cache_key] = value
                            return value
                except Exception:
                    continue
            
            self._value_cache[cache_key] = 0
            return 0
            
        except Exception:
            return 0
    
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