from concurrent.futures import ProcessPoolExecutor, as_completed
import os
import time

def task(n):
    time.sleep(n)
    return n

if __name__ == '__main__':
    arr = [i for i in range(0, 5)]
    cpu_nums = os.cpu_count()
    
    start = time.time()

    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(task, item) for item in arr]

    result = []
    for future in as_completed(futures):
        result.append(future.result())
    print(result)
    print(time.time() - start)
