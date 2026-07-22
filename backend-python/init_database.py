import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

root = Path(__file__).resolve().parent.parent
load_dotenv(root / '.env')
url = os.getenv('DATABASE_URL', '')
if not url:
    raise SystemExit('Create .env from .env.example first.')
database_name = url.rsplit('/', 1)[-1]
admin_url = url.rsplit('/', 1)[0] + '/postgres'
engine = create_engine(admin_url, isolation_level='AUTOCOMMIT')
with engine.connect() as connection:
    exists = connection.execute(text('SELECT 1 FROM pg_database WHERE datname = :name'), {'name': database_name}).scalar()
    if not exists:
        connection.execute(text(f'CREATE DATABASE "{database_name}"'))
        print(f'Created {database_name}.')
    else:
        print(f'{database_name} already exists.')
