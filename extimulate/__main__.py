from . import endpoint


if __name__ == "__main__":
    endpoint.app.run(host='localhost', port=8080, debug=True)

