import multiprocessing
import os
import time

def task(n):
    time.sleep(n)
    return n

if __name__ == '__main__':
    arr = [i for i in range(0, 5)]
    cpu_nums = os.cpu_count()
    
    start = time.time()

    process_pool = multiprocessing.Pool(processes=1)
    result = process_pool.map(task, arr)
    process_pool.close()
    process_pool.join()
    print(result)
    print(time.time() - start)
