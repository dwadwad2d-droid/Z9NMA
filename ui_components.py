#!/usr/bin/env python3
"""
UI Components Module
Additional UI components and utilities
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Any
import threading

class ModernComponents:
    """Collection of modern UI components"""
    
    @staticmethod
    def create_loading_spinner(parent, size: int = 30):
        """Create a loading spinner widget"""
        spinner_frame = ctk.CTkFrame(parent, fg_color="transparent")
        
        # Simple progress bar as spinner
        progress = ctk.CTkProgressBar(spinner_frame, width=size*6, height=size//2)
        progress.pack(pady=10)
        progress.set(0.5)
        
        return spinner_frame, progress
    
    @staticmethod
    def create_status_card(parent, title: str, value: str, icon: str = "📊"):
        """Create a status card widget"""
        card = ctk.CTkFrame(parent)
        
        # Icon and title
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 5))
        
        icon_label = ctk.CTkLabel(
            header_frame, 
            text=icon, 
            font=ctk.CTkFont(size=20)
        )
        icon_label.pack(side="left")
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text=title, 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(side="left", padx=(10, 0))
        
        # Value
        value_label = ctk.CTkLabel(
            card, 
            text=value, 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        value_label.pack(padx=15, pady=(0, 15))
        
        return card
    
    @staticmethod
    def create_progress_dialog(parent, title: str = "Processing"):
        """Create a progress dialog window"""
        dialog = ctk.CTkToplevel(parent)
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.transient(parent)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (200 // 2)
        dialog.geometry(f"400x200+{x}+{y}")
        
        # Content
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            main_frame, 
            text=title, 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        
        status_label = ctk.CTkLabel(main_frame, text="Initializing...")
        status_label.pack(pady=5)
        
        progress_bar = ctk.CTkProgressBar(main_frame, width=300)
        progress_bar.pack(pady=20)
        progress_bar.set(0)
        
        # Cancel button
        cancel_button = ctk.CTkButton(
            main_frame, 
            text="Cancel", 
            command=dialog.destroy,
            width=100
        )
        cancel_button.pack(pady=10)
        
        return dialog, status_label, progress_bar, cancel_button

class AsyncTaskManager:
    """Manages async tasks with UI updates"""
    
    def __init__(self, parent_widget):
        self.parent = parent_widget
        self.tasks = []
        self.current_task = None
    
    def run_task(self, task_func: Callable, callback: Optional[Callable] = None, 
                 progress_callback: Optional[Callable] = None):
        """Run a task asynchronously with progress updates"""
        
        def task_wrapper():
            try:
                if progress_callback:
                    result = task_func(progress_callback)
                else:
                    result = task_func()
                
                # Schedule callback on main thread
                if callback:
                    self.parent.after(0, lambda: callback(result, None))
                    
            except Exception as e:
                if callback:
                    self.parent.after(0, lambda: callback(None, e))
        
        thread = threading.Thread(target=task_wrapper)
        thread.daemon = True
        thread.start()
        
        self.current_task = thread
        return thread

class DataTable:
    """A custom data table component"""
    
    def __init__(self, parent, columns: list, height: int = 300):
        self.parent = parent
        self.columns = columns
        self.data = []
        
        # Create frame
        self.frame = ctk.CTkFrame(parent)
        
        # Create treeview with custom styling
        style = ttk.Style()
        style.theme_use("clam")
        
        # Configure treeview style for dark theme
        style.configure("Treeview", 
                       background="#2b2b2b",
                       foreground="white",
                       fieldbackground="#2b2b2b",
                       borderwidth=0)
        style.configure("Treeview.Heading",
                       background="#1f1f1f",
                       foreground="white",
                       relief="flat")
        
        # Create treeview
        self.tree = ttk.Treeview(self.frame, columns=columns, show="headings", height=height//20)
        
        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(self.frame, orient="horizontal", command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack widgets
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Configure grid weights
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
    
    def insert_data(self, data: list):
        """Insert data into the table"""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Insert new data
        for row in data:
            self.tree.insert("", "end", values=row)
        
        self.data = data
    
    def get_frame(self):
        """Get the table frame widget"""
        return self.frame
    
    def get_selected(self):
        """Get selected row data"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            return item['values']
        return None

class NotificationManager:
    """Manages toast notifications"""
    
    def __init__(self, parent):
        self.parent = parent
        self.notifications = []
    
    def show_notification(self, message: str, type: str = "info", duration: int = 3000):
        """Show a toast notification"""
        # Create notification window
        notification = ctk.CTkToplevel(self.parent)
        notification.withdraw()  # Hide initially
        
        # Configure window
        notification.overrideredirect(True)
        notification.attributes("-topmost", True)
        
        # Colors based on type
        colors = {
            "info": ("#3b82f6", "#1e40af"),
            "success": ("#10b981", "#047857"),
            "warning": ("#f59e0b", "#d97706"),
            "error": ("#ef4444", "#dc2626")
        }
        
        bg_color, border_color = colors.get(type, colors["info"])
        
        # Create content frame
        frame = ctk.CTkFrame(notification, fg_color=bg_color, border_width=2, border_color=border_color)
        frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Message label
        label = ctk.CTkLabel(
            frame, 
            text=message, 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="white"
        )
        label.pack(padx=15, pady=10)
        
        # Position notification
        notification.update_idletasks()
        width = notification.winfo_reqwidth()
        height = notification.winfo_reqheight()
        
        screen_width = notification.winfo_screenwidth()
        screen_height = notification.winfo_screenheight()
        
        x = screen_width - width - 20
        y = 20 + len(self.notifications) * (height + 10)
        
        notification.geometry(f"{width}x{height}+{x}+{y}")
        notification.deiconify()  # Show notification
        
        # Store notification
        self.notifications.append(notification)
        
        # Auto-remove after duration
        def remove_notification():
            if notification in self.notifications:
                self.notifications.remove(notification)
                notification.destroy()
                # Reposition remaining notifications
                self._reposition_notifications()
        
        notification.after(duration, remove_notification)
        
        return notification
    
    def _reposition_notifications(self):
        """Reposition all visible notifications"""
        for i, notification in enumerate(self.notifications):
            if notification.winfo_exists():
                notification.update_idletasks()
                width = notification.winfo_width()
                height = notification.winfo_height()
                
                screen_width = notification.winfo_screenwidth()
                x = screen_width - width - 20
                y = 20 + i * (height + 10)
                
                notification.geometry(f"+{x}+{y}")

class ThemeManager:
    """Manages application themes"""
    
    def __init__(self):
        self.current_theme = "dark"
        self.themes = {
            "dark": {
                "bg_color": "#1a1a1a",
                "fg_color": "#2b2b2b",
                "text_color": "white",
                "button_color": "#3b82f6",
                "button_hover_color": "#2563eb"
            },
            "light": {
                "bg_color": "#ffffff",
                "fg_color": "#f1f5f9",
                "text_color": "black",
                "button_color": "#3b82f6",
                "button_hover_color": "#2563eb"
            }
        }
    
    def get_theme(self, theme_name: str = None):
        """Get theme configuration"""
        if theme_name is None:
            theme_name = self.current_theme
        return self.themes.get(theme_name, self.themes["dark"])
    
    def switch_theme(self, theme_name: str):
        """Switch to a different theme"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            ctk.set_appearance_mode(theme_name)
            return True
        return False