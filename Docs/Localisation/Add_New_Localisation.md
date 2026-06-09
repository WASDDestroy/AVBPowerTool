# Add New Localisation

AVBPowerTool uses Android-style XML string resources.

## Resource Layout

- English default: `Resources/values/strings.xml`
- Other languages: `Resources/values-<language>/strings.xml`

Examples:

- `Resources/values-zh/strings.xml`
- `Resources/values-ja/strings.xml`
- `Resources/values-fr/strings.xml`

## Add A New Language

1. Create a new folder:

```shell
Resources/values-<language>
```

2. Create `strings.xml` inside it.

3. Copy entries from:

```shell
Resources/values/strings.xml
```

4. Translate only the text between XML tags.

Do not change keys:

```xml
<string name="cli.about.version">AVBPowerTool Version {version}</string>
```

The `name` value must stay the same. Only translate the visible text.

## Placeholders

Keep placeholders unchanged:

```xml
{version}
{config}
{old}
{new}
{error}
{config_key}
```

Example:

```xml
<string name="settings.saved">Saved {config_key}: {old} -> {new}</string>
```

The translated string must still contain `{config_key}`, `{old}`, and `{new}`.

## Enable The Language

Edit `GlobalConfig.cfg`:

```text
language="<language>"
```

Example:

```text
language="ja"
```

You can also change this from the Settings page in the app.

## Check Missing Strings

Run:

```shell
python main.py check_l10n
```

The checker compares `Resources/values/strings.xml` with the selected language file and prints missing entries as XML snippets that can be copied into your language file.

## Validate XML

Run:

```shell
python -c "import xml.etree.ElementTree as ET; ET.parse('Resources/values/strings.xml'); ET.parse('Resources/values-<language>/strings.xml')"
```

If this command exits without error, the XML is valid.

## Fallback Behavior

If a key is missing in the selected language, AVBPowerTool falls back to English from `Resources/values/strings.xml`.
