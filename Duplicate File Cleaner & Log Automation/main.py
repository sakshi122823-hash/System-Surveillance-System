# command line input

import psutil
import sys
import os
import time
import schedule
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

Border = "-" * 50

# ─── Feature 1 : Thread Monitoring ───────────────────────────────────────────
def ThreadScan():
    """For each running process return Process Name, PID, Thread Count."""
    ThreadData = []
    for proc in psutil.process_iter():
        try:
            info = {}
            info["pid"]          = proc.pid
            info["name"]         = proc.name()
            info["thread_count"] = proc.num_threads()
            ThreadData.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return ThreadData

# ─── Feature 2 : Open Files Monitoring ───────────────────────────────────────
def OpenFilesScan():
    """For each process return number of open file descriptors."""
    OpenFilesData = []
    for proc in psutil.process_iter():
        try:
            info = {}
            info["pid"]  = proc.pid
            info["name"] = proc.name()
            try:
                info["open_files_count"] = len(proc.open_files())
            except (psutil.AccessDenied, PermissionError):
                info["open_files_count"] = "Access Denied"
            OpenFilesData.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return OpenFilesData

# ─── Feature 3 : Actual Memory Allocation ────────────────────────────────────
def MemoryScan():
    """Return RSS, VMS, Memory% for each process. Also return Top 10 by memory."""
    MemoryData = []
    for proc in psutil.process_iter():
        try:
            info = {}
            info["pid"]            = proc.pid
            info["name"]           = proc.name()
            mem_info               = proc.memory_info()
            info["rss"]            = mem_info.rss / (1024 * 1024)   # MB
            info["vms"]            = mem_info.vms / (1024 * 1024)   # MB
            info["memory_percent"] = proc.memory_percent()
            MemoryData.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    Top10 = sorted(MemoryData, key=lambda x: x["memory_percent"], reverse=True)[:10]
    return MemoryData, Top10

# ─── Feature 4 : Email Report ─────────────────────────────────────────────────
def SendEmail(ReceiverMail, LogFilePath, SummaryText):
    """Send email with log file attachment and summary."""
    SenderMail     = "sakshi152005@gmail.com"
    SenderPassword = "aihj sflr zrvx tmie"

    try:
        msg = MIMEMultipart()
        msg["From"]    = SenderMail
        msg["To"]      = ReceiverMail
        msg["Subject"] = " Platform Surveillance Report - " + time.ctime()

        msg.attach(MIMEText(SummaryText, "plain"))

        if os.path.exists(LogFilePath):
            with open(LogFilePath, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition",
                                "attachment; filename=%s" % os.path.basename(LogFilePath))
                msg.attach(part)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SenderMail, SenderPassword)
        server.sendmail(SenderMail, ReceiverMail, msg.as_string())
        server.quit()
        print("Email sent successfully to:", ReceiverMail)

    except Exception as e:
        print("Unable to send email:", e)

# ─── Process Scan (original) ──────────────────────────────────────────────────
def ProcessScan():
    """Scan all running processes and return their info."""
    listprocess = []

    # warm up for cpu percent
    for proc in psutil.process_iter():
        try:
            proc.cpu_percent()
        except:
            pass

    time.sleep(0.2)

    for proc in psutil.process_iter():
        try:
            info = proc.as_dict(attrs=["pid", "name", "username", "status", "create_time"])
            # convert create time
            try:
                info["create_time"] = time.strftime("%y-%m-%d %H:%M:%S",
                                                    time.localtime(info["create_time"]))
            except:
                info["create_time"] = "NA"
            info["cpu_percent"]    = proc.cpu_percent(None)
            info["memory_percent"] = proc.memory_percent()
            listprocess.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return listprocess

# ─── Create Log ───────────────────────────────────────────────────────────────
def CreateLog(FolderName, ReceiverMail):
    """Create a full system surveillance log and email it."""

    Ret = os.path.exists(FolderName)

    if Ret == True:
        Ret = os.path.isdir(FolderName)
        if Ret == False:
            print("Unable to create folder")
            return
    else:
        os.mkdir(FolderName)
        print("Directory for log files gets created successfully")

    timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
    FileName  = os.path.join(FolderName, "MarvellousLog%s.log" % timestamp)
    print("Log file created:", FileName)

    fobj = open(FileName, "w")
    fobj.write(Border + "\n")
    fobj.write("-----Marvellous Platfrom Surveillance System -----\n")
    fobj.write("Log created at:" + time.ctime() + "\n")
    fobj.write(Border + "\n\n")

    # ── System Usage ──────────────────────────────────────────────────────────
    fobj.write("---------------system usage ---------------\n")
    fobj.write("cpu usage : %s %%\n" % psutil.cpu_percent())
    print("cpu usage:", psutil.cpu_percent())

    mem = psutil.virtual_memory()
    fobj.write("ram usage %s %%\n" % mem.percent)
    fobj.write(Border + "\n")
    print("Ram usage:", mem.percent)

    # ── Disk Usage ────────────────────────────────────────────────────────────
    fobj.write("\ndisk usage report\n")
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            fobj.write("%s -> %s %% used\n" % (part.mountpoint, usage.percent))
        except:
            pass
    fobj.write(Border + "\n")

    # ── Network Usage ─────────────────────────────────────────────────────────
    net = psutil.net_io_counters()
    fobj.write("\nnetwork usage report\n")
    fobj.write("sent : %.2f MB\n" % (net.bytes_sent / (1024 * 1024)))
    fobj.write("recv : %.2f MB\n" % (net.bytes_recv / (1024 * 1024)))
    fobj.write(Border + "\n")

    # ── Feature 1 : Thread Monitoring ─────────────────────────────────────────
    fobj.write("\n---------------thread monitoring---------------\n")
    fobj.write("Timestamp: %s\n" % time.ctime())
    fobj.write(Border + "\n")
    ThreadData = ThreadScan()
    for info in ThreadData:
        fobj.write("Process Name : %s\n" % info.get("name"))
        fobj.write("PID          : %s\n" % info.get("pid"))
        fobj.write("Thread Count : %s\n" % info.get("thread_count"))
        fobj.write(Border + "\n")
    print("Thread monitoring data written to log")

    # ── Feature 2 : Open Files Monitoring ─────────────────────────────────────
    fobj.write("\n---------------open files monitoring---------------\n")
    fobj.write(Border + "\n")
    OpenFilesData = OpenFilesScan()
    for info in OpenFilesData:
        fobj.write("Process Name     : %s\n" % info.get("name"))
        fobj.write("PID              : %s\n" % info.get("pid"))
        fobj.write("Open Files Count : %s\n" % info.get("open_files_count"))
        fobj.write(Border + "\n")
    print("Open files monitoring data written to log")

    # ── Feature 3 : Actual Memory Allocation ──────────────────────────────────
    fobj.write("\n---------------actual memory allocation---------------\n")
    fobj.write(Border + "\n")
    MemoryData, Top10 = MemoryScan()
    for info in MemoryData:
        fobj.write("Process Name    : %s\n" % info.get("name"))
        fobj.write("PID             : %s\n" % info.get("pid"))
        fobj.write("RSS (Actual RAM): %.2f MB\n" % info.get("rss"))
        fobj.write("VMS (Virtual)   : %.2f MB\n" % info.get("vms"))
        fobj.write("Memory %%        : %.2f\n"   % info.get("memory_percent"))
        fobj.write(Border + "\n")

    fobj.write("\n---------------top 10 memory consuming processes---------------\n")
    fobj.write(Border + "\n")
    for info in Top10:
        fobj.write("Process Name    : %s\n" % info.get("name"))
        fobj.write("PID             : %s\n" % info.get("pid"))
        fobj.write("RSS (Actual RAM): %.2f MB\n" % info.get("rss"))
        fobj.write("VMS (Virtual)   : %.2f MB\n" % info.get("vms"))
        fobj.write("Memory %%        : %.2f\n"   % info.get("memory_percent"))
        fobj.write(Border + "\n")
    print("Memory allocation data written to log")

    # ── Process Log (original) ────────────────────────────────────────────────
    fobj.write("\n---------------process log---------------\n")
    fobj.write(Border + "\n")
    Data = ProcessScan()
    for info in Data:
        fobj.write("pid         : %s\n" % info.get("pid"))
        fobj.write("name        : %s\n" % info.get("name"))
        fobj.write("username    : %s\n" % info.get("username"))
        fobj.write("status      : %s\n" % info.get("status"))
        fobj.write("create_time : %s\n" % info.get("create_time"))
        fobj.write("cpu %%       : %.2f\n" % info.get("cpu_percent"))
        fobj.write("mem %%       : %.2f\n" % info.get("memory_percent"))
        fobj.write(Border + "\n")

    fobj.write(Border + "\n")
    fobj.write("\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
    fobj.write(Border + "\n")
    fobj.write("-----------------End of log file-------------------\n")
    fobj.write(Border + "\n")
    fobj.close()

    # ── Feature 4 : Email Summary ─────────────────────────────────────────────
    TopCPU    = sorted(Data,        key=lambda x: x.get("cpu_percent", 0),    reverse=True)[:5]
    TopMem    = sorted(Data,        key=lambda x: x.get("memory_percent", 0), reverse=True)[:5]
    TopThread = sorted(ThreadData,  key=lambda x: x.get("thread_count", 0),   reverse=True)[:5]
    TopFiles  = [x for x in OpenFilesData if isinstance(x.get("open_files_count"), int)]
    TopFiles  = sorted(TopFiles,    key=lambda x: x.get("open_files_count", 0), reverse=True)[:5]

    SummaryText  = Border + "\n"
    SummaryText += "Marvellous Platform Surveillance Report\n"
    SummaryText += "Generated at: %s\n" % time.ctime()
    SummaryText += Border + "\n\n"
    SummaryText += "Total Processes : %d\n\n" % len(Data)

    SummaryText += "Top CPU Usage Processes:\n"
    for p in TopCPU:
        SummaryText += "  %s (PID:%s) -> CPU: %.2f%%\n" % (p.get("name"), p.get("pid"), p.get("cpu_percent", 0))

    SummaryText += "\nTop Memory Usage Processes:\n"
    for p in TopMem:
        SummaryText += "  %s (PID:%s) -> Mem: %.2f%%\n" % (p.get("name"), p.get("pid"), p.get("memory_percent", 0))

    SummaryText += "\nTop Thread Count Processes:\n"
    for p in TopThread:
        SummaryText += "  %s (PID:%s) -> Threads: %s\n" % (p.get("name"), p.get("pid"), p.get("thread_count", 0))

    SummaryText += "\nTop Open Files Processes:\n"
    for p in TopFiles:
        SummaryText += "  %s (PID:%s) -> Open Files: %s\n" % (p.get("name"), p.get("pid"), p.get("open_files_count", 0))

    SummaryText += "\n" + Border + "\n"
    SummaryText += "---------Thank you for using our script ---------\n"
    SummaryText += Border + "\n"

    print(SummaryText)
    SendEmail(ReceiverMail, FileName, SummaryText)


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():

    print(Border)
    print("-----Marvellous Platfrom Surveillance System -----")
    print(Border)

    if len(sys.argv) == 2:
        if sys.argv[1] == "--h" or sys.argv[1] == "--H":
            print("This script is used to :")
            print("1 : Create automatic logs")
            print("2 : Execute periodically")
            print("3 : Sends mail with the log")
            print("4 : Store information about process")
            print("5 : Store information about CPU")
            print("6 : Store information about RAM Usage")
            print("7 : Store information about secondary storage")
            print("8 : Store thread count for each process")
            print("9 : Store open files count for each process")
            print("10: Store RSS and VMS memory for each process")

        elif sys.argv[1] == "--u" or sys.argv[1] == "--U":
            print("Use the automation script as")
            print("PlatformSurveillance.py DirectoryName ReceiverMail TimeInterval")
            print("DirectoryName : Name of the directory to create auto logs")
            print("ReceiverMail  : Email address to send the report")
            print("TimeInterval  : Time in minutes for periodic scheduling")

        else:
            print("Unable to use as there is no such option")
            print("Use --h for help and --u for usage of the script")

    # python PlatformSurveillance.py "MarvellousLogs" "receiver@gmail.com" 10
    elif len(sys.argv) == 4:
        print("Inside projects logic")
        print("Directory name:", sys.argv[1])
        print("Receiver mail :", sys.argv[2])
        print("Time interval :", sys.argv[3])
        print(Border)

        # apply the scheduler
        schedule.every(int(sys.argv[3])).minutes.do(CreateLog, sys.argv[1], sys.argv[2])

        print("Platform surveillance system gets started with periodic scheduling")
        print("Directory created with name:", sys.argv[1])
        print("Receiver mail             :", sys.argv[2])
        print("Time interval in minutes  :", sys.argv[3])
        print("")

        while True:
            schedule.run_pending()
            time.sleep(1)

    else:
        print("Invalid no of command line arguments")
        print("Use --h for help and --u for usage of the script")

    print(Border)
    print("---------Thank you for using our script ---------")
    print(Border)


if __name__ == "__main__":
    main()
