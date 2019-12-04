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
                output = ""
                output += "<html><body>"
                output += "<h1>Make a New Restaurant</h1>"
                output += "<form method = 'POST' enctype='multipart/form-data' action = '/restaurants/new'>"
                output += "<input name = 'newRestaurantName' type = 'text' placeholder = 'New Restaurant Name' > "
                output += "<input type='submit' value='Create'>"
                output += "</form></body></html>"

            if self.path.endswith('/hello'):
                output = ""
                output += "<html><body>"
                output += "<h1>Hello !</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
                output += "</body></html>"

            if self.path.endswith('/restaurants'):
                db = self.__get_db()
                restaurant_items = db.query(Restaurant).all()
                output = "<html><body>"
                output += "<a href = '/restaurants/new' > Make a New Restaurant Here </a></br></br>"
                for item in restaurant_items:
                    output += '<p>{}</p>'.format(item.name)
                    output += "<a href ='/restaurants/{}/edit' >Edit </a> ".format(item.id)
                    output += "</br>"
                    output += "<a href ='/restaurants/{}/delete' >Delete </a> ".format(item.id)
                    output += "</br></br></br>"
                output += "</body></html>"

            if self.path.endswith('/edit'):
                restaurant_id = self.path.split("/")[2]
                db = self.__get_db()
                restaurant = db.query(Restaurant).filter_by(id=restaurant_id).one()
                if restaurant:
                    output = "<html><body>"
                    output += "<h1> {} </h1>".format(restaurant.name)
                    output += "<form method='POST' enctype='multipart/form-data' action = '/restaurants/{}/edit' >".format(restaurant.id)
                    output += "<input name = 'newRestaurantName' type='text' placeholder = '{}' >".format(restaurant.name)
                    output += "<input type = 'submit' value = 'Rename'>"
                    output += "</form>"
                    output += "</body></html>"

            if self.path.endswith('/delete'):
                restaurant_id = self.path.split("/")[2]
                db = self.__get_db()
                restaurant = db.query(Restaurant).filter_by(id=restaurant_id).one()
                output = ""
                output += "<html><body>"
                output += "<h1>Are you sure you want to delete {}?".format(restaurant.name)
                output += "<form method='POST' enctype = 'multipart/form-data' action = '/restaurants/{}/delete'>".format(restaurant.id)
                output += "<input type = 'submit' value = 'Delete'>"
                output += "</form>"
                output += "</body></html>"

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(output.encode('utf-8'))
            logging.debug("Send message: %s ", output.encode('utf-8'))

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



            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(
                    self.headers['content-type'])
                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")

                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    new_reataurant_name = fields.get('newRestaurantName')[0].decode('utf-8')
                    restaurantIDPath = self.path.split("/")[2]
                    db = self.__get_db()

                    myRestaurantQuery = db.query(Restaurant).filter_by(
                        id=restaurantIDPath).one()
                    if myRestaurantQuery != []:
                        myRestaurantQuery.name = new_reataurant_name
                        db.add(myRestaurantQuery)
                        db.commit()

            if self.path.endswith('/delete'):
                logging.debug("Path %s",self.path)
                restaurant_id = self.path.split("/")[2]
                db = self.__get_db()
                restaurant_to_delete = db.query(Restaurant).filter_by(id=restaurant_id).one()
                if restaurant_to_delete!=[]:
                    db.delete(restaurant_to_delete)
                    db.commit()
                    logging.debug("Restaurant record (id = %s, name = %s deleted) ",restaurant_to_delete.id, restaurant_to_delete.name )
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
