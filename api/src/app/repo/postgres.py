import json
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from globals import Globals
from utils.apiResponse import ApiResponse


def create_connection_pool(host: str, port: str, database: str, user: str, password: str, minconn: int = 1, maxconn: int = 10):
    """
    Creates a connection pool to the Postgres database.
    :param host: The host of the Postgres database.
    :param port: The port of the Postgres database.
    :param database: The database name of the Postgres database.
    :param user: The user of the Postgres database.
    :param password: The password of the Postgres database.
    :param minconn: The minimum number of connections in the connection pool.
    :param maxconn: The maximum number of connections in the connection pool.
    :return: Returns the connection pool.
    """
    connection_pool = None
    try:
        print("Creating Postgres connection...")
        connection_pool = SimpleConnectionPool(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            minconn=minconn,
            maxconn=maxconn,
            connect_timeout=1800
        )
        print("Postgres connection created successfully!")
    except psycopg2.Error as e:
        print(f"Error creating Postgres connection: {e}")
    except Exception as ex:
        print(f"Exception creating Postgres connection: {ex}")
    return connection_pool

connection_pool = create_connection_pool(
    host=Globals.pg_host,
    port=Globals.pg_port,
    database=Globals.pg_db,
    user=Globals.pg_user,
    password=Globals.pg_password,
    minconn=1,
    maxconn=10
)


pg_schema = Globals.pg_schema


analysis_insert_query = f"""INSERT INTO {pg_schema}."analysis_audit" (id, "text", created_at, user_email, flagged_text, analysed_entity, criticality)
                          VALUES(gen_random_uuid(), %s, CURRENT_TIMESTAMP, %s, %s, %s, %s);"""


anonymize_insert_query = f"""INSERT INTO {pg_schema}.anonymize_audit (id, original_text, anonymized_text, flagged_text, created_at, user_email, analysed_entity, criticality)
                            VALUES(gen_random_uuid(), %s, %s, %s, CURRENT_TIMESTAMP, %s, %s, %s);"""

chat_log_insert_query = f'''INSERT INTO {pg_schema}.chat_log (id, created_at, user_email, "text")
                             VALUES(gen_random_uuid(), CURRENT_TIMESTAMP, %s, %s);'''
get_org_query = f'''SELECT * FROM {pg_schema}.organisation;'''


def get_filter_conditions(filter_dict):
    """
    Gets the filter conditions for the SQL query.
    :param filter_dict: The filter dictionary.
    :return: Returns the filter conditions.
    """
    filter_conditions = ""
    if (filter_dict['filterOperator'] == 'contains'):
        filter_conditions = f"{filter_dict['filterField']} like '%{filter_dict['filterValue']}%'"
    elif (filter_dict['filterOperator'] == 'equals'):
        filter_conditions = f"{filter_dict['filterField']}='{filter_dict['filterValue']}'"
    elif (filter_dict['filterOperator'] == 'startsWith'):
        filter_conditions = f"{filter_dict['filterField']} like '{filter_dict['filterValue']}%'"
    elif (filter_dict['filterOperator'] == 'endsWith'):
        filter_conditions = f"{filter_dict['filterField']} like '%{filter_dict['filterValue']}'"
    elif (filter_dict['filterOperator'] == 'isEmpty'):
        filter_conditions = f"{filter_dict['filterField']} is NULL"
    elif (filter_dict['filterOperator'] == 'isAnyOf'):
        if len(filter_dict['filterValue']) > 0:
            values = ",".join(
                [f"'{value}'" for value in filter_dict['filterValue']])
            filter_conditions = f"{filter_dict['filterField']} in ({values})"

    return filter_conditions


