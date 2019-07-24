#-*- coding: utf-8 -*-

from flask import Flask, g, make_response, request, Response
from datetime import datetime, date
from flask import session

app = Flask(__name__)
app.debug = True # debug mode on
# app.config['SERVER_NAME'] = 'local.com:5000'

app.config.update(MAX_CONTEXT_LENGTH=1024*1024) # client가 올릴 수 있는 용량 제한

app.secret_key = 'x12343yRH!mMwf' # app에 설정했으므로 모든 session이 공유

app.config.update(
    SECRET_KEY='x12343yRH!mMwf',
    SESSION_COOKIE_NAME='hororok',
    PERMANENT_SESSION_LIFETIME=11
)

@app.before_first_request
def before_first_request():
    """
    request 요청 처음에만
    """

@app.before_request
def before_request():
    """
    매 번의 request시 호출
    app.route()의 경로가 어디든 before_request()는 호출됨
    1. filter 역할도 해줄 수 있다는 것임
    2. DB connection 열기
    """
    print("before request!!")
    g.str = "한글" # g : application context(모든 유저가 사용 가능)

# @app.after_request
# def after_request():
#     """
#     매번 request가 종료되는 시점
#     response가 끈나고 불리
#     1. DB connection 닫기
#     """
#     pass

@app.teardown_request
def teardown_request(Exception):
    """
    after_reqeust 후에 실행
    오류처리
    """
    pass

@app.teardown_appcontext
def teardown_appcontext(Exception):
    """
    app context 끝나고 불림
    """
    pass

@app.route('/')
def helloworld():
    return "Hello Flask World"

@app.route('/') # methods를 지정 안해주면 get방식만 가능
def test_get():
    pass

@app.route('/test', methods=['POST', 'PUT']) # post, put 일때 이 메소드 호출
def test_post_put():
    pass

@app.route('/test/<tid>') # tid는 변수로 받고 사용 가능
def test_tid(tid):
    print("tid is", tid)

@app.route('/test', defaults={'page': 'index'}) # page값이 안넘어올 경우 default로 index라는 값을 가진다
@app.route('/test/<page>') # page값에 따라 다르게 이동
def test_default(page):
    pass

@app.route('/test', host='abc.com') # 같은 uri라도 도메인에 따라 처리가 가능
def test_host():
    pass

@app.route('/test', redirect_to='/new_test') # methods를 지정 안해주면 get방식만 가능
def test_redirect_to():
    pass

@app.route('/', subdomain='g') # subdomain도 지정 가능
def helloworld3():
    return "Hello G.Local.com!!!"

@app.route('/gg')
def helloworld2():
    return "Hello Flask World" + getattr(g, 'str', '111') # 현재 접속자, 방문자 수 처럼 공유해서 사용하는 것에 응용 가능

@app.route('/res1')
def res1():
    custom_res = Response("Custom Response", 200, {'test': 'ttt'})
    return make_response(custom_res)

@app.route('/rp')
def rp():

    # 모두 multi dic type
    q = request.args.get('q') # GET

    request.form.get('p', 123) # GET, p가 안들어 오면 default로 123을 지정
    request.values.get('v') # GET, POST 모두 다 받기 가능
    request.args.getlist('qs') # list 형태로 받음 ex) /rp?q=한글&q=영어

    return "q=%s" % str(q)

# request 처리용 함수
# 함수 처리로 해야 실행 시간이 빠르다. 객체가 1개만 생성되므로
def ymd(fmt):
    def trans(date_str):
        return datetime.strptime(date_str, fmt)
    return trans

@app.route('/dt')
def dt():
    datestr = request.values.get('date', date.today(), type=ymd('%Y-%m-%d')) # date값이 안 넘어 오면 date.today()가 default. request로 넘어온 값의 type을 ymd()타입으로 바꿔 주세요~
    return "우리나라 시간 형식 : " + str(datestr)

# WSGT(SebServer Gateway Interface)
@app.route('/test_wsgi')
def wsgi_test():
    def application(environ, start_response): # environ: request에 대한 환경변수
        body = 'The request method was %s' % environ['REQUEST_METHOD']
        headers = [('Content-Type','text/plain'), ('Content-Length', str(len(body)))]
        start_response('200 OK', headers)

        return [body]
    
    return make_response(application)

@app.route('/reqenv')
def reqenv():
    """
    request environment
    """
    return ('REQUEST_METHOD: %(REQUEST_METHOD) s <br>'
            'PATH_INFO: %(PATH_INFO) s <br>'
    ) % request.environ

@app.route('/wc') # /wc?key=token&val=abc
def wc():
    """
    write cookie
    """
    key = request.args.get('key')
    val = request.args.get('val')
    res = Response("SET COOKIE")
    res.set_cookie(key, val)

    return make_response(res)

@app.route('/rc') # /wc?key=token&val=abc
def rc():
    """
    read cookie
    """
    key = request.args.get('key') # token
    val = request.cookies.get(key)
    
    return "cookie[" + key + "] = " + val

@app.route('/setsess')
def setsess():
    session['Token'] = '123x'

    return "Session이 설정되었습니다!"

@app.route('/getsess')
def getsess():
    return session.get('Token')

@app.route('/delsess')
def delsess():
    if session.get('Token'):
        del session['Token']
    
    return "Session이 삭제되었습니다! "