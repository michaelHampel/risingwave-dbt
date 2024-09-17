import pyarrow.parquet as pq
import pandas
import duckdb
from pyiceberg.catalog import load_catalog

catalog_name = 'default'
iceberg_namespace = 'enox'
table_name = 'enox.smartMeter_incoming'

parquet_df = pq.read_table('smartMeter-incoming+1+0000000000.snappy.parquet')
iceberg_catalog = load_catalog(catalog_name)
nss = iceberg_catalog.list_namespaces()
print(f"existing iceberg namespaces: ${nss}")
if(len(nss) == 0):
    iceberg_catalog.create_namespace("enox")
    iceberg_catalog.create_table(
        table_name,
        schema = parquet_df.schema,
    )
print(f"existing iceberg tables: ${iceberg_catalog.list_tables(iceberg_namespace)}")
iceberg_table = iceberg_catalog.load_table(table_name)
print(f"iceberg table schema: ${iceberg_table.schema()}")
print(f"iceberg table properties: ${iceberg_table.properties}")
print(f"iceberg table location: ${iceberg_table.location}")
print(f"iceberg table current snapshot: ${iceberg_table.current_snapshot()}")
print(f"iceberg table spec: ${iceberg_table.spec()}")

#if(len(filter(lambda n: n[0] == iceberg_namespace, nss) ) == 0):
    

iceberg_table.append(parquet_df)
print(len(iceberg_table.scan().to_arrow()))

pdf = iceberg_table.scan(
    row_filter = "readingFrom >= '2024-08-19T12:11:35Z' and readingFrom < '2024-08-19T13:37:55Z'",
    selected_fields = ("owner", "device", "energy")
).to_pandas()

display(pdf)

