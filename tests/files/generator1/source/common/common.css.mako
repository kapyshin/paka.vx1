<%namespace file="css_helpers.mako" import="vendored, box_sizing, size, mobile"/>

@charset "utf-8";


/* BASIC */
html {
    ${vendored("text-size-adjust: 100%", vendors=("webkit", "ms"))}
}

body {
    margin: 0;
    padding: 0;
}
/* END OF BASIC */


/* LINKS */
.nou {
    text-decoration: none !important;
}

a,
.nou .u {
    cursor: pointer;
    text-decoration: underline;
}

a:hover,
a:active {
    outline: 0;
}

a:focus {
    outline: thin dotted #333;
    outline: 5px auto -webkit-focus-ring-color;
    outline-offset: -2px;
}

@media print {
    a {
        text-decoration: none;
    }
    a::after {
        content: "\a0(" attr(href) ")";
    }
}
/* END OF LINKS */


/* ACTIVE */
.a {
    background: #ecf0ff;
    color: #000;
}
/* END OF ACTIVE */


/* CONTENT (c) */
.c {
    display: table;
    table-layout: fixed;
    border-collapse: collapse;
    width: 100%;
    margin: ${size(4)} 0;
}
.c-i {
    display: table-row;
}
.c-p,
.c-s {
    display: table-cell;
    ${box_sizing("border-box")}
    vertical-align: top;
}
.c-p {
    width: 70%;
    padding-left: ${size("fringe")};
}
.c-s {
    width: 30%;
    padding-left: 3%;
    padding-right: ${size("fringe")};
}

@media print, ${mobile()} {
    .c,
    .c-i,
    .c-p {
        display: block;
        width: 100%;
    }
}
@media ${mobile()} {
    .c-s {
        display: block;
        width: 100%;
        margin-top: ${size(4)};
        padding-top: ${size(4)};
    }
}
@media print {
    .c-s {
        display: none;
    }
}
/* END OF CONTENT */


/* FOOTER (f) */
.f {
    display: table;
    table-layout: fixed;
    border-collapse: collapse;
    width: 100%;
}
.f-i {
    display: table-row;
}
.f-a,
.f-s {
    display: table-cell;
    ${box_sizing("border-box")}
    vertical-align: top;
    width: 50%;
    padding: ${size(4)} ${size("fringe")} ${size(12)};
}
.f-s {
    text-align: right;
}

@media ${mobile()} {
    .f,
    .f-i,
    .f-a,
    .f-s {
        display: block;
        text-align: left;
    }
    .f-a,
    .f-s {
        width: 100%;
    }
    .f-a {
        padding-bottom: 0;
    }
    .f-s {
        padding-top: 0;
    }
}
@media print {
    .f {
        display: none;
    }
}
/* END OF FOOTER */


/* ERROR PAGE (oh-no) */
.oh-no {
    margin: 4%;
}
.oh-no h1 {
    font-weight: normal;
    margin-bottom: .4em;
}
/* END OF ERROR PAGE */
