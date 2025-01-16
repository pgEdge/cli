import json
import re
import pytest
import psycopg
from test_simple import TestSimple


class TestCompareKeys(TestSimple):
    """Test class for compare_keys functionality in table-diff and table-repair"""

    @pytest.fixture(scope="class", autouse=True)
    def setup_test_tables(self):
        """Create and populate test tables with sequences and unique constraints"""

        # Create table with sequence and unique constraints
        create_table_sql = """
        CREATE TABLE public.users (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            first_name TEXT,
            last_name TEXT
        );
        """

        # Different starting sequences for each node
        sequence_starts = {"n1": 100, "n2": 200, "n3": 300}

        # Execute on all nodes
        for node in ["n1", "n2", "n3"]:
            try:
                params = {
                    "host": node,
                    "dbname": "demo",
                    "user": "admin",
                    "application_name": "ace-tests",
                }

                conn = psycopg.connect(**params)
                cur = conn.cursor()

                cur.execute(create_table_sql)
                seq_start = sequence_starts[node]
                cur.execute(f"ALTER SEQUENCE users_id_seq RESTART WITH {seq_start}")

                cur.execute(
                    """
                INSERT INTO public.users (email, username, first_name, last_name)
                SELECT
                    'user' || n || '@example.com',
                    'user' || n,
                    'First' || n,
                    'Last' || n
                FROM generate_series(1, 100) n;
                """
                )

                cur.execute("SELECT COUNT(*), MIN(id), MAX(id) FROM public.users")
                count, min_id, max_id = cur.fetchone()
                assert count == 100, f"Expected 100 rows on {node}, got {count}"
                assert min_id >= seq_start, f"Min ID {min_id} below start {seq_start}"

                conn.commit()
                cur.close()
                conn.close()
            except Exception as e:
                pytest.fail(f"Failed to setup test tables on {node}: {str(e)}")

        yield  # Let the tests run

        # Cleanup: drop the test table
        for node in ["n1", "n2", "n3"]:
            try:
                params = {
                    "host": node,
                    "dbname": "demo",
                    "user": "admin",
                    "application_name": "ace-tests",
                }

                conn = psycopg.connect(**params)
                cur = conn.cursor()
                cur.execute("DROP TABLE IF EXISTS public.users")
                conn.commit()
                cur.close()
                conn.close()
            except Exception as e:
                pytest.fail(f"Failed to cleanup test tables on {node}: {str(e)}")

    @pytest.mark.parametrize("table_name", ["public.users"])
    def test_compare_keys_table_diff(
        self, cli, capsys, ace_conf, table_name, diff_file_path
    ):
        """Test table-diff using compare_keys with email and username as keys"""

        # First verify that without compare_keys we get differences
        cli.table_diff_cli("eqn-t9da", table_name, nodes="n1,n2")
        captured = capsys.readouterr()
        output = captured.out

        clean_output = re.sub(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", output)
        match = re.search(r"diffs written out to (.+\.json)", clean_output.lower())
        assert match, "Diff file path not found in output"
        diff_file_path.path = match.group(1)

        with open(diff_file_path.path, "r") as f:
            diff_data = json.load(f)

        # Check that all node pairs have 100 differences
        assert all(
            all(len(diffs) == 100 for diffs in node_diffs.values())
            for _, node_diffs in diff_data["diffs"].items()
        ), "Expected 100 differences for each node pair"

        # We should see no differences with compare keys
        cli.table_diff_cli(
            "eqn-t9da",
            table_name,
            nodes="n1,n2",
            compare_keys="email",
        )
        captured = capsys.readouterr()
        output = captured.out
        assert "tables match ok" in output.lower(), "Should match with email"

        cli.table_diff_cli(
            "eqn-t9da", table_name, nodes="n1,n2", compare_keys="username"
        )
        captured = capsys.readouterr()
        output = captured.out
        assert "tables match ok" in output.lower(), "Should match with username"

        # Now let's introduce differences such that in addition to the id diffs,
        # we have some name diffs as well.
        try:
            params = {
                "host": "n2",
                "dbname": "demo",
                "user": "admin",
                "application_name": "ace-tests",
            }
            if ace_conf.USE_CERT_AUTH:
                params["sslmode"] = "verify-full"
                params["sslrootcert"] = ace_conf.CA_CERT_FILE
                params["sslcert"] = ace_conf.ADMIN_CERT_FILE
                params["sslkey"] = ace_conf.ADMIN_KEY_FILE

            conn = psycopg.connect(**params)
            cur = conn.cursor()

            cur.execute(
                """
            UPDATE public.users
            SET first_name = first_name || '-n2',
                last_name = last_name || '-n2'
            WHERE id IN (
                SELECT id FROM public.users
                WHERE email LIKE 'user%@example.com'
                ORDER BY random()
                LIMIT 50
            );
            """
            )
            conn.commit()
            cur.close()
            conn.close()

            params["host"] = "n3"
            conn = psycopg.connect(**params)
            cur = conn.cursor()

            # Modify random rows between 51-100
            cur.execute(
                """
            UPDATE public.users
            SET first_name = first_name || '-n3',
                last_name = last_name || '-n3'
            WHERE id IN (
                SELECT id FROM public.users
                WHERE email LIKE 'user%@example.com'
                ORDER BY random()
                LIMIT 50
            );
            """
            )
            conn.commit()
            cur.close()
            conn.close()

        except Exception as e:
            pytest.fail(f"Failed to modify names: {str(e)}")

        cli.table_diff_cli("eqn-t9da", table_name, compare_keys="username,email")
        captured = capsys.readouterr()
        output = captured.out
        clean_output = re.sub(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", output)
        match = re.search(r"diffs written out to (.+\.json)", clean_output.lower())

        assert match, "Diff file path not found in output"

        diff_file_path.path = match.group(1)

        with open(diff_file_path.path, "r") as f:
            diff_data = json.load(f)

        # We are deliberately not checking for n2/n3 since we won't know
        # what to assert for because of the random() function.
        assert len(diff_data["diffs"]["n1/n2"]["n2"]) == 50
        assert len(diff_data["diffs"]["n1/n3"]["n3"]) == 50

    @pytest.mark.parametrize("table_name", ["public.users"])
    def test_compare_keys_table_rerun(self, cli, capsys, table_name, diff_file_path):
        """Test table-rerun using compare_keys with email and username as keys"""

        # First verify that rerun without compare_keys fails
        with pytest.raises(SystemExit):
            cli.table_rerun_cli(
                cluster_name="eqn-t9da",
                diff_file=diff_file_path.path,
                table_name=table_name,
                dbname="demo",
                behavior="hostdb",
            )
        captured = capsys.readouterr()
        assert (
            "--compare-keys was used to perform the table-diff" in captured.out.lower()
        )

        # Now test rerun with hostdb behavior
        cli.table_rerun_cli(
            cluster_name="eqn-t9da",
            diff_file=diff_file_path.path,
            table_name=table_name,
            dbname="demo",
            behavior="hostdb",
            compare_keys="email,username",
        )
        captured = capsys.readouterr()
        output = captured.out
        clean_output = re.sub(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", output)
        match = re.search(r"diffs written out to (.+\.json)", clean_output.lower())
        assert match, "Diff file path not found in output"
        hostdb_diff_path = match.group(1)

        # Test rerun with multiprocessing behavior
        cli.table_rerun_cli(
            cluster_name="eqn-t9da",
            diff_file=diff_file_path.path,
            table_name=table_name,
            dbname="demo",
            behavior="multiprocessing",
            compare_keys="email,username",
        )
        captured = capsys.readouterr()
        output = captured.out
        clean_output = re.sub(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", output)
        match = re.search(r"diffs written out to (.+\.json)", clean_output.lower())
        assert match, "Diff file path not found in output"
        mp_diff_path = match.group(1)

        # Verify both rerun methods produce the same results
        with open(hostdb_diff_path, "r") as f:
            hostdb_data = json.load(f)
        with open(mp_diff_path, "r") as f:
            mp_data = json.load(f)

        # Compare the diffs from both methods
        assert hostdb_data["diffs"] == mp_data["diffs"], "Rerun methods differ"
        assert len(hostdb_data["diffs"]["n1/n2"]["n2"]) == 50, "Expected 50 differences"
        assert len(hostdb_data["diffs"]["n1/n3"]["n3"]) == 50, "Expected 50 differences"

    @pytest.mark.parametrize("table_name", ["public.users"])
    def test_compare_keys_table_repair(self, cli, capsys, table_name, diff_file_path):
        """Test table-repair using compare_keys with email and username as keys"""

        # Test that repair fails without compare_keys
        with pytest.raises(SystemExit):
            cli.table_repair_cli(
                cluster_name="eqn-t9da",
                diff_file=diff_file_path.path,
                source_of_truth="n1",
                table_name=table_name
            )
        captured = capsys.readouterr()
        assert (
            "--compare-keys was used to perform the table-diff" in captured.out.lower()
        )

        # Now perform repair with compare_keys
        cli.table_repair_cli(
            cluster_name="eqn-t9da",
            diff_file=diff_file_path.path,
            table_name=table_name,
            source_of_truth="n1",
            compare_keys="email,username",
        )
        captured = capsys.readouterr()
        output = captured.out
        assert "repair completed" in output.lower(), "Repair should succeed"

        # Run table-diff without compare_keys to verify original diffs still exist
        cli.table_diff_cli("eqn-t9da", table_name, nodes="n1,n2")
        captured = capsys.readouterr()
        output = captured.out
        clean_output = re.sub(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", output)
        match = re.search(r"diffs written out to (.+\.json)", clean_output.lower())
        assert match, "Diff file path not found in output"
        diff_file_path.path = match.group(1)

        with open(diff_file_path.path, "r") as f:
            diff_data = json.load(f)

        # Verify we still see the original ID differences
        assert all(
            all(len(v) == 100 for v in node_diffs.values())
            for node_diffs in diff_data["diffs"].values()
        ), "Expected 100 differences for each node pair"

        # Finally verify that table-diff with compare_keys shows everything matches
        cli.table_diff_cli(
            "eqn-t9da",
            table_name,
            compare_keys="email,username",
        )
        captured = capsys.readouterr()
        output = captured.out
        assert "tables match ok" in output.lower(), "Should match with compare_keys"
