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


def _substitute_code_blocks(root, callback):
    """Walk tree, replace code blocks with HTML returned from callback."""
    def _invoke_callback(old_node):
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
                    _invoke_callback(node)
    finally:
        _lowlevel.iter_free(iter_)
