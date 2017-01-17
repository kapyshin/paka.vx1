<%def name="vendored(suffix, vendors=('webkit', 'moz', 'o', 'ms'), bare=True)">
  % for prefix in vendors:
    -${prefix}-${suffix};
  % endfor
  % if bare:
    ${suffix};
  % endif
</%def>

<%def name="box_sizing(value)">
  ${vendored("box-sizing: " + value, vendors=("webkit", "moz", "ms"), bare=True)}
</%def>

<%def name="size(idx)" filter="trim">
  <%
      sizes = {
          "fringe": "1%",
          1: ".2em",
          2: ".4em",
          3: ".8em",
          4: "1em",
          5: "1.2em",
          6: "1.4em",
          7: "1.8em",
          8: "2em",
          9: "2.2em",
          10: "2.4em",
          11: "2.8em",
          12: "4em",
      }
  %>
  ${sizes[idx]}
</%def>

<%def name="mobile()" filter="trim">handheld, (max-width: 500px)</%def>
