from dotenv import load_dotenv

load_dotenv()

# OR, the same with increased verbosity
load_dotenv(verbose=True)

# OR, explicitly providing path to '.env'
from pathlib import Path  # python3 only

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

import os
BOT_TOKEN = os.getenv("BOT_TOKEN")
W_TOKEN = os.getenv("W_TOKEN")