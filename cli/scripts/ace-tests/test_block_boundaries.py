import logging
import random
import pytest
import psycopg
from psycopg import sql
import re
import json

import test_config


@pytest.mark.usefixtures("prepare_databases")
class TestBlockBoundaries:
    """Tests for table-diff block boundaries handling"""

    @pytest.fixture(scope="class")
    def setup_test_scenario(self, nodes):
        """Setup fixture to create different scenarios for block boundary testing"""
        try:
            for node in nodes:
                conn = psycopg.connect(host=node, dbname="demo", user="admin")
                cur = conn.cursor()
                customers1_sql = """
                CREATE TABLE customers1 (
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

                customers2_sql = """
                CREATE TABLE customers2 (
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

                cur.execute(customers1_sql)
                cur.execute(customers2_sql)

                with open(test_config.CUSTOMERS1_CSV, "r") as f:
                    with cur.copy(
                        "COPY customers1 FROM STDIN CSV HEADER DELIMITER ','"
                    ) as copy:
                        copy.write(f.read())

                with open(test_config.CUSTOMERS2_CSV, "r") as f:
                    with cur.copy(
                        "COPY customers2 FROM STDIN CSV HEADER DELIMITER ','"
                    ) as copy:
                        copy.write(f.read())

                cur.execute(
                    "SELECT spock.repset_add_table('test_repset', 'customers1')"
                )
                cur.execute(
                    "SELECT spock.repset_add_table('test_repset', 'customers2')"
                )

                conn.commit()
                cur.close()
                conn.close()

                print(f"Created customers1 and customers2 tables on {node}")

            yield

            # Cleanup
            for node in nodes:
                conn = psycopg.connect(host=node, dbname="demo", user="admin")
                cur = conn.cursor()

                cur.execute("DROP TABLE customers1 cascade")
                cur.execute("DROP TABLE customers2 cascade")
                conn.commit()
                cur.close()
                conn.close()

                print(f"Dropped customers1 and customers2 tables on {node}")

        except Exception as e:
            pytest.fail(f"Test failed: {str(e)}")

    @pytest.mark.usefixtures("setup_test_scenario")
    @pytest.mark.parametrize(
        "table, row_count, block_size",
        [
            ("customers", 10000, 10),
            ("customers", 10000, 100),
            ("customers", 10000, 1000),
            ("customers", 10000, 5000),
            ("customers1", 10500, 10),
            ("customers1", 10500, 100),
            ("customers1", 10500, 1000),
            ("customers1", 10500, 5000),
            ("customers1", 10500, 10000),
            ("customers2", 1000000, 1000),
            ("customers2", 1000000, 10000),
            ("customers2", 1000000, 100000),
            ("customers2", 1000000, 500000),
        ],
    )
    @pytest.mark.parametrize("max_sample_size", [50])
    def test_block_boundaries(
        self, caplog, cli, capsys, table, row_count, block_size, max_sample_size
    ):
        """Test that table-diff correctly identifies differences at block boundaries"""
        caplog.set_level(logging.INFO)
        try:
            # Better to randomise this instead of using hardcoded values
            multiplier = row_count // block_size
            rand_boundaries = list(
                set(
                    [
                        block_size * random.randint(1, multiplier)  # nosec: B311
                        for _ in range(1, multiplier + 1)
                    ]
                )
            )
            block_boundaries = [b - 1 for b in rand_boundaries] + [
                b + 1 for b in rand_boundaries
            ]

            block_boundaries.sort()

            if len(block_boundaries) > max_sample_size:
                block_boundaries = random.sample(block_boundaries, max_sample_size)

            block_boundaries = block_boundaries + [row_count]

            block_boundaries = list(filter(lambda x: x <= row_count, block_boundaries))

            logging.getLogger().info(f"Block boundaries: {block_boundaries}")

            conn = psycopg.connect(host="n2", dbname="demo", user="admin")
            cur = conn.cursor()
            cur.execute("SELECT spock.repair_mode(true)")

            for boundary in block_boundaries:
                cur.execute(
                    sql.SQL(
                        """
                        UPDATE {schema}.{table}
                        SET first_name = 'Modified'
                        WHERE index = {boundary}
                        """
                    ).format(
                        schema=sql.Identifier("public"),
                        table=sql.Identifier(table),
                        boundary=boundary,
                    )
                )

            conn.commit()
            cur.close()
            conn.close()

            # Run table-diff with block size of 1000
            cli.table_diff(
                "eqn-t9da",
                f"public.{table}",
                block_size=block_size,
                skip_block_size_check=True,
            )

            captured = capsys.readouterr()
            clean_output = re.sub(
                r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", captured.out
            )
            match = re.search(r"diffs written out to (.+\.json)", clean_output.lower())
            assert match, "Diff file path not found in output"
            diff_file = match.group(1)

            with open(diff_file, "r") as f:
                diff_data = json.load(f)

            assert len(diff_data["diffs"]["n1/n2"]["n2"]) == len(
                block_boundaries
            ), f"Expected {len(block_boundaries)} diffs,"
            f" got {len(diff_data['diffs']['n1/n2']['n2'])}"

            for diff in diff_data["diffs"]["n1/n2"]["n2"]:
                assert (
                    diff["first_name"] == "Modified"
                ), "Expected first_name to be Modified"

            # Repair everything now
            cli.table_repair(
                "eqn-t9da", f"public.{table}", diff_file, source_of_truth="n1"
            )

        except Exception as e:
            pytest.fail(f"Test failed: {str(e)}")
