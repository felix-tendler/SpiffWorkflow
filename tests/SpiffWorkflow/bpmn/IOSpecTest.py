from SpiffWorkflow.bpmn.exceptions import WorkflowDataException
from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow


from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase


class CallActivityDataTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec, self.subprocesses = self.load_workflow_spec('io_spec*.bpmn', 'parent')

    def testCallActivityWithIOSpec(self):
        self.actual_test()

    def testCallActivityWithIOSpecSaveRestore(self):
        self.actual_test(True)

    def testCallActivityMissingInput(self):

        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        set_data = self.workflow.spec.task_specs['Activity_0haob58']
        set_data.script = """in_1, unused = 1, True"""

        with self.assertRaises(WorkflowDataException) as exc:
            self.advance_to_subprocess()
        self.assertEqual("'in_2' was not found in the task data. "
                         "You are missing a required Data Input for a call activity.",
                         str(exc.exception))
        self.assertEqual(exc.exception.data_input.name,'in_2')

    def testCallActivityMissingOutput(self):

        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        script_task = self.workflow.spec.task_specs['Activity_0haob58']
        script_task.script = """in_1, in_2, unused = 1, "hello world", True"""

        self.advance_to_subprocess()
        task = self.workflow.get_tasks(TaskState.READY)[0]
        transform_task = task.workflow.spec.task_specs['Activity_04d94ee']
        transform_task.script = """out_1, unused = in_1 * 2, False"""

        with self.assertRaises(WorkflowDataException) as exc:
            self.complete_subprocess()

        self.assertEqual("'out_2' was not found in the task data. A Data Output was not provided as promised.",
                         str(exc.exception))
        self.assertEqual(exc.exception.data_output.name,'out_2')

    def actual_test(self, save_restore=False):

        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        set_data = self.workflow.spec.task_specs['Activity_0haob58']
        set_data.script = """in_1, in_2, unused = 1, "hello world", True"""

        if save_restore:
            self.save_restore()

        self.advance_to_subprocess()
        # This will be the first task of the subprocess
        task = self.workflow.get_tasks(TaskState.READY)[0]

        # These should be copied
        self.assertIn('in_1', task.data)
        self.assertIn('in_2', task.data)
        # This should not
        self.assertNotIn('unused', task.data)

        self.complete_subprocess()
        task = self.workflow.get_tasks(TaskState.READY)[0]
        # Originals should not change
        self.assertEqual(task.data['in_1'], 1)
        self.assertEqual(task.data['in_2'], "hello world")
        self.assertEqual(task.data['unused'], True)
        # New variables should be present
        self.assertEqual(task.data['out_1'], 2)
        self.assertEqual(task.data['out_2'], "HELLO WORLD")

    def advance_to_subprocess(self):
        # Once we enter the subworkflow it becomes a waiting task
        waiting = self.workflow.get_tasks(TaskState.WAITING)
        while len(waiting) == 0:
            next_task = self.workflow.get_tasks(TaskState.READY)[0]
            next_task.complete()
            waiting = self.workflow.get_tasks(TaskState.WAITING)

    def complete_subprocess(self):
        # When we complete, the subworkflow task will move from WAITING to READY
        waiting = self.workflow.get_tasks(TaskState.WAITING)
        while len(waiting) > 0:
            next_task = self.workflow.get_tasks(TaskState.READY)[0]
            next_task.complete()
            waiting = self.workflow.get_tasks(TaskState.WAITING)
