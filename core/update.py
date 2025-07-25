import os
from datetime import datetime, timezone, timedelta
from influxdb_client import InfluxDBClient, Point, WritePrecision

INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://influxdb:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "watchcat")

client = InfluxDBClient(
    url=INFLUXDB_URL,
    token=INFLUXDB_TOKEN,
    org=INFLUXDB_ORG
)

print("InfluxDB Initialized with URL:", INFLUXDB_URL)
print("InfluxDB Bucket:", INFLUXDB_BUCKET)
print("InfluxDB Org:", INFLUXDB_ORG)

write_api = client.write_api()

def write_to_influx(name, prev, open_, current):
    try:
        point = (
            Point("stock_price")
            .tag("name", name)
            .field("prev", float(prev.replace(",", "")))
            .field("open", float(open_.replace(",", "")))
            .field("current", float(current.replace(",", "")))
            .time(datetime.now(timezone.utc), WritePrecision.NS)
        )
        write_api.write(bucket=INFLUXDB_BUCKET, record=point)
    except Exception as e:
        raise e