from abc import ABC, abstractmethod

class Stage(ABC):
    """
        Staging class defines the main functionality that has to be implemented for different stages
        in order to be used by Coordinator
    """
    @abstractmethod
    def create_stage(self, type_of_stage):
        """
            This method creates the needed platform in different execution environments
        :param type_of_stage: specified the type of platform that has to be created
        :return: reference to the created platform or error code
        """
        pass

    @abstractmethod
    def is_stage_active(self, type_of_stage):
        """
            This method checks if the needed platform is active
        :param type_of_platfrom:
        :return: false - the platform is down
                 true - the platform is up
        """
        pass

    @abstractmethod
    def create_runner(self, ref_to_stage, runner_id, db_type):
        """
            This method starts a runner on the specified platform
        :param ref_to_stage: reference to software platform
        :param runner_id: id of the runner taken from DB
        :param db_type: type of the database
        :return: True - if the runner creation ends successfully
        """
        pass

    @abstractmethod
    def get_idle_runner(self, ref_to_stage):
        """
            This method returns the idle runner in the specified platform
        :param ref_to_platform:
        :return: runner_id - the id of the idle runner or 0
        """
        pass


    @abstractmethod
    def get_job_status(self, job_id):
        """
            This method returns the status of the specified job
        :param job_id:
        :return: false - if job is still running
                 true - if job is finished
        """
        pass

