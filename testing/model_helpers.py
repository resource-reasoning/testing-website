from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import case, func, literal_column



"""
For columns to group by a,b,c,d and values in x, generate the query:
    SELECT a, b, c, d, SUM(x) FROM t WHERE
        a IS NOT NULL AND b IS NOT NULL AND c IS NOT NULL AND d IS NOT NULL
        GROUP BY a, b, c, d
    UNION ALL SELECT a, b, c, NULL AS d, SUM(x) FROM t WHERE
        a IS NOT NULL AND b IS NOT NULL AND c IS NOT NULL
        GROUP BY a, b, c
    UNION ALL SELECT a, b, NULL AS c, NULL AS d, SUM(x) FROM t WHERE
        a IS NOT NULL AND b IS NOT NULL
        GROUP BY a, b
    UNION ALL SELECT a, NULL AS b, NULL AS c, NULL as d, SUM(x) FROM t WHERE
        a IS NOT NULL
        GROUP BY a
    UNION ALL SELECT NULL AS a, NULL AS b, NULL AS c, NULL AS d, SUM(x) FROM t
    ORDER BY a, b, c, d
"""


def rollup(session, query, *cols, f=func.count):
    """
    cols should not be present in the original query
    """

    def label(col, n):
        return col.label("rollup_%s" % n)

    original_cols = [c['expr'] for c in query.column_descriptions]
    labels = ["rollup_%s" % (n+1) for n in range(0, len(cols))]

    cte = query.add_columns(*cols).cte()

    cte_cols = [cte.corresponding_column(c).label(l)
                    for (c, l) in zip(cols, labels)]
    agg_cols = [f(cte.corresponding_column(c)) for c in original_cols]
    filters = [c.isnot(None) for c in cte_cols]

    subqueries = []

    for x in reversed(range(0, len(cols))):
        subqueries.append(session.query(*cte_cols)
                                 .add_columns(*agg_cols)
                                 .filter(*filters[0:x+1])
                                 .group_by(*labels))
        cte_cols[x] = literal_column('NULL').label(labels[x])

    subqueries.append(session.query(*cte_cols)
                             .add_columns(*agg_cols)
                             .group_by(*labels))

    return subqueries[0].union_all(*subqueries[1:]).order_by(*labels)
