# mise SDK for Workshop

This SDK provides [mise](https://mise.jdx.dev/), a polyglot tool version manager,
for Workshop. Mise replaces per-language version managers like asdf, nvm, pyenv, and
rbenv with a single unified interface. Tool data is persisted on the host to speed up
installs across workshop updates.

---

## Reference workshop

A minimal workshop:

```yaml
# workshop.yaml
name: my-project
base: ubuntu@24.04
sdks:
  - name: mise
    channel: latest/stable

actions:
  setup: |
    mise install
```

This demonstrates a basic mise workflow with persistent tool data caching.

---

## Using the SDK

### Prerequisites, project layout

1. Add a `.mise.toml` or `.tool-versions` file to your project to declare which
   tool versions you need:

   ```toml
   # .mise.toml
   [tools]
   node = "22"
   python = "3.12"
   ```

2. On launch, the SDK installs the mise snap and configures `MISE_DATA_DIR` to
   point to a persistent host mount.

### Install and use tools

Once the workshop is ready:

```bash
workshop shell
mise install
node --version
python --version
```

Tool binaries managed by mise are available within the workshop shell.

---

## Plugs (resources this SDK consumes)

### `mise-data`

- Interface: `mount`
- Workshop target: `/home/workshop/.local/share/mise`
- Purpose: Persists downloaded tool data between workshop updates so that
  `mise install` does not re-download tools on each update.

---

## Documentation and guidance

- [mise official documentation](https://mise.jdx.dev/)
- [mise GitHub repository](https://github.com/jdx/mise)

---

## Community and support

- mise community: [https://github.com/jdx/mise/discussions](https://github.com/jdx/mise/discussions)
- Please review our [Code of Conduct](https://ubuntu.com/community/ethos/code-of-conduct)
  before participating.

---

## Contributions

All contributions, including code, documentation updates, and issue reports,
are welcome!

- Open issues or pull requests on the [official repository](https://github.com/raineszm/mise-sdk).

---

## License and copyright

Copyright 2026 Zachary Raines.

This project is licensed under the MIT License.
