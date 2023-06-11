import sys
from dotenv import load_dotenv

'''
PROBABLY WONT BE NEEDED. USING APSCHEDULER INSTEAD
'''

load_dotenv()

def example():
    print("Successfully logged in", file=sys.stderr)
