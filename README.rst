.. image:: https://travis-ci.org/datakortet/dkbuild-apacheconf.svg?branch=master
    :target: https://travis-ci.org/datakortet/dkbuild-apacheconf

.. image:: https://codecov.io/gh/datakortet/dkbuild-apacheconf/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/datakortet/dkbuild-apacheconf

.. image:: https://codecov.io/gh/datakortet/dkbuild-apacheconf/branch/master/graphs/sunburst.svg
   :target: https://codecov.io/gh/datakortet/dkbuild-apacheconf

dkbuild-apacheconf - build apache.conf from site.ini and server.ini
===================================================================

NOTE / WARNING
--------------
This code is currently more proof-of-concept than reliable too.. you have been warned.

The generated file relies on a definition of ``SRV`` (which requires an Apache that supports ``mod_define``):: 

    Define SRV  /srv

The generated file is currently hardcoded to our setup in several ways
and you'll almost certainly want to edit it by hand after generating
it.

Alternatively you can modify the ``apache.conf.jinja`` template to
suit your needs. If you think your changes are of general interest
we're very happy to receive PRs.

Please report any bugs on github: https://github.com/datakortet/dkbuild-apacheconf/issues/new

Known issues:

 - we expect to be on a Ubuntu installation of Apache
 - sites are expected to be at ``${SRV}/www/<sitename>``
 - Django static and media folders are expected to be linked to
   ``${SRV}/www/<sitename>/static`` (and similarly for media).
 - Certain static files are expected to be under
   ``${SRV}/www/docroot``:
   
   - favicon.ico
   - robots.txt
   - cookies.html  (cookie policy)
   - privacy-policy.html 
   

Installation
------------

I'm using the ``virtualenv-win`` package to create the virtualenv
here, you can of course do it any way you want::

    c:\srv> mkvirtualenv apb
    New python executable in c:\srv\venv\apb\Scripts\python.exe
    Installing setuptools, pip, wheel...
    done.
    
    (apb) c:\srv> cdvirtualenv
    (apb) c:\srv\venv\apb> git clone https://github.com/datakortet/dkbuild-apacheconf.git
    Cloning into 'dkbuild-apacheconf'...
    ...    
    (apb) c:\srv\venv\apb> cd dkbuild-apacheconf
    
    (apb) c:\srv\venv\apb\dkbuild-apacheconf> pip install -r requirements.txt
    ...
    (apb) c:\srv\venv\apb\dkbuild-apacheconf> pip install -e .
    Obtaining file:///C:/srv/venv/apb/dkbuild-apacheconf
    Installing collected packages: dkbuild-apacheconf
      Running setup.py develop for dkbuild-apacheconf
    Successfully installed dkbuild-apacheconf

Creating a sample ``site.ini`` file::

    (apb) c:\srv\venv\apb\dkbuild-apacheconf> cd ..
    
    (apb) c:\srv\venv\apb> mkdir mysite
    
    (apb) c:\srv\venv\apb> cd mysite
    
    (apb) c:\srv\venv\apb\mysite> emacs site.ini
    
    (apb) c:\srv\venv\apb\mysite> cat site.ini
    [site]
    sitename = example
    dns = www.example.com
    virtual_env = prod_142
    www_prefix = require
    https = yes
    
    [ssl]
    certpath = /srv/ssl/mycert/2019/42
    cert_file = example.crt
    key_file = example.key
    chain_file = YourPreferredCA.crt
    
    [wsgi]
    processes = 2
    threads = 20

Now generate the ``apache.conf`` file::
  
    (apb) c:\srv\venv\apb\mysite> dkbuild-apacheconf --skip-server run
    
    (apb) c:\srv\venv\apb\mysite> dir
     Volume in drive C has no label.
     Volume Serial Number is 04D6-81F0
    
     Directory of c:\srv\venv\apb\mysite
    
    2019-04-18  15:24    <DIR>          .
    2019-04-18  15:24    <DIR>          ..
    2019-04-18  15:24             7,405 apache.conf
    2019-04-18  15:22               278 site.ini
                   2 File(s)          7,683 bytes
                   2 Dir(s)  320,047,165,440 bytes free
    
    (apb) c:\srv\venv\apb\mysite>

The generated ``apache.conf`` file can e.g. be linked to your
``/etc/apache2/sites-available`` directory (you'll likely need to do
this using ``sudo``)::

    ln -s apache.conf /etc/apache2/sites-available/www-example.conf

and then enabled/disabled the usual way, e.g.::

    a2ensite www-example
    a2dissite www-example

