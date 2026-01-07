"""
CSS theme and scripts for Markdown rendering.
"""

CSS_STYLES = """
<style>
/* Code block */
pre {
  font-family: "SF Mono", "Menlo", "Monaco", "Consolas", monospace;
  font-size: 13px;
  line-height: 1.45;
  background-color: #1e1e1e;
  color: #d4d4d4;
  padding: 12px 16px;
  border-radius: 6px;
  overflow-x: auto;
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
code.inline {
  font-family: "SF Mono", "Menlo", "Monaco", "Consolas", monospace;
  font-size: 0.9em;
  background-color: rgba(110, 118, 129, 0.4);
  color: #e06c75;
  padding: 2px 6px;
  border-radius: 4px;
}

/* Syntax highlighting - VSCode Dark+ (simple highlighter) */
.hl-k { color: #569cd6; }
.hl-t { color: #4ec9b0; }
.hl-s { color: #ce9178; }
.hl-n { color: #b5cea8; }
.hl-c { color: #6a9955; font-style: italic; }

/* Syntax highlighting - VSCode Dark+ (Pygments) */
.highlight .k, .highlight .kd, .highlight .kn, .highlight .kp, .highlight .kr, .highlight .kc { color: #569cd6; }
.highlight .kt { color: #4ec9b0; }
.highlight .nc, .highlight .nn, .highlight .ne { color: #4ec9b0; }
.highlight .nf, .highlight .nb, .highlight .nd { color: #dcdcaa; }
.highlight .s, .highlight .s1, .highlight .s2, .highlight .sb, .highlight .sc, .highlight .sd, .highlight .se, .highlight .sh, .highlight .si, .highlight .sx, .highlight .sr, .highlight .ss { color: #ce9178; }
.highlight .m, .highlight .mi, .highlight .mf, .highlight .mh, .highlight .mo, .highlight .il { color: #b5cea8; }
.highlight .c, .highlight .c1, .highlight .cm, .highlight .cp, .highlight .cs { color: #6a9955; font-style: italic; }
.highlight .o, .highlight .p { color: #d4d4d4; }
.highlight .na, .highlight .nv, .highlight .vc, .highlight .vg, .highlight .vi { color: #9cdcfe; }
.highlight .ow { color: #c586c0; }

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
}

th, td {
  border: 1px solid #444;
  padding: 8px 12px;
  text-align: left;
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
  background-color: #1e1e1e;
  padding: 16px;
  border-radius: 6px;
  margin: 12px 0;
  text-align: center;
}

.mermaid img {
  max-width: 100%;
  height: auto;
}

/* Front field styling */
.front {
  font-size: 1.4em;
  font-weight: 600;
  color: #569cd6;
}
</style>
"""
