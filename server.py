# -*- coding: utf-8 -*-
from flask import Flask, request, render_template
import datetime
app = Flask(__name__)
file_sensor = "./sensor_data.csv"
file_key = "./key_data.csv"
file_result = "./result_data.csv"
file_log = "./log_data.csv"

port_num = 17086

#閾値・測定値の初期設定
Threshold_Key = 30
Threshold_Light = 10
Now_Key = 0
Now_Light = 0

#利用可能時間の設定
Start_Time = 700
Limit_Time = 2200

#閾値の周期変更値(辞書)
Cycle_Time = {'500':10, '800':12, '1300':15, '1700':12, '1800':11, '2100':10}

#桁揃え(0埋め)
def set2fig(x):
    if x > 9:
        return x
    else:
        return str(0)+str(x)

#現在時刻を取得する関数
def reload_time():
    date=datetime.datetime.now()
    now_time=str(date.month)+"月"+str(date.day)+"日 "+str(date.hour)+"時"+str(date.minute)+"分"
    return now_time

#ファイルの中身を調べ、第2項目の値(int)を返す
def data_from_file(file_path):
    try:
        f = open(file_path,'r')
        for row in f:
            lux = row
        data = lux.split(',')
        Now = int(data[1])
    except Exception as e:
        print("FILE OPEN ERROR")
        Now = 0
    finally:
        f.close()
        return Now

#利用可能時間かどうかを調べる
def Check_Usable():
    #利用時間外の場合には0を返すようにする
    date=datetime.datetime.now()
    Now_Minute = set2fig(date.minute)
    Now_Time = int(str(date.hour)+str(Now_Minute))
    if (Now_Time >= Start_Time) and (Now_Time < Limit_Time):
        return 1
    else:
        return 0

#特定の時間になると閾値を変更する
def Cycle_Threshold():
    date=datetime.datetime.now()
    Now_Minute = set2fig(date.minute)
    Now_Time = str(date.hour)+str(Now_Minute)
    if (Now_Time in Cycle_Time) is True:
        global Threshold_Light
        Threshold_Light = Cycle_Time[Now_Time]

#手動更新の際閾値を更新する(再起動するとリセットされるので注意)
def Update_Threshold(situation):

    Now_Light = data_from_file(file_sensor)
    Now_Key = data_from_file(file_key)

    if situation == "1":
        New_Light = Now_Light - 10
        New_Key = Now_Key - 30
    elif situation == "2":
        New_Light = Now_Light + 10
        New_Key = Now_Key + 30
    elif situation == "3":
        New_Light = Now_Light - 10
        New_Key = Now_Key + 30
    elif situation == "4":
        New_Light = Now_Light + 10
        New_Key = Now_Key - 30
    elif situation == "5":
        New_Light = Now_Light + 10
        New_Key = Now_Key + 30

    global Threshold_Light
    global Threshold_Key
    Threshold_Light = New_Light
    Threshold_Key = New_Key

#状態を更新
def Update_Judge():

    Now_Light = data_from_file(file_sensor)
    Now_Key = data_from_file(file_key)
    Now_Result = data_from_file(file_result)

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

    if Now_Result != Result:
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
@app.route('/<files>', methods=['POST'])
def post_files(files):
    id=request.form['id']
    password=request.form['pass']
    #print(id,password)
    result = "false"
    try:
        f = open("./user/user.txt",'r')
        for row in f:
            lux = row
            data = lux.split(',')
            if (data[0] == id) and (data[1] == password):
                result = "true," + data[2]
    except Exception as e:
        print("FILE OPEN ERROR")
    finally:
        f.close()
        return result

#センサからのデータを受信、データを更新
@app.route('/lux', methods=['POST'])
def update_lux():
    time=request.form["time"]
    lux=request.form["lux"]
    key=request.form["key"]
    now_time = reload_time()
    try:
        f = open(file_sensor,'w')
        f.write(now_time + "," + lux)
        f.close()
        f = open(file_key,'w')
        f.write(now_time + "," + key)
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
    Cycle_Threshold()
    try:
        f = open(file_result,'r')
        lux = f.read()
    except Exception as e:
        print("FILE OPEN ERROR")
        lux = "0,0"
    finally:
        f.close()
        return lux

#初期接続時にログデータを送信
@app.route('/getlog',methods=['GET'])
def send_log():
    lux = "0,0"
    try:
        f = open(file_log,'r')
        lux = f.read()
    except Exception as e:
        print("FILE OPEN ERROR")
        lux = "0,0"
    finally:
        f.close()
        return lux

#ログ受信用 4つ以上になった場合最新の4つ以外は削除する
@app.route('/log/<logtext>',methods=['GET'])
def get_log(logtext):

    f = open(file_log,'a')
    f.write(logtext+",")
    f.close()

    f = open(file_log,'r')
    logtext = f.read()
    data = logtext.split(',')
    quantity = len(data)
    f.close()

    if quantity > 4:
        f = open(file_log,'w')
        f.write(data[quantity-5]+","+data[quantity-4]+","+data[quantity-3]+","+data[quantity-2]+",")
        f.close()
    return "0,0"

#手動入力用 強制的に閾値を更新することで状態を更新してる
@app.route('/demo/<situation>',methods=['GET'])
def get_situation_demo(situation):
    Update_Threshold(situation)
    return "0,0"

#退室勧告用 コンソールにコメントを出すだけ
@app.route('/alert/<situation>',methods=['GET'])
def start_alert(situation):
    print("退室時刻です")
    return "0,0"

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=port_num)
