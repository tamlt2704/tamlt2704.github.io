import sys
from flask import Flask, render_template
from flask_flatpages import FlatPages, pygments_style_defs
from flask_frozen import Freezer

DEBUG = True
FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = '.md'
FLATPAGES_ROOT = 'content'
POST_DIR = 'posts'

app = Flask(__name__, static_url_path='/static')

flatpages = FlatPages(app)
freezer = Freezer(app)
app.config.from_object(__name__)



@app.route("/index")
@app.route("/")
def index():
	posts = [p for p in flatpages if p.path.startswith(POST_DIR)]
	posts.sort(key=lambda x: x['date'], reverse=False)
	return render_template('index.html', posts=posts)

@app.route("/posts/")
def posts():
	posts = [p for p in flatpages if p.path.startswith(POST_DIR)]
	posts.sort(key=lambda x: x['date'], reverse=False)
	return render_template('posts.html', posts=posts)

@app.route("/projects/")
def projects():
	return render_template('projects.html')

@app.route("/photos/")
def photos():
	posts = [p for p in flatpages if p.path.startswith(POST_DIR)]
	posts.sort(key=lambda x: x['date'], reverse=False)
	return render_template('posts.html', posts=posts)

@app.route("/about/")
def about():
	posts = [p for p in flatpages if p.path.startswith(POST_DIR)]
	posts.sort(key=lambda x: x['date'], reverse=False)
	return render_template('posts.html', posts=posts)

@app.route('/posts/<name>/')
def post(name):
	path = '{}/{}'.format(POST_DIR, name)
	post = flatpages.get_or_404(path)
	return render_template('post.html', post=post)


@app.route("/hanoibus")
def hanoibus():
	return render_template('hanoibus.html')



if __name__ == "__main__":
	if len(sys.argv) > 1 and sys.argv[1] == "build":
		freezer.freeze()
	else:
		app.run(host='0.0.0.0', debug=True)
