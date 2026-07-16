Developed a Python-based automation script to detect and delete duplicate files from a directory 
periodically. The system automatically generates log files of operations performed and shares them via email 
for audit purposes.  
• Implemented checksum-based duplicate detection using hashlib (MD5).  
• Automated log generation with timestamps for every execution.  
• Used schedule library for periodic execution of duplicate file cleanup.

Duplicate File Cleaner

Python automation tool to detect and remove duplicate files using MD5 hashing.

Features

Detects duplicate files
Removes duplicate copies
Generates log reports
Displays execution time
Tech Stack

Python
hashlib
os
sys
How To Run

python main.py Demo

Example

The script scans the "Demo" folder, detects duplicate files, removes duplicates, and stores logs in "Log.txt".
