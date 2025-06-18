import os
import pytest
import json
import time
import requests
import threading

from test_simple_base import TestSimpleBase


# @pytest.mark.skip(reason="Skipping API tests")
@pytest.mark.usefixtures("prepare_databases")
class TestAPI(TestSimpleBase):
    @pytest.fixture(scope="class", autouse=True)
    def setup_ace_daemon(self, ace_daemon):
        # Start ACE daemon in a background thread
        daemon_thread = threading.Thread(target=ace_daemon.start_ace)
        daemon_thread.daemon = True  # Set as daemon so it exits when main thread exits
        daemon_thread.start()
        time.sleep(2)

    def _get_api_base_url(self):
        return "https://localhost:5000/ace"

    def _get_cert_config(self, ace_conf):
        # Return the full certificate configuration needed for client auth
        # Skip server certificate verification (equivalent to curl's -k flag)
        return {
            "cert": (ace_conf.ACE_USER_CERT_FILE, ace_conf.ACE_USER_KEY_FILE),
            "verify": False,
        }

    def test_database_connectivity(self, ace_conf, nodes):
        """Test API server connectivity"""
        try:
            cert_config = self._get_cert_config(ace_conf)
            response = requests.get(
                f"{self._get_api_base_url()}/task-status",
                params={"task_id": "test"},
                **cert_config,
            )
            # Even if task doesn't exist, server should respond
            assert response.status_code in [200, 404]
        except Exception as e:
            pytest.fail(f"Failed to connect to API server: {str(e)}")

    @pytest.mark.parametrize("table_name", ["public.customers"])
    def test_simple_table_diff(self, cli, capsys, ace_conf, table_name):
        """Test table diff API on cluster eqn-t9da for specified table"""
        try:
            # Prepare the request payload
            payload = {
                "cluster_name": "eqn-t9da",
                "table_name": table_name,
                "dbname": "demo",
                "block_size": 10000,
                "max_cpu_ratio": 0.6,
                "output": "json",
                "nodes": "all",
                "batch_size": 1,
                "quiet": True,
            }

            # Get certificate configuration
            cert_config = self._get_cert_config(ace_conf)

            # Make the API request
            response = requests.post(
                f"{self._get_api_base_url()}/table-diff",
                json=payload,
                **cert_config,
            )

            assert response.status_code == 200, f"API request failed: {response.text}"
            response_data = response.json()
            assert "task_id" in response_data, "Response missing task_id"
            assert "submitted_at" in response_data, "Response missing submitted_at"

            task_id = response_data["task_id"]

            # Poll the task-status API until the task completes or times out
            max_retries = 30
            retry_count = 0
            task_completed = False

            while retry_count < max_retries and not task_completed:
                status_response = requests.get(
                    f"{self._get_api_base_url()}/task-status",
                    params={"task_id": task_id},
                    **cert_config,
                )

                assert (
                    status_response.status_code == 200
                ), f"Status API request failed: {status_response.text}"
                status_data = status_response.json()

                if status_data["task_status"] == "COMPLETED":
                    task_completed = True
                    # For simple diff, we expect no differences
                    assert (
                        status_data.get("diff_file_path") is None
                    ), "Expected no differences but found some"
                elif status_data["task_status"] == "FAILED":
                    error_msg = status_data.get("error_message", "Unknown error")
                    pytest.fail(f"Task failed: {error_msg}")
                else:
                    time.sleep(1)
                    retry_count += 1

            assert task_completed, "Task did not complete within timeout period"

        except Exception as e:
            pytest.fail(f"Test failed: {str(e)}")

    @pytest.mark.parametrize("table_name", ["public.customers"])
    @pytest.mark.parametrize("column_name", ["first_name"])
    @pytest.mark.parametrize("key_column", ["index"])
    def test_table_diff_with_differences(
        self,
        cli,
        capsys,
        ace_conf,
        table_name,
        column_name,
        key_column,
        diff_file_path,
    ):
        """Test table diff API with differences between nodes"""
        try:
            # Introduce differences using the helper method
            modified_indices = self._introduce_differences(
                ace_conf, "n2", table_name, column_name, key_column
            )

            # Prepare the request payload
            payload = {
                "cluster_name": "eqn-t9da",
                "table_name": table_name,
                "dbname": "demo",
                "block_size": 10000,
                "max_cpu_ratio": 0.6,
                "output": "json",
                "nodes": "all",
                "batch_size": 1,
                "quiet": False,
            }

            # Get certificate configuration
            cert_config = self._get_cert_config(ace_conf)

            # Make the API request
            response = requests.post(
                f"{self._get_api_base_url()}/table-diff",
                json=payload,
                **cert_config,
            )

            assert response.status_code == 200, f"API request failed: {response.text}"
            response_data = response.json()
            assert "task_id" in response_data, "Response missing task_id"
            assert "submitted_at" in response_data, "Response missing submitted_at"

            task_id = response_data["task_id"]

            # Poll the task-status API until the task completes or times out
            max_retries = 30
            retry_count = 0
            task_completed = False

            while retry_count < max_retries and not task_completed:
                status_response = requests.get(
                    f"{self._get_api_base_url()}/task-status",
                    params={"task_id": task_id},
                    **cert_config,
                )

                assert status_response.status_code == 200, "Status API request failed"
                status_data = status_response.json()

                if status_data["task_status"] == "COMPLETED":
                    task_completed = True
                    diff_file_path.path = status_data.get("diff_file_path")
                elif status_data["task_status"] == "FAILED":
                    error_msg = status_data.get("error_message", "Unknown error")
                    pytest.fail(f"Diff task failed: {error_msg}")
                else:
                    time.sleep(1)
                    retry_count += 1

            assert task_completed, "Task did not complete within timeout period"

            # Read and verify the diff file
            with open(diff_file_path.path, "r") as f:
                diff_data = json.load(f)

            # Verify the number of differences matches our modifications
            assert (
                len(diff_data["diffs"]["n1/n2"]["n2"]) == 50
            ), "Expected 50 differences"

            # Verify each modified row is present in the diff
            diff_indices = {
                diff[key_column] for diff in diff_data["diffs"]["n1/n2"]["n2"]
            }
            assert (
                modified_indices == diff_indices
            ), "Modified rows don't match diff file records"

            # Verify the differences are correctly reported
            for diff in diff_data["diffs"]["n1/n2"]["n2"]:
                assert diff[column_name].endswith(
                    "-modified"
                ), f"Modified row {diff[key_column]} doesn't have expected suffix"

            # Verify the control rows are not modified
            for diff in diff_data["diffs"]["n1/n2"]["n1"]:
                assert not diff[column_name].endswith(
                    "-modified"
                ), f"Control row {diff[key_column]} shouldn't have modification suffix"

        except Exception as e:
            pytest.fail(f"Test failed: {str(e)}")

    @pytest.mark.parametrize("table_name", ["public.customers"])
    def test_simple_table_repair(
        self, cli, capsys, ace_conf, table_name, diff_file_path
    ):
        """Test table repair API on cluster eqn-t9da for specified table"""
        assert diff_file_path.path is not None
        assert os.path.exists(diff_file_path.path)

        cert_config = self._get_cert_config(ace_conf)
        max_retries = 10
        retry_count = 0
        task_completed = False

        try:
            # Now call the repair API
            repair_payload = {
                "cluster_name": "eqn-t9da",
                "diff_file": diff_file_path.path,
                "source_of_truth": "n1",
                "table_name": table_name,
                "dbname": "demo",
                "quiet": False,
            }

            repair_response = requests.post(
                f"{self._get_api_base_url()}/table-repair",
                json=repair_payload,
                **cert_config,
            )

            assert repair_response.status_code == 200
            repair_task_id = repair_response.json()["task_id"]

            # Wait for repair to complete
            retry_count = 0
            task_completed = False

            while retry_count < max_retries and not task_completed:
                status_response = requests.get(
                    f"{self._get_api_base_url()}/task-status",
                    params={"task_id": repair_task_id},
                    **cert_config,
                )

                print(status_response.text)

                assert status_response.status_code == 200
                status_data = status_response.json()

                if status_data["task_status"] == "COMPLETED":
                    task_completed = True
                elif status_data["task_status"] == "FAILED":
                    error_msg = status_data.get("error_message", "Unknown error")
                    pytest.fail(f"Repair task failed: {error_msg}")
                else:
                    time.sleep(1)
                retry_count += 1

            assert task_completed, "Repair task did not complete within timeout period"

        except Exception as e:
            pytest.fail(f"Test failed: {str(e)}")

    @pytest.mark.parametrize("table_name", ["public.customers"])
    @pytest.mark.parametrize("key_column", ["index"])
    def test_table_rerun_temptable(
        self,
        cli,
        capsys,
        ace_conf,
        table_name,
        key_column,
        diff_file_path,
    ):
        """Test table rerun API (hostdb mode) on cluster eqn-t9da"""

        modified_indices = self._introduce_differences(
            ace_conf, "n2", table_name, "first_name", "index"
        )

        try:
            # First create a diff file using table-diff API
            payload = {
                "cluster_name": "eqn-t9da",
                "table_name": table_name,
                "dbname": "demo",
                "block_size": 10000,
                "max_cpu_ratio": 0.6,
                "output": "json",
                "nodes": "all",
                "batch_size": 1,
                "quiet": False,
            }

            cert_config = self._get_cert_config(ace_conf)
            response = requests.post(
                f"{self._get_api_base_url()}/table-diff",
                json=payload,
                **cert_config,
            )

            assert response.status_code == 200, f"API request failed: {response.text}"
            task_id = response.json()["task_id"]

            # Wait for diff to complete
            max_retries = 30
            retry_count = 0
            task_completed = False

            while retry_count < max_retries and not task_completed:
                status_response = requests.get(
                    f"{self._get_api_base_url()}/task-status",
                    params={"task_id": task_id},
                    **cert_config,
                )

                assert status_response.status_code == 200
                status_data = status_response.json()

                if status_data["task_status"] == "COMPLETED":
                    task_completed = True
                    diff_file_path.path = status_data.get("diff_file_path")
                elif status_data["task_status"] == "FAILED":
                    error_msg = status_data.get("error_message", "Unknown error")
                    pytest.fail(f"Diff task failed: {error_msg}")
                else:
                    time.sleep(1)
                    retry_count += 1

            assert task_completed, "Diff task did not complete within timeout period"
            assert diff_file_path.path is not None, "No diff file was generated"

            rerun_payload = {
                "cluster_name": "eqn-t9da",
                "diff_file": diff_file_path.path,
                "table_name": table_name,
                "dbname": "demo",
                "quiet": False,
            }

            rerun_response = requests.post(
                f"{self._get_api_base_url()}/table-rerun",
                json=rerun_payload,
                **cert_config,
            )

            assert rerun_response.status_code == 200
            rerun_task_id = rerun_response.json()["task_id"]

            # Wait for rerun to complete
            retry_count = 0
            task_completed = False

            while retry_count < max_retries and not task_completed:
                status_response = requests.get(
                    f"{self._get_api_base_url()}/task-status",
                    params={"task_id": rerun_task_id},
                    **cert_config,
                )

                assert status_response.status_code == 200
                status_data = status_response.json()

                if status_data["task_status"] == "COMPLETED":
                    task_completed = True
                elif status_data["task_status"] == "FAILED":
                    error_msg = status_data.get("error_message", "Unknown error")
                    pytest.fail(f"Rerun task failed: {error_msg}")
                else:
                    time.sleep(1)
                    retry_count += 1

            assert task_completed, "Rerun task did not complete within timeout period"

            with open(diff_file_path.path, "r") as f:
                diff_data = json.load(f)

            # Verify the number of differences matches our modifications
            assert (
                len(diff_data["diffs"]["n1/n2"]["n2"]) == 50
            ), "Expected 50 differences"

            diff_indices = {
                diff[key_column] for diff in diff_data["diffs"]["n1/n2"]["n2"]
            }
            assert (
                modified_indices == diff_indices
            ), "Modified rows don't match diff file records"

            # Verify the differences are correctly reported
            for diff in diff_data["diffs"]["n1/n2"]["n2"]:
                assert diff["first_name"].endswith(
                    "-modified"
                ), f"Modified row {diff[key_column]} doesn't have expected suffix"

            # Repair to restore state
            cli.table_repair(
                cluster_name="eqn-t9da",
                diff_file=diff_file_path.path,
                table_name=table_name,
                source_of_truth="n1",
            )

            captured = capsys.readouterr()
            output = captured.out

            assert (
                "successfully applied diffs" in output.lower()
            ), f"Table repair failed. Output: {output}"

        except Exception as e:
            pytest.fail(f"Test failed: {str(e)}")
