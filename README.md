# Bull Marker

Bull Marker is a Stock Trading Game made using Python/Flask in the 
back-end, Jinja for the template engine, SQLite3 as DataBase and 
HTML/JS/CSS (Bootstrap) for the front-end.




The web application provides registration/login for users and real-time stock prices using IEX API. You can buy and sell stocks in real-time and follow the up and down of the prices. Every user starts with 
$10.000,00 and it's up to him or her use that amount of money as they wish.

## About


The idea was to create a web application using the paradigm MVC 
(Model View Controller) where the "Model" stands for the data of the 
tables and the rows that are inside of the database I created with 
SQLite3 (i.e. users, password, money, etc.).




The "View" determines what the user sees, in that case, 
these are the templates, the HTML files that display forms for the user 
to fill out, the tables that show all the stocks and all the other 
visual aspects.




Finally, the "Controller" is represented by the application.py, it's the logic that connects the "Model" and the "View". It's responsible to make database queries to finance.db by running SQL queries and pass these data to a template, to a view to determine what it is the user is going to see when they perform actions with the application.

## Tools 

* Python 3.8.3 - The Back-End
* [Flask](http://flask.palletsprojects.com/en/1.1.x/) - The Web Framework used
* [Jinja](https://www.palletsprojects.com/p/jinja/) - Template Engine
* [SQLite](https://www.sqlite.org/index.html) - Database Engine
* [BootStrap](https://getbootstrap.com/) - Front-End component (Menu)

## API & Widget 

* https://iexcloud.io/docs/api/
* https://tradingview.com/widget/

## Screenshots

![Index](https://github.com/LuisFlavioOliveira/BullMarker/blob/master/Screenshots/Index.png)
![Register](https://github.com/LuisFlavioOliveira/BullMarker/blob/master/Screenshots/Register.png)
![Login](https://github.com/LuisFlavioOliveira/BullMarker/blob/master/Screenshots/Login.png)
![Portfolio](https://github.com/LuisFlavioOliveira/BullMarker/blob/master/Screenshots/Portfolio.png)
![Quote](https://github.com/LuisFlavioOliveira/BullMarker/blob/master/Screenshots/Quote.png)
![Transactions](https://github.com/LuisFlavioOliveira/BullMarker/blob/master/Screenshots/Transactions.png)

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 

### Prerequisites

You will need Python 3.x and the following libraries and packages. Type commands in terminal to install:

`pip install flask`

`pip install flask_session`

`pip install sqlite3`

`pip install cs50`

In addition, you will need a Vantage AUTH Key to access real-time stock data and use this application. 
Request a Key by signing up on [IEX CLOUD](https://iexcloud.io/)

### Installing

A step by step series of examples that tell you how to get a development env running

Download all files into a folder. Ensure that all imported libraries in `app.py` and `helpers.py` are 
installed on your machine or virtual environment.

Edit `helpers.py` by replacing 'AUTH_KEY' in the `lookup()` function with your personal AUTH Key (See prerequisites)

Run the program on your machine or virtual environment.

```
flask run
```

## License / Copyright

* Completed as part of Harvard CS50 Curriculum
* This project is licensed under the MIT License.
