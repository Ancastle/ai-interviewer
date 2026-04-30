SELECT 'CREATE DATABASE langfuse_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'langfuse_db')\gexec
