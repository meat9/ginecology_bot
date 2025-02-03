from dateutil.parser import parse as du_parse
from dateutil.relativedelta import relativedelta
from importlib import import_module
from log import Logging
from sqlalchemy import and_, or_, not_
from models import *
import datetime
import inspect
import re

# import pprint
# pprint.pprint(list_result_sorted)


def write_to_bd(session, typeClass, **kwargs):
    try:
        module = import_module("models")
        class_obj = getattr(module, typeClass)
        sig = inspect.signature(class_obj)
        bounded = sig.bind(**kwargs)
        bounded.apply_defaults()
        session.add(class_obj(*bounded.args, **bounded.kwargs))
        session.commit()
    except:
        log = Logging(__name__)
        log.error_library(typeClass, __name__, __file__, " Ошибка при записи данных в БД. keys:"+str(kwargs))
        return 0
    return 1


def get_info_by_id(session, typeClass, id_search, props_list):
    module = import_module("models")
    class_obj = getattr(module, typeClass)
    q = session.query(class_obj).filter(class_obj.id == id_search)
    tmp_dict = {}
    for c in q:
        for props in props_list:
            tmp_dict[props] = getattr(c, props, None)
    return tmp_dict


def get_info_by_filter(session, typeClass, filter_par, meaning, props_list):
    module = import_module("models")
    class_obj = getattr(module, typeClass)
    q = (
        session.query(class_obj)
        .filter(getattr(class_obj, filter_par) == meaning)
        .order_by(getattr(class_obj, filter_par))
    )
    tmp_list = []
    for c in q:
        tmp_dict = {}
        for props in props_list:
            tmp_dict[props] = getattr(c, props, None)
        tmp_list.append(tmp_dict)
    return tmp_list


def get_info_by_like(session, typeClass, filter_par, meaning, props_list):
    module = import_module("models")
    class_obj = getattr(module, typeClass)
    q = (
        session.query(class_obj)
        .filter(getattr(class_obj, filter_par).ilike(meaning + "%"))
        .order_by(getattr(class_obj, filter_par))
    )
    tmp_list = []

    for c in q:
        tmp_dict = {}
        for props in props_list:
            tmp_dict[props] = getattr(c, props, None)
        tmp_list.append(tmp_dict)
    return tmp_list


def get_vacc_pass(session, baby_id):
    return get_info_by_filter(
        session, "Vacc_pass", "baby_id", baby_id, ["patogen_id", "drug_id", "dose"]
    )


def get_plain_vaccine(session, month, vacc_pass_info):
    module = import_module("models")
    vacc_table = getattr(module, "Vacc_table")
    props_list = ["id", "age", "num_dose", "nationalUp", "patogen_id", "info"]
    list_result = []
    uniq_dict = {}

    query = session.query(vacc_table).filter(vacc_table.age == month)
    results = query.all()
    for c in results:
        id_table = c.id
        patogen_id = c.patogen_id
        num_dose = c.num_dose
        stop_flag = 0
        for check in vacc_pass_info:
            if (
                stop_flag == 0
                and check["patogen_id"] == patogen_id
                and check["dose"] == num_dose
            ):
                stop_flag = 1
        if stop_flag == 1:
            break

        if id_table not in uniq_dict:
            uniq_dict[id_table] = {}
            patogen_obj = get_patogen_info(session, patogen_id)

            syringe = get_info_by_filter(
                session, "Syringe", "patogen_id", patogen_id, ["syringe"]
            )
            try:
                syringe = syringe[0]["syringe"]
            except:
                syringe = 999

            uniq_dict[id_table]["name"] = patogen_obj["name"]
            uniq_dict[id_table]["syringe"] = syringe
            for props in props_list:
                uniq_dict[id_table][props] = getattr(c, props, None)
            uniq_dict[id_table]["drug"] = []
        list_drugs = get_drug_for_patogen(session, patogen_id)
        list_draugs_res = []
        for i in list_drugs:
            list_draugs_res.append(i["name"])
        uniq_dict[id_table]["drug"] = list_draugs_res
    for i in uniq_dict:
        list_result.append(uniq_dict[i])

    list_result_sorted = sorted(list_result, key=lambda d: d["syringe"])

    return list_result_sorted


def get_info_all(session, typeClass, props_list, sort_par=""):
    module = import_module("models")
    class_obj = getattr(module, typeClass)
    if sort_par != "":
        q = session.query(class_obj).order_by(getattr(class_obj, sort_par))
    else:
        q = session.query(class_obj)
    tmp_list = []
    for c in q:
        tmp_dict = {}
        for props in props_list:
            tmp_dict[props] = getattr(c, props, None)
        tmp_list.append(tmp_dict)
    return tmp_list


def user_exist(session, user_id):
    q = get_info_by_filter(session, "User", "chat_id", user_id, ["id"])
    for c in q:
        if c:
            return 1
    return 0


