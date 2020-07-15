import sqlite3
from sqlalchemy import create_engine
engine = create_engine('sqlite:///getitem.db', echo=True)
from sqlalchemy.ext.declarative import declarative_base



con = sqlite3.connect("test.db") ##db이름
cur = con.cursor()
cur.execute("CREATE TABLE users(id INTEGER NOT NULL, name VARCHAR NOT NULL, password VARCHAR NOT NULL, email VARCHAR, phone VARCHAR, PRIMARY KEY (id));")


cur.execute("INSERT INTO users VALUES(1, '조항정', '1234', 'stneowh@naver.com', '010-0000-0000');")

con.commit()
