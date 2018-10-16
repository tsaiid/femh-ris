from webapp import db
import yaml
import os

def get_similar_recent_report(accno):
    report = {'examdate': '', 'accno': '', 'findings': '', 'impression': ''}
    info = []
    err = []
    debug = []

    # get exam map
    sim_cat_map_yml_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'sim_cat_map.yml')
    with open(sim_cat_map_yml_path, 'r') as ymlfile:
        sim_cat_map = yaml.load(ymlfile)

    # get worklist of cxr on the target date
    sql_get_worklist = '''
SELECT patid, examcode, examname
FROM risworklistdatas
WHERE accno = '{accno}'
    '''.format(accno=accno)
    results = db.engine.execute(sql_get_worklist)
    examinfo = [{'patid': row['patid'], 'examcode': row['examcode'], 'examname': row['examname']} for row in results]
    if examinfo:
        debug.append(examinfo)   # log
        examcode = examinfo[0]['examcode']
        sim_cat_list = sim_cat_map.get(examcode, [])
        if not sim_cat_list:
            info.append('Similar exam category is not defined: {}'.format(examcode))    # log
        sim_cat_list.append(examcode)   # always query sefl category
        exam_similar_list = ','.join("'{0}'".format(w) for w in sim_cat_list)
        info.append(exam_similar_list)  # log
        sql_get_report = '''
SELECT TO_CHAR(examdate, 'yyyy-mm-dd hh24:mi:ss') examdate_str, accno, findings, impression FROM (
    SELECT *
    FROM risworklistdatas w
    LEFT JOIN (
        SELECT reportid, itemname, textvalue AS findings FROM ristextdatas
        WHERE itemname = '1') t1
        ON w.reportid = t1.reportid
    LEFT JOIN (
        SELECT reportid, itemname, textvalue AS impression FROM ristextdatas
        WHERE itemname = '2') t2
        ON w.reportid = t2.reportid
    WHERE patid = '{patid}'
        AND examdate IS NOT NULL
        AND w.reportid IS NOT NULL
        AND examcode IN ({exam_similar_list})
        AND accno != '{accno}'
        AND findings IS NOT NULL
    ORDER BY examdate DESC
    )
WHERE ROWNUM = 1'''.format(patid=examinfo[0]['patid'], accno=accno, exam_similar_list=exam_similar_list)
        results = db.engine.execute(sql_get_report)
        similar_reports = [{'examdate': row['examdate_str'],
                            'accno': row['accno'],
                            'findings': row['findings'],
                            'impression': row['impression']} for row in results]
        if similar_reports:
            report['examdate'] = similar_reports[0]['examdate']
            report['accno'] = similar_reports[0]['accno']
            report['findings'] = similar_reports[0]['findings']
            report['impression'] = similar_reports[0]['impression']
        else:
            info.append('No available similar report.')
    else:
        info.append('No such exam.')

    return (report, info, err, debug)
