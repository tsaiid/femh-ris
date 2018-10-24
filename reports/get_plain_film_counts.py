import yaml
import os
import cx_Oracle
from sqlalchemy import create_engine

def get_plain_film_counts(dr_id, mode='this_month', db_engine=None):
    # load db cfg
    if not db_engine:
        db_yml_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'db.yml')
        with open(db_yml_path, 'r') as ymlfile:
            cfg = yaml.load(ymlfile)

        oracle_conn_str = 'oracle+cx_oracle://{username}:{password}@{dsn_str}'
        dsn_str = cx_Oracle.makedsn(cfg['oracle']['ip'],
                                    cfg['oracle']['port'],
                                    cfg['oracle']['service_name']).replace('SID', 'SERVICE_NAME')
        db_engine = create_engine(
            oracle_conn_str.format(
                username=cfg['oracle']['username'],
                password=cfg['oracle']['password'],
                dsn_str=dsn_str
            )
        )

    # Get total exam and total image count of plain film exam in current month or today
    sql_trunc_mode = 'mm' if mode == 'this_month' else 'dd'
    sql_get_counts = '''
SELECT COUNT(*) total_exam, SUM(imagecount) total_image
FROM risworklistdatas w
LEFT JOIN
    (SELECT * FROM risreportdatas
    ) r
    ON w.accno = r.accno
WHERE
    confirmdate BETWEEN
            TRUNC (SYSDATE, '{sql_trunc_mode}')/*current month*/ AND SYSDATE
        AND
    confirmdrid = '{dr_id}'
        AND
    w.datastatus = 'RPTVS'
        AND
    (examcode LIKE 'RA%' OR examcode LIKE '340-0%')
    '''.format(dr_id=dr_id, sql_trunc_mode=sql_trunc_mode)
    results = db_engine.execute(sql_get_counts)
    counts = [{ 'exam':     row['total_exam'],
                'images':   row['total_image']  } for row in results]
    if counts:
        return counts[0]
