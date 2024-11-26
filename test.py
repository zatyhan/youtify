from flask import Flask
from redis import Redis

app = Flask(__name__)
redis = Redis(host='localhost', port=6379)

@app.route('/')
def index():
    redis.incr('hits')  
    return 'Hello World! I have been seen {} times.'.format(redis.get('hits'))

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(debug=True)