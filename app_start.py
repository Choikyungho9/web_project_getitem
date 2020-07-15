from __future__ import with_statement
from sqlalchemy import create_engine
from flask import Flask, url_for, render_template, request, redirect, session, jsonify, make_response, abort, g, flash
#pip install Flask-SQLAlchemy cmd창에서 설치해야함
from flask_sqlalchemy import SQLAlchemy
from pip._vendor.appdirs import user_data_dir
from sqlalchemy import desc
from datetime import datetime
import time
from sqlalchemy.sql.expression import null
from _hashlib import new
from sqlite3 import dbapi2 as sqlite3
from _dummy_thread import error
from contextlib import closing
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename


DATABASE = 'getitem.db'
PER_PAGE = 30



app = Flask(__name__) # app 초기화
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///getitem.db'

#파일 업로드 용량 제한
app.config['MAX_CONTENT_LENGTH'] = 16*1024*1024

db2 = SQLAlchemy(app)
app.config.from_object(__name__)
# 
def connect_db():
    """DB 연결 후 Connection객체 반환, DB 없으면 내부적으로 새로 생성됨."""
    return sqlite3.connect(app.config['DATABASE'])


class User(db2.Model):
    __tablename__ = 'users'

    id = db2.Column(db2.Integer,  primary_key = True) # 시퀀스 추가
    name = db2.Column(db2.String)
    email = db2.Column(db2.String)
    password = db2.Column(db2.String)
    phone = db2.Column(db2.String)
    address = db2.Column(db2.String)

    def __init__(self, name, email, password, phone, address):
        self.name = name
        self.email = email
        self.password = password
        self.phone = phone
        self.address = address
   
    def __repr__(self):
        return"<User('%s', '%s', '%s', '%s', '%s')>" % (self.name, self.email, self.password, self.phone, self.address)


class Product(db2.Model):
    __tablename__ = 'product'
    
    id = db2.Column(db2.Integer, primary_key = True) # 시퀀스 추가
    author_id = db2.Column(db2.Integer)
    title = db2.Column(db2.String)
    picture = db2.Column(db2.String)
    start_val = db2.Column(db2.String)
    current_val = db2.Column(db2.String)
    immediate_val = db2.Column(db2.String)
    days = db2.Column(db2.Integer)
    board = db2.Column(db2.String)
    now_date = db2.Column(db2.Integer)

    def __init__(self, author_id, title, picture, start_val, current_val, immediate_val, days, board, now_date):
        self.author_id = author_id
        self.title = title
        self.picture = picture
        self.start_val = start_val
        self.current_val = current_val
        self.immediate_val = immediate_val
        self.days = days
        self.board = board
        self.now_date = now_date
   
    def __repr__(self):
        return"<Product('%d', '%s', '%s', '%s', '%s', '%s', '%d', '%s', '%d')>" % (self.author_id, self.title, self.picture, self.start_val,
                                                      self.current_val, self.immediate_val,
                                                       self.days, self.board, self.now_date)

class Message(db2.Model):
    __tablename__ = 'message'
    
    id = db2.Column(db2.Integer, primary_key = True) # 시퀀스 추가
    author_id = db2.Column(db2.String)
    text = db2.Column(db2.String)
    pub_date = db2.Column(db2.Integer)


    def __init__(self, author_id, text, pub_date):
        self.author_id = author_id
        self.text = text
        self.pub_date = pub_date
   
    def __repr__(self):
        return"<Message('%s', '%s', '%d')>" % (self.author_id, self.text, self.pub_date)

""" 파싱해주는 함수 """
def query_db(query, args=(), one=False):
    """Queries the database and returns a list of dictionaries."""
    """ g는 전역객체, fetchall():조회할때 쓰는 메소드"""
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

@app.before_request
def before_request():
    """http 요청이 올 때마다 실행 : db연결하고 전역 객체 g에 저장하고 세션에 userid가 저장되어 있는지 체크해서 user 테이블로부터 user 정보 조회 한 후에 전역 객체 g에 저장 """
    g.db=connect_db()


@app.route("/")
def home():
    user=User.query.filter_by(id=session['user_id']).first() # 로그인한 유저 정보
    product_deadline=Product.query.order_by(Product.now_date.asc()).limit(3)
    return render_template('index.html', product_head=product_deadline)

##
    
def format_datetime(timestamp):
    """ 정수값에 해당하는 날짜 시간 포맷 형식 변경해서 문자열로 반환하는 함수 """
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d  %H:%M')

