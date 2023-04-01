# Zoom OAuth CLI
This is a set of scripts to make it easier to work with the Zoom OAuth system as a developer, specifically while developing bots.

## Prerequisites
You must have an Ngrok account, as well as Zoom OAuth credentials.

## Installation
This is a Python package, which can be installed with `pip install .`

## Quickstart
1. Complete the OAuth token flow
    ```
    $ zoom-oauth-cli oauth connect
    Connecting Zoom OAuth...
        Visit the auth URL: https://zoom.us/oauth/authorize?[REDACTED]
        Initiating Ngrok tunnel...
        Listening on port 5000 for callback...
    127.0.0.1 - - [01/Apr/2023 23:25:12] "GET /?code=[REDACTED] HTTP/1.1" 204 -
        Retrieving tokens using code...
        Saving tokens...
    Done
    ```
2. Retrieve your ZAK token
    ```
    $ zoom-oauth-cli zak get
    [REDACTED]
    ```
3. Create a URL that responds with your ZAK token. When creating a Recall bot, you can pass this URL as the `zoom.zak_token_url`
    ```
    $ zoom-oauth-cli zak serve
    Serving ZAK token at [REDACTED]
    ```