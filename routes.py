from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from passlib.hash import sha256_crypt
from werkzeug.utils import secure_filename
import os

from flask_app import app, db
from flask_app.models import User, Supplier, Product
from flask_app.forms import PostForm

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

# reformats submitted files?
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/view")
def view():
    if current_user.username == "admin":
        users = User.query.all()
        suppliers = Supplier.query.all()
        products = Product.query.all()
        return render_template("view.html", users=users, Suppliers=suppliers, products=products)
    else:
        return redirect(url_for("index"))


@app.route("/")
def index():
    db.create_all()
    # posts = Post.query.all() change to Products
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("index.html")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "GET":
        if session["supplier"] != -1:
            return redirect(url_for("supplier"))
        return render_template("profile.html", user=current_user)


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("register.html")

    else:
        # Create user object to insert into SQL
        passwd1 = request.form.get("password1")
        passwd2 = request.form.get("password2")

        if passwd1 != passwd2 or passwd1 == None:
            flash("Password Error!", "danger")
            return render_template("register.html")

        hashed_pass = sha256_crypt.encrypt(str(passwd1))

        # get promotions and set true/false
        promotions = False
        if "checkbox" in request.form:
            promotions = True

        new_user = User(
            username=request.form.get("username"),
            email=request.form.get("email"),
            password=hashed_pass,
            promotions=promotions,
        )

        if user_exsists(new_user.username, new_user.email):
            flash("User already exsists!", "danger")
            return render_template("register.html")
        else:
            # Insert new user into SQL
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)

            flash("Account created!", "success")
            return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    else:
        username = request.form.get("username")
        password_candidate = request.form.get("password")

        # Query for a user with the provided username
        result = User.query.filter_by(username=username).first()

        # If a user exsists and passwords match - login
        if result is not None and sha256_crypt.verify(password_candidate, result.password):

            # Init session vars
            login_user(result)
            flash("Logged in!", "success")
            return redirect(url_for("index"))

        else:
            flash("Incorrect Login!", "danger")
            return render_template("login.html")


@app.route("/product=?{product_id}", methods=["POST", "GET"])
def product_info(product_id):
    if request.method == "GET":
        return render_template("product.html", product=Product.query.filter_by(id=product_id).first())
    else:
        pass


@app.route("/supplier")
def supplier():
    if session["supplier"] != -1:
        supplier = Supplier.query.get(session["supplier"])
        # if isinstance(current_user, Supplier):
        # if True:
        return render_template("supplier.html", supplier=supplier)
    else:
        flash("Please Login to continue to the page!", "danger")
        return redirect(url_for("supplier_login"))


# BUSY
@app.route("/add-product", methods=["GET", "POST"])
def add_product():
    if session["supplier"] == -1:
        flash("Please login to view this page!", "error")
        return redirect(url_for("supplier_login"))

    if request.method == "GET":
        # if isinstance(current_user, Supplier):
        return render_template("add_product.html")
        # else:
        #     flash("You don't have permission to view this page", "danger")
        #     return redirect(url_for("supplier_login"))
    else:
        flash("test", "error")
        return redirect(url_for("index"))

        # Create product object to insert into SQL
        if "file" not in request.files:
            flash("No file part")
            return render_template("add_product.html")
        file = request.files["file"]
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == "":
            flash("No selected file")
            return render_template("add_product.html")

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            title = request.form["title"]
            content = request.form["content"]
            price = request.form["price"]
            # supplier_id = current_user.id
            supplier = Supplier.query.filter_by(id=1).first()
            supplier_id = supplier.id
            image_name = filename
            stock = request.form["stock"]

            product = Product(
                title=title, content=content, price=price, supplier_id=supplier_id, image_name=image_name, stock=stock
            )

            # Insert new user into SQL
            db.session.add(product)
            db.session.commit()

            flash("Product has been added!", "success")
            return redirect(url_for("supplier"))

        flash("something went wrong", "error")
        return render_template("add_product.html")


@app.route("/supplier/register", methods=["GET", "POST"])
def supplier_register():
    if request.method == "GET":
        return render_template("supplier_register.html")

    else:
        # Create supplier object to insert into SQL
        passwd1 = request.form.get("password1")
        passwd2 = request.form.get("password2")

        if passwd1 != passwd2 or passwd1 == None:
            flash("Password Error!", "danger")
            return render_template("supplier_register.html")

        hashed_pass = sha256_crypt.encrypt(str(passwd1))

        new_supplier = Supplier(
            company_name=request.form.get("company_name"),
            email=request.form.get("email"),
            password=hashed_pass,
        )

        if supplier_exsists(new_supplier.company_name, new_supplier.email):
            flash("User already exsists!", "danger")
            return render_template("supplier_register.html")
        else:
            # Insert new user into SQL
            db.session.add(new_supplier)
            db.session.commit()

            # login_user(new_supplier)
            session["supplier"] = new_supplier.id

            flash("Account created!", "success")
            return redirect(url_for("index"))


@app.route("/supplier/login", methods=["GET", "POST"])
def supplier_login():
    if request.method == "GET":
        return render_template("supplier_login.html")

    else:
        company_name = request.form.get("company_name")
        password_candidate = request.form.get("password")

        # Query for a user with the provided username
        result = Supplier.query.filter_by(company_name=company_name).first()

        # If a user exsists and passwords match - login
        if result is not None and sha256_crypt.verify(password_candidate, result.password):

            # Init session vars
            session["supplier"] = result.id

            # login_user(result)
            flash("Logged in!", "success")
            return redirect(url_for("supplier"))

        else:
            flash("Incorrect Login!", "danger")
            return render_template("supplier_login.html")


# user or supplier logout
@app.route("/logout")
def logout():
    logout_user()
    if session["supplier"]:
        session.pop("supplier", None)
    flash("Logged out!", "success")
    return redirect(url_for("index"))


@app.before_first_request
def before_first_request():
    session["supplier"] = -1


# Check if username or email are already taken
def user_exsists(username, email):
    # Get all Users in SQL
    users = User.query.all()
    for user in users:
        if username == user.username or email == user.email:
            return True

    # No matching user
    return False


def supplier_exsists(company_name, email):
    # Get all Suppliers in SQL
    suppliers = Supplier.query.all()
    for supplier in suppliers:
        if company_name == supplier.company_name or email == supplier.company_name:
            return True

    # No matching user
    return False
