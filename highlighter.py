"""
Syntax highlighter for code blocks.
Uses Pygments if available, falls back to simple highlighter.
"""

import html

# Try to use Pygments for professional syntax highlighting
try:
    from pygments import highlight as pygments_highlight
    from pygments.lexers import get_lexer_by_name, guess_lexer, TextLexer
    from pygments.formatters import HtmlFormatter
    from pygments.util import ClassNotFound
    HAS_PYGMENTS = True
except ImportError:
    HAS_PYGMENTS = False


def highlight(code: str, lang: str = '') -> str:
    """Apply syntax highlighting to code."""
    if not code:
        return code

    if HAS_PYGMENTS:
        return highlight_pygments(code, lang)
    else:
        return highlight_simple(code, lang)


def highlight_pygments(code: str, lang: str) -> str:
    """Highlight using Pygments library."""
    try:
        if lang:
            try:
                lexer = get_lexer_by_name(lang, stripall=True)
            except ClassNotFound:
                lexer = TextLexer()
        else:
            try:
                lexer = guess_lexer(code)
            except ClassNotFound:
                lexer = TextLexer()

        formatter = HtmlFormatter(nowrap=True, cssclass='highlight')
        return pygments_highlight(code, lexer, formatter)
    except Exception:
        return html.escape(code)


def highlight_simple(code: str, lang: str = '') -> str:
    """Simple fallback highlighter."""

    # Keywords for common languages
    KEYWORDS = {
        'abstract', 'async', 'await', 'boolean', 'break', 'byte', 'case',
        'catch', 'char', 'class', 'const', 'continue', 'debugger', 'default',
        'delete', 'do', 'double', 'else', 'enum', 'export', 'extends', 'false',
        'final', 'finally', 'float', 'for', 'from', 'func', 'function', 'goto',
        'if', 'implements', 'import', 'in', 'instanceof', 'int', 'interface',
        'let', 'long', 'native', 'new', 'nil', 'null', 'package', 'private',
        'protected', 'public', 'return', 'short', 'static', 'struct', 'super',
        'switch', 'synchronized', 'this', 'throw', 'throws', 'transient', 'true',
        'try', 'type', 'typeof', 'undefined', 'var', 'void', 'volatile', 'while',
        'with', 'yield', 'def', 'elif', 'except', 'lambda', 'pass', 'raise',
        'None', 'True', 'False', 'and', 'or', 'not', 'is', 'as', 'fn', 'mut',
        'impl', 'trait', 'pub', 'mod', 'use', 'crate', 'match', 'loop', 'move',
        'ref', 'self', 'Self', 'where', 'unsafe'
    }

    BUILTINS = {
        'String', 'Integer', 'Boolean', 'Double', 'Float', 'Long', 'Object',
        'Array', 'List', 'Map', 'Set', 'Math', 'Promise', 'Date', 'Error',
        'console', 'fmt', 'Vec', 'Option', 'Result', 'Box', 'int', 'str',
        'float', 'bool', 'dict', 'tuple', 'bytes', 'print', 'len', 'range',
        'System', 'Scanner', 'StringBuilder', 'ArrayList', 'HashMap'
    }

    result = []
    i = 0
    n = len(code)

    while i < n:
        char = code[i]

        # Strings
        if char in '"\'':
            end = _find_string_end(code, i, char, n)
            result.append(f'<span class="hl-s">{html.escape(code[i:end])}</span>')
            i = end
            continue

        # Comments
        if code[i:i+2] == '//':
            end = code.find('\n', i)
            end = n if end == -1 else end
            result.append(f'<span class="hl-c">{html.escape(code[i:end])}</span>')
            i = end
            continue

        if char == '#' and (i == 0 or code[i-1] in ' \n\t'):
            end = code.find('\n', i)
            end = n if end == -1 else end
            result.append(f'<span class="hl-c">{html.escape(code[i:end])}</span>')
            i = end
            continue

        if code[i:i+2] == '/*':
            end = code.find('*/', i + 2)
            end = n if end == -1 else end + 2
            result.append(f'<span class="hl-c">{html.escape(code[i:end])}</span>')
            i = end
            continue

        # Numbers
        if char.isdigit() or (char == '.' and i + 1 < n and code[i+1].isdigit()):
            end = i
            while end < n and (code[end].isdigit() or code[end] in '.xXabcdefABCDEFLlUu_'):
                end += 1
            result.append(f'<span class="hl-n">{html.escape(code[i:end])}</span>')
            i = end
            continue

        # Identifiers
        if char.isalpha() or char == '_':
            end = i
            while end < n and (code[end].isalnum() or code[end] == '_'):
                end += 1
            word = code[i:end]

            if word in KEYWORDS:
                result.append(f'<span class="hl-k">{word}</span>')
            elif word in BUILTINS:
                result.append(f'<span class="hl-t">{word}</span>')
            else:
                result.append(html.escape(word))

            i = end
            continue

        result.append(html.escape(char))
        i += 1

    return ''.join(result)


def _find_string_end(code: str, start: int, quote: str, length: int) -> int:
    """Find the end of a string literal."""
    i = start + 1
    while i < length:
        if code[i] == '\\' and i + 1 < length:
            i += 2
        elif code[i] == quote:
            return i + 1
        else:
            i += 1
    return length
