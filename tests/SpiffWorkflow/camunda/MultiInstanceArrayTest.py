# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
import unittest
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'

from tests.SpiffWorkflow.camunda.BaseTestCase import BaseTestCase


class MultiInstanceArrayTest(BaseTestCase):
    """The example bpmn diagram tests both a set cardinality from user input
    as well as looping over an existing array."""

    def setUp(self):
        self.spec = self.load_workflow_spec(
            'data/multi_instance_array.bpmn',
            'MultiInstanceArray')

    def testRunThroughHappy(self):
        self.actual_test(False)

    def testRunThroughSaveRestore(self):
        self.actual_test(True)

    def actual_test(self, save_restore=False):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()

        # Set initial array size to 3 in the first user form.
        task = self.workflow.get_ready_user_tasks()[0]
        self.assertEquals("Activity_FamSize", task.task_spec.name)
        task.update_data({"FamilySize": 3})
        self.workflow.complete_task_from_id(task.id)
        if save_restore: self.save_restore()

        # Set the names of the 3 family members.
        for i in range(3):
            task = self.workflow.get_ready_user_tasks()[0]
            self.assertEquals("FamilyMemberTask", task.task_spec.name)
            task.update_data({"FirstName": "The Funk #%i" % i})
            self.workflow.complete_task_from_id(task.id)
            if save_restore: self.save_restore()

        self.assertEqual({1: {'FirstName': 'The Funk #0'},
                          2: {'FirstName': 'The Funk #1'},
                          3: {'FirstName': 'The Funk #2'}},
                         task.data["FamilyMembers"])
        # Set the birthdays of the 3 family members.
        for i in range(3):
            task = self.workflow.get_ready_user_tasks()[0]
            self.assertEquals("FamilyMemberBday", task.task_spec.name)
            task.update_data({"Birthdate": "10/0%i/1985" % i})
            self.workflow.complete_task_from_id(task.id)
#            if save_restore: self.save_restore()

        self.workflow.do_engine_steps()
        if save_restore: self.save_restore()
        self.assertTrue(self.workflow.is_completed())

        self.assertEqual({1: {'FirstName': 'The Funk #0', "Birthdate": "10/00/1985"},
                          2: {'FirstName': 'The Funk #1', "Birthdate": "10/01/1985"},
                          3: {'FirstName': 'The Funk #2', "Birthdate": "10/02/1985"}},
                         self.workflow.last_task.data["FamilyMembers"])


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(MultiInstanceArrayTest)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
