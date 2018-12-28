
- Official doc: https://www.odoo.com/documentation/8.0/setup/deploy.html#builtin-server

from your odoo config, if have use workers:

    openerp-server --workers=2 ...

and configure nginx:

    location /longpolling {
        proxy_pass http://127.0.0.1:8072;
    }
    location / {
        proxy_pass http://127.0.0.1:8069;
    }



Edit /etc/nginx/site-availables/defaut as attached file in same folder with this document.
Replace location with:

        location / {
            # First attempt to serve request as file, then
            # as directory, then fall back to displaying a 404.
            proxy_pass http://127.0.0.1:8069;
                    proxy_redirect off;
                    proxy_set_header Host $host;
                    proxy_set_header X-Real-IP $remote_addr;
                    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                    proxy_set_header X-Forwarded-Proto $scheme;
                    client_max_body_size 200M;
        }

        location /longpolling {
                    proxy_pass http://127.0.0.1:8072;
            }


Edit /etc/odoo/openerp-server.conf:

    xmlrpc_port = 8069
    xmlrpc_interface = 127.0.0.1
    xmlrpc = True
    workers = 6
    proxy_mode = 1
    longpolling_port = 8072
