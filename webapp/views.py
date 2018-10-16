# -*- coding: utf-8 -*-

from webapp import app
from flask import jsonify, request
#from flask_cors import cross_origin
from .reports import get_similar_recent_report

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
