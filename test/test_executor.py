import os
import time
import pytest
from src import db, start
from src.job_executor import JobExecutor, LOG_DIR
from src.models import Job

@pytest.fixture(scope="function")
def app_context():
    app = start()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()

@pytest.fixture
def executor():
    return JobExecutor()

def test_executor_runs_successful_job(app_context, executor):
    job = Job(command="echo Hello World", user_id=1)
    db.session.add(job)
    db.session.commit()

    executor.submit(job.id, job.command)

    # updated_job = Job.query.get(job.id)

    updated_job = wait_for_job_completion(job.id)
    assert updated_job.status == "completed"
    assert updated_job.exit_code == 0
    assert updated_job.log_path is not None
    assert os.path.exists(updated_job.log_path)

    with open(updated_job.log_path) as f:
        assert "Hello World" in f.read()

# this is to make sure the tests arent run before the job is finished
def wait_for_job_completion(job_id, timeout=5):
    start_time = time.time()
    while time.time() - start_time < timeout:
        job = Job.query.get(job_id)
        if job.status not in ("submitted", "running"):
            return job
        time.sleep(0.1)
    raise TimeoutError("Job did not complete in time")

def test_executor_handles_failed_command(app_context, executor):
    job = Job(command="false", user_id=1)  # `false` exits with code 1
    db.session.add(job)
    db.session.commit()

    executor.submit(job.id, job.command)

    # updated_job = Job.query.get(job.id)
    updated_job = wait_for_job_completion(job.id)

    assert updated_job.status == "failed"
    assert updated_job.exit_code != 0
    assert os.path.exists(updated_job.log_path)

def test_executor_creates_log_file_even_on_error(app_context, executor):
    job = Job(command="nonexistentcommand", user_id=1)
    db.session.add(job)
    db.session.commit()

    executor.submit(job.id, job.command)

    # updated_job = Job.query.get(job.id)
    updated_job = wait_for_job_completion(job.id)

    assert updated_job.status == "failed"
    assert updated_job.exit_code != 0
    assert os.path.exists(updated_job.log_path)

    with open(updated_job.log_path) as f:
        content = f.read()
        assert "not found" in content or "No such file" in content
