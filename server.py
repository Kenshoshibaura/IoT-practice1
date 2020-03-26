# -*- coding: utf-8 -*-
from flask import Flask, request, render_template
import datetime
app = Flask(__name__)
file_sensor = "./sensor_data.csv"
file_key = "./key_data.csv"
file_result = "./result_data.csv"

port_num = 17086

def reload_time():
    date=datetime.datetime.now()
    now_time = str(date.month) + "月" + str(date.day) + "日 " + str(date.hour) + "時" + str(date.minute) + "分"
    return now_time

print("HELLO")
now_time = reload_time()
print(now_time)
@app.route('/', methods=['GET'])
def get_html():
    return render_template('./index.html')

@app.route('/lux', methods=['POST'])
def update_lux():
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

@app.route('/lux/<select>',methods=['GET'])
def get_lux_select(select):
    now_time = reload_time()
    f = open(file_result,'w')
    f.write(now_time+","+select)
    f.close()
    #この後の３行は暫定　最終的には閾値を変えるだけで直接は書き換えない
    f = open(file_key,'w')
    f.write(now_time+","+select)
    f.close()

    print(select)

    #ユーザ入力による状態変動なので閾値を更新する処理を行う

    try:
        f = open(file_result,'r')
        for row in f:
            select = row
    except Exception as e:
        print("FILE OPEN ERROR")
        select = "0,0"
    finally:
        f.close()
        return select

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=port_num)
