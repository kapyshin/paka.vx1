<%def name="render_site_name(site)">${site.attrs["name"] | h,trim}</%def>
<%def name="render_site_language(site)">${site.attrs["language"] | h,trim}</%def>

<%def name="render_note_title(note)">${note.attrs["title"] | h,trim}</%def>
<%def name="render_tag_name(tag)">${tag.attrs["name"] | h,trim}</%def>

<%def name="render_chunk(name)">${context["chunks"][name]() | trim}</%def>
<%def name="render_translation(key, ctx)" filter="trim">
  <%
      from paka.vx1.translations import translate
  %>
  ${translate(key, context=ctx, site=site)}
</%def>

<%def name="render_secondary_about()" filter="trim">
  % if view_name != "about":
    <div class="c-s-s">
      <h6>${render_translation("secondary_section_about_heading", {})}</h6>
      <p>${render_translation("secondary_about", {"site": site})}</p>
    </div>
  % endif
</%def>
<%def name="render_secondary_recent_notes()" filter="trim">
  % if view_name not in {"home", "all_notes"}:
    <div class="c-s-s">
      <h6>${render_translation("secondary_section_recent_notes_heading", {})}</h6>
      ${render_recent_notes()}
    </div>
  % endif
</%def>
<%def name="render_secondary_popular_tags()" filter="trim">
  % if view_name in {"home", "all_notes"}:
    <div class="c-s-s">
      <h6>${render_translation("secondary_section_popular_tags_heading", {})}</h6>
      ${render_popular_tags()}
    </div>
  % endif
</%def>

<%def name="format_date(format_string, dt)">${format_string.format(dt)}</%def>

<%def name="link(target, item=False)">
  <% is_active = target == url_path %>
  % if item:
    <li${"" if not is_active else ' class="a-o"'}>
  % endif
  % if is_active:
    <span class="a">${caller.body()}</span>
  % else:
    <a href="${target | h,trim}">${caller.body()}</a>
  % endif
  % if item:
    </li>
  % endif
</%def>

<%def name="render_recent_notes()" filter="trim">
  <%
      from paka.vx1.consts import RECENT_NOTES_TEMPLATE_CONTEXT_KEY
  %>
  ${render_notes_list(context[RECENT_NOTES_TEMPLATE_CONTEXT_KEY])}
  <p><%self:link target="${routes_map.format_url_path('all_notes', context=None)}">${render_translation("recent_notes_all_link_text", {})}</%self:link></p>
</%def>
<%def name="render_popular_tags()" filter="trim">
  <%
      from paka.vx1.consts import POPULAR_TAGS_TEMPLATE_CONTEXT_KEY
  %>
  ${render_tags_list(context[POPULAR_TAGS_TEMPLATE_CONTEXT_KEY])}
  <p><%self:link target="${routes_map.format_url_path('all_tags', context=None)}">${render_translation("popular_tags_all_link_text", {})}</%self:link></p>
</%def>

<%def name="render_notes_list(notes)">
  <ol class="n-l">
    % for note in notes:
      <%
          note_url_path = routes_map.format_url_path('one_note', context={'note': note})
      %>
      <%self:link target="${note_url_path}" item="${True}">${render_note_title(note)}</%self:link>
    % endfor
  </ol>
</%def>
<%def name="render_tags_list(tags)">
  <ol class="t-l">
    % for tag in tags:
      <%
          tag_url_path = routes_map.format_url_path('one_tag', context={'tag': tag})
      %>
      <%self:link target="${tag_url_path}" item="${True}">${render_tag_name(tag)}</%self:link>
    % endfor
  </ol>
</%def>

<%def name="render_heading(breadcrumbs)">
  <% crumb = breadcrumbs[-1] %>
  <h1>${crumb["heading"]}</h1>
</%def>
<%def name="render_title(breadcrumbs, separator=u' ← ')" filter="trim">
  ${separator.join(crumb["text"] for crumb in reversed(breadcrumbs))}</%def>

<%def name="render_network_list(site, class_)">
  <ol class="${class_}">
    <% current_domain = site.attrs["domain"] %>
    % for connected_site in site.network.sites:
      <% conn_domain = connected_site.attrs["domain"] %>
      <% is_current = conn_domain == current_domain %>
      % if is_current:
        <li class="a-o">
          % if view_name == "home":
            <span class="a">${render_site_name(site)}</span>
          % else:
            <a href="/" rel="home" class="a">${render_site_name(site)}</a>
          % endif
        </li>
      % else:
        <li>
          <a href="//${connected_site.attrs['domain'] | h,trim}">${render_site_name(connected_site)}</a>
        </li>
      % endif
    % endfor
  </ol>
</%def>

<%def name="render_meta()" filter="trim">
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
</%def>
<%def name="render_feeds()" filter="trim">
  <%def name="render_feed(feed_url_path, feed_title)" filter="trim">
    <link rel="alternate" type="application/atom+xml" href="${feed_url_path | h,trim}" title="${feed_title}">
  </%def>
  % if view_name == "one_tag":
    <%
        tg = context["tag"]  # workaround (otherwise NameError)
    %>
    ${render_feed(routes_map.format_url_path('recent_tag_notes_feed', context={'tag': tg}), capture(render_translation, 'recent_tag_notes_feed_title', {'site': site, 'tag': tg}))}
  % endif
  ${render_feed(routes_map.format_url_path('recent_notes_feed', context={}), capture(render_translation, 'recent_notes_feed_title', {'site': site}))}
</%def>
<%def name="render_styles()" filter="trim">
  <link rel="stylesheet" href="/s/styles.css">
</%def>
<%def name="render_scripts()" filter="trim">
  <script src="/s/scripts.js" type="text/javascript"></script>
</%def>

<%def name="render_footer_years(site, separator)" filter="trim">
  <%
      import six
      str = six.text_type
      ey, cy = site.earliest_year, site.current_year
      years = str(cy) if cy == ey else separator.join((str(ey), str(cy)))
  %>
  ${years}
</%def>

<%def name="render_note_metadata(note, tags)">
  <dl class="nm-l">
    <dt>${render_translation("note_metadata_pubdate", {})}</dt>
    <dd>${format_date(site.attrs["date_format"], note.date) | h}</dd>
    <dt>${render_translation("note_metadata_tags", {})}</dt>
    <dd>${render_tags_list(tags)}</dd>
  </dl>
</%def>
