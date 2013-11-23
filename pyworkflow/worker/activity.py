import traceback
from uuid import uuid4
from ..activity import ActivityCompleted, ActivityAborted, ActivityFailed, ActivityMonitor

class ActivityWorker(object):
    """
    Executes activities provided by the WorkflowManager
    """

    def __init__(self, manager, name=None):
        self.manager = manager
        self.name = name or str(uuid4())

    def monitor_for_task(self, task):
        heartbeat_fn = lambda: self.manager.heartbeat(task)
        return ActivityMonitor(heartbeat_fn)

    def execute_activity(self, activity):
        try:
            result = activity.execute()
            return ActivityCompleted(result)
        except ActivityAborted, a:
            return a
        except ActivityFailed, f:
            return f
        except Exception, e:
            return ActivityFailed(str(e), traceback.format_exc())

    def log_result(self, task, result, logger):
        if isinstance(result, ActivityCompleted):
            logger.info("Worker %s: Completed %s: %s" % (self.name, task, result))
        elif isinstance(result, ActivityAborted):
            logger.info("Worker %s: Aborted %s: %s" % (self.name, task, result))
        elif isinstance(result, ActivityFailed):
            logger.warning("Worker %s: Failed %s: %s" % (self.name, task, result))

    def step(self, logger=None):
        # Rely on the backend poll to be blocking
        task = self.manager.next_activity(identity=self.name)
        if task:
            if logger:
                logger.info("Worker %s: Starting %s" % (self.name, task))

            activity = self.manager.activity_for_task(task, monitor=self.monitor_for_task(task))
            result = self.execute_activity(activity)

            if logger:
                self.log_result(task, result, logger)

            self.manager.complete_task(task, result)

    def __repr__(self):
        return 'ActivityWorker(%s, %s)' % (self.manager, self.name)