#!/usr/bin/python


"""
This is what I'm thinking the API would look like in use:

psql db -c 'SELECT domain, time, count FROM sometable;' \
    | curl -s http://databin.com/' \
           -d domain=text \
           -d time='timestamp with timezone' \
           -d count=integer \
           -d data=@-
"""


from pg8000 import DBAPI
import os

def connector():
    """Get a connection context."""
    class conctx:
        def __enter__(self):
            self.con = DBAPI.connect(
                host="localhost", 
                database=os.environ.get("DATABIN_DB", "databin"),
                user="nferrier"
                )
            return self.con

        def __exit__(self, type, values, traceback):
            self.con.close()

    return conctx()

def get(tablename, stream):
    """Return  some representation of the specified table"""
    with connector() as con:
        cursor = con.cursor()
        cursor.execute("SELECT * from %(tablename)s;" % {"tablename": tablename})
        names = [desc[0] for desc in cursor.description]
        header = ["""<th id="%s">%s</th>""" % ("id__%s" % name, name) 
                  for name in names]
        print >>stream, "<table>\n<tr>\n%s\n</tr>" % "\n".join(header)
        for row in cursor.fetchall():
            print >>stream, "<tr>"
            for name,col in zip(names,row):
                print >>stream, """<td header="%s">%s</td>""" % ("id__%s" % name, col)
        print >>stream, "%s\n</table>\n"

def csvmake(tablename, stream, **kwargs):
    """Oh look. I've invented COPY"""
    sql_decls = ['"%s" %s' % (n, t) for n,t in kwargs.iteritems()]
    with connector() as con:
        cursor = con.cursor()
        metadata = {
            "tablename": tablename,
            "defuns": ",\n".join(sql_decls),
            }
        create_sql = """CREATE TABLE %(tablename)s (
"id" SERIAL NOT NULL PRIMARY KEY,
%(defuns)s
);""" % metadata
        cursor.execute(create_sql)
        con.commit()

        # Get the data in there
        fieldnames = stream.readline().split(",")
        cursor.copy_from(
            stream, 
            query="COPY %s (%s) FROM stdout DELIMITER ',' ;" % (
                tablename,
                ",".join(fieldnames)
                )
            )
        con.commit()


import cgi

def handle_args(argv, stream):
    """Abstracted command line arg handler. Useful for tests"""
    csvmake(
        argv[1], 
        stream, 
        **dict(
            cgi.parse_qsl("&".join(argv[2:]))
            )
        )
    
def main():
    import sys
    handle_args(sys.argv)

if __name__ == "__main__":
    main()
    
# End
