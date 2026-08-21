from sqlalchemy import create_engine, text
e = create_engine("postgresql://postgres:postgres@localhost:5432/memorychat")
with e.connect() as c:
    r = c.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name"))
    tables = [row[0] for row in r]
    print("Tables:", tables)
    ver = c.execute(text("SELECT version_num FROM alembic_version")).scalar()
    print("Alembic:", ver)
    print()
    print("users columns:")
    cols = c.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='public' AND table_name='users' ORDER BY ordinal_position"))
    for col in cols:
        print(f"  {col[0]:20s} {col[1]}")
