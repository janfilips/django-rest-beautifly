# ioi-game

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/4069ca481ad64ea196947ef42974a518)](https://www.codacy.com?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ioi-game/ioi-game&amp;utm_campaign=Badge_Grade)


## Notes on configuration

Nginx config must contain -

    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;

..in order for the django social-auth to work.

### Facebook OAUTH integration

Add https://mydomain/social-auth/complete/facebook to Valid Redirect URLs

To register the app visit https://developer.facebook.com/

### Google OAUTH2 integration

Add https://mydomain/social-auth/complete/google-oauth2/ to Authorized Redirect URLs

To register the app visit https://developers.google.com/identity/sign-in/web/sign-in

To edit the app visit https://console.developers.google.com/apis/dashboard


### SSL Certificates

Easiest way to load on SSL certificates is using Certbot:

 $ certbot --nginx -d aws.filips -d www.aws.filips --nginx-server-root=/usr/local/nginx/conf --nginx-ctl=/usr/local/nginx/sbin/nginx
