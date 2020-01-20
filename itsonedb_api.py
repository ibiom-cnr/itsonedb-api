import itsonedb_read
from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

class ReadITSoneDB(Resource):
    def get(self, action, name):
        return itsonedb_read.itsonedb_read(action, name)

api.add_resource(ReadITSoneDB, '/api/<action>/<name>')

if __name__ == '__main__':
     app.run(host='0.0.0.0')
