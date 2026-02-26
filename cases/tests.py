from django.test import TestCase
from rest_framework.test import APIClient
from accounts.models import User, Role
from .models import Case, WorkflowHistory


class CaseWorkflowTest(TestCase):

    def setUp(self):
        self.complainant = User.objects.create_user(username='complainant', password='password',
                                                    national_id="complainant")
        self.cadet = User.objects.create_user(username='cadet', password='password', national_id="cadet")
        self.officer = User.objects.create_user(username='officer', password='password', national_id="officer")

        complainant_role = Role.objects.get(name="complainant")
        cadet_role = Role.objects.get(name="cadet")
        officer_role = Role.objects.get(name="police_officer")

        self.complainant.roles.add(complainant_role)
        self.cadet.roles.add(cadet_role)
        self.officer.roles.add(officer_role)

        self.cadet.reporting_to = self.officer
        self.cadet.save()

        self.case = Case.objects.create(
            title="Test Case", description="Test case description", created_by=self.complainant
        )

        self.client = APIClient()

    def become(self, username):
        self.client.logout()
        self.client.login(username=username, password='password')
        tok = self.client.post(path='/auth/login/', data={"username": username, "password": "password"})
        self.client_headers = {"Authorization": "Token " + tok.data["key"]}

    def test_send_case_to_cadet(self):
        """Test sending a case to a cadet for approval"""
        self.become("complainant")
        url = f'/cases/{self.case.id}/workflow'
        response = self.client.post(url, data={}, headers=self.client_headers)

        self.case.refresh_from_db()
        self.assertEqual(self.case.status, 'pending_approval')

        workflow_history = WorkflowHistory.objects.filter(case=self.case, recipient=self.cadet).first()
        self.assertIsNotNone(workflow_history)

    def test_send_case_to_officer(self):
        """Test sending the case from cadet to officer for approval"""
        self.case.send_to_cadet()

        url = f'/cases/{self.case.id}/workflow'
        self.become("cadet")
        response = self.client.post(url, data={"verdict": "pass"}, headers=self.client_headers)

        self.case.refresh_from_db()
        self.assertEqual(self.case.status, 'pending_verification')

        workflow_history = WorkflowHistory.objects.filter(case=self.case, recipient=self.officer).first()
        self.assertIsNotNone(workflow_history)

    def test_reject_case_to_complainant(self):
        """Test rejecting the case and sending it back to the complainant"""
        self.case.send_to_cadet()

        error_message = "Missing important info"
        url = f'/cases/{self.case.id}/workflow'
        self.become("cadet")
        response = self.client.post(url, data={"verdict": "fail", "message": error_message},
                                     headers=self.client_headers)

        self.case.refresh_from_db()
        self.assertEqual(self.case.status, 'created')

        workflow_history = WorkflowHistory.objects.filter(case=self.case, recipient=self.complainant).last()
        self.assertIsNotNone(workflow_history)
        self.assertEqual(workflow_history.message, error_message)

    def test_open_case(self):
        self.case.send_to_cadet()
        self.case.send_to_officer(self.cadet)

        url = f'/cases/{self.case.id}/workflow'
        self.become("officer")
        response = self.client.post(url, data={"verdict": "pass"}, headers=self.client_headers)

        self.case.refresh_from_db()
        self.assertEqual(self.case.status, 'open')

    def test_reject_case_to_cadet(self):
        """Test rejecting the case and sending it back to the cadet"""
        self.case.send_to_cadet()
        self.case.send_to_officer(self.cadet)

        url = f'/cases/{self.case.id}/workflow'
        error_message = "Needs more details"
        self.become("officer")
        response = self.client.post(url, data={"verdict": "fail", "message": error_message},
                                     headers=self.client_headers)

        self.case.refresh_from_db()
        self.assertEqual(self.case.status, 'pending_approval')

        workflow_history = WorkflowHistory.objects.filter(case=self.case, recipient=self.cadet).last()
        self.assertIsNotNone(workflow_history)
        self.assertEqual(workflow_history.message, error_message)

    def test_cancel_case(self):
        """Test that a case is cancelled after being rejected 3 times"""
        self.case.send_to_cadet()
        self.case.reject_case_to_creator("Rejected due to missing info")
        self.case.send_to_cadet()
        self.case.reject_case_to_creator("Rejected due to incorrect details")
        self.case.send_to_cadet()

        url = f'/cases/{self.case.id}/workflow'
        self.become("cadet")
        response = self.client.post(url, data={"verdict": "fail", "message": "Needs more details"},
                                     headers=self.client_headers)

        self.case.refresh_from_db()
        self.assertEqual(self.case.status, 'cancelled')


class CaseWorkflowByPoliceTest(TestCase):

    def setUp(self):
        self.officer = User.objects.create_user(username='officer', password='password', national_id="officer")
        self.chief = User.objects.create_user(username='chief', password='password', national_id="chief")

        officer_role = Role.objects.get(name="police_officer")
        chief_role = Role.objects.get(name="chief_police")

        self.officer.roles.add(officer_role)
        self.chief.roles.add(chief_role)

        self.officer.save()
        self.chief.save()

        self.officer.reporting_to = self.chief
        self.officer.save()

        self.client = APIClient()

    def become(self, username):
        self.client.logout()
        self.client.login(username=username, password='password')
        tok = self.client.post(path='/auth/login', data={"username": username, "password": "password"})
        self.client_headers = {"Authorization": "Token " + tok.data["key"]}

    def test_create_case_by_officer(self):
        case = Case.objects.create(
            title="Test Case", description="Test case description", created_by=self.officer
        )

        self.become("officer")
        url = f'/cases/{case.id}/workflow'
        response = self.client.post(url, data={}, headers=self.client_headers)

        case.refresh_from_db()
        self.assertEqual(case.status, 'pending_verification')

        workflow_history = WorkflowHistory.objects.filter(case=case, recipient=self.chief).first()
        self.assertIsNotNone(workflow_history)

    def test_verify_officer_case(self):
        case = Case.objects.create(
            title="Test Case", description="Test case description", created_by=self.officer
        )
        case.send_to_officer(self.officer)
        case.refresh_from_db()
        self.become("chief")

        url = f'/cases/{case.id}/workflow'
        response = self.client.post(url, data={"verdict": "pass"}, headers=self.client_headers)

        case.refresh_from_db()

        self.assertEqual(case.status, 'open')

    def test_reject_officer_case(self):
        case = Case.objects.create(
            title="Test Case", description="Test case description", created_by=self.officer
        )
        case.send_to_officer(self.officer)
        case.refresh_from_db()
        self.become("chief")

        error_message = "Not enough data"
        url = f'/cases/{case.id}/workflow'
        response = self.client.post(url, data={"verdict": "fail", "message": error_message},
                                     headers=self.client_headers)

        case.refresh_from_db()
        self.assertEqual(case.status, 'created')

        workflow_history = WorkflowHistory.objects.filter(case=case, recipient=self.officer).last()
        self.assertIsNotNone(workflow_history)
        self.assertEqual(workflow_history.message, error_message)

    def test_create_case_by_chief(self):
        case = Case.objects.create(
            title="Test Case", description="Test case description", created_by=self.chief
        )

        self.become("chief")
        url = f'/cases/{case.id}/workflow'
        response = self.client.post(url, data={}, headers=self.client_headers)

        case.refresh_from_db()
        self.assertEqual(case.status, 'open')

        workflow_history = WorkflowHistory.objects.count()
        self.assertEqual(workflow_history, 0)
