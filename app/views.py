# -*- coding: utf-8 -*-

from flask import render_template, flash, session, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, login_manager
from models import User, Board, Post, Reply
from forms import RegisterFrom, LoginForm, PostForm, ReplyForm, CompeteForm, SearchForm, ChangeForm
from sqlalchemy import text, func, extract, or_,and_,all_,any_
from datetime import datetime, date, timedelta
from dicttoxml import dicttoxml
from xml.dom.minidom import parseString
import sys
reload(sys)
sys.setdefaultencoding('utf8')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterFrom()
    if request.method == 'POST':
        if form.validate_on_submit():
            usr_name = form.data['usr_name']
            usr_email = form.data['usr_email']
            usr_password = form.data['usr_password']
            usr_birthday = form.data['usr_birthday']
            usr_gender = form.data['usr_gender']
            u = User(usr_name=usr_name, usr_password=usr_password,
                     usr_email=usr_email, usr_birthday=usr_birthday,
                     usr_gender=usr_gender)
            try:
                #print 'hello'
                #print(u)
                #print(form.data)
                db.session.add(u)
                db.session.commit()
                flash('signup successful')
            except Exception, e:
                return 'something goes wrong'
            return redirect(url_for('index'))
        else:
            print 'not validate'
            print form.errors
            print form.data
    return render_template('signup.html', form=form)

@login_manager.user_loader
def load_user(usr_name):
    print type(User.query.get(usr_name))
    print User.query.get(usr_name)
    return User.query.get(usr_name)
    #return db.session.query(User.usr_name).filter(User.usr_name == usr_name)

@app.route('/', methods=['GET', 'POST'])
def index():  # sign in page
    #post1 = Post(p_title='hhhh', p_content='1234', p_board='1', p_usrid='123')
    #db.session.add(post1)
    #db.session.commit()

    form = LoginForm()
    if request.method == 'POST':
        #print(form.data)
        if form.validate_on_submit():
            usr_name = form.data['usr_name']
            usr_password = form.data['usr_password']
            user = User.query.filter_by(usr_name=usr_name, usr_password=usr_password).first()
            if user:
                #print 'succeess'
                login_user(user)
                flash('sign in successful')
                #return render_template('login0.html',user=current_user, name=current_user.usr_name)
                return redirect(url_for('profile'))
                #return redirect(request.args.get('next') or url_for('index'))
            else:
                flash(u'用户名或者密码错误')
        else:
            print 'not validate'
    return render_template('signin.html', form=form)


@app.route('/signout')
@login_required
def signout():
    logout_user()
    flash('signout successful')
    return redirect('/')


@app.route('/profile')  # 个人主页，有个人信息以及发过的帖
@login_required
def profile():
    #return 'Welcome'
    query_obj = db.session.query(Post).filter(Post.p_usrid == current_user.usr_name)
    user_post_cnt = query_obj.count() # 这个人发了几个贴
    query_obj1 = db.session.query(Reply).filter(Reply.r_name == current_user.usr_name)
    usr_reply_cnt = query_obj1.count()  # 这个人的回复数
    post1 = query_obj.all()
    reply1 = query_obj1.all()
    post = []
    for i in range(len(post1)):
        if post1[i].p_title:
            p_title = post1[i].p_title
            p_board = post1[i].p_board
            p_clickcnt = post1[i].p_clickcnt
            p_replycnt = post1[i].p_replycnt
            p_time = post1[i].p_time.strftime("%Y-%m-%d %H:%M:%S")
            p_id = post1[i].p_id
            post.append({'p_title': p_title, 'p_board': p_board, 'p_clickcnt': p_clickcnt,
                       'p_replycnt': p_replycnt, 'p_time': p_time, 'p_id': p_id})
    reply = []
    for i in range(len(reply1)):
        query_obj2 = db.session.query(Post).filter(Post.p_id == reply1[i].r_title).first()
        if query_obj2:
            r_title = query_obj2.p_title
            r_time = reply1[i].r_time.strftime("%Y-%m-%d %H:%M:%S")
            r_agreecnt = reply1[i].r_agreecnt
            r_name = query_obj2.p_usrid
            r_board = query_obj2.p_board
            reply.append({'r_title': r_title, 'r_time': r_time, 'r_agreecnt': r_agreecnt,
                     'r_name': r_name, 'r_board': r_board, 'p_id': str(query_obj2.p_id)})

    #print reply

    usr_level = (user_post_cnt*5 + usr_reply_cnt*2)/10
    current_user.usr_level = usr_level
    db.session.commit()
    usr_regdate = current_user.usr_regdate.strftime("%Y-%m-%d %H:%M:%S")
    usr_birthday1 = datetime.strptime(current_user.usr_birthday, '%d/%m/%Y')
    today = date.today()
    usr_age = today.year - usr_birthday1.year - ((today.month, today.day) < (usr_birthday1.month, usr_birthday1.day))
    userposts = {
        'usr_name': current_user.usr_name,
        'usr_email': current_user.usr_email,
        'usr_birthday': current_user.usr_birthday,
        'usr_gender': current_user.usr_gender,
        'usr_role': current_user.usr_role,
        'post': post,
        'reply': reply,
        'user_post_cnt': user_post_cnt,
        'usr_reply_cnt': usr_reply_cnt,
        'usr_level': usr_level,
        'usr_regdate': usr_regdate,
        'usr_postcnt': user_post_cnt,
        'usr_replycnt': usr_reply_cnt,
        'usr_age': usr_age
    }
    return render_template('profile.html', user=userposts)


