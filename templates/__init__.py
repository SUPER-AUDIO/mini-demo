"""
HTML Template System for SuperAudio Mini
Provides functions to load and render HTML templates with dynamic content.
"""

import os
from typing import Dict, Any, Optional
from string import Template

class HTMLTemplateLoader:
    """Loads and renders HTML templates with dynamic content."""
    
    def __init__(self, template_dir: str = "templates"):
        self.template_dir = template_dir
        self._template_cache = {}
    
    def load_template(self, template_name: str) -> str:
        """Load a template file and cache it."""
        if template_name in self._template_cache:
            return self._template_cache[template_name]
        
        template_path = os.path.join(self.template_dir, template_name)
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
                self._template_cache[template_name] = template_content
                return template_content
        except FileNotFoundError:
            print(f"Warning: Template file {template_path} not found.")
            return ""
        except Exception as e:
            print(f"Error loading template {template_path}: {e}")
            return ""
    
    def render_template(self, template_name: str, **kwargs) -> str:
        """Render a template with the provided variables."""
        template_content = self.load_template(template_name)
        if not template_content:
            return ""
        
        try:
            # Use safe_substitute to avoid KeyError for missing variables
            template = Template(template_content)
            return template.safe_substitute(**kwargs)
        except Exception as e:
            print(f"Error rendering template {template_name}: {e}")
            return template_content
    
    def render_header(self, **kwargs) -> str:
        """Render the header template."""
        return self.render_template("header.html", **kwargs)
    
    def render_status_card(self, status_type: str = "info", icon: str = "ℹ️", 
                          title: str = "Status", message: str = "", 
                          additional_content: str = "", action_buttons: str = "") -> str:
        """Render a status card with the provided parameters."""
        return self.render_template("status_card.html",
                                  status_type=status_type,
                                  icon=icon,
                                  title=title,
                                  message=message,
                                  additional_content=additional_content,
                                  action_buttons=action_buttons)
    
    def render_audio_visualizer(self, title: str = "Audio", audio_id: str = "audio", 
                               duration: str = "0:00", format: str = "WAV",
                               sample_rate: str = "44100", channels: str = "2",
                               bitrate: str = "1411 kbps") -> str:
        """Render an audio visualizer component."""
        return self.render_template("audio_visualizer.html",
                                  title=title,
                                  audio_id=audio_id,
                                  duration=duration,
                                  format=format,
                                  sample_rate=sample_rate,
                                  channels=channels,
                                  bitrate=bitrate)
    
    def render_processing_panel(self) -> str:
        """Render the processing panel."""
        return self.render_template("processing_panel.html")
    
    def render_chat_message(self, message_type: str = "user", avatar_url: str = "",
                           sender: str = "User", timestamp: str = "", 
                           content: str = "", message_id: str = "",
                           status: str = "online", additional_actions: str = "") -> str:
        """Render a chat message."""
        return self.render_template("chat_message.html",
                                  message_type=message_type,
                                  avatar_url=avatar_url,
                                  sender=sender,
                                  timestamp=timestamp,
                                  content=content,
                                  message_id=message_id,
                                  status=status,
                                  additional_actions=additional_actions)
    
    def render_tool_card(self, icon: str = "🔧", name: str = "Tool",
                        category: str = "Audio", status: str = "available",
                        description: str = "", parameters: str = "",
                        tool_id: str = "", usage_count: str = "0",
                        success_rate: str = "100") -> str:
        """Render a tool card."""
        return self.render_template("tool_card.html",
                                  icon=icon,
                                  name=name,
                                  category=category,
                                  status=status,
                                  description=description,
                                  parameters=parameters,
                                  tool_id=tool_id,
                                  usage_count=usage_count,
                                  success_rate=success_rate)
    
    def render_javascript(self) -> str:
        """Render the JavaScript functions."""
        return self.render_template("javascript_functions.html")

# Global template loader instance
template_loader = HTMLTemplateLoader()

# Convenience functions
def render_header(**kwargs) -> str:
    return template_loader.render_header(**kwargs)

def render_status_card(**kwargs) -> str:
    return template_loader.render_status_card(**kwargs)

def render_audio_visualizer(**kwargs) -> str:
    return template_loader.render_audio_visualizer(**kwargs)

def render_processing_panel(**kwargs) -> str:
    return template_loader.render_processing_panel(**kwargs)

def render_chat_message(**kwargs) -> str:
    return template_loader.render_chat_message(**kwargs)

def render_tool_card(**kwargs) -> str:
    return template_loader.render_tool_card(**kwargs)

def render_javascript(**kwargs) -> str:
    return template_loader.render_javascript(**kwargs)
