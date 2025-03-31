import random
import pytest
from psycopg import sql
import psycopg
import re
import json
import abc

from faker import Faker

import test_config


@pytest.mark.usefixtures("prepare_databases")
@pytest.mark.abstract_base
class TestMerkleTreesSimple(abc.ABC):
    """Tests for merkle tree operations"""

    def insert_records(self, conn, schema, table, key_column, num_records):
        fake = Faker()
        start = 0
        cur = conn.cursor()
        cur.execute("SELECT spock.repair_mode(true)")
        inserts = []
        for _ in range(num_records):
            start += 1
            index = start
            customer_id = fake.uuid4()
            first_name = fake.first_name()
            last_name = fake.last_name()
            company = fake.company()
            city = fake.city()
            country = fake.country()
            phone_1 = fake.phone_number()
            phone_2 = fake.phone_number()
            email = fake.email()
            subscription_date = fake.date_time_this_decade(
                before_now=True, after_now=False
            ).strftime("%Y-%m-%d %H:%M:%S")
            website = fake.url()

            inserts.append(
                (
                    index,
                    customer_id,
                    first_name,
                    last_name,
                    company,
                    city,
                    country,
                    phone_1,
                    phone_2,
                    email,
                    subscription_date,
                    website,
                )
            )

        cur.executemany(
            sql.SQL(
                """
            INSERT INTO {schema}.{table}
            (
                index,
                customer_id,
                first_name,
                last_name,
                company,
                city,
                country,
                phone_1,
                phone_2,
                email,
                subscription_date,
                website
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT({key_column}) DO NOTHING;
        """
            ).format(
                schema=sql.Identifier(schema),
                table=sql.Identifier(table),
                key_column=sql.SQL(", ").join(sql.Identifier(k) for k in key_column),
            ),
            inserts,
        )

        conn.commit()
        print(f"Successfully inserted {num_records} records into the database.")

    @pytest.fixture(scope="class", autouse=True)
    def setup_test_scenario(self, nodes):
        """Setup fixture to create different scenarios for block boundary testing"""
        try:
            for node in nodes:
                conn = psycopg.connect(host=node, dbname="demo", user="admin")
                cur = conn.cursor()
                customers2_sql = """
                CREATE TABLE IF NOT EXISTS customers2 (
                    index INTEGER PRIMARY KEY NOT NULL,
                    customer_id TEXT NOT NULL,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    company TEXT NOT NULL,
                    city TEXT NOT NULL,
                    country TEXT NOT NULL,
                    phone_1 TEXT NOT NULL,
                    phone_2 TEXT NOT NULL,
                    email TEXT NOT NULL,
                    subscription_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                    website TEXT NOT NULL
                );
                """

                cur.execute(customers2_sql)

                with open(test_config.CUSTOMERS2_CSV, "r") as f:
                    with cur.copy(
                        "COPY customers2 FROM STDIN CSV HEADER DELIMITER ','"
                    ) as copy:
                        copy.write(f.read())

                cur.execute(
                    "SELECT spock.repset_add_table('test_repset', 'customers2')"
                )

                conn.commit()
                cur.close()
                conn.close()

                print(f"Created customers2 table on {node}")

            yield

            # Cleanup
            for node in nodes:
                conn = psycopg.connect(host=node, dbname="demo", user="admin")
                cur = conn.cursor()
                cur.execute("DROP TABLE customers2 cascade")
                conn.commit()
                cur.close()
                conn.close()

                print(f"Dropped customers2 table on {node}")

        except Exception as e:
            pytest.fail(f"Test failed: {str(e)}")

    @pytest.mark.parametrize("cluster_name", ["eqn-t9da"])
    def test_merkle_tree_init(self, cli, capsys, cluster_name, nodes):
        """Test merkle tree init"""
        cli.merkle_tree_cli("init", cluster_name)

        captured = capsys.readouterr()

        for node in nodes:
            if node == "n1":
                node = "localhost"
            assert (
                f"Merkle tree objects initialised successfully on {node}"
                in captured.out
            )

    @pytest.mark.parametrize("table", ["public.customers", "public.customers2"])
    def test_merkle_tree_setup(self, cli, capsys, table, nodes):
        """
        Test merkle tree setup for tables
        """

        block_size = 50000 if table == "public.customers2" else 1000

        cli.merkle_tree_cli(
            "build", "eqn-t9da", table_name=table, block_size=block_size
        )

        captured = capsys.readouterr()
        clean_output = re.sub(
            r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", captured.out
        )

        for node in nodes:
            assert f"Merkle tree built successfully on {node}" in clean_output

    @pytest.mark.parametrize(
        "table, diff_count", [("public.customers", 75), ("public.customers2", 1000)]
    )
    def test_simple_diff(self, cli, capsys, table, diff_count):
        """Test simple diff cases"""

        l_schema, l_table = table.split(".")
        conn = psycopg.connect(host="n1", dbname="demo", user="admin")
        cur = conn.cursor()
        cur.execute("SELECT spock.repair_mode(true)")

        cur.execute(
            sql.SQL(
                """
                UPDATE {schema}.{table}
                SET first_name = 'Modified'
                WHERE index in
                (
                    SELECT index from {table} order by random() limit {diff_count}
                )
                """
            ).format(
                schema=sql.Identifier(l_schema),
                table=sql.Identifier(l_table),
                diff_count=sql.SQL(str(diff_count)),
            )
        )

        conn.commit()
        cur.close()
        conn.close()

        cli.merkle_tree_cli("diff", "eqn-t9da", table_name=table)
        captured = capsys.readouterr()
        clean_output = re.sub(
            r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", captured.out
        )
        match = re.search(r"diffs written out to (.+\.json)", clean_output.lower())
        assert match, "Diff file path not found in output"
        diff_file = match.group(1)

        diffs = []

        with open(diff_file, "r") as f:
            diffs = json.load(f)

        assert len(diffs["diffs"]["n1/n2"]["n1"]) == diff_count
        assert len(diffs["diffs"]["n1/n2"]["n2"]) == diff_count

        for diff in diffs["diffs"]["n1/n2"]["n1"]:
            assert diff["first_name"] == "Modified"

        # We're done. Repair it back.
        cli.table_repair_cli("eqn-t9da", table, diff_file, source_of_truth="n2")

    @pytest.mark.parametrize("table", ["public.customers", "public.customers2"])
    def test_boundaries(self, cli, capsys, table):
        """Test block boundaries"""

        l_schema, l_table = table.split(".")

        conn = psycopg.connect(host="n2", dbname="demo", user="admin")
        cur = conn.cursor()

        # Let's first read the ranges and then pick a random set.
        cur.execute(
            sql.SQL(
                f"""
                SELECT range_start, range_end
                FROM ace_mtree_{l_schema}_{l_table}
                where node_level = 0
                order by node_position
                """
            )
        )

        ranges = cur.fetchall()
        print(ranges)

        ranges_to_modify = (
            [ranges[0][0]]
            + [random.choice(r) for r in random.sample(ranges, int(0.5 * len(ranges)))]
            + [ranges[-1][0]]
        )

        ranges_to_modify = list(set(ranges_to_modify))
        ranges_to_modify.sort()

        expected_diff_count = len(ranges_to_modify)

        cur.execute("SELECT spock.repair_mode(true)")
        for range in ranges_to_modify:
            cur.execute(
                sql.SQL(
                    f"""
                UPDATE {table}
                SET first_name = 'Modified'
                WHERE index = {range}
                """
                )
            )

        conn.commit()
        cur.close()
        conn.close()

        cli.merkle_tree_cli("diff", "eqn-t9da", table_name=table)
        captured = capsys.readouterr()
        clean_output = re.sub(
            r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", captured.out
        )
        match = re.search(r"diffs written out to (.+\.json)", clean_output.lower())
        assert match, "Diff file path not found in output"
        diff_file = match.group(1)

        with open(diff_file, "r") as f:
            diff_data = json.load(f)

        assert len(diff_data["diffs"]["n1/n2"]["n2"]) == expected_diff_count

        for diff in diff_data["diffs"]["n1/n2"]["n2"]:
            assert diff["first_name"] == "Modified"

        # Repair everything now
        cli.table_repair_cli("eqn-t9da", table, diff_file, source_of_truth="n1")

    @pytest.mark.parametrize("table", ["public.customers"])
    def test_split_ranges(self, cli, capsys, table):
        """
        Testing range splits automatically tests merges as well.
        """

        l_schema, l_table = table.split(".")

        # We'll first delete keys en masse. Then get the new ranges, and finally
        # insert records to trigger the split.
        conn = psycopg.connect(host="n2", dbname="demo", user="admin")
        cur = conn.cursor()

        cur.execute(sql.SQL("SELECT spock.repair_mode(true)"))
        cur.execute(
            sql.SQL("DELETE FROM {schema}.{table} WHERE index <= 4000").format(
                schema=sql.Identifier(l_schema), table=sql.Identifier(l_table)
            )
        )

        conn.commit()
        cur.close()
        conn.close()

        # We're going to deliberately rebalance the tree to make way for the splits.
        cli.merkle_tree_cli(
            "update", "eqn-t9da", table_name=table, nodes="n2", rebalance=True
        )
        captured = capsys.readouterr()
        clean_output = re.sub(
            r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", captured.out
        )
        print(clean_output)

        assert "successfully updated" in clean_output.lower()

        conn = psycopg.connect(host="n2", dbname="demo", user="admin")
        cur = conn.cursor()

        # check if the merge from the rebalance has happened

        cur.execute(
            sql.SQL(
                f"""
            SELECT range_end
            FROM ace_mtree_{l_schema}_{l_table}
            where node_level = 0
            order by node_position
            limit 1
            """
            )
        )

        range_end = cur.fetchone()[0]
        assert range_end > 4000

        # Now we'll insert records to trigger the split.
        self.insert_records(conn, l_schema, l_table, ["index"], 2000)

        cli.merkle_tree_cli(
            "update", "eqn-t9da", table_name=table, nodes="n2", rebalance=True
        )
        captured = capsys.readouterr()
        clean_output = re.sub(
            r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", captured.out
        )
        print(clean_output)
        assert "successfully updated" in clean_output.lower()

        # check if the split has happened
        cur.execute(
            sql.SQL(
                f"""
            SELECT range_end
            FROM ace_mtree_{l_schema}_{l_table}
            where node_level = 0
            order by node_position
            limit 1
            """
            )
        )

        range_end = cur.fetchone()[0]
        assert range_end <= 2000

        cli.merkle_tree_cli("diff", "eqn-t9da", table_name=table)
        captured = capsys.readouterr()
        clean_output = re.sub(
            r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", captured.out
        )
        diff_file = re.search(r"diffs written out to (.+\.json)", clean_output.lower())
        assert diff_file, "Diff file path not found in output"
        diff_file = diff_file.group(1)

        cli.table_repair_cli("eqn-t9da", table, diff_file, source_of_truth="n1")

    @pytest.mark.parametrize("table, block_size", [("public.customers2", 50000)])
    def test_merges(self, cli, capsys, table, block_size):
        """Test merges"""

        l_schema, l_table = table.split(".")

        conn = psycopg.connect(host="n2", dbname="demo", user="admin")
        cur = conn.cursor()
        cur.execute(sql.SQL("SELECT spock.repair_mode(true)"))

        # delete 100k-200k and >=900k
        cur.execute(
            sql.SQL(
                """
                DELETE FROM {schema}.{table}
                WHERE (index >= 100000 AND index <= 200000) OR index >= 900000
                """
            ).format(schema=sql.Identifier(l_schema), table=sql.Identifier(l_table))
        )

        conn.commit()
        cur.close()

        cli.merkle_tree_cli("diff", "eqn-t9da", table_name=table, rebalance=True)
        captured = capsys.readouterr()
        clean_output = re.sub(
            r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", captured.out
        )
        diff_file = re.search(r"diffs written out to (.+\.json)", clean_output.lower())
        assert diff_file, "Diff file path not found in output"

        diff_file = diff_file.group(1)

        conn = psycopg.connect(host="n2", dbname="demo", user="admin")
        cur = conn.cursor()

        cur.execute(
            sql.SQL(
                """
            SELECT count(t.index)
            FROM {mtree_table} mt
            LEFT JOIN {schema}.{table} t
            ON t.index >= mt.range_start
            AND (t.index <= mt.range_end OR mt.range_end IS NULL)
            WHERE mt.node_level = 0
            GROUP BY mt.range_start, mt.range_end
            """
            ).format(
                schema=sql.Identifier(l_schema),
                table=sql.Identifier(l_table),
                mtree_table=sql.Identifier(f"ace_mtree_{l_schema}_{l_table}"),
            )
        )

        counts = cur.fetchall()
        assert all(count[0] > 0 for count in counts)

        cur.close()
        conn.close()

        # cli.table_repair_cli("eqn-t9da", table, diff_file, source_of_truth="n1")

    @pytest.mark.parametrize("table", ["public.customers", "public.customers2"])
    def test_mtree_table_cleanup(self, cli, capsys, table, nodes):
        cli.merkle_tree_cli("teardown", "eqn-t9da", table_name=table)

        captured = capsys.readouterr()

        for node in nodes:
            if node == "n1":
                node = "localhost"
            assert (
                f"Dropped table-specific merkle tree objects on {node}" in captured.out
            )

    def test_mtree_cleanup(self, cli, capsys, nodes):
        cli.merkle_tree_cli("teardown", "eqn-t9da")

        captured = capsys.readouterr()

        for node in nodes:
            if node == "n1":
                node = "localhost"
            assert f"Dropped generic merkle tree objects on {node}" in captured.out
