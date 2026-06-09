# 添加新的本地化

AVBPowerTool 使用类似 Android 的 XML 字符串资源。

## 资源文件结构

- 英文默认资源：`Resources/values/strings.xml`
- 其他语言资源：`Resources/values-<language>/strings.xml`

示例：

- `Resources/values-zh/strings.xml`
- `Resources/values-ja/strings.xml`
- `Resources/values-fr/strings.xml`

## 添加新语言

1. 创建新的资源目录：

```shell
Resources/values-<language>
```

2. 在该目录下创建 `strings.xml`。

3. 从英文默认资源复制条目：

```shell
Resources/values/strings.xml
```

4. 只翻译 XML 标签之间的文本。

不要修改 key：

```xml
<string name="cli.about.version">AVBPowerTool Version {version}</string>
```

`name` 的值必须保持不变，只翻译显示给用户的文本。

## 占位符

必须原样保留占位符：

```xml
{version}
{config}
{old}
{new}
{error}
{config_key}
```

示例：

```xml
<string name="settings.saved">Saved {config_key}: {old} -> {new}</string>
```

翻译后仍然必须包含 `{config_key}`、`{old}` 和 `{new}`。

## 启用语言

编辑 `GlobalConfig.cfg`：

```text
language="<language>"
```

示例：

```text
language="ja"
```

也可以在程序的 Settings 页面中修改语言。

## 检查缺失字符串

运行：

```shell
python main.py check_l10n
```

检查器会比较 `Resources/values/strings.xml` 和当前语言的 `strings.xml`，并把缺失条目输出为可直接复制的 XML 片段。

## 验证 XML

运行：

```shell
python -c "import xml.etree.ElementTree as ET; ET.parse('Resources/values/strings.xml'); ET.parse('Resources/values-<language>/strings.xml')"
```

如果命令没有报错，说明 XML 格式有效。

## 回退行为

如果当前语言缺少某个 key，AVBPowerTool 会自动回退到 `Resources/values/strings.xml` 中的英文文本。
