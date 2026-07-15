import ast
import json
import re
from pathlib import Path

import pandas as pd


def test_first_author_id_extraction_and_experience() -> None:
    source = (
        Path(__file__).parents[1]
        / 'research/dimensions-dataset-construction/analysis/create_variables.py'
    ).read_text(
        encoding='utf-8'
    )
    helpers = source[source.index('# Helpers'):source.index('# Output frames')]
    namespace = {'ast': ast, 'json': json, 'pd': pd, 're': re}
    namespace['fa_raw'] = pd.DataFrame({
        'id': ['r1', 'r2', 'r3', 'r4', 'r5'],
        'paper_year': [2000, 2005, 2007, 2010, 2004],
        'researchers': [
            '[{"id":"ur.1"}]',
            None,
            '[{"ids":[{"dimensions_id":"ur.3"}]}]',
            None,
            '[{"id":"ur.1"}]',
        ],
        'authors': [
            '[{"id":"ur.9"}]',
            '[{"id":"ur.2"}]',
            '[{"id":"ur.8"}]',
            '[{"name":"unkeyed"}]',
            '[{"id":"ur.9"}]',
        ],
    })
    exec(helpers, namespace)

    fa_raw = namespace['fa_raw']
    fa_exp = namespace['fa_exp']
    assert fa_raw['first_author_key'].tolist() == ['ur.1', 'ur.2', 'ur.3', None, 'ur.1']
    assert fa_exp.tolist()[:3] == [0, 0, 0]
    assert pd.isna(fa_exp.iloc[3])
    assert fa_exp.iloc[4] == 4


if __name__ == '__main__':
    test_first_author_id_extraction_and_experience()
    print('first_author_experience check: ok')