def get_all_children(session, user_id):
    tmp_dict = {}
    tmp_dict[user_id] = []
    tmp_list = []
    prop_list = ["id", "name", "birth_date", "vaccines"]
    tmp_list = get_info_by_filter(session, "Baby", "parent_id", user_id, prop_list)
    tmp_dict[user_id] = tmp_list
    return tmp_dict


def get_all_patogen_with_drugs(session):
    prop_list = ["id", "name"]
    list_return = []
    list_patogens = get_info_all(session, "Patogen", prop_list, "name")

    for patogen in list_patogens:
        drug = get_drug_for_patogen(session, patogen["id"])
        if drug != []:
            patogen["drugs"] = drug
        list_return.append(patogen)
    return list_return


def get_drug_for_patogen(session, patogen_id):
    tmp_list_drug = []
    q = get_info_by_filter(
        session, "Rel_patogen_to_drug", "patogen_id", patogen_id, ["drug_id"]
    )
    for c in q:

        tmp_list_drug.append(
            get_info_by_id(session, "Drug", c["drug_id"], ["id", "name","age_start","age_stop"])
        )

    return tmp_list_drug


def get_patogen_info(session, patogen_id):
    param_list = ["id", "name", "drugs_names", "title", "link"]
    return get_info_by_id(session, "Patogen", patogen_id, param_list)


def get_all_drugs(session):
    prop_list = ["id", "name"]
    return get_info_all(session, "Drug", prop_list, "name")


def get_all_drugs_by_like(session, first_letter):
    props_list = ["id", "name"]
    q = get_info_by_like(session, "Drug", "name", first_letter, props_list)
    return q


def get_all_patogens_by_like(session, first_letter):
    props_list = ["id", "name"]
    q = get_info_by_like(session, "Patogen", "name", first_letter, props_list)
    return q


def get_drug_full_info(session, drug_id):
    param_list = [
        "id",
        "name",
        "title",
        "link",
        "description",
        "warning",
        "age",
        "patogens_names",
    ]
    return get_info_by_id(session, "Drug", drug_id, param_list)


def get_children_info(session, baby_id):
    param_list = ["id", "name", "birth_date", "parent_id"]
    return get_info_by_id(session, "Baby", baby_id, param_list)


def get_children_vaccine_info(session, baby_id):
    tmp_list = []
    prop_list = ["id", "name"]
    prop_list_vac = ["id", "patogen_id", "drug_id", "date_medication", "baby_age"]
    q = get_info_by_filter(session, "Vacc_pass", "baby_id", baby_id, prop_list_vac)
    for c in q:
        vacc_dict = {}
        vacc_dict["id"] = c["id"]
        vacc_dict["patogen"] = get_info_by_id(
            session, "Patogen", c["patogen_id"], prop_list
        )["name"]
        vacc_dict["drug"] = get_info_by_id(session, "Drug", c["drug_id"], prop_list)[
            "name"
        ]
        vacc_dict["date_medication"] = c["date_medication"]
        vacc_dict["baby_age"] = c["baby_age"]
        tmp_list.append(vacc_dict)
    return tmp_list


def getListVacByMonth(session, month):
    set_ids_patogen = set()
    patogen_dict = {}
    patogen_list = []

    prop_list = ["id", "num_dose", "nationalUp", "patogen_id", "info"]
    q = get_info_by_filter(session, "Vacc_table", "age", month, prop_list)
    if not q:
        return {}

    for c in q:

        set_ids_patogen.add(
            str(c["patogen_id"])
            + "#"
            + str(c["num_dose"])
            + "#"
            + str(c["nationalUp"])
            + "#"
            + str(c["info"])
        )

    for c in set_ids_patogen:
        patogen_dict = {}
        drug_names = set()
        tmp_list_drug_ids = get_drug_for_patogen(session, int(c.split("#")[0]))
        
        for i in tmp_list_drug_ids:
            drug_start=i["age_start"]
            drug_and=i["age_stop"]
            if int(month)>=drug_start and int(month)<drug_and:
                drug_names.add(i["name"])

        syringe = get_info_by_filter(
            session, "Syringe", "patogen_id", int(c.split("#")[0]), ["syringe"]
        )
        try:
            syringe = syringe[0]["syringe"]
        except:
            syringe = 999
        res = get_info_by_id(session, "Patogen", int(c.split("#")[0]), ["name"])
        patogen_dict["syringe"] = syringe  # 1#syringe[0]["syringe"]
        patogen_dict["name"] = res["name"]
        patogen_dict["num_dose"] = int(c.split("#")[1])
        patogen_dict["nationalUp"] = c.split("#")[2]
        patogen_dict["info"] = c.split("#")[3]
        patogen_dict["drug"] = list(drug_names)
        patogen_list.append(patogen_dict)

    patogen_list_sorted = sorted(patogen_list, key=lambda d: d["syringe"])

    return patogen_list_sorted


