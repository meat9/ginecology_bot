from dbase.create_data import (
    get_answers,
    get_drugs,
    get_patogens,
    get_pics,
    get_questions,
    get_rel_drug_to_patogen,
    get_rel_patogen_to_drug,
    get_syringe,
    get_vact_table,
)

from dbase.library import write_to_bd
from models import *
from sqlalchemy import create_engine
import os


def start_write_table(session):
    list_pics=get_pics()
    list_patogens=get_patogens()
    list_drugs_names=get_drugs()
    list_vacc_table=get_vact_table()
    list_questions=get_questions()
    list_answers=get_answers()
    list_syringe=get_syringe()
    list_rel_drug_to_patogen=get_rel_drug_to_patogen()
    list_rel_patogen_to_drug=get_rel_patogen_to_drug()
    for i in list_patogens:
        if i["drugs_names"] != "":
            i["drugs_names"] = ";".join(i["drugs_names"])
        write=write_to_bd(session, "Patogen", **i)
    for i in list_drugs_names:
        write=write_to_bd(session, "Drug", **i)
    for i in list_vacc_table:
        write=write_to_bd(session, "Vacc_table", **i)
    for i in list_pics:
        write=write_to_bd(session, "Picture", **i)
    for i in list_questions:
        write=write_to_bd(session, "Question", **i)
    for i in list_answers:
        write=write_to_bd(session, "Answer", **i)
    for i in list_syringe:
        write=write_to_bd(session, "Syringe", **i)
    for i in list_rel_patogen_to_drug:
        write=write_to_bd(session, "Rel_patogen_to_drug", **i)
    for i in list_rel_drug_to_patogen:
        write=write_to_bd(session, "Rel_drug_to_patogen", **i)

    return 1

def create_db(file_name):
    engine = create_engine("sqlite:///" + file_name)
    table_objects = []
    class_list = [
        "user",
        "user_params",
        "picture",
        "question",
        "answer",
        "baby",
        "vacc_pass",
        "patogen",
        "drug",
        "vacc_table",
        "risk_result",
        "rel_patogen_to_drug",
        "rel_drug_to_patogen",
        "syringe",
    ]
    for i in class_list:
        table_objects.append(Base.metadata.tables[i])
    Base.metadata.create_all(engine, tables=table_objects)
    return engine


def check_db(filename):
    return os.path.exists(filename)
