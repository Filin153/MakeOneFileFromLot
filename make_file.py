import pandas as pd
import os
from datetime import datetime
import re
import zipfile

def get_info_from_name_disc(data: str) -> dict:
    info = data.split("\t")[-1].split("-")

    do_type = info[0].strip().rstrip()
    do_name = info[1].strip().rstrip()
    try:
        do_group = info[2].strip().rstrip()
    except Exception:
        do_group = None
    do_full_name = " ".join(map(lambda x: x.strip().rstrip(), info))

    return {
        "type": do_type,
        "name": do_name,
        "group": do_group,
        "full_name": do_full_name
    }


def str_to_datetime(data: str):
    try:
        info = data.split("\t")[-1].split(",")
        date = info[0].strip().rstrip().replace("/", ".")
        time = info[1].split()[0].strip().rstrip()

        if info[1].split()[-1] == "PM":
            tmp_time = time.split(":")
            tmp_h = int(tmp_time[0]) * 2
            tmp_time[0] = str(tmp_h)
            time = ":".join(tmp_time)

        return datetime.strptime(date + " " + time, "%m.%d.%y %H:%M:%S").strftime("%d.%m.%Y %H:%M:%S")
    except Exception:
        return None


def create_dfs(file_path) -> (pd.DataFrame, pd.DataFrame):
    df = pd.read_csv(file_path, encoding="UTF-16", sep=";", names=['info'])
    df.reset_index(drop=True, inplace=True)

    start_id = df[df['info'] == "2. Участники"].index
    end_id = df[df['info'] == "3. Действия на собрании"].index

    data_user = list(i[0].split("\t") for i in df.loc[start_id[0] + 1:end_id[0] - 1].values.tolist())
    df_user = pd.DataFrame(data_user[1:], columns=data_user[0])
    df_user.reset_index(drop=True, inplace=True)

    data_svod = list(i[0].split("\t") for i in df.loc[1:start_id[0] - 1].values.tolist())
    df_svod = pd.DataFrame(data_svod, columns=[['Тип', 'Значение']])
    df_svod.reset_index(drop=True, inplace=True)

    return df_svod, df_user


def add_data_to_res(data: dict, full_path, name, time_start, time_end, type_z, prog, group) -> dict:
    data['Путь до файла'].append(full_path)
    data['Название собрания'].append(name)
    data['Время начала собрания'].append(time_start)
    data['Время окончания собрания'].append(time_end)
    data['Тип занятия'].append(type_z)
    data['Программа'].append(prog)
    data['Подгруппа'].append(group)
    return data


def add_new_time(t: list) -> list:
    res = []
    for _ in range(3 - len(t)):
        res.append("00")

    for i in t:
        res.append(i)
    return res

def make_file_from(path: str, save_path: str):
    with zipfile.ZipFile(path, "r") as zip_data:
        path = path.split(".")[0]
        zip_data.extractall(path)
        zip_data.close()


    res_data = {
        "Путь до файла": [],
        "Название собрания": [],
        "Время начала собрания": [],
        "Время окончания собрания": [],
        "Тип занятия": [],
        "Программа": [],
        "Подгруппа": [],
        "ФИО": [],
        "Время на собрании": [],
        "Почта": [],
    }

    for folder in os.listdir(path):
        for folder_in in os.listdir(f"{path}/{folder}"):
            if folder_in.endswith(".csv"):
                svod, user = create_dfs(f"{path}/{folder}/{folder_in}")
                info = get_info_from_name_disc(svod['Значение'].loc[0][0])
                for fio, time_in, email in zip(user['Имя'].values.tolist(),
                                               user['Длительность собрания'].values.tolist(),
                                               user['Электронная почта'].values.tolist()):
                    res_data = add_data_to_res(res_data, f"{folder}/{folder_in}/{file}", info['full_name'],
                                               str_to_datetime(svod.loc[2]['Значение']),
                                               str_to_datetime(svod.loc[3]['Значение']),
                                               info['type'], info['name'], info['group'])
                    res_data['ФИО'].append(fio)
                    res_data['Время на собрании'].append(datetime.strptime(":".join(list(
                        map(lambda x: x if len(x) == 2 else f"0{x}",
                            add_new_time(re.sub("[^0-9\s]", "", time_in).strip().rstrip().split("  "))))),
                        "%H:%M:%S").time())
                    res_data['Почта'].append(email)
                continue
            for file in os.listdir(f"{path}/{folder}/{folder_in}"):
                svod, user = create_dfs(f"{path}/{folder}/{folder_in}/{file}")
                info = get_info_from_name_disc(svod['Значение'].loc[0][0])
                for fio, time_in, email in zip(user['Имя'].values.tolist(),
                                               user['Длительность собрания'].values.tolist(),
                                               user['Электронная почта'].values.tolist()):
                    res_data = add_data_to_res(res_data, f"{folder}/{folder_in}/{file}", info['full_name'],
                                               str_to_datetime(svod.loc[2]['Значение']),
                                               str_to_datetime(svod.loc[3]['Значение']),
                                               info['type'], info['name'], info['group'])
                    res_data['ФИО'].append(fio)
                    res_data['Время на собрании'].append(datetime.strptime(":".join(list(
                        map(lambda x: x if len(x) == 2 else f"0{x}",
                            add_new_time(re.sub("[^0-9\s]", "", time_in).strip().rstrip().split("  "))))),
                        "%H:%M:%S").time())
                    res_data['Почта'].append(email)

    df = pd.DataFrame(res_data)
    df['Время начала собрания'] = pd.to_datetime(df['Время начала собрания'], format='mixed')
    df['Время окончания собрания'] = pd.to_datetime(df['Время окончания собрания'], format='mixed')
    df.to_excel(save_path, index=False, engine="openpyxl")

    return save_path