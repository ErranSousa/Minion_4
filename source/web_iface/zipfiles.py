from zipfile import ZipFile
import os
import time


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


data_dir = "/home/pi/Desktop/minion_data/"
pics_dir = "/home/pi/Desktop/minion_pics/"
conf = "/home/pi/Desktop/Minion_config.ini"

endmessage = "Files Compressed!"

data_paths = get_all_files(data_dir)
pics_paths = get_all_files(pics_dir)

paths = data_paths + pics_paths

paths.append(conf)

clear_log()

with ZipFile('MinionXXX.zip', 'w') as archive:
    for file in paths:
        filename = file.replace('/home/pi/Desktop', '')
        archive.write(file, filename)
        with open('/var/www/html/livefeed.txt', 'a+') as output:
            output.write(file)
            output.write('<br><br>')

with open('/var/www/html/livefeed.txt', 'w') as output:
    output.write(endmessage)
    output.write("<br><br>")

time.sleep(10)

clear_log()
