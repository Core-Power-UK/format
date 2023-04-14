# Format pre-commit hook

A [pre-commit](https://pre-commit.com/) hook for custom formatting using [black](https://github.com/psf/black) and [add-trailing comma](https://github.com/asottile/add-trailing-comma). The custom formatting removes trailing commas if the item can be collased onto one line.

### Using format

Add this to your `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/Core-Power-UK/format
  rev: v1.0.2
  hooks:
    - id: format
```
