'''fonty.fonty: entry point for fonty'''
import click
import colorama
from fonty.commands.install import cli_install
from fonty.commands.source import cli_source

colorama.init()

@click.group()
def main():
    '''Entry function for fonty'''
    pass

@click.command()
@click.argument('variant', nargs=-1)
def test(variant):
    '''Testing command'''
    # from fonty.lib.variants import FontAttribute
    # variant = ' '.join(variant)
    # attr = FontAttribute.parse(variant)
    # attr.print(output=True, long=True)
    from fonty.lib.list_fonts import get_user_fonts
    get_user_fonts()

# Register commands
main.add_command(cli_install)
main.add_command(cli_source)
main.add_command(test)