The generated ``apache.conf`` from the ``site.ini`` file above::


    <VirtualHost *:443>
    
        ServerName www.example.com
        ServerAdmin bp@norsktest.no
    
        # these will be availablee from request.META
        SetEnv DK_SITE_NAME example
        SetEnv DK_SITE_DNS www.example.com
        SetEnv DK_SITE_ROOT ${SRV}/www/example
        SetEnv DK_SRV_ROOT ${SRV}
        SetEnv DKSTATICROOT ${SRV}/data/static
        SetEnv DK_VIRTUAL_ENV prod_142
    
        DocumentRoot ${SRV}/www/example/docroot
    
        <Directory "${SRV}/www/example/docroot">
            Options Indexes FollowSymLinks MultiViews
            AllowOverride None
            Order allow,deny
            Allow from all
        </Directory>
    ##:41
    
        ErrorLog /var/log/apache2/example-error.log
        CustomLog /var/log/apache2/example-access.log combined
        ServerSignature Off
    
        <Location /server-status>
            SetHandler server-status
            Order allow,deny
            Allow from ${AllowFromISP}
            Allow from 127.0.0.1
        </Location>
    
        SetOutputFilter DEFLATE
        AddOutputFilterByType DEFLATE text/html text/plain text/xml application/x-javascript text/css application/javascript image/svg+xml
        SetEnvIfNoCase Request_URI \.(?:gif|jpe?g|png|pdf|swf)$ no-gzip dont-vary
        Header append Vary User-Agent env=!dont-vary
        AddType image/svg+xml svg svgz
        AddEncoding gzip svgz
    ##:70
        # SSL Certificates
        SSLEngine on
        SSLCertificateFile /srv/ssl/mycert/2019/42/example.crt
        SSLCertificateKeyFile /srv/ssl/mycert/2019/42/example.key
        SSLCertificateChainFile /srv/ssl/mycert/2019/42/YourPreferredCA.crt
    
        SetEnvIf User-Agent ".*MSIE.*" ssl-unclean-shutdown
    
        # IE >= 9, Android >= 2.2, Java >= 6
        # SSLCipherSuite EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH
        # The real world is ugly..
        SSLCipherSuite EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH:ECDHE-RSA-AES128-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA128:DHE-RSA-AES128-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES128-GCM-SHA128:ECDHE-RSA-AES128-SHA384:ECDHE-RSA-AES128-SHA128:ECDHE-RSA-AES128-SHA:ECDHE-RSA-AES128-SHA:DHE-RSA-AES128-SHA128:DHE-RSA-AES128-SHA128:DHE-RSA-AES128-SHA:DHE-RSA-AES128-SHA:ECDHE-RSA-DES-CBC3-SHA:EDH-RSA-DES-CBC3-SHA:AES128-GCM-SHA384:AES128-GCM-SHA128:AES128-SHA128:AES128-SHA128:AES128-SHA:AES128-SHA:DES-CBC3-SHA:HIGH:!aNULL:!eNULL:!EXPORT:!DES:!MD5:!PSK:!RC4
        SSLProtocol all -SSLv2 -SSLv3
        SSLHonorCipherOrder On
        Header always set X-Frame-Options SAMEORIGIN
        Header always set X-Content-Type-Options nosniff
    
    ##:100
        # Requires Apache >= 2.4
        #SSLCompression off
        #SSLSessionTickets Off
        #SSLUseStapling on
        #SSLStaplingCache "shmcb:logs/stapling-cache(150000)"
    
        # Due to CRIME and BREACH it is not safe to use compression over https,
        # howvever, turning it off generally has major performance repercussions..
        # SetEnv no-gzip 1
    
        # BREACH migitation (turn off gzip only for foreign requests)
        SetEnvIfNoCase Referer .* self_referer=no
        SetEnvIfNoCase Referer ^https://www\.example\.com/ self_referer=yes
        SetEnvIf self_referer ^no$ no-gzip
        Header append Vary User-Agent env=!dont-vary
    
        <FilesMatch "\.(ico|flv|jpg|jpeg|png|svg|svgz|gif|woff2)$">
            Header set Cache-Control "public"
        </FilesMatch>
    
        ExpiresActive On
        ExpiresByType image/gif "access plus 1 year"
        ExpiresByType image/png "access plus 1 year"
        ExpiresByType image/jpeg "access plus 1 year"
        ExpiresByType image/svg+xml "access plus 1 year"
        ExpiresByType application/pdf "access plus 1 year"
        ExpiresByType application/javascript "access plus 1 year"
        ExpiresByType text/css "access plus 1 year"
    
        FileETag MTime Size
    
        <IfModule mod_rewrite.c>
            RewriteEngine On
    
            RewriteCond %{HTTP_HOST} !^www\. [NC]
            RewriteRule ^(.*)$ https://www.example.com/ [L,R=301]
    
            RewriteCond %{REQUEST_METHOD} ^(TRACE|TRACK|OPTIONS|PROPFIND)
            RewriteRule .* - [F]
        </IfModule>
    
        WSGIDaemonProcess example \
            display-name=example \
            processes=2 threads=20 \
            maximum-requests=10000 \
            umask=0002 \
            python-path=${SRV}/www:${SRV}/src:${SRV}/venv/prod_142/lib/python2.7/site-packages \
            python-eggs=${SRV}/.python-eggs
    
        WSGIScriptAlias / ${SRV}/www/example/wsgi.py  \
            process-group=example      \
            application-group=%{GLOBAL}
    
    ##:204
        Alias /favicon.ico ${SRV}/www/example/docroot/favicon.ico
        Alias /robots.txt ${SRV}/www/example/docroot/robots.txt
        Alias /cookies.html ${SRV}/www/example/docroot/cookies.html
        Alias /privacy-policy.html ${SRV}/www/example/docroot/privacy-policy.html
    
        Alias /static/ ${SRV}/www/example/static/
        Alias /media/ ${SRV}/www/example/media/
    
    </VirtualHost>
    
    <VirtualHost *:80>
    
        ServerName www.example.com
        ServerAdmin bp@norsktest.no
    
        # these will be availablee from request.META
        SetEnv DK_SITE_NAME example
        SetEnv DK_SITE_DNS www.example.com
        SetEnv DK_SITE_ROOT ${SRV}/www/example
        SetEnv DK_SRV_ROOT ${SRV}
        SetEnv DKSTATICROOT ${SRV}/data/static
        SetEnv DK_VIRTUAL_ENV prod_142
    
        DocumentRoot ${SRV}/www/example/docroot
    
        <Directory "${SRV}/www/example/docroot">
            Options Indexes FollowSymLinks MultiViews
            AllowOverride None
            Order allow,deny
            Allow from all
        </Directory>
    ##:41
    
        ErrorLog /var/log/apache2/example-error.log
        CustomLog /var/log/apache2/example-access.log combined
        ServerSignature Off
    
        <Location /server-status>
            SetHandler server-status
            Order allow,deny
            Allow from ${AllowFromISP}
            Allow from 127.0.0.1
        </Location>
    
        SetOutputFilter DEFLATE
        AddOutputFilterByType DEFLATE text/html text/plain text/xml application/x-javascript text/css application/javascript image/svg+xml
        SetEnvIfNoCase Request_URI \.(?:gif|jpe?g|png|pdf|swf)$ no-gzip dont-vary
        Header append Vary User-Agent env=!dont-vary
        AddType image/svg+xml svg svgz
        AddEncoding gzip svgz
    ##:70
    
        <FilesMatch "\.(ico|flv|jpg|jpeg|png|svg|svgz|gif|woff2)$">
            Header set Cache-Control "public"
        </FilesMatch>
    
        ExpiresActive On
        ExpiresByType image/gif "access plus 1 year"
        ExpiresByType image/png "access plus 1 year"
        ExpiresByType image/jpeg "access plus 1 year"
        ExpiresByType image/svg+xml "access plus 1 year"
        ExpiresByType application/pdf "access plus 1 year"
        ExpiresByType application/javascript "access plus 1 year"
        ExpiresByType text/css "access plus 1 year"
    
        FileETag MTime Size
    
        <IfModule mod_rewrite.c>
            RewriteEngine On
    
            RewriteCond %{HTTP_HOST} !^www\. [NC]
            RewriteRule ^(.*)$ http://www.example.com/ [L,R=301]
    
            RewriteCond %{REQUEST_METHOD} ^(TRACE|TRACK|OPTIONS|PROPFIND)
            RewriteRule .* - [F]
        </IfModule>
    
        WSGIProcessGroup example
        WSGIScriptAlias / ${SRV}/www/example/wsgi.py
    
    ##:204
        Alias /favicon.ico ${SRV}/www/example/docroot/favicon.ico
        Alias /robots.txt ${SRV}/www/example/docroot/robots.txt
        Alias /cookies.html ${SRV}/www/example/docroot/cookies.html
        Alias /privacy-policy.html ${SRV}/www/example/docroot/privacy-policy.html
    
        Alias /static/ ${SRV}/www/example/static/
        Alias /media/ ${SRV}/www/example/media/
    
    </VirtualHost>
