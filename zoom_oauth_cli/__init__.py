import click

from zoom_oauth_cli.join_token import join_token
from zoom_oauth_cli.oauth import oauth
from zoom_oauth_cli.zak import zak


@click.group()
def cli():
    pass


cli.add_command(oauth)
cli.add_command(join_token)
cli.add_command(zak)
