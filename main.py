import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.app import App

if __name__ == "__main__":
    app = App()
    app.run()
