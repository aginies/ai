# SearNXG

Start the container one time, stop it. Edit the file `/etc/searxng/settings.yml`:
to add **json** around line 78:
```ini
# remove format to deny access, use lower case.
# formats: [html, csv, json, rss]
  formats:
    - html
    - json
```
