from app import app, socketio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(
        app, 
        debug=True, 
        host='0.0.0.0', 
        port=port,
        allow_unsafe_werkzeug=True
    )
