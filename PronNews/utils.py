import snowflake.client


def get_snowflake_uuid():
    return snowflake.client.get_guid()
