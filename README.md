# Format pre-commit hook

A [pre-commit](https://pre-commit.com/) hook for custom formatting to remove trailing commas if the item can be collapsed onto one line.

## Using format

Add this to your `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/Core-Power-UK/format
  rev: v24.06.1
  hooks:
    - id: ruff
      args: [--fix]
      additional_dependencies:
        - ruff==0.4.10
    - id: format
      additional_dependencies:
        - ruff==0.4.10
```
