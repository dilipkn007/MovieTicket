import reader.configReader as read
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_login import UserMixin, LoginManager, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__, static_folder='static')
app.secret_key = "dilipkn007"
app.config['LOGIN_FLAG'] = False
login = str(app.config['LOGIN_FLAG'])
U = None

# MongoDB connection
connection_string = read.config_reader("DB_CONNECTION", "string")
client = MongoClient(connection_string)
db = client['MovieBooking']
users_collection = db['users']
collection = db['movie_data']

# User Loader for Login Manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(UserMixin):

    def __init__(self, user_dict):
        self.id = str(user_dict['_id'])
        self.username = user_dict['username']
        self.email = user_dict['email']
        self.password = user_dict['password']


def create_movie_ticket(ticket_id, movie_name, screen_name, seat_numbers,
                        show_date, show_time, amount):
    # Create a PDF canvas
    c = canvas.Canvas("movie_ticket.pdf", pagesize=letter)

    # Define content for the ticket
    content = [
        f"Ticket ID: {ticket_id}", f"Movie Name: {movie_name}",
        f"Screen Name: {screen_name}",
        f"Seat Numbers: {', '.join(seat_numbers)}", f"Show Date: {show_date}",
        f"Show Time: {show_time}", f"Amount: ${amount}"
    ]

    # Draw the content on the PDF
    c.setFont("Helvetica", 12)
    c.drawString(100, 700, "Movie Ticket")
    c.setFont("Helvetica", 10)

    y_position = 680  # Initial y-position for text
    for line in content:
        c.drawString(100, y_position, line)
        y_position -= 20  # Move to the next line

    # Save the PDF
    c.save()


# def create_movie_ticket(ticket_id, movie_name, screen_name, seat_numbers, show_date, show_time, amount):
#     # Create a PDF canvas
#     c = canvas.Canvas("movie_ticket.pdf", pagesize=letter)
#
#     # Define content for the ticket
#     content = f"Ticket ID: {ticket_id}\n"\
#               f"Movie Name: {movie_name}\n"\
#               f"Screen Name: {screen_name}\n"\
#               f"Seat Numbers: {', '.join(seat_numbers)}\n"\
#               f"Show Date: {show_date}\n"\
#               f"Show Time: {show_time}\n"\
#               f"Amount: ${amount}"
#
#     # Draw the content on the PDF
#     c.setFont("Helvetica", 12)
#     c.drawString(100, 700, "Movie Ticket")
#     c.setFont("Helvetica", 10)
#     c.drawString(100, 680, content)
#
#     # Save the PDF
#     c.save()

# Example usage
# ticket_id = "123456789"
# movie_name = "Example Movie"
# screen_name = "Screen 1"
# seat_numbers = ["A1", "A2", "A3"]
# show_date = "2024-05-04"
# show_time = "18:00"
# amount = "30"
#
# create_movie_ticket(ticket_id, movie_name, screen_name, seat_numbers, show_date, show_time, amount)


@login_manager.user_loader
def load_user(user_id):
    user_dict = db.signup.find_one({'email': user_id})
    if user_dict:
        return User(user_dict)
    return None


@app.route('/')
def index():

    return render_template('index.html', loginstatus=login, current_user=U)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        name = request.form['signup_name']
        email = request.form['signup_email']
        password = request.form['signup_password']

        existing_user = users_collection.find_one({'email': email})
        if existing_user:
            flash("Email Already Exist", "warning")
            return render_template('/signup.html')

        users_collection.insert_one({
            'username':
            name,
            'email':
            email,
            'password':
            generate_password_hash(password)
        })

        flash("Signup Success Please Login", "success")

    return render_template('index.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    global U
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        user_dict = users_collection.find_one({'username': username})

        if user_dict and check_password_hash(user_dict['password'], password):
            collection.delete_many({})
            collection.insert_one({"id": username})
            return render_template('kannadaaction.html')
    return render_template('index.html')


@app.route('/theaterlist')
def theaterlist():
    return render_template('Theater_List.html')


@app.route('/Book_Seats')
def book_seats():
    return render_template('Book_Seats.html')


@app.route('/store_data/<id>', methods=['POST'])
def store_data(id):
    if request.method == 'POST':
        movie = request.form[f'ka_actmv_{id}']
        collection.insert_one({'movie': movie})
        print(movie)
        return render_template('Theater_List.html')
    return render_template('Book_Seats.html')


@app.route('/store_data/t/<id>', methods=['POST'])
def store_theater_data(id):
    if request.method == 'POST':
        theater = request.form[f't{id}']
        collection.insert_one({'theater': theater})
        print(theater)
        return render_template('Book_Seats.html')
    return render_template('Theater_List.html')


@app.route('/store_seating', methods=['POST'])
def store_seating():
    if request.method == 'POST':
        seates = request.form.getlist('tickets')
        date = request.form['trip-start']
        time = request.form['date']
        amount = request.form['amount']
        print(seates, date, time)
        collection.find_one({'id': ticket_id})
        collection.find_one({'movie': movie_name})
        collection.find_one({'theater': screen_name})
        collection.insert_one({'seates': seates})
        collection.insert_one({'date': date})
        collection.insert_one({'time': time})
        collection.insert_one({'amount': amount})

        create_movie_ticket(ticket_id, movie_name, screen_name, seates, date,
                            time, amount)
        return send_file('movie_ticket.pdf', as_attachment=True)
    return render_template('Book_Seats.html')

@app.route('/<movie>')
def movielist(movie):
    return render_template(f'{movie}.html')

if __name__ == "__main__":
    app.run(debug=True)