@app.route('/board/<board_name>', methods=['GET', 'POST'])
def board(board_name):
    if request.method == 'GET':
        form = SearchForm()
        query_obj = db.session.query(Board).filter(Board.b_name == board_name).first()
        b_id = query_obj.b_id
        b_postcnt = query_obj.b_postcnt
        b_master = query_obj.b_master
        b_name = query_obj.b_name
        query_obj1 = db.session.query(Post).filter(Post.p_board == board_name).all()
        query_obj2 = db.session.query(Post.p_usrid).filter(Post.p_board == board_name).distinct().all()
        tmpusers = []
        for i in range(len(query_obj2)):
            usr_name = query_obj2[i][0]
            userfind = db.session.query(User).filter(User.usr_name == usr_name).first()
            usr_birthday1 = datetime.strptime(userfind.usr_birthday, '%d/%m/%Y')
            usr_gender = userfind.usr_gender
            today = date.today()
            usr_age = today.year - usr_birthday1.year - (
                        (today.month, today.day) < (usr_birthday1.month, usr_birthday1.day))
            postcnt = db.session.query(Post).filter(and_(Post.p_usrid == usr_name, Post.p_board == board_name)).count()
            replycnt = db.session.query(Reply).filter(Reply.r_name == usr_name).count()
            tmpusers.append({'usr_name': usr_name, 'usr_age': usr_age, 'postcnt': postcnt, 'replycnt': replycnt, 'usr_gender': usr_gender})
        b_aveclick = round(db.session.query(func.avg(Post.p_clickcnt)).filter(Post.p_board == board_name)[0][0], 2)
        b_avereply = round(db.session.query(func.avg(Post.p_replycnt)).filter(Post.p_board == board_name)[0][0], 2)
        board = {'b_id': b_id, 'b_postcnt': b_postcnt, 'b_master': b_master, 'b_name': b_name,
                 'b_url': board_name, 'post': query_obj1, 'user': tmpusers, 'b_avereply': b_avereply,
                 'b_aveclick': b_aveclick}
        return render_template('module.html', board=board, form=form, user=current_user)


@app.route('/editor',methods=['GET','POST'])
@login_required
def addpost():
    if request.method == 'GET':
        #boards = Board.query.all()
        return render_template('editor.html', form=PostForm(), user=current_user)
    else:
        form = PostForm(request.form)
        p_title = form.p_title.data
        p_content = form.p_content.data
        p_board = form.p_board.data
        p_usrid = current_user.usr_name
        query_obj = db.session.query(Post).order_by(Post.p_id.desc()).first()
        p_id = query_obj.p_id + 1
        #print(query_obj)
        #print len(query_obj)
        post1 = Post(p_title=p_title, p_content=p_content, p_board=p_board, p_id=p_id, p_usrid=p_usrid)
        db.session.add(post1)
        db.session.commit()
        board = db.session.query(Board).filter(Board.b_name == p_board).first()
        board.b_postcnt += 1
        db.session.commit()
        post = {
            'p_title': p_title,
            'p_content': p_content,
            'p_board': p_board,
            'p_id': p_id,
            'p_usrid': p_usrid,
            'p_reply': []
        }
        return redirect(url_for('post', p_id=p_id))

