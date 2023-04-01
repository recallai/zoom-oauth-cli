import os
import sys


def get_env_or_err(env):
    try:
        return os.environ[env]
    except KeyError:
        print(f"Environment variable {env} is required.")
        sys.exit(1)


CLIENT_ID = get_env_or_err("CLIENT_ID")
CLIENT_SECRET = get_env_or_err("CLIENT_SECRET")

NGROK_PORT = int(get_env_or_err("NGROK_PORT"))
NGROK_SUBDOMAIN = get_env_or_err("NGROK_SUBDOMAIN")
NGROK_URL = f"https://{NGROK_SUBDOMAIN}.ngrok.io/"
