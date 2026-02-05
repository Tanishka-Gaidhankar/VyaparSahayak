from sqlalchemy import create_engine, inspect

DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(DATABASE_URL)
inspector = inspect(engine)

print("Columns in 'products' table:")
for column in inspector.get_columns("products"):
    print(f"- {column['name']} ({column['type']})")

print("\nColumns in 'orders' table:")
for column in inspector.get_columns("orders"):
    print(f"- {column['name']} ({column['type']})")
