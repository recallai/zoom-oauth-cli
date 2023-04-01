import base64
import json
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlencode, urlparse

import click
import requests
from pyngrok import ngrok

from .config import CLIENT_ID, CLIENT_SECRET, NGROK_PORT, NGROK_SUBDOMAIN, NGROK_URL
from .exceptions import ZoomAPIError


@click.group()
def oauth():
    pass


@oauth.command()
def status():
    try:
        get_access_token()
        print("Connected")
    except ZoomAPIError as exc:
        print(f"Not Connected:\n\t{exc}")


@oauth.command()
def connect():
    print("Connecting Zoom OAuth...")

    auth_url = generate_auth_url(NGROK_URL, CLIENT_ID)
    print(f"\tVisit the auth URL: {auth_url}")

    print("\tInitiating Ngrok tunnel...")
    http_tunnel = ngrok.connect(
        addr=NGROK_PORT,
        subdomain=NGROK_SUBDOMAIN,
    )

    print(f"\tListening on port {NGROK_PORT} for callback...")
    httpd = HTTPServer(("", NGROK_PORT), OAuthCallbackHandler)
    httpd.handle_request()
    if not httpd.oauth_code:
        print("Error: Callback did not include code parameter")
        return
    ngrok.disconnect(http_tunnel.public_url)

    print("\tRetrieving tokens using code...")
    try:
        (access_token, expires_in, refresh_token) = exchange_code_for_tokens(
            httpd.oauth_code, NGROK_URL
        )
    except ZoomAPIError as exc:
        print(exc)
        return

    print("\tSaving tokens...")
    store_access_token(access_token, expires_in)
    store_refresh_token(refresh_token)
    print("Done")


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        qs = parse_qs(urlparse(self.path).query)
        self.server.oauth_code = qs.get("code", [None])[0]
        self.send_response(204)


def generate_auth_url(redirect_uri, client_id):
    base_url = "https://zoom.us/oauth/authorize"
    query_params = {
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "client_id": client_id,
    }
    return base_url + "?" + urlencode(query_params)


def exchange_code_for_tokens(code, redirect_uri):
    resp = requests.post(
        "https://zoom.us/oauth/token",
        headers={
            "Authorization": build_basic_auth_string(),
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        },
    )
    data = resp.json()
    if "error" in data:
        raise ZoomAPIError(f"{data['error']}: {data['reason']}")
    return data["access_token"], data["expires_in"], data["refresh_token"]


def get_access_token():
    if existing_access_token := load_access_token():
        return existing_access_token

    refresh_token = load_refresh_token()
    resp = requests.post(
        "https://zoom.us/oauth/token",
        headers={
            "Authorization": build_basic_auth_string(),
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
    )
    data = resp.json()
    if "error" in data:
        raise ZoomAPIError(f"{data['error']}: {data['reason']}")
    store_refresh_token(data["refresh_token"])
    return data["access_token"]


def build_basic_auth_string():
    return "Basic " + base64.b64encode(
        f"{CLIENT_ID}:{CLIENT_SECRET}".encode("ascii")
    ).decode("ascii")


def load_access_token():
    try:
        with open("tokens.json", "r") as f:
            data = json.load(f)
            expires_at = data["expires_at"]
            if expires_at < time.time():
                return None
            return data["access_token"]
    except (IOError, KeyError):
        return None


def load_refresh_token():
    try:
        with open("tokens.json", "r") as f:
            return json.load(f)["refresh_token"]
    except (IOError, KeyError):
        raise ValueError("Refresh token not found.")


def store_access_token(access_token, expires_in):
    def fn(tokens):
        tokens["access_token"] = access_token
        tokens["expires_at"] = int(time.time()) + expires_in
        return tokens

    modify_tokens_json(fn)


def store_refresh_token(refresh_token):
    def fn(tokens):
        tokens["refresh_token"] = refresh_token
        return tokens

    modify_tokens_json(fn)


def modify_tokens_json(fn):
    try:
        with open("tokens.json", "r") as f:
            tokens = json.load(f)
    except FileNotFoundError:
        tokens = {}
    with open("tokens.json", "w") as f:
        json.dump(fn(tokens), f)
