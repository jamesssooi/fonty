# Privacy
fonty collects a few simple, anonymous and non-personal usage data to better understand how users use fonty; and to identify interesting font usage statistics and trends.

As a privacy-conscious person who believes in keeping personal data personal, efforts has been made to fonty to ensure you have full and total control over how your data is collected:

* You can opt-out of telemetry anytime.
* Data collected is non-personal and non-identifying.
* Your IP address is discarded.
* Data is only reported and presented in the form of aggregates.

## What data is collected?
Telemetry data is sent in the form of events to a telemetry service. In all events, a common base data is collected in addition to its event-specific data.

### Base data
The following data is collected in all telemetry events.
* `timestamp`: The date and time the commmand was executed.
* `status_code`: The resulting status code of this command.
* `execution_time`: The duration it took to run this command.
* `fonty_version`: The current fonty version being used.
* `os_family`: The family of the current operating system.
* `os_version`: The version of the current operating system.
* `python_version`: The version of the current python executable.

### Event-specific data
The following additional data is collected depending on the command being run.

#### `FONT_INSTALL`
Called when the user initiates the `fonty install` command.
* `font_name`: The name of the font being installed (only when not files are provided)
* `font_source`: Either `local_files`, `remote_url`, `private_source` or `font_source`.
* `source_url`: The URL of the font source, only if the source is marked as `public`.
* `variants`: The list of variants the user provided.
* `output_dir`: A true/false value on whether the user provided an output directory.

#### `FONT_UNINSTALL`
Called when the user initiates the `fonty uninstall` command.
* `font_name`: The name of the font being uninstalled.
* `variants`: The list of variants the user provided.

#### `FONT_LIST`
Called when the user initiates the `font list` command.
* `has_font_name`: A true/false value on whether a font name is provided.
* `font_count`: The total number of fonts installed in the user's system.
* `family_count`: The total number of font families installed in the user's system.

#### `FONT_LIST_REBUILD`
Called when the user initiates the `font list --rebuild` command.
* No additional data is collected.

#### `FONT_CONVERT`
Called when the user initiates the `fonty webfont` command.
* `font_source`: Either `local_files`, `remote_url`, `private_source` or `font_source`.
* `source_url`: The URL of the font source, only if the source is marked as `public`.
* `font_name`: The name of the font being converted.
* `output_dir`: A true/false value on whether the user provided an output directory.

#### `SOURCE_LIST`
Called when the user initiates the `fonty source list` command.
* `source_count`: The number of source(s) listed.

#### `SOURCE_ADD`
Called when the user initiates the `fonty source add` command.
* `source_url`: The URL of the source, only if the font source is marked as `public`.

#### `SOURCE_REMOVE`
Called when the user initiates the `fonty source remove` command.
* `source_url`: The URL of the source, only if the font source is marked as `public`.

#### `SOURCE_UPDATE`
Called when the user initiates the `fonty source update` command.
* No additional data is collected.

#### `FONTY_SETUP`
Called when the initial setup script is ran.
* `font_count`: The total number of fonts installed in the user's system.
* `family_count`: The total number of font families installed in the user's system.

## How is the data processed?
All telemetry data is sent to a telemetry service, which is a simple Go API endpoint hosted in a Google Compute Engine instance. The Go API endpoint simply acts as a relay and immediately publishes the event data into Google PubSub.

A Google PubSub consumer then consumes the event data, discards any identifiable information such as IP addresses, then apply transformations to the data, before finally storing the transformed data into Google BigQuery for future processing and analytics.

## Open Source
In the spirit of open-source, the public is urged and welcome to not only review and contribute to fonty's source code, but also to its data collection policies. PRs and discussions are always welcomed!