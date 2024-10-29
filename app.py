from flask import Flask, render_template, request, redirect, session, jsonify, flash
import requests


app = Flask(__name__)
app.secret_key = 'hamburger'

# cant be bothered to make a database so I will store single user here
users = {}
liked_movies = []

@app.route('/')
def index():
    # clear session
    # session.clear()
    print(users)
    # get request to get movies
    movies = []
    data = requests.get('https://api.themoviedb.org/3/trending/movie/week?api_key=9161e693ca8646c3ec83632bd13e1b72')
    for movie in data.json()['results']:
        movie = {
            'title': movie['title'],
            'poster': 'https://image.tmdb.org/t/p/w500' + movie['poster_path'],
            'overview': movie['overview'],
            'release_date': movie['release_date'],
            'link': 'https://www.themoviedb.org/movie/' + str(movie['id'])
        }
        movies.append(movie)
    return render_template('index.html', movies=movies)

@app.route('/likes')
def likes():
    if 'email' not in session:
        return redirect('/login')
    return render_template('likes.html', liked_movies=liked_movies)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/profile')
def profile():
    if 'email' not in session:
        return redirect('/login')
    user = users[session['email']]
    return render_template('profile.html', user=user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    # Get the info from the form
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

    # Check for missing fields
    if not name or not email or not password:
        flash('Please fill out all fields.', 'error')
        return redirect('/register')

    # Check for duplicate email
    if email in users:
        flash('Email already registered. Please use a different email.', 'error')
        return redirect('/register')

    try:
        # Store the user in the users dict
        users[email] = {
            'name': name,
            'email': email,
            'password': password
        }
        session['email'] = email
        print(users)
    except Exception as e:
        flash('An error occurred while registering. Please try again.', 'error')
        print(f"Error: {e}")  # Log the error for debugging
        return redirect('/register')

    return redirect('/profile')

@app.route('/like', methods=['POST'])
def like_movie():
    if 'email' not in session:  # Check if the user is logged in
        return redirect('/login')  # Redirect to login if not authenticated

    movie_title = request.json.get('title')  # Get the movie title from the request
    movie_description = request.json.get('description')
    movie_poster = request.json.get('poster')

    movie = {
        'title': movie_title,
        'description': movie_description,
        'poster': movie_poster
    }

    liked_movies.append(movie)  # Add the movie to the liked movies list

    print(movie_title)  # Debugging: Print the liked movie title
    return jsonify({'status': 'success', 'message': f'Liked {movie_title}'}), 200