@app.route('/post/<p_id>',methods=['GET','POST'])
@login_required
def post(p_id):
    p_id = int(p_id)
    queryfind = db.session.query(Post).filter(Post.p_id == p_id).first()
    query_obj = db.session.query(Post).filter(Post.p_id == p_id).all()
    #print(query_obj)
    result_dict = [u.__dict__ for u in query_obj][0]
    # result_dict = [u.__dict__ for u in query_obj.all()]
    #print(result_dict)
    #print type(result_dict)
    p_clickcnt = result_dict['p_clickcnt']
    #print p_clickcnt
    # p_clickcnt = 1
    p_content = result_dict['p_content']
    # p_content = u'hhhh'
    p_replycnt = result_dict['p_replycnt']
    # p_replycnt = 1
    p_time1 = result_dict['p_time']
    p_time = p_time1.strftime("%Y-%m-%d %H:%M:%S")
    p_usrid = result_dict['p_usrid']
    p_title = result_dict['p_title']
    query_obj1 = db.session.query(Reply).filter(p_id == Reply.r_title).all()
    cnt = len(query_obj1) # 这个帖的回复数
    boardname = queryfind.p_board
    query_b_master = db.session.query(Board.b_master).filter(Board.b_name == boardname).first()
    isBoarder = 2
    if query_b_master[0] == current_user.usr_name or current_user.usr_role == 2:
        isBoarder = 1
    #print query_b_master
    reply =[{'r_title': str(v.r_title), 'r_agreecnt': v.r_agreecnt, 'r_name': v.r_name, 'r_time': v.r_time.strftime("%Y-%m-%d %H:%M:%S"),
             'r_id': v.r_id, 'r_layer': v.r_layer, 'r_content': v.r_content}
             for v in query_obj1]
    #print(reply)
    #p_id = 1;
    if request.method == 'GET':
        p_clickcnt = p_clickcnt + 1
        queryfind.p_clickcnt = p_clickcnt
        db.session.commit()
        post = {
            'p_clickcnt': p_clickcnt,
            'p_content': p_content,
            'p_replycnt': p_replycnt,
            'p_time': p_time,
            'p_usrid': p_usrid,
            'p_title': p_title,
            'p_reply': reply,
            'isBoarder': isBoarder
        }
        return render_template('post.html', post=post, form=ReplyForm(), user=current_user)
    else:
        form = ReplyForm(request.form)
        #r_title = form.r_title.data
        r_title = p_id
        #print(r_title)
        r_content = form.r_content.data
        query_obj2 = db.session.query(Reply).filter(Reply.r_title == r_title).all()
        query_objrid = db.session.query(Reply).all()
        cnt = len(query_obj2)  # 这个帖下面的的回复数
        cntrid = len(query_objrid)
        #print(query_obj2)
        print(cnt)
        query_obj = db.session.query(Reply).order_by(Reply.r_id.desc()).first()
        r_id = query_obj.r_id + 1
        r_layer = cnt+1
        r_name = current_user.usr_name
        reply = Reply(r_title=r_title, r_content=r_content, r_id=r_id, r_layer=r_layer, r_name=r_name)
        #print(reply)
        db.session.add(reply)
        db.session.commit()
        queryfind.p_replycnt += 1
        db.session.commit()
        return redirect('/post/'+str(p_id))
        #return render_template('post.html', post=post, form=ReplyForm(), user=current_user)

