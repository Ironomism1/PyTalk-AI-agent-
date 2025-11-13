from __future__ import annotations

import base64
import html
from typing import List

from markdown_it import MarkdownIt
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.util import ClassNotFound


def _highlight_code(code: str, lang: str | None) -> str:
    formatter = HtmlFormatter(style="monokai", nowrap=False)
    try:
        if lang:
            lexer = get_lexer_by_name(lang, stripall=True)
        else:
            lexer = guess_lexer(code)
        return highlight(code, lexer, formatter)
    except ClassNotFound:
        return f"<pre><code>{code}</code></pre>"


def render_markdown(md_text: str) -> str:
    md = MarkdownIt("commonmark", {"html": False, "linkify": True, "typographer": True})

    tokens = md.parse(md_text)
    html_parts: List[str] = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok.type == "fence" and tok.tag == "code":
            info = tok.info or ""
            code = tok.content
            lang = info.strip().split()[0] if info else None
            code_html = _highlight_code(code, lang)
            encoded = base64.b64encode(code.encode("utf-8")).decode("ascii")
            html_parts.append(f"""
            <div class="codeblock">
              <a class="copy-btn" href="copy:{encoded}">Copy</a>
              {code_html}
            </div>
            """)
        else:
            html_parts.append(tok.content if tok.type == "inline" else tok.markup or "")
        i += 1

    css = HtmlFormatter(style="monokai").get_style_defs('.highlight')
    base_css = f"""
    <style>
      body {{
        background-color: #0b1020;
        color: #d1d5db;
        font-family: 'Segoe UI', Roboto, Inter, sans-serif;
        margin: 0;
        padding: 0 8px;
      }}
      img {{
        max-width: 100%;
        border-radius: 8px;
      }}
      .codeblock {{
        position: relative;
        background: #1f2937;
        border-radius: 8px;
        padding-top: 28px;
        margin: 8px 0;
      }}
      .copy-btn {{
        position: absolute;
        right: 8px;
        top: 4px;
        background: rgba(34,197,94,0.1);
        color: #93c5fd;
        border: 1px solid rgba(56,189,248,0.25);
        padding: 2px 8px;
        border-radius: 6px;
        cursor: pointer;
        text-decoration: none;
      }}
      pre {{
        margin: 0;
        overflow-x: auto;
      }}
      {css}
    </style>
    """
    body = "".join(html_parts)
    return f"<!DOCTYPE html><html><head>{base_css}</head><body>{body}</body></html>"


