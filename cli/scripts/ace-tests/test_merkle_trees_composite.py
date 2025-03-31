import pdb
import random
import pytest
from psycopg import sql
import psycopg
import re
import json
from test_merkle_trees_simple import TestMerkleTreesSimple

from psycopg.types.composite import register_composite, CompositeInfo


@pytest.mark.usefixtures("prepare_databases")
class TestMerkleTreesComposite(TestMerkleTreesSimple):
    """Tests for merkle tree operations with composite keys"""

    @pytest.fixture(scope="class", autouse=True)
    def setup_composite_keys(self, nodes, setup_test_scenario):
        """Setup fixture to create different scenarios for block boundary testing"""

        try:
            for node in nodes:
                conn = psycopg.connect(host=node, dbname="demo", user="admin")
                cur = conn.cursor()
                cur.execute(
                    sql.SQL("ALTER TABLE customers DROP CONSTRAINT customers_pkey")
                )
                cur.execute(
                    sql.SQL(
                        "ALTER TABLE customers ADD PRIMARY KEY (index, customer_id)"
                    )
                )

                cur.execute(
                    sql.SQL("ALTER TABLE customers2 DROP CONSTRAINT customers2_pkey")
                )
                cur.execute(
                    sql.SQL(
                        "ALTER TABLE customers2 ADD PRIMARY KEY (index, customer_id)"
                    )
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
                cur.execute(
                    sql.SQL("ALTER TABLE customers DROP CONSTRAINT customers_pkey")
                )
                cur.execute(sql.SQL("ALTER TABLE customers ADD PRIMARY KEY (index)"))
                conn.commit()
                cur.close()
                conn.close()

                print(f"Reverted original primary key for customers on {node}")

        except Exception as e:
            pytest.fail(f"Test failed: {str(e)}")

    @pytest.mark.parametrize("cluster_name", ["eqn-t9da"])
    def test_merkle_tree_init(self, cli, capsys, cluster_name, nodes):
        return super().test_merkle_tree_init(cli, capsys, cluster_name, nodes)

    @pytest.mark.parametrize("table", ["public.customers", "public.customers2"])
    def test_merkle_tree_setup(self, cli, capsys, table, nodes):
        return super().test_merkle_tree_setup(cli, capsys, table, nodes)

    @pytest.mark.parametrize(
        "table, diff_count", [("public.customers", 75), ("public.customers2", 1000)]
    )
    def test_simple_diff(self, cli, capsys, table, diff_count):
        return super().test_simple_diff(cli, capsys, table, diff_count)

    @pytest.mark.parametrize("table", ["public.customers", "public.customers2"])
    def test_boundaries(self, cli, capsys, table):
        """Test block boundaries"""

        l_schema, l_table = table.split(".")

        conn = psycopg.connect(host="n2", dbname="demo", user="admin")
        info = CompositeInfo.fetch(conn, f"{l_schema}_{l_table}_key_type")
        register_composite(info, conn, factory=lambda *args: tuple(args))

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

        ranges_to_modify = (
            [ranges[0][0][0]]
            + [
                random.choice(r)[0]
                for r in random.sample(ranges, int(0.5 * len(ranges)))
            ]
            + [ranges[-1][1][0]]
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
        info = CompositeInfo.fetch(conn, f"{l_schema}_{l_table}_key_type")
        register_composite(info, conn, factory=lambda *args: tuple(args))
        cur = conn.cursor()

        cur.execute(sql.SQL("SELECT spock.repair_mode(true)"))
        cur.execute(
            sql.SQL("DELETE FROM {schema}.{table} WHERE index <= 4000").format(
                schema=sql.Identifier(l_schema), table=sql.Identifier(l_table)
            )
        )

        conn.commit()

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

        range_end = cur.fetchone()[0][0]
        assert range_end > 4000

        # Now we'll insert records to trigger the split.
        self.insert_records(conn, l_schema, l_table, ["index", "customer_id"], 2000)

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

        range_end = cur.fetchone()[0][0]
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
        cur.close()
        conn.close()

    @pytest.mark.parametrize("table", [("public.customers2")])
    def test_merges(self, cli, capsys, table):
        """Test merges"""

        l_schema, l_table = table.split(".")

        conn = psycopg.connect(host="n2", dbname="demo", user="admin")
        info = CompositeInfo.fetch(conn, f"{l_schema}_{l_table}_key_type")
        register_composite(info, conn, factory=lambda *args: tuple(args))
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

        cli.merkle_tree_cli("diff", "eqn-t9da", table_name=table, rebalance=True)
        captured = capsys.readouterr()
        clean_output = re.sub(
            r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", captured.out
        )
        diff_file = re.search(r"diffs written out to (.+\.json)", clean_output.lower())
        assert diff_file, "Diff file path not found in output"

        diff_file = diff_file.group(1)

        cur.execute(
            sql.SQL(
                """
                WITH block_data AS
                (
                    SELECT node_position, range_start, range_end
                    FROM {mtree_table}
                    WHERE node_level = 0
                )
                SELECT
                    COUNT(t.*) AS cnt
                FROM block_data b
                LEFT JOIN {schema}.{table} t
                ON ROW({pkey_cols}) >= b.range_start
                AND (ROW({pkey_cols}) <= b.range_end OR b.range_end IS NULL)
                GROUP BY
                    b.node_position,
                    b.range_start,
                    b.range_end
                ORDER BY b.node_position;
            """
            ).format(
                schema=sql.Identifier(l_schema),
                table=sql.Identifier(l_table),
                mtree_table=sql.Identifier(f"ace_mtree_{l_schema}_{l_table}"),
                pkey_cols=sql.SQL(",").join(
                    [sql.Identifier(col) for col in ["index", "customer_id"]]
                ),
            )
        )

        counts = cur.fetchall()
        assert all(count[0] > 0 for count in counts)

        # FIXME! Repair for large diffs seems to be having issues with
        # the bulk dispatcher
        # cli.table_repair_cli("eqn-t9da", table, diff_file, source_of_truth="n1")
        cur.close()
        conn.close()

    @pytest.mark.parametrize("table", ["public.customers", "public.customers2"])
    def test_mtree_table_cleanup(self, cli, capsys, table, nodes):
        return super().test_mtree_table_cleanup(cli, capsys, table, nodes)

    def test_mtree_cleanup(self, cli, capsys, nodes):
        return super().test_mtree_cleanup(cli, capsys, nodes)
