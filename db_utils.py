import pandas as pd
from sqlalchemy import create_engine

MYSQL_URI = "mysql+mysqlconnector://ufficio:2ksVkoEPF0DNrKT@smartoltre.nanoh.it:3306/smart"
COLUMNS = ["titolo", "descrizione", "requisiti", "costo", "testocosto", "ore", "sede"]
TABLE = "corsi"
FILTER = "stato_id != 4"

def fetch_courses():
    engine = create_engine(MYSQL_URI)
    query = f"SELECT {', '.join(COLUMNS)} FROM {TABLE} WHERE {FILTER}"
    df = pd.read_sql(query, engine)
    engine.dispose()
    return df

def fetch_courses_dict():
    df = fetch_courses()
    return df.to_dict(orient="records") 