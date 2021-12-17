
Title of Project: Movie Watch Party

Contributors: Avery Park, Jayden Personnat, Rain Wang 

Summary: Movie Watch Party is a web social app for Harvard students implemented with HTML, CSS, and Python Flask

Background: 
In Movie Watch Party, Harvard students can register for an account, make friends with other users on the sight, and schedule movie dates with their friends. After a user has created an approriate username and password, the site then prompts a user to create a profile where they will input their first and last name, graduation year, dorm, and top three favorite movie genres. From there, users will be redirected to a "matches" page, where they will be able to see information and send friend requests to three users that share similar genre "tastes". Once a user has logged in, they can access five pages: "Home", "My Profile", "My Friends", "Movie Planner", and "Notifications". On "Home", the user can view a carousel that includes all the events that they are hosting or have signed up for. On each caurosel, users can click to see more information about the event, and for each host, the info page includes a button where they cancel the event. On "My Profile", users can see their own profile, which includes their profile picture, their username, dorm, favorite genre, and class year. If a user wants to ever change their profile for some reason, they can do so by clicking the "Change Profile" button and filling out a form. Next, on the "My Friends" page, a user will see a chart showing information about each of their friends. In the chart, there are also two buttons, "View Profile" and "Unfriend" which users can click to view their friends' profiles or "unfriend" a friend that they had made previously. "Movie Planner" includes a form where users can create an event and select friends to send invites to. Lastly, in "Messages", users can accept or decline friend requests and invites and view messages that say whether a request has been accepted or an event has been cancelled. If their inbox gets "too full", users have the option to clear specific messages. 

In addition to the features outlined above, there is a search bar that allows users to search and find other users on the site. From there, users have the option to send a friend request to another user.  


Getting Started:
1. Download the project.zip file into your computer and open it. 

2. Open VS code and open a new folder. In Finder (or Windows Explorer for Mac), look for the project folder from the project.zip file. Select the project folder to be opened in VS code and open a new terminal.

3. Ensure that you are in the project directory. If not, make sure to execute cd project. Then, execute ls to see the files in the directory. You should see the following files and folders: game.db, DESIGN.md, app.py, helpers.py, static/, templates/. There may also be some other folders relating to the dependencies that were installed for the project. 

4. Before running the project, you'll need to install some dependencies (if they haven't been already installed). 

5.  First, install the Python extension by clicking on "Extensions" in the left tool bar. Search for "python" and install the first extension that comes up (should have a blue check from Microsoft). 

6. Next download a sqlite extension. Again, go to "Extensions" and search "sqlite". Download the first extension that appears (from "alexcvzz"). 

6. Then, install a version of Python 3 from the following link: https://www.python.org/downloads/. You should download the latest version (which typically appears first on the page).

7. From here, you'll need to create and activate a virtual environment called .venv. Depending on your operating system, execute one of the following commands:
Linux
python3 -m venv .venv
source .venv/bin/activate

macOS
python3 -m venv .venv
source .venv/bin/activate

Windows
py -3 -m venv .venv
.venv\scripts\activate

8. In VS code, open the Command Palette (View > Command Palette). Select the Python: Select Interpreter command. The command will then show a list of available interpreters; select the one that begins with ./.venv or .\.venv. 

9. Update pip in the virtual environment by running the following command: python -m pip install --upgrade pip

10. Install Flask in the virtual environment by executing the following command: python -m pip install flask

11. Install Flask-Session by executing the following command: pip3 install Flask-Session

12. Install the CS50 library by executing the following command: pip3 install cs50.

** Note: If you are having any trouble, refer to this source: https://code.visualstudio.com/docs/python/tutorial-flask. The instructions above are taken from this source. 

**Note: if you already have all the extensions, modules, and libraries install, all you need to do is ensure that you are running the project in a virtual enviroment. After you cd into the project folder, create and active a virtual environment by following step 7. 

***Note: Before running, you'll want to go into app.py and define a path to the images folder on line 25. You'll need to define a path that is specific for your computer. To find the path, find the project folder in Finder (which likely was in downloads), go inside the static folder, right click on the images folder, and click on Get Info. In Get Info, under General there is a section called Where that shows the the path to the image folder. 

To define your path, format it as so: /Users/[username]/[location (e.g. downloads)]/project/static/images. 
Here is an example:
"Users/averypark/downloads/project/static/images". 



Running:
1. To view this site after a virtual enviroment has been activated, execute flask run in your terminal, and open the URL that will appear in your terminal. 
2. If you would like access the SQL tables in game.db, execute sqlite3 game.db in your terminal. From there you can run .schema to see the create tables and make SQL queries. 

Testing:

To test our website, we are providing you with the login information of the following users on the website:

Username:           Password:
jaydenpersonnat     personnat 
averypark           park
rainwang            wang
johnharvard         harvard
harrypotter         potter 

Feel free to create your own users as well to test!


Video URL: https://www.youtube.com/watch?v=7XSjAAw-PNk # MovieWatchParty
