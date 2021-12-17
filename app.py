import os 

import sys
from datetime import datetime, timedelta
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask_session import Session
import sqlite3
from functools import wraps
from helpers import login_required, convert

app = Flask(__name__)

# Debug
if __name__ == '__main__':
    app.debug = True
    app.run()

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# configure path to image folder
app.config["IMAGE_UPLOADS"] = "/Users/jaydenpersonnat/project/static/images"

db = SQL("sqlite:///game.db")

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Define path for upload folder 
UPLOAD_FOLDER = '/path/to/static/images' 

# List of student dorms 
dorms = ['Apley Court', 'Canaday', 'Grays', 'Greenough', 'Hollis', 'Holworthy', 'Hurlbut', 'Lionel', 'Mower', 'Matthews', 'Pennpacker','Prescott',
'Stoughton', 'Straus', 'Thayer', 'Weld', 'Wigglesworth', 'Adams', 'Cabot', 'Currier', 'Dunster', 'Dewolfe', 'Eliot', 'Kirkland', 
'Leverett', 'Lowell', 'Mather', 'Pforzheimer', 'The Inn','Quincy', 'Wintrop', 'The Prescotts']

# Dict of Movie Genres
genres = {'Adventure': 10, 'Action': 20, 'Drama': 30, 'Comedy': 40, 'Thriller': 50, 'Horror': 60, 'Romance': 70, 'Musical': 80, 'Documentary': 90, 'Sci-Fi': 100, 'Rom-Com': 110, 'Fantasy': 120}


@app.route("/")
@login_required
def index():
    # Select all event_ids for events user is going to and hosting and combine into one list of dictionaries
    events_hosting = db.execute("SELECT * FROM events JOIN profiles ON events.host_id = profiles.user_id WHERE host_id = ?", session["user_id"])
    events_going = db.execute("SELECT * FROM events JOIN profiles ON events.host_id = profiles.user_id WHERE event_id IN (SELECT event_id FROM invites WHERE sender_id = ? AND type = ?)", session["user_id"], "rsvp")
    all_events = events_hosting + events_going
    
    # Sort events by date and time for carousel on home page
    all_events.sort(key = lambda x: (x["date"], x["time"]))

    # If user has no events, print message saying that no events have been signed up for
    if len(all_events) == 0:
        return render_template("error.html", message = "sign up for some events", code = 400)
    
    # Take user to home page 
    return render_template("index.html", events = all_events)


@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        # Get three inputs from user to register 
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # if user puts in invalid username and/or password return error message
        if not username: 
            return render_template("error.html", message = "fill in all fields", code = 400)
        if password != confirmation:
            return render_template("error.html", message = "passwords do not match", code = 400)
        try:
            id = db.execute("INSERT INTO users (username, password, friends, score) VALUES(?, ?, ?, ?)",
                            username, generate_password_hash(password), 0, 0)
        except ValueError:
            return render_template("error.html", code = 400, message = "username already taken")

        # Log User In
        session["user_id"] = id
       
        # Bring user to create profile page
        return redirect("/create")

    else:
        return render_template("register.html")


@app.route("/login", methods = ["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()

    if request.method == "POST":
        # Get user input 
        username = request.form.get("username")
        password = request.form.get("password")

        # if user inputs invalid username and/or password, return error message
        if not username or not password:
            return render_template("error.html", code = 403, message = "fill in all fields")
        
        users = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(users) != 1 or not check_password_hash(users[0]["password"], password):
            return render_template("error.html", code = 403, message = "incorrect username and/or password")
        
        # Log user in
        session["user_id"] = users[0]["id"]

        # Bring to index page 
        return redirect("/")
    
    else:
        return render_template("login.html")



@app.route("/create", methods = ["GET", "POST"])
@login_required
def create():
    # initalize user matching  score 
    score = 0
    if request.method == "POST":
        # Get user information for profile page 
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        dorm = request.form.get("dorm")
        top_genre = request.form.get("top_genre")
        second_genre = request.form.get("second_genre")
        third_genre = request.form.get("third_genre")
        year = request.form.get("year")

        # Make default image standard profile pic 
        image_name = "profile.jpg"

        # if user inputs image, upload image to static/images/
        image = request.files["image"]
        if image:
            image.save(os.path.join(app.config["IMAGE_UPLOADS"], image.filename))
            image_name = image.filename 
        
        # user can only submit create profile form once 
        if len(db.execute("SELECT * FROM profiles WHERE user_id = ?", session["user_id"])) > 0:
            return render_template("error.html", message = "you already submitted this form", code = 400)

        # make sure users provide valid input for each field 
        if not first_name or not last_name or not dorm or not top_genre or not second_genre or not third_genre or not year:
            return render_template("error.html", code = 400, message = "fill in all fields", profile = False)
        if top_genre == second_genre or top_genre == third_genre or second_genre == third_genre:
            return render_template("error.html", code = 400, message = "please do not pick the same genres", profile = False)

        # Calculate matching score based on genres picked 
        score = 100 * genres[top_genre] + 10 * genres[second_genre] + genres[third_genre]

        # Input information above into profiles and users table 
        db.execute("INSERT into profiles (user_id, first_name, last_name, dorm, year, genre, image) VALUES (?, ?, ?, ?, ?, ?, ?)", session["user_id"], first_name, last_name, dorm, year, top_genre, image_name)
        db.execute("UPDATE users SET score = ? WHERE id = ?", score, session["user_id"])

        # redirect to matches page to show users' matches
        return redirect("/match")
    else:
        return render_template("create.html", genres = genres, dorms = dorms)


@app.route("/profile")
@login_required
def profile():
    # if user hasn't created a profile, return error message 
    if len(db.execute("SELECT * FROM profiles WHERE user_id = ?", session["user_id"])) == 0:
        return render_template("error.html", message = "you need to create a profile", code = 400, profile = False)
    
    # Select information for profile page
    user = db.execute("SELECT * FROM users JOIN profiles ON users.id = profiles.user_id WHERE id = ?", session["user_id"])[0]
    return render_template("profile.html", user = user, view = False)


@app.route("/match", methods = ["GET", "POST"])
@login_required
def match():
    
    # select matching scores from all users in table 
    score = db.execute("SELECT score FROM users WHERE id = ?", session["user_id"])[0]["score"]
    scores = db.execute("SELECT * FROM users")

    # compare matching scores to newly registered user
    for dict in scores:
        dict["score"] = abs(score - int(dict["score"]))
        if dict["id"] == session["user_id"]:
            dict["score"] = sys.maxsize

    # sort score differences from least to greatest
    scores = sorted(scores, key = lambda x:x["score"])

    # Find three matches with closest score
    matches = scores[ : 3]

    # Select information on matches
    profiles = db.execute("SELECT DISTINCT(users.username), * FROM users JOIN profiles ON users.id = profiles.user_id WHERE profiles.user_id = ? OR profiles.user_id = ? OR profiles.user_id = ?", matches[0]["id"], matches[1]["id"], matches[2]["id"])


    if request.method == "POST":
        # Making a friend request 
        friend = request.form.get("friend")
        friend_one = db.execute("SELECT * FROM friends WHERE friend_one = ? and friend_two = ?", session["user_id"], friend)
        friend_two = db.execute("SELECT * FROM friends WHERE friend_one = ? and friend_two = ?", friend, session["user_id"])
        follow = db.execute("SELECT * FROM messages WHERE sender_id = ? AND receiver_id = ? AND type = ?", session["user_id"], friend, "request")

        # provide error message if user attempts to request or follow someone more than once
        if len(friend_one) != 0 or len(friend_two) != 0:
            return render_template("error.html", code = 400, message = "you already follow this person")
        if len(follow) > 0:
            return render_template("error.html", code = 400, message = "you already requested to follow this user", match_pg = True)

        # Insert information into messages table 
        db.execute("INSERT INTO messages (sender_id, receiver_id, message, type) VALUES (?, ?, ?, ?)", session["user_id"], friend, "you got a friend request", "request")
    
       # Redirect back to match page 
        return redirect("/match")

    else:
        return render_template("matches.html", matches = matches, profiles = profiles)


@app.route("/message", methods = ["GET", "POST"])
@login_required
def message():
    # Select info to show on notifications page 
    requests = db.execute("SELECT * FROM messages JOIN profiles ON messages.sender_id = profiles.user_id WHERE messages.receiver_id = ? AND messages.type = ?", session["user_id"], "request")
    messages = db.execute("SELECT * FROM messages JOIN profiles ON messages.sender_id = profiles.user_id WHERE receiver_id = ? AND (type = ? or type = ?)", session["user_id"], "accept", "cancel")
    invites = db.execute("SELECT * FROM invites JOIN profiles ON invites.sender_id = profiles.user_id WHERE receiver_id = ? AND type = ?", session["user_id"], "invite")

    if request.method == "POST":
        # Allow user to clear messages
        delete = request.form.get("delete")
        if delete:
            db.execute("DELETE FROM messages WHERE message_id = ?", delete)
            return redirect("/message")

        clear = request.form.get("clear")
        if clear:
            db.execute("DELETE FROM invites WHERE event_id = ? AND receiver_id = ?", clear, session["user_id"])
            return redirect("/message")

        friend = request.form.get("friend")
        friend_one = db.execute("SELECT * FROM friends WHERE friend_one = ? and friend_two = ?", session["user_id"], friend)
        friend_two = db.execute("SELECT * FROM friends WHERE friend_one = ? and friend_two = ?", friend, session["user_id"])
        event = request.form.get("invite")

        # Show user an invitation to an event 
        if event:
            events = db.execute("SELECT * FROM events WHERE event_id = ?", event)[0]
            for event in events:
                return render_template("invites.html", events = events, time = convert(events["time"]))

        # prevent user from accepting friend request more than once
        if len(friend_one) != 0 or len(friend_two) != 0:
            return render_template("error.html", code = 400, message = "you already follow this person")
        
        # allow user to decline friend_request
        if int(friend) < 0:
            db.execute("DELETE FROM messages WHERE sender_id = ? AND receiver_id = ? AND type = ?", int(friend) * -1, session["user_id"], "request")
            # db.execute("DELETE FROM messages WHERE sender_id = ? AND receiver_id = ?", session["user_id"], int(friend) * -1)
            return render_template("error.html", code = 200, message = "you successfully declined the request")

        # Once a friend request has been accepted, create friendship by inserting into tables referenced below
        db.execute("INSERT INTO messages (sender_id, receiver_id, message, type) VALUES (?, ?, ?, ?)", session["user_id"], friend, "your request was accepted", "accept")
        db.execute("INSERT INTO friends (friend_one, friend_two) VALUES (?, ?)", session["user_id"], friend)
        friend_count_one = db.execute("SELECT friends FROM users WHERE id = ?", session["user_id"])[0]["friends"]
        friend_count_two = db.execute("SELECT friends FROM users WHERE id = ?", friend)[0]["friends"]
        db.execute("UPDATE users SET friends = ? WHERE id = ?", friend_count_one + 1, session["user_id"])
        db.execute("UPDATE users SET friends = ? WHERE id = ?", friend_count_two + 1, friend)
        db.execute("DELETE FROM messages WHERE sender_id = ? AND receiver_id = ? AND type = ?", friend, session["user_id"], "request")

        # redirect back to message page 
        return redirect("/message")
    else:
        return render_template("messages.html", requests = requests, messages = messages, invites = invites)

@app.route("/rsvp", methods = ["POST"])
@login_required
def rsvp():
    # Allow user to rsvp for an event they are invited to 
    rsvp = request.form.get("rsvp")
    attending = db.execute("SELECT * FROM invites WHERE event_id = ? AND sender_id = ? AND type = ?", rsvp, session["user_id"], "rsvp")
    host = db.execute("SELECT host_id FROM events WHERE event_id = ?", rsvp)[0]["host_id"]
    # prevent user from rsvp'ing for event more than once
    if len(attending) > 0:
        return render_template("error.html", message = "you already rsvp'd for this event", code = "400")
    
    db.execute("INSERT INTO invites (event_id, sender_id, receiver_id, message, type) VALUES (?, ?, ?, ?, ?)", rsvp, session["user_id"], host, "someone rsvp'd for your event", "rsvp")

    return redirect("/")

@app.route("/friends")
@login_required
def friend():
    # Get user id of all friends
    friend_one = db.execute("SELECT friend_two FROM friends WHERE friend_one = ?", session["user_id"])
    friend_two = db.execute("SELECT friend_one FROM friends WHERE friend_two = ?", session["user_id"])

    # Combine list of dictionaries above 
    combined_dict = friend_one + friend_two

    # Create a list to store id of all friends of user 
    friend_list = []
    for element in combined_dict:
       for key in element:
           friend_list.append(element[key])

    # Select information from friends' profiles 
    users = db.execute("SELECT DISTINCT(username), users.id, first_name, last_name, dorm FROM users JOIN profiles ON profiles.user_id = users.id AND users.id IN (?)", friend_list)

    return render_template("friends.html", users = users)


@app.route("/planner", methods = ["GET", "POST"])
def planner():
    if request.method == "POST":
        # get user input for event 
        fullname = request.form.get("fullname")
        movie = request.form.get("movie")
        date = request.form.get("date")
        time = request.form.get("time")
        location = request.form.get("location")
        description = request.form.get("description")
        invites = request.form.getlist("invites")
        image = request.files["image"]

        # if user does not fill in all fields provide error message 
        if not fullname or not movie or not date or not location or not time or not image:
            return render_template("error.html", message = "fill in all required fields", code = 400)
        
        # get user's "cover" for event 
        image.save(os.path.join(app.config["IMAGE_UPLOADS"], image.filename))

        # Insert into events table 
        db.execute("INSERT INTO events (host_id, fullname, movie, date, time, location, description, cover) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", session["user_id"], fullname, movie, date, time, location, description, image.filename)

        # Create invitations for users invited to event 
        event = db.execute("SELECT event_id FROM events WHERE host_id = ? ORDER BY event_id DESC LIMIT 1", session["user_id"])[0]["event_id"]
        for invite in invites:
            db.execute("INSERT INTO invites (event_id, sender_id, receiver_id, message, type) VALUES (?, ?, ?, ?, ?)", event, session["user_id"], invite, "you got invited to an event", "invite")

        return redirect("/")
        
    else:
        # Select all friends
        friend_one = db.execute("SELECT friend_two FROM friends WHERE friend_one = ?", session["user_id"])
        friend_two = db.execute("SELECT friend_one FROM friends WHERE friend_two = ?", session["user_id"])

        # Combine list of dictionaries above 
        combined_dict = friend_one + friend_two

        # Create a list to store id of all friends of user 
        friend_list = []
        for element in combined_dict:
            for key in element:
                friend_list.append(element[key])

        # Select info from friends
        users = db.execute("SELECT DISTINCT(username), users.id, first_name, last_name, dorm FROM users JOIN profiles ON profiles.user_id = users.id AND users.id IN (?) ORDER BY first_name", friend_list)

        # Use to prevent user from picking date before today
        tmr = datetime.now() + timedelta(1)
        tmr = tmr.strftime('%Y-%m-%d')
        return render_template("planner.html", tmr = tmr, users = users)

@app.route("/info", methods = ["POST"])
@login_required
def info():
    # Get event info 
    event = request.form.get("event")

    # Obtain info about all attendees (who have rsvp'd) for event 
    attendees = db.execute("SELECT * FROM profiles JOIN invites ON invites.sender_id = profiles.user_id WHERE type = ? AND event_id = ?", "rsvp", event)
    events = db.execute("SELECT * FROM events WHERE event_id = ?", event)[0]

    # Convert time to 12 hour format
    time = convert(events["time"])

    # Bring user to info page on the event 
    return render_template("info.html", events = events, people = attendees, time = time)

@app.route("/cancel", methods = ["POST"])
def cancel():
    # Allow user to cancel event 
    cancel = request.form.get("cancel")

    # Send cancel message to users who rsvp'd for the event 
    attendees = db.execute("SELECT * FROM profiles JOIN invites ON invites.sender_id = profiles.user_id WHERE type = ? AND event_id = ?", "rsvp", cancel)
    if cancel:
        movie = db.execute("SELECT movie FROM events WHERE event_id = ?", cancel)[0]["movie"]
        for people in attendees:
            db.execute("INSERT INTO messages (sender_id, receiver_id, message, type) VALUES (?, ?, ?, ?)", session["user_id"], people["user_id"], f"{movie} was cancelled", "cancel")
        db.execute("DELETE FROM invites WHERE event_id = ?", cancel)
        db.execute("DELETE FROM events WHERE event_id = ?", cancel)
        return redirect("/")



@app.route("/unfriend", methods = ["POST"])
def unfriend():
    # Allow users to unfriend friends they currently have 
    friend_id = request.form.get("unfriend")
    db.execute("DELETE FROM friends WHERE (friend_one = ? AND friend_two = ?) OR (friend_one = ? AND friend_two = ?)", session["user_id"], friend_id, friend_id, session["user_id"])
    friend_count_one = db.execute("SELECT friends FROM users WHERE id = ?", session["user_id"])[0]["friends"]
    friend_count_two = db.execute("SELECT friends FROM users WHERE id = ?", friend_id)[0]["friends"]
    db.execute("UPDATE users SET friends = ? WHERE id = ?", friend_count_one - 1, session["user_id"])
    db.execute("UPDATE users SET friends = ? WHERE id = ?", friend_count_two - 1, friend_id)

    return redirect("/friends")

@app.route("/view", methods = ["POST"])
def view():
    # Allow user ot view profiles of friends on friend page
    profile = request.form.get("profile")
    user = db.execute("SELECT * FROM users JOIN profiles ON users.id = profiles.user_id WHERE id = ?", profile)[0]
    return render_template("profile.html", user = user, view = True)


@app.route("/search", methods = ["POST"])
def search():
    # Allow users to search for other users
    search = request.form.get("search")
    users = db.execute("SELECT * FROM users JOIN profiles ON profiles.user_id = users.id WHERE username LIKE ?", f"%{search}%")

    # if not user found, print error message
    if not search or len(users) == 0:
        return render_template("error.html", code = 400, message = "No results found, try again")
    return render_template("search.html", users = users)

@app.route("/follow", methods = ["POST"])
def follow():
    # Making a friend request after a search result
        friend = request.form.get("follow")
        friend_one = db.execute("SELECT * FROM friends WHERE friend_one = ? and friend_two = ?", session["user_id"], friend)
        friend_two = db.execute("SELECT * FROM friends WHERE friend_one = ? and friend_two = ?", friend, session["user_id"])
        follow = db.execute("SELECT * FROM messages WHERE sender_id = ? AND receiver_id = ? AND type = ?", session["user_id"], friend, "request")

        # make sure user does not friend someone twice 
        if len(friend_one) != 0 or len(friend_two) != 0:
            return render_template("error.html", code = 400, message = "you already follow this person")

        if len(follow) > 0:
            return render_template("error.html", code = 400, message = "you already requested to follow this user")

        # prevent user from following themselves
        if int(friend) == session["user_id"]:
            return render_template("error.html", message = "you can't follow yourself!", code = 400)     

        # Insert information into messages table 
        db.execute("INSERT INTO messages (sender_id, receiver_id, message, type) VALUES (?, ?, ?, ?)", session["user_id"], friend, "you got a friend request", "request")
       
       # Redirect back to match page 
        return redirect("/")

@app.route("/change", methods = ["POST"])
@login_required
def change():
    # Allow user to change profile information 
    change = request.form.get("change")
    existing_info = db.execute("SELECT * FROM users JOIN profiles ON users.id = profiles.user_id WHERE users.id = ?", change)[0]
    fav_genre = existing_info["genre"]
    curr_dorm = existing_info["dorm"]

    return render_template("change.html", change = change, info = existing_info, genres = genres, dorms = dorms, fav_genre = fav_genre, curr_dorm = curr_dorm)

@app.route("/update", methods = ["POST"])
@login_required
def update():
    # Update user profile profile information after making request to change 
    username = request.form.get("username")
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    dorm = request.form.get("dorm")
    genre = request.form.get("genre")
    year = request.form.get("year")

    # require user to fill in all fields (except image)
    if not first_name or not last_name or not dorm or not genre or not year:
            return render_template("error.html", code = 400, message = "fill in all fields")

    db.execute("UPDATE users SET username = ? WHERE id = ?", username, session["user_id"])
    db.execute("UPDATE profiles SET first_name = ?, last_name = ?, dorm = ?, genre = ?, year = ? WHERE user_id = ?", first_name, last_name, dorm, genre, year, session["user_id"])

    image = request.files["image"]

    # if user uploads image, update profile image  
    if image:
        image.save(os.path.join(app.config["IMAGE_UPLOADS"], image.filename))
        db.execute("UPDATE profiles SET image = ? WHERE user_id = ?", image.filename, session["user_id"])
    
    return redirect("/profile")

@app.route("/logout")
def logout():
    # Logout user and forget id; take user back to login 
    session.clear()
    
    return redirect("/login")
