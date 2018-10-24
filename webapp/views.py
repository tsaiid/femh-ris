# -*- coding: utf-8 -*-

from webapp import app
from flask import jsonify, request, render_template
#from flask_cors import cross_origin
from reports import get_similar_recent_report
from reports import get_plain_film_counts
from datetime import date

@app.route('/')
def index():
    return 'Hello World!'

@app.route('/recent-similar-report/<accno>')
def get_report(accno):
    report, info, err, debug = get_similar_recent_report(accno)

    result_dict = {
        'report': report,
        'info': info,
        'err': err,
        'debug': debug
    }
    return jsonify(result_dict)

@app.route('/plain-film-count/<dr_id>')
def get_month_plain_film_count(dr_id):
    counts = get_plain_film_counts(dr_id)
    return render_template('plain-film-counts.html', counts=counts, date_str=date.today().strftime("%Y/%m"))

@app.route('/plain-film-count/<dr_id>/today')
def get_today_plain_film_count(dr_id):
    counts = get_plain_film_counts(dr_id, mode='today')
    return render_template('plain-film-counts.html', counts=counts, date_str=date.today().strftime("%Y/%m/%d"))
