import pytest
from cloudmesh.configuration.Config import Config
from cloudmesh.storage_service.providers.Provider import Provider

from cloudmesh.common.StopWatch import StopWatch


class TestStorageService():
    def initial_setup(self):
        print("Initial setup")
        config = Config()

        self.local_dir = config["cloudmesh"]["storage"]["local"]["dir"]

    def test_localtoaws_dir(self):
        sourcecloud = "local"
        targetcloud = "aws"
        sourceFile = "uploadtest"
        targetFile = "testFol/"

        StopWatch.start("LOCAL_TO_AWS")
        awsProvider = Provider(service="aws")
        testResult = awsProvider.copy(sourcecloud, targetcloud, sourceFile, targetFile)
        StopWatch.stop("LOCAL_TO_AWS")
        assert testResult is not None

    def test_awstolocal_dir(self):
        sourcecloud = "local"
        targetcloud = "aws"
        sourceFile = "testFol/"
        targetFile = "uploadtest"

        StopWatch.start("LOCAL_TO_AWS")
        awsProvider = Provider(service="aws")
        testResult = awsProvider.copy(sourcecloud, targetcloud, sourceFile, targetFile)
        StopWatch.stop("LOCAL_TO_AWS")
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
        sourceFile = "testLocalToAws.txt"
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
        targetFile = "testGoogleToAws.txt"

        StopWatch.start("GOOGLE_TO_LOCAL")
        googleProvider = Provider(service=sourcecloud)
        testResult = googleProvider.copy(sourcecloud, targetcloud, sourceFile, targetFile)
        StopWatch.stop("GOOGLE_TO_LOCAL")

        assert testResult is not None

    def test_localtogoogle(self):
        sourcecloud = "local"
        targetcloud = "google"
        sourceFile = "test1.txt"
        targetFile = "testLocalToGoogle.txt"

        StopWatch.start("LOCAL_TO_GOOGLE")
        googleProvider = Provider(service="google")
        testResult = googleProvider.copy(sourcecloud, targetcloud, sourceFile, targetFile)
        StopWatch.stop("LOCAL_TO_GOOGLE")

        assert testResult is not None

    def test_googletoaws(self):
        sourcecloud = "aws"
        targetcloud = "google"
        sourceFile = "test1.txt"
        targetFile = "testGoogleToAws.txt"

        StopWatch.start("GOOGLE_TO_AWS")
        googleProvider = Provider(service=sourcecloud)
        testResult = googleProvider.copy(sourcecloud, targetcloud, sourceFile, targetFile)
        StopWatch.stop("GOOGLE_TO_AWS")

        assert testResult is not None