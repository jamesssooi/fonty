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
**fonty** can help you convert fonts to `woff` and `woff2` formats, which is supported by all major browsers (IE9 and above) as well as generate their `@font-face` declarations.

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
# Example: `fonty install Lato`

> fonty install <FONT URL> [OPTIONS]
# Example: `fonty install http://url/to/Lato.ttf`

> fonty install --files <FONT FILES> [OPTIONS]
# Example: `fonty install --files *.ttf`
```
**Installs a font into the computer or into a directory.**

In it's default behaviour, **fonty** searches through your [subscribed sources](#) to download and install the specified font automatically. Alternatively, it can also support downloading `.ttf`/`.otf` files directly, or if a `--files` flag is passed, **fonty** can help you install local font files on your computer.

##### Options

* **`-v`/`--variants`** `text`
    * A comma separated list of the [Fonty Attribute](#) format, with no spaces in between.
* **`-o`/`--output`** `path`
    * Output fonts into this directory. If supplied, the fonts won't be installed into the system.
* **`--files`** `flag`
    * If provided, read arguments as a list of font files to be installed. Files can be a glob pattern.

---

#### [3.2 &nbsp;&nbsp; `fonty uninstall`](#)
```bash
> fonty uninstall <FONT NAME> [OPTIONS]
```

**Uninstalls a font from this computer.**

This command uninstalls the specified font from the computer and deletes them into the Trash or Recycle Bin.

##### Options

* **`-v`/`--variants`** `text`
    * A list of comma separated values with no spaces in between using the [Fonty Attribute](#) format.

---

#### [3.3 &nbsp;&nbsp; `fonty list`](#)
```bash
> fonty list [OPTIONS]
> fonty list <FONT NAME> [OPTIONS]
```

**Show a list of installed fonts**.

This command shows a list of all installed fonts in this computer, scanned through the user's font directory.

If a specific font name is specified, then this command prints a list of all the font files of that particular family.

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

**Convert fonts to webfonts and generate @font-face declarations**.

This command convert fonts to `.woff` and `.woff2` formats, as well as generate their @font-face CSS declaration into a file named `styles.css`.

**fonty's** default behaviour is to convert a list of font files that you have provided. Alternative, it can also download fonts using the `—download` flag, or use an existing installed font on your computer using the `—installed` flag.

The [Web Open Font Format (WOFF)](#) is a widely supported font format for web browsers, and should be sufficient for a large majority of use cases. You can read the compatibility tables on [caniuse.com](https://caniuse.com/#search=woff).

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
**Adds a new font source.**

This command allows you to add and subscribe to a new font source. This allows you to have instant access to all of the source's fonts through the `fonty install` command.

---

```bash
> fonty source remove <SOURCE ID or SOURCE URL>
```

**Removes a subscribed font source.**

---

```bash
> fonty source list
```

**Print a list of subscribed font sources.**

This command shows a list of all subscribed sources, along with their IDs, update status, and number of available fonts.

---

```bash
> fonty source update [OPTIONS]
```

**Check all subscribed sources for available updates.**

When font sources are subscribed to, a local copy of the source is downloaded into your computer, which will result in the local copy being outdated when the font source is updated. By default, **fonty** will automatically check for available updates periodically. This command however, offers you a way to force all sources to check for available updates.

* **`f`/`--force`** `flag`
    * If provided, force all sources to be redownloaded and rebuild the search index.


## [4 &nbsp;&nbsp; Font Sources](#)

**fonty** relies on font sources to resolve, download and install fonts. A font source is simply a JSON file containing an index of its fonts, and where to download them.

With **fonty**, you can subscribe to multiple font sources at the same time to have instant access to a wide variety of fonts through the `fonty install` command.

### [4.1 &nbsp;&nbsp; Default sources](#)

Right out of the box, **fonty** is automatically subscribed to a few default font sources so you can enjoy the benefits of using **fonty** rightaway. These default sources are:

1. **fonty's Google Fonts Repository**
    * The entire [Google Fonts](#) repository, in a format that **fonty** understands.
    * **URL:** https://sources.fonty.io/googlefonts

2. **fonty's Open Source Fonts Repository**
    * A self-maintained list of open source fonts across the web.
    * **URL**: https://sources.fonty.io/fontyfonts

You can unsubscribe and subscribe from these sources at anytime. See the [`fonty source`](#) command.

### [4.2 &nbsp;&nbsp; Hosting your own](#)

You may wish to host your own repository for your personal usage, or perhaps you might want to make a set of fonts available for your entire team. A repository of fonts is a powerful concept that allows people to share and use fonts effortlessly.

Creating your own font sources is incredibly simple. At its core, a font source is simply a publicly accessible JSON file containing an index of its fonts and where to download them from.

You can check out the specification of the [fonty json source](#) format.

## [5 &nbsp;&nbsp; Specifying Font Variants](#)

**fonty** uses a custom, CSS inspired syntax to notate font variants such as font weights, italicisation, obliqueness, stretchness, and etc. The goal is to create a notation that is short and concise (for easier input), while mantaining clarity.




