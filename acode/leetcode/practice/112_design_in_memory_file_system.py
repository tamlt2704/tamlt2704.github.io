# 588. Design In-Memory File System
# Difficulty: Hard | Topic: Design
#
# Design an in-memory file system to simulate the following functions:
# - ls(path): list directory contents or file name
# - mkdir(path): make a new directory (create intermediate dirs as needed)
# - addContentToFile(filePath, content): append content to a file
# - readContentFromFile(filePath): return file content
#
# Example: FileSystem() -> ls("/") -> mkdir("/a/b/c") -> addContentToFile("/a/b/c/d","hello")
# Constraints: paths start with '/', lowercase letters and '/' only


class FileSystem:
    def __init__(self):
        pass

    def ls(self, path: str) -> list[str]:
        pass

    def mkdir(self, path: str) -> None:
        pass

    def addContentToFile(self, filePath: str, content: str) -> None:
        pass

    def readContentFromFile(self, filePath: str) -> str:
        pass
