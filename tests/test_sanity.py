
# Confirms pg_config is working, PATH is good, & system is ready to run pytest-postgresql
def test_pg_config_availability():
    import subprocess
    out = subprocess.run(["pg_config", "--version"], capture_output=True)
    print("pg_config output:", out.stdout.decode())
    assert out.returncode == 0

def test_postgresql_proc_works(postgresql_proc):
    print("Postgres DSN:", postgresql_proc.dsn())
    assert "postgresql://" in postgresql_proc.dsn()

def test_postgresql_manual(postgresql):
    postgresql.start()
    print("DSN:", postgresql.dsn())
    assert "postgresql://" in postgresql.dsn()

def test_postgresql_is_up(postgresql_proc):
    # This checks that PostgreSQL started successfully
    assert postgresql_proc is not None
    assert postgresql_proc.dsn() is not None
    print(f"PostgreSQL DSN: {postgresql_proc.dsn()}")
