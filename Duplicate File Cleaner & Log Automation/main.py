import os
import sys
import hashlib
import time

Border = "-" * 50
LogFile = "Log.txt"

def CalculateChecksum(FilePath):
    """Calculate MD5 checksum of a file."""
    md5 = hashlib.md5()
    with open(FilePath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)
    return md5.hexdigest()

def RemoveDuplicatesWithTime(DirectoryName):
    """Find and delete duplicate files. Write log. Display execution time."""

    if not os.path.exists(DirectoryName):
        print("Unable to find directory:", DirectoryName)
        return

    if not os.path.isdir(DirectoryName):
        print("Given path is not a directory:", DirectoryName)
        return

    StartTime = time.time()

    print("Scanning for duplicate files in:", DirectoryName)
    print(Border)

    ChecksumMap = {}

    for root, dirs, files in os.walk(DirectoryName):
        for file in files:
            FilePath = os.path.join(root, file)
            try:
                checksum = CalculateChecksum(FilePath)
                if checksum in ChecksumMap:
                    ChecksumMap[checksum].append(FilePath)
                else:
                    ChecksumMap[checksum] = [FilePath]
            except Exception as e:
                print("Error reading file:", FilePath, "->", e)

    duplicates = {k: v for k, v in ChecksumMap.items() if len(v) > 1}

    deleted_count = 0

    with open(LogFile, 'w') as log:
        if duplicates:
            log.write("Deleted Duplicate Files\n")
            log.write(Border + "\n")
            for checksum, files in duplicates.items():
                log.write("Checksum: %s\n" % checksum)
                log.write("  Kept   : %s\n" % files[0])
                print("Kept    :", files[0])
                for f in files[1:]:
                    os.remove(f)
                    log.write("  Deleted: %s\n" % f)
                    print("Deleted :", f)
                    deleted_count += 1
                log.write(Border + "\n")
        else:
            log.write("No duplicate files found in: %s\n" % DirectoryName)

    EndTime = time.time()
    ExecutionTime = EndTime - StartTime

    print(Border)
    if duplicates:
        print("Total duplicate files deleted: %d" % deleted_count)
        print("Deleted file names written to:", LogFile)
    else:
        print("No duplicate files found in:", DirectoryName)
        print("Log written to:", LogFile)

    print(Border)
    print("Execution time: %.4f seconds" % ExecutionTime)


def main():

    print(Border)
    print("--Marvellous Duplicate Removal With Time System--")
    print(Border)

    if len(sys.argv) == 2:
        if sys.argv[1] == "--h" or sys.argv[1] == "--H":
            print("This script is used to:")
            print("1 : Find and delete duplicate files in a directory")
            print("2 : Keeps one copy of each duplicate file")
            print("3 : Writes deleted file names into Log.txt")
            print("4 : Displays total execution time of the script")

        elif sys.argv[1] == "--u" or sys.argv[1] == "--U":
            print("Use the script as:")
            print("DirectoryDusplicateRemovalTime.py DirectoryName")
            print("DirectoryName : Name of the directory to process")

        else:
            print("Inside duplicate removal with time logic")
            print("Directory name:", sys.argv[1])
            print(Border)
            RemoveDuplicatesWithTime(sys.argv[1])

    # python DirectoryDusplicateRemovalTime.py "Demo"
    else:
        print("Invalid number of command line arguments")
        print("Use --h for help and --u for usage of the script")

    print(Border)
    print("---------Thank you for using our script ---------")
    print(Border)


if __name__ == "__main__":
    main()
