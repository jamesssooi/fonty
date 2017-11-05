<p align="center">
  <img src="https://raw.githubusercontent.com/jamesssooi/fonty/feat/readme/art/logo.png" alt="Logo of fonty">
</p>

<h3 align="center">A friendly CLI tool for installing, managing and converting fonts</h3>

**fonty** is a command line interface that helps you simplify your font management workflow by allowing you to install and uninstall fonts like a package manager (think npm, apt-get, chocolatey). It can also help you create webfonts and generate @font-face declarations so that you can focus on building great websites.
## Table of Contents
* [Installation](#installation)
* [Basic Usage](#)
    * [Installing and uninstalling fonts](#)
    * [Listing installed fonts](#)
    * [Generating webfonts](#)
    * [Managing font sources](#)
* [Commands](#)
    * [`fonty install`](#)
    * [`fonty uninstall`](#)
    * [`fonty list`](#)
    * [`fonty webfont`](#)
    * [`fonty source`](#)
* [Font Sources](#)
    * [Default sources](#)
    * [Hosting your own source](#)
* [Roadmap](#)
* [Contributing](#)
* [License](#)

## [1 &nbsp;&nbsp; Installation](#)
*__Prerequisites__: Please make sure you have at least [Python 3](https://www.python.org/downloads/) installed*

```bash
$ pip install fonty
```

**fonty** is only available for macOS and Windows for now. Linux support is planned.

## [2 &nbsp;&nbsp; Basic Usage](#)
Append any command with `--help` for a detailed help text of what you can do.
```bash
$ fonty [command] --help
```

### [2.1 &nbsp;&nbsp; Installing and uninstalling fonts](#)
#### [2.1.1 &nbsp;&nbsp; Installing fonts](#)
Downloading and installing a font from [subscribed sources](#):
```bash
› fonty install Lato
```

Downloading a font into a directory:
```bash
› fonty install Lato -o "~/Desktop/Lato"
```

Download only the bold and bold italic variants of a font:
```bash
› fonty install Lato -v 700,700i
```

*__Further reading__: [`fonty install`](#)*

---

#### [2.1.2 &nbsp;&nbsp; Uninstalling fonts](#)
Uninstalling a font family from your computer:
```bash
› fonty uninstall Lato
```

Uninstalling only a specific variant:
```bash
# This only removes the 900i (Black Italic) variant of the font
› fonty uninstall Lato -v 900i
```

*__Further reading__: [`fonty uninstall`](#)*

---

### [2.2 &nbsp;&nbsp; Listing installed fonts](#)
List all installed fonts
```bash
› fonty list
```

List further details about a specific installed font
```bash
› fonty list Lato
```

*__Further reading__: [`fonty list`](#)*

---

### [2.3 &nbsp;&nbsp; Generating webfonts](#)
**fonty** can help you convert fonts to `woff` and `woff2` formats, which is supported by all major browsers (IE9 and above) as well as generate their `@fontface` declarations.

Download font from subscribed sources and generate webfonts into the current directory:
```bash
› fonty webfont Lato
```

Generate webfonts into a specific directory:
```bash
› fonty webfont Lato -o ./webfonts
```

Generate webfonts from `ttf`/`otf` files
```bash
› fonty webfont --files Lato.ttf Lato-Regular.ttf
```

Generate webfonts from an already installed font
```bash
› fonty webfont --installed Lato
```

*__Further reading__: [`fonty webfont`](#)*

---

### [2.3 &nbsp;&nbsp; Managing font sources](#)
**fonty** searches and downloads fonts from your list of subscribed sources. Upon installation, fonty automatically subscribes to a few [default sources](#). Here's how you can manage your subscriptions:

Adding a new font source:
```bash
› fonty source add http://url/to/source.json
```

Removing a font source:
```bash
# Deleting by URL
› fonty source remove http://url/to/source.json

# Deleting by ID
› fonty source remove e0f9cbd9977479825e1cd38aafb1660d
```

Show list of subscribed sources:
```bash
› fonty source list
```

Updating sources:
```bash
› fonty source update
```

*__Further reading__: [`fonty source`](#), [Font Sources](#)*

---

## [3 &nbsp;&nbsp; Commands Reference](#)
