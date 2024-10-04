# see the time taken to save a file

import time
import threading

file_lock = threading.Lock()

msg = 'Hello, World! \n'


# use high definition time
start = time.perf_counter()
f = open('test.txt', 'r+')

# read all the lines from the start then print the msg a the end
for line in f:
    if '[3434.3]' in line:
        pass

f.write(msg)
f.flush()
print('File saved successfully')
end = time.perf_counter()
f.close()

print('Time taken to save a file:', end- start,'ns')
