from src import celery
from src.models import Job, db
from src.jobs.executor import run_command_on_remote
from datetime import datetime

@celery.task(bind=True)
def execute_job(self, job_id):
    job = Job.query.get(job_id)
    if not job:
        return

    job.status = "running"
    db.session.commit()

    try:
        output = run_command_on_remote(job.command)
        job.status = "completed"
        job.output = output
    except Exception as e:
        job.status = "failed"
        job.output = str(e)

    job.completed_at = datetime.now()
    db.session.commit()