app.jinja_env.filters['datetimeformat'] = format_datetime
""" jinja 템플릿 엔진에 filter로 등록 => html페이지에서 필터처리할 때 사용됨"""
# template engine jinja에 이름을 지정(datetimeformat)하고 format_datetime(우리가 위에서 만든 함수)를 넣어준다


# 
# #app.route("/board/list", method = ['GET', 'POST']) 뒤의 method를 작성하지 않으면 default 값으로 GET이 셋팅됨
# @app.route("/board/list", methods=['GET', 'POST'])
# def boardlist():
#     boardlist = Boards.query.order_by(desc(Boards.id)).all()
#     return render_template("bbslist.html", boards = boardlist)
#     
# # 새 게시글 추가하는 뷰 함수
# @app.route("/board/new")
# def boardNew():
#     user=User.query.filter_by(id=session['user_id']).first()
#     return render_template("bbsform.html", username=user.name)
# 
# @app.route("/board/add" , methods=['GET', 'POST'])
# def addPost():  
#     new_post = Boards(writer=request.form['writer'], title = request.form['title'],   content = request.form['content'] , regdate = int(time.time()), reads=0)
#     db.session.add(new_post)
#     db.session.commit()                                           
#     return redirect(url_for("boardlist"))   #get요청
# #get요청
# 
@app.route("/single-product/<int:product_id>")
def viewProduct(product_id=None):
    post = Product.query.filter_by(id=product_id).first()
    post.reads=post.reads+1
    db2.session.commit()
    return render_template("bbsview.html", bbs = post)
# 
# @app.route("/board/edit",methods=['POST', 'GET'])
# def editPost():
#     post = Boards.query.filter_by(id=request.form["bbsid"]).first()
#     return render_template("bbsedit.html",bbs=post)
# 
# @app.route("/board/save", methods=['POST', 'GET'])
# def savePost():
#     post = Boards.query.filter_by(id=request.form["bbsid"]).first()
#     post.title = request.form["title"]
#     post.content = request.form["content"]
#     #post.reads=post.reads+1
#     db.session.commit()
#     return redirect(url_for("boardlist"))
# 
# @app.route("/board/delete", methods=['POST','GET'])
# def removePost():
#     post = Boards.query.filter_by(id=request.form["bbsid"]).first()
#     db.session.delete(post)
#     db.session.commit()
#     return redirect(url_for("boardlist"))   



@app.route("/login", methods=['GET','POST'])
def login():
    if request.method=='GET':
        return render_template("login.html")
        error = None
    else:
        uname=request.form['username']
        upasswd=request.form['password']
        try:
            user_data = User.query.filter_by(name=uname, password=upasswd).first()
            if user_data is not None : 
                session['user_id']=user_data.id
                session['logged_in']=True
                return redirect(url_for('home'))
            else:
                error = "ID가 존재하지 않거나 비밀번호가 일치하지 않습니다."
                return render_template("login.html", error=error)
        except :
            error = "DB조회중에 에러가 발생했습니다."
            return render_template("login.html", error=error)


@app.route("/register", methods=['GET', 'POST'])
def register():
    """get방식  요청은 reighter.html 응답 전송 post 방식 요청은 db에 회원 정보 추가하고 login페이지로 redirect시킵니다"""
    if request.method=='POST':
        new_user = User(name=request.form['username'],
                        email= request.form['emailid']+'@'+request.form['emailadd'],
                        password = request.form['password'],
                        phone = request.form['txtMobile1']+'-'+request.form['txtMobile2']+'-'+request.form['txtMobile3'],
                        address = '')
        if (request.form['username'] and request.form['password'] and request.form['emailid'] and request.form['emailadd']) == '':
            if  request.form['username'] == '':
                error = "ID는 필수 입력 사항입니다."
                return render_template("register.html", error=error)
            elif request.form['password'] == '':
                error = "비밀번호는 필수 입력 사항입니다."
                return render_template("register.html", error=error)
            elif (request.form['emailid'] or request.form['emailadd']) == '' :
                error = "E-mail은 필수 입력 사항입니다."
                return render_template("register.html", error=error)
        
        if request.form['password']==request.form['confirmPassword']: # 비밀번호 확인이 일치하면 commit 시킨다.
            db2.session.add(new_user)
            db2.session.commit()
            return render_template("login.html", error = None)
        else:
            error = "입력하신 비밀번호와 비밀번호 확인값이 일치하지 않습니다."
            return render_template("register.html", error=error)
    else:
        return render_template("register.html", error = None)
 
 
