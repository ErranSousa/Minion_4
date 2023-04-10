from zipfile import ZipFile
import os
import time
import sys

data = sys.argv[1]

if data:
    exit(0)

path = '/home/pi/Desktop/minion_memory/{}'.format(data)


def get_all_files(directory):

    file_paths = []

    for root, directories, files in os.walk(directory):
        for fname in files:
            filepath = os.path.join(root, fname)
            file_paths.append(filepath)

    return file_paths


def clear_log():
    with open('/var/www/html/livefeed.txt', 'w') as output_file:
        output_file.write('')


end_message = "Files Compressed!"

clear_log()

zip_name = "/var/www/html/MXXX-{}.zip".format(data)

paths = get_all_files(path)

with ZipFile(zip_name, 'w') as archive:
    for file in paths:
        filename = file.replace('/home/pi/Desktop/minion_memory', '')
        archive.write(file, filename)
        with open('/var/www/html/livefeed.txt', 'a+') as output:
            output.write(file)
            output.write('<br><br>')
            output.close()

with open('/var/www/html/livefeed.txt', 'w') as output:
    output.write(end_message)
    output.write("<br><br>")

time.sleep(10)

clear_log()
