import os
from threading import Thread
from time import time
from datetime import datetime
from numpy import Inf
from tomlkit import date

iostat_response = []

start_time = 0.0
start_date_time = ""
dif_time = []
date_time = []

count = 0

def execute_requirements(file):
    # os.system("source ~/.bashrc")
    for line in file.file.readlines():
        os.system(line)

def monitor_iostat():
    os.system("time iostat -mx sda 60 > iostat.txt&")

def monitor_blktrace():
    os.system("time blktrace -d /dev/sda -a complete -o - > trace.txt&")

t1 = Thread(target=monitor_iostat)
t2 = Thread(target=monitor_blktrace)

def start_monitor(url, dataset_name):
    global start_time, count, start_date_time, date_time
    os.system("echo none > /sys/block/sda/queue/scheduler")
    os.system("sync; echo 3 > /proc/sys/vm/drop_caches")

    stop_monitor()
    start_time = time()
    start_date_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    count = 0

    date_time.append(start_date_time)

    t1.start()
    t2.start()

    os.system("pidof iostat > 1.txt")
    os.system("pidof blktrace >> 1.txt")

    folder = url.split("/")[-1]
    if folder == "vehicle-speed-check":
        os.system("git clone " + url)
        os.system("cd vehicle-speed-check & python -m venv venv & ./venv/bin/activate")
        os.system("pip install -r vehicle-speed-check/requirements.txt")
        os.system("python vehicle-speed-check/speed_check.py")
    
    elif folder == "ImageStitching":
        os.system("git clone " + url)
        os.system("pip install -r ImageStitching/requirements.txt")
        os.system("python3 ImageStitching/stitching.py " + dataset_name + " --display --save")
    
    elif folder == "resnet50-tensorflow":
        os.system("git clone " + url)

    elif folder == "object-detection-opencv":
        os.system("git clone " + url)
        os.system("pip install numpy opencv-python")
        os.system("wget https://pjreddie.com/media/files/yolov3.weights")
        os.system("python yolo_opencv.py --image dog.jpg --config yolov3.cfg " + 
        "--weights yolov3.weights --classes yolov3.txt")
    
    elif folder == "retinaface":
        os.system("git clone " + url)
        os.system("pip install retina-face")
    
    elif folder == "face-detection":
        os.system("git clone " + url)
        os.system("pip install git+https://github.com/elliottzheng/face-detection.git@master")
    
def iostat_info():
    global dif_time, start_time
    f = open("iostat.txt")
    with f:
        lines = [line.rstrip() for line in f]
    f.close()
    processor_utility = []
    disk_utiliy = []
    bandwidth = []
    disk_width = []

    dif_time.append(time() - start_time)

    for i in range(len(lines)):
        if (7 * i + 3) < len(lines):
            # processor_utility.append((60 * i, lines[7 * i + 3].split()[0].split()[0]))
            processor_utility.append({"time": f'{dif_time[i]:0.2f}', "% CPU": float(lines[7 * i + 3].split()[0].split()[0])})
        if (7 * i + 6) < len(lines):
            disk_utiliy.append({"time": f'{dif_time[i]:0.2f}', "% Disk": float(lines[7 * i + 6].split()[-1])})
            # disk_utiliy.append((60 * i, lines[7 * i + 6].split()[-1]))
            bandwidth.append({"time": f'{dif_time[i]:0.2f}', "Read (MB/s)": float(lines[7 * i + 6].split()[2]), "Write (MB/s)": float(lines[7 * i + 6].split()[8])})
            # bandwidth.append((60 * i, lines[7 * i + 6].split()[2], lines[7 * i + 6].split()[8]))
            disk_width.append({"time": f'{dif_time[i]:0.2f}', "Read (MB/s)": float(lines[7 * i + 6].split()[2]), "Write (MB/s)": float(lines[7 * i + 6].split()[8]), "% Disk": float(lines[7 * i + 6].split()[-1])})
            
    iostat_response = []
    iostat_response.append({"diagram": "Processor Utility", "data": processor_utility})
    iostat_response.append({"diagram": "Disk Utiliy", "data": disk_utiliy})
    iostat_response.append({"diagram": "Bandwidth", "data": bandwidth})
    iostat_response.append({"diagram": "Disk Utiliy vs Bandwidth", "data": disk_width})
    return iostat_response


