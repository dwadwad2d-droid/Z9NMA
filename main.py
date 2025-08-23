#!/usr/bin/env python3
"""
Roblox Community Scraper
A modern application to analyze Roblox communities and create wealth leaderboards
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import asyncio
from datetime import datetime
import json
import os
from typing import Dict, List, Optional, Tuple

from roblox_scraper import RobloxScraper
from discord_finder import DiscordFinder
from ui_components import ModernComponents

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class RobloxCommunityAnalyzer:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Roblox Community Analyzer")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Initialize components
        self.scraper = None
        self.discord_finder = DiscordFinder()
        self.current_analysis = None
        
        # Setup UI
        self.setup_ui()
        
        # Status variables
        self.is_analyzing = False
        
    def setup_ui(self):
        """Setup the modern UI interface"""
        # Main container
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            self.main_frame, 
            text="🎮 Roblox Community Analyzer", 
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.pack(pady=(20, 30))
        
        # Input section
        self.setup_input_section()
        
        # Control buttons
        self.setup_control_section()
        
        # Results section
        self.setup_results_section()
        
        # Status bar
        self.setup_status_section()
    
    def setup_input_section(self):
        """Setup input fields for cookie and community URL"""
        input_frame = ctk.CTkFrame(self.main_frame)
        input_frame.pack(fill="x", padx=20, pady=10)
        
        # Cookie input
        cookie_label = ctk.CTkLabel(input_frame, text="🍪 Roblox Cookie (Required):", font=ctk.CTkFont(size=14, weight="bold"))
        cookie_label.pack(anchor="w", padx=20, pady=(20, 5))
        
        self.cookie_entry = ctk.CTkEntry(
            input_frame, 
            placeholder_text="Enter your .ROBLOSECURITY cookie here...",
            show="*",
            height=40,
            font=ctk.CTkFont(size=12)
        )
        self.cookie_entry.pack(fill="x", padx=20, pady=(0, 15))
        
        # Community URL input
        url_label = ctk.CTkLabel(input_frame, text="🌐 Community URL:", font=ctk.CTkFont(size=14, weight="bold"))
        url_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.url_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="https://www.roblox.com/communities/35461612/Z9-Market#!/about",
            height=40,
            font=ctk.CTkFont(size=12)
        )
        self.url_entry.pack(fill="x", padx=20, pady=(0, 20))
        
        # Help text
        help_text = ctk.CTkLabel(
            input_frame,
            text="💡 Tip: Find your cookie in browser dev tools > Application > Cookies > .ROBLOSECURITY",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        help_text.pack(anchor="w", padx=20, pady=(0, 20))
    
    def setup_control_section(self):
        """Setup control buttons"""
        control_frame = ctk.CTkFrame(self.main_frame)
        control_frame.pack(fill="x", padx=20, pady=10)
        
        button_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        button_frame.pack(pady=20)
        
        self.analyze_button = ctk.CTkButton(
            button_frame,
            text="🔍 Analyze Community",
            command=self.start_analysis,
            height=50,
            width=200,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=15
        )
        self.analyze_button.pack(side="left", padx=(0, 10))
        
        self.stop_button = ctk.CTkButton(
            button_frame,
            text="⏹️ Stop Analysis",
            command=self.stop_analysis,
            height=50,
            width=150,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=15,
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=10)
        
        self.export_button = ctk.CTkButton(
            button_frame,
            text="💾 Export Results",
            command=self.export_results,
            height=50,
            width=150,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=15,
            state="disabled"
        )
        self.export_button.pack(side="left", padx=(10, 0))
    
    def setup_results_section(self):
        """Setup results display area"""
        results_frame = ctk.CTkFrame(self.main_frame)
        results_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Tabview for different result types
        self.tabview = ctk.CTkTabview(results_frame, height=400)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Leaderboard tab
        self.tabview.add("💰 Wealth Leaderboard")
        self.leaderboard_text = ctk.CTkTextbox(
            self.tabview.tab("💰 Wealth Leaderboard"),
            font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.leaderboard_text.pack(fill="both", expand=True)
        
        # Discord matches tab
        self.tabview.add("🎮 Discord Matches")
        self.discord_text = ctk.CTkTextbox(
            self.tabview.tab("🎮 Discord Matches"),
            font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.discord_text.pack(fill="both", expand=True)
        
        # Community info tab
        self.tabview.add("ℹ️ Community Info")
        self.info_text = ctk.CTkTextbox(
            self.tabview.tab("ℹ️ Community Info"),
            font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.info_text.pack(fill="both", expand=True)
        
        # Log tab
        self.tabview.add("📋 Analysis Log")
        self.log_text = ctk.CTkTextbox(
            self.tabview.tab("📋 Analysis Log"),
            font=ctk.CTkFont(family="Consolas", size=11)
        )
        self.log_text.pack(fill="both", expand=True)
    
    def setup_status_section(self):
        """Setup status bar"""
        status_frame = ctk.CTkFrame(self.main_frame)
        status_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="🟢 Ready to analyze",
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        self.status_label.pack(side="left", padx=20, pady=10)
        
        self.progress_bar = ctk.CTkProgressBar(status_frame, width=300)
        self.progress_bar.pack(side="right", padx=20, pady=10)
        self.progress_bar.set(0)
    
    def log_message(self, message: str, level: str = "INFO"):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colored_message = f"[{timestamp}] {level}: {message}\n"
        
        self.log_text.insert("end", colored_message)
        self.log_text.see("end")
        self.root.update_idletasks()
    
    def update_status(self, message: str, progress: float = None):
        """Update status bar"""
        self.status_label.configure(text=message)
        if progress is not None:
            self.progress_bar.set(progress)
        self.root.update_idletasks()
    
    def validate_inputs(self) -> bool:
        """Validate user inputs"""
        cookie = self.cookie_entry.get().strip()
        url = self.url_entry.get().strip()
        
        if not cookie:
            messagebox.showerror("Error", "Please enter your Roblox cookie")
            return False
        
        if not url:
            messagebox.showerror("Error", "Please enter a community URL")
            return False
        
        if "roblox.com/communities/" not in url:
            messagebox.showerror("Error", "Invalid community URL format")
            return False
        
        return True
    
    def start_analysis(self):
        """Start the community analysis in a separate thread"""
        if not self.validate_inputs():
            return
        
        if self.is_analyzing:
            messagebox.showwarning("Warning", "Analysis already in progress")
            return
        
        # Start analysis in background thread
        self.is_analyzing = True
        self.analyze_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        
        analysis_thread = threading.Thread(target=self.run_analysis)
        analysis_thread.daemon = True
        analysis_thread.start()
    
    def run_analysis(self):
        """Main analysis logic"""
        try:
            self.update_status("🔄 Initializing scraper...", 0.1)
            self.log_message("Starting community analysis")
            
            # Initialize scraper
            cookie = self.cookie_entry.get().strip()
            self.scraper = RobloxScraper(cookie)
            
            # Validate authentication
            self.update_status("🔐 Validating authentication...", 0.2)
            if not self.scraper.validate_auth():
                raise Exception("Invalid Roblox cookie or authentication failed")
            
            self.log_message("Authentication successful")
            
            # Parse community URL
            url = self.url_entry.get().strip()
            community_id = self.extract_community_id(url)
            
            self.update_status("📊 Fetching community data...", 0.3)
            self.log_message(f"Analyzing community ID: {community_id}")
            
            # Get community info
            community_info = self.scraper.get_community_info(community_id)
            self.display_community_info(community_info)
            
            # Get community members
            self.update_status("👥 Fetching community members...", 0.4)
            members = self.scraper.get_community_members(community_id)
            self.log_message(f"Found {len(members)} community members")
            
            # Display member list immediately
            self.display_member_list(members)
            
            # Analyze member wealth with high-speed processing
            self.update_status("🚀 Starting high-speed wealth analysis...", 0.5)
            self.log_message("Using concurrent processing for maximum speed")
            
            import time
            start_time = time.time()
            wealth_data = self.scraper.analyze_member_wealth(members, self.update_progress)
            end_time = time.time()
            
            analysis_time = end_time - start_time
            members_analyzed = len(wealth_data)
            
            # Calculate privacy statistics
            private_count = len([m for m in wealth_data if m.get('total_value') == -1])
            error_count = len([m for m in wealth_data if m.get('total_value') == -2])
            public_with_limiteds = len([m for m in wealth_data if m.get('total_value', 0) > 0])
            public_no_limiteds = len([m for m in wealth_data if m.get('total_value', 0) == 0])
            
            self.log_message(f"⚡ Analysis completed in {analysis_time:.2f} seconds")
            self.log_message(f"📊 Analyzed {members_analyzed} members ({members_analyzed/analysis_time:.1f} members/second)")
            self.log_message(f"🔒 Privacy Stats: {private_count} private, {error_count} errors, {public_with_limiteds} with limiteds, {public_no_limiteds} public empty")
            
            # Create leaderboard
            self.update_status("📊 Creating wealth leaderboard...", 0.8)
            leaderboard = self.create_leaderboard(wealth_data)
            self.display_leaderboard(leaderboard)
            
            # Find Discord server
            self.update_status("🔍 Searching for Discord server...", 0.9)
            discord_info = self.discord_finder.find_discord_server(community_info)
            
            discord_matches = []
            if discord_info:
                invite_url = discord_info.get('invite_url', discord_info.get('invite', 'Unknown'))
                self.log_message(f"Found Discord server: {invite_url}")
                self.discord_text.delete("1.0", "end")
                self.discord_text.insert("1.0", f"🔍 Discord server found: {invite_url}\n\nSearching for user matches...\n\n")
                
                # Match Discord users
                discord_matches = self.discord_finder.match_discord_users(wealth_data, discord_info)
                self.display_discord_matches(discord_matches)
            else:
                self.log_message("No Discord server found in community social links")
                self.discord_text.delete("1.0", "end")
                self.discord_text.insert("1.0", "❌ No Discord server found in community social links.\n\nChecked:\n- Community description\n- Social media links\n- Community details\n\nNo Discord invite links were discovered.")
            
            self.update_status("✅ Analysis completed successfully!", 1.0)
            self.log_message("Analysis completed successfully")
            
            self.current_analysis = {
                'community_info': community_info,
                'leaderboard': leaderboard,
                'discord_matches': discord_matches if discord_info else None
            }
            
            self.export_button.configure(state="normal")
            
        except Exception as e:
            self.log_message(f"Error during analysis: {str(e)}", "ERROR")
            self.update_status(f"❌ Error: {str(e)}", 0)
            messagebox.showerror("Analysis Error", f"An error occurred: {str(e)}")
        
        finally:
            self.is_analyzing = False
            self.analyze_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            
            # Reset scraper stop flag for next analysis
            if self.scraper:
                self.scraper.stop_analysis = False
    
    def update_progress(self, current: int, total: int, user_info: dict = None):
        """Update progress during member analysis"""
        progress = 0.5 + (current / total) * 0.3  # Between 0.5 and 0.8
        percentage = int((current / total) * 100)
        
        if user_info:
            username = user_info.get('username', 'Unknown')
            total_value = user_info.get('total_value', 0)
            limiteds_count = len(user_info.get('limiteds', []))
            privacy_status = user_info.get('privacy_status', 'unknown')
            status_info = user_info.get('status_info', '')
            
            # Show high-speed processing status
            self.update_status(f"🚀 Processed {username}... ({current}/{total} - {percentage}%) [CONCURRENT]", progress)
            
            # Log users with different statuses
            if total_value == -1:  # Private inventory
                self.log_message(f"🔒 PRIVATE: {username} - Inventory is private")
            elif total_value == -2:  # Error accessing
                self.log_message(f"❌ ERROR: {username} - Could not access inventory")
            elif total_value > 0:  # Has limiteds
                self.log_message(f"💰 WEALTHY: {username} - {total_value:,} R$ ({limiteds_count} limiteds)")
            else:  # Public but no limiteds
                self.log_message(f"📭 PUBLIC: {username} - No valuable limiteds found")
            
            # Update leaderboard in real-time for any user (not just wealthy ones)
            self.root.after_idle(self.update_leaderboard_partial, user_info)
        else:
            self.update_status(f"🚀 High-speed processing... ({current}/{total} - {percentage}%)", progress)
    
    def extract_community_id(self, url: str) -> str:
        """Extract community ID from URL"""
        import re
        match = re.search(r'/communities/(\d+)/', url)
        if match:
            return match.group(1)
        raise ValueError("Could not extract community ID from URL")
    
    def create_leaderboard(self, wealth_data: List[Dict]) -> List[Dict]:
        """Create sorted wealth leaderboard filtering out negative values (private/error)"""
        # Filter to only include valid wealth values (>= 0)
        valid_wealth = [member for member in wealth_data if member.get('total_value', 0) >= 0]
        # Sort by wealth descending
        sorted_members = sorted(valid_wealth, key=lambda x: x['total_value'], reverse=True)
        return sorted_members[:50]  # Top 50
    
    def display_community_info(self, info: Dict):
        """Display community information"""
        text = f"""
