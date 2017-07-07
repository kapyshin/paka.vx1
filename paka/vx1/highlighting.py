import io
import re

import lxml.html
from pygments import (
    lexers as _lexers, formatters as _formatters,
    highlight as _pygments_highlight)
from paka.cmark import lowlevel as _lowlevel


_OPTS = _lowlevel.OPT_DEFAULT | _lowlevel.OPT_NOBREAKS


def render_commonmark(text):
    """Render CommonMark as HTML.

    Highlights code in code blocks.

    """
    text_bytes = _lowlevel.text_to_c(text)
    root = _lowlevel.parse_document(text_bytes, len(text_bytes), _OPTS)
    try:
        _substitute_code_blocks(root, _highlight)
        result = _lowlevel.text_from_c(_lowlevel.render_html(root, _OPTS))
    finally:
        _lowlevel.node_free(root)
    return result


class _HtmlFormatter(_formatters.HtmlFormatter):
    """HTML formatter that just wraps with pre and code tags."""

    def wrap(self, source, outfile):
        yield (0, "<pre><code>")
        for tup in source:
            yield tup
        yield (0, "</code></pre>")


def _highlight(fence_info, contents):
    """Highlight contents according to fence info."""
    if not fence_info:  # lexer name is not specified
        return
    if fence_info == "pycon3":
        lexer = _lexers.get_lexer_by_name("pycon", python3=True)
    else:
        lexer = _lexers.get_lexer_by_name(fence_info)
    return _pygments_highlight(contents, lexer, _HtmlFormatter())


_match_highlighting_comment = re.compile(
    r"^vx1\.highlighting: (?P<fence_info>[a-zA-Z0-9]+)$").match


def _substitute_code_blocks(root, callback):
    """Walk tree, replace code blocks with HTML returned from callback.

    In HTML blocks, highlight code in <pre> that have comment
    <!-- vx1.highlighting: ... --> as first child.

    """
    def _invoke_code_block_callback(old_node):
        old_contents = _lowlevel.text_from_c(
            _lowlevel.node_get_literal(old_node))
        fence_info = _lowlevel.text_from_c(
            _lowlevel.node_get_fence_info(old_node))
        new_contents = callback(fence_info, old_contents)
        if new_contents is None:  # can't create new contents, skip
            return
        new_node = _lowlevel.node_new(_lowlevel.NODE_HTML_BLOCK)
        try:
            assert _lowlevel.node_set_literal(
                new_node, _lowlevel.text_to_c(new_contents)) == 1
            assert _lowlevel.node_replace(old_node, new_node) == 1
        except Exception:
            _lowlevel.node_free(new_node)
            raise
        _lowlevel.node_free(old_node)

    def _invoke_html_block_callback(node):
        """Take HTML block, highlight code (if possible), set new literal."""
        def _get_html(body):
            assert body.tag == "body"
            for old_el in body.iter("pre"):
                children = list(old_el)
                first_child = children[0]
                if not isinstance(first_child, lxml.html.HtmlComment):
                    continue
                first_child_match = _match_highlighting_comment(
                    first_child.text.strip())
                if not first_child_match:
                    continue
                fence_info = first_child_match.group("fence_info")
                code = children[1].text_content()
                highlighted = callback(fence_info, code)
                new_el = lxml.html.fragment_fromstring(highlighted)
                old_el.getparent().replace(old_el, new_el)
            for el in body:
                yield lxml.html.tostring(el, encoding="unicode")

        root = lxml.html.fragment_fromstring(
            _lowlevel.text_from_c(_lowlevel.node_get_literal(node)),
            create_parent="body")
        buf = io.StringIO()
        buf.writelines(_get_html(root))
        new_literal = _lowlevel.text_to_c(buf.getvalue())
        assert _lowlevel.node_set_literal(node, new_literal) == 1

    iter_ = _lowlevel.iter_new(root)
    try:
        while True:
            event_type = _lowlevel.iter_next(iter_)
            if event_type == _lowlevel.EVENT_DONE:
                break
            elif event_type == _lowlevel.EVENT_ENTER:
                node = _lowlevel.iter_get_node(iter_)
                node_type = _lowlevel.node_get_type(node)
                if node_type == _lowlevel.NODE_CODE_BLOCK:
                    _invoke_code_block_callback(node)
                elif node_type == _lowlevel.NODE_HTML_BLOCK:
                    _invoke_html_block_callback(node)
    finally:
        _lowlevel.iter_free(iter_)
