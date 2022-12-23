####################################################################
########       Copyright (c) 2016-2018 BigSQL            ###########
####################################################################

import pgpasslib

extra_args = {'timeout': 20}
try:
    import psycopg2 as pgclient
    extra_args={'connect_timeout':20}
except ImportError as e:
    import pg8000 as pgclient

class PgInstance(object):
    """
    PgInstance Class is used to connect to the postgres instance.
    """

    def __init__(self, host, username, dbname, port, password=None):
        self.host = host
        self.username = username
        self.dbname = dbname
        self.port = port
        self.conn = None
        self.password = password

    def connect(self):
        """
        It establishes database connection using credentials
        which are set during initialization.
        If password is not provided, will retreive the password from
        .pgpass file using pgpasslib
        """
        password = self.password
        if self.password is None:
            password = pgpasslib.getpass(dbname=self.dbname,
                                         user=self.username,
                                         host=self.host,
                                         port=self.port)
        self.conn = pgclient.connect(database=self.dbname,
                                   user=self.username,
                                   host=self.host,
                                   port=self.port,
                                   password=password,
                                   **extra_args
                                   )
        self.conn.autocommit = True

    def get_cluster_size(self):
        """
        Function to get the cluster size of the connected pg instance.
        :return: Returns the cluster size in human readable format (Eg : 14 GB)
        """
        query = """select pg_size_pretty(sum(pg_database_size(datname::text))::bigint)
                    from pg_database where datname not in ('template0','template1')"""
        cursor = self.conn.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        size = result[0]
        cursor.close()
        return size

    def get_uptime(self):
        """
        Function to get the up time of the connected pg instance.
        :return: It returns the datetime format
        """
        query = "SELECT now() - pg_postmaster_start_time()"
        cursor = self.conn.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        up_time = result[0]
        cursor.close()
        return up_time

    def get_database_list(self):
        """
        Function to get the list of database available in connected pg instance
        excluding the ('template0','template1').
        :return: It returns the list of database and their size.
        """
        query = """SELECT d.datname,
                          cast (round((pg_database_size(d.datname::text)/1024.0)/1024.0, 1) as float8) as size,
                          u.usename as owner
                    FROM pg_database d
                    JOIN pg_user u ON (d.datdba = u.usesysid)
                   WHERE d.datname NOT IN ('template0','template1')
                   ORDER BY 1"""
        cursor = self.conn.cursor()
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        result = []
        for res in cursor:
            result.append(dict(zip(columns, res)))
        cursor.close()
        return result

    def get_active_connections(self):
        """
        Function to get number of active connections.
        :return: It returns the number of active connection with
        max connections (Eg: 12/100 )
        """
        query = """WITH act_base as (
                    SELECT unnest(ARRAY['idle','active','idle in transaction']) as "state" )
                    SELECT ab.state, count(sa.state)
                    FROM act_base ab LEFT OUTER JOIN pg_stat_activity sa ON ab.state = sa.state
                    GROUP BY ab.state
                    UNION ALL
                    SELECT 'total', count(1) FROM pg_stat_activity
                    UNION ALL
                    SELECT 'max', setting::bigint FROM pg_settings WHERE name='max_connections'"""
        cursor = self.conn.cursor()
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        result = []
        for res in cursor:
            result.append(dict(zip(columns, res)))
        cursor.close()
        return result

    def get_current_activity(self):
        """
        Function to get the current activity from the instance.
        :return: It returns the list of current activities
        excluding the pid of this query.
        """
        query = """SELECT datname, state, pid, usename, client_addr::varchar,
            to_char(backend_start::timestamp(0),'MM-DD-YYYY HH24:MI:SS') as backend_start,
            to_char(xact_start::timestamp(0),'MM-DD-YYYY HH24:MI:SS') as xact_start,
            justify_interval((clock_timestamp() - query_start)::interval(0))::varchar as query_time,
            query
            FROM pg_stat_activity
            ORDER BY 8 DESC"""
        cursor = self.conn.cursor()
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        result = []
        for res in cursor:
            result.append(dict(zip(columns, res)))
        cursor.close()
        return result

    def get_tables(self):
        """
        Function to get the list of tables from database connected.
        :return: It returns the list of current tables with table size,
        index size and estimated rows.
        """
        query = """SELECT t.schemaname, t.relname, c.reltuples::bigint,
            pg_size_pretty(pg_total_relation_size(quote_ident(t.schemaname) || '.' || quote_ident(t.relname))) tablesize,
            pg_size_pretty(sum(pg_total_relation_size(quote_ident(i.schemaname) || '.' || quote_ident(i.indexrelname)))) indexsize,
            pg_total_relation_size(quote_ident(t.schemaname) || '.' || quote_ident(t.relname)) t_bytes,
            sum(pg_total_relation_size(quote_ident(i.schemaname) || '.' || quote_ident(i.indexrelname) )) i_bytes
            FROM  pg_stat_user_tables as t, pg_stat_user_indexes  as i, pg_class as c
            WHERE t.relid = i.relid AND c.relfilenode=t.relid
            GROUP BY t.schemaname, t.relname,c.reltuples 
            ORDER BY 1,2,3,6,7 DESC"""
        cursor = self.conn.cursor()
        cursor.execute(query)
        columns = ['schema', 'table', 'rows', 'tablesize', 'indexsize']
        result = []
        for res in cursor:
            result.append(dict(zip(columns, res)))
        cursor.close()
        return result

    def get_indexes(self, table=None):
        """
        Function to get the list of indexes on a table if provided else
        all the indexes from the database
        :param table: tablename for which you want to get the list of indexes (optional)
        :return: Returns the list of indexes with the size.
        """
        query = """SELECT schemaname, relname, indexrelname,
            pg_size_pretty(pg_total_relation_size(quote_ident(schemaname) || '.' || quote_ident(indexrelname))) indexsize,
            pg_total_relation_size(quote_ident(schemaname) || '.' || quote_ident(indexrelname) ) i_bytes
            FROM pg_stat_user_indexes"""
        if table:
            query += " where relname='" + table + "'"
        query += " ORDER BY 1,2,3,4 DESC"
        cursor = self.conn.cursor()
        cursor.execute(query)
        columns = ['schema', 'table', 'indexname', 'indexsize']
        result = []
        for res in cursor:
            result.append(dict(zip(columns, res)))
        cursor.close()
        return result

    def get_extensions(self):
        """
        Function to get the list of extensions available in the cluster.
        :return: Returns the list of extensions with the installed status.
        """
        query = "select * from pg_available_extension_versions"
        cursor = self.conn.cursor()
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        result = []
        for res in cursor:
            result.append(dict(zip(columns, res)))
        cursor.close()
        return result

    def get_users(self):
        """
        Function to get the list of users in the connected pg instance.
        """
        query = "select * from pg_user"
        cursor = self.conn.cursor()
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        result = []
        for res in cursor:
            result.append(dict(zip(columns, res)))
        cursor.close()
        return result

    def get_version(self):
        """
        Function to get the server version.
        :return: It returns server version.
        """
        query = "SELECT version()"
        cursor = self.conn.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        server_version = result[0]
        cursor.close()
        return server_version

    def get_per_table_stats(self):
        """
        Function to get per table stats.
        :return: It returns per table stats
        """
        query = """SELECT relname, n_tup_ins, n_tup_upd, n_tup_del,
                          seq_scan, idx_scan
                     FROM pg_stat_user_tables
                    ORDER BY (n_tup_ins + n_tup_del + n_tup_upd + seq_scan + idx_scan) DESC limit 10"""
        cursor = self.conn.cursor()
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        result = []
        for res in cursor:
            result.append(dict(zip(columns, res)))
        cursor.close()
        return result

    def get_cluster_stats(self):
        """
        Function to get the cluster metrics .
        :return: Returns the cluster metrics data.
        """
        query = """SELECT sum(numbackends::float8) as "num_backends",
                          sum(xact_commit::float8) as "xact_commit",
                          sum(xact_rollback::float8) as "xact_rollback",
                          sum(blks_read::float8) as "blks_read",
                          sum(blks_hit::float8) as "blks_hit",
                          sum(tup_fetched::float8) as "tup_fetched",
                          sum(tup_inserted::float8) as "tup_inserted",
                          sum(tup_updated::float8) as "tup_updated",
                          sum(tup_deleted::float8) as "tup_deleted"
                     FROM pg_stat_database"""
        cursor = self.conn.cursor()
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        result = []
        for res in cursor:
            result.append(dict(zip(columns, res)))
        cursor.close()
        return result

    def get_tuples_stats(self):
        """
        Function to get the tuples metrics .
        :return: Returns the tuples metrics data.
        """
        query = """SELECT sum(n_tup_ins) as "n_tup_ins",
                          sum(n_tup_upd) as "n_tup_upd",
                          sum(n_tup_del) as "n_tup_del",
                          sum(seq_scan) as "seq_scan",
                          sum(idx_scan) as "idx_scan"
                     FROM pg_stat_user_tables"""
        cursor = self.conn.cursor()
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        result = []
        for res in cursor:
            result.append(dict(zip(columns, res)))
        cursor.close()
        return result

    def get_pg_settings(self):
        """
        Function to get the postgres settings.
        :return: Returns the settings of a cluster.
        """
        query = "select category, name, setting, short_desc from pg_settings order by category"
        cursor = self.conn.cursor()
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        result = []
        for res in cursor:
            result.append(dict(zip(columns, res)))
        cursor.close()
        return result

    def get_raw_pg_settings(self):
        query = "select name, setting from pg_settings"
        cursor = self.conn.cursor()
        cursor.execute(query)

        #columns = [desc[0] for desc in cursor.description]
        result = {}
        for res in cursor:
         #   result.append(dict(zip(columns, res)))
         result[res[0]] = res[1]
        cursor.close()
        return result

    def is_extension_installed(self,extension):
        """
        Function to check if the extension is exists in the database.
        :return: It returns extension version if available.
        """
        query = "select extname, extversion from pg_extension where extname='%s'" % extension
        cursor = self.conn.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        ext_version=None
        if result:
            ext_version = result[1]
        cursor.close()
        return ext_version

    def create_extension(self,extension):
        """
        Function to create extension in the database.
        :return: It returns true if extension is created successfully.
        """
        query = "create extension %s" % extension
        cursor = self.conn.cursor()
        cursor.execute(query)
        cursor.close()
        return True

    def get_shared_libaries(self):
        """
        Function to get the shared libraries from the cluster
        :return: shared libraries
        """
        query="show shared_preload_libraries"
        cursor = self.conn.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        shared_libs=None
        if result:
            shared_libs = result[0]
        cursor.close()
        return shared_libs

    def add_shared_library(self,p_library):
        """
        Function to add library to shared_preload_libraries.
        :return: It returns true if library is added successfully.
        """
        existing_librarires=self.get_shared_libaries()
        library_to_add=p_library
        if existing_librarires:
            library_to_add = "{0}, {1}".format(existing_librarires, p_library)

        query = "alter system set shared_preload_libraries=%s" % library_to_add
        cursor = self.conn.cursor()
        cursor.execute(query)
        cursor.close()
        return True

    def remove_shared_library(self,p_library):
        """
        Function to remove library from shared_preload_libraries.
        :return: It returns true if library is removed successfully.
        """
        existing_librarires=self.get_shared_libaries()
        library_to_add=p_library
        if existing_librarires:
            if existing_librarires.find(p_library)>=-1:
                return True
            libs_added=existing_librarires.split(",")
            lib_to_add=[]
            for lib in libs_added:
                if p_library!=lib.strip():
                    pass
                lib_to_add.append(lib.strip())
            library_to_add = ",".join(lib_to_add)

        query = "alter system set shared_preload_libraries=%s" % library_to_add
        cursor = self.conn.cursor()
        cursor.execute(query)
        cursor.close()
        return True

    def config(self, name, val):
        """
        Function to change the config parameters of postgres instance.
        :param name: setting name
        :param val: setting value
        :return: True
        """
        self.conn.autocommit = True
        query = "ALTER SYSTEM SET {0}={1}".format(name, val)
        cursor = self.conn.cursor()
        cursor.execute(query)
        cursor.close()
        return True

    def reset_config(self, name):
        """
        Function to reset the config parameters of postgres instance.
        :param name: setting name
        :return: True
        """
        self.conn.autocommit=True
        query = "ALTER SYSTEM RESET {0}".format(name)
        cursor = self.conn.cursor()
        cursor.execute(query)
        cursor.close()
        return True

    def reload_config(self):
        """
        Function to reload the postgres config.
        :return: True
        """
        query = "SELECT * from pg_reload_conf()"
        cursor = self.conn.cursor()
        cursor.execute(query)
        cursor.close()
        return True

    def restart_required(self, name=None, list_params = []):
        """
        Function to check if any params are waiting for restart.
        :param name: setting name to check if restart required
        :param list_params: muliple settings name to check if restart required
        :return: list of params waiting for restart
        """
        self.reload_config()
        query = "SELECT name from pg_settings WHERE pending_restart=true"
        if name:
            query = "SELECT name from pg_settings WHERE pending_restart=true and name='{0}'".format(name)
        elif len(list_params)>0:
            query = "SELECT name from pg_settings WHERE pending_restart=true and name in {0}".format(tuple(list_params))
        cursor = self.conn.cursor()
        result = cursor.execute(query)
        params = []
        for cur in cursor:
            params.append(str(cur[0]))
        cursor.close()
        return params

    def get_config_value(self, name):
        """
        Function to get the postgres config value for given setting.
        :param name: setting name to check in the pg_settings
        :return: True
        """
        query = "SELECT name, setting, reset_val from pg_settings WHERE name='{0}'".format(name)
        cursor = self.conn.cursor()
        result = cursor.execute(query)
        final_result = cursor.fetchone()
        cursor.close()
        return final_result

    def close(self):
        self.conn.close()
