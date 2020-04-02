import pytest
from cloudmesh.configuration.Config import Config
from cloudmesh.storage_service.providers.Provider import Provider

from cloudmesh.common.StopWatch import StopWatch


class TestStorageService():
    def initial_setup(self):
        print("Initial setup")
        config = Config()

        self.local_dir = config["cloudmesh"]["storage"]["local"]["dir"]

    def test_listaws(self):
        StopWatch.start("LIST AWS")
        awsProvider = Provider(service="aws")
        testResult = awsProvider.list("test1")
        StopWatch.stop("LIST AWS")
        assert testResult is not None

    def test_listgoogle(self):
        StopWatch.start("LIST GOOGLE")
        googleProvider = Provider(service="google")
        testResult = googleProvider.list("a1")
        StopWatch.stop("LIST GOOGLE")
        assert testResult is not None

    def test_localtoaws_dir(self):
        sourcecloud = "local"
        targetcloud = "aws"
        sourceFile = "uploadtest"
        targetFile = "testFol1/"

        StopWatch.start("LOCAL_TO_AWS_DIR")
        awsProvider = Provider(service="aws")
        testResult = awsProvider.copy(sourcecloud, targetcloud, sourceFile, targetFile)
        StopWatch.stop("LOCAL_TO_AWS_DIR")
        assert testResult is not None

    def test_awstolocal_dir(self):
        sourcecloud = "local"
        targetcloud = "aws"
        sourceFile = "testFol1/"
        targetFile = "uploadtest"

        StopWatch.start("AWS_TO_LOCAL_DIR")
        awsProvider = Provider(service="aws")
        testResult = awsProvider.copy(sourcecloud, targetcloud, sourceFile, targetFile)
        StopWatch.stop("AWS_TO_LOCAL_DIR")
        assert testResult is not None

    def test_AwsToLocal(self):
        sourcecloud = "aws"
        targetcloud = "local"
        sourceFile = "test1.txt"
        targetFile = "testAwsToLocal.txt"

        StopWatch.start("AWS_TO_LOCAL")
        awsProvider = Provider(service=sourcecloud)
        testResult = awsProvider.copy(sourcecloud, targetcloud, sourceFile, targetFile)
        StopWatch.stop("AWS_TO_LOCAL")

        assert testResult is not None

    def test_localtoaws(self):
        sourcecloud = "local"
        targetcloud = "aws"
        sourceFile = "test1.txt"
        targetFile = "testLocalToAws.txt"

        StopWatch.start("LOCAL_TO_AWS")
        awsProvider = Provider(service="aws")
        testResult = awsProvider.copy(sourcecloud, targetcloud, sourceFile, targetFile)
        StopWatch.stop("LOCAL_TO_AWS")
        assert testResult is not None

    def test_awstogoogle(self):
        sourcecloud = "aws"
        targetcloud = "google"
        sourceFile = "test1.txt"
        targetFile = "testAwsToGoogle.txt"

        StopWatch.start("AWS_TO_GOOGLE")
        awsProvider = Provider(service=sourcecloud)
        testResult = awsProvider.copy(sourcecloud, targetcloud, sourceFile, targetFile)
        StopWatch.stop("AWS_TO_GOOGLE")

        assert testResult is not None

    def test_googletolocal(self):
        sourcecloud = "google"
        targetcloud = "local"
        sourceFile = "test1.txt"
        targetFile = "testGoogleToLocal.txt"

        StopWatch.start("GOOGLE_TO_LOCAL")
        googleProvider = Provider(service=sourcecloud)
        testResult = googleProvider.copy(sourcecloud, targetcloud, sourceFile, targetFile)
        StopWatch.stop("GOOGLE_TO_LOCAL")

        assert testResult is not None

    def test_localtogoogle(self):
        sourcecloud = "local"
        targetcloud = "google"
        sourceFile = "test1.txt"
        targetFile = "text1copy.txt"

        StopWatch.start("LOCAL_TO_GOOGLE")
        googleProvider = Provider(service="google")
        testResult = googleProvider.copy(sourcecloud, targetcloud, sourceFile, targetFile)
        StopWatch.stop("LOCAL_TO_GOOGLE")

        assert testResult is not None

    def test_googletoaws(self):
        sourcecloud = "aws"
        targetcloud = "google"
        sourceFile = "test1.txt"
        targetFile = "test1Copy.txt"

        StopWatch.start("GOOGLE_TO_AWS")
        googleProvider = Provider(service=sourcecloud)
        testResult = googleProvider.copy(sourcecloud, targetcloud, sourceFile, targetFile)
        StopWatch.stop("GOOGLE_TO_AWS")

        assert testResult is not None

    def test_deletegoogle(self):
        StopWatch.start("DELETE GOOGLE")
        googleProvider = Provider(service="google")
        testResult = googleProvider.delete("text1copy.txt")
        StopWatch.stop("DELETE GOOGLE")
        assert testResult is not None

    def test_deleteaws(self):
        StopWatch.start("DELETE AWS")
        awsprovider = Provider(service="aws")
        testResult = awsprovider.delete("testLocalToAws.txt.txt")
        StopWatch.stop("DELETE AWS")
        assert testResult is not None

    def test_results(self):
        StopWatch.benchmark(csv=False)