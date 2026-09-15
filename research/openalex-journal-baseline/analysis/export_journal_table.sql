-- January 2026 US public source; one row per journal Source ID.
-- Aggregate child tables independently so one-to-many joins cannot multiply journals.
-- JSON cells retain every related row, including duplicates and null fields.
WITH journals AS (
  SELECT * FROM `multiobs.publicdb_openalex_2026_01_rm.sources`
  WHERE type = 'journal'
), apc AS (
  SELECT source_id, TO_JSON_STRING(ARRAY_AGG(t ORDER BY TO_JSON_STRING(t))) AS data
  FROM `multiobs.publicdb_openalex_2026_01_rm.sources_apc_prices` AS t GROUP BY source_id
), concepts AS (
  SELECT source_id, TO_JSON_STRING(ARRAY_AGG(t ORDER BY TO_JSON_STRING(t))) AS data
  FROM `multiobs.publicdb_openalex_2026_01_rm.sources_concepts` AS t GROUP BY source_id
), years AS (
  SELECT source_id, TO_JSON_STRING(ARRAY_AGG(t ORDER BY year, TO_JSON_STRING(t))) AS data
  FROM `multiobs.publicdb_openalex_2026_01_rm.sources_counts_by_year` AS t GROUP BY source_id
), institutions AS (
  SELECT source_id, TO_JSON_STRING(ARRAY_AGG(t ORDER BY TO_JSON_STRING(t))) AS data
  FROM `multiobs.publicdb_openalex_2026_01_rm.sources_host_institution_lineage` AS t GROUP BY source_id
), institution_names AS (
  SELECT source_id, TO_JSON_STRING(ARRAY_AGG(t ORDER BY TO_JSON_STRING(t))) AS data
  FROM `multiobs.publicdb_openalex_2026_01_rm.sources_host_institution_lineage_names` AS t GROUP BY source_id
), organizations AS (
  SELECT source_id, TO_JSON_STRING(ARRAY_AGG(t ORDER BY TO_JSON_STRING(t))) AS data
  FROM `multiobs.publicdb_openalex_2026_01_rm.sources_host_organization_lineage` AS t GROUP BY source_id
), organization_names AS (
  SELECT source_id, TO_JSON_STRING(ARRAY_AGG(t ORDER BY TO_JSON_STRING(t))) AS data
  FROM `multiobs.publicdb_openalex_2026_01_rm.sources_host_organization_lineage_names` AS t GROUP BY source_id
), publisher_lineage AS (
  SELECT source_id, TO_JSON_STRING(ARRAY_AGG(t ORDER BY TO_JSON_STRING(t))) AS data
  FROM `multiobs.publicdb_openalex_2026_01_rm.sources_publisher_lineage` AS t GROUP BY source_id
), publisher_names AS (
  SELECT source_id, TO_JSON_STRING(ARRAY_AGG(t ORDER BY TO_JSON_STRING(t))) AS data
  FROM `multiobs.publicdb_openalex_2026_01_rm.sources_publisher_lineage_names` AS t GROUP BY source_id
), societies AS (
  SELECT source_id, TO_JSON_STRING(ARRAY_AGG(t ORDER BY TO_JSON_STRING(t))) AS data
  FROM `multiobs.publicdb_openalex_2026_01_rm.sources_societies` AS t GROUP BY source_id
)
SELECT s.*,
  COALESCE(apc.data, '[]') AS apc_prices_json,
  COALESCE(concepts.data, '[]') AS concepts_json,
  COALESCE(years.data, '[]') AS counts_by_year_json,
  COALESCE(institutions.data, '[]') AS host_institution_lineage_json,
  COALESCE(institution_names.data, '[]') AS host_institution_lineage_names_json,
  COALESCE(organizations.data, '[]') AS host_organization_lineage_json,
  COALESCE(organization_names.data, '[]') AS host_organization_lineage_names_json,
  COALESCE(publisher_lineage.data, '[]') AS publisher_lineage_json,
  COALESCE(publisher_names.data, '[]') AS publisher_lineage_names_json,
  COALESCE(societies.data, '[]') AS societies_json,
  IF(p.id IS NULL, NULL, TO_JSON_STRING(p)) AS publisher_record_json
FROM journals AS s
LEFT JOIN apc ON apc.source_id = s.id
LEFT JOIN concepts ON concepts.source_id = s.id
LEFT JOIN years ON years.source_id = s.id
LEFT JOIN institutions ON institutions.source_id = s.id
LEFT JOIN institution_names ON institution_names.source_id = s.id
LEFT JOIN organizations ON organizations.source_id = s.id
LEFT JOIN organization_names ON organization_names.source_id = s.id
LEFT JOIN publisher_lineage ON publisher_lineage.source_id = s.id
LEFT JOIN publisher_names ON publisher_names.source_id = s.id
LEFT JOIN societies ON societies.source_id = s.id
-- publisher_id is almost entirely null. Match the explicit OpenAlex P identifier;
-- do not infer publishers from similar names or from an institution identifier.
LEFT JOIN `multiobs.publicdb_openalex_2026_01_rm.publishers` AS p
  ON p.id = SAFE_CAST(REGEXP_EXTRACT(s.host_organization,
    r'^https://openalex.org/P([0-9]+)$') AS INT64)
ORDER BY s.id
