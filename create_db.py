from database import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)
print("Database and tables created successfully!")
