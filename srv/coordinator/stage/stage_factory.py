from srv.coordinator.stage.dummy_platform import DummyPlatform
from srv.coordinator.stage.domino_platform import DominoPlatform
from srv.coordinator.stage.k8s_platform import K8sPlatform

class StageFactory:
    """
        This class creates an execution platform for the given type
    """
    def __init__(self):
        self._stages = {}

    def stage_register(self, stage_type, stage):
        """
            This method registers the given type of the execution platform
        :param stage_type: type of the platform
        :param stage: the execution platform
        """
        self._stages[stage_type] = stage

    def get_stage(self, stage_type):
        """
            This method returns the execution platform by the given type
        :param stage_type: type of the execution platform
        :return: the execution platform
        """
        stage = self._stages.get(stage_type)
        if not stage:
            raise ValueError(stage_type)
        return stage()

stage = StageFactory()
stage.stage_register('DUMMY', DummyPlatform)
stage.stage_register('shell', DummyPlatform)
stage.stage_register('DOMINO', DominoPlatform)
stage.stage_register('K8S', K8sPlatform)
