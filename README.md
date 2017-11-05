<p align="center">
  <img src="https://raw.githubusercontent.com/jamesssooi/fonty/feat/readme/art/logo.png" alt="Logo of fonty">
</p>

<h3 align="center">A friendly CLI tool for installing, managing and converting fonts</h3>

**fonty** is a command line interface that helps you simplify your font management workflow by allowing you to install and uninstall fonts like a package manager (think npm, apt-get, chocolatey). It can also help you create webfonts and generate @font-face declarations so that you can focus on building great websites.
## Table of Contents
* [Installation](#installation)
* [Basic Usage](#)
    * [Installing and Uninstalling Fonts](#)
    * [Listing Installed Fonts](#)
    * [Generating Webfonts](#)
    * [Managing Font Sources](#)
* [Commands](#)
    * [`fonty install`](#)
    * [`fonty uninstall`](#)
    * [`fonty list`](#)
    * [`fonty webfont`](#)
    * [`fonty source`](#)
* [Contributing](#)
* [License](#)

## Installation
*__Prerequisites__: Please make sure you have at least [Python 3](https://www.python.org/downloads/) installed*

```bash
$ pip install fonty
```

**fonty** is only available for macOS and Windows for now. Linux support is planned.

## Basic Usage
### Installing fonts
```bash
$ fonty install 'Open Sans'
```
