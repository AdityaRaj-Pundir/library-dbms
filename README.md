# Library Database Management System
#### Video Demo:  https://youtu.be/p3PEtIO9NOY
#### Try It: https://library-dbms-69c7.onrender.com/login
#### Python-only Version: https://github.com/AdityaRaj-Pundir/library-dbms-python

> [!NOTE]
> When opening the site, you may experience a delay (Up to a minute) or the site may say `Not found` when accessing. If so, refresh the page. This is a problem with Render's free tier for hosting flask applications
#### Description: Online Library Management System that allows for its users to issue and return books, search authors or books available in the library's database, and keep a log of all their issues.

## Starting with the Library Database Management System
The LDBMS requires a user to register an account or login to an existing account to avail its features. The passwords are hash encrypted and are not stored in the database, so that the user's account remains secured.

## Landing Page
Users who log in to the LDBMS are greeted with a landing page that greets them and displays their issued books. If there are no issued books, the website provides a link for the user to issue books. This page only shows the user their currently issued books, and not books that they issued and have already returned (that happens in the log).

This is achieved by adding an extra constraint to the SQL query that gives the index page its data.
```
select * from issues where ... and returndate is null;
```
This makes sure that the books that are displayed on the index page have not been returned, and are thereforecurrently issued by the user.

## Search Page
Users can search for their favorite books or authors that are in the library's database with the help of this page. The backend SQL query uses the like operator instead of the = operator so that the user can get all the fitting results to their searches without having to memorize the name of the book.

For example:
```
select * from books where bookname = 'Harry Potter';
```
Would result in no results, because the Harry Potter books are titled differently (Harry Potter and the Goblet of Fire, etc.). But, using a different SQL query, like so:
```
select * from books where bookname like 'Harry Potter';
```
Would be much more effective in helping the user find their preferred book.

Similarly, an SQL query usingthe like operator was also used to help users search for their favorite authors.

## Issue Books
Users can issue books easily with the issue books page. When opening the issue book page, users are greeted with a table that shows them the bookid and name of all books in the library's database, and if they have been issued by a user or not. They can also see who the book is issued by.

To issue a book, a user has to type in the book's BookID into a form. If the book has already been issued by another user or themselves, they will be shown an error message that tells them that the book has already been issued. The book should be returned within 14 days, or they shall be fined.

## Returning Books
The return books page shows users the books they currently have issued, so that they have easy access to the Book IDs of their issued books. If the user has no issued books, they will be provided with a link to issue a book. If the user tries returning a book they have not issued, they will be shown an error message that tells them where they went wrong. Similarly, there will be error messages for books that don't exist.

## Log
The log shows the user all of their issues, even those that have been returned, along with the fines that had been applied (if applicable) on each issue. If the user never issued a book, they are provided with a link to the issue books page. In the SQL query that gives the log its data, there is no `returndate is null` condition. Thus, the log also shows the users previous issues, even if the user has issued the same book more than once.

## Fines for Returning a Book Late
The LDBMS automatically calculates the fines that are applicable to each of the user's issues. The user is fined $5 for each day they keep the book for over 2 weeks (14 days). SO, if the user keeps a book for 30 days, they will be fined 5*16 = $80.

This was accomplished using python's datetime module.
```
from datetime import datetime
rday = datetime.today() # Returns today's date
days = rdate - datetime.strptime(issuedate, '%Y-%m-%d') # Calculates how many days have passed since the book was issued
# strptime was used to convert the date acquired from sqlite as a string to a datetime.datetime type
if days > 14:
    (fine)...
else:
    (return without fining)...
```

## Thank you for reading!
### Happy hacking!

