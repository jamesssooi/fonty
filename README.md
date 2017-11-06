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
> fonty install Lato
```

Downloading a font into a directory:
```bash
> fonty install Lato -o "~/Desktop/Lato"
```

Download only the bold and bold italic variants of a font:
```bash
> fonty install Lato -v 700,700i
```

*__Further reading__: [`fonty install`](#)*

---

#### [2.1.2 &nbsp;&nbsp; Uninstalling fonts](#)
Uninstalling a font family from your computer:
```bash
> fonty uninstall Lato
```

Uninstalling only a specific variant:
```bash
# This only removes the 900i (Black Italic) variant of the font
> fonty uninstall Lato -v 900i
```

*__Further reading__: [`fonty uninstall`](#)*

---

### [2.2 &nbsp;&nbsp; Listing installed fonts](#)
List all installed fonts
```bash
> fonty list
```

List further details about a specific installed font
```bash
> fonty list Lato
```

*__Further reading__: [`fonty list`](#)*

---

### [2.3 &nbsp;&nbsp; Generating webfonts](#)
**fonty** can help you convert fonts to `woff` and `woff2` formats, which is supported by all major browsers (IE9 and above) as well as generate their `@fontface` declarations.

Download font from subscribed sources and generate webfonts into the current directory:
```bash
> fonty webfont Lato
```

Generate webfonts into a specific directory:
```bash
> fonty webfont Lato -o ./webfonts
```

Generate webfonts from `ttf`/`otf` files
```bash
> fonty webfont --files Lato.ttf Lato-Regular.ttf
```

Generate webfonts from an already installed font
```bash
> fonty webfont --installed Lato
```

*__Further reading__: [`fonty webfont`](#)*

---

### [2.4 &nbsp;&nbsp; Managing font sources](#)
**fonty** searches and downloads fonts from your list of subscribed sources. Upon installation, fonty automatically subscribes to a few [default sources](#). Here's how you can manage your subscriptions:

Adding a new font source:
```bash
> fonty source add http://url/to/source.json
```

Removing a font source:
```bash
# Deleting by URL
> fonty source remove http://url/to/source.json

# Deleting by ID
> fonty source remove e0f9cbd9977479825e1cd38aafb1660d
```

Show list of subscribed sources:
```bash
> fonty source list
```

Updating sources:
```bash
> fonty source update
```

*__Further reading__: [`fonty source`](#), [Font Sources](#)*

---

## [3 &nbsp;&nbsp; Commands Reference](#)

#### [3.1 &nbsp;&nbsp; `fonty install`](#)
```bash
> fonty install <FONT NAME> [OPTIONS]
> fonty install --files <FONT FILES> [OPTIONS]
```
**Install a font into the computer or into a directory.**

**fonty** will download the fonts from the list of [subscribed sources](#). If a `--files` flag is passed, **fonty** will install fonts from the list of files provided.

##### Options

* **`-v`/`--variants`** `text`
    * A list of comma separated values with no spaces in between using the [Fonty Attribute](#) format.
* **`-o`/`--output`** `path`
    * Output fonts into this directory. If supplied, the fonts won't be installed into the system.
* **`--files`** `flag`
    * If provided, read arguments as a list of font files to be installed. Files can be a glob pattern.

---

#### [3.2 &nbsp;&nbsp; `fonty uninstall`](#)
```bash
> fonty uninstall <FONT NAME> [OPTIONS]
```

##### Options

* **`-v`/`--variants`** `text`
    * A list of comma separated values with no spaces in between using the [Fonty Attribute](#) format.

---

#### [3.3 &nbsp;&nbsp; `fonty list`](#)
```bash
> fonty list <FONT NAME?> [OPTIONS]
```

##### Options

* **`--rebuild`** `flag`
    * If provided, rebuild the font manifest file.

---

#### [3.3 &nbsp;&nbsp; `fonty webfont`](#)
```bash
> fonty webfont <FONT FILES> [OPTIONS]
> fonty webfont --download <FONT NAME> [OPTIONS]
> fonty webfont --installed <FONT NAME> [OPTIONS]
```

##### Options

* **`--download`** `flag`
    * If provided, download font from subscribed sources and convert.

* **`--installed`** `flag`
    * If provided, convert an existing font installed on the system.

* **`-o`/`--output`** `path`
    * Output webfonts into a specific directory.

---

#### [3.4 &nbsp;&nbsp; `fonty source`](#)
```bash
> fonty source add <SOURCE URL>
```
---

```bash
> fonty source remove <SOURCE ID or SOURCE URL>
```

---

```bash
> fonty source list
```

---

```bash
> fonty source update [OPTIONS]
```

* **`f`/`--force`** `flag`
    * If provided, force all sources to update and rebuild search index.