import os


CODES = {400, 403, 404, 413, 500}


def make_view_name(code):
    return "error_page_{}".format(code)


def make_url_path(code):
    return "/e/{}/".format(code)
