#####################################################
#  Copyright 2022-2023 PGEDGE  All rights reserved. #
#####################################################

import sys, os, json, time, logging, datetime
import util, spock, random, meta, api, fire

try:
  import psycopg
except ImportError as e:
  util.exit_message("Missing 'psycopg' module from pip", 1)

def get_pg_connection(pg_v, db, usr):
  dbp = util.get_column("port", pg_v)
  if util.debug_lvl() > 0:
    util.message(f"get_pg_connection(): dbname={db}, user={usr}, port={dbp}", "debug")
  try:
    con = psycopg.connect(dbname=db, user=usr, host="127.0.0.1", port=dbp, autocommit=False)
  except Exception as e:
    util.exit_exception(e)
  return(con)


def install_pgbench(db, replication_set=None, pg=None):
  """Initialize pgBench data, Alter Tables, and add to replication_set"""
  pg_v = util.get_pg_v(pg)
  usr = util.get_user()  
  try:
    con = get_pg_connection(pg_v, db, usr)
    cur = con.cursor()
    os.system(f"{pg_v}{os.sep}bin{os.sep}pgbench -i {db}")
    cur.execute("ALTER TABLE pgbench_accounts ALTER COLUMN abalance SET (LOG_OLD_VALUE=true)")
    cur.execute("ALTER TABLE pgbench_branches ALTER COLUMN bbalance SET (LOG_OLD_VALUE=true)")
    cur.execute("ALTER TABLE pgbench_tellers ALTER COLUMN tbalance SET (LOG_OLD_VALUE=true);")
    con.commit()
    cur.close()
  except Exception as e:
    util.exit_exception(e)
  if replication_set:
    os.system(f"./nodectl spock repset-add-table {replication_set} 'pgbench_*' {db}")


def run_pgbench(db, rate, time, pg=None):
  """Run pgBench"""
  pg_v = util.get_pg_v(pg)
  os.system(f"{pg_v}{os.sep}bin{os.sep}pgbench -R {rate} -T {time} -n {db}")


def validate_pgbench(db, pg=None):
  """Validate pgBench"""
  pg_v = util.get_pg_v(pg)
  usr = util.get_user()  
  try:
    con = get_pg_connection(pg_v, db, usr)
    cur = con.cursor()
    cur.execute("SELECT SUM(tbalance) FROM pgbench_tellers;")
    v_sum = cur.fetchone()[0]
    cur.close()
  except Exception as e:
    util.exit_exception(e)
  util.exit_message(f"Sum of tbalance in pgbench_tellers= {v_sum}",0)


def uninstall_pgbench(db, pg=None):
  """Drop pgBench Tables"""
  pg_v = util.get_pg_v(pg)
  usr = util.get_user()
  try:
    con = get_pg_connection(pg_v, db, usr)
    cur = con.cursor()
    cur.execute("DROP TABLE pgbench_accounts")
    cur.execute("DROP TABLE pgbench_branches")
    cur.execute("DROP TABLE pgbench_tellers")
    cur.execute("DROP TABLE pgbench_history")
    con.commit()
    cur.close()
  except Exception as e:
    util.exit_exception(e)
  util.exit_message(f"Uninstalled pgBench from database: {db}",0)


def install_northwind(db, replication_set=None, country=None, pg=None):
  """Install northwind data, Alter tables, and add to repsets"""
  os.system(f"psql -f hub{os.sep}scripts{os.sep}sql{os.sep}northwind.sql {db}")
  if country:
    if country!='US' or country!='USA':
      out_of_country='USA'
    else:
      out_of_country='UK'
  pg_v = util.get_pg_v(pg)
  usr = util.get_user()  
  try:
    con = get_pg_connection(pg_v, db, usr)
    cur = con.cursor()
    cur.execute("ALTER TABLE northwind.products ALTER COLUMN units_in_stock SET (LOG_OLD_VALUE=true)")
    cur.execute("ALTER TABLE northwind.products ALTER COLUMN units_on_order SET (LOG_OLD_VALUE=true)")
    if country:
      cur.execute(f"UPDATE northwind.employees SET birth_date = NULL, address = NULL, city = NULL, region = NULL, \
                postal_code = NULL, home_phone = NULL, extension = NULL WHERE country = '{out_of_country}'")
    con.commit()
    cur.close()
  except Exception as e:
    util.exit_exception(e)
  if replication_set:
    os.system(f"./nodectl spock repset-add-table {replication_set} 'northwind.*' {db}")
  if country:
    os.system(f"./nodectl spock repset-remove-table {replication_set} 'northwind.employees' {db}")
    os.system(f"./nodectl spock repset-create {replication_set}_eu {db}")
    os.system(f"./nodectl spock repset-create {replication_set}_us {db}")
    os.system(f"./nodectl spock repset-add-table {replication_set}_us 'northwind.employees' {db}")
    os.system(f"./nodectl spock repset-add-table {replication_set}_eu 'northwind.employees' {db} --columns='employee_id, last_name, first_name, title, title_of_courtesy, hire_date, country, photo, notes, reports_to, photo_path'")


