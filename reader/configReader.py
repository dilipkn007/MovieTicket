import configparser,os,re
import pathlib as pl

PATH=pl.Path(__file__)
ROOT_PATH=PATH.parent.parent.absolute()

config_path=os.path.join(ROOT_PATH,"config.ini")
config=configparser.ConfigParser()
config.read(config_path)


def get_csv_path(file) -> str:
    return get_path("CSV",file=file)+".csv"


def get_excel_path(workbook) -> str:
    return get_path("EXCEL",file=workbook)+".xlsx"


def get_path(path_key,file='nan') -> str:
    if file=='nan':
        value=config_reader("FILE_PATHS",path_key)
    else:
        value=config_reader("FILE_PATHS",path_key).replace("{file_name}",file)
    return str(ROOT_PATH)+value


def config_reader(section,key) -> str:
    actual_value = config.get(section, key)
    if re.search(r"^`.+`$",actual_value):
        pattern = r'\{\[\(.+\)\]\}'
        matching_string = re.search(pattern,actual_value)
        value=matching_string.group()
        sub_string_pattern=r'[\[\(\{\}\)\]]'
        value = re.sub(sub_string_pattern, "", value)
        actual_value = re.sub(pattern,config_reader(section,value),actual_value).replace('`','')
    return actual_value


if __name__=="__main__":
    print(config_reader("DB_CONNECTION","string"))