@app.route('/delete/<del_type>/<del_id>')
def delete(del_type, del_id):
    if del_type == "reply":
        replydel = db.session.query(Reply).filter(Reply.r_id == del_id).first()
        query_obj = db.session.query(Post).filter(Post.p_id == replydel.r_title).first()
        query_obj.p_replycnt -= 1
        db.session.commit()
        db.session.delete(replydel)
        db.session.commit()
        return("Delete successfully"+str(del_id))
    if del_type == "agree":
        query_obj = db.session.query(Reply).filter(Reply.r_id == del_id).first()
        query_obj.r_agreecnt -= 1
        db.session.commit()
        return "Success delete one agree of "+str(del_id)
    if del_type == "user":
        query_obj = db.session.query(User).filter(User.usr_name == del_id).first()
        db.session.delete(query_obj)
        db.session.commit()
        return "Success delete user"
    if del_type == "post":
        query_obj = db.session.query(Post).filter(Post.p_id == del_id).first()
        print del_id
        query_obj1 = db.session.query(Board).filter(Board.b_name == query_obj.p_board).first()
        query_obj1.b_postcnt -= 1
        db.session.commit()
        db.session.delete(query_obj)
        db.session.commit()
        return "Success"
    if del_type == "editor":
        query_obj = db.session.query(Post).filter(Post.p_usrid == current_user.usr_name).all()
        if query_obj:
            cnt = len(query_obj)  # 现在有多少个帖子，数据库里的所以删除的不影响
            if cnt >= 11:
                lasttime = query_obj[cnt-1].p_time
                print "lasttime ", lasttime
                delta = timedelta(minutes=10)
                firsttime1 = lasttime - delta
                print "firsttime1 ", firsttime1
                firsttime2 = query_obj[cnt-11].p_time
                print "firsttime2 ", firsttime2
                space = firsttime1 - firsttime2
                print space, space.seconds
                if space.days < 0:  # 水贴
                    return "1"  # 水贴用户
        print "not water"
        return "0"  # 非水贴用户


@app.route('/add/<add_type>/<add_id>', methods=['Get', 'Post'])
def add(add_type, add_id):
    if add_type == "agree":
        query_obj = db.session.query(Reply).filter(Reply.r_id == add_id).first()
        query_obj.r_agreecnt += 1
        db.session.commit()
        return "Success add one agree of "+str(add_id)
    if add_type == "user":
        form = RegisterFrom()
        if request.method == 'POST':
            if form.validate_on_submit():
                usr_name = form.data['usr_name']
                usr_email = form.data['usr_email']
                usr_password = form.data['usr_password']
                usr_birthday = form.data['usr_birthday']
                usr_gender = form.data['usr_gender']
                u = User(usr_name=usr_name, usr_password=usr_password,
                         usr_email=usr_email, usr_birthday=usr_birthday,
                         usr_gender=usr_gender)
                try:
                    #print 'hello'
                    #print(u)
                    #print(form.data)
                    db.session.add(u)
                    db.session.commit()
                except Exception, e:
                    return 'something goes wrong'
                return redirect(url_for('config'))
        return render_template('signup.html', form=form)
    if add_type == "board":
        #if request.method == 'POST':
        request.data = request.args.to_dict()['b_name']
        #print request.args.to_dict()['b_name']
        query_obj = db.session.query(Board).filter(Board.b_master == current_user.usr_name).first()
        temp = query_obj.b_name
        #print temp
        query_obj.b_name = request.data
        query_obj1 = db.session.query(Post).filter(Post.p_board == temp).all()
        for i in range(len(query_obj1)):
            query_obj1[i].p_board = request.data
            db.session.commit()
        db.session.commit()
        return "1"
    if add_type == "xml":
        query_obj = db.session.query(User).filter(User.usr_name == add_id).first()
        if query_obj:
            return "1"
        else:
            return "0"


@app.route('/edit/<p_id>', methods=['Get', 'Post'])
@login_required
def edit(p_id):
    p_id = int(p_id)
    form = ReplyForm()
    tmppost = db.session.query(Post).filter(Post.p_id == p_id).first()
    tmpuser = db.session.query(User).filter(User.usr_name == tmppost.p_usrid)
    query_obj = db.session.query(Post).filter(Post.p_id == p_id).all()
    # print(query_obj)
    result_dict = [u.__dict__ for u in query_obj][0]
    # result_dict = [u.__dict__ for u in query_obj.all()]
    # print(result_dict)
    # print type(result_dict)
    p_clickcnt = result_dict['p_clickcnt']
    # print p_clickcnt
    # p_clickcnt = 1
    p_content = result_dict['p_content']
    # p_content = u'hhhh'
    p_replycnt = result_dict['p_replycnt']
    # p_replycnt = 1
    p_time1 = result_dict['p_time']
    p_time = p_time1.strftime("%Y-%m-%d %H:%M:%S")
    p_usrid = result_dict['p_usrid']
    p_title = result_dict['p_title']
    query_obj1 = db.session.query(Reply).filter(p_id == Reply.r_title).all()
    isBoarder = 1  # 这里要改

    # print(cnt)
    # p_id = 1;
    if request.method == 'GET':
        post = {
            'p_clickcnt': p_clickcnt,
            'p_content': form.r_content.data,
            'p_replycnt': p_replycnt,
            'p_time': p_time,
            'p_usrid': p_usrid,
            'p_title': p_title,
            'isBoarder': isBoarder
        }
        #return render_template('edit.html', post=post, form=ReplyForm(), user=current_u
        # 要找到这个id对应的post
        return render_template('edit.html', user=tmpuser, post=post, form=form)
    else:
        form = ReplyForm()
        tmppost.p_content = form.r_content.data
        db.session.commit()
        #return render_template('edit.html', user=tmpuser, post=tmppost, form=form)
        return redirect(url_for('post', p_id=p_id))


@app.route('/compete', methods=['GET', 'POST'])
def compete():
    form = CompeteForm()
    if request.method == 'GET':
        return render_template('compete.html', user=current_user, form=form)
    if request.method == 'POST':
        board1 = db.session.query(Board).filter(Board.b_name == form.data['board1']).first()
        board2 = db.session.query(Board).filter(Board.b_name == form.data['board2']).first()
        print board1
        post1 = db.session.query(Post).filter(Post.p_board == str(board1.b_name)).all()  # 版面1所有帖
        post2 = db.session.query(Post).filter(Post.p_board == str(board2.b_name)).all()  # 版面2所有帖
        print post1, "hahha"
        print post2, "heihiehi"
        list1 = {}
        for i in range(len(post1)):
            if list1.has_key(post1[i].p_usrid):
                list1[post1[i].p_usrid] += 1
            else:
                list1[post1[i].p_usrid] = 1
        list2 = {}
        for i in range(len(post2)):
            if list2.has_key(post2[i].p_usrid):
                list2[post2[i].p_usrid] += 1
            else:
                list2[post2[i].p_usrid] = 1
        name1 = list1.keys()
        result = []
        for i in name1:
            if list2.has_key(i):
                if list1[i] > list2[i]:  # win
                    query_name = db.session.query(User).filter(User.usr_name == i).first()
                    usr_name = query_name.usr_name
                    usr_gender = query_name.usr_gender
                    usr_level = query_name.usr_level
                    usr_birthday = query_name.usr_birthday
                    result.append({'usr_name': usr_name, 'usr_gender': usr_gender,
                                   'usr_level': usr_level, 'usr_birthday': usr_birthday,
                                   'b1cnt': list1[i], 'b2cnt': list2[i]})
            else:
                query_name = db.session.query(User).filter(User.usr_name == i).first()
                usr_name = query_name.usr_name
                usr_gender = query_name.usr_gender
                usr_level = query_name.usr_level
                usr_birthday = query_name.usr_birthday
                result.append({'usr_name': usr_name, 'usr_gender': usr_gender,
                               'usr_level': usr_level, 'usr_birthday': usr_birthday,
                               'b1cnt': list1[i], 'b2cnt': 0})
        tmpresult = {'board1': form.data['board1'], 'board2': form.data['board2'], 'userlist': result}
        form = CompeteForm()
        return render_template('compete.html', user=current_user, form=form, result=tmpresult)



