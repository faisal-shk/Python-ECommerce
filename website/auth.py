
from flask import Blueprint, render_template, flash, redirect
from .forms import LoginForm, SignUpForm, PasswordChangeForm
from werkzeug.security import check_password_hash, generate_password_hash
from .models import Customer
from . import db
from flask_login import login_user, logout_user, login_required

auth = Blueprint('auth', __name__)

# Sing up page
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm() 
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password1 = form.password1.data
        password2 = form.password2.data
        
        if password1 == password2:
            new_customer = Customer()
            new_customer.email = email              
            new_customer.username = username
            new_customer.password = (password2)
            # new_customer.password = generate_password_hash(password2) # Hashing the password generate_password_hash

            
            try:
                db.session.add(new_customer)
                db.session.commit()
                flash('Account created successfully') #{username}
                return redirect('/login')
            
            except Exception as e:
                print(e)
                flash('Email already exists! Account not Created')
                
            form.email.data = ''
            form.username.data = ''
            form.password1.data = ''
            form.password2.data = ''
            
    return render_template("signup.html", form=form)
    # return 'This Signup page' 
    
# Login Page    
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        customer = Customer.query.filter_by(email=email).first()

        if customer:
            if customer.verify_password(password=password):
                login_user(customer)
                return redirect('/')
            else:
                flash('Incorrect email or password!')
                
        else:
            flash('Email doesnt exist!')
            
    return render_template("login.html", form=form)
    # return 'This Login page'

    
@auth.route('/forms')
def forms():
    return render_template("forms.html")
    # return 'This Forms page'

@auth.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    return redirect('/')

@auth.route('/profile/<int:customer_id>')
@login_required
def profile(customer_id):

    customer = Customer.query.get(customer_id)
    print('Customer Id: ', customer_id)
    return render_template("profile.html", customer=customer)

    print('Customer Id: ', customer_id)
    return f'Customer Id is {customer_id}'

@auth.route('/change-password/<int:customer_id>', methods=['GET','POST'])
@login_required
def change_password(customer_id):
    form = PasswordChangeForm()
    customer = Customer.query.get(customer_id)

    if form.validate_on_submit():
        current_password = form.current_password.data
        new_password = form.new_password.data
        confirm_new_password = form.confirm_new_password.data

        if customer.verify_password(current_password):
            if new_password == confirm_new_password:
                customer.password = confirm_new_password
                db.session.commit()
                flash('Password changed successfully')
                return redirect('/profile/{customer_id}')
            else:
                flash('New passwords do not match')
        else:
            flash('Current password is incorrect')

    return  render_template("change_password.html", form=form)