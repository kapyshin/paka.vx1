<%namespace file="css_helpers.mako" import="size, mobile, vendored"/>

<%
    font_family = {"short": "serif", "long": 'Times, "Times New Roman", serif', "heading": "Georgia, serif"}
    font_size = "100%"
    line_height = "150%"
    text_color = "#000"
    solid_border = "solid 1px #ccc"
%>

<%include file="common.css.mako"/>

/* BASIC */
html {
    font-family: ${font_family["short"]};
}

body {
    color: ${text_color};
    background: #fff;
    font: ${font_size}/${line_height} ${font_family["long"]};
}

pre,
code,
kbd,
samp {
    font-family: monospace;
}

pre {
    display: block;
    overflow: auto;
    overflow-y: hidden;  /* fixes display issues in Chrome browsers */
    border-top: solid 1px #ccc;
    border-bottom: solid 1px #ccc;
}

@media print {
    pre {
        overflow: visible;
        white-space: pre-wrap;
        /*page-break-inside: avoid; -- not (yet?); this leaves huge blanks... */
    }
}

strong {
    font-weight: bolder;
}

em {
    font-style: italic;
}

p,
blockquote,
figure {
    margin: 0 0 ${size(3)};
}

blockquote {
    display: block;
    border-left: solid 2px #ccf;
    margin-left: ${size(3)};
    padding: 0 0 0 ${size(3)};
}

li,
dt {
    margin: ${size(4)} 0 0;
}

dt + dt {
    margin: 0;
}

ol li:first-child,
ul li:first-child,
dl dt:first-child {
    margin-top: 0;
}

ol,
ul,
dd {
    padding: 0 0 0 ${size(8)};
    margin: 0;
}

dl {
    margin: 0;
    padding: 0;
}

ol,
ul {
    list-style: circle outside;
}

ol + p,
ul + p,
dl + p {
    margin-top: ${size(4)};
}

figure {
    padding: 0;
    text-align: center;
}
figure img {
    width: 100%;
    height: auto;
    /*  of course this does not work...
    max-width: attr(width px);
    max-height: attr(height px);*/
    ${vendored("box-shadow: 0 0 1em #ccc", vendors=("webkit", "moz"))}
}
figcaption {
    text-align: center;
    font-size: 80%;
    font-style: italic;
}
/* END OF BASIC */


/* LINKS */
a:link {color: #05c;}
a:visited {color: #551a8b;}
a:hover {color: #c00;}
a:active {color: #f00;}
@media print {
    a {
        color: ${text_color} !important;
    }
}

a img {
    border: none;
}
/* END OF LINKS */


/* HEADER (h) */
.h {
    padding: ${size("fringe")} ${size("fringe")} 0
}
.h-bc {
    margin: 0;
    padding: 0;
    list-style: none;
}
.h-bc li:first-child {
    font-weight: bold;
}
.h-bc li {
    display: inline-block;
    list-style: none;
    margin: 0;
    padding: 0;
}
.h-bc li:before {
    content: "\a0\2192\a0";
}
.h-bc li:first-child:before {
    content: "";
}
.h-bc .last:after {
    content: "\a0\2193";
}

@media print {
    .h {
        display: none;
    }
}
/* END OF HEADER */


/* CONTENT (c) */
.c-p h1,
.c-p h2,
.c-p h3,
.c-p h4,
.c-p h5,
.c-p h6 {
    font-family: ${font_family["heading"]};
}
.c-p h1,
.c-p h2,
.c-p h3 {
    font-weight: normal;
    display: block;
    line-height: 140%;
}
.c-p h1 {
    margin: 0 0 ${size(2)};
    font-size: 170%;
}
.c-p h2 {
    margin: 0 0 ${size(1)};
    font-size: 140%;
}
.c-p h3 {
    margin: 0 0 ${size(1)};
    font-size: 120%;
}
.c-p h4,
.c-p h5,
.c-p h6 {
    display: inline;
    font-weight: bold;
    font-size: ${font_size};
    line-height: ${line_height};
}
/* secondary */
.c-s {}
.c-s-s {
    border-top: solid 1px #ccc;
    margin-top: ${size(4)};
    padding-top: ${size(4)};
}
.c-s-s:first-child {
    border-top: none;
    margin-top: 0;
    padding-top: 0;
}
.c-s-s h6 {
    font-size: 100%;
    font-family: ${font_family["heading"]};
    display: block;
    margin: 0;
    color: #333;
    font-weight: bolder;
}
.nm-l .t-l {
    padding-left: 0;
}

.c-s li,
.c-s dt {
    margin: ${size(1)} 0 0;
}

.c-s ol + p,
.c-s ul + p,
.c-s dl + p {
    margin-top: ${size(1)};
}

.c-s ol,
.c-s ul {
    list-style: none;
}
.c-s li:before {
    position: absolute;
    margin-left: -.8em;
    content: "\b7\a0";
}

@media ${mobile()} {
    .c-s {
        border-top: ${solid_border};
    }
}
/* END OF CONTENT */


/* FOOTER (f) */
.f {
    border-top: ${solid_border};
    font-size: 80%;
}

.f-nw {
    padding: 0;
    margin: 0;
    list-style: none;
}
.f-nw a,
.f-nw span {
    padding: ${size(1)} ${size(2)};
}
.f-nw li {
    display: inline-block;
    list-style: none;
    margin: 0;
    padding: 0;
}
.f-nw li:before {
    content: "\b7";
}
.f-nw li:first-child:before {
    content: "";
}
/* END OF FOOTER */