def str_to_date(string):
    try:
        date = re.sub(r"[,.;@#?!&$]+\ *", " ", string)
        date = datetime.datetime.strptime(date, "%d %m %Y")
    except:
        date = "error"
    return date


def date_to_str(date):
    string = datetime.datetime.strftime(date, "%d.%m.%Y")
    return string


def date_diff(date_start, date_stop=None):
    if not date_stop:
        now = du_parse(str(datetime.datetime.today().strftime("%Y-%m-%d")))
    else:
        now = du_parse(str(date_stop))
    date_start = du_parse(str(date_start))
    delta = relativedelta(now, date_start)
    return delta.years * 12 + delta.months


def prep_str_future_vac(data, month, old=0):
    str_patogen = ""
    if old == 1:
        head = " мес. необходимо было сделать следующие прививки: "
    else:
        head = " мес. необходимо сделать следующие прививки: "
    string = "Для возраста " + str(month) + head + "\n" + "\n"
    for elem in data:
        str_national = ""
        if elem["nationalUp"] == "True" or elem["nationalUp"] == True:
            str_national = " (сверх нац. календаря)"
        str_dose = ""
        if elem["num_dose"] != 0:
            str_dose = " доза №" + str(elem["num_dose"])
        str_info = ""
        if elem["info"] != "":
            str_info = " (" + elem["info"] + ") "
        str_patogen += elem["name"] + str_info + str_dose + str_national + "\n"
        str_patogen += "Препараты: "
        for name in elem["drug"]:

            str_patogen += name + ", "
        str_patogen += "\n" + "\n"

    string += str_patogen
    return string


def get_all_question(session):
    prop_list_q = ["id", "text", "type", "picture", "next_question_id"]
    result_list = []
    tmp_list_q = get_info_all(session, "Question", prop_list_q)
    for elem in tmp_list_q:
        tmp_dict_q = {}
        tmp_dict_q["answers"] = get_all_answers(session, elem["id"])
        result_list.append(tmp_dict_q)

    return result_list


def get_all_answers(session, question_id):
    prop_list_a = [
        "id",
        "text",
        "points_szrp",
        "points_pre",
        "question_id",
        "next_question_id",
    ]
    result = get_info_by_filter(
        session, "Answer", "question_id", question_id, prop_list_a
    )
    return result


def get_question_by_id(session, question_id):
    prop_list_q = ["id", "text", "type", "picture", "next_question_id"]
    result = get_info_by_id(session, "Question", question_id, prop_list_q)

    result["answers"] = get_all_answers(session, result["id"])

    return result


def get_last_risk_result(session, user_id):
    prop_list = ["id", "result", "result_szrp", "result_pre", "date"]
    tmp_list = get_info_by_filter(session, "Risk_result", "user_id", user_id, prop_list)
    prop_list = ["id", "imt"]
    tmp_list_imt = get_info_by_filter(
        session, "User_params", "user_id", user_id, prop_list
    )
    try:
        res_dict = tmp_list[-1]
    except:
        return {}
    res_dict["imt"] = tmp_list_imt[-1]["imt"]
    return tmp_list[-1]


def get_image_by_id(session, id):
    param_list = ["id", "picture"]
    return get_info_by_id(session, "Picture", id, param_list)



def fix_all_pics(session,bot):
    prop_list = ["id", "picture"]
    pics_array=get_info_all(session, "Picture", prop_list, "id")
    pics_array_corr={}
    for i in pics_array:
        if i["id"]!=3:
            pics_array_corr["picture"]=i["picture"]
            if i["id"]==1:
                pics_array_corr["id"] = 21
            if i["id"]==2:
                pics_array_corr["id"] = 11

        #pics_array_corr.append({"picture": i["picture"]})

            write=write_to_bd(session, "Picture", **pics_array_corr)
    pics_array=get_info_all(session, "Picture", prop_list, "id")
    for i in pics_array:
        if i["id"]!=3:
            if (i["id"]==1) or (i["id"]==2):
                module = import_module("models")
                class_obj = getattr(module, "Picture")
                obj2=session.get(class_obj, i["id"])
                session.delete(obj2)
                session.commit()
                continue
            pics_array_corr["picture"]=i["picture"]
            if i["id"]==21:
                pics_array_corr["id"] = 2
            if i["id"]==11:
                pics_array_corr["id"] = 1
            write=write_to_bd(session, "Picture", **pics_array_corr)
        #pics_array_corr.append({"picture": i["picture"]})

    for i in pics_array:
        if i["id"]!=3:
            if (i["id"]==21) or (i["id"]==11):
                module = import_module("models")
                class_obj = getattr(module, "Picture")
                obj2=session.get(class_obj, i["id"])
                session.delete(obj2)
                session.commit()