class SqlAudits:
    """
    Class to handle all the SQL queries for the audits.
    """
    def insert_analysis_audits(text, user_email, flagged_text, analysed_entity, criticality):
        """
        Inserts the analysis audit into the database.
        :param text: The text that was analysed.
        :param user_email: The email of the user that performed the analysis.
        :param flagged_text: The text that was flagged.
        :param analysed_entity: The entity that was analysed.
        :param criticality: The criticality of the flagged text.
        :return: Returns nothing.
        """
        global connection_pool
        if connection_pool:
            conn = connection_pool.getconn()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    analysis_insert_query,
                    (text, user_email, flagged_text, analysed_entity, criticality),
                )
            except Exception as ex:
                print(f"Exception while inserting analysis audit: {ex}")
            finally:
                connection_pool.putconn(conn)


    def insert_anonymize_audits(original_text, anonymized_text, flagged_text, user_email, analysed_entity, criticality):
        """
        Inserts the anonymize audit into the database.
        :param original_text: The original text.
        :param anonymized_text: The anonymized text.
        :param flagged_text: The text that was flagged.
        :param user_email: The email of the user that performed the analysis.
        :param analysed_entity: The entity that was analysed.
        :param criticality: The criticality of the flagged text.
        :return: Returns nothing.
        """
        global connection_pool
        if connection_pool:
            conn = connection_pool.getconn()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    anonymize_insert_query, (original_text, anonymized_text,
                                            flagged_text, user_email, analysed_entity, criticality)
                )
            except Exception as ex:
                print(f"Exception while inserting anonymize audit: {ex}")
            finally:
                connection_pool.putconn(conn)


    def insert_chat_log(user_email, text):
        """
        Inserts the chat log into the database.
        :param user_email: The email of the user that performed the analysis.
        :param text: The text that was sent.
        :return: Returns nothing.
        """
        global connection_pool
        if connection_pool:
            conn = connection_pool.getconn()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    chat_log_insert_query, (user_email, text)
                )
            except Exception as ex:
                print(f"Exception while inserting chat log: {ex}")
            finally:
                connection_pool.putconn(conn)


    def get_chat_log():
        """
        Gets the chat logs from the database.
        :return: Returns the chat logs as a json object.
        """
        data = None
        global connection_pool
        if connection_pool:
            conn = connection_pool.getconn()
            try:
                cursor = conn.cursor()
                cursor.execute(f'''SELECT * FROM {pg_schema}.chat_log''')
                data = cursor.fetchall()
            except Exception as ex:
                print(f"Exception while getting chat log: {ex}")
            finally:
                connection_pool.putconn(conn)
        return json.dumps(data, indent=4, sort_keys=True, default=str)
    
    # Admin APIs below
    # def get_org():
    #     """
    #     Gets the organisation details from the database.
    #     :return: Returns the organisation details as a json object.
    #     """
    #     data = None
    #     global connection_pool
    #     if connection_pool:
    #         conn = connection_pool.getconn()
    #         try:
    #             cursor = conn.cursor()
    #             cursor.execute(get_org_query)
    #             data = cursor.fetchone()
    #         except Exception as ex:
    #             print(f"Exception while getting organisation details: {ex}")
    #         finally:
    #             connection_pool.putconn(conn)
    #     return json.dumps(data, indent=4, sort_keys=True, default=str)


    # def save_org(orgdata):
    #     """
    #     Saves the organisation details into the database.
    #     :param orgdata: dict containing the organisation details.
    #     :return: Returns the response of the API as a json object.
    #     """
    #     apiResponse = ""
    #     global connection_pool
    #     if connection_pool:
    #         conn = connection_pool.getconn()
    #         try:
    #             cursor = conn.cursor()
    #             cursor.execute(f"SELECT * FROM {pg_schema}.organisation")
    #             empty_records = cursor.fetchone()
    #             if not empty_records:
    #                 query = f'''INSERT INTO {pg_schema}.organisation (name, email, details, openai_key, created_at) VALUES (%s,%s, %s, %s, current_timestamp)'''
    #                 cursor.execute(
    #                     query, (orgdata['name'], orgdata['email'], orgdata['details'], orgdata['openai_key']))
    #                 apiResponse = "{'success':True}"
    #             else:
    #                 query = f"UPDATE {pg_schema}.organisation SET name = %s, email = %s, details = %s, openai_key = %s, created_at = current_timestamp WHERE id = %s"
    #                 cursor.execute(query, (orgdata['name'], orgdata['email'],
    #                             orgdata['details'], orgdata['openai_key'], empty_records[0]))
    #                 apiResponse = "{'success':True}"
    #         except Exception as e:
    #             print("Exception while saving organisation details: ", e)
    #             apiResponse = "Error: {}".format(str(e))
    #         finally:
    #             connection_pool.putconn(conn)
    #     return json.dumps(apiResponse)


    def get_list_query(table, sort, range_, filter_):
        """
        Gets the list of records from the database.
        :param table: The table name.
        :param sort: The sort order.
        :param range_: The range of records to be fetched.
        :param filter_: The filter to be applied.
        :return: Returns the list of records.
        """
        response=ApiResponse()
        data = []
        global connection_pool
        if connection_pool:
            conn = connection_pool.getconn()
            try:
                cursor = conn.cursor()
                query = f"SELECT * FROM {table}"
                filter_dict = eval(filter_)
                if len(filter_dict) != 0:
                    filter_conditions = get_filter_conditions(filter_dict)
                    if (filter_conditions != ''):
                        query += f" WHERE {filter_conditions}"
                if sort:
                    sort_list = eval(sort)
                    sort_str = " ".join(sort_list)
                    query += f" ORDER BY {sort_str}"
                if range_:
                    range_list = eval(range_)
                    start = range_list[0]
                    end = range_list[1]
                    query += f" OFFSET {start} LIMIT {end - start + 1}"
                cursor.execute(query)
                rows = cursor.fetchall()
                data = [dict(zip([column[0] for column in cursor.description], row))
                        for row in rows]
                response.update(True,"Successfully retrieved the data",data)
            except Exception as ex:
                print(f"Exception while getting list: {ex}")
                response.update(False,"Error in retrieving the data",None)
            finally:
                connection_pool.putconn(conn)
        return response.json()


    def get_one_query(table, id):
        """
        Gets the single record from the database.
        :param table: The table name.
        :param id: The id of the record to be fetched.
        :return: Returns the single record.
        """
        response=ApiResponse()
        row_dict = {}
        global connection_pool
        if connection_pool:
            conn = connection_pool.getconn()
            try:
                cursor = conn.cursor()
                query = f"SELECT * FROM {table} WHERE id=%s"
                cursor.execute(query, (id,))
                row = cursor.fetchone()
                columns = [desc[0] for desc in cursor.description]
                for i in range(len(columns)):
                    row_dict[columns[i]] = row[i]
                
                response.update(True,"Successfully retrieved the data",row_dict)
            except Exception as ex:
                print(f"Exception while getting query: {ex}")
                response.update(False,"Error in retrieving the data",None)
            finally:
                connection_pool.putconn(conn)
        return response.json()


    def count_query(table, filter_):
        """
        Gets the count of records from the database with filters.
        :param table: The table name.
        :param filter_: The filter to be applied.
        :return: Returns the count of records.
        """
        response=ApiResponse()
        
        count = 0
        global connection_pool
        if connection_pool:
            conn = connection_pool.getconn()
            try:
                cursor = conn.cursor()
                query = f"SELECT count(*) FROM {table}"
                filter_dict = eval(filter_)
                if len(filter_dict) != 0:
                    filter_conditions = get_filter_conditions(filter_dict)
                    if (filter_conditions != ''):
                        query += f" WHERE {filter_conditions}"
                cursor.execute(query)
                count = cursor.fetchone()[0]
                response.update(True,"Successfully retrieved the data",count)
                
            except Exception as ex:
                print(f"Exception while getting count of query: {ex}")
                response.update(False,"Error in retrieving the data",None)
            finally:
                connection_pool.putconn(conn)
        return response.json()


    # def create_query(table, data):
    #     """
    #     Creates a new record in the database.
    #     :param table: The table name.
    #     :param data: The data to be inserted.
    #     :return: Returns the newly created record.
    #     """
    #     result = {}
    #     global connection_pool
    #     if connection_pool:
    #         conn = connection_pool.getconn()
    #         try:
    #             cursor = conn.cursor()
    #             keys = ", ".join(data.keys())
    #             values_template = ", ".join(["%s" for _ in data.values()])
    #             values = tuple(data.values())

    #             query = f"INSERT INTO {table} ({keys}) VALUES ({values_template}) RETURNING id"
    #             cursor.execute(query, values)

    #             new_id = cursor.fetchone()[0]
    #             result = SqlAudits.get_one_query(table, new_id)
    #         except Exception as ex:
    #             print(f"Exception while creating query: {ex}")
    #         finally:
    #             connection_pool.putconn(conn)
    #     return result


    # def update_query(table, id, data):
    #     """
    #     Updates the record in the database.
    #     :param table: The table name.
    #     :param id: The id of the record to be updated.
    #     :param data: The data to be updated.
    #     :return: Returns the updated record.
    #     """
    #     result = {}
    #     global connection_pool
    #     if connection_pool:
    #         conn = connection_pool.getconn()
    #         try:
    #             cursor = conn.cursor()
    #             set_list = [f"{key}=%s" for key in data.keys()]
    #             set_str = ", ".join(set_list)
    #             values = tuple(data.values()) + (id,)

    #             query = f"UPDATE {table} SET {set_str} WHERE id=%s"
    #             cursor.execute(query, values)
    #             result = SqlAudits.get_one_query(table, id)
    #         except Exception as ex:
    #             print(f"Exception while updating query: {ex}")
    #         finally:
    #             connection_pool.putconn(conn)
    #     return result


    #Get rules name from provider
    def get_all_enabled_entities(table, provider_name):
        """
        Gets the list of enabled entities from the database.
        :param table: The table name.
        :param provider_name: The provider name.
        :return: Returns the list of enabled entities.
        """
        enabled_entities = []
        global connection_pool
        if connection_pool:
            conn = connection_pool.getconn()
            try:
                cursor = conn.cursor()
                query = f"SELECT name FROM {table} where provider='{provider_name}' and is_active = true"
                cursor.execute(query, (id,))
                count=cursor.fetchall()
                enabled_entities = [item[0] for item in count]
            except Exception as ex:
                print(f"Exception while getting enabled entities: {ex}")
            finally:
                connection_pool.putconn(conn)
        return enabled_entities