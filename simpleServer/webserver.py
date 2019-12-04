from http.server import BaseHTTPRequestHandler, HTTPServer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
import cgi
import cgitb
cgitb.enable()
import logging
logging.basicConfig(level=logging.DEBUG)

def init_db():
    engine = create_engine('sqlite:///restaurantmenu.db')
    # Bind the engine to the metadata of the Base class so that the
    # declaratives can be accessed through a DBSession instance
    Base.metadata.bind = engine

    DBSession = sessionmaker(bind=engine)
    # A DBSession() instance establishes all conversations with the database
    # and represents a "staging zone" for all the objects loaded into the
    # database session object. Any change made against the objects in the
    # session won't be persisted into the database until you call
    # session.commit(). If you're not happy about the changes, you can
    # revert all of them back to the last commit by calling
    # session.rollback()
    session = DBSession()
    return session


class webserverHandler(BaseHTTPRequestHandler):
    _db = None
    def do_GET(self):
        try:
            if self.path.endswith('/restaurants/new'):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Make a New Restaurant</h1>"
                output += "<form method = 'POST' enctype='multipart/form-data' action = '/restaurants/new'>"
                output += "<input name = 'newRestaurantName' type = 'text' placeholder = 'New Restaurant Name' > "
                output += "<input type='submit' value='Create'>"
                output += "</form></body></html>"
                logging.debug("Send message: %s ", output.encode('utf-8'))
                self.wfile.write(output.encode('utf-8'))


            if self.path.endswith('/hello'):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Hello !</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
                output += "</body></html>"
                logging.debug("Send message: %s ", output.encode('utf-8'))
                self.wfile.write(output.encode('utf-8'))

            if self.path.endswith('/restaurants'):
                db = self.__get_db()
                restaurant_items = db.query(Restaurant).all()
                output = "<html><body>"
                output += "<a href = '/restaurants/new' > Make a New Restaurant Here </a></br></br>"
                for item in restaurant_items:
                    output += '<p>'+item.name +'</p>'
                    output += "<a href ='#' >Edit </a> "
                    output += "</br>"
                    output += "<a href =' #'> Delete </a>"
                    output += "</br></br></br>"
                output += "</body></html>"
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                logging.debug("Send message: %s ", output.encode('utf-8'))
                self.wfile.write(output.encode('utf-8'))
            return

        except IOError:
            self.send_error(404, 'File Not Found {}'.format(self.path))

    def do_POST(self):
        try:
            if self.path.endswith('/restaurants/new'):
                logging.debug("Headers: %s", self.headers['content-type'])
                ctype, pdict = cgi.parse_header(
                    self.headers['content-type'])

                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
                logging.debug('pdict: %s', pdict)
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    restaurant_name = fields.get('newRestaurantName')[0].decode('utf-8')
                db = self.__get_db()
                newRestaurant = Restaurant(name=restaurant_name)
                db.add(newRestaurant)
                db.commit()
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()
                return

        except:
            pass




    def __get_db(self):
        if self._db is None:
            engine = create_engine('sqlite:///restaurantmenu.db')
            Base.metadata.bind = engine
            DBSession = sessionmaker(bind=engine)
            self._db = DBSession()
        return self._db






def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webserverHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("Stopping web server...")
        server.socket.close()

if __name__ == '__main__':
    main()
