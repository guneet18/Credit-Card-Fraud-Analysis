import os

api_key = os.getenv("OPENAI_API_KEY")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST", "localhost")  # default to localhost
db_port = os.getenv("DB_PORT", "5432")  # default to 5432
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
