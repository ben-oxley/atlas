
from atlas.collect import SENTINEL_ZOOM_TILE_LEVEL, check_jobs, tile_image_and_store
from atlas.db import AtlasDBFacade
from atlas.models.jobs import JobStatus, JobType


def run():
    while True:
        check_jobs()



def check_jobs():
    dbcontext = AtlasDBFacade()
    dbcontext.connect()
    job = dbcontext.peek_job()
    job_type = job[1]

    if not job is None:
        match job_type:
            case JobType.TILE:
                run_tile_job(job)
                
def run_tile_job(job):
    dbcontext = AtlasDBFacade()

    dbcontext.connect()
    dbcontext.update_job(job[0],JobType.TILE,JobStatus.RUNNING,JobStatus.NOT_STARTED)
    job_details = dbcontext.get_job(job[0])
    jobparams = job_details[2]
    tile_image_and_store(jobparams["id"],jobparams["source_db_id"],jobparams["href"],SENTINEL_ZOOM_TILE_LEVEL,jobparams["props"]["datetime"])
    dbcontext.update_job(job[0],JobType.TILE,JobStatus.COMPLETE,JobStatus.RUNNING)