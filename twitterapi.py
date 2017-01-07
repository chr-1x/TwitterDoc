#!/bin/python3

import re, json, os, sys
import requests
from bs4 import BeautifulSoup as bs

class APIParam:
    def __init__(self):
        self.name = ""
        self.required = False
        self.desc = ""
        self.example = ""
        self.default = ""
        self.type = ""

class APIEndpoint:
    def __init__(self):
        self.url = ""
        self.path = ""
        self.desc = ""
        self.method = ""
        self.params = []

class APIEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, APIEndpoint):
            paramlist = []
            for param in obj.params:
                paramdict = { "name" : param.name,
                              "required" : param.required,
                              "desc" : param.desc,
                              "type" : param.type }
                if (param.example != ""):
                    paramdict["example"] = param.example
                if (param.default != ""):
                    paramdict["default"] = param.default
                paramlist.append(paramdict)

            return { "path" : obj.path,
                     "desc" : obj.desc,
                     "method" : obj.method,
                     "params": paramlist }

        return json.JSONEncoder.default(self, obj)

def request_and_parse(url):
    r = requests.get(url)
    r.encoding = "utf-8"
    return bs(r.text, 'html.parser')

def get_endpoint_list():
    doc = request_and_parse("https://dev.twitter.com/rest/reference")
    result = []
    for tag in doc.find(id="reference-documentation").find_all("li", class_="toctree-l1"):
        result.append(tag.contents[0]['href'])
    return [s.replace("%3A", ":") for s in result if (s.find("reference") == 0) ]

def replace_all(str, l1, l2):
    result = str
    for i in range(len(l1)):
        result = result.replace(l1[i], l2[i])
    return result

def parse_api_info(doc):
    result = APIEndpoint()

    try: 
        heading = doc.find("h1")
        title = next(heading.children).string.strip()
        result.method = title.split(" ")[0]
        result.path = title.split(" ")[1]

        url_parent = doc.find(id="resource-url")
        result.url = next(url_parent.find("p").stripped_strings).strip()

        body_ps = doc.find(class_="document").find(class_="section").find_all("p", recursive=False)
        result.desc = " ".join(sum([[s.strip(" ") for s in p.strings] for p in body_ps], [])).strip()
        result.desc = replace_all(result.desc, ['\u2019', '\u201c', '\u201d'], ['\'', '\"', '\"'])

        params_parent = doc.find(id="parameters")
        params = params_parent.find_all("tr")
        if (len(params) > 1):
            params = params[1:]
    except AttributeError as e:
        print("Check %s, got error %s" % (result.url, e), file=sys.stderr)


    for param in params:
        try:
            cells = param.find_all("td")
            p = APIParam()
            p.name = "".join(cells[0].stripped_strings)
            p.required = next(cells[1].stripped_strings) == "required"
            p.desc = "".join(cells[2].strings).strip()
            p.desc = replace_all(p.desc, ['\u2019', '\u201c', '\u201d'], ['\'', '\"', '\"'])

            p.default = "".join(cells[4].stripped_strings)
            p.example = "".join(cells[4].stripped_strings)
            result.params.append(p)
        except AttributeError as e:
            print("Check %s, got error %s" % (result.url, e), file=sys.stderr)
    return result

def infer_type(param):
    idish = ""
    intish = False
    if (hasattr(param, "example")):
        if (param.example == "true" or param.example == "false"):
            return "bool"
        try:
            val = int(param.example)
            if (val == 12345 or val == 54321): idish = "_id"
            intish = True
        except ValueError:
            pass
    if (param.name.find("color") >= 0):
        return "color"
    if (param.name.find("cursor") >= 0):
        return "cursor"
    if (param.name.find("count") >= 0):
        return "int"
    if (param.name == "media"):
        return "binary"
    if (param.name.find("_ids") > 0):
        idish = "_ids"
    elif (param.name.find("_id") > 0 or param.name == "id"):
        idish = "_id"

    if (len(idish) > 0):
        if (param.name.find("user") >= 0): return "user" + idish
        if (param.name.find("place") >= 0): return "place" + idish
        if (param.desc.find("search") >= 0): return "search" + idish
        if (param.desc.find("media") >= 0): return "media" + idish
        return "status" + idish

    if (intish): return "int"

    return "string"

endpoints = get_endpoint_list()
api = []

for endpoint in endpoints:
    doc = request_and_parse("https://dev.twitter.com/rest/" + endpoint)
    parsed = parse_api_info(doc)
    for param in parsed.params:
        param.type = infer_type(param)
    api.append(parsed)

print(APIEncoder().encode(api))

