import threading
import subprocess
import os
import time
from queue import Queue
from datetime import datetime, timezone
from . import db
from models import Job

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

class JobRunner(threading.Thread):
    def __init__(self, job_id, command):
        super().__init__()
        self.job_id = job_id
        self.command = command

    def run(self):
        log_path = os.path.join(LOG_DIR, f"job_{self.job_id}.log")
        job = Job.query.get(self.job_id)
        job.status = "running"
        job.log_path = log_path
        db.session.commit()

        try:
            with open(log_path, "w") as log_file:
                process = subprocess.Popen(
                    self.command, shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
                for line in process.stdout:
                    log_file.write(line)
                    log_file.flush()
                process.wait()
                exit_code = process.returncode
        except Exception as e:
            job.status = "failed"
            job.exit_code = -1
            job.output = str(e)
        else:
            job.status = "completed" if exit_code == 0 else "failed"
            job.exit_code = exit_code

        job.completed_at = datetime.now(timezone.utc)
        db.session.commit()


class JobExecutor:
    def __init__(self):
        self.queue = Queue()
        self.worker_thread = threading.Thread(target=self.worker_loop, daemon=True)
        self.worker_thread.start()

    def worker_loop(self):
        while True:
            job_id, command = self.queue.get()
            runner = JobRunner(job_id, command)
            runner.start()

    def submit(self, job_id, command):
        self.queue.put((job_id, command))
