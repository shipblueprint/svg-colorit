[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE) ![GitHub release](https://img.shields.io/github/v/release/shipblueprint/svg-colorit)

# SVG Colorit 🎨

A single Python script that batch-processes SVG files — replaces colors with a custom palette while preserving stroke/detail logic.

## Usage

1. Place `.svg` files in the **`Assets/`** folder.
2. Run the script:

```bash
python process_svgs.py
```

3. Processed SVGs are output to **`Output/`** with the same folder structure.

### Batch file

On Windows, double-click `process_svgs.bat` instead.

## Color Palette

| Token | Hex |
|-------|-----|
| Electric Coral (primary) | `#FF6B4A` |
| Sand Mist (fill) | `#EBE4D5` |
| Slate Echo (stroke) | `#7A7570` |

## How it works

- Orange-ish colors → replaced with **Electric Coral**
- Detail colors (high saturation) → filled with **Sand Mist**, stroked with **Slate Echo**
- Everything else → fill set to `none`, stroke set to **Slate Echo**

## License

MIT
