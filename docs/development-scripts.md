![Find By Color Logo](https://findbycolor-github.s3.amazonaws.com/logo.png "Find By Color Logo Logo")

**[↤ Developer Overview](../README.md)**

Development Scripts
===

### CLI Flags:

Default values come from constants defined in `./src/config.py` but can be overwritten with CLI flags.

| flag          | alias | default           | description                               |
|---------------|-------|-------------------|-------------------------------------------|
| `--limit`     | `-l`  | `COLOR_LIMIT`     | Limit of Extracted Colors [1-12]          |
| `--max-size`  | `-m`  | `MAX_IMAGE_SIZE`  | Max Image Size before Resize [512-1024]   |
| `--tolerance` | `-t`  | `COLOR_TOLERANCE` | Threshold to Group Related Colors [0-100] |
| `--clean`     |       |                   | Clean Output Folder                       |
| `--debug`     |       |                   | Print Output to Terminal                  |
| `--images`    |       |                   | Generate Images                           |
| `--json`      |       |                   | Generate JSON Data                        |
| `--trace`     |       |                   | Trace Memory Allocations                  |
