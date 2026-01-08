"""
AnkiMD - Markdown & Mermaid support for Anki
Cross-platform rendering using JavaScript (works on iOS/Android/Desktop).

Author: Lauren Wong
"""

from aqt import gui_hooks, mw

# Note type name
NOTE_TYPE_NAME = "AnkiMD"

# CSS styles embedded in template
CARD_CSS = """.card {
  font-family: "PingFang SC", "Microsoft YaHei", "Helvetica Neue", sans-serif;
  font-size: 16px;
  text-align: left;
  color: #d4d4d4;
  background-color: #1e1e1e;
  padding: 20px;
  line-height: 1.6;
  -webkit-text-size-adjust: 100%;
}

/* Code block */
pre {
  font-family: "SF Mono", "Menlo", "Monaco", "Consolas", monospace;
  font-size: 13px;
  line-height: 1.45;
  background-color: #2d2d2d;
  color: #d4d4d4;
  padding: 12px 16px;
  border-radius: 6px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  white-space: pre;
  margin: 12px 0;
}

pre code {
  font-family: inherit;
  font-size: inherit;
  background: none;
  padding: 0;
  color: inherit;
}

/* Inline code */
code.inline, p code, li code {
  font-family: "SF Mono", "Menlo", "Monaco", "Consolas", monospace;
  font-size: 0.9em;
  background-color: rgba(110, 118, 129, 0.4);
  color: #e06c75;
  padding: 2px 6px;
  border-radius: 4px;
}

/* Syntax highlighting */
.hl-k { color: #569cd6; }
.hl-t { color: #4ec9b0; }
.hl-s { color: #ce9178; }
.hl-n { color: #b5cea8; }
.hl-c { color: #6a9955; font-style: italic; }
.hl-f { color: #dcdcaa; }
.hl-v { color: #9cdcfe; }

/* Headers */
h1, h2, h3, h4, h5, h6 {
  color: #569cd6;
  margin: 16px 0 8px 0;
  font-weight: 600;
}

h1 { font-size: 1.8em; }
h2 { font-size: 1.5em; }
h3 { font-size: 1.3em; }
h4 { font-size: 1.1em; }
h5 { font-size: 1em; }
h6 { font-size: 0.9em; }

/* Blockquote */
blockquote {
  border-left: 4px solid #569cd6;
  margin: 12px 0;
  padding: 8px 16px;
  background-color: rgba(86, 156, 214, 0.1);
  color: #9cdcfe;
}

/* Table */
table {
  border-collapse: collapse;
  margin: 12px 0;
  width: 100%;
  display: block;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

th, td {
  border: 1px solid #444;
  padding: 8px 12px;
  text-align: left;
  white-space: nowrap;
}

th {
  background-color: #2d2d2d;
  font-weight: 600;
}

tr:nth-child(even) {
  background-color: rgba(255, 255, 255, 0.05);
}

/* Links */
a {
  color: #569cd6;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

/* Images */
img {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
}

/* Strikethrough */
del {
  color: #808080;
  text-decoration: line-through;
}

/* Horizontal rule */
hr {
  border: none;
  border-top: 1px solid #444;
  margin: 16px 0;
}

/* Lists */
ul, ol {
  margin: 8px 0;
  padding-left: 24px;
}

li {
  margin: 4px 0;
}

/* Mermaid diagrams */
.mermaid {
  background-color: #2d2d2d;
  padding: 16px;
  border-radius: 6px;
  margin: 12px 0;
  text-align: center;
}

.mermaid svg {
  max-width: 100%;
  height: auto;
}

/* Answer divider */
hr#answer {
  border: none;
  border-top: 2px solid #569cd6;
  margin: 20px 0;
}

/* Markdown container */
.markdown-content {
  text-align: left;
}

/* Front styling */
.front-side .markdown-content {
  font-size: 1.1em;
}
"""

