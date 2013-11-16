from uuid import uuid4
from workflow import Workflow
from event import DecisionEvent, ActivityEvent
from activity import ActivityExecution
from decision import ScheduleActivity

class Process(object):
    def __init__(self, workflow=None, id=None, input=None, history=[], parent=None, tags=None):
        if isinstance(workflow, Workflow):
            self._workflow = workflow.__class__.name
        elif type(workflow) is type:
            self._workflow = workflow.name
        else:
            self._workflow = str(workflow)
            
        self._id = id or str(uuid4())
        self._parent = None
        self._input = input
        self._history = history
        self._tags = None
        
    @property
    def workflow(self):
        return self._workflow

    @property
    def id(self):
        return self._id

    @property
    def parent(self):
        return self._parent

    @property
    def input(self):
        return self._input

    @property
    def history(self):
        return self._history
    
    @property
    def tags(self):
        return self._tags

    def unseen_events(self):
        events = []
        for event in reversed(self.history):
            if isinstance(event, DecisionEvent):
                break
            events.insert(0, event)
        return events

    def unfinished_activities(self):
        activities = []
        for event in self.history:
            if isinstance(event, DecisionEvent) and isinstance(event.decision, ScheduleActivity):
                activities.append(ActivityExecution(event.decision.activity, event.decision.id, event.decision.input))
            elif isinstance(event, ActivityEvent) and event.activity in activities:
                activities.remove(event.activity)
        return activities

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return 'Process(%s, %s, %s, %s)' % (self.workflow, self.id, self.input, self.tags)