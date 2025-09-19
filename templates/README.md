# SuperAudio Mini - HTML Template System

This directory contains the HTML template system for creating custom UI components in SuperAudio Mini. The templates are separated from the main application code for better maintainability and reusability.

## 📁 Directory Structure

```
templates/
├── __init__.py                 # Template loader and convenience functions
├── header.html                 # Custom header component
├── status_card.html           # Status notification cards
├── audio_visualizer.html      # Audio waveform visualizer
├── processing_panel.html      # Processing steps panel
├── chat_message.html          # Chat message components
├── tool_card.html             # Tool information cards
├── javascript_functions.html  # Custom JavaScript functions
└── README.md                  # This documentation
```

## 🚀 Quick Start

### 1. Basic Usage

```python
from templates import render_header, render_status_card

# Render a header
header_html = render_header()

# Render a status card
status_html = render_status_card(
    status_type="success",
    icon="✅",
    title="Success!",
    message="Operation completed successfully."
)
```

### 2. Integration with Gradio

```python
import gradio as gr
from templates import render_header, render_javascript

def create_interface():
    with gr.Blocks(css=custom_css) as interface:
        # Add custom header
        gr.HTML(render_header())
        
        # Your Gradio components here
        audio_input = gr.Audio(elem_classes=["custom-audio"])
        
        # Add JavaScript functions
        gr.HTML(render_javascript())
    
    return interface
```

## 🎨 Available Templates

### Header Component
```python
render_header() -> str
```
Creates a branded header with logo, status indicator, and progress bar.

### Status Cards
```python
render_status_card(
    status_type: str = "info",     # "success", "error", "warning", "info"
    icon: str = "ℹ️",
    title: str = "Status",
    message: str = "",
    additional_content: str = "",
    action_buttons: str = ""
) -> str
```

### Audio Visualizer
```python
render_audio_visualizer(
    title: str = "Audio",
    audio_id: str = "audio",
    duration: str = "0:00",
    format: str = "WAV",
    sample_rate: str = "44100",
    channels: str = "2",
    bitrate: str = "1411 kbps"
) -> str
```

### Processing Panel
```python
render_processing_panel() -> str
```
Shows a 4-step processing workflow with statistics.

### Chat Messages
```python
render_chat_message(
    message_type: str = "user",    # "user" or "bot"
    avatar_url: str = "",
    sender: str = "User",
    timestamp: str = "",
    content: str = "",
    message_id: str = "",
    status: str = "online",
    additional_actions: str = ""
) -> str
```

### Tool Cards
```python
render_tool_card(
    icon: str = "🔧",
    name: str = "Tool",
    category: str = "Audio",
    status: str = "available",      # "available", "busy", "unavailable"
    description: str = "",
    parameters: str = "",
    tool_id: str = "",
    usage_count: str = "0",
    success_rate: str = "100"
) -> str
```

### JavaScript Functions
```python
render_javascript() -> str
```
Includes all custom JavaScript functions for interactive features.

## 🎛️ CSS Classes

The templates use these CSS classes (defined in `static/components.css`):

### Layout Classes
- `.glass-card` - Glass morphism effect
- `.custom-header` - Header styling
- `.fade-in`, `.slide-up` - Animation classes

### Component Classes
- `.status-card` - Status notification styling
- `.audio-visualizer` - Audio component styling
- `.processing-panel` - Processing steps styling
- `.chat-message` - Chat message styling
- `.tool-card` - Tool card styling

### Interactive Classes
- `.btn-primary`, `.btn-secondary` - Button styling
- `.custom-input` - Input field styling
- `.custom-dropdown` - Dropdown styling

## 🎯 JavaScript Functions

The template system includes these JavaScript functions:

### Theme Management
```javascript
SuperAudioUI.toggleTheme()              // Switch between light/dark themes
```

### Progress & Notifications
```javascript
SuperAudioUI.updateProgress(id, percent) // Update progress bars
SuperAudioUI.showNotification(msg, type) // Show notifications
```

### Processing Steps
```javascript
SuperAudioUI.updateProcessingStep(step, status) // Update processing steps
SuperAudioUI.updateStats()                      // Update statistics
```

### Audio Controls
```javascript
SuperAudioUI.toggleAudio(audioId)       // Play/pause audio
SuperAudioUI.drawWaveform(canvasId, data) // Draw waveforms
```

## 📝 Template Variables

Templates use Python's `string.Template` syntax with `${variable}` placeholders:

```html
<div class="status-card ${status_type}">
    <h3>${title}</h3>
    <p>${message}</p>
</div>
```

## 🔧 Customization

### Adding New Templates

1. Create a new HTML file in the `templates/` directory
2. Add template variables using `${variable}` syntax
3. Add a render function to `__init__.py`:

```python
def render_my_component(self, param1: str = "default") -> str:
    return self.render_template("my_component.html", param1=param1)
```

### Modifying Existing Templates

1. Edit the HTML file directly
2. Add new CSS classes to `static/components.css`
3. Update the render function parameters if needed

### Custom Styling

Add your CSS to `static/components.css`:

```css
.my-custom-class {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    padding: 1rem;
}
```

## 🌙 Theme Support

The template system supports light/dark themes via CSS variables:

```css
:root {
    --primary-color: #6366f1;
    --dark-bg: #1f2937;
}

[data-theme="dark"] {
    --primary-color: #818cf8;
    --dark-bg: #000000;
}
```

Toggle themes with:
```javascript
SuperAudioUI.toggleTheme()
```

## 📱 Responsive Design

All templates include responsive design with mobile-first approach:

```css
@media (max-width: 768px) {
    .glass-card {
        padding: 1rem;
        margin: 0.5rem 0;
    }
}
```

## 🔍 Debugging

To debug template rendering:

1. Run `python example_usage.py` to see template output
2. Check browser console for JavaScript errors
3. Inspect CSS classes in browser developer tools

## 📚 Examples

See `example_usage.py` for comprehensive examples of all template functions.

## 🤝 Contributing

When adding new templates:

1. Follow the existing naming convention
2. Include comprehensive CSS styling
3. Add responsive design considerations
4. Update this README with documentation
5. Add examples to `example_usage.py`

## 📄 License

This template system is part of SuperAudio Mini and follows the same license terms.
