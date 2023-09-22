from flask import Flask,render_template,request,redirect, url_for
import sqlite3
from datetime import datetime,date
import csv

##### --- INITIALIZATION --- ######

database = sqlite3.connect('BurgerGalore.db')

### Create Tables ###

try:
    c = database.cursor()
    # Members Table #
    c.execute('''CREATE TABLE members (\
            id INTEGER PRIMARY KEY AUTOINCREMENT,\
            name VARCHAR(256) NOT NULL,\
            location VARCHAR(256) NOT NULL,\
            email VARCHAR(256) UNIQUE NOT NULL,\
            password VARCHAR(256) NOT NULL);''')
    database.commit()
    # Meals Table #
    c.execute('''CREATE TABLE meals (\
            id INTEGER PRIMARY KEY AUTOINCREMENT,\
            burger VARCHAR(256) NOT NULL,\
            sidemeal VARCHAR(256) NOT NULL,\
            drink VARCHAR(256) NOT NULL,\
            price INTEGER UNIQUE NOT NULL);''')
    database.commit()
    # Orders Table #
    c.execute('''CREATE TABLE orders (\
            id INTEGER PRIMARY KEY AUTOINCREMENT,\
            custID INTEGER REFERENCES members(id),\
            mealID INTEGER REFERENCES meals(id),\
            price INTEGER NOT NULL,\
            date DATE NOT NULL,\
            discount VARCHAR(256) NOT NULL);''')
    database.commit()
except:
    print('Tables already created;')

### Insert Members ###
    
temp = ()
mem = open('static/MEMBERS.txt')
members = mem.readlines()
for member in members:
    member = member.strip().split(',')
    temp += (tuple(member),)
try:
    c = database.cursor()
    for t in temp:
        c.execute('''INSERT INTO members(name,location,email,password) \
                VALUES(:name,:location,:email,:password)''',t)
    database.commit()
except:
    print('Members already added.')

### Insert Meals ###
    
tem = ()
mea = open('static/MEALS.txt')
meals = mea.readlines()
for meal in meals:
    meal = meal.strip().split(',')
    tem += (tuple(meal),)
try:
    c = database.cursor()
    for t in tem:
        c.execute('''INSERT INTO meals(burger,sidemeal,drink,price) \
                VALUES(:burger,:sidemeal,:drink,:price)''',t)
    database.commit()
except:
    print('Meals already added.')
    
database.close()

##### --- ----- --- #####

curr_login = []
curr_order = []
Dmsg = []
msg = ''

##### --- FLASK BACKEND --- #####

app = Flask(__name__)

# ----------------------------------------------------------------- #

### MENU ###
@app.route('/',methods=["GET","POST"])
def main():
    database = sqlite3.connect('BurgerGalore.db')
    c = database.cursor()
    c.execute('SELECT id,burger,sidemeal,drink,price FROM meals')
    meals = c.fetchall()
    images = ('mealOne.png','mealTwo.png')
    index = len(meals)
    if curr_login != []:
        # Find CustID #
        c.execute('''SELECT id FROM members WHERE name = :N''',\
                  {'N':curr_login[0]})
        custID = c.fetchone()[0]
        # Get All Orders For CustID
        c.execute('''SELECT mealID,price,date FROM orders WHERE custID = :ID''',{"ID":custID})
        orders = c.fetchall()
        if orders != [] and len(orders) >= 10:
            c.execute('''SELECT mealID FROM orders GROUP BY mealID ORDER BY COUNT(mealID) DESC LIMIT 3;''')
            topmeals = c.fetchall()
            top = []
            for t in topmeals:
                c.execute('''SELECT id,burger,sidemeal,drink,price FROM meals WHERE id = :ID''',{"ID":int(t[0])})
                topmeal = c.fetchone()
                top.append(topmeal)
            line = "-" * 300 ### Design ###
            return render_template('main.html',\
                                   login=curr_login,\
                                   msg=msg,\
                                   meals=meals,\
                                   images=images,\
                                   index=index,\
                                   top_3 = top,\
                                   line=line)
        else:
            return render_template('main.html',\
                                   login=curr_login,\
                                   msg=msg,\
                                   meals=meals,\
                                   images=images,\
                                   index=index,\
                                   top_3 = None)
    else:
        return render_template('main.html',\
                               login=curr_login,\
                               msg=msg,\
                               meals=meals,\
                               images=images,\
                               index=index,\
                               top_3 = None)
