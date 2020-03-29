/*使い方
  - 初期設定
    -認証を行う時に使うURLを記入　-> auth_path
    -認証完了時に帰ってくる文字列については、authSync内のresult変数を利用したif文を加工する
    -認証方法はPOST, キー名はid,pass 変更時はauthSync内のfetch部分を改変

  -認証を行う時の呼び出し関数
    auth.init(実行したい関数,(※任意)[実行したい関数の引数(配列)],(※任意)記憶のチェックボックス);

*/
var auth= {
  auth_path:window.location.protocol + '//' + window.location.host+"/"+"auth",
  id:null,
  pass:null,
  popup:false,
  remember:false,
  target:null,
  args:[],
  last_auth:{user:null,mode:null},
  init: async function(fn,args = [],remember = true){
    this.target=fn;
    this.args=args;
    //console.log(this);
    var cookies = document.cookie;
    var cookiesArray = cookies.split(';');
    for(var c of cookiesArray){
      var cArray = c.split('=');
      if(cArray[0].match('id')){
        this.id = decodeURIComponent(cArray[1]);
      }
      if(cArray[0].match('pass')){
        this.pass = decodeURIComponent(cArray[1]);
        if(this.id != null){
          this.remember = true;
        }
      }
    }
    console.log(this.id);
    console.log(this.pass);
    console.log(this.remember);
    if(this.remember){
      await this.authSync();
    }else{
      this.show_popup(remember);
    }
  },
  show_popup: function(remember = true){
    if(this.popup){
      throw("Unexpected WindowOpen.");
    }
    this.popup=true;
    var div1 = document.createElement('div');
    div1.className = "bgAlert";
    var div2 = document.createElement('div');
    div2.className = "alert auth";
    var h2 = document.createElement('h2');
    h2.innerHTML = "認証";
    var p = document.createElement('p');
    var id= this.id;
    if(id==null) id="";
    p.innerHTML = "<label for='user'>ユーザー名:</label><input id='user' type='text' value="+id+">";
    p.innerHTML +="<br><label for='pass'>パスワード:</label><input id='pass' type='password'><br>";
    if(remember){
      p.innerHTML += "<input type=checkbox id='remember'><label for='remember'>ログイン状態を維持する</label>";
    }
    var errorLog = document.createElement('div');
    errorLog.id= "errorLog";
    errorLog.style.color="#F00";
    errorLog.innerHTML = "";
    var cancel =
    document.createElement('button');
    cancel.id="cancel_button";
    cancel.innerHTML = "キャンセル";
    cancel.setAttribute("onclick","auth.nodeBreak(this);");
    var okay = document.createElement('button');
    okay.id="okay_button";
    okay.style.background = "#5566FF";
    okay.addEventListener('click',this.authSync.bind(this),{once:true});
    okay.innerHTML  = "ログイン";
    div2.appendChild(h2);
    div2.appendChild(p);
    div2.appendChild(errorLog);
    div2.appendChild(cancel);
    div2.appendChild(okay);
    div1.appendChild(div2);
    document.getElementsByTagName('body')[0].appendChild(div1);
  },
  nodeBreak: function(remember = false){
    this.remember=false;
    this.id=null;
    this.pass=null;
    this.target=null;
    this.args=[];
    this.popup=false;
    var node = document.getElementById("okay_button").parentNode.parentNode;
    node.remove(node);
  },
  nodeFinish: function(remember = false){
    if(remember){
      this.remember=true;
      var m = 60 * 10;
      document.cookie = "id=" + encodeURIComponent(this.id)+";max-age="+m;
      document.cookie = "pass=" + encodeURIComponent(this.pass)+";max-age="+m;
      console.log("add cookies");
    }else{
      this.remember=false;
      this.id=null;
      this.pass=null;
    }
    this.target=null;
    this.args=[];
    this.popup=false;
    var node = document.getElementById("okay_button").parentNode.parentNode;
    node.remove(node);
  },
  authSync: async function(){
    if(this.popup){
      //this.id=document.getElementById("user").innerHTML;//
      //this.pass=document.getElementById("pass").innerHTML;//
      document.getElementById("okay_button").innerHTML="認証中...";
      document.getElementById("okay_button").disabled=true;
      document.getElementById("cancel_button").disabled=true;
      document.getElementById("pass").disabled=true;
      document.getElementById("user").disabled=true;
      this.id=document.getElementById("user").value;
      this.pass=document.getElementById("pass").value;
    }
    //console.log(this);
    var path = this.auth_path;
    //console.log(path);
    var form = new FormData();
    form.append('id',this.id);
    form.append('pass',this.pass);
    try{
      var result  =await (await fetch(path,{
        method: 'POST',
        body: form
      })).text();
    }catch(e){
      console.error(e);
      if(this.popup){
        document.getElementById("okay_button").innerHTML="ログイン";
        document.getElementById("okay_button").disabled=false;
        document.getElementById("cancel_button").disabled=false;
        document.getElementById("pass").disabled=false;
        document.getElementById("user").disabled=false;
      }else{
        this.remember=false;
        this.show_popup();
      }
      document.getElementById("errorLog").innerHTML="ネットワーク接続を確認してください。";
    }
    if (result.match("true")){
      this.last_auth.user=this.id;
      this.last_auth.mode=result;
      this.target(this.args,result);
      if(this.popup==true){
        if(document.getElementById('remember')){
          this.remember=document.getElementById("remember").checked;
        }
        this.nodeFinish(this.remember);
      }
    }else if(result=="false"){
      if(!this.popup){
        this.remember=false;
        this.show_popup();
      }else{
        document.getElementById("okay_button").innerHTML="ログイン";
        document.getElementById("okay_button").disabled=false;
        document.getElementById("cancel_button").disabled=false;
        document.getElementById("pass").disabled=false;
        document.getElementById("user").disabled=false;
        document.getElementById("okay_button").addEventListener('click',this.authSync.bind(this),{once:true});
      }
      document.getElementById("errorLog").innerHTML="ユーザー名・パスワードが間違えています。";
    }else{
      if(this.popup==false){
        this.remember=false;
        this.show_popup();
      }else{
        document.getElementById("okay_button").innerHTML="ログイン";
        document.getElementById("okay_button").disabled=false;
        document.getElementById("cancel_button").disabled=false;
        document.getElementById("pass").disabled=false;
        document.getElementById("user").disabled=false;
        document.getElementById("okay_button").addEventListener('click',this.authSync.bind(this),{once:true});
      }
      console.error("Unexpected result. Details -> warn");
      console.warn(result);
      document.getElementById("errorLog").innerHTML="不明なエラーが発生しました。";
    }
  }
}
