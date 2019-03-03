
# bofhbot api server daemon 

# flask main executable
# run as (with python3 in venv): 
# python botd.py 


from flask import Flask
from flask_restful import Resource, Api
import os

app = Flask(__name__)
api = Api(app)

class botD(Resource):
    def get(self):
        return {'bot': 'bofh'}

api.add_resource(botD, '/')

if __name__ == '__main__':
    #app.run(debug=True)
    port = int(os.environ.get('PORT', 5000))
    #app.run(port=port)                         # this is default, localhost only
    app.run(host='0.0.0.0', port=port, debug=True)          # i have iptables limiting exposure

# vim:shiftwidth=2 tabstop=4 formatoptions-=cro list nu expandtab filetype=python