### ORDER ###
@app.route('/order',methods=["GET","POST"])
def order():
    if request.method == "POST":
        if curr_login == []:
            msg = 'Log In Required'
            return redirect(url_for('main',msg=msg))
        MealID = request.form.get('selected')
        database = sqlite3.connect('BurgerGalore.db')
        c = database.cursor()
        c.execute('''SELECT burger,sidemeal,drink,price FROM meals WHERE id = :ID''',\
                  {'ID':MealID})
        meal = c.fetchall()[0]
        ### Update Order Table Contents ###
        curr_order.append(meal)
        # Find CustID #
        c.execute('''SELECT id FROM members WHERE name = :N''',\
                  {'N':curr_login[0]})
        custID = c.fetchone()[0]
        # Get All Orders For CustID
        c.execute('''SELECT mealID,price,date FROM orders WHERE custID = :ID''',{"ID":custID})
        orders = c.fetchall()
        ### Calculate Total Price ###
        total = 0
        Dmsg.clear()
        for order in curr_order:
            if orders != [] and len(orders) >= 10:
                total += (order[3]* 0.90)
                Dmsg.append('Discount 10% OFF')
            else:
                total += order[3]
                Dmsg.append('No Discount Available')
        total = round(total,2)
        msg = 'Order Added'
        return render_template('order.html',login=curr_login,msg=msg,orders=curr_order,total=total,Dmsg=Dmsg)
    else:
        if curr_login == []:
            msg = 'Log In Required'
            return redirect(url_for('main',msg=msg))
        else:
            database = sqlite3.connect('BurgerGalore.db')
            c = database.cursor()
            # Find CustID #
            c.execute('''SELECT id FROM members WHERE name = :N''',\
                  {'N':curr_login[0]})
            custID = c.fetchone()[0]
            # Get All Orders For CustID
            c.execute('''SELECT mealID,price,date FROM orders WHERE custID = :ID''',{"ID":custID})
            orders = c.fetchall()
            ### Calculate Total Price ###
            total = 0
            Dmsg.clear()
            for order in curr_order:
                if orders != [] and len(orders) >= 10:
                    total += (order[3]* 0.90)
                    Dmsg.append('Discount 10% OFF')
                else:
                    total += order[3]
                    Dmsg.append('No Discount Available')
            msg = 'Order Table'
            return render_template('order.html',login=curr_login,msg=msg,orders=curr_order,total=total,Dmsg=Dmsg)
        
### Drop Table ###
@app.route('/droporder',methods=["GET","POST"])
def droptable():
    curr_order.clear()
    msg = "Order Dropped"
    return redirect(url_for('main',msg=msg))

### ConfirmPayment ###
@app.route('/confirm',methods=["GET","POST"])
def confirm():
    database = sqlite3.connect('BurgerGalore.db')
    c = database.cursor()
    # Find CustID #
    c.execute('''SELECT id FROM members WHERE name = :N''',\
              {'N':curr_login[0]})
    custID = c.fetchone()[0]
    # Get All Orders For CustID
    c.execute('''SELECT mealID,price,date FROM orders WHERE custID = :ID''',{"ID":custID})
    orders = c.fetchall()
    if orders != [] and len(orders) >= 10:
        dis = "10% OFF"
    else:
        dis = "None"
    # Find Date #
    now = datetime.today().ctime()
    # Input into DB #
    for order in curr_order:
        # Find MealID
        c.execute('''SELECT id FROM meals WHERE price = :P''',\
                  {'P':order[3]})
        mealID = c.fetchone()[0]
        c.execute('''INSERT INTO orders(custID,mealID,price,date,discount) \
                VALUES(:custID,:mealID,:price,:date,:discount)''',(custID,mealID,order[3],now,dis))
    database.commit()
    database.close()
    #Payment Methods#
    logos = ('MasterCardLogo.jpg','VISACardLogo.jpg','AmericanExpressLogo.png','DiscoverCardLogo.jpg','DebitCardsLogo.png')
    cards = ('MasterCard','VISACard','AmericanExpress','DiscoverCard','DebitCards')
    length = len(logos)
    return render_template('confirm.html',logos=logos,length=length,cards=cards)

### Success ###
@app.route('/success',methods=["GET","POST"])
def success():
    curr_order.clear()
    msg = "Success"
    return redirect(url_for('main',msg=msg))