def run_northwind(db, offset, time, rate, pg=None):
  """Run Sample Queries to Create Orders in Northwind"""
  pg_v = util.get_pg_v(pg)
  usr = util.get_user()
  try:
    con = get_pg_connection(pg_v, db, usr)
    cur = con.cursor()
    cur.execute("SELECT MAX(order_id) FROM northwind.orders")
    mx_ooid = cur.fetchone()[0]
    cur.close()
  except Exception as e:
    util.exit_exception(e)

  ##t_end = time.time() + time
  ##while time.time() < t_end:
  v_order_id = mx_ooid + offset
  v_employee_id = random.randrange(9)

  v_order_date = datetime.date.today().strftime("%Y-%m-%d")
  v_required_date = datetime.date.today().replace(day=datetime.date.today().day + 5).strftime("%Y-%m-%d")
  v_shipped_date = datetime.date.today().replace(day=datetime.date.today().day + 2).strftime("%Y-%m-%d")

  offset_cust = random.randrange(91)
  try:
    con = get_pg_connection(pg_v, db, usr)
    cur = con.cursor()
    cur.execute(f"SELECT customer_id, contact_name, address, city, region, postal_code, country \
                FROM northwind.customers LIMIT 1 OFFSET {offset_cust}")
    data=cur.fetchone()
    v_customer_id, v_contact_name, v_address, v_city, v_region, v_postal_code, v_country = data[0],data[1],data[2],data[3],data[4],data[5],data[6]
    cur.close()
  except Exception as e:
    util.exit_exception(e)

  ship_via = random.randrange(6)
  freight = random.random() * 100
  print(f"INSERT INTO northwind.orders (order_id, customer_id, employee_id, order_date, required_date, \
        shipped_date, ship_via, freight, ship_name, ship_address, ship_city, ship_region, ship_postal_code, \
        ship_country)") 
  print(f"VALUES ({v_order_id}, {v_customer_id}, {v_employee_id}, {v_order_date}, {v_required_date}, \
        {v_shipped_date}, {ship_via}, {freight}, {v_contact_name}, {v_address}, {v_city}, {v_region}, \
            {v_postal_code}, {v_country})")

  offset_det = random.randrange(77)
  try:
    con = get_pg_connection(pg_v, db, usr)
    cur = con.cursor()
    cur.execute(f"SELECT product_id, unit_price, units_on_order, units_in_stock, reorder_level \
                FROM northwind.products LIMIT 1 OFFSET {offset_det}")
    data=cur.fetchone()
    v_product_id, v_unit_price, v_units_on_order, v_units_in_stock, v_reorder_level = data[0],data[1],data[2],data[3],data[4]
    cur.close()
  except Exception as e:
    util.exit_exception(e)

  v_quantity = random.randrange(130)
  v_discount = random.random() 
  print(f"INSERT INTO northwind.orders_details(order_id, product_id, unit_price, quantity, discount)")
  print(f"VALUES ({v_order_id}, {v_product_id}, {v_unit_price}, {v_quantity}, {v_discount})")
  v_units_on_order = v_units_on_order + v_quantity
  if v_units_in_stock < v_reorder_level:
    v_units_in_stock = v_units_in_stock + 100

  print(f"UPDATE northwind.products SET units_on_order = {v_units_on_order}, units_in_stock = {v_units_in_stock} \
        WHERE product_id = {v_product_id}")


def validate_northwind(db, pg=None):
  """Run Sample Queries to Create Orders in Northwind"""
  pg_v = util.get_pg_v(pg)
  usr = util.get_user()
  try:
    con = get_pg_connection(pg_v, db, usr)
    cur = con.cursor()
    cur.execute("SELECT SUM(units_on_order), SUM(units_in_stock) FROM northwind.products")
    data=cur.fetchone()
    sum_on_order, sum_in_stock = data[0],data[1]
    cur.close()
  except Exception as e:
    util.exit_exception(e)
  util.exit_message(f"  Sum of units on order: {sum_on_order}\n  Sum of units in stock: {sum_in_stock}",0)


def uninstall_northwind(db, pg=None):
  """Drop northwind data and schema"""
  pg_v = util.get_pg_v(pg)
  usr = util.get_user()
  try:
    con = get_pg_connection(pg_v, db, usr)
    cur = con.cursor()
    cur.execute("DROP SCHEMA northwind CASCADE")
    con.commit()
    cur.close()
  except Exception as e:
    util.exit_exception(e)
  util.exit_message(f"Uninstalled northwind from database: {db}",0)


if __name__ == '__main__':
  fire.Fire({
      'install-pgbench': install_pgbench,
      'run-pgbench': run_pgbench,
      'validate-pgbench': validate_pgbench,
      'uninstall-pgbench': uninstall_pgbench,
      'install-northwind': install_northwind,
      'run-northwind': run_northwind,
      'validate-northwind': validate_northwind,
      'uninstall-northwind': uninstall_northwind
      })