# JavaScript Markdown parser - fully self-contained, no external dependencies
MARKDOWN_JS = """
<script>
(function() {
  // Simple Markdown parser for Anki
  function renderMarkdown(text) {
    if (!text || !text.trim()) return text;

    var codeBlocks = {};
    var blockIndex = 0;

    // Step 1: Extract and preserve code blocks
    text = text.replace(/```(\\w*)\\n?([\\s\\S]*?)```/g, function(match, lang, code) {
      var placeholder = '%%CODEBLOCK' + (blockIndex++) + '%%';
      lang = (lang || '').toLowerCase();

      // Clean up code
      code = code.replace(/<br\\s*\\/?>/gi, '\\n');
      code = code.replace(/&nbsp;/g, ' ');
      code = code.replace(/<[^>]+>/g, '');
      code = decodeHtml(code).trim();

      if (lang === 'mermaid') {
        codeBlocks[placeholder] = '<div class="mermaid">' + escapeHtml(code) + '</div>';
      } else {
        var highlighted = highlightCode(code, lang);
        codeBlocks[placeholder] = '<pre><code>' + highlighted + '</code></pre>';
      }
      return placeholder;
    });

    // Step 2: Preserve existing img tags
    var imgTags = {};
    var imgIndex = 0;
    text = text.replace(/<img[^>]+>/gi, function(match) {
      var placeholder = '%%IMG' + (imgIndex++) + '%%';
      imgTags[placeholder] = match;
      return placeholder;
    });

    // Step 3: HTML cleanup
    text = text.replace(/<br\\s*\\/?>/gi, '\\n');
    text = text.replace(/&nbsp;/g, ' ');
    text = text.replace(/<\\/?div[^>]*>/gi, '\\n');
    text = decodeHtml(text);
    text = text.replace(/\\n{3,}/g, '\\n\\n');

    // Step 4: Parse inline code (before other formatting)
    text = text.replace(/`([^`\\n]+)`/g, '<code class="inline">$1</code>');

    // Step 5: Parse block elements line by line
    var lines = text.split('\\n');
    var result = [];
    var inList = false;
    var listType = '';
    var inBlockquote = false;
    var blockquoteLines = [];
    var inTable = false;
    var tableLines = [];

    for (var i = 0; i < lines.length; i++) {
      var line = lines[i];
      var trimmed = line.trim();

      // Skip code block placeholders
      if (trimmed.match(/^%%CODEBLOCK\\d+%%$/)) {
        closeList();
        closeBlockquote();
        closeTable();
        result.push(trimmed);
        continue;
      }

      // Table detection
      if (trimmed.indexOf('|') !== -1 && trimmed.charAt(0) === '|') {
        closeList();
        closeBlockquote();
        if (!inTable) {
          inTable = true;
          tableLines = [];
        }
        tableLines.push(trimmed);
        continue;
      } else if (inTable) {
        closeTable();
      }

      // Blockquote
      if (trimmed.charAt(0) === '>') {
        closeList();
        closeTable();
        var content = trimmed.substring(1).trim();
        if (trimmed.substring(0, 2) === '> ') {
          content = trimmed.substring(2);
        }
        blockquoteLines.push(content);
        inBlockquote = true;
        continue;
      } else if (inBlockquote) {
        closeBlockquote();
      }

      // Headers
      var headerMatch = trimmed.match(/^(#{1,6})\\s+(.+)$/);
      if (headerMatch) {
        closeList();
        closeBlockquote();
        closeTable();
        var level = headerMatch[1].length;
        result.push('<h' + level + '>' + parseInline(headerMatch[2]) + '</h' + level + '>');
        continue;
      }

      // Horizontal rule
      if (trimmed.match(/^[-*_]{3,}$/)) {
        closeList();
        closeBlockquote();
        closeTable();
        result.push('<hr>');
        continue;
      }

      // Unordered list
      var ulMatch = trimmed.match(/^[-*+]\\s+(.+)$/);
      if (ulMatch) {
        closeBlockquote();
        closeTable();
        if (!inList || listType !== 'ul') {
          closeList();
          result.push('<ul>');
          inList = true;
          listType = 'ul';
        }
        result.push('<li>' + parseInline(ulMatch[1]) + '</li>');
        continue;
      }

      // Ordered list
      var olMatch = trimmed.match(/^(\\d+)\\.\\s+(.+)$/);
      if (olMatch) {
        closeBlockquote();
        closeTable();
        if (!inList || listType !== 'ol') {
          closeList();
          result.push('<ol>');
          inList = true;
          listType = 'ol';
        }
        result.push('<li>' + parseInline(olMatch[2]) + '</li>');
        continue;
      }

      // Regular line
      closeList();
      closeBlockquote();
      closeTable();

      if (trimmed) {
        result.push(parseInline(line));
      } else {
        result.push('');
      }
    }

    closeList();
    closeBlockquote();
    closeTable();

    function closeList() {
      if (inList) {
        result.push(listType === 'ul' ? '</ul>' : '</ol>');
        inList = false;
        listType = '';
      }
    }

    function closeBlockquote() {
      if (inBlockquote && blockquoteLines.length > 0) {
        result.push('<blockquote>' + blockquoteLines.map(parseInline).join('<br>') + '</blockquote>');
        blockquoteLines = [];
        inBlockquote = false;
      }
    }

    function closeTable() {
      if (inTable && tableLines.length > 0) {
        result.push(parseTable(tableLines));
        tableLines = [];
        inTable = false;
      }
    }

    // Join and convert remaining newlines to <br>
    text = result.join('\\n');
    text = text.replace(/\\n/g, '<br>\\n');

    // Clean up <br> around block elements
    text = text.replace(/<br>\\s*(<\\/?(?:pre|ul|ol|li|h[1-6]|hr|blockquote|table|thead|tbody|tr|th|td|div))/gi, '$1');
    text = text.replace(/(<\\/(?:pre|ul|ol|li|h[1-6]|blockquote|table|thead|tbody|tr|th|td|div)>|<hr>)\\s*<br>/gi, '$1');

    // Step 6: Restore code blocks
    for (var placeholder in codeBlocks) {
      text = text.replace(placeholder, codeBlocks[placeholder]);
    }

    // Step 7: Restore img tags
    for (var placeholder in imgTags) {
      text = text.replace(placeholder, imgTags[placeholder]);
    }

    return text;
  }

  // Parse inline elements (bold, italic, links, images, etc.)
  function parseInline(text) {
    // Images: ![alt](url)
    text = text.replace(/!\\[([^\\]]*)\\]\\(([^)]+)\\)/g, '<img src="$2" alt="$1">');

    // Links: [text](url)
    text = text.replace(/\\[([^\\]]+)\\]\\(([^)]+)\\)/g, '<a href="$2">$1</a>');

    // Bold: **text** or __text__
    text = text.replace(/\\*\\*([^*]+)\\*\\*/g, '<strong>$1</strong>');
    text = text.replace(/__([^_]+)__/g, '<strong>$1</strong>');

    // Strikethrough: ~~text~~
    text = text.replace(/~~([^~]+)~~/g, '<del>$1</del>');

    // Italic: *text* or _text_ (without lookbehind for compatibility)
    text = text.replace(/([^*])\\*([^*]+)\\*/g, '$1<em>$2</em>');
    text = text.replace(/^\\*([^*]+)\\*/g, '<em>$1</em>');
    text = text.replace(/([^_])_([^_]+)_/g, '$1<em>$2</em>');
    text = text.replace(/^_([^_]+)_/g, '<em>$1</em>');

    return text;
  }

  // Parse table
  function parseTable(lines) {
    if (lines.length < 2) return lines.join('<br>');

    var html = '<table>';
    var isHeader = true;

    for (var i = 0; i < lines.length; i++) {
      var line = lines[i].trim();

      // Skip separator line
      if (line.match(/^\\|[\\s\\-:|]+\\|$/)) {
        isHeader = false;
        continue;
      }

      var cells = line.replace(/^\\|/, '').replace(/\\|$/, '').split('|');

      if (isHeader) {
        html += '<thead><tr>';
        for (var j = 0; j < cells.length; j++) {
          html += '<th>' + parseInline(cells[j].trim()) + '</th>';
        }
        html += '</tr></thead><tbody>';
        isHeader = false;
      } else {
        html += '<tr>';
        for (var j = 0; j < cells.length; j++) {
          html += '<td>' + parseInline(cells[j].trim()) + '</td>';
        }
        html += '</tr>';
      }
    }

    html += '</tbody></table>';
    return html;
  }

  // Simple syntax highlighting
  function highlightCode(code, lang) {
    if (!lang) return escapeHtml(code);

    var keywords = {
      'python': ['def', 'class', 'import', 'from', 'return', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'finally', 'with', 'as', 'lambda', 'yield', 'raise', 'pass', 'break', 'continue', 'and', 'or', 'not', 'in', 'is', 'None', 'True', 'False', 'async', 'await', 'self'],
      'javascript': ['function', 'const', 'let', 'var', 'return', 'if', 'else', 'for', 'while', 'class', 'extends', 'import', 'export', 'default', 'new', 'this', 'try', 'catch', 'finally', 'throw', 'async', 'await', 'typeof', 'instanceof', 'null', 'undefined', 'true', 'false', 'of', 'in'],
      'java': ['public', 'private', 'protected', 'class', 'interface', 'extends', 'implements', 'return', 'if', 'else', 'for', 'while', 'try', 'catch', 'finally', 'throw', 'new', 'this', 'super', 'static', 'final', 'void', 'int', 'boolean', 'String', 'null', 'true', 'false', 'import', 'package'],
      'c': ['int', 'char', 'float', 'double', 'void', 'return', 'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'break', 'continue', 'struct', 'typedef', 'enum', 'const', 'static', 'extern', 'sizeof', 'NULL', 'include', 'define'],
      'cpp': ['int', 'char', 'float', 'double', 'void', 'return', 'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'break', 'continue', 'class', 'struct', 'public', 'private', 'protected', 'virtual', 'override', 'const', 'static', 'new', 'delete', 'nullptr', 'true', 'false', 'namespace', 'using', 'template', 'typename', 'include'],
      'go': ['func', 'package', 'import', 'return', 'if', 'else', 'for', 'range', 'switch', 'case', 'default', 'break', 'continue', 'type', 'struct', 'interface', 'map', 'chan', 'go', 'defer', 'select', 'var', 'const', 'nil', 'true', 'false', 'make', 'new', 'len', 'cap', 'append'],
      'rust': ['fn', 'let', 'mut', 'const', 'if', 'else', 'for', 'while', 'loop', 'match', 'return', 'struct', 'enum', 'impl', 'trait', 'pub', 'use', 'mod', 'self', 'super', 'where', 'async', 'await', 'move', 'Some', 'None', 'Ok', 'Err', 'true', 'false'],
      'sql': ['SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER', 'TABLE', 'INDEX', 'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER', 'ON', 'AND', 'OR', 'NOT', 'NULL', 'IN', 'LIKE', 'ORDER', 'BY', 'GROUP', 'HAVING', 'LIMIT', 'OFFSET', 'AS', 'DISTINCT', 'COUNT', 'SUM', 'AVG', 'MAX', 'MIN'],
      'typescript': ['function', 'const', 'let', 'var', 'return', 'if', 'else', 'for', 'while', 'class', 'extends', 'implements', 'import', 'export', 'default', 'new', 'this', 'try', 'catch', 'finally', 'throw', 'async', 'await', 'typeof', 'instanceof', 'null', 'undefined', 'true', 'false', 'interface', 'type', 'enum', 'namespace', 'module', 'declare', 'readonly', 'private', 'public', 'protected', 'static', 'abstract']
    };

    // Normalize language name
    var langMap = {'js': 'javascript', 'ts': 'typescript', 'py': 'python'};
    lang = langMap[lang] || lang;

    var escaped = escapeHtml(code);
    var langKeywords = keywords[lang] || [];

    // Highlight strings (double and single quotes)
    escaped = escaped.replace(/(&quot;[^&]*&quot;|&#x27;[^&]*&#x27;|"[^"]*"|'[^']*')/g, '<span class="hl-s">$1</span>');

    // Highlight comments (// and #)
    escaped = escaped.replace(/(\\/{2}.*|#.*)/g, '<span class="hl-c">$1</span>');

    // Highlight numbers
    escaped = escaped.replace(/\\b(\\d+\\.?\\d*)\\b/g, '<span class="hl-n">$1</span>');

    // Highlight keywords
    if (langKeywords.length > 0) {
      var keywordPattern = new RegExp('\\\\b(' + langKeywords.join('|') + ')\\\\b', 'g');
      escaped = escaped.replace(keywordPattern, '<span class="hl-k">$1</span>');
    }

    return escaped;
  }

  function escapeHtml(text) {
    var map = {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#x27;'};
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
  }

  function decodeHtml(text) {
    var map = {'&amp;': '&', '&lt;': '<', '&gt;': '>', '&quot;': '"', '&#x27;': "'", '&nbsp;': ' '};
    return text.replace(/&amp;|&lt;|&gt;|&quot;|&#x27;|&nbsp;/g, function(m) { return map[m]; });
  }

  // Initialize when DOM is ready
  function init() {
    var containers = document.querySelectorAll('.markdown-content');
    for (var i = 0; i < containers.length; i++) {
      var container = containers[i];
      if (container.getAttribute('data-rendered')) continue;

      var originalText = container.innerHTML;
      container.innerHTML = renderMarkdown(originalText);
      container.setAttribute('data-rendered', 'true');
    }

    // Initialize Mermaid if present
    initMermaid();
  }

  // Mermaid: display as formatted code block (CDN not supported in Anki WebView)
  function initMermaid() {
    var mermaidElements = document.querySelectorAll('.mermaid');
    for (var i = 0; i < mermaidElements.length; i++) {
      var el = mermaidElements[i];
      var code = el.textContent.trim();
      if (!code) continue;
      // Display mermaid source as code block with label
      el.innerHTML = '<div style="text-align:left;font-size:11px;color:#6a9955;margin-bottom:4px;">mermaid</div><pre style="margin:0;"><code>' + escapeHtml(code) + '</code></pre>';
    }
  }

  // Run on load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    setTimeout(init, 10);
  }
})();
</script>
"""


