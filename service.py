import os
from threading import Thread

iostat_response = []


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
    os.system("echo none > /sys/block/sda/queue/scheduler")
    os.system("sync; echo 3 > /proc/sys/vm/drop_caches")

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
    f = open("iostat.txt")
    with f:
        lines = [line.rstrip() for line in f]
    f.close()
    processor_utility = []
    disk_utiliy = []
    bandwidth = []
    for i in range(len(lines)):
        if (7 * i + 3) < len(lines):
            # processor_utility.append((60 * i, lines[7 * i + 3].split()[0].split()[0]))
            processor_utility.append({"x": 60 * i, "y": lines[7 * i + 3].split()[0].split()[0]})
        if (7 * i + 6) < len(lines):
            disk_utiliy.append({"x": 60 * i, "y": lines[7 * i + 6].split()[-1]})
            # disk_utiliy.append((60 * i, lines[7 * i + 6].split()[-1]))
            bandwidth.append({"x": 60 * i, "y1": lines[7 * i + 6].split()[2], "y2": lines[7 * i + 6].split()[8]})
            # bandwidth.append((60 * i, lines[7 * i + 6].split()[2], lines[7 * i + 6].split()[8]))
    iostat_response = []
    iostat_response.append({"diagram": 1, "data": processor_utility})
    iostat_response.append({"diagram": 2, "data": disk_utiliy})
    iostat_response.append({"diagram": 3, "data": bandwidth})
    return iostat_response


def get_info():
    # stop monitor?
    os.system("time cat trace.txt | blkparse -i - > parsed_trace.txt")
    stop_monitor()
    # os.system("cat iostat.txt")

def stop_monitor():
    with open("1.txt") as f:
        lines = [line.rstrip() for line in f]
    for line in lines:
        os.system("kill -9 " + str(int(line) - 1))
        os.system("kill -9 " + line)
    

