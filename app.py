import os
from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from database import DBhandler
import hashlib
import sys

application = Flask(__name__)
DB = DBhandler()
application.config["SECRET_KEY"] = "helloosp"

@application.route("/")
def hello():
    return redirect(url_for('login'))

@application.route("/list")
def view_list():
    page = request.args.get("page", 0, type=int)
    per_page=6 # item count to display per page
    per_row=3  # item count to display per row
    row_count=int(per_page/per_row)
    start_idx=per_page*page
    end_idx=per_page*(page+1)
    
    data = DB.get_items()
    
    if data is None:
        data = {}
    elif isinstance(data, list):
        data = {str(i): v for i, v in enumerate(data)}
    elif not isinstance(data, dict):
        data = {}
    
    images_dir = os.path.join(application.static_folder, "images")
    files = os.listdir(images_dir)
    image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    
    data = {
        filename: {"img_path": filename}
        for filename in image_files
    }
    
    item_counts = len(data)
    
    sliced_items = list(data.items())[start_idx:end_idx]
    data = dict(sliced_items)
    tot_count = len(data)
    items = list(data.items())
    
    for i in range(row_count):
        if(i == row_count-1) and (tot_count % per_row != 0):
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:])
        else:
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:(i+1)*per_row])
    return render_template("list.html", datas = data.items(), row1=locals()['data_0'].items(), row2=locals()['data_1'].items(),
    limit=per_page, page=page, page_count=int((item_counts/per_page)+1), total = item_counts)




@application.route("/review")
def view_review():
    page = request.args.get("page", 0, type=int)
    per_page = 6  # item count to display per page
    per_row = 3   # item count to display per row
    row_count = int(per_page / per_row)

    start_idx = per_page * page
    end_idx = per_page * (page + 1)

    data = DB.get_reviews()   # read the table

    if data is None:
        data = {}
    else:
        data = dict(data)

    item_counts = len(data)

    data = dict(list(data.items())[start_idx:end_idx])
    tot_count = len(data)

    for i in range(row_count):
        if (i == row_count - 1) and (tot_count % per_row != 0):
            locals()['data_{}'.format(i)] = dict(list(data.items())[i * per_row:])
        else:
            locals()['data_{}'.format(i)] = dict(list(data.items())[i * per_row:(i + 1) * per_row])

    return render_template(
        "review.html",
        datas=data.items(),
        row1=locals()['data_0'].items(),
        row2=locals()['data_1'].items(),
        limit=per_page,
        page=page,
        page_count=int((item_counts / per_page) + 1),
        total=item_counts
    )


@application.route("/reg_review_init/<name>/")
def reg_review_init(name):
    return render_template("reg_reviews.html", name=name)


@application.route("/reg_items")
def reg_item():
    return render_template("reg_items.html")

@application.route("/reg_reviews")
def reg_review():
    return render_template("reg_reviews.html")

@application.route("/reg_review", methods=['POST'])
def reg_review_post():
    data = request.form
    image_file = request.files["file"]
    save_path = os.path.join(application.root_path, "static", "images", image_file.filename)
    image_file.save(save_path)
    DB.reg_review(data, image_file.filename)
    return redirect(url_for('view_review'))





@application.route("/view_detail/<name>/")
def view_item_detail(name):
    print("###name:",name)
    data = DB.get_item_byname(str(name))
    print("####data:",data)
    return render_template("detail.html", name=name, data=data)


@application.route("/submit_item")
def reg_item_submit():
    name=request.args.get("name")
    seller=request.args.get("seller")
    addr=request.args.get("addr")
    email=request.args.get("email")
    category=request.args.get("category")
    card=request.args.get("card")
    status=request.args.get("status")
    phone=request.args.get("phone")
    
    print(name,seller,addr,email,category,card,status,phone)
    #return render_template("reg_item.html")

@application.route("/submit_item_post", methods=['POST'])
def reg_item_submit_post():
    image_file=request.files["file"]
    image_file.save("static/images/{}".format(image_file.filename))
    data=request.form
    DB.insert_item(data['name'], data, image_file.filename)
    return render_template("submit_item_result.html", data=data, img_path="static/images/{}".format(image_file.filename))

@application.route("/view_review_detail/<name>/")
def view_review_detail(name):
    data = DB.get_review_byname(name)
    return render_template("review_detail.html", name=name, data=data)



@application.route("/login")
def login():
    return render_template("login.html")

@application.route("/login_confirm", methods=['POST'])
def login_user():
    id_ = request.form['id']
    pw = request.form['pw']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    if DB.find_user(id_, pw_hash):
        session['id'] = id_
        return redirect(url_for('view_list'))
    else:
        flash("Wrong ID or PW!")
        return render_template("login.html")
    
@application.route("/logout")
def logout_user():
    session.clear()
    return redirect(url_for('login'))






@application.route("/signup", methods=['GET'])
def signup():
    return render_template("signup.html")

@application.route("/signup_post", methods=['POST'])
def register_user():
    data=request.form
    pw=request.form['pw']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    if DB.insert_user(data,pw_hash):
        return render_template("login.html")
    else:
        flash("user id already exist!")
        return render_template("signup.html")

@application.route('/show_heart/<name>/', methods=['GET'])
def show_heart(name):
    clean_name = name.rsplit('.',1)[0]
    my_heart = DB.get_heart_byname(session['id'], clean_name)
    return jsonify({'my_heart': my_heart})

@application.route('/like/<name>/', methods=['POST'])
def like(name):
    clean_name = name.rsplit('.',1)[0]
    DB.update_heart(session['id'], 'Y', clean_name)
    return jsonify({'msg': '좋아요 완료!'})

@application.route('/unlike/<name>/', methods=['POST'])
def unlike(name):
    clean_name = name.rsplit('.',1)[0]
    DB.update_heart(session['id'], 'N', clean_name)
    return jsonify({'msg': '안좋아요 완료!'})

if __name__=="__main__":
    application.run(debug=True)

