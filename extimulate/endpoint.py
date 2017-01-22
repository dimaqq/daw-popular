import bottle

app = bottle.Bottle()


@app.route("/api/recent_purchases/<username>")
def recent_purchases(username):
    return "boobarbaz"
