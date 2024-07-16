from flask import Flask, request, render_template, jsonify, redirect
from pymongo import MongoClient, errors
from razorpay import Client
from dotenv import load_dotenv
import os
import hmac
import hashlib

load_dotenv()

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client.Furhaven1
user = db.users 
vol = db.volunteers

# Razorpay config
razorpay_client = Client(auth=(os.getenv("RAZORPAY_API_KEY"), os.getenv("RAZORPAY_API_SECRET")))
razorpay_client.set_app_details({"title" : "<YOUR_APP_TITLE>", "version" : "<YOUR_APP_VERSION>"})

'''
user.create_index([('email',1)], unique= True)
user.create_index([('username',1),('passowrd',1)])

vol.create_index([('email', 1),('phone',1),('preferred_shelter',1)], unique=True)
vol.create_index([('first_name',1),('last_name',1),('remarks',1)])
'''

# Route to serve the home page
@app.route('/')
def home():
    return render_template('index.html')

# Route to serve the home page
@app.route('/index.html')
def index():
    return home()

# Route to serve sign up page
@app.route('/sign-up.html')
def signUp():
    return render_template('sign-up.html')

# Route to serve login page
@app.route('/login.html')
def LogIn():
    return render_template('login.html')

# Route to serve error
@app.route('/404.html')
def Error404():
    return render_template('404.html')

# Route to serve donate page
@app.route('/donate.html')
def Donation():
    return render_template('donate.html')

# Route to serve search page
@app.route('/search.html')
def Search():
    return render_template('search.html')

# Route to serve volunteer page
@app.route('/volunteer.html')
def Volunteer():
    return render_template('volunteer.html')

# Route to serve volunteer page
@app.route('/success.html')
def paymentSuccess():
    return render_template('success.html')

# Route to serve volunteer page
@app.route('/failed.html')
def paymentFailed():
    return render_template('failed.html')

# Route to add new user
@app.route('/new_user', methods=['POST'])
def addNewUser():
    try:
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

    # Save to MongoDB
        user.insert_one({'username': username, 'email': email, 'password': password})
        return jsonify({'message': 'You are registered successfully, continue to LogIn'})
    
    except errors.PyMongoError:
        return jsonify({'message': 'The email id is alredy registered, try some other email or LogIn'})
    except Exception as e:
        return jsonify({'message': 'An unexpected error occurred: ' + str(e)}), 500

#Route to login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Validate input
        if not email or not password:
            return jsonify({'message': "Username and password are required"}), 400

        # Find user in MongoDB
        found = user.find_one({'email': email})
        if found:
            if found['password']== password:
                name = str(found['username']).capitalize()
                return jsonify({'message': f"Welcome {name}, it's nice to see you"})
            return jsonify({'message': "Incorrect password"})
        return jsonify({'message': "Invalid email"})
    
#Route to volunteer registration
@app.route('/register', methods=['POST'])
def register():
    try:
        firstName = request.form['first_name']
        email = request.form['email']
        lastName = request.form['last_name']
        phNo = request.form['ph_no']
        pref = request.form['shelter_pref']
        remarks = request.form['msg'].strip()

    # Save to MongoDB
        vol.insert_one({'first_name': firstName, 'email': email, 'last_name': lastName, 'phone': phNo, 'preferred_shelter' : pref, 'remarks':remarks})
        return jsonify({'message': 'You are registered successfully'})
    
    except errors.PyMongoError:
        return jsonify({'message': 'The email id is alredy registered.'})
    except Exception as e:
        return jsonify({'message': 'An unexpected error occurred: ' + str(e)}), 500

# Route to initiate payment
@app.route("/order", methods=["POST"])
def checkout():
    try:
        # money is always in lowest unit : 500 -> Rs.5
        amount = request.json['amount'] * 100
        currency = "INR"
        order_data = razorpay_client.order.create(data={
            "amount": int(amount),
            "currency": currency,
        })
        return jsonify(order_data)

    except Exception as e:
        print(e)
        return jsonify({
            'message': "500: InternalServerError"
        }), 500

# Route to send public_key (needed for order)
@app.route("/api/key", methods=["GET"])
def sendKey():
    return jsonify(dict(
        # Do not export API-secret (key needs to be shared)
        key=os.getenv("RAZORPAY_API_KEY")))

# Route to verify payment
@app.route("/paymentVerify", methods=["POST"])
def verify_payment():
    # razorpay does not send back "application/json", it is a "form"
    payment_id = request.form['razorpay_payment_id']
    order_id = request.form['razorpay_order_id']
    signature = request.form['razorpay_signature']
    content = order_id + "|" + payment_id
    generate = hmac.new(
        str(os.getenv("RAZORPAY_API_SECRET")).encode("utf-8"), 
        content.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    if generate == signature:
        return redirect("success.html"), 302
    else:
        return redirect("failed.html"), 302

if __name__ == '__main__':
    app.run(debug=True)
