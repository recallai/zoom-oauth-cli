import click
import requests
from pyngrok import ngrok

from .config import NGROK_PORT, NGROK_SUBDOMAIN, NGROK_URL
from .exceptions import ZoomAPIError
from .http import serve_token
from .oauth import get_access_token


@click.group()
def zak():
    pass


@zak.command()
def get():
    access_token = get_access_token()
    print(retrieve_zak(access_token))


@zak.command()
def serve():
    def token_callback():
        access_token = get_access_token()
        return retrieve_zak(access_token)

    print(f"Serving ZAK token at {NGROK_URL}")
    ngrok.connect(
        addr=NGROK_PORT,
        subdomain=NGROK_SUBDOMAIN,
    )
    serve_token(NGROK_PORT, token_callback)


def retrieve_zak(token):
    resp = requests.get(
        "https://api.zoom.us/v2/users/me/zak",
        headers={"Authorization": f"Bearer {token}"},
    )
    data = resp.json()
    if "code" in data:
        raise ZoomAPIError(f"{data['code']}: {data['message']}")
    return data["token"]