@app.route("/single-product", methods=['GET', 'POST'])
def single_product():
    """get방식  요청은 reighter.html 응답 전송 post 방식 요청은 db에 회원 정보 추가하고 login페이지로 redirect시킵니다"""
    user=User.query.filter_by(id=session['user_id']).first()
    if request.method=='POST':
        quest_msg = Message(author_id=session['user_id'], text=request.form['text'], pub_date=int(time.time()))
        if not session['logged_in']:
            return render_template("login.html")
        else:
            db2.session.add(quest_msg)
            db2.session.commit()
            flash('메시지가 저장되었습니다.')
            return render_template('single-product.html', messages=query_db('''
                                    select message.*, users.* from message, users
                                    where message.author_id = users.id
                                    order by message.pub_date desc limit ?''', [PER_PAGE]))
    else:
        return render_template("single-product.html", messages=query_db('''
                                    select message.*, users.* from message, users
                                    where message.author_id = users.id
                                    order by message.pub_date desc limit ?''', [PER_PAGE]))

''' 문의 게시판  (데모) '''
@app.route('/add_message', methods=['GET', 'POST'])
def add_message():
    if not session['logged_in']:
        return render_template("login.html")
    user=User.query.filter_by(id=session['user_id']).first()
    quest_msg = Message(author_id=session['user_id'], text=request.form['text'], pub_date=int(time.time()))
    db2.session.add(quest_msg)
    db2.session.commit()
    flash('메시지가 저장되었습니다.')
    return render_template('single-product.html', messages=query_db('''
        select message.*, users.* from message, users
        where message.author_id = users.id
        order by message.pub_date desc limit ?''', [PER_PAGE]))

''' 경매 내역 보기 '''
@app.route("/bidder")
def bidder():
    if session['logged_in']:
        return render_template("bidder.html")
    else:
        return render_template("login.html")

    
''' 마이 페이지 '''
@app.route("/mypage")
def mypage():
    if session['logged_in']:
        return render_template("mypage.html")
    else:
        return render_template("login.html")  
########################## 마이페이지 여섯가지 목록 ###########################  
''' 입찰 내역 '''
@app.route("/bid_list")
def bid_list():
    if session['logged_in']:
        return render_template("bid_list.html")
    else:
        return render_template("login.html")

''' 찜목록 '''
@app.route("/favorite_list")
def favorite_list():
    if session['logged_in']:
        return render_template("favorite_list.html")
    else:
        return render_template("login.html")

''' 내가 보낸 문의 '''
@app.route("/myboard")
def myboard():
    if session['logged_in']:
        return render_template("myboard.html")
    else:
        return render_template("login.html")
    

''' 낙찰 내역  '''
@app.route("/sbid_list")
def sbid_list():
    if session['logged_in']:
        return render_template("sbid_list.html")
    else:
        return render_template("login.html")

''' 회원 정보 수정  '''
@app.route("/mchange", methods=['GET', 'POST'])
def mchange():
    user_data = User.query.filter_by(id=session['user_id']).first()
    if not session['logged_in']:
        return render_template("login.html") #로그인 안되어 있으면 로그인 화면으로
    if request.method == 'GET':
        return render_template("mchange.html", user=user_data)
    else:
        edit_user = User.query.filter_by(id=session['user_id']).first()
        edit_user.password = request.form['password']
        edit_user.email = request.form['emailid']+'@'+request.form['emailadd']
        edit_user.phone = request.form['txtMobile1']+'-'+request.form['txtMobile2']+'-'+request.form['txtMobile3']
        edit_user.address = request.form['address']

        if (request.form['password'] and request.form['emailid'] and request.form['emailadd']) == '':
            if request.form['password'] == '':
                error = "비밀번호란이 입력되지 않았습니다."
                return render_template("mchange.html", error=error, user=user_data)
            elif (request.form['emailid'] or request.form['emailadd']) == '' :
                error = "E-mail란이 입력되지 않았습니다."
                return render_template("mchange.html", error=error, user=user_data)
        if request.form['password'] == request.form['confirmPassword']:
            db2.session.add(edit_user)
            db2.session.commit()
            return render_template("mchange.html", error = None, user=user_data)
        else:
            error = "입력하신 비밀번호와 비밀번호 확인값이 일치하지 않습니다."
            return render_template("mchange.html", error=error, user=user_data)

