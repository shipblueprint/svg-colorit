import re, os, glob

ELECTRIC_CORAL = "#FF6B4A"
SAND_MIST = "#EBE4D5"
SLATE_ECHO = "#7A7570"

def is_orange(hex_code):
    hex_code = hex_code.lstrip("#")
    if len(hex_code) == 3:
        hex_code = "".join([c*2 for c in hex_code])
    if len(hex_code) != 6:
        return False
    try:
        r, g, b = int(hex_code[0:2], 16), int(hex_code[2:4], 16), int(hex_code[4:6], 16)
        return r > 160 and g > 60 and b < 140
    except ValueError:
        return False

def is_detail_color(hex_code):
    hex_code = hex_code.lstrip("#")
    if len(hex_code) == 3:
        hex_code = "".join([c*2 for c in hex_code])
    if len(hex_code) != 6:
        return False
    try:
        r, g, b = int(hex_code[0:2], 16), int(hex_code[2:4], 16), int(hex_code[4:6], 16)
        return max(r, g, b) - min(r, g, b) > 30
    except ValueError:
        return False

def process_svg(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    def css_replacer(match):
        full_block = match.group(0)
        style_content = re.search(r"<style[^>]*>(.*?)</style>", full_block, flags=re.DOTALL)
        if not style_content:
            return full_block
        css_inner = style_content.group(1)
        style_tag_open = full_block[:full_block.find(">")+1]
        style_tag_close = "</style>"

        def rule_replacer(rule_match):
            selector = rule_match.group(1).strip()
            props = rule_match.group(2)
            hexes = re.findall(r"#[0-9a-fA-F]{3,6}", props)
            has_orange = any(is_orange(h) for h in hexes)
            stroke_props = "stroke-width: 2.5px; stroke-linecap: round; stroke-linejoin: round;"
            if has_orange:
                new_props = f"fill: {ELECTRIC_CORAL}; stroke: {ELECTRIC_CORAL}; {stroke_props}"
            else:
                fill_match = re.search(r"fill\s*:\s*(#[0-9a-fA-F]{3,6})", props)
                if fill_match and is_detail_color(fill_match.group(1)):
                    new_props = f"fill: {SAND_MIST}; stroke: {SLATE_ECHO}; {stroke_props}"
                else:
                    new_props = f"fill: none; stroke: {SLATE_ECHO}; {stroke_props}"
            return f"{selector} {{{new_props}}}"

        new_css = re.sub(r"([^{}]+?)\s*\{([^}]*)\}", rule_replacer, css_inner, flags=re.DOTALL)
        return f"{style_tag_open}\n{new_css}\n{style_tag_close}"

    content = re.sub(r"<style[^>]*>.*?</style>", css_replacer, content, flags=re.DOTALL)

    def tag_replacer(match):
        tag = match.group(0)
        if tag.startswith("<svg") or tag.startswith("</"):
            return tag
        has_class = "class=" in tag
        has_direct_colors = re.search(r"(fill|stroke|stop-color)\s*=\s*\"", tag, re.I)
        if has_class and not has_direct_colors:
            return tag
        hexes = re.findall(r"#[0-9a-fA-F]{3,6}", tag)
        has_orange = any(is_orange(h) for h in hexes)
        if has_orange:
            for h in set(hexes):
                tag = tag.replace(h, ELECTRIC_CORAL)
            if "fill=" in tag:
                tag = re.sub(r"fill=\"[^\"]*\"", f"fill=\"{ELECTRIC_CORAL}\"", tag)
            if "stroke=" in tag:
                tag = re.sub(r"stroke=\"[^\"]*\"", f"stroke=\"{ELECTRIC_CORAL}\"", tag)
            if "stop-color=" in tag:
                tag = re.sub(r"stop-color=\"[^\"]*\"", f"stop-color=\"{ELECTRIC_CORAL}\"", tag)
        elif hexes:
            orig_fill_match = re.search(r"fill\s*=\s*\"(#[0-9a-fA-F]{3,6})\"", tag)
            orig_fill_val = orig_fill_match.group(1) if orig_fill_match else "none"
            for h in set(hexes):
                tag = tag.replace(h, SLATE_ECHO)
            if "fill=" in tag:
                if orig_fill_val != "none" and is_detail_color(orig_fill_val):
                    tag = re.sub(r"fill=\"[^\"]*\"", f"fill=\"{SAND_MIST}\"", tag)
                else:
                    tag = re.sub(r"fill=\"[^\"]*\"", "fill=\"none\"", tag)
            if "stroke=" in tag:
                tag = re.sub(r"stroke=\"[^\"]*\"", f"stroke=\"{SLATE_ECHO}\"", tag)
            if "stop-color=" in tag:
                tag = re.sub(r"stop-color=\"[^\"]*\"", f"stop-color=\"{SLATE_ECHO}\"", tag)
        return tag

    content = re.sub(r"<[^>]+>", tag_replacer, content)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Processed: {os.path.basename(input_path)}")

script_dir = os.path.dirname(os.path.abspath(__file__))
input_root = os.path.join(script_dir, "Assets")
output_root = os.path.join(script_dir, "Output")

count = 0
for dirpath, dirnames, filenames in os.walk(input_root):
    rel_path = os.path.relpath(dirpath, input_root)
    if rel_path == ".":
        out_dir = output_root
    else:
        out_dir = os.path.join(output_root, rel_path)
    svgs = [f for f in filenames if f.lower().endswith(".svg")]
    if not svgs:
        continue
    os.makedirs(out_dir, exist_ok=True)
    for svg in svgs:
        in_file = os.path.join(dirpath, svg)
        out_file = os.path.join(out_dir, svg)
        process_svg(in_file, out_file)
        count += 1

print(f"Done — processed {count} SVG(s).")
