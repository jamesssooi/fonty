'''
    send_telemetry.py
    ~~~~~~~~~~~~~~~~~
    An independent Python module to send telemetry requests.
'''
import sys
import requests

def main():
    '''The entry function.'''
    # Get request body from stdin instead of command line arguments to prevent
    # JSON character conflicts
    d = sys.stdin.read()

    # Get telemetry endpoint url from arguments
    url = sys.argv[1]

    # Send the request
    requests.post(url=url,
                  data=d.encode('utf8'),
                  headers={'Content-Type': 'application/json'})

if __name__ == '__main__':
    main()
