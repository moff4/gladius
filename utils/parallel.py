import time
from multiprocessing import Process, Queue
from typing import List, Callable


async def parallel_run(itr: List, handler: Callable, worker: Callable, proc_num: int):
    async def read(q):
        x = 0
        while not q.empty():
            res = q.get()
            x += 1
            await handler(res)
        return x

    def check_procs(az):
        bz = []
        for p in az:
            if p.is_alive():
                bz.append(p)
            else:
                p.join()
        return bz

    len_ = len(itr)
    itr += [None] * proc_num
    proc_num = min(proc_num, len_)
    q_in, q_out = Queue(), Queue()
    for i in range(proc_num):
        q_in.put(itr.pop(0))

    procs = [
        (p := Process(target=worker, args=(q_in, q_out))).start() or p
        for _ in range(proc_num)
    ]

    done = 0
    while done < len_ and procs:
        done += await read(q_out)
        i = 0
        while itr and i < 20:
            q_in.put(itr.pop(0))
            i += 1
        time.sleep(0.001)
        procs = check_procs(procs)
    for p in procs:
        p.join()
    await read(q_out)
