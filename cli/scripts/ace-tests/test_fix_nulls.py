import pytest
import psycopg
import re


@pytest.mark.usefixtures("prepare_databases")
class TestTableRepairFixNulls:
    """Group of tests for table-repair fix-nulls feature"""

    @pytest.fixture(scope="class")
    def setup_simple_nulls(self, nodes):
        """Setup fixture to create a table with simple primary key and nulls"""
        try:
            # Create table with simple primary key
            for node in nodes:
                conn = psycopg.connect(host=node, dbname="demo", user="admin")
                cur = conn.cursor()

                # Create the table
                cur.execute(
                    """
                    CREATE TABLE simple_nulls (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        description TEXT
                    )
                """
                )

                # Insert data with nulls on n2
                if node == "n2":
                    cur.execute(
                        """
                        INSERT INTO simple_nulls VALUES
                        (1, 'Item 1', NULL),
                        (2, NULL, 'Description 2'),
                        (3, 'Item 3', NULL)
                    """
                    )
                else:
                    cur.execute(
                        """
                        INSERT INTO simple_nulls VALUES
                        (1, 'Item 1', 'Description 1'),
                        (2, 'Item 2', 'Description 2'),
                        (3, 'Item 3', 'Description 3')
                    """
                    )

                repset_add_nulls_sql = """
                SELECT spock.repset_add_table('test_repset', 'simple_nulls')
                """
                cur.execute(repset_add_nulls_sql)
                print("add nulls to test_repset", cur.fetchone())

                conn.commit()
                cur.close()
                conn.close()

            yield

            # Cleanup
            for node in nodes:
                conn = psycopg.connect(host=node, dbname="demo", user="admin")
                cur = conn.cursor()
                repset_remove_nulls = """
                SELECT spock.repset_remove_table('test_repset', 'simple_nulls')
                """
                cur.execute(repset_remove_nulls)
                print("remove nulls from test_repset", cur.fetchone())
                cur.execute("DROP TABLE IF EXISTS simple_nulls CASCADE")
                conn.commit()
                cur.close()
                conn.close()

        except Exception as e:
            pytest.fail(f"Failed to setup/cleanup simple nulls test: {str(e)}")

    @pytest.fixture(scope="class")
    def setup_composite_nulls(self, nodes):
        """Setup fixture to create a table with composite primary key and nulls"""
        try:
            # Create table with composite primary key
            for node in nodes:
                conn = psycopg.connect(host=node, dbname="demo", user="admin")
                cur = conn.cursor()

                # Create the table
                cur.execute(
                    """
                    CREATE TABLE composite_nulls (
                        id1 INTEGER,
                        id2 TEXT,
                        data TEXT,
                        notes TEXT,
                        PRIMARY KEY (id1, id2)
                    )
                """
                )

                # Insert data with different nulls on different nodes
                if node == "n1":
                    cur.execute(
                        """
                        INSERT INTO composite_nulls VALUES
                        (1, 'A', 'Data 1', NULL),
                        (2, 'B', NULL, 'Note 2'),
                        (3, 'C', 'Data 3', 'Note 3')
                    """
                    )
                elif node == "n2":
                    cur.execute(
                        """
                        INSERT INTO composite_nulls VALUES
                        (1, 'A', NULL, 'Note 1'),
                        (2, 'B', 'Data 2', NULL),
                        (3, 'C', NULL, NULL)
                    """
                    )
                else:
                    cur.execute(
                        """
                        INSERT INTO composite_nulls VALUES
                        (1, 'A', 'Data 1', 'Note 1'),
                        (2, 'B', 'Data 2', 'Note 2'),
                        (3, 'C', 'Data 3', 'Note 3')
                    """
                    )

                repset_add_nulls_sql = """
                SELECT spock.repset_add_table('test_repset', 'composite_nulls')
                """
                cur.execute(repset_add_nulls_sql)
                print("add nulls to test_repset", cur.fetchone())

                conn.commit()
                cur.close()
                conn.close()

            yield

            # Cleanup
            for node in nodes:
                conn = psycopg.connect(host=node, dbname="demo", user="admin")
                cur = conn.cursor()
                repset_remove_nulls = """
                SELECT spock.repset_remove_table('test_repset', 'composite_nulls')
                """
                cur.execute(repset_remove_nulls)
                print("remove nulls from test_repset", cur.fetchone())
                cur.execute("DROP TABLE IF EXISTS composite_nulls CASCADE")
                conn.commit()
                cur.close()
                conn.close()

        except Exception as e:
            pytest.fail(f"Failed to setup/cleanup composite nulls test: {str(e)}")

    @pytest.fixture(scope="class")
    def setup_mixed_case_nulls(self, nodes):
        """Setup fixture to create a table with mixed case names and nulls"""
        try:
            # Create table with mixed case names
            for node in nodes:
                conn = psycopg.connect(host=node, dbname="demo", user="admin")
                cur = conn.cursor()

                # Create the table with mixed case names
                cur.execute(
                    """
                    CREATE TABLE "MixedCaseNulls" (
                        "ItemId" INTEGER PRIMARY KEY,
                        "ItemName" TEXT,
                        "ItemDesc" TEXT
                    )
                """
                )

                # Insert data with nulls on n2
                if node == "n2":
                    cur.execute(
                        """
                        INSERT INTO "MixedCaseNulls" VALUES
                        (1, 'Item 1', NULL),
                        (2, NULL, 'Description 2'),
                        (3, 'Item 3', NULL)
                    """
                    )
                else:
                    cur.execute(
                        """
                        INSERT INTO "MixedCaseNulls" VALUES
                        (1, 'Item 1', 'Description 1'),
                        (2, 'Item 2', 'Description 2'),
                        (3, 'Item 3', 'Description 3')
                    """
                    )

                repset_add_nulls_sql = """
                SELECT spock.repset_add_table('test_repset', '"MixedCaseNulls"')
                """
                cur.execute(repset_add_nulls_sql)
                print("add nulls to test_repset", cur.fetchone())

                conn.commit()
                cur.close()
                conn.close()

            yield

            # Cleanup
            for node in nodes:
                conn = psycopg.connect(host=node, dbname="demo", user="admin")
                cur = conn.cursor()
                repset_remove_nulls = """
                SELECT spock.repset_remove_table('test_repset', '"MixedCaseNulls"')
                """
                cur.execute(repset_remove_nulls)
                print("remove nulls from test_repset", cur.fetchone())
                cur.execute('DROP TABLE IF EXISTS "MixedCaseNulls" CASCADE')
                conn.commit()
                cur.close()
                conn.close()

        except Exception as e:
            pytest.fail(f"Failed to setup/cleanup mixed case nulls test: {str(e)}")

    @pytest.fixture(scope="class")
    def setup_datatype_nulls(self, nodes):
        """Setup fixture to create a table with various datatypes and nulls"""
        try:
            # Create table with various datatypes
            for node in nodes:
                conn = psycopg.connect(host=node, dbname="demo", user="admin")
                cur = conn.cursor()

                # Create the table with various datatypes
                cur.execute(
                    """
                    CREATE TABLE datatype_nulls (
                        id INTEGER PRIMARY KEY,
                        json_data JSONB,
                        array_data INTEGER[],
                        point_data POINT,
                        bytea_data BYTEA,
                        text_data TEXT
                    )
                """
                )

                # Insert data with nulls on n2
                if node == "n2":
                    cur.execute(
                        """
                        INSERT INTO datatype_nulls VALUES
                        (1, NULL, ARRAY[1,2,3], point(1,1),
                         decode('DEADBEEF', 'hex'), 'Text 1'),
                        (2, '{"key": "value"}', NULL, point(2,2),
                         NULL, 'Text 2'),
                        (3, '{"key": "value3"}', ARRAY[7,8,9], NULL,
                         decode('BADDCAFE', 'hex'), NULL)
                    """
                    )
                else:
                    cur.execute(
                        """
                        INSERT INTO datatype_nulls VALUES
                        (1, '{"key": "value1"}', ARRAY[1,2,3], point(1,1),
                         decode('DEADBEEF', 'hex'), 'Text 1'),
                        (2, '{"key": "value2"}', ARRAY[4,5,6], point(2,2),
                         decode('FEEDFACE', 'hex'), 'Text 2'),
                        (3, '{"key": "value3"}', ARRAY[7,8,9], point(3,3),
                         decode('BADDCAFE', 'hex'), 'Text 3')
                    """
                    )

                repset_add_nulls_sql = """
                SELECT spock.repset_add_table('test_repset', 'datatype_nulls')
                """
                cur.execute(repset_add_nulls_sql)
                print("add nulls to test_repset", cur.fetchone())

                conn.commit()
                cur.close()
                conn.close()

            yield

            # Cleanup
            for node in nodes:
                conn = psycopg.connect(host=node, dbname="demo", user="admin")
                cur = conn.cursor()
                repset_remove_nulls = """
                SELECT spock.repset_remove_table('test_repset', 'datatype_nulls')
                """
                cur.execute(repset_remove_nulls)
                print("remove nulls from test_repset", cur.fetchone())
                cur.execute("DROP TABLE IF EXISTS datatype_nulls CASCADE")
                conn.commit()
                cur.close()
                conn.close()

        except Exception as e:
            pytest.fail(f"Failed to setup/cleanup datatype nulls test: {str(e)}")

    @pytest.mark.usefixtures("setup_simple_nulls")
    def test_simple_nulls(self, cli, capsys):
        """Test fix-nulls with simple primary key"""
        # First run table-diff to get the diff file
        cli.table_diff(
            cluster_name="eqn-t9da",
            table_name="public.simple_nulls",
        )
        captured = capsys.readouterr()
        output = captured.out

        # Get diff file path
        clean_output = re.sub(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", output)
        match = re.search(r"diffs written out to (.+\.json)", clean_output.lower())
        assert match, "Diff file path not found in output"
        diff_file_path = match.group(1)

        # Run table-repair with fix-nulls
        cli.table_repair(
            cluster_name="eqn-t9da",
            table_name="public.simple_nulls",
            diff_file=diff_file_path,
            fix_nulls=True,
        )

        # Verify the nulls were fixed
        conn = psycopg.connect(host="n2", dbname="demo", user="admin")
        cur = conn.cursor()
        cur.execute("SELECT * FROM simple_nulls ORDER BY id")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        print("rows", rows)

        # Check that nulls were replaced with correct values
        assert rows[0][2] == "Description 1"  # description was null
        assert rows[1][1] == "Item 2"  # name was null
        assert rows[2][2] == "Description 3"  # description was null

    @pytest.mark.usefixtures("setup_composite_nulls")
    def test_composite_nulls(self, cli, capsys):
        """Test fix-nulls with composite primary key"""
        # First run table-diff to get the diff file
        cli.table_diff(
            cluster_name="eqn-t9da",
            table_name="public.composite_nulls",
        )
        captured = capsys.readouterr()
        output = captured.out

        # Get diff file path
        clean_output = re.sub(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", output)
        match = re.search(r"diffs written out to (.+\.json)", clean_output.lower())
        assert match, "Diff file path not found in output"
        diff_file_path = match.group(1)

        # Run table-repair with fix-nulls
        cli.table_repair(
            cluster_name="eqn-t9da",
            table_name="public.composite_nulls",
            diff_file=diff_file_path,
            fix_nulls=True,
        )

        # Verify the nulls were fixed on both n1 and n2
        for node in ["n1", "n2"]:
            conn = psycopg.connect(host=node, dbname="demo", user="admin")
            cur = conn.cursor()
            cur.execute("SELECT * FROM composite_nulls ORDER BY id1, id2")
            rows = cur.fetchall()
            cur.close()
            conn.close()

            # Check that all nulls were replaced with correct values
            for row in rows:
                assert None not in row, f"Found null in row on node {node}"

    @pytest.mark.usefixtures("setup_mixed_case_nulls")
    def test_mixed_case_nulls(self, cli, capsys):
        """Test fix-nulls with mixed case table and column names"""
        # First run table-diff to get the diff file
        cli.table_diff(
            cluster_name="eqn-t9da",
            table_name="public.MixedCaseNulls",
        )
        captured = capsys.readouterr()
        output = captured.out

        # Get diff file path
        clean_output = re.sub(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", output)
        match = re.search(r"diffs written out to (.+\.json)", clean_output.lower())
        assert match, "Diff file path not found in output"
        diff_file_path = match.group(1)

        # Run table-repair with fix-nulls
        cli.table_repair(
            cluster_name="eqn-t9da",
            table_name="public.MixedCaseNulls",
            diff_file=diff_file_path,
            fix_nulls=True,
        )

        # Verify the nulls were fixed
        conn = psycopg.connect(host="n2", dbname="demo", user="admin")
        cur = conn.cursor()
        cur.execute('SELECT * FROM "MixedCaseNulls" ORDER BY "ItemId"')
        rows = cur.fetchall()
        cur.close()
        conn.close()

        # Check that nulls were replaced with correct values
        assert rows[0][2] == "Description 1"  # ItemDesc was null
        assert rows[1][1] == "Item 2"  # ItemName was null
        assert rows[2][2] == "Description 3"  # ItemDesc was null

    @pytest.mark.usefixtures("setup_datatype_nulls")
    def test_datatype_nulls(self, cli, capsys):
        """Test fix-nulls with various datatypes"""
        # First run table-diff to get the diff file
        cli.table_diff(
            cluster_name="eqn-t9da",
            table_name="public.datatype_nulls",
        )
        captured = capsys.readouterr()
        output = captured.out

        # Get diff file path
        clean_output = re.sub(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", output)
        match = re.search(r"diffs written out to (.+\.json)", clean_output.lower())
        assert match, "Diff file path not found in output"
        diff_file_path = match.group(1)

        # Run table-repair with fix-nulls
        cli.table_repair(
            cluster_name="eqn-t9da",
            table_name="public.datatype_nulls",
            diff_file=diff_file_path,
            fix_nulls=True,
        )

        # Verify the nulls were fixed
        conn = psycopg.connect(host="n2", dbname="demo", user="admin")
        cur = conn.cursor()
        cur.execute("SELECT * FROM datatype_nulls ORDER BY id")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        # Check that nulls were replaced with correct values
        assert rows[0][1] == {"key": "value1"}
        assert rows[1][2] == [4, 5, 6]
        assert rows[1][4].decode().lower() == "feedface"
        assert rows[2][3] == "(3,3)"
        assert rows[2][5] == "Text 3"
