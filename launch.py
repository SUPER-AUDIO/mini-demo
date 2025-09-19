#!/usr/bin/env python3
"""
SuperAudio Mini Launcher

Choose which interface to launch:
- Main App: Full AI-powered audio processing with natural language
- Debug Tool: Individual tool testing with parameter controls
"""

import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="SuperAudio Mini Launcher")
    parser.add_argument(
        "--mode", 
        choices=["main", "debug", "all"], 
        default="main",
        help="Which interface to launch (default: main)"
    )
    parser.add_argument(
        "--port-main", 
        type=int, 
        default=7860,
        help="Port for main app (default: 7860)"
    )
    parser.add_argument(
        "--port-debug", 
        type=int, 
        default=7861,
        help="Port for debug tool (default: 7861)"
    )
    parser.add_argument(
        "--share", 
        action="store_true",
        help="Create shareable Gradio links"
    )
    
    args = parser.parse_args()
    
    print("🎵 SuperAudio Mini Launcher")
    print("=" * 40)
    
    if args.mode == "main":
        print("🚀 Launching Main App (AI-Powered Audio Processing)")
        print(f"📡 URL: http://localhost:{args.port_main}")
        
        from app import create_interface
        interface = create_interface()
        interface.launch(
            server_name="0.0.0.0",
            server_port=args.port_main,
            share=args.share
        )
        
    elif args.mode == "debug":
        print("🔧 Launching Debug Tool (Individual Tool Testing)")
        print(f"📡 URL: http://localhost:{args.port_debug}")
        
        from debug_tools import create_debug_interface
        interface = create_debug_interface()
        interface.launch(
            server_name="0.0.0.0",
            server_port=args.port_debug,
            share=args.share
        )
        
    elif args.mode == "all":
        print("🚀 Launching Both Interfaces")
        print(f"📡 Main App: http://localhost:{args.port_main}")
        print(f"🔧 Debug Tool: http://localhost:{args.port_debug}")
        
        import threading
        import time
        
        def launch_main():
            from app import create_interface
            interface = create_interface()
            interface.launch(
                server_name="0.0.0.0",
                server_port=args.port_main,
                share=args.share,
                prevent_thread_lock=True
            )
        
        def launch_debug():
            time.sleep(2)  # Small delay to avoid port conflicts
            from debug_tools import create_debug_interface
            interface = create_debug_interface()
            interface.launch(
                server_name="0.0.0.0",
                server_port=args.port_debug,
                share=args.share,
                prevent_thread_lock=True
            )
        
        # Launch both in separate threads
        main_thread = threading.Thread(target=launch_main)
        debug_thread = threading.Thread(target=launch_debug)
        
        main_thread.start()
        debug_thread.start()
        
        try:
            main_thread.join()
            debug_thread.join()
        except KeyboardInterrupt:
            print("\n👋 Shutting down...")
            sys.exit(0)

if __name__ == "__main__":
    main()
