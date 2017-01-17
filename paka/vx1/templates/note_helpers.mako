<%!
import markupsafe


def _mark_up_code(raw_code, tag_name):
    code = markupsafe.escape(raw_code.strip())
    beginning = '<pre><{tag_name}>'.format(tag_name=tag_name)
    ending = "</{}></pre>".format(tag_name)
    return "".join((beginning, code, ending))

%>
<%def name="code()">${_mark_up_code(capture(caller.body), tag_name="code")}</%def>
