Firefox requires intermediate SSL certificates while some other browsers don’t.
I use nginx, and all companies I work with use it too. Its
[documentation](http://nginx.org/en/docs/http/ngx_http_ssl_module.html#ssl_certificate)
states:

> If intermediate certificates should be specified in addition to a primary
> certificate, they should be specified in the same file in the following
> order: the primary certificate comes first, then the intermediate certificates.

This means that your certificate should look like this:

```
-----BEGIN CERTIFICATE-----
your certificate
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
intermediate certificate
-----END CERTIFICATE-----
```
