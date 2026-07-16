import os
import sys
import hashlib
import time
import smtplib
from email.message import EmailMessage

Border = "-" * 50
LogFile = "Log.txt"


def CalculateChecksum(FilePath):
    """Calculate MD5 checksum of a file."""
    md5 = hashlib.md5()

    with open(FilePath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)

    return md5.hexdigest()


def SendEmail(SenderEmail, SenderPassword, ReceiverEmail, Attachment):
    """Send Log.txt as email attachment."""

    try:
        msg = EmailMessage()

        msg["Subject"] = "Duplicate File Removal Report"
        msg["From"] = SenderEmail
        msg["To"] = ReceiverEmail

        msg.set_content(
            "Hello,\n\n"
            "Please find the attached Duplicate File Removal Report.\n\n"
            "Thank You."
        )

        with open(Attachment, "rb") as f:
            file_data = f.read()
            file_name = os.path.basename(Attachment)

        msg.add_attachment(
            file_data,
            maintype="application",
            subtype="octet-stream",
            filename=file_name,
        )

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()

        server.login(SenderEmail, SenderPassword)

        server.send_message(msg)

        server.quit()

        print(Border)
        print("Email sent successfully.")
        print(Border)

    except Exception as e:
        print("Unable to send email:", e)


def RemoveDuplicatesWithTime(DirectoryName):
    """Find duplicate files, delete them, write log and send email."""

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
                print("Error reading file:", FilePath)
                print(e)

    duplicates = {k: v for k, v in ChecksumMap.items() if len(v) > 1}

    deleted_count = 0

    with open(LogFile, "w") as log:

        if duplicates:

            log.write("Duplicate File Removal Report\n")
            log.write(Border + "\n")

            for checksum, files in duplicates.items():

                log.write("Checksum : %s\n" % checksum)
                log.write("Kept File : %s\n" % files[0])

                print("Kept :", files[0])

                for duplicate in files[1:]:

                    try:
                        os.remove(duplicate)

                        log.write("Deleted : %s\n" % duplicate)

                        print("Deleted :", duplicate)

                        deleted_count += 1

                    except Exception as e:
                        print("Unable to delete:", duplicate)
                        print(e)

                log.write(Border + "\n")

        else:
            log.write("No duplicate files found.\n")

    EndTime = time.time()

    ExecutionTime = EndTime - StartTime

    print(Border)

    if duplicates:
        print("Total duplicate files deleted:", deleted_count)
    else:
        print("No duplicate files found.")

    print("Log file created:", LogFile)

    print("Execution Time : %.4f seconds" % ExecutionTime)

    print(Border)

    # ---------------- EMAIL SETTINGS ----------------

    SenderEmail = "your_email@gmail.com"
    SenderPassword = "your_app_password"      # Gmail App Password
    ReceiverEmail = "receiver_email@gmail.com"

    # Send the Log.txt file
    SendEmail(SenderEmail, SenderPassword, ReceiverEmail, LogFile)


def main():

    print(Border)
    print("----  Duplicate Removal With Email ----")
    print(Border)

    if len(sys.argv) == 2:

        if sys.argv[1] == "--h" or sys.argv[1] == "--H":

            print("This application removes duplicate files.")
            print("It also creates Log.txt and emails the report.")

        elif sys.argv[1] == "--u" or sys.argv[1] == "--U":

            print("Usage:")
            print("python DirectoryDuplicateRemovalTime.py DirectoryName")

        else:

            print("Directory :", sys.argv[1])

            print(Border)

            RemoveDuplicatesWithTime(sys.argv[1])

    else:

        print("Invalid number of arguments.")
        print("Use --h for help")
        print("Use --u for usage")

    print(Border)
    print("Thank you for using our application")
    print(Border)


if __name__ == "__main__":
    main()
