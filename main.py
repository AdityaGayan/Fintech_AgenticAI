import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    print("Launching FinTech Agentic RE Platform...")
    
    # Resolve the path to the streamlit app safely
    app_path = Path("src") / "ui" / "app.py"
    
    # Launch Streamlit
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path)])