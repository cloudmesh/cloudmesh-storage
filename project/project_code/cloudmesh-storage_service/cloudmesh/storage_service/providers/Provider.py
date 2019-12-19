from cloudmesh.storage_service.providers.aws.aws_provider import Provider as AWS_Provider
from cloudmesh.storage_service.providers.google.google_provider import Provider as Google_Provider
from cloudmesh.storage.StorageNewABC import StorageABC

class Provider(StorageABC):

    def __init__(self, service=None, config="~/.cloudmesh/cloudmesh.yaml"):

        super(Provider, self).__init__(service=service, config=config)

        if self.kind == "aws-s3":
            self.provider = AWS_Provider(service=service, config=config)
        elif self.kind == "google":
            self.provider = Google_Provider(service=service, config=config)

    def copy(self, source_cloud , target_cloud, source_file, target_file):

        return self.provider.copy(source_cloud , target_cloud, source_file, target_file)


    def delete(self, source):

        return self.provider.delete(source)


    def list (self, source_cloud= None, location=None):

        return self.provider.list(source_cloud)
