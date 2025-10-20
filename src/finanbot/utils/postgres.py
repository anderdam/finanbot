import logging

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# 🎯 Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)


class PostgresUtils:
    def __init__(self, host, port, user, password, database, schema="public"):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.schema = schema
        self._engine = None  # cache interno

    def get_connection_string(self):
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    @property
    def engine(self):
        if self._engine is None:
            self._engine = create_engine(
                self.get_connection_string(),
                connect_args={"options": f"-c search_path={self.schema}"},
            )
        return self._engine

    def test_connection(self):
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logging.info("✅ Conexão com PostgreSQL bem-sucedida.")
        except SQLAlchemyError as e:
            logging.error(f"❌ Falha na conexão: {e}")

    def create_schema_if_not_exists(self, schema_name):
        try:
            with self.engine.connect() as connection:
                # ⚠️ Interpolação direta — certifique-se que schema_name é seguro
                connection.execute(
                    text("CREATE SCHEMA IF NOT EXISTS :schema_name;"),
                    {"schema_name": schema_name},
                )
            logging.info(f"✅ Schema '{schema_name}' garantido no banco.")
        except SQLAlchemyError as e:
            logging.error(f"❌ Erro ao criar schema '{schema_name}': {e}")

    def save_dataframe(self, df: pd.DataFrame, table_name: str):
        try:
            with self.engine.connect() as connection:
                df.to_sql(table_name, connection, if_exists="append", index=False)
            logging.info(
                f"✅ Dados salvos na tabela '{table_name}' no schema '{self.schema}'."
            )
        except SQLAlchemyError as e:
            logging.error(f"❌ Erro ao salvar dados na tabela '{table_name}': {e}")

    def fetch_dataframe(self, query: str) -> pd.DataFrame:
        try:
            with self.engine.connect() as connection:
                df = pd.read_sql(query, connection)
            logging.info("✅ Dados carregados com sucesso.")
            return df
        except SQLAlchemyError as e:
            logging.error(f"❌ Erro ao executar query: {e}")
            return pd.DataFrame()

    def list_schemas(self):
        try:
            with self.engine.connect() as connection:
                result = connection.execute(
                    text("SELECT schema_name FROM information_schema.schemata;")
                )
                schemas = [row[0] for row in result]
            logging.info("✅ Schemas listados com sucesso.")
            return schemas
        except SQLAlchemyError as e:
            logging.error(f"❌ Erro ao listar schemas: {e}")
            return []

    def list_tables(self, schema_name):
        try:
            with self.engine.connect() as connection:
                result = connection.execute(
                    text(
                        """
                        SELECT table_name
                        FROM information_schema.tables
                        WHERE table_schema = :schema_name;
                    """
                    ),
                    {"schema_name": schema_name},
                )
                tables = [row[0] for row in result]
            logging.info(f"✅ Tabelas do schema '{schema_name}' listadas com sucesso.")
            return tables
        except SQLAlchemyError as e:
            logging.error(f"❌ Erro ao listar tabelas do schema '{schema_name}': {e}")
            return []


if __name__ == "__main__":
    from app.core.config import get_settings

    settings = get_settings()

    db = PostgresUtils(
        host=settings.postgres_host,
        port=settings.postgres_port,
        user=settings.postgres_user,
        password=settings.postgres_password,
        database=settings.postgres_db,
        schema="finance-tracker",  # or settings.schema if you add it
    )

    db.test_connection()
    print(db.list_schemas())
