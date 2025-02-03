from sqlalchemy import BLOB, Boolean, Column, Date, ForeignKey, Integer, String,Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    chat_id = Column(Integer, primary_key=True)
    name = Column(String(100))
    childrens = relationship("Baby")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class User_params(Base):
    __tablename__ = "user_params"
    id = Column(Integer, primary_key=True, autoincrement=True)
    weight = Column(Integer)
    height = Column(Integer)
    imt = Column(Integer)
    age = Column(Integer)
    sex = Column(Integer)
    user_id = Column(Integer, ForeignKey("user.chat_id"))

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Question(Base):
    __tablename__ = "question"
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String(1000), nullable=False)
    type = Column(String(10), nullable=False)
    picture = Column(Integer, ForeignKey("picture.id"))
    next_question_id = Column(Integer)
    answer = relationship("Answer")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Answer(Base):
    __tablename__ = "answer"
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String(100), nullable=False)
    points_szrp = Column(Integer, nullable=False)
    points_pre = Column(Integer, nullable=False)
    question_id = Column(Integer, ForeignKey("question.id"))
    next_question_id = Column(Integer)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Picture(Base):
    __tablename__ = "picture"
    id = Column(Integer, primary_key=True, autoincrement=True)
    picture = Column(BLOB)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Risk_result(Base):
    __tablename__ = "risk_result"
    id = Column(Integer, primary_key=True, autoincrement=True)
    result = Column(Integer, nullable=False)
    result_szrp = Column(String(1000), nullable=False)
    result_pre = Column(String(1000), nullable=False)
    date = Column(Date, nullable=False)
    user_id = Column(Integer, ForeignKey("user.chat_id"))

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Baby(Base):
    __tablename__ = "baby"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    birth_date = Column(Date, nullable=False)
    parent_id = Column(Integer, ForeignKey("user.chat_id"))
    vaccines = relationship("Vacc_pass")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Vacc_pass(Base):
    __tablename__ = "vacc_pass"
    id = Column(Integer, primary_key=True, autoincrement=True)
    patogen_id = Column(Integer, ForeignKey("patogen.id"))
    drug_id = Column(Integer, ForeignKey("drug.id"))
    dose = Column(Integer, nullable=False)
    date_medication = Column(Date, nullable=False)
    baby_age = Column(Integer, nullable=False)
    baby_id = Column(Integer, ForeignKey("baby.id"))

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Patogen(Base):
    __tablename__ = "patogen"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    title = Column(String(1000), nullable=False)
    link = Column(String(1000), nullable=False)
    drugs_names = Column(String(1000), nullable=False)
    drug = relationship("Vacc_table", backref="patogen")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Drug(Base):
    __tablename__ = "drug"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    title = Column(String(1000), nullable=False)
    link = Column(String(1000), nullable=False)
    description = Column(String(1000))
    warning = Column(String(1000))
    age = Column(String(1000), nullable=False)
    age_start = Column(Float, nullable=False)
    age_stop = Column(Float)
    patogens_names = Column(String(1000), nullable=False)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Rel_patogen_to_drug(Base):
    __tablename__ = "rel_patogen_to_drug"
    id = Column(Integer, primary_key=True, autoincrement=True)
    patogen_id = Column(Integer, ForeignKey("patogen.id"))
    drug_id = Column(Integer, ForeignKey("drug.id"))

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Rel_drug_to_patogen(Base):
    __tablename__ = "rel_drug_to_patogen"
    id = Column(Integer, primary_key=True, autoincrement=True)
    drug_id = Column(Integer, ForeignKey("drug.id"))
    patogen_id = Column(Integer, ForeignKey("patogen.id"))

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Vacc_table(Base):
    __tablename__ = "vacc_table"
    id = Column(Integer, primary_key=True, autoincrement=True)
    age = Column(Integer, nullable=False)
    num_dose = Column(Integer, nullable=False)
    nationalUp = Column(Boolean, nullable=False)
    patogen_id = Column(Integer, ForeignKey("patogen.id"))
    info = Column(String(1000))

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Syringe(Base):
    __tablename__ = "syringe"
    id = Column(Integer, primary_key=True, autoincrement=True)
    syringe = Column(Integer, nullable=False)
    patogen_id = Column(Integer, ForeignKey("patogen.id"))

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
