import yaml

def load_stock_infos(path="data/stocks.yml"):
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)["stocks"]

    by_code = data
    by_name = {name: code for code, name in data.items()}

    return by_code, by_name