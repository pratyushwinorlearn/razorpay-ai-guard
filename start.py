import subprocess
import sys
import time
import os
import webbrowser

def main():
    print("\n🚀 Booting Razorpay AI Buildathon Project...\n")
    root_dir = os.getcwd()

    # 1. Start the FastAPI Backend
    print("▶️ Starting Backend Server (Port 8080)...")
    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--port", "8080"],
        cwd=os.path.join(root_dir, "backend")
    )

    # 2. Start the Vite React Frontend
    print("▶️ Starting Frontend Server...")
    frontend = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=os.path.join(root_dir, "frontend"),
        shell=True
    )

    # 3. Wait for boot and open browser
    print("\n⏳ Waiting for servers to spin up...")
    time.sleep(3) # Give Vite a second to bind to the port
    print("🌐 Opening Merchant Dashboard...")
    webbrowser.open("http://localhost:5173")

    print("\n✅ System is LIVE. Leave this terminal open.")
    print("💡 To test the AI, open ONE new terminal and run: python agent/buyer.py\n")

    try:
        # Keep the script running until you hit Ctrl+C
        backend.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers gracefully...")
        backend.terminate()
        frontend.terminate()
        print("Goodbye!")

if __name__ == "__main__":
    main()