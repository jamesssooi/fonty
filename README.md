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

## Installation
*__Prerequisites__: Please make sure you have at least [Python 3](https://www.python.org/downloads/) installed*

```bash
$ pip install fonty
```

**fonty** is only available for macOS and Windows for now. Linux support is planned.

## Basic Usage
Append any command with `--help` for a detailed help text of what you can do.
```bash
$ fonty [command] --help
```

### [1&nbsp;&nbsp;Installing and uninstalling fonts](#)
#### [1.1&nbsp;&nbsp;Installing fonts](#)
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
*__Note__: List of variants must be comma-separated values with no space*

#### [1.2&nbsp;&nbsp;Uninstalling fonts](#)
Uninstalling a font family from your computer:
```bash
› fonty uninstall Lato
```

Uninstalling only a specific variant:
```bash
# This only removes the 900i (Black Italic) variant of the font
› fonty uninstall Lato -v 900i
```
