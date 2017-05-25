'''fonty.fonty: entry point for fonty'''
import click


@click.group()
def main():
    '''Entry function for fonty'''
    pass


@click.command()
@click.argument('name')
def install(name):
    '''Installs a font'''
    click.echo('Installing font ' + name)


@click.command()
@click.argument('name')
def uninstall(name):
    '''Uninstalls a font'''
    click.echo('Uninstalling font ' + name)


# register commands
main.add_command(install)
main.add_command(uninstall)
