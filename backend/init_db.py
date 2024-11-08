from libs.db.common import Base, get_engine
from libs.db.models import Notice

if __name__ == "__main__":
    engine = get_engine()
    Base.metadata.create_all(engine)
