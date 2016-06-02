from functools import wraps

from flask import flash, redirect, url_for, request, session
#g

def requires_login(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    print "LOGIN CHECK"
    if request.path == '/upload/md/':
      return f(*args, **kwargs)
    if session['user'] is None:
      flash(u'You need to be signed in for this page.')
      return redirect(url_for('users.login', next=request.path))
    return f(*args, **kwargs)
  return decorated_function

def logout_user():
    '''
    Logs a user out. (You do not need to pass the actual user.) This will
    also clean up the remember me cookie if it exists.
    '''
    print "LOGOUT CHECK"
    #print session.keys()
    try:
      #if 'user_id' in session:
      # user = User.query.get(session['user_id'])
      # user.current_user = False
      # user.save()
      print "Logged out: %s | %s" % (session.pop('user_id'), 
                                     session.pop('user'))
      return True
    except:
      return False
