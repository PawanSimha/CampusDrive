from app import app
from waitress import serve
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    print(f"🚀 Serving CampusConnect on port {port} using Waitress...")
    serve(app, host="0.0.0.0", port=port)
