import psycopg2
import time
import string

def softMerge(a, b):
    for k in b:
        if k not in a:
            a[k] = b[k]
    return a

class Database:
    def __init__(self, **args):
        softMerge(args, {'dbname': 'postgres',
                         'user': 'mohit.saini',
                         'host':'localhost'})
        self.conn = psycopg2.connect(**args)
        self.conn.autocommit = True
        self.cur = self.conn.cursor()

    def readQuery(self, query, params = None):
        self.queryInternal(query, params)
        titles = [desc[0] for desc in self.cur.description]
        return list(dict(zip(titles, list(row))) for row in self.cur.fetchall())

    def writeQuery(self, query, params = None):
        return self.queryInternal(query, params)

    def queryInternal(self, query, params=None):
        if params is None:
            return self.cur.execute(query)
        else:
            keys = list(x[1] for x in string.Formatter().parse(query)
                                    if x[1] is not None)
            query = query.format(**dict.fromkeys(keys, "%s"))
            params = tuple(params[i] for i in keys)
            return self.cur.execute(query, params)

if __name__ == '__main__':
    database = Database(user="sonu", password="sonu")
    try:
        print(database.readQuery('SELECT * from person where age={age}',
                 {"age": 112, "mohit": 44}))
    except psycopg2.Error as e:
        print(e)
    print("---")
    try:
        print(database.readQuery('SELECT * from perso where age={age}', {"age": 22}))
    except psycopg2.Error as e:
        print(e)
    try:
        print(database.readQuery('SELECT * from person'))
    except psycopg2.Error as e:
        print(e)
    try:
        print(database.writeQuery("insert into person values ('mohit', 112)"))
    except psycopg2.Error as e:
        print(e)
    try:
        print(database.writeQuery('insert into perso values ("mohit", 112)'))
    except psycopg2.Error as e:
        print(e)
    try:
        print(database.readQuery('SELECT * from person'))
    except psycopg2.Error as e:
        print(e)