def create_note_type() -> None:
    """Create the AnkiMD note type if it doesn't exist."""
    if not mw or not mw.col:
        return

    # Check if note type already exists
    existing = mw.col.models.by_name(NOTE_TYPE_NAME)
    if existing:
        # Update existing note type with new template
        _update_note_type(existing)
        return

    # Create new note type
    model = mw.col.models.new(NOTE_TYPE_NAME)

    # Add fields
    front_field = mw.col.models.new_field("Front")
    back_field = mw.col.models.new_field("Back")
    mw.col.models.add_field(model, front_field)
    mw.col.models.add_field(model, back_field)

    # Add template with JavaScript rendering
    template = mw.col.models.new_template("Card 1")
    template["qfmt"] = """<div class="front-side">
<div class="markdown-content">{{Front}}</div>
</div>
""" + MARKDOWN_JS

    template["afmt"] = """<div class="front-side">
<div class="markdown-content">{{Front}}</div>
</div>
<hr id="answer">
<div class="back-side">
<div class="markdown-content">{{Back}}</div>
</div>
""" + MARKDOWN_JS

    mw.col.models.add_template(model, template)

    # Set CSS
    model["css"] = CARD_CSS

    # Add to collection
    mw.col.models.add(model)
    print(f"[AnkiMD] Created note type '{NOTE_TYPE_NAME}'")


