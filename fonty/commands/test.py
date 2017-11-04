'''test.py: Test command'''
import os

import click
from fonty.models.font import Font

@click.command('test')
@click.argument('font_path', type=click.Path())
def test(font_path):
    from fonty.lib.install_windows import install_fonts, uninstall_fonts

    font_path = 'C:\\Windows\\Fonts\\Lato-Regular.ttf'

    # Get bytes
    with open(font_path, 'rb') as f:
        font_bytes = f.read()

    font = Font(path_to_font=os.path.abspath(font_path),
                filename=os.path.basename(font_path),
                raw_bytes=font_bytes)
    
    uninstall_fonts([font])