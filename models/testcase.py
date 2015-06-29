from sqlalchemy import Boolean, Column, String


class TestCase(Base):
    id = Column(String, primary_key=True)
    negative = Column(Boolean)
