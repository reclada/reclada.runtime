from stage.stage import Stage


class DummyPlatform(Stage):

    def create_stage(self, type_of_stage):
        print(f'Platform {type_of_stage} was created.')
        return "platform_1"

    def create_runner(self, ref_to_platform, runner_id, db_type):
        print(f'The runner on the platform {ref_to_platform} was started.')
        return True

    def get_idle_runner(self, ref_to_platform):
        print(f'There are no idle runners on the specified platform {ref_to_platform}')
        return 0

    def get_job_status(self, job_id):
        print(f'The job with id:{job_id} is still running.')
        return False

    def is_stage_active(self, type_of_platform):
        print(f'The specified platform {type_of_platform} is active')

    def run_job(self, runner_id, reclada_job):
        print(f'The job has not been finished yet.')
        return 1