def blktrace_info():
    global count, start_date_time, date_time
    os.system("time cat trace.txt | blkparse -i - > parsed_trace.txt")
    count += 1
    if count == 20:
        stop_monitor()
    f = open("parsed_trace.txt")
    with f:
        lines = [line.rstrip() for line in f]
    f.close()

    if len(lines) == 0:
        return

    end_date_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    date_time.append(end_date_time)

    # Read/Write count - Read/Write distribution
    read_sectors = 0
    write_sectors = 0
    min_read = Inf
    min_write = Inf
    max_read = 0
    max_write = 0
    read_count = 0
    write_count = 0
    read = {"1-4": 0, "5-8": 0, "9-12": 0, "13-16": 0, "17-20": 0, "21-24": 0, "25-48": 0, \
    "49-64": 0, "65-128": 0, ">128": 0}
    write = {"1-4": 0, "5-8": 0, "9-12": 0, "13-16": 0, "17-20": 0, "21-24": 0, "25-48": 0, \
    "49-64": 0, "65-128": 0, ">128": 0}
    blktrace_output = []

    frequency = {}

    read_count_interval = [0 for i in range(20)]
    write_count_interval = [0 for i in range(20)]

    for i in range(len(lines) - 12):
        line = lines[i].split()
        if (len(line) < 7):
            break
        if line[6].startswith("R"):
            read_count_interval[int(float(line[3]) / 60)] += 1
        elif line[6].startswith("W"):
            write_count_interval[int(float(line[3]) / 60)] += 1
        
        if line[-3] == "+":

            for j in range(int(line[-2])):
                if not frequency.__contains__(str(int(line[-4]) + j)):
                    frequency.update({str(int(line[-4]) + j): 1})
                else:
                    frequency.update({str(int(line[-4]) + j): frequency[str(int(line[-4]) + j)] + 1})

            if line[6].startswith("R"):
                read_count += 1
                read_sectors += int(line[-2])

                if int(line[-2]) / 8 * 4 < min_read:
                    min_read = int(line[-2]) / 8 * 4
                if int(line[-2]) / 8 * 4 > max_read:
                    max_read = int(line[-2]) / 8 * 4

                if (int(line[-2]) / 8 * 4) <= 4:
                    read["1-4"] += 1 
                elif (int(line[-2]) / 8 * 4) <= 8:
                    read["5-8"] += 1
                elif (int(line[-2]) / 8 * 4) <= 12:
                    read["9-12"] += 1
                elif (int(line[-2]) / 8 * 4) <= 16:
                    read["13-16"] += 1
                elif (int(line[-2]) / 8 * 4) <= 20:
                    read["17-20"] += 1
                elif (int(line[-2]) / 8 * 4) <= 24:
                    read["21-24"] += 1
                elif (int(line[-2]) / 8 * 4) <= 48:
                    read["25-48"] += 1
                elif (int(line[-2]) / 8 * 4) <= 64:
                    read["49-64"] += 1
                elif (int(line[-2]) / 8 * 4) <= 128:
                    read["65-128"] += 1
                else:
                    read[">128"] += 1
            elif line[6].startswith("W"):
                write_count += 1
                write_sectors += int(line[-2])

                if int(line[-2]) / 8 * 4 < min_write:
                    min_write = int(line[-2])  / 8 * 4
                if int(line[-2]) / 8 * 4 > max_write:
                    max_write = int(line[-2])  / 8 * 4

                if (int(line[-2]) / 8 * 4) <= 4:
                    write["1-4"] += 1 
                elif (int(line[-2]) / 8 * 4) <= 8:
                    write["5-8"] += 1
                elif (int(line[-2]) / 8 * 4) <= 12:
                    write["9-12"] += 1
                elif (int(line[-2]) / 8 * 4) <= 16:
                    write["13-16"] += 1
                elif (int(line[-2]) / 8 * 4) <= 20:
                    write["17-20"] += 1
                elif (int(line[-2]) / 8 * 4) <= 24:
                    write["21-24"] += 1
                elif (int(line[-2]) / 8 * 4) <= 48:
                    write["25-48"] += 1
                elif (int(line[-2]) / 8 * 4) <= 64:
                    write["49-64"] += 1
                elif (int(line[-2]) / 8 * 4) <= 128:
                    write["65-128"] += 1
                else:
                    write[">128"] += 1

    sum_read = read_sectors / 8 * 4
    sum_write = write_sectors / 8 * 4

    # Read/Write-Intensive
    rw_intensive = []
    for i in range(len(read_count_interval)):
        if read_count_interval[i] != 0 and read_count_interval[i] < write_count_interval[i]:
            rw_intensive.append({"Start Time": date_time[i], "End Time": date_time[i + 1], "Data": "Write"})
        elif read_count_interval[i] != 0 and read_count_interval[i] > write_count_interval[i]:
            rw_intensive.append({"Start Time": date_time[i], "End Time": date_time[i + 1], "Data": "Read"})
        elif read_count_interval[i] != 0:
            rw_intensive.append({"Start Time": date_time[i], "End Time": date_time[i + 1], "Data": "Read/Write"})
    
    start_date_time = end_date_time

    # requset frequency
    res = {"1-2": 0,"3-4": 0,"5-6": 0,"7-8": 0,"9-10": 0,"11-12": 0,">12": 0}
    res["1-2"] = sum(x == 1 or x == 2 for x in frequency.values())
    res["3-4"] = sum(x == 3 or x == 4 for x in frequency.values())
    res["5-6"] = sum(x == 5 or x == 6 for x in frequency.values())
    res["7-8"] = sum(x == 7 or x == 8 for x in frequency.values())
    res["9-10"] = sum(x == 9 or x == 10 for x in frequency.values())
    res["11-12"] = sum(x == 11 or x == 12 for x in frequency.values())
    res[">12"] = sum(x > 12 for x in frequency.values())

    blktrace_output.append({"diagram": "Read/Write", "data": {"Read": read_sectors, "Write": write_sectors}})
    blktrace_output.append({"diagram": "Distribution of I/O Sizes", "data": {"data":{"Read": read, "Write": write},
    "analysis": {"Min": {"Read": min_read, "Write": min_write}, "Max": {"Read": max_read, "Write": max_write}, "Avg": {"Read": sum_read / read_count, "Write": sum_write / write_count}}}})
    blktrace_output.append({"diagram": "Read/Write-Intensive", "data": rw_intensive})
    blktrace_output.append({"diagram": "Access Frequency Distribution (Total R/W)", "data": res})
    return blktrace_output
    # return read_count
    # os.system("cat iostat.txt")

def stop_monitor():
    with open("1.txt") as f:
        lines = [line.rstrip() for line in f]
    for line in lines:
        os.system("kill -15 " + str(int(line) - 1))
        os.system("kill -15 " + line)
    

