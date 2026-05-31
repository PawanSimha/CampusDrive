from app import app
import os

if __name__ == "__main__":
    from waitress import serve
    port = int(os.environ.get("PORT", 5001))
    print(f"Serving CampusDrive on port {port} using Waitress...")
    serve(app, host="0.0.0.0", port=port)
