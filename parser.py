"""
Markdown to HTML parser with full syntax support.
"""

import re
import html
import uuid
import os

from .highlighter import highlight
from .theme import CSS_STYLES

# Get plugin directory for local mermaid.js
PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
MERMAID_JS_PATH = os.path.join(PLUGIN_DIR, 'mermaid.min.js')


def render_markdown(text: str) -> str:
    """Convert Markdown to HTML with syntax highlighting."""
    if not text or not text.strip():
        return text

    original = text
    has_mermaid = False

    try:
        # Step 1: Extract code blocks BEFORE any HTML processing
        code_blocks = {}

        def save_code_block(match):
            nonlocal has_mermaid
            lang = (match.group(1) or '').lower()
            code = match.group(2)

            # Clean up code block content
            code = re.sub(r'<[^>]+>', '\n', code)
            code = html.unescape(code)
            lines = [line for line in code.split('\n') if line.strip()]
            code = '\n'.join(lines)

            # Handle Mermaid diagrams
            if lang == 'mermaid':
                has_mermaid = True
                block_html = f'<div class="mermaid">{html.escape(code)}</div>'
            else:
                highlighted = highlight(code, lang)
                block_html = f'<pre><code>{highlighted}</code></pre>'

            # Use UUID as placeholder
            placeholder = f'CODEBLOCK{uuid.uuid4().hex}ENDBLOCK'
            code_blocks[placeholder] = block_html
            return placeholder

        text = re.sub(r'```(\w*)([\s\S]*?)```', save_code_block, text)

        # Step 1.5: Preserve existing <img> tags from Anki (pasted images)
        img_tags = {}
        def save_img_tag(match):
            placeholder = f'IMGTAG{uuid.uuid4().hex}ENDIMG'
            img_tags[placeholder] = match.group(0)
            return placeholder
        text = re.sub(r'<img[^>]+>', save_img_tag, text, flags=re.IGNORECASE)

        # Step 2: HTML normalization
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
        text = text.replace('&nbsp;', ' ')
        text = html.unescape(text)
        text = re.sub(r'</?div[^>]*>', '\n', text, flags=re.IGNORECASE)
        # Add newlines around <hr> tags so content after them is on its own line
        text = re.sub(r'(<hr[^>]*>)', r'\n\1\n', text, flags=re.IGNORECASE)
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = text.strip()

        # Step 3: Parse Markdown elements
        text = _parse_inline_code(text)
        text = _parse_images(text)
        text = _parse_links(text)
        text = _parse_formatting(text)
        text = _parse_headers(text)
        text = _parse_blockquotes(text)
        text = _parse_horizontal_rules(text)
        text = _parse_lists(text)
        text = _parse_tables(text)

        # Step 4: Convert newlines
        text = text.replace('\n', '<br>\n')
        block_tags = r'pre|ul|ol|li|h[1-6]|hr|blockquote|table|thead|tbody|tr|th|td|div'
        text = re.sub(rf'<br>\s*(</?(?:{block_tags}))', r'\1', text)
        text = re.sub(rf'(</(?:{block_tags})>|<hr[^>]*>)\s*<br>', r'\1', text)

        # Step 5: Restore code blocks
        for placeholder, block_html in code_blocks.items():
            text = text.replace(placeholder, block_html)

        # Step 5.5: Restore img tags
        for placeholder, img_html in img_tags.items():
            text = text.replace(placeholder, img_html)

        # Add mermaid script if needed
        mermaid_script = ''
        if has_mermaid:
            try:
                with open(MERMAID_JS_PATH, 'r', encoding='utf-8') as f:
                    mermaid_js_content = f.read()
                mermaid_script = f'''
<script>{mermaid_js_content}</script>
<script>
(function() {{
    mermaid.initialize({{
        startOnLoad: false,
        theme: 'dark',
        securityLevel: 'loose',
        logLevel: 'fatal'
    }});
    setTimeout(async function() {{
        var elements = document.querySelectorAll('.mermaid');
        for (var el of elements) {{
            var code = el.textContent.trim();
            var originalCode = code;
            try {{
                var result = await mermaid.render('mermaid-' + Math.random().toString(36).substr(2, 9), code);
                if (result && result.svg && result.svg.indexOf('<svg') !== -1) {{
                    el.innerHTML = result.svg;
                }} else {{
                    throw new Error('Invalid SVG');
                }}
            }} catch(e) {{
                el.innerHTML = '<pre style="background:#1e1e1e;color:#d4d4d4;padding:12px;border-radius:6px;text-align:left;white-space:pre;overflow-x:auto;"><code>' + originalCode.replace(/</g, '&lt;').replace(/>/g, '&gt;') + '</code></pre>';
            }}
        }}
    }}, 100);
}})();
</script>
'''
            except Exception as e:
                print(f"[AnkiMD] Failed to load mermaid.js: {e}")

        return CSS_STYLES + text.strip() + mermaid_script

    except Exception as e:
        print(f"[AnkiMD] Parse error: {e}")
        return original


def _parse_inline_code(text: str) -> str:
    """Parse inline code (`...`)."""
    def replace_inline(match):
        code = html.escape(match.group(1))
        return f'<code class="inline">{code}</code>'
    return re.sub(r'`([^`\n]+)`', replace_inline, text)