def _update_note_type(model: dict) -> None:
    """Update existing note type with new templates."""
    if not mw or not mw.col:
        return

    updated = False

    # Check if template needs updating
    if model.get("tmpls"):
        template = model["tmpls"][0]

        new_qfmt = """<div class="front-side">
<div class="markdown-content">{{Front}}</div>
</div>
""" + MARKDOWN_JS

        new_afmt = """<div class="front-side">
<div class="markdown-content">{{Front}}</div>
</div>
<hr id="answer">
<div class="back-side">
<div class="markdown-content">{{Back}}</div>
</div>
""" + MARKDOWN_JS

        if template.get("qfmt") != new_qfmt or template.get("afmt") != new_afmt:
            template["qfmt"] = new_qfmt
            template["afmt"] = new_afmt
            updated = True

    # Update CSS if needed
    if model.get("css") != CARD_CSS:
        model["css"] = CARD_CSS
        updated = True

    if updated:
        mw.col.models.save(model)
        print(f"[AnkiMD] Updated note type '{NOTE_TYPE_NAME}'")


def on_profile_loaded() -> None:
    """Called when profile is loaded - create note type if needed."""
    create_note_type()


# Register hooks
gui_hooks.profile_did_open.append(on_profile_loaded)

print("[AnkiMD] Plugin loaded (JS rendering mode)")
