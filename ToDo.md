## Notebooks:

## xctrails.org
* error handling in create_static_files.sh
* maybe call nbconvert from script
* provide colored KML? (-> geojson_clip.py)
* replace filter_schongebiete.sh (make exported geojson compatibel)
* maybe push generated geojson to github -> to be directly picked up by geojson.io
  
## General:
* Doku page (https://pages.github.com/)

---

Do 25. Mär 02:00:01 CET 2021 starting update...
Traceback (most recent call last):
  File "./OSMSchutzgebiete.py", line 77, in <module>
    data = response.json()
  File "/home/www/osm/scripts/python/.venv/lib/python3.6/site-packages/requests/models.py", line 900, in json
    return complexjson.loads(self.text, **kwargs)
  File "/usr/lib/python3.6/json/__init__.py", line 354, in loads
    return _default_decoder.decode(s)
  File "/usr/lib/python3.6/json/decoder.py", line 339, in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
  File "/usr/lib/python3.6/json/decoder.py", line 357, in raw_decode
    raise JSONDecodeError("Expecting value", s, err.value) from None
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)