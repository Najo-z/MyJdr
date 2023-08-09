#!/usr/bin/env python3

from my_jdr import create_app

app = create_app()
port = 5000


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port, debug=True)
