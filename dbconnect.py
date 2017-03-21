import MySQLdb

host = "localhost"
# port=3306
socket = ""
user = "walkwithme"
password = "walkwithme"
dbname = "walk_with_me"


def connect():
    con = MySQLdb.connect(host, user, password, dbname)
    c = con.cursor()
    return (con, c)


def close(con, c):
    c.close()
    con.close()
