from flask import jsonify
from cloudmesh.common.console import Console


def setup(kind):
    config = "~/.cloudmesh/cloudmesh.yaml"
    if kind == "local":
        from cloudmesh.storage.provider.local.Provider import \
            Provider as LocalProvider
        provider = LocalProvider(service=kind)
    elif kind == "box":
        from cloudmesh.storage.provider.box.Provider import \
            Provider as BoxProvider
        provider = BoxProvider(service=kind)
    elif kind == "gdrive":
        from cloudmesh.storage.provider.gdrive.Provider import \
            Provider as GdriveProvider
        provider = GdriveProvider(service=kind)
    elif kind == "azureblob":
        from cloudmesh.storage.provider.azureblob.Provider import \
            Provider as AzureblobProvider
        provider = AzureblobProvider(service=kind)
    elif kind == "awss3":
        from cloudmesh.storage.provider.awss3.Provider import \
            Provider as AwsProvider

        provider = AwsProvider(service=kind)
    else:
        Console.error(f"Storage Provider is not supported: {kind}")
    return provider


def create_dir(service, directory):
    provider = setup(service)
    d = provider.create_dir(service, directory)
    return jsonify(d)


def put(params=None):
    service = params['service']
    source = params['source']
    destination = params['destination']
    recursive = params['recursive']

    provider = setup(service)
    d = provider.put(service, source, destination, recursive)
    return jsonify(d)


def get(service, source, destination, recursive=False):
    provider = setup(service)
    d = provider.get(service, source, destination, recursive)
    return jsonify(d)


def list(service, directory, recursive=False):
    provider = setup(service)
    d = provider.list(service, directory, recursive)
    return jsonify(d)


def search(service, directory, filename, recursive=False):
    provider = setup(service)
    d = provider.search(service, directory, filename, recursive)
    return jsonify(d)


def delete(service, source, recursive=False):
    provider = setup(service)
    d = provider.delete(service, source, recursive)
    return jsonify(d)
