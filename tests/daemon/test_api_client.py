import json

import responses
import pytest

from flock_agent import Common
from flock_agent.daemon.global_settings import GlobalSettings
from flock_agent.daemon import api_client
from flock_agent.daemon.api_client import FlockApiClient


class TestApiClient:
    test_url = "https://example.org"

    def _build_common(self):
        common = Common(None, None)
        global_settings = GlobalSettings(common, testing=True)
        common.global_settings = global_settings
        common.global_settings.set("gateway_url", self.test_url)
        common.global_settings.set("gateway_username", "test-username")
        common.global_settings.set("gateway_token", "test-token")
        return common

    @responses.activate
    def test_ping(self):
        common = self._build_common()
        responses.add(
            responses.GET, "https://example.org/ping", status=200,
        )
        FlockApiClient(common).ping()

    @responses.activate
    def test__make_request_connection_error(self):
        common = self._build_common()
        with pytest.raises(api_client.ConnectionError):
            FlockApiClient(common)._make_request("/test", "get", False)

        with pytest.raises(api_client.ConnectionError):
            FlockApiClient(common)._make_request("/test", "post", False)

    @responses.activate
    def test__make_request_ok_with_401_response(self):
        response_data = {"error": False, "a": "test", "b": "test"}
        common = self._build_common()
        responses.add(
            responses.GET, f"{self.test_url}/test", json=response_data, status=401,
        )
        with pytest.raises(api_client.PermissionDenied):
            FlockApiClient(common)._make_request("/test", "get", False)

        common = self._build_common()
        responses.add(
            responses.POST, f"{self.test_url}/test", json=response_data, status=401,
        )
        with pytest.raises(api_client.PermissionDenied):
            FlockApiClient(common)._make_request("/test", "post", False)

    @responses.activate
    def test__make_request_ok_with_403_response(self):
        response_data = {"error": False, "a": "test", "b": "test"}
        common = self._build_common()
        responses.add(
            responses.GET, f"{self.test_url}/test", json=response_data, status=403,
        )
        with pytest.raises(api_client.BadStatusCode):
            FlockApiClient(common)._make_request("/test", "get", False)

        common = self._build_common()
        responses.add(
            responses.POST, f"{self.test_url}/test", json=response_data, status=403,
        )
        with pytest.raises(api_client.BadStatusCode):
            FlockApiClient(common)._make_request("/test", "post", False)

    @responses.activate
    def test__make_request_error_with_404(self):
        response_data = {"error": False, "a": "test", "b": "test"}
        common = self._build_common()
        responses.add(
            responses.GET, f"{self.test_url}/test", json=response_data, status=404,
        )
        with pytest.raises(api_client.BadStatusCode):
            FlockApiClient(common)._make_request("/test", "get", False)

        responses.add(
            responses.POST, f"{self.test_url}/test", json=response_data, status=404,
        )
        with pytest.raises(api_client.BadStatusCode):
            FlockApiClient(common)._make_request("/test", "get", False)

    @responses.activate
    def test__make_request_error_with_error_msg_response(self):
        response_data = {
            "error": True,
            "error_msg": "test_error_msg",
            "a": "test",
            "b": "test",
        }
        common = self._build_common()
        responses.add(
            responses.GET, f"{self.test_url}/test", json=response_data, status=200,
        )
        with pytest.raises(api_client.RespondedWithError) as excinfo:
            FlockApiClient(common)._make_request("/test", "get", False)
        responses.add(
            responses.POST, f"{self.test_url}/test", json=response_data, status=200,
        )
        with pytest.raises(api_client.RespondedWithError) as excinfo:
            FlockApiClient(common)._make_request("/test", "post", False)

        assert "test_error_msg" in str(excinfo)

    @responses.activate
    def test__make_request_error_without_error_msg_response(self):
        response_data = {
            "error": True,
            "a": "test",
            "b": "test",
        }
        common = self._build_common()
        responses.add(
            responses.GET, f"{self.test_url}/test", json=response_data, status=200,
        )
        with pytest.raises(api_client.InvalidResponse) as excinfo:
            FlockApiClient(common)._make_request("/test", "get", False)
        responses.add(
            responses.POST, f"{self.test_url}/test", json=response_data, status=200,
        )
        with pytest.raises(api_client.InvalidResponse) as excinfo:
            FlockApiClient(common)._make_request("/test", "post", False)

    @responses.activate
    def test__make_request_good_json_no_error_key_in_response(self):
        common = self._build_common()
        responses.add(
            responses.GET,
            f"{self.test_url}/test",
            json={"a": "test", "b": "test"},
            status=200,
        )
        with pytest.raises(api_client.InvalidResponse):
            FlockApiClient(common)._make_request("/test", "get", False)
        responses.add(
            responses.POST,
            f"{self.test_url}/test",
            json={"a": "test", "b": "test"},
            status=200,
        )
        with pytest.raises(api_client.InvalidResponse):
            FlockApiClient(common)._make_request("/test", "post", False)

    @responses.activate
    def test__make_request_ok_with_bad_json_response(self):
        common = self._build_common()
        responses.add(
            responses.GET, f"{self.test_url}/test", body="I'm not json", status=200,
        )
        with pytest.raises(api_client.ResponseIsNotJson):
            FlockApiClient(common)._make_request("/test", "get", False)
        responses.add(
            responses.POST, f"{self.test_url}/test", body="I'm not json", status=200,
        )
        with pytest.raises(api_client.ResponseIsNotJson):
            FlockApiClient(common)._make_request("/test", "post", False)

    @responses.activate
    def test__make_request_ok_with_good_json(self):
        common = self._build_common()
        response_data = {"error": False, "a": "test", "b": "test"}
        responses.add(
            responses.GET, f"{self.test_url}/test", json=response_data, status=200,
        )
        assert (
            FlockApiClient(common)._make_request("/test", "get", False) == response_data
        )
        responses.add(
            responses.POST, f"{self.test_url}/test", json=response_data, status=200,
        )
        assert (
            FlockApiClient(common)._make_request("/test", "post", False)
            == response_data
        )

    @responses.activate
    def test__make_request_ok_with_auth(self):
        common = self._build_common()
        response_data = {"error": False, "a": "test", "b": "test"}

        def request_callback(request):
            assert "Authorization" in request.headers
            assert (
                request.headers["Authorization"]
                == "Basic dGVzdC11c2VybmFtZTp0ZXN0LXRva2Vu"
            )
            return 200, {}, json.dumps(response_data)

        responses.add_callback(
            responses.GET, f"{self.test_url}/test", callback=request_callback,
        )
        assert (
            FlockApiClient(common)._make_request("/test", "get", True) == response_data
        )
        responses.add_callback(
            responses.POST, f"{self.test_url}/test", callback=request_callback,
        )
        assert (
            FlockApiClient(common)._make_request("/test", "post", True) == response_data
        )

    @responses.activate
    def test__make_request_ok_with_data(self):
        common = self._build_common()
        request_data = {"test_key": "test_response", "test_key2": False}
        response_data = {"error": False, "a": "test", "b": "test"}

        def request_callback(request):
            assert json.loads(request.body) == request_data
            return 200, {}, json.dumps(response_data)

        responses.add_callback(
            responses.GET, f"{self.test_url}/test", callback=request_callback,
        )
        assert (
            FlockApiClient(common)._make_request(
                "/test", "get", False, data=request_data
            )
            == response_data
        )
        responses.add_callback(
            responses.POST, f"{self.test_url}/test", callback=request_callback,
        )
        assert (
            FlockApiClient(common)._make_request(
                "/test", "post", True, data=request_data
            )
            == response_data
        )

    def test__get_headers_no_auth(self):
        common = self._build_common()
        assert FlockApiClient(common)._get_headers(auth=False) == {
            "User-Agent": f"Flock Agent {common.version}"
        }

    def test__get_headers_yes_auth(self):
        common = self._build_common()
        assert FlockApiClient(common)._get_headers(auth=True) == {
            "User-Agent": f"Flock Agent {common.version}",
            "Authorization": "Basic dGVzdC11c2VybmFtZTp0ZXN0LXRva2Vu",
        }

    def test__build_url_with_trailing_slash(self):
        common = self._build_common()
        common.global_settings.set("gateway_url", "https://example.org/")
        assert (
            FlockApiClient(common)._build_url("/api/test")
            == "https://example.org/api/test"
        )

    def test__build_url_without_trailing_slash(self):
        common = self._build_common()
        assert (
            FlockApiClient(common)._build_url("/api/test")
            == "https://example.org/api/test"
        )
