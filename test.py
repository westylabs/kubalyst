import pandas
import pyarrow
from query.commands import type_mapper

type_mapper.trino_type_to_pyarrow_type("array(varchar(14))")
data = ["1", "2", "3"]
mapped_data = type_mapper.ArrayValueMapper().map(data)

table = pyarrow.table([[["1", "2", "3"]]], names=["col"])
print(table.schema)


trino_type = "array(varchar)"
field = pyarrow.field(
    "col",
    type_mapper.trino_type_to_pyarrow_type(trino_type),
    # metadata=type_mapper.trino_type_to_snowflake_metadata(trino_type),
)
schema = pyarrow.schema([field])
print(schema)

print(table.schema == pyarrow.schema)

# table = pyarrow.table(
#     [
#         pyarrow.array([1, 2, 3]),
#     ],
#     names=["col1"],
# )
# print(table.schema)

df = pandas.DataFrame(
    [[mapped_data]],
    columns=["col"],
)
tb = pyarrow.table(
    [[mapped_data]],
    schema=schema,
)
print(tb)

# table2 = pyarrow.Table.from_pandas(df, schema=schema)