@app.route('/home',methods=['GET', 'POST'])  # 十大+各个板块最popular的帖
@login_required
def home():
    query_obj = db.session.query(Post).order_by(Post.p_clickcnt.desc())
    click10 = query_obj.limit(10).all()

    query_obj1 = db.session.query(Post).order_by(Post.p_replycnt.desc())
    reply10 = query_obj1.limit(10).all()

    query_obj2 = db.session.query(Post).\
        filter(Post.p_board == 'entertainment').all()
    #print query_obj2[1]
    max1 = 0.0
    maxpostid1 = 0
    for i in range(len(query_obj2)):
        postid = query_obj2[i].p_id
        #print postid
        query_objreply = db.session.query(Reply).filter(Reply.r_title == postid).order_by(Reply.r_time.desc()).all()
        len1 = len(query_objreply)
        if len1:
            tmp = (query_objreply[0].r_time - query_objreply[len1 - 1].r_time).seconds  # 可以直接减吗？？
            #print ""
            if (tmp > max1):
                max1 = tmp  # 要不要传回来max1？
                maxpostid1 = postid
    query_objhot1 = db.session.query(Post).filter(Post.p_id == maxpostid1).first()
    hot1name = query_objhot1.p_title
    hot1id = query_objhot1.p_id
    entertainment_max1 = db.session.query(Reply.r_name).filter(Reply.r_title == maxpostid1).distinct().all()
    entertainment_max = []
    for i in range(len(entertainment_max1)):
        entertainment_max.append(entertainment_max1[i][0])
    #print entertainment_max
    b_post1 = [{
        'p_title': hot1name, 'p_id': hot1id, 'p_reply': entertainment_max
    }]

    query_obj3 = db.session.query(Post). \
        filter(Post.p_board == 'studies').all()
    max2 = 0.0
    maxpostid2 = 0
    for i in range(len(query_obj3)):
        postid = query_obj3[i].p_id
        query_objreply = db.session.query(Reply).filter(Reply.r_title == postid).order_by(Reply.r_time.desc()).all()
        len2 = len(query_objreply)
        if len2:
            tmp = (query_objreply[0].r_time - query_objreply[len(query_objreply) - 1].r_time).seconds  # 可以直接减吗？？
            if (tmp > max2):
                max2 = tmp  # 要不要传回来max1？
                maxpostid2 = postid
    query_objhot2 = db.session.query(Post).filter(Post.p_id == maxpostid2).first()
    hot2name = query_objhot2.p_title
    hot2id = query_objhot2.p_id
    studies_max1 = db.session.query(Reply.r_name).filter(Reply.r_title == maxpostid2).distinct().all()
    studies_max = []
    for i in range(len(studies_max1)):
        studies_max.append(studies_max1[i][0])
    #print studies_max
    b_post2 = [{
        'p_title': hot2name, 'p_id': hot2id, 'p_reply': studies_max
    }]
    #print b_post2

    query_obj4 = db.session.query(Post). \
        filter(Post.p_board == 'secret-garden').all()
    max3 = 0.0
    maxpostid3 = 0
    for i in range(len(query_obj4)):
        postid = query_obj4[i].p_id
        query_objreply = db.session.query(Reply).filter(Reply.r_title == postid).order_by(Reply.r_time.desc()).all()
        len3 = len(query_objreply)
        if len3:
            tmp = (query_objreply[0].r_time - query_objreply[len(query_objreply) - 1].r_time).seconds  # 可以直接减吗？？
            if (tmp > max3):
                max3 = tmp  # 要不要传回来max1？
                maxpostid3 = postid
    query_objhot3 = db.session.query(Post).filter(Post.p_id == maxpostid3).first()
    hot3name = query_objhot3.p_title
    hot3id = query_objhot3.p_id
    secret_garden_max1 = db.session.query(Reply.r_name).filter(Reply.r_title == maxpostid3).distinct().all()
    secret_garden_max = []
    #print secret_garden_max1
    if len(secret_garden_max1):
        for i in range(len(secret_garden_max1)):
            #print i, 'hellp'
            secret_garden_max.append(secret_garden_max1[i][0])
            #print secret_garden_max1[i][0], 'zheli!'
        #print secret_garden_max

    b_post3 = [{
        'p_title': hot3name, 'p_id': hot3id, 'p_reply': secret_garden_max
    }]

    print b_post3

    home = {
        'post1': reply10,
        'post2': click10
    }
    board = [{'b_name': 'Entertainment', 'b_post': b_post1, 'b_url': 'entertainment'},
                 {'b_name': 'Studies', 'b_post': b_post2, 'b_url': 'studies'},
                 {'b_name': 'Secret Garden', 'b_post': b_post3, 'b_url': 'secret-garden'}]

    # 十大是从Post里面找，点击数前10以及回复数前10，click10，reply10，entertainment-max，secret-garden-max, studies-max
    # 还要展示3个版块里最后恢复时间-发帖时间max的帖子

    return render_template('home.html', home=home, board=board, user=current_user)


