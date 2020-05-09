import os
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.configuration.Config import Config
from cloudmesh.storage.Provider import Provider
from cloudmesh.common.util import HEADING, path_expand
from cloudmesh.common.StopWatch import StopWatch

service = "copy"
fileSizes = [1,5]


class TestStorageService():

    def initial_setup(self):
        print("Initial setup")
        config = Config()

        # self.local_test = "~/.cloudmesh/storage/test"

    def test_create_source(self):
        HEADING()
        local_test = "~/.cloudmesh/storage/test"

        if not (os.path.exists(path_expand(local_test))):
            os.mkdir(path_expand(local_test))

        for fileSize in fileSizes:
            Benchmark.file(path_expand(f'{local_test}/test_file_size_{fileSize}.txt'), fileSize)

    def test_localtoaws(self):
        HEADING()

        local_test = "~/.cloudmesh/storage/test"

        sourcecloud = "local"
        targetcloud = "aws"
        for fileSize in fileSizes:
            sourceFile = path_expand(f'{local_test}/test_file_size_{fileSize}.txt')
            # targetFile = f'local_to_aws_fileSize_{fileSize}.txt'
            targetFile = f'{sourcecloud}_to_{targetcloud}_fileSize_{fileSize}.txt'
            StopWatch.start(targetFile)
            provider = Provider(service=sourcecloud)
            try:
                testResult = provider.copyFiles(source_cloud=sourcecloud, source_file=sourceFile,
                                                target_cloud=targetcloud, target_file=targetFile)
                StopWatch.status(targetFile, "Success")
            finally:
                StopWatch.stop(targetFile)

    def test_localtogoogle(self):
        HEADING()

        local_test = "~/.cloudmesh/storage/test"

        sourcecloud = "local"
        targetcloud = "google"
        for fileSize in fileSizes:
            sourceFile = path_expand(f'{local_test}/test_file_size_{fileSize}.txt')
            # targetFile = f'local_to_google_fileSize_{fileSize}.txt'
            targetFile = f'{sourcecloud}_to_{targetcloud}_fileSize_{fileSize}.txt'
            StopWatch.start(targetFile)
            provider = Provider(service=sourcecloud)
            try:
                testResult = provider.copyFiles(source_cloud=sourcecloud, source_file=sourceFile,
                                                target_cloud=targetcloud, target_file=targetFile)
                StopWatch.status(targetFile, "Success")

            finally:
                StopWatch.stop(targetFile)

    def test_awstolocal(self):
        HEADING()

        local_test = "~/.cloudmesh/storage/test"

        sourcecloud = "aws"
        targetcloud = "local"
        for fileSize in fileSizes:
            targetFileName = f"{sourcecloud}_to_{targetcloud}_fileSize_{fileSize}.txt"
            targetFile = path_expand(f'{local_test}/{targetFileName}')
            sourceFile = f'local_to_aws_fileSize_{fileSize}.txt'
            StopWatch.start(targetFileName)
            provider = Provider(service=sourcecloud)
            try:
                testResult = provider.copyFiles(source_cloud=sourcecloud, source_file=sourceFile,
                                                target_cloud=targetcloud, target_file=targetFile)
                StopWatch.status(targetFileName, "Success")
            finally:
                StopWatch.stop(targetFileName)

    def test_googletolocal(self):
        HEADING()

        local_test = "~/.cloudmesh/storage/test"

        sourcecloud = "google"
        targetcloud = "local"
        for fileSize in fileSizes:
            targetFileName = f"{sourcecloud}_to_{targetcloud}_fileSize_{fileSize}.txt"
            targetFile = path_expand(f'{local_test}/{targetFileName}')
            sourceFile = f'local_to_google_fileSize_{fileSize}.txt'
            StopWatch.start(targetFileName)
            provider = Provider(service=sourcecloud)
            try:
                testResult = provider.copyFiles(source_cloud=sourcecloud, source_file=sourceFile,
                                                target_cloud=targetcloud, target_file=targetFile)
                StopWatch.status(targetFileName, "Success")
            finally:
                StopWatch.stop(targetFileName)

    def test_awstogoogle(self):
        HEADING()

        sourcecloud = "aws"
        targetcloud = "google"
        for fileSize in fileSizes:
            targetFile = f"{sourcecloud}_to_{targetcloud}_fileSize_{fileSize}.txt"
            sourceFile = f'local_to_aws_fileSize_{fileSize}.txt'
            StopWatch.start(targetFile)
            provider = Provider(service=sourcecloud)
            try:
                testResult = provider.copyFiles(source_cloud=sourcecloud, source_file=sourceFile,
                                                target_cloud=targetcloud, target_file=targetFile)
                StopWatch.status(targetFile, "Success")
            finally:
                StopWatch.stop(targetFile)

    def test_googletoaws(self):
        HEADING()

        sourcecloud = "google"
        targetcloud = "aws"
        for fileSize in fileSizes:
            targetFile = f"{sourcecloud}_to_{targetcloud}_fileSize_{fileSize}.txt"
            sourceFile = f'local_to_google_fileSize_{fileSize}.txt'
            StopWatch.start(targetFile)
            provider = Provider(service=sourcecloud)
            try:
                testResult = provider.copyFiles(source_cloud=sourcecloud, source_file=sourceFile,
                                                target_cloud=targetcloud, target_file=targetFile)
                StopWatch.status(targetFile, "Success")
            finally:
                StopWatch.stop(targetFile)

    def test_googletoawsDir(self):
        HEADING()

        sourcecloud = "google"
        targetcloud = "aws"
        sourceFile = "a1/"
        targetFile = "a2/"

        StopWatch.start("google_to_aws_directory")
        provider = Provider(service=sourcecloud)
        try:
            testResult = provider.copyFiles(source_cloud=sourcecloud, source_file=sourceFile,
                                            target_cloud=targetcloud, target_file=targetFile)
            StopWatch.status("google_to_aws_directory", "Success")
        finally:
            StopWatch.stop("google_to_aws_directory")

    def test_awstogoogleDir(self):
        HEADING()

        sourcecloud = "aws"
        targetcloud = "google"
        sourceFile = "uploadtest1.txt"
        targetFile = "a2/testAwsToGoogle.txt"

        StopWatch.start("aws_to_google_directory")
        awsProvider = Provider(service=sourcecloud)
        try:
            testResult = awsProvider.copyFiles(
            source_cloud=sourcecloud, source_file=sourceFile, target_cloud=targetcloud, target_file=targetFile)
            StopWatch.status("aws_to_google_directory", "Success")
        finally:
            StopWatch.stop("aws_to_google_directory")

    def test_googletoawsDir2(self):
        HEADING()

        sourcecloud = "google"
        targetcloud = "aws"
        sourceFile = "a1/testfolder/"
        targetFile = "a1/testfolder2/"

        StopWatch.start("google_to_aws_directory2")
        awsProvider = Provider(service=sourcecloud)
        try:
            testResult = awsProvider.copyFiles(
            source_cloud=sourcecloud, source_file=sourceFile, target_cloud=targetcloud, target_file=targetFile)
            StopWatch.status("google_to_aws_directory2", "Success")
        finally:
            StopWatch.stop("google_to_aws_directory2")

    def test_benchmark(self):
        StopWatch.benchmark(sysinfo=False, csv=True, tag=service)


