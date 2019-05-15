from flask import jsonify
from bson import json_util
import json
from cloudmesh.vdir.api.manager import Vdir


def setup():
    vdir = Vdir()
    return vdir


def mkdir(params=None):
    vdir = setup()
    dir = params['dir']
    d = vdir.mkdir(dir)
    return jsonify(d)


def cd(dir=None):
    vdir = setup()
    d = vdir.cd(dir)
    return json.loads(json_util.dumps(d))


def ls(dir=None):
    vdir = setup()
    d = vdir.ls(dir)
    return d


def add(params=None):
    vdir = setup()
    endpoint = params['endpoint']
    dir_and_name = params['dir_and_name']
    d = vdir.add(endpoint, dir_and_name)
    return json.loads(json_util.dumps(d))


def delete(dir_or_name):
    vdir = setup()
    d = vdir.delete(dir_or_name)
    return json.loads(json_util.dumps(d))


def status(dir_or_name):
    vdir = setup()
    d = vdir.status(dir_or_name)
    return json.loads(json_util.dumps(d))


def get(name, destination=None):
    vdir = setup()
    d = vdir.get(name, destination)
    return jsonify(d)
