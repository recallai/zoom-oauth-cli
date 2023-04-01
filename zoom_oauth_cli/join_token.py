import click
import requests
from pyngrok import ngrok

from .config import NGROK_PORT, NGROK_SUBDOMAIN, NGROK_URL
from .exceptions import ZoomAPIError
from .http import serve_token
from .oauth import get_access_token


@click.group()
def join_token():
    pass


@join_token.command()
@click.argument("meeting_id")
def get(meeting_id):
    access_token = get_access_token()
    print(retrieve_join_token(access_token, meeting_id))


@join_token.command()
@click.argument("meeting_id")
def serve(meeting_id):
    def token_callback():
        access_token = get_access_token()
        return retrieve_join_token(access_token, meeting_id)

    print(f"Serving join token at {NGROK_URL}")
    ngrok.connect(
        addr=NGROK_PORT,
        subdomain=NGROK_SUBDOMAIN,
    )
    serve_token(NGROK_PORT, token_callback)


def retrieve_join_token(token, meeting_id):
    resp = requests.get(
        f"https://api.zoom.us/v2/meetings/{meeting_id}/jointoken/local_recording",
        headers={"Authorization": f"Bearer {token}"},
    )
    data = resp.json()
    if "code" in data:
        raise ZoomAPIError(f"{data['code']}: {data['message']}")
    return data["token"]
