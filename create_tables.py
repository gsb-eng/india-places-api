from db import Base, engine

# Create db defined in the models.
def init_db():
    import models
    Base.metadata.create_all(bind=engine)

init_db()
