import os
from dotenv import load_dotenv
from peewee import Model, PostgresqlDatabase

load_dotenv()


class Base(Model):
    class Meta:
        database = PostgresqlDatabase(
            os.getenv("PG_DATABASE_NAME"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT")
        )
