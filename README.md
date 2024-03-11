# Format pre-commit hook

A [pre-commit](https://pre-commit.com/) hook for custom formatting to remove trailing commas if the item can be collapsed onto one line.

## Using format

Add this to your `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/Core-Power-UK/format
  rev: v23.8.1
  hooks:
    - id: format
```
