# -*- coding: utf-8 -*-
from flask import Flask, request, render_template
import datetime
app = Flask(__name__)
file_sensor = "./sensor_data.csv"
file_key = "./key_data.csv"
file_result = "./result_data.csv"

port_num = 17086

#残りserverで実装すること

#利用時間外の設定
#時間変動による閾値の更新
#センサーからの情報を情量も受け取るverに変更
#リロード時の履歴追加
#更新時刻を正しく設定


#閾値・測定値の初期設定
Threshold_Key = 10
Threshold_Light = 10
Now_Key = 0
Now_Light = 0

#現在時刻を取得する関数
def reload_time():
    date=datetime.datetime.now()
    now_time=str(date.month)+"月"+str(date.day)+"日 "+str(date.hour)+"時"+str(date.minute)+"分"
    return now_time

def Check_Usable():
    #利用時間外の場合には0を返すようにする
    return 1

def Update_Threshold(situation):
    #print(situation)
    try:
        f = open(file_sensor,'r')
        for row in f:
            lux = row
        data = lux.split(',')
        Now_Light=int(data[1])
    except Exception as e:
        print("FILE OPEN ERROR")
    finally:
        f.close()
    try:
        f = open(file_key,'r')
        for row in f:
            lux = row
        data = lux.split(',')
        Now_Key=int(data[1])
    except Exception as e:
        print("FILE OPEN ERROR")
    finally:
        f.close()

    if situation == "1":
        New_Light = Now_Light - 50
        New_Key = Now_Key - 50
    elif situation == "2":
        New_Light = Now_Light + 50
        New_Key = Now_Key + 50
    elif situation == "3":
        New_Light = Now_Light - 10
        New_Key = Now_Key + 50
    elif situation == "4":
        New_Light = Now_Light + 50
        New_Key = Now_Key - 50
    elif situation == "5":
        New_Light = Now_Light + 50
        New_Key = Now_Key + 50

    global Threshold_Light
    global Threshold_Key
    Threshold_Light = New_Light
    Threshold_Key = New_Key

def Update_Judge():

    try:
        f = open(file_sensor,'r')
        for row in f:
            lux = row
        data = lux.split(',')
        Now_Light=int(data[1])
    except Exception as e:
        print("FILE OPEN ERROR")
    finally:
        f.close()
    try:
        f = open(file_key,'r')
        for row in f:
            lux = row
        data = lux.split(',')
        Now_Key=int(data[1])
    except Exception as e:
        print("FILE OPEN ERROR")
    finally:
        f.close()

    if Now_Key >= Threshold_Key:#解錠中
        if Now_Light >= Threshold_Light:#照明on
            Result = 1
        else:
            Result = 4
    else:#施錠中
        if Now_Light >= Threshold_Light:
            Result = 3
        else:
            if (Check_Usable()==1):
                Result = 2
            else:
                Result = 5
    #print(Result)
    now_time = reload_time()
    f = open(file_result,'w')
    f.write(now_time+","+str(Result))
    f.close()

#初期接続
@app.route('/', methods=['GET'])
def get_html():
    return render_template('./index.html')
#css,jsファイル読み込み
@app.route('/<files>', methods=['GET'])
def get_files(files):
    return render_template('./'+files)

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
    Update_Judge()
    try:
        f = open(file_result,'r')
        for row in f:
            lux = row
    except Exception as e:
        print("FILE OPEN ERROR")
        lux = "0,0"
    finally:
        f.close()
        return lux

#手動入力用 強制的に閾値を更新することで状態を更新してる
@app.route('/demo/<situation>',methods=['GET'])
def get_situation_demo(situation):
    Update_Threshold(situation)
    return "0,0"

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=port_num)
