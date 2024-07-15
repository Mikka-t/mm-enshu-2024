from flask import Flask
from index import display_knowledge_graph

app = Flask(__name__)

@app.route('/')
def index():
    return display_knowledge_graph()
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
