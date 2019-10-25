import yaml
import os
import cx_Oracle
from sqlalchemy import create_engine
from .datelib import get_month_strs
import pandas as pd

#os.environ["NLS_LANG"] = "GERMAN_GERMANY.UTF8"
os.environ["NLS_LANG"] = "TRADITIONAL CHINESE_TAIWAN.AL32UTF8"

def get_monthly_cr_stats(month_str='prev_month', db_engine=None):
    # load db cfg
    if not db_engine:
        db_yml_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'db.yml')
        with open(db_yml_path, 'r') as ymlfile:
            cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

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

    # get month
    (the_month, the_prev_month, the_next_month) = get_month_strs(month_str)
    # Get total exam and total image count of plain film exam in current month or today
    sql_get_stats = '''
SELECT DISTINCT w.machineid,
    NVL(門, 0) 門,
    NVL(急, 0) 急,
    NVL(住, 0) 住,
    NVL(健, 0) 健,
    NVL(總量, 0) 總量,
    NVL(前月總量, 0) 前月總量,
    CASE
        WHEN NVL(前月總量, 0) > 0 THEN ROUND(100 * (NVL(總量, 0) - NVL(前月總量, 0)) / NVL(前月總量, 0), 1)
        ELSE -99999
    END delta,
    NVL(未RCP, 0) 未RCP,
    NVL(未Verify, 0) 未Verify
FROM risworklistdatas w
LEFT JOIN  (SELECT machineid, SUM(CASE WHEN examname = 'Chest AP (Portable)' THEN 1 ELSE imagecount END) AS 門
            FROM risworklistdatas
            WHERE 1=1
                AND orderfrom = 'OPDR'
                AND modality = 'CR'
                AND examname NOT IN ('IVP', '虛擬醫令')
                AND machineid IS NOT NULL
                AND examdate BETWEEN
                    TO_DATE( '{the_month}', 'yyyy-mm-dd' )
                        AND
                    TO_DATE( '{the_next_month}', 'yyyy-mm-dd' )
            GROUP BY machineid) o
ON w.machineid = o.machineid
LEFT JOIN  (SELECT machineid, SUM(CASE WHEN examname = 'Chest AP (Portable)' THEN 1 ELSE imagecount END) AS 急
            FROM risworklistdatas
            WHERE 1=1
                AND orderfrom = 'OPDE'
                AND modality = 'CR'
                AND examname NOT IN ('IVP', '虛擬醫令')
                AND machineid IS NOT NULL
                AND examdate BETWEEN
                    TO_DATE( '{the_month}', 'yyyy-mm-dd' )
                        AND
                    TO_DATE( '{the_next_month}', 'yyyy-mm-dd' )
            GROUP BY machineid) e
ON w.machineid = e.machineid
LEFT JOIN  (SELECT machineid, SUM(CASE WHEN examname = 'Chest AP (Portable)' THEN 1 ELSE imagecount END) AS 住
            FROM risworklistdatas
            WHERE 1=1
                AND orderfrom = 'IPD'
                AND modality = 'CR'
                AND examname NOT IN ('IVP', '虛擬醫令')
                AND machineid IS NOT NULL
                AND examdate BETWEEN
                    TO_DATE( '{the_month}', 'yyyy-mm-dd' )
                        AND
                    TO_DATE( '{the_next_month}', 'yyyy-mm-dd' )
            GROUP BY machineid) i
ON w.machineid = i.machineid
LEFT JOIN  (SELECT machineid, SUM(CASE WHEN examname = 'Chest AP (Portable)' THEN 1 ELSE imagecount END) AS 健
            FROM risworklistdatas
            WHERE 1=1
                AND orderfrom = 'H'
                AND modality = 'CR'
                AND examname NOT IN ('IVP', '虛擬醫令')
                AND examdate BETWEEN
                    TO_DATE( '{the_month}', 'yyyy-mm-dd' )
                        AND
                    TO_DATE( '{the_next_month}', 'yyyy-mm-dd' )
            GROUP BY machineid) h
ON w.machineid = h.machineid
LEFT JOIN  (SELECT machineid, SUM(CASE WHEN examname = 'Chest AP (Portable)' THEN 1 ELSE imagecount END) AS 總量
            FROM risworklistdatas
            WHERE 1=1
                AND modality = 'CR'
                AND examname NOT IN ('IVP', '虛擬醫令')
                AND orderfrom IN ('OPDR', 'OPDE', 'IPD', 'H')
                AND examdate BETWEEN
                    TO_DATE( '{the_month}', 'yyyy-mm-dd' )
                        AND
                    TO_DATE( '{the_next_month}', 'yyyy-mm-dd' )
            GROUP BY machineid) t
ON w.machineid = t.machineid
LEFT JOIN  (SELECT machineid, SUM(CASE WHEN examname = 'Chest AP (Portable)' THEN 1 ELSE imagecount END) AS 前月總量
            FROM risworklistdatas
            WHERE 1=1
                AND modality = 'CR'
                AND examname NOT IN ('IVP', '虛擬醫令')
                AND orderfrom IN ('OPDR', 'OPDE', 'IPD', 'H')
                AND examdate BETWEEN
                    TO_DATE( '{the_prev_month}', 'yyyy-mm-dd' )
                        AND
                    TO_DATE( '{the_month}', 'yyyy-mm-dd' )
            GROUP BY machineid) lt
ON w.machineid = lt.machineid
LEFT JOIN  (SELECT machineid, COUNT(*) AS 未RCP
            FROM risworklistdatas
            WHERE 1=1
                AND modality = 'CR'
                AND datastatus IN ( 'IMAGEDONE', 'SHIFT', 'CHECKIN', 'NEW' )
                AND examname NOT IN ('IVP', '虛擬醫令')
                AND orderfrom IN ('OPDR', 'OPDE', 'IPD', 'H')
                AND examdate BETWEEN
                    TO_DATE( '{the_month}', 'yyyy-mm-dd' )
                        AND
                    TO_DATE( '{the_next_month}', 'yyyy-mm-dd' )
            GROUP BY machineid) nr
ON w.machineid = nr.machineid
LEFT JOIN  (SELECT machineid, COUNT(*) AS 未Verify
            FROM risworklistdatas
            WHERE 1=1
                AND modality = 'CR'
                AND datastatus = 'RCP'
                AND imagecount > 0
                AND examname NOT IN ('IVP', '虛擬醫令')
                AND orderfrom IN ('OPDR', 'OPDE', 'IPD', 'H')
                AND examdate BETWEEN
                    TO_DATE( '{the_month}', 'yyyy-mm-dd' )
                        AND
                    TO_DATE( '{the_next_month}', 'yyyy-mm-dd' )
            GROUP BY machineid) nv
ON w.machineid = nv.machineid
WHERE 1=1
    AND modality = 'CR'
    AND SUBSTR(w.machineid, 1, 2) IN ('CR', 'DR')
    AND examdate BETWEEN
        TO_DATE( '{the_month}', 'yyyy-mm-dd' )
            AND
        TO_DATE( '{the_next_month}', 'yyyy-mm-dd' )
ORDER BY SUBSTR(w.machineid, 1, 1) DESC, TO_NUMBER(SUBSTR(w.machineid, 3)) ASC
    '''.format(the_month=the_month, the_prev_month=the_prev_month, the_next_month=the_next_month)
    df1 = pd.read_sql_query(sql_get_stats, db_engine)

    sql_get_stats = '''
SELECT CASE
        WHEN orderfrom = 'H' THEN '健'
        WHEN orderfrom = 'IPD' THEN '住'
        WHEN orderfrom = 'OPDE' THEN '急'
        WHEN orderfrom = 'OPDR' THEN '門'
        ELSE orderfrom END orderfrom, 總量, 前月總量, delta
FROM (
SELECT DISTINCT w.orderfrom,
    NVL(總量, 0) 總量,
    NVL(前月總量, 0) 前月總量,
    CASE
        WHEN NVL(前月總量, 0) > 0 THEN ROUND(100 * (NVL(總量, 0) - NVL(前月總量, 0)) / NVL(前月總量, 0), 1)
        ELSE -99999
    END delta
FROM risworklistdatas w
LEFT JOIN  (SELECT orderfrom, SUM(CASE WHEN examname = 'Chest AP (Portable)' THEN 1 ELSE imagecount END) AS 總量
            FROM risworklistdatas
            WHERE 1=1
                AND modality = 'CR'
                AND SUBSTR(machineid, 1, 2) IN ('CR', 'DR')
                AND orderfrom IN ('OPDR', 'OPDE', 'IPD', 'H')
                AND examname NOT IN ('IVP', '虛擬醫令')
                AND examdate BETWEEN
                    TO_DATE( '{the_month}', 'yyyy-mm-dd' )
                        AND
                    TO_DATE( '{the_next_month}', 'yyyy-mm-dd' )
            GROUP BY orderfrom) t
ON w.orderfrom = t.orderfrom
LEFT JOIN  (SELECT orderfrom, SUM(CASE WHEN examname = 'Chest AP (Portable)' THEN 1 ELSE imagecount END) AS 前月總量
            FROM risworklistdatas
            WHERE 1=1
                AND modality = 'CR'
                AND SUBSTR(machineid, 1, 2) IN ('CR', 'DR')
                AND orderfrom IN ('OPDR', 'OPDE', 'IPD', 'H')
                AND examname NOT IN ('IVP', '虛擬醫令')
                AND examdate BETWEEN
                    TO_DATE( '{the_prev_month}', 'yyyy-mm-dd' )
                        AND
                    TO_DATE( '{the_month}', 'yyyy-mm-dd' )
            GROUP BY orderfrom) lt
ON w.orderfrom = lt.orderfrom
WHERE 1=1
    AND modality = 'CR'
    AND SUBSTR(w.machineid, 1, 2) IN ('CR', 'DR')
    AND w.orderfrom IN ('OPDR', 'OPDE', 'IPD', 'H')
    AND w.examname NOT IN ('IVP', '虛擬醫令')
    AND examdate BETWEEN
        TO_DATE( '{the_month}', 'yyyy-mm-dd' )
            AND
        TO_DATE( '{the_next_month}', 'yyyy-mm-dd' )
ORDER BY w.orderfrom DESC
)
    '''.format(the_month=the_month, the_prev_month=the_prev_month, the_next_month=the_next_month)
    df2 = pd.read_sql_query(sql_get_stats, db_engine)
    #df2 = df2.T
    #print(df.to_string())
    return [df1, df2]
