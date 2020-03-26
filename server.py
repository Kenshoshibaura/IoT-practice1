# -*- coding: utf-8 -*-
from flask import Flask, request, render_template
import datetime
app = Flask(__name__)
file_sensor = "./sensor_data.csv"
file_key = "./key_data.csv"
file_result = "./result_data.csv"

port_num = 17086

#現在時刻を取得する関数
def reload_time():
    date=datetime.datetime.now()
    now_time=str(date.month)+"月"+str(date.day)+"日 "+str(date.hour)+"時"+str(date.minute)+"分"
    return now_time

#初期接続
@app.route('/', methods=['GET'])
def get_html():
    return render_template('./index.html')

#センサからのデータを受信、データを更新
@app.route('/lux', methods=['POST'])
def update_lux():
    #現在は照度センサの値の更新のみだが、鍵の情報更新もここに追加
    time=request.form["time"]
    lux=request.form["lux"]
    now_time = reload_time()
    try:
        f = open(file_sensor,'w')
        f.write(now_time + "," + lux)
        return "succeeded to write"
    except Exception as e:
        print(e)
        return "failed to write"
    finally:
        f.close()

#クライアントからの更新要求 resultの中身を読んで返す
@app.route('/lux',methods=['GET'])
def get_lux():
    lux = "0,0"
    try:
        f = open(file_result,'r')
        for row in f:
            lux = row
    except Exception as e:
        #print(e)
        print("FILE OPEN ERROR")
        lux = "0,0"
    finally:
        f.close()
        return lux

#デモ入力用 強制的に各ファイルを書き換えてる result以外は閾値を更新する関数を作って呼び出す必要あり
@app.route('/demo/<situation>',methods=['GET'])
def get_situation_demo(situation):
    now_time = reload_time()
    if situation == "1":
        lite = "100"
        key = "0"
    elif situation == "2":
        lite = "0"
        key = "1"
    elif situation == "3":
        lite = "100"
        key = "1"
    elif situation == "4":
        lite = "0"
        key = "0"
    elif situation == "5":
        lite = "0"
        key = "1"
    else:
        lite = "0"
        key = "1"

    f = open(file_result,'w')
    f.write(now_time+","+situation)
    f.close()

    #今はここで直接書き換えてる
    f = open(file_sensor,'w')
    f.write(now_time+","+lite)
    f.close()
    f = open(file_key,'w')
    f.write(now_time+","+key)
    f.close()

    return "0,0"

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=port_num)