@app.route('/boarder', methods=['GET', 'POST'])  # 版主
@login_required
def boarder():
    role = current_user.usr_role
    #print role
    if role == 1:  # 版主
        board1 = db.session.query(Board).filter(Board.b_master == current_user.usr_name).first()
        post = db.session.query(Post).filter(Post.p_board == board1.b_name).all()
        #print board1.b_postcnt
        board = {
            'b_name': board1.b_name, 'b_id': board1.b_id, 'b_master': board1.b_master,
            'b_postcnt': board1.b_postcnt, 'post': post
        }
    return render_template('boarder.html', board=board, post=post, user=current_user)


@app.route('/config', methods=['GET', 'POST']) # 管理员
@login_required
def config():
    role = current_user.usr_role
    #print role
    if role == 2:  # 管理员
        post1 = db.session.query(Post).all()
        user1 = db.session.query(User).all()
        post = []
        user = []
        for i in range(len(user1)):
            usr_name = user1[i].usr_name
            usr_birthday = user1[i].usr_birthday
            usr_level = user1[i].usr_level
            usr_regdate = user1[i].usr_regdate.strftime("%Y-%m-%d %H:%M:%S")
            usr_postcnt = db.session.query(Post).filter(Post.p_usrid == usr_name).count()
            usr_replycnt = db.session.query(Reply).filter(Reply.r_name == usr_name).count()
            usr_gender = user1[i].usr_gender
            user.append({
                'usr_name': usr_name, 'usr_birthday': usr_birthday, 'usr_level': usr_level,
                'usr_regdate': usr_regdate, 'usr_postcnt': usr_postcnt, 'usr_replycnt': usr_replycnt, 'usr_gender': usr_gender
            })
        for i in range(len(post1)):
            p_id = post1[i].p_id
            p_title = post1[i].p_title
            p_usrid = post1[i].p_usrid
            p_replycnt = post1[i].p_replycnt
            p_clickcnt = post1[i].p_clickcnt
            p_time = post1[i].p_time.strftime("%Y-%m-%d %H:%M:%S")
            if p_title:
                post.append({
                    'p_id': p_id, 'p_title': p_title, 'p_usrid': p_usrid,
                    'p_replycnt': p_replycnt, 'p_clickcnt': p_clickcnt,
                    'p_time': p_time
                })
        board = {'post': post, 'user': user}
    return render_template('boarder.html', board=board, post=post, user=current_user)


@app.route('/xml/<usr_name>', methods=['GET', 'POST'])
@login_required
def xml(usr_name):
    if request.method == 'GET':
        obj = db.session.query(User).filter(User.usr_name == usr_name).first()

        print usr_name

        zidian = obj.__dict__
        zidian.pop('_sa_instance_state')
        obj1 = db.session.query(Post).filter(Post.p_usrid == usr_name).all()
        zidian1 = []
        for i in range(len(obj1)):
            item = obj1[i].__dict__
            item.pop('_sa_instance_state')
            zidian1.append(item)
        obj2 = db.session.query(Reply).filter(Reply.r_name == usr_name).all()
        zidian2 = []
        for i in range(len(obj2)):
            item = obj2[i].__dict__
            item.pop('_sa_instance_state')
            zidian2.append(item)
        zidian['Post'] = zidian1
        zidian['Reply'] = zidian2
        # print zidian
        xml1 = dicttoxml(zidian)
        #print xml1
        xml1 = parseString(xml1)
        xml1 = xml1.toprettyxml()
        return render_template('result.html', xml1=xml1, user=current_user)
