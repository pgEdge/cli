#####################################################
#  Copyright 2022-2024 PGEDGE  All rights reserved. #
#####################################################

import sys, os, json, time, logging, datetime, random, time
import util, spock, meta, api, fire


def pgbench_install(db, replication_set=None, pg=None):
    """Initialize pgBench data, Alter Tables, and add to replication_set"""
    pg_v = util.get_pg_v(pg)
    pg = pg_v.replace("pg", "")
    usr = util.get_user()
    try:
        con = util.get_pg_connection(pg_v, db, usr)
        cur = con.cursor()
        pgbench_cmd = '"pgbench --initialize --scale=1 ' + str(db) + '"'
        util.echo_cmd(f"./nc pgbin " + str(pg) + " " + pgbench_cmd)
        cur.execute(
            "ALTER TABLE pgbench_accounts ALTER COLUMN abalance SET (LOG_OLD_VALUE=true)"
        )
        cur.execute(
            "ALTER TABLE pgbench_branches ALTER COLUMN bbalance SET (LOG_OLD_VALUE=true)"
        )
        cur.execute(
            "ALTER TABLE pgbench_tellers ALTER COLUMN tbalance SET (LOG_OLD_VALUE=true);"
        )
        con.commit()
        cur.close()
    except Exception as e:
        util.exit_exception(e)
    if replication_set:
        os.system(
            f"./nodectl spock repset-add-table {replication_set} 'pgbench_*' {db}"
        )


def pgbench_run(db, Rate, Time, pg=None):
    """Run pgBench"""
    pg_v = util.get_pg_v(pg)
    pg = pg_v.replace("pg", "")
    pgbench_cmd = f'"pgbench -R {Rate} -T {Time} -n {db}"'
    util.echo_cmd(f"./nc pgbin " + str(pg) + " " + pgbench_cmd)


def pgbench_validate(db, pg=None):
    """Validate pgBench"""
    pg_v = util.get_pg_v(pg)
    usr = util.get_user()
    try:
        con = util.get_pg_connection(pg_v, db, usr)
        cur = con.cursor()
        cur.execute("SELECT SUM(tbalance) FROM pgbench_tellers;")
        v_sum = cur.fetchone()[0]
        cur.close()
    except Exception as e:
        util.exit_exception(e)
    util.exit_message(f"Sum of tbalance in pgbench_tellers= {v_sum}", 0)


def pgbench_remove(db, pg=None):
    """Drop pgBench Tables"""
    pg_v = util.get_pg_v(pg)
    usr = util.get_user()
    try:
        con = util.get_pg_connection(pg_v, db, usr)
        cur = con.cursor()
        cur.execute("DROP TABLE IF EXISTS pgbench_accounts CASCADE")
        cur.execute("DROP TABLE IF EXISTS pgbench_branches CASCADE")
        cur.execute("DROP TABLE IF EXISTS pgbench_tellers  CASCADE")
        cur.execute("DROP TABLE IF EXISTS pgbench_history  CASCADE")
        con.commit()
        cur.close()
    except Exception as e:
        util.exit_exception(e)
    util.exit_message(f"Dropped pgBench tables from database: {db}", 0)


def northwind_install(db, replication_set=None, pg=None):
    """Install northwind data, Alter tables, and add to repsets"""
    pg_v = util.get_pg_v(pg)

    sql_file = f"hub{os.sep}scripts{os.sep}sql{os.sep}northwind.sql"
    os.system(f"./nodectl psql -f {sql_file} {db}")

    usr = util.get_user()
    try:
        con = util.get_pg_connection(pg_v, db, usr)
        cur = con.cursor()
        cur.execute(
            "ALTER TABLE northwind.products ALTER COLUMN units_in_stock SET (LOG_OLD_VALUE=true)"
        )
        cur.execute(
            "ALTER TABLE northwind.products ALTER COLUMN units_on_order SET (LOG_OLD_VALUE=true)"
        )
        con.commit()
        cur.close()
    except Exception as e:
        util.exit_exception(e)

    if replication_set:
        os.system(
            f"./nodectl spock repset-add-table {replication_set} 'northwind.*' {db}"
        )


