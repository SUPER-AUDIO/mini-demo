
"""
Assistant Capabilities Tool

Lists the currently available tools (from the registry) with brief descriptions
and parameter keys. Useful when the user asks what the agent can do.
"""

import json
from typing import Tuple, Dict, Any

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api import tool, Audio, AudioBuf, REG, TOOL_MESSAGES


def _load_tools_config() -> Dict[str, Any]:
    try:
        with open("tools_config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


@tool("list_capabilities")
def list_capabilities(audio: Audio, sr: int) -> AudioBuf:
    """
    Report current capabilities grouped concisely.
    Returns the input audio unchanged; writes a compact grouped summary to TOOL_MESSAGES.
    """
    try:
        tool_names = sorted(REG._tools.keys())

        groups = {
            "Generation": [],
            "Analysis": [],
            "Enhancement / Cleanup": [],
            "Effects": [],
            "EQ / Filters": [],
            "Utility / Master": [],
            "Meta": [],
            "Other": [],
        }

        def add(group: str, name: str):
            if name not in groups[group]:
                groups[group].append(name)

        for name in tool_names:
            lname = name.lower()
            if lname in {"text_to_speech"}:
                add("Generation", name)
            elif lname in {"speech_recognition"}:
                add("Analysis", name)
            elif lname in {"speech_enhancement", "speechbrain_enhancement", "compressor", "noise_gate", "highpass_filter", "lowpass_filter"}:
                add("Enhancement / Cleanup", name)
            elif lname in {"reverb", "delay", "chorus", "phaser", "distortion", "clipping", "bitcrush", "voice_conversion"}:
                add("Effects", name)
            elif lname in {"peak_filter", "high_shelf", "low_shelf", "ladder_filter"}:
                add("EQ / Filters", name)
            elif lname in {"gain", "limiter", "invert", "mp3_compressor", "gsm_compressor", "add_latency"}:
                add("Utility / Master", name)
            elif lname in {"list_capabilities"}:
                add("Meta", name)
            else:
                add("Other", name)

        # Build compact markdown lines, skipping empty groups
        lines = []
        for group in [
            "Generation", "Analysis", "Enhancement / Cleanup", "Effects", "EQ / Filters", "Utility / Master", "Meta", "Other"
        ]:
            names = groups[group]
            if names:
                names_str = ", ".join(sorted(names))
                lines.append(f"- {group}: {names_str}")

        msg = "\n".join(lines) if lines else "No tools registered."
        TOOL_MESSAGES.add_message("list_capabilities", f"🧰 **Available Tools (grouped)**\n\n{msg}")
    except Exception as e:
        TOOL_MESSAGES.add_message("list_capabilities", f"❌ Failed to list tools: {e}")

    return audio, sr


