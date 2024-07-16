from flask import Flask, request, render_template, jsonify
from pymongo import MongoClient, errors

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client.Furhaven1
user = db.users
vol = db.volunteers

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

if __name__ == '__main__':
    app.run(debug=True)