Community Name: {info.get('name', 'Unknown')}
Description: {info.get('description', 'No description')}
Member Count: {info.get('member_count', 'Unknown')}
Owner: {info.get('owner', 'Unknown')}
Created: {info.get('created', 'Unknown')}

Social Links:
"""
        for link in info.get('social_links', []):
            text += f"  • {link['type']}: {link['url']}\n"
        
        self.info_text.delete("1.0", "end")
        self.info_text.insert("1.0", text)
    
    def display_member_list(self, members: List[Dict]):
        """Display community member list immediately"""
        text = "👥 COMMUNITY MEMBERS\n" + "="*40 + "\n\n"
        text += f"Total Members: {len(members)}\n\n"
        
        for i, member in enumerate(members[:50], 1):  # Show first 50
            user = member.get('user', {})
            username = user.get('username', 'Unknown')
            user_id = user.get('userId', 'Unknown')
            role = member.get('role', {}).get('name', 'Member')
            
            text += f"{i:2d}. {username} (ID: {user_id})\n"
            text += f"     Role: {role}\n"
            text += f"     Profile: https://www.roblox.com/users/{user_id}/profile\n\n"
        
        if len(members) > 50:
            text += f"... and {len(members) - 50} more members\n"
        
        # Update the leaderboard tab initially with member list
        self.leaderboard_text.delete("1.0", "end")
        self.leaderboard_text.insert("1.0", text)
    
    def display_leaderboard(self, leaderboard: List[Dict]):
        """Display wealth leaderboard"""
        text = "🏆 WEALTH LEADERBOARD (Top 50)\n" + "="*60 + "\n\n"
        
        for i, member in enumerate(leaderboard, 1):
            text += f"{i:2d}. {member['username']:<20} | {member['total_value']:>10,} R$ | {len(member['limiteds']):>3} limiteds\n"
            if member.get('profile_url'):
                text += f"     Profile: {member['profile_url']}\n"
            if member['limiteds']:
                text += f"     Top Items: {', '.join(member['limiteds'][:3])}\n"
            text += "\n"
        
        self.leaderboard_text.delete("1.0", "end")
        self.leaderboard_text.insert("1.0", text)
    
    def update_leaderboard_partial(self, user_info: Dict):
        """Update leaderboard with new user info in real-time"""
        try:
            current_text = self.leaderboard_text.get("1.0", "end")
            
            # If this is the first analysis entry, create header
            if "🏆 ANALYSIS IN PROGRESS" not in current_text:
                header = "🏆 ANALYSIS IN PROGRESS (Live Updates)\n" + "="*60 + "\n"
                header += "Users are being analyzed in real-time with privacy detection:\n\n"
                self.leaderboard_text.delete("1.0", "end")
                self.leaderboard_text.insert("1.0", header)
            
            # Add new user info with privacy status
            total_value = user_info.get('total_value', 0)
            limiteds_count = len(user_info.get('limiteds', []))
            status_info = user_info.get('status_info', '')
            
            # Show user with appropriate status indicator
            if total_value == -1:  # Private inventory
                user_line = f"🔒 {user_info['username']:<20} | {'PRIVATE':>15} | Inventory Hidden\n"
            elif total_value == -2:  # Error accessing
                user_line = f"❌ {user_info['username']:<20} | {'ERROR':>15} | Access Failed\n"
            elif total_value > 0:  # Has limiteds
                user_line = f"💰 {user_info['username']:<20} | {total_value:>10,} R$ | {limiteds_count:>3} limiteds\n"
                if user_info.get('limiteds'):
                    user_line += f"     📦 Items: {', '.join(user_info['limiteds'][:3])}\n"
            else:  # Public but no limiteds
                user_line = f"📭 {user_info['username']:<20} | {'NO LIMITEDS':>15} | Public Inventory\n"
            
            if user_info.get('profile_url'):
                user_line += f"     🔗 Profile: {user_info['profile_url']}\n"
            user_line += "\n"
            
            self.leaderboard_text.insert("end", user_line)
            self.leaderboard_text.see("end")
            
        except Exception as e:
            self.log_message(f"Error updating leaderboard: {e}", "ERROR")
    
    def display_discord_matches(self, matches: List[Dict]):
        """Display Discord user matches"""
        text = "🎮 DISCORD USER MATCHES\n" + "="*50 + "\n\n"
        
        if not matches:
            text += "No Discord users found for leaderboard members.\n"
        else:
            for match in matches:
                text += f"Roblox: {match['roblox_username']}\n"
                text += f"Discord: {match['discord_username']} ({match['discord_id']})\n"
                text += f"Match Source: {match['source']}\n"
                text += f"Wealth: {match['wealth']:,} R$\n"
                text += "-" * 40 + "\n"
        
        self.discord_text.delete("1.0", "end")
        self.discord_text.insert("1.0", text)
    
    def stop_analysis(self):
        """Stop current analysis"""
        self.is_analyzing = False
        self.update_status("⏹️ Analysis stopped by user", 0)
        self.log_message("Analysis stopped by user")
        
        # Re-enable controls immediately
        self.analyze_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        
        # Stop the scraper if it exists
        if self.scraper:
            self.scraper.stop_analysis = True
    
    def export_results(self):
        """Export analysis results to JSON"""
        if not self.current_analysis:
            messagebox.showwarning("Warning", "No analysis results to export")
            return
        
        try:
            filename = f"roblox_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(self.current_analysis, f, indent=2, default=str)
            
            messagebox.showinfo("Success", f"Results exported to {filename}")
            self.log_message(f"Results exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = RobloxCommunityAnalyzer()
    app.run()