### Transactions ###
@app.route('/transactions',methods=["GET","POST"])
def transactions():
    if curr_login == []:
        msg = 'Log In Required'
        return redirect(url_for('main',msg=msg))
    else:
        database = sqlite3.connect('BurgerGalore.db')
        c = database.cursor()
        # Find CustID #
        c.execute('''SELECT id FROM members WHERE name = :N''',\
                  {'N':curr_login[0]})
        custID = c.fetchone()[0]
        # Get All Orders For CustID
        c.execute('''SELECT mealID,price,date,discount FROM orders WHERE custID = :ID''',{"ID":custID})
        orders = c.fetchall()
        meals = []
        for order in orders:
            c.execute('''SELECT burger,sidemeal,drink FROM meals WHERE id = :ID''',{"ID":order[0]})
            meal = c.fetchone()
            meals.append(meal)
        leng = len(orders)
        return render_template("transaction.html",orders=orders,\
                               meals=meals,\
                               leng=leng)

# ----------------------------------------------------------------- #

### LOGIN ###
@app.route('/login',methods=["GET","POST"])
def login():
    return render_template('login.html',login=curr_login,msg=msg)

@app.route('/processlogin',methods=["GET","POST"])
def processlogin():
    # Process and Redirect back to main #
    if request.method == "POST":
        database = sqlite3.connect('BurgerGalore.db')
        email = request.form.get('email')
        password = request.form.get('password')
        c = database.cursor()
        c.execute('''SELECT password FROM members WHERE email = :usermail''',\
                  {'usermail':email})
        checkpass = c.fetchone()
        if checkpass == None:
            # No such email and password #
            msg = 'No such email'
            return redirect(url_for('main',msg=msg))
        else:
            if checkpass[0] == password:
                c = database.cursor()
                c.execute('''SELECT name FROM members WHERE email = :usermail''',\
                          {'usermail':email})
                curr_log = c.fetchone()[0]
                database.close()
                curr_login.append(curr_log)
                msg = 'Successful Login'
                return redirect(url_for('main',msg=msg))
            else:
                msg = 'Wrong email or password.'
                return redirect(url_for('main',msg=msg))
    else:
        print('Error Encountered.')

### LOGOUT ###
@app.route('/logout',methods=["GET","POST"])
def logout():
    curr_login.pop()
    msg = 'Logged Out'
    return redirect(url_for('main',msg=msg))

### SIGNUP ###
@app.route('/signup',methods=["GET","POST"])
def signup():
    return render_template('signup.html',login=curr_login)

@app.route('/processsignup',methods=["GET","POST"])
def processsignup():
    # Process and Redirect back to main #
    if request.method == "POST":
        database = sqlite3.connect('BurgerGalore.db')
        personal = request.form.getlist('personal')
        email = personal[2]
        c = database.cursor()
        c.execute('''SELECT email FROM members WHERE email = :now''',\
                  {'now':email})
        check = c.fetchone()
        if check == None:
            # Add member
            c.execute('''INSERT INTO members(name,location,email,password)\
                    VALUES(:name,:location,:email,:password)''',tuple(personal))
            database.commit()
            database.close()
            msg = 'Successful SignUp'
            return redirect(url_for('main',msg=msg))
        else:
            msg = 'Member with email exist already.'
            return redirect(url_for('main',msg=msg))
    else:
        print('Error Encountered.')

### Profile ###
@app.route('/profile',methods=["GET","POST"])
def profile():
    name = curr_login[0]
    database = sqlite3.connect('BurgerGalore.db')
    c = database.cursor()
    c.execute('''SELECT name,location,email,password FROM members WHERE name = :logname''',\
              {'logname':name})
    info = c.fetchall()[0]
    database.close()
    return render_template('profile.html',info=info)

### Change Password ###
@app.route('/changepassword',methods=['GET','POST'])
def changepassword():
    if request.method == "POST":
        newpassword = request.form.get('newpassword')
        database = sqlite3.connect('BurgerGalore.db')
        c = database.cursor()
        c.execute('''UPDATE members SET password = :pas WHERE name = :loginName''',\
                  {'pas':newpassword,'loginName':curr_login[0]})
        database.commit()
        database.close()
        msg = 'Changed Password Successfully'
        return redirect(url_for('main',msg=msg))
    else:
        print('Error Encountered.')

# ----------------------------------------------------------------- #


app.run(debug=False,port=5070)


