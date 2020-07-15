import sqlite3
from sqlalchemy import create_engine
engine = create_engine('sqlite:///getitem.db', echo=True)
from sqlalchemy.ext.declarative import declarative_base



con = sqlite3.connect("getitem.db") ##db이름
cur = con.cursor()
cur.execute("CREATE TABLE users(id INTEGER NOT NULL, name VARCHAR NOT NULL, password VARCHAR NOT NULL, email VARCHAR, phone VARCHAR, PRIMARY KEY (id));")
cur.execute("CREATE TABLE product(product_id INTEGER NOT NULL, title VARCHAR NOT NULL, start_val VARCHAR  NOT NULL, current_val VARCHAR NOT NULL, name VARCHAR NOT NULL, board VARCHAR, picture VARCHAR, days INTEGER, PRIMARY KEY(product_id));")
cur.execute("CREATE TABLE message(message_id INTEGER, author_id INTEGER NOT NULL, text VARCHAR NOT NULL, pub_date INTEGER, PRIMARY KEY (message_id));")



cur.execute("INSERT INTO users VALUES(1, '조항정', '1234', 'stneowh@naver.com', '010-0000-0000');")
cur.execute("INSERT INTO product VALUES(1, '테스트title', '300000', '300000', 'admin', '테스트board', 'static/img/test.png', 5);")

con.commit()
