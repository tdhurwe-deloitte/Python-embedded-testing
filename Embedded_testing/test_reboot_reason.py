import requests
import responses
from responses import matchers
from responses.matchers import multipart_matcher
from responses.registries import OrderedRegistry

base_url = "https://7facbdb5-b28c-46e1-a70f-a00b44f62626.mock.io/api/v1.0/"


class TestCasesRebootReason:
    @responses.activate
    def test_reboot_reason(self):
        responses.get(
            f"{base_url}system/reboot_reason",
            json={"Reboot reason": "System failure"},
            status=200
        )
        req = requests.get(f"{base_url}system/reboot_reason")
        assert req.status_code == 200
        print(f"\n{req.json()['Reboot reason']}")

    @responses.activate
    def test_process_running(self):
        process_name = "Some_process"
        responses.get(
            f"{base_url}system/is_running/{process_name}",
            json={"Process name": process_name, "Status": "Running"},
            status=200
        )
        req = requests.get(f"{base_url}system/is_running/{process_name}")
        assert req.json()["Process name"] == process_name
        assert req.status_code == 200
        print(f"\nProcess name = {req.json()['Process name']}, status = {req.json()['Status']}")

    @responses.activate
    def test_set_trigger_pulse_time(self):
        # header_data = {"Content-type": "application/json"}
        responses.post(
            f"{base_url}g2_5mp_camera/set_trigger_pulse_time",
            match=[matchers.urlencoded_params_matcher({"sec": "1234", "nsec": "1234"})],
            json={"status": "successful"},
            status=201
        )
        req = requests.post(f"{base_url}g2_5mp_camera/set_trigger_pulse_time", data={"sec": "1234", "nsec": "1234"})
        assert req.headers == {"Content-type": "application/json"}
        assert req.json()['status'] == "successful"
        assert req.status_code == 201

    @responses.activate
    def test_set_trigger_pulse_interval(self):
        responses.post(
            f"{base_url}g2_5mp_camera/set_trigger_pulse_interval",
            match=[matchers.urlencoded_params_matcher({"sec": "1234", "nsec": "1234"})],
            json={"status": "successful"},
            status=201
        )
        req = requests.post(f"{base_url}g2_5mp_camera/set_trigger_pulse_interval", data={"sec": "1234", "nsec": "1234"})
        assert req.json()['status'] == "successful"
        assert req.status_code == 201
        assert req.headers == {"Content-type": "application/json"}

    @responses.activate
    def test_enable_trigger_pulse(self):
        responses.post(
            f"{base_url}g2_5mp_camera/enable_trigger_pulse",
            match=[matchers.urlencoded_params_matcher({"enable": "1"})],
            json={"Enabled": True},  # initially trigger pulse is disabled
            status=202
        )
        req = requests.post(f"{base_url}g2_5mp_camera/enable_trigger_pulse", data={"enable": "1"})
        assert req.json()["Enabled"] == True
        assert req.status_code == 202
        assert req.headers == {"Content-type": "application/json"}

    @responses.activate(registry=OrderedRegistry)
    def test_trigger_pulse_status(self):
        responses.get(
            f"{base_url}g2_5mp_camera/trigger_pulse_status",
            json={"Status": "Enabled"},
            status=200
        )
        responses.post(
            f"{base_url}g2_5mp_camera/trigger_pulse_status",
            body="Method not allowed",
            status=405
        )
        req = requests.get(f"{base_url}g2_5mp_camera/trigger_pulse_status")
        print(f"\n{req.json()}")
        assert req.status_code == 200

        req1 = requests.post(f"{base_url}g2_5mp_camera/trigger_pulse_status")
        print(f"\n{req1.text}")
        assert req1.text == "Method not allowed"
        assert req1.status_code == 405

    @responses.activate
    def test_stress_ng(self):
        pass

    @responses.activate
    def test_stress_ng_status(self):
        responses.get(
            f"{base_url}hardware_test/stress_ng/status",
            json={
                "api": "api/v1.0/hardware_test/stress_ng/status",
                "status": "success",
                "svc_status": {
                    "argument_string": "",
                    "is_running": False
                }
            },
            status=200
        )
        responses.post(
            f"{base_url}hardware_test/stress_ng/status",
            body="Bad request",
            status=400
        )
        req = requests.get(f"{base_url}hardware_test/stress_ng/status")
        assert req.headers == {"Content-Type": "application/json"}
        assert req.json()['api'] == "api/v1.0/hardware_test/stress_ng/status"
        assert req.status_code == 200

        req2 = requests.post(f"{base_url}hardware_test/stress_ng/status")
        assert req2.headers == {"Content-Type": "text/plain"}
        assert req2.status_code == 400
        assert req2.text == "Bad request"
