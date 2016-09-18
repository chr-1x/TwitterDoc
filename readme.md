# TwitterDoc

Ever needed a machine-readable format of the Twitter API docs? I did, so I wrote a python script to crawl the HTML of
the REST API pages and generate a JSON document describing the API. And just because I care, I also wrote a schema for
the schema. (The schema for the schema for the schema is available at [json-schema.org](http://json-schema.org/).

The script is written for Python 3 and uses the following libraries:

 - beautifulsoup4
 - requests

These will have to be installed (`pip install bs4 requests`) before the script will run. By default, it'll output a
minified JSON document (this is the default behavior of `json.JSONEncoder`) -- you can pipe the output to `python -m
json.tool` to validate and pretty-print. Example:

    python twitterapi.py | python -m json.tool > api.json

The resulting document can be used to help generate API usage code in various languages or alternate/offline
documentation of the REST API. **Note**: the script attempts to infer the types of the REST parameters but may be
inaccurate&mdash;be sure to manually inspect / test code using that information before deploying.

Support for the twitter Streaming API may be added eventually, but for now the script only outputs the schema for the
REST endpoints described on [the public REST API page](https://dev.twitter.com/rest/public).

