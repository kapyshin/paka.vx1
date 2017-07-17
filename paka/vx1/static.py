import os

import paka.webstatic.pipeline as _pipeline


def _make_output(spec, filename):
    return _pipeline.Output(
        os.path.join(spec.static_build_dir, filename),
        makedirs=True)


def _make_input(spec, template_name):
    return _pipeline.InputItem(
        None, data=spec.site.renderer(template_name))


def _gen_css_pipeline(spec):
    yield from (
        _make_input(spec, "styles.css.mako"),
        _pipeline.CSSMin(),
        _make_output(spec, "styles.css"))


def _gen_js_pipeline(spec):
    yield from (
        _make_input(spec, "scripts.js.mako"),
        _pipeline.JSMin(),
        _make_output(spec, "scripts.js"))


def build_static(specs):
    for spec in specs:
        for func in (_gen_css_pipeline, _gen_js_pipeline):
            _pipeline.run(func(spec))
