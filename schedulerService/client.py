"""
This is an example RPC client that connects to the RPyC based scheduler service.
It first connects to the RPyC server on localhost:12345.
Then it schedules a job to run on 2 second intervals and sleeps for 10 seconds.
After that, it unschedules the job and exits.
"""

from time import sleep

import rpyc

conn = rpyc.connect('localhost', 12345)
job = conn.root.add_job('server:exec_task', 'interval', args=['Hello, World'], seconds=2)
sleep(10)
job0 = conn.root.add_job('server:exec_task', 'interval', args=['world, Hello'], seconds=5)
sleep(20)
conn.root.remove_job(job.id)
conn.root.remove_job(job0.id)