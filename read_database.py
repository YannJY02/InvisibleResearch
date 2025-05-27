from sqlalchemy import create_engine, inspect
import pandas as pd
import os
# Force Modin to use the Python (non-Ray) engine to avoid Ray serialization issues
os.environ["MODIN_ENGINE"] = "python"
from lxml import etree
from huggingface_hub import hf_hub_download
import fasttext
# 让 Pandas／Modin 在打印时不省略任何列
pd.set_option('display.max_columns', None)    # 不限制要显示的列数
pd.set_option('display.width', 1000)         # 或更大，根据你终端的宽度调整
pd.set_option('display.max_colwidth', None)  # 让每个单元格都完整展开

# 样本数量，用于限制读取记录数
N = 10

engine = create_engine(
    "mysql+pymysql://root:secret@127.0.0.1:3306/invisible_research"
)

# view all tables in the database
inspector = inspect(engine)
print(inspector.get_table_names())

# list all columns' names in each table
for table in inspector.get_table_names():
    cols = inspector.get_columns(table)
    print(f"Columns in {table}: {[col['name'] for col in cols]}")

# only read 10 records from the 'records' table
df_meta = pd.read_sql(f"SELECT id, metadata FROM records LIMIT {N}", con=engine)

# view the first 10 records of xml metadata header
tags = set()
for xml_str in df_meta['metadata'].head(N):
    try:
        root = etree.fromstring(xml_str.encode('utf-8'))
        for elem in root.iter():
            tags.add(elem.tag)
    except Exception:
        continue
print(f"Unique XML tags in first {N} records: {tags}")

# Extract <language>, <title> and <description> from each sample record's XML metadata
df_meta['language'] = df_meta['metadata'].apply(
    lambda xml: (
        etree.fromstring(xml.encode('utf-8'))
               .findtext('.//{http://purl.org/dc/elements/1.1/}language')
               if xml else None
    )
)
df_meta['title'] = df_meta['metadata'].apply(
    lambda xml: (
        etree.fromstring(xml.encode('utf-8'))
               .findtext('.//{http://purl.org/dc/elements/1.1/}title')
               if xml else None
    )
)
df_meta['abstract'] = df_meta['metadata'].apply(
    lambda xml: (
        (etree.fromstring(xml.encode('utf-8'))
               .findtext('.//{http://purl.org/dc/elements/1.1/}description'))
        if xml else None
    )
)

# Download and load GlotLID FastText model
model_path = hf_hub_download("cis-lmu/glotlid", "model.bin")
model = fasttext.load_model(model_path)

# Predict language of title and abstract using GlotLID model
df_meta['pred_lang_title'] = df_meta['title'].apply(
    lambda txt: model.predict(txt)[0][0] if txt else None
)
df_meta['pred_lang_abstract'] = df_meta['abstract'].apply(
    lambda txt: model.predict(txt)[0][0] if txt else None
)

print(f"Language (metadata vs GlotLID) for first {N} records:")
print(
    df_meta[
        [
            'id',
            'language',               # language from metadata
            'pred_lang_title',        # GlotLID from title
            'pred_lang_abstract',     # GlotLID from abstract
            'title',
            'abstract',
        ]
    ].to_string(index=False)
)

# Save the sample records to a CSV file instead of only printing
output_cols = [
    'id',
    'language',
    'pred_lang_title',
    'pred_lang_abstract',
    'title',
    'abstract',
]
df_meta[output_cols].to_csv("sample_records_language_title_abstract.csv", index=False)
print("✅ CSV file 'sample_records_language_title_abstract.csv' has been written.")
