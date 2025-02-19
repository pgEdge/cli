import pytest
import psycopg
import re


@pytest.mark.usefixtures("prepare_databases")
class TestInsertOnly:
    """Tests for table-repair --insert-only feature"""

    @pytest.fixture(scope="class")
    def setup_test_scenario(self, nodes):
        """Setup fixture to create different scenarios for insert-only testing"""
        try:
            for node in nodes:
                conn = psycopg.connect(host=node, dbname="demo", user="admin")
                cur = conn.cursor()

                cur.execute(
                    """
                    CREATE TABLE insert_only_test (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        value INTEGER,
                        created_at TIMESTAMP WITHOUT TIME ZONE
                    )
                """
                )

                if node == "n1":
                    cur.execute(
                        """
                        INSERT INTO insert_only_test VALUES
                        (1, 'Original 1', 100, '2024-01-01'),
                        (2, 'Original 2', 200, '2024-01-02'),
                        (3, 'Original 3', 300, '2024-01-03')
                    """
                    )
                elif node == "n2":
                    cur.execute(
                        """
                        INSERT INTO insert_only_test VALUES
                        (1, 'Modified 1', 150, '2024-01-01'),
                        (3, 'Modified 3', 350, '2024-01-03')
                    """
                    )
                else:
                    cur.execute(
                        """
                        INSERT INTO insert_only_test VALUES
                        (1, 'Different 1', 175, '2024-01-01')
                    """
                    )

                repset_sql = """
                    SELECT spock.repset_add_table('test_repset', 'insert_only_test')
                """
                cur.execute(repset_sql)

                conn.commit()
                cur.close()
                conn.close()

            yield

            for node in nodes:
                conn = psycopg.connect(host=node, dbname="demo", user="admin")
                cur = conn.cursor()

                cur.execute(
                    """
                    SELECT spock.repset_remove_table('test_repset', 'insert_only_test')
                """
                )

                cur.execute("DROP TABLE IF EXISTS insert_only_test CASCADE")

                conn.commit()
                cur.close()
                conn.close()

        except Exception as e:
            pytest.fail(f"Failed to setup/cleanup insert only test: {str(e)}")

    @pytest.mark.usefixtures("setup_test_scenario")
    def test_insert_only_repair(self, cli, capsys):
        """
        Test that insert-only repair only adds missing rows without
        modifying existing ones
        """
        try:
            cli.table_diff_cli("eqn-t9da", "public.insert_only_test")
            captured = capsys.readouterr()
            clean_output = re.sub(
                r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", captured.out
            )
            match = re.search(r"diffs written out to (.+\.json)", clean_output.lower())
            assert match, "Diff file path not found in output"
            diff_file = match.group(1)

            cli.table_repair_cli(
                "eqn-t9da",
                "public.insert_only_test",
                diff_file,
                source_of_truth="n1",
                insert_only=True,
            )

            conn = psycopg.connect(host="n2", dbname="demo", user="admin")
            cur = conn.cursor()
            cur.execute("SELECT * FROM insert_only_test ORDER BY id")
            n2_rows = cur.fetchall()
            cur.close()
            conn.close()

            # Verify that on n2:
            # 1. Missing row (id=2) was inserted
            # 2. Existing rows (id=1,3) were not modified
            assert len(n2_rows) == 3, "Expected 3 rows after repair"

            assert n2_rows[0][1] == "Modified 1", "Row 1 should not be modified"
            assert n2_rows[0][2] == 150, "Row 1 value should not be modified"

            assert n2_rows[2][1] == "Modified 3", "Row 3 should not be modified"
            assert n2_rows[2][2] == 350, "Row 3 value should not be modified"

            assert n2_rows[1][0] == 2, "Missing row should be inserted"
            assert (
                n2_rows[1][1] == "Original 2"
            ), "Missing row should have original name"
            assert n2_rows[1][2] == 200, "Missing row should have original value"

            conn = psycopg.connect(host="n3", dbname="demo", user="admin")
            cur = conn.cursor()
            cur.execute("SELECT * FROM insert_only_test ORDER BY id")
            n3_rows = cur.fetchall()
            cur.close()
            conn.close()

            # Verify that on n3:
            # 1. Missing rows (id=2,3) were inserted
            # 2. Existing row (id=1) was not modified
            assert len(n3_rows) == 3, "Expected 3 rows after repair"

            assert n3_rows[0][1] == "Different 1", "Row 1 should not be modified"
            assert n3_rows[0][2] == 175, "Row 1 value should not be modified"

            assert n3_rows[1][0] == 2, "Missing row 2 should be inserted"
            assert n3_rows[1][1] == "Original 2", "Row 2 should have original name"
            assert n3_rows[1][2] == 200, "Row 2 should have original value"

            assert n3_rows[2][0] == 3, "Missing row 3 should be inserted"
            assert n3_rows[2][1] == "Original 3", "Row 3 should have original name"
            assert n3_rows[2][2] == 300, "Row 3 should have original value"

        except Exception as e:
            pytest.fail(f"Test failed: {str(e)}")

    @pytest.mark.usefixtures("setup_test_scenario")
    def test_insert_only_with_deletes(self, cli, capsys):
        """Test that insert-only repair ignores deletes"""
        try:
            # Let's delete a row on n1 and check that it's not deleted on n2
            conn = psycopg.connect(host="n1", dbname="demo", user="admin")
            cur = conn.cursor()
            cur.execute("SELECT spock.repair_mode(true)")
            cur.execute("DELETE FROM insert_only_test WHERE id = 1")
            conn.commit()
            cur.close()
            conn.close()

            cli.table_diff_cli("eqn-t9da", "public.insert_only_test")
            captured = capsys.readouterr()
            clean_output = re.sub(
                r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", captured.out
            )
            match = re.search(r"diffs written out to (.+\.json)", clean_output.lower())
            assert match, "Diff file path not found in output"
            diff_file = match.group(1)

            cli.table_repair_cli(
                "eqn-t9da",
                "public.insert_only_test",
                diff_file,
                source_of_truth="n1",
                insert_only=True,
            )

            # Verify that row 1 still exists on n2 and n3
            for node in ["n2", "n3"]:
                conn = psycopg.connect(host=node, dbname="demo", user="admin")
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM insert_only_test WHERE id = 1")
                count = cur.fetchone()[0]
                cur.close()
                conn.close()

                assert count == 1, f"Row 1 should still exist on {node}"

        except Exception as e:
            pytest.fail(f"Test failed: {str(e)}")

    @pytest.fixture(scope="class")
    def setup_bidirectional_scenario(self, nodes):
        """Setup fixture to create scenarios for bidirectional insert testing"""
        try:
            for node in nodes:
                conn = psycopg.connect(host=node, dbname="demo", user="admin")
                cur = conn.cursor()

                cur.execute(
                    """
                    CREATE TABLE bidirectional_test (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        value INTEGER,
                        created_at TIMESTAMP WITHOUT TIME ZONE
                    )
                """
                )
                print(f"Created table bidirectional_test on {node}")

                if node == "n1":
                    cur.execute(
                        """
                        INSERT INTO bidirectional_test
                        SELECT
                            generate_series(1, 10) as id,
                            'n1_row_' || generate_series(1, 10) as name,
                            generate_series(1, 10) * 100 as value,
                            now() as created_at
                    """
                    )
                elif node == "n2":
                    cur.execute(
                        """
                        INSERT INTO bidirectional_test
                        SELECT
                            id,
                            'n2_row_' || id as name,
                            id * 100 as value,
                            now() as created_at
                        FROM (
                            SELECT generate_series(11, 15) as id
                        ) t
                    """
                    )
                else:
                    cur.execute(
                        """
                        INSERT INTO bidirectional_test
                        SELECT
                            id,
                            'n3_row_' || id as name,
                            id * 100 as value,
                            now() as created_at
                        FROM (
                            SELECT generate_series(16, 20) as id
                        ) t
                    """
                    )
                print(f"Inserted data into bidirectional_test on {node}")

                repset_sql = """
                    SELECT spock.repset_add_table('test_repset', 'bidirectional_test')
                """
                cur.execute(repset_sql)
                print(f"Added table to replication set on {node}")
                conn.commit()
                cur.close()
                conn.close()

            yield

            for node in nodes:
                conn = psycopg.connect(host=node, dbname="demo", user="admin")
                cur = conn.cursor()

                cur.execute(
                    """
                    SELECT
                    spock.repset_remove_table('test_repset', 'bidirectional_test')
                    """
                )

                cur.execute("DROP TABLE IF EXISTS bidirectional_test CASCADE")

                conn.commit()
                cur.close()
                conn.close()

        except Exception as e:
            pytest.fail(f"Failed to setup/cleanup bidirectional test: {str(e)}")

    @pytest.mark.usefixtures("setup_bidirectional_scenario")
    def test_bidirectional_insert(self, cli, capsys):
        """Test that bidirectional insert propagates missing rows in both directions"""
        try:
            print("Running table-diff on bidirectional_test")
            cli.table_diff_cli("eqn-t9da", "public.bidirectional_test")
            captured = capsys.readouterr()
            clean_output = re.sub(
                r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", captured.out
            )
            match = re.search(r"diffs written out to (.+\.json)", clean_output.lower())
            assert match, "Diff file path not found in output"
            diff_file = match.group(1)

            print("Running table-repair on bidirectional_test")
            cli.table_repair_cli(
                "eqn-t9da",
                "public.bidirectional_test",
                diff_file,
                insert_only=True,
                bidirectional=True,
            )
            captured = capsys.readouterr()
            clean_output = re.sub(
                r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", captured.out
            )
            assert (
                "completed bidirectional repair" in clean_output.lower()
            ), "Bidirectional repair failed"

            # Verify results on each node
            for node in ["n1", "n2", "n3"]:
                print(f"\nVerifying data on node {node}")
                try:
                    conn = psycopg.connect(
                        host=node,
                        dbname="demo",
                        user="admin",
                        connect_timeout=10,  # Add connection timeout
                    )
                    cur = conn.cursor()

                    print(f"Checking total row count on {node}")
                    cur.execute("SELECT COUNT(*) FROM bidirectional_test")
                    count = cur.fetchone()[0]
                    assert count == 20, f"Expected 20 rows on {node}, found {count}"
                    print(f"Total row count on {node}: {count}")

                    # Check n1's original rows (1-10)
                    print(f"Checking n1's rows on {node}")
                    cur.execute(
                        """
                        SELECT COUNT(*) FROM bidirectional_test
                        WHERE id BETWEEN 1 AND 10
                        AND name LIKE 'n1_row_%'
                    """
                    )
                    n1_rows = cur.fetchone()[0]
                    assert (
                        n1_rows == 10
                    ), f"Expected 10 n1 rows on {node}, found {n1_rows}"
                    print(f"n1 row count on {node}: {n1_rows}")

                    # Check n2's unique rows (11-15)
                    print(f"Checking n2's rows on {node}")
                    cur.execute(
                        """
                        SELECT COUNT(*) FROM bidirectional_test
                        WHERE id BETWEEN 11 AND 15
                        AND name LIKE 'n2_row_%'
                    """
                    )
                    n2_rows = cur.fetchone()[0]
                    assert (
                        n2_rows == 5
                    ), f"Expected 5 n2 rows on {node}, found {n2_rows}"
                    print(f"n2 row count on {node}: {n2_rows}")

                    # Check n3's unique rows (16-20)
                    print(f"Checking n3's rows on {node}")
                    cur.execute(
                        """
                        SELECT COUNT(*) FROM bidirectional_test
                        WHERE id BETWEEN 16 AND 20
                        AND name LIKE 'n3_row_%'
                    """
                    )
                    n3_rows = cur.fetchone()[0]
                    assert (
                        n3_rows == 5
                    ), f"Expected 5 n3 rows on {node}, found {n3_rows}"
                    print(f"n3 row count on {node}: {n3_rows}")

                    # Print full data for debugging if counts don't match
                    if count != 20 or n1_rows != 10 or n2_rows != 5 or n3_rows != 5:
                        print(f"\nDumping full data for {node}:")
                        cur.execute(
                            """
                            SELECT id, name, value
                            FROM bidirectional_test
                            ORDER BY id
                        """
                        )
                        rows = cur.fetchall()
                        for row in rows:
                            print(row)

                except Exception as node_error:
                    print(f"Error while checking node {node}: {str(node_error)}")
                    raise

                finally:
                    if cur:
                        cur.close()
                    if conn:
                        conn.close()
                    print(f"Completed verification for node {node}")

        except Exception as e:
            print(f"Test failed with error: {str(e)}")
            pytest.fail(f"Test failed: {str(e)}")

    @pytest.mark.usefixtures("setup_bidirectional_scenario")
    def test_bidirectional_insert_with_updates(self, cli, capsys):
        """Test that bidirectional insert ignores updates even with conflicts"""
        try:
            for node, suffix in [("n2", "_n2_modified"), ("n3", "_n3_modified")]:
                conn = psycopg.connect(host=node, dbname="demo", user="admin")
                cur = conn.cursor()
                cur.execute("SELECT spock.repair_mode(true)")
                # Modify rows 1-5 which exist on all nodes
                cur.execute(
                    f"""
                    UPDATE bidirectional_test
                    SET name = name || '{suffix}',
                        value = value + 1000
                    WHERE id BETWEEN 1 AND 5
                """
                )
                conn.commit()
                cur.close()
                conn.close()

            cli.table_diff_cli("eqn-t9da", "public.bidirectional_test")
            captured = capsys.readouterr()
            clean_output = re.sub(
                r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", captured.out
            )
            match = re.search(r"diffs written out to (.+\.json)", clean_output.lower())
            assert match, "Diff file path not found in output"
            diff_file = match.group(1)

            cli.table_repair_cli(
                "eqn-t9da",
                "public.bidirectional_test",
                diff_file,
                insert_only=True,
                bidirectional=True,
            )

            # Verify that modifications remain unchanged
            for node, suffix in [("n2", "_n2_modified"), ("n3", "_n3_modified")]:
                conn = psycopg.connect(host=node, dbname="demo", user="admin")
                cur = conn.cursor()

                cur.execute(
                    f"""
                    SELECT COUNT(*) FROM bidirectional_test
                    WHERE id BETWEEN 1 AND 5
                    AND name LIKE '%{suffix}'
                    AND value > 1000
                """
                )
                modified_count = cur.fetchone()[0]
                assert (
                    modified_count == 5
                ), f"Modified rows should remain unchanged on {node}"

                # But all 20 rows should exist
                cur.execute("SELECT COUNT(*) FROM bidirectional_test")
                total_count = cur.fetchone()[0]
                assert (
                    total_count == 20
                ), f"Expected 20 total rows on {node}, found {total_count}"

                cur.close()
                conn.close()

        except Exception as e:
            pytest.fail(f"Test failed: {str(e)}")