def _parse_images(text: str) -> str:
    """Parse images ![alt](url)."""
    return re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1">', text)


def _parse_links(text: str) -> str:
    """Parse links [text](url)."""
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)


def _parse_formatting(text: str) -> str:
    """Parse bold, italic, strikethrough."""
    # Strikethrough: ~~text~~
    text = re.sub(r'~~([^~]+)~~', r'<del>\1</del>', text)
    # Bold: **text** or __text__
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__([^_]+)__', r'<strong>\1</strong>', text)
    # Italic: *text* or _text_
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', text)
    text = re.sub(r'(?<!_)_([^_]+)_(?!_)', r'<em>\1</em>', text)
    return text


def _parse_headers(text: str) -> str:
    """Parse Markdown headers."""
    lines = text.split('\n')
    result = []

    for line in lines:
        matched = False
        # Strip any invisible/control characters from start of line
        clean_line = line.lstrip('\x00\x01\x02\x03\x04\x05\x06\x07\x08\x0b\x0c\x0e\x0f'
                                  '\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f'
                                  '\u200b\u200c\u200d\ufeff\u00a0')

        # Check for headers (h1-h6), starting from h6 to avoid partial matches
        for level in range(6, 0, -1):
            hashes = '#' * level
            # Match: optional whitespace, N hashes, not followed by #, whitespace, content
            pattern = rf'^[ \t]*{hashes}(?!#)\s+(.+)$'
            match = re.match(pattern, clean_line)
            if match:
                result.append(f'<h{level}>{match.group(1)}</h{level}>')
                matched = True
                break
        if not matched:
            result.append(line)

    return '\n'.join(result)


def _parse_blockquotes(text: str) -> str:
    """Parse blockquotes (> text)."""
    lines = text.split('\n')
    result = []
    in_quote = False
    quote_lines = []

    for line in lines:
        if line.startswith('>'):
            content = line[1:].strip()
            if line.startswith('> '):
                content = line[2:]
            quote_lines.append(content)
            in_quote = True
        else:
            if in_quote:
                result.append('<blockquote>' + '<br>'.join(quote_lines) + '</blockquote>')
                quote_lines = []
                in_quote = False
            result.append(line)

    if in_quote:
        result.append('<blockquote>' + '<br>'.join(quote_lines) + '</blockquote>')

    return '\n'.join(result)


def _parse_horizontal_rules(text: str) -> str:
    """Parse horizontal rules (---, ***, ___)."""
    text = re.sub(r'^-{3,}\s*$', '<hr>', text, flags=re.MULTILINE)
    text = re.sub(r'^\*{3,}\s*$', '<hr>', text, flags=re.MULTILINE)
    text = re.sub(r'^_{3,}\s*$', '<hr>', text, flags=re.MULTILINE)
    return text


def _parse_lists(text: str) -> str:
    """Parse ordered and unordered lists."""
    lines = text.split('\n')
    result = []
    in_ul = False
    in_ol = False

    for line in lines:
        # Unordered list item
        ul_match = re.match(r'^[-*+]\s+(.+)$', line)
        # Ordered list item
        ol_match = re.match(r'^(\d+)\.\s+(.+)$', line)

        if ul_match:
            if in_ol:
                result.append('</ol>')
                in_ol = False
            if not in_ul:
                result.append('<ul>')
                in_ul = True
            result.append(f'<li>{ul_match.group(1)}</li>')
        elif ol_match:
            if in_ul:
                result.append('</ul>')
                in_ul = False
            if not in_ol:
                result.append('<ol>')
                in_ol = True
            result.append(f'<li>{ol_match.group(2)}</li>')
        else:
            if in_ul:
                result.append('</ul>')
                in_ul = False
            if in_ol:
                result.append('</ol>')
                in_ol = False
            result.append(line)

    if in_ul:
        result.append('</ul>')
    if in_ol:
        result.append('</ol>')

    return '\n'.join(result)


def _parse_tables(text: str) -> str:
    """Parse Markdown tables."""
    lines = text.split('\n')
    result = []
    table_lines = []
    in_table = False

    for line in lines:
        # Check if line looks like a table row
        if '|' in line and line.strip().startswith('|'):
            table_lines.append(line)
            in_table = True
        else:
            if in_table and table_lines:
                result.append(_convert_table(table_lines))
                table_lines = []
                in_table = False
            result.append(line)

    if table_lines:
        result.append(_convert_table(table_lines))

    return '\n'.join(result)


def _convert_table(lines: list) -> str:
    """Convert table lines to HTML."""
    if len(lines) < 2:
        return '\n'.join(lines)

    html_parts = ['<table>']

    for i, line in enumerate(lines):
        # Skip separator line (|---|---|)
        if re.match(r'^\|[\s\-:|]+\|$', line.strip()):
            continue

        cells = [c.strip() for c in line.strip().strip('|').split('|')]

        if i == 0:
            # Header row
            html_parts.append('<thead><tr>')
            for cell in cells:
                html_parts.append(f'<th>{cell}</th>')
            html_parts.append('</tr></thead><tbody>')
        else:
            # Body row
            html_parts.append('<tr>')
            for cell in cells:
                html_parts.append(f'<td>{cell}</td>')
            html_parts.append('</tr>')

    html_parts.append('</tbody></table>')
    return ''.join(html_parts)
