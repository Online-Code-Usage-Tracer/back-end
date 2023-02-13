# back-end
It was our project in the OS course at Sharif University of Technology in the fall of 2022. It traces consumable resources such as CPU and disk and traces those resources using Iostat and Blktrace in Linux.

---
## APIs
- ***start***: It gets the code URL and dataset name. Then it started the monitoring process.
- ***monitor/iostat***: It gets needed data to show iostat related charts. Iostat related charts are:
  - Processor Utility
  - Disk Utility
  - Disk Bandwidth
  - Disk Utility vs Disk Bandwidth
- ***monitor/blktrace***: It gets needed data to show blktrace related charts. Blktrace related charts are:
  - Disk Read/Write
  - Distribution of I/O Sizes
  - Access Frequency Distribution (Total R/W)
  - Read/Write Intensive