''' 상품 등록  '''
@app.route("/pdregister")
def pdregister():
    if not session['logged_in']:
        return render_template("login.html")
    else:
        user_data = User.query.filter_by(id=session['user_id']).first()
        return render_template("pdregister.html", user=user_data)

############################## 상품등록 이미지 파일 관련 ################################
@app.route('/pdregister/uploader', methods = ['GET', 'POST'])
def pdregister_uploadFile():
    user_data = User.query.filter_by(id=session['user_id']).first()
    if request.method == 'POST':
        f = request.files['product_img']
        picture = "./static/img/product_img/"+str(int(time.time()))+"_"+ secure_filename(f.filename)
        f.save(picture) #파일명을 보호하기 위한 메소드에 적용시킨 후 save
        g.db.execute('''insert into   product(author_id, title, picture, start_val, current_val, immediate_val, days, board, now_date)
        values (?, ?, ?, ?, ?, ?, ?, ?, ?)''',( session['user_id'],
                                request.form.get('product_name'), picture, request.form.get('initial_price'),
                                request.form.get('initial_price'), request.form.get('direct_price'),
                                request.form.get('days'), request.form.get('description'), int(time.time()) ) )
        g.db.commit()
        return render_template("pdregister.html", user=user_data)
#######################################################################################
   
#######################################################################################
# @app.route('/')
# def timeline():
#     """
#       전역 객체 g에 저장된 user 정보가 없으면 로그인 없이 볼 수 있는 public_timelie 으로 url을 요청하고,
#       전역 객체 g에 저장된 user 정보가  있으며 로그인한 user와 following한 user들이 작성한 트윗글을 
#       최신 작성 날짜 시간순으로 모두 조회해서 timeline.html페이지로 전달하고 응답
#     """
#     if not session['logged_in']:
#         return redirect(url_for('login'))
#     return render_template('timeline.html', messages=query_db('''
#         select message.*, user.* from message, user
#         where message.author_id = user.user_id and (
#             user.user_id = ? or
#             user.user_id in (select whom_id from follower
#                                     where who_id = ?))
#         order by message.pub_date desc limit ?''',
#         [session['user_id'], session['user_id'], PER_PAGE], False))
# 
# @app.route('/public')
# def public_timeline():
#     """로그인 안한 사용자 모두  볼수 있는 공개 트윗 글 목록 """
#     return render_template('timeline.html', messages=query_db('''
#         select message.*, user.* from message, user
#         where message.author_id = user.user_id
#         order by message.pub_date desc limit ?''', [PER_PAGE]))
# 
# 
# 
# 
# @app.route('/<username>')
# def user_timeline(username):
#     """로그인 한 사용자의 트윗글 목록과 following 사용자 트윗글 """
#     profile_user = query_db('select * from user where username = ?',
#                             [username], one=True)
#     if profile_user is None:
#         abort(404)
#     followed = False
#     if g.user:
#         followed = query_db('''select 1 from follower where
#             follower.who_id = ? and follower.whom_id = ?''',
#             [session['user_id'], profile_user['user_id']],
#             one=True) is not None
#     return render_template('timeline.html', messages=query_db('''
#             select message.*, user.* from message, user where
#             user.user_id = message.author_id and user.user_id = ?
#             order by message.pub_date desc limit ?''',
#             [profile_user['user_id'], PER_PAGE]), followed=followed,
#             profile_user=profile_user)    
# @app.route('/<username>/follow')
###############################################################################################    
    
@app.route("/logout")
def logout():
    session['logged_in'] = False
    session['user_id'] = None
    return redirect(url_for('home'))

@app.route("/unjoin")
def unjoin():
    try:
        user_data = User.query.filter_by(id=session['user_id']).first()
        print(user_data)
        db2.session.delete(user_data)
        db2.session.commit()
        session['logged_in'] = False
        session['user_id'] = None 
        return render_template("login.html")
    except:
        message = "회원정보 삭제중에 예외가 발생했습니다. -회원정보 삭제"
        return render_template("message.html", msg=message)


@app.route("/sell_product")
def sell_product():
    return render_template("sell_product.html")




if __name__ == '__main__':
    app.debug=True
#     db2.create_all() #테이블이 생성되고 나서는 주석처리해줌
    app.secret_key = '1234567890'
    app.run(host='0.0.0.0')