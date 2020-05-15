# Finance
A web application where you can sign in to play with the stocks market in real time. T
The website was built using HTML &amp; CSS in the front-end, while in the back-end, I had used Flask(Python) to. 

The idea was to create a web application using the paradigm MVC (Model View Controller) where the "Model" stands for the data 
of the tables and the rows that are inside of the database I created with SQLite3 (i.e. users, password, money and etc.).

The "View" determines what the user actually sees, in that case, these are the templates, the HTML files that display forms for
the user to fill out, the tables that show all the stocks and all the other visual aspects.

Finally, the "Controller" is represented by the application.py, it's the logic that connects the "Model" and the "View" together
The controle is responsible to make database queries to finance.db by running SQL queries and pass these data to a template, to a view
in order to determine what it is the user is actually going to see when they perfom actions with the application.