def northwind_run(db, offset, Rate=2, Time=10, pg=None):
    """Run Sample Queries to Create Orders in Northwind"""

    print(f"db={db}, offset={offset}, Rate={Rate}, Time={Time}\n")

    pg_v = util.get_pg_v(pg)
    usr = util.get_user()
    try:
        con = util.get_pg_connection(pg_v, db, usr)
        cur = con.cursor()
        cur.execute("SELECT MAX(order_id) FROM northwind.orders")
        mx_ooid = cur.fetchone()[0]
        cur.close()
    except Exception as e:
        util.exit_exception(e)
    v_order_id = mx_ooid + offset

    k = 0
    start_t = time.time()
    while True:
        k = k + 1
        run_t = time.time() - start_t
        expected_t = (k / Rate) + start_t

        current_t = time.time()
        if current_t > (start_t + Time):
            util.exit_message(f"Finished running Northwind App for {Time} seconds", 0)

        delay = expected_t - current_t
        if delay > 0:
            time.sleep(delay)

        v_employee_id = random.randrange(9) + 1

        v_order_date = datetime.date.today().strftime("%Y-%m-%d")
        v_required_date = (datetime.date.today() + datetime.timedelta(days=5)).strftime(
            "%Y-%m-%d"
        )
        v_shipped_date = (datetime.date.today() + datetime.timedelta(days=2)).strftime(
            "%Y-%m-%d"
        )

        offset_cust = random.randrange(91) + 1

        con = util.get_pg_connection(pg_v, db, usr)
        try:
            cur = con.cursor()
            cur.execute(
                f"SELECT customer_id, contact_name, address, city, region, postal_code, country \
                FROM northwind.customers LIMIT 1 OFFSET {offset_cust}"
            )
            data = cur.fetchone()
            if data:
                (
                    v_customer_id,
                    v_contact_name,
                    v_address,
                    v_city,
                    v_region,
                    v_postal_code,
                    v_country,
                ) = (data[0], data[1], data[2], data[3], data[4], data[5], data[6])
            cur.close()
        except Exception as e:
            util.exit_exception(e)

        ship_via = random.randrange(6) + 1
        freight = random.random() * 100
        v_address = v_address.replace("'", "''")
        try:
            cur = con.cursor()
            cur.execute(
                f"INSERT INTO northwind.orders (order_id, customer_id, employee_id, order_date, required_date, \
        shipped_date, ship_via, freight, ship_name, ship_address, ship_city, ship_region, ship_postal_code, \
        ship_country) VALUES ({v_order_id}, '{v_customer_id}', {v_employee_id}, '{v_order_date}', '{v_required_date}', \
        '{v_shipped_date}', {ship_via}, {freight}, '{v_contact_name}', '{v_address}', '{v_city}', '{v_region}', \
            '{v_postal_code}', '{v_country}')"
            )
            con.commit()
            cur.close()
        except Exception as e:
            util.exit_exception(e)

        offset_det = random.randrange(77)
        try:
            cur = con.cursor()
            cur.execute(
                f"SELECT product_id, unit_price, units_on_order, units_in_stock, reorder_level \
                FROM northwind.products LIMIT 1 OFFSET {offset_det}"
            )
            data = cur.fetchone()
            (
                v_product_id,
                v_unit_price,
                v_units_on_order,
                v_units_in_stock,
                v_reorder_level,
            ) = (data[0], data[1], data[2], data[3], data[4])
            cur.close()
        except Exception as e:
            util.exit_exception(e)

        v_quantity = random.randrange(130)
        v_discount = random.random()
        try:
            con = util.get_pg_connection(pg_v, db, usr)
            cur = con.cursor()
            cur.execute(
                f"INSERT INTO northwind.order_details(order_id, product_id, unit_price, quantity, discount) \
                VALUES ({v_order_id}, {v_product_id}, {v_unit_price}, {v_quantity}, {v_discount})"
            )
            v_units_on_order = v_units_on_order + v_quantity
            if v_units_in_stock < v_reorder_level:
                v_units_in_stock = v_units_in_stock + 100
            cur.execute(
                f"UPDATE northwind.products SET units_on_order = {v_units_on_order}, units_in_stock = {v_units_in_stock} \
        WHERE product_id = {v_product_id}"
            )
            con.commit()
            cur.close()
        except Exception as e:
            util.exit_exception(e)
        print(f"Placed order {k} with order_id = {v_order_id}")
        v_order_id = v_order_id + 10


def northwind_validate(db, pg=None):
    """Validate running sums in the Northwind products table"""
    pg_v = util.get_pg_v(pg)
    usr = util.get_user()
    try:
        con = util.get_pg_connection(pg_v, db, usr)
        cur = con.cursor()
        cur.execute(
            "SELECT SUM(units_on_order), SUM(units_in_stock) FROM northwind.products"
        )
        data = cur.fetchone()
        sum_on_order, sum_in_stock = data[0], data[1]
        cur.close()
    except Exception as e:
        util.exit_exception(e)
    util.exit_message(
        f"  Sum of units on order: {sum_on_order}\n  Sum of units in stock: {sum_in_stock}",
        0,
    )


def northwind_remove(db, pg=None):
    """Drop northwind schema"""
    pg_v = util.get_pg_v(pg)
    usr = util.get_user()
    try:
        con = util.get_pg_connection(pg_v, db, usr)
        cur = con.cursor()
        cur.execute("DROP SCHEMA northwind CASCADE")
        con.commit()
        cur.close()
    except Exception as e:
        util.exit_exception(e)
    util.exit_message(f"Dropped northwind schema from database: {db}", 0)


if __name__ == "__main__":
    fire.Fire(
        {
            "pgbench-install": pgbench_install,
            "pgbench-run": pgbench_run,
            "pgbench-validate": pgbench_validate,
            "pgbench-remove": pgbench_remove,
            "northwind-install": northwind_install,
            "northwind-run": northwind_run,
            "northwind-validate": northwind_validate,
            "northwind-remove": northwind_remove,
        }
    )
