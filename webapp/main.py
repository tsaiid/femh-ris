# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
#from flask_cors import cross_origin
from .config import DevConfig
import reports

# 初始化 Flask 類別成為 instance
app = Flask(__name__)
app.config.from_object(DevConfig)
db = SQLAlchemy(app)

# 路由和處理函式配對
@app.route('/')
def index():
    return 'Hello World!'

@app.route('/recent-similar-report/<accno>')
def get_report(accno):
    report, info, err, debug = reports.get_similar_recent_report(accno, db.engine)

    result_dict = {
        'report': report,
        'info': info,
        'err': err,
        'debug': debug
    }
    return jsonify(result_dict)

# 判斷自己執行非被當做引入的模組，因為 __name__ 這變數若被當做模組引入使用就不會是 __main__
if __name__ == '__main__':
    #app.run(host='0.0.0.0', ssl_context=('ssl/fullchain.pem', 'ssl/privkey.pem'))
    #app.run(host='0.0.0.0')
    app.run(host='127.0.0.1')
