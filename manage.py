#!/usr/bin/env python
import os
from app import create_app, db
from app.models import User, Role, Permission, Post,Regular
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from flask import send_from_directory
import schedule
import time
import datetime
import send_mail
#from threading import Thread

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Permission=Permission,
                Post=Post)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
	
	
#@app.route('/')
#def root():
#    return app.send_static_file('index.html')


start_time = time.time()

def run_every_day():
    #print("Running periodic task!")
    with app.app_context():
        tasks = Regular.query.all()
        for task in tasks:
            seconds_passed = datetime.timedelta.total_seconds(datetime.datetime.utcnow()-task.timestamp)
            frequency = task.frequency
            seconds_required = 86400 * frequency
            if(seconds_required < seconds_passed):
                post = task.postID
                if send_mail.get_pages_send_email(post,task):
                    task.timestamp = datetime.datetime.utcnow()
                    db.session.commit()
                print('Something happend')

    print ("Elapsed time: " + str(time.time() - start_time))

def run_schedule():
    while 1:
        schedule.run_pending()
        time.sleep(1)

# continue with the rest of your code

@app.route('/uploads/<filename>') #working
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                             filename)

							 
							 
@manager.command
def profile(length=25, profile_dir=None):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                      profile_dir=profile_dir)
    app.run()


@manager.command
def deploy():
    """Run deployment tasks."""
    from flask_migrate import upgrade
    from app.models import Role, User

    # migrate database to latest revision
    upgrade()
	

if __name__ == '__main__':

    #schedule.every(86400).seconds.do(run_every_day)
    #t = Thread(target=run_schedule)
    #t.start()
    #print ("Start time: " + str(start_time))
    #app.run()
    manager.run()