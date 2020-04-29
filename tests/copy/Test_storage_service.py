from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.configuration.Config import Config
from cloudmesh.storage.Provider import Provider
from cloudmesh.common.util import HEADING

service = "aws-google"


class TestStorageService():
    def initial_setup(self):
        print("Initial setup")
        config = Config()

      #  self.local_dir = config["cloudmesh"]["storage"]["local"]["dir"]


    def test_awstogoogle(self):
        HEADING()

        sourcecloud = "aws"
        targetcloud = "google"
        sourceFile = "uploadtest1.txt"
        targetFile = "testAwsToGoogle3.txt"

        Benchmark.Start("AWS_TO_GOOGLE")
        awsProvider = Provider(service=sourcecloud)
        testResult = awsProvider.copyFiles(
            source_cloud=sourcecloud, source_file=sourceFile, target_cloud=targetcloud, target_file=targetFile )
        Benchmark.Stop()

       # assert testResult is not None

    def test_googletoaws(self):
        HEADING()

        sourcecloud = "google"
        targetcloud = "aws"
        sourceFile = "uploadtest1.txt"
        targetFile = "testGoogleToAws1.txt"

        Benchmark.Start("GOOGLE_TO_AWS1")
        awsProvider = Provider(service=sourcecloud)
        testResult = awsProvider.copyFiles(
          source_cloud=sourcecloud, source_file=sourceFile, target_cloud=targetcloud, target_file=targetFile )

        Benchmark.Stop()

    def test_googletoawsDir(self):
        HEADING()

        sourcecloud = "google"
        targetcloud = "aws"
        sourceFile = "a1/"
        targetFile = "a2/"

        Benchmark.Start("GOOGLE_TO_AWS2")
        awsProvider = Provider(service=sourcecloud)
        testResult = awsProvider.copyFiles(
            source_cloud=sourcecloud, source_file=sourceFile, target_cloud=targetcloud, target_file=targetFile )
        Benchmark.Stop()

    def test_googletoawsDir2(self):
        HEADING()

        sourcecloud = "google"
        targetcloud = "aws"
        sourceFile = "a1/testfolder/"
        targetFile = "a1/testfolder2/"

        Benchmark.Start("GOOGLE_TO_AWS3")
        awsProvider = Provider(service=sourcecloud)
        testResult = awsProvider.copyFiles(
            source_cloud=sourcecloud, source_file=sourceFile, target_cloud=targetcloud, target_file=targetFile )
        Benchmark.Stop()

    def test_benchmark(self):
        Benchmark.print(sysinfo=False, csv=True, tag=service)
