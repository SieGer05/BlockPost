from node.server import app
import argparse

if __name__ == '__main__':
   parser = argparse.ArgumentParser()
   parser.add_argument('-p', '--port', default=8000, type=int, help='Port to listen on')
   args = parser.parse_args()
   
   app.run(debug=True, port=args.port)
