from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, abort
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from functools import wraps
import os
from datetime import datetime, timedelta
import logging
from logging.handlers import RotatingFileHandler
from itsdangerous import URLSafeTimedSerializer
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename
from bson.json_util import dumps
from flask_wtf.csrf import CSRFProtect
import uuid
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length
app = Flask(__name__)
csrf = CSRFProtect(app)

# Enhanced Configuration
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production',
    MONGO_URI=os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/',
    PERMANENT_SESSION_LIFETIME=timedelta(days=7),
    UPLOAD_FOLDER='static/uploads',
    PROFILE_IMAGES='static/uploads/profile',
    POST_IMAGES='static/uploads/posts',
    ALLOWED_EXTENSIONS={'png', 'jpg', 'jpeg', 'gif'},
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB
    MAIL_SERVER='smtp.example.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=os.environ.get('MAIL_USERNAME'),
    MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD'),
    POSTS_PER_PAGE=10,
    COMMENTS_PER_PAGE=5,
    CSRF_ENABLED=True
)
class EventForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('LGBTQ+', 'LGBTQ+'),
        ('Tech', 'Tech'),
        ('Art', 'Art'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    submit = SubmitField('Create Event')

# Database setup
# Database setup
client = MongoClient(app.config['MONGO_URI'])
db = client["social_media"]
users_collection = db["users"]
posts_collection = db["posts"]
comments_collection = db["comments"]
reports_collection = db["reports"]
moderation_collection = db["moderation"]
sessions_collection = db["sessions"]
notifications_collection = db["notifications"]
followers_collection = db["followers"]
likes_collection = db["likes"]  # Add this line
events_collection = db["events"]

# Rate limiting
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["500 per day", "100 per hour"]
)

# Email verification
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# Logging configuration
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)

@app.context_processor
def inject_user():
    if 'user_id' in session:
        current_user = users_collection.find_one({'_id': ObjectId(session['user_id'])})
        return {'current_user': current_user}
    return {'current_user': None}

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%b %d, %Y %I:%M %p'):
    if isinstance(value, datetime):
        return value.strftime(format)
    return value
    
# Helper functions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = users_collection.find_one({'_id': ObjectId(session['user_id'])})
        if not user or user.get('role') != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def save_file(file, folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    # Generate unique filename
    ext = filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(folder, filename)
    file.save(filepath)
    
    # Add basic image moderation
    try:
        # Here you would add actual image moderation logic
        # This could be an API call to a moderation service
        is_safe = moderate_image(filepath)
        if not is_safe:
            os.remove(filepath)
            return None
    except Exception as e:
        app.logger.error(f"Image moderation failed: {str(e)}")
        os.remove(filepath)
        return None
    
    return filename

        # Enhanced Upload Function with Moderation
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def create_notification(user_id, message, link=None):
    notification = {
        'user_id': ObjectId(user_id),
        'message': message,
        'link': link,
        'read': False,
        'created_at': datetime.utcnow()
    }
    notifications_collection.insert_one(notification)

# New Report System
def check_user_status(user_id):
    user = users_collection.find_one({'_id': ObjectId(user_id)})
    if user and user.get('status') == 'banned':
        return False
    return True

# Report threshold checker
def check_report_threshold(user_id):
    report_count = reports_collection.count_documents({
        'reported_user': ObjectId(user_id),
        'status': 'pending'
    })
    if report_count >= 30:
        # Ban user and mark all reports as resolved
        users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'status': 'banned'}}
        )
        reports_collection.update_many(
            {'reported_user': ObjectId(user_id)},
            {'$set': {'status': 'resolved'}}
        )
        return True
    return False


def moderate_image(filepath):
    # Implement actual moderation logic here
    # This could use AI models or external APIs
    return True  # Temporary implementation

def validate_category(category):
    valid_categories = ['lgbt', 'male', 'female', 'others']
    return category if category in valid_categories else None



# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('feed'))
    return render_template('index.html')

@app.route('/feed')
@login_required
def feed():
    page = request.args.get('page', 1, type=int)
    skip = (page - 1) * app.config['POSTS_PER_PAGE']
    
    # Get posts from users the current user follows
    following = followers_collection.find({'follower_id': ObjectId(session['user_id'])})
    following_ids = [f['following_id'] for f in following]
    following_ids.append(ObjectId(session['user_id']))  # Include own posts
    
    posts = posts_collection.find({'user_id': {'$in': following_ids}})\
                           .sort('created_at', -1)\
                           .skip(skip)\
                           .limit(app.config['POSTS_PER_PAGE'])
    
    posts = list(posts)
    
    # Add user and like info to each post
    for post in posts:
        post['user'] = users_collection.find_one({'_id': post['user_id']}, {'password': 0})
        post['like_count'] = likes_collection.count_documents({'post_id': post['_id']})
        post['is_liked'] = likes_collection.find_one({
            'post_id': post['_id'],
            'user_id': ObjectId(session['user_id'])
        }) is not None
        
        # Get first few comments
        post['comments'] = list(comments_collection.find({'post_id': post['_id']}))
        for comment in post['comments']:
            comment['user'] = users_collection.find_one({'_id': comment['user_id']}, {'username': 1, 'avatar': 1})
    
    return render_template('feed.html', posts=posts, page=page)  # Make sure this is properly indented inside the function
    # ... [previous imports and configuration remain the same]

# Add these new routes after your existing feed route
@app.route('/feed/lgbt')
@login_required
def lgbt_feed():
    page = request.args.get('page', 1, type=int)
    skip = (page - 1) * app.config['POSTS_PER_PAGE']
    
    lgbt_users = users_collection.find({
        'gender': {'$in': ['non-binary', 'transgender', 'genderqueer', 'other']}
    })
    lgbt_user_ids = [user['_id'] for user in lgbt_users]
    
    posts = posts_collection.find({'user_id': {'$in': lgbt_user_ids}})\
                           .sort('created_at', -1)\
                           .skip(skip)\
                           .limit(app.config['POSTS_PER_PAGE'])
    
    posts = list(posts)
    
    for post in posts:
        post['user'] = users_collection.find_one({'_id': post['user_id']}, {'password': 0})
        post['like_count'] = likes_collection.count_documents({'post_id': post['_id']})
        post['is_liked'] = likes_collection.find_one({
            'post_id': post['_id'],
            'user_id': ObjectId(session['user_id'])
        }) is not None
        
        post['comments'] = list(comments_collection.find({'post_id': post['_id']}))
        for comment in post['comments']:
            comment['user'] = users_collection.find_one({'_id': comment['user_id']}, {'username': 1, 'avatar': 1})
    
    return render_template('lgbt_feed.html', 
                     posts=posts, 
                     page=page,
                     posts_per_page=app.config['POSTS_PER_PAGE'])


#communities from lgbt feed 
@app.route('/communities/<category>')
@login_required
def communities(category):  # <-- Must include 'category' to avoid TypeError
    # You can later use the category to filter communities or posts
    
    popular_communities = [
        {'name': 'Tech Enthusiasts', 'members': 1250, 'icon': 'fas fa-laptop-code'},
        {'name': 'Art Lovers', 'members': 980, 'icon': 'fas fa-palette'},
        {'name': 'Music Fans', 'members': 2100, 'icon': 'fas fa-music'},
        {'name': 'Fitness Community', 'members': 750, 'icon': 'fas fa-dumbbell'}
    ]
    
    # Fetch actual user communities from the DB if needed
    user_communities = []

    return render_template('communities_lgbt.html',
                           category=category,
                           popular_communities=popular_communities,
                           user_communities=user_communities)


#events from lgbt feed 
# Make category optional with a default value
@app.route('/events/')
@app.route('/events/<category>')
@login_required
def events(category='lgbt'):
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of events per page
    
    # If using MongoDB for events (recommended):
    if db.events.count_documents({}) == 0:
        # Insert sample events if collection is empty
        sample_events = [
            {'title': 'Pride Parade', 'date': datetime(2023, 6, 25), 'location': 'City Center', 'category': 'LGBTQ+'},
            {'title': 'Tech Conference', 'date': datetime(2023, 7, 15), 'location': 'Convention Center', 'category': 'Tech'},
            {'title': 'Art Exhibition', 'date': datetime(2023, 8, 5), 'location': 'Modern Art Museum', 'category': 'Art'}
        ]
        db.events.insert_many(sample_events)
    
    # Build query based on category
    query = {}
    if category and category.lower() != 'all':
        query['category'] = {'$regex': f'^{category}$', '$options': 'i'}  # Case-insensitive exact match
    
    # Get total count for pagination
    total_events = db.events.count_documents(query)
    
    # Calculate total pages
    total_pages = (total_events + per_page - 1) // per_page
    
    # Get paginated events
    events_list = list(db.events.find(query)
                         .sort('date', 1)  # Sort by date ascending
                         .skip((page - 1) * per_page)
                         .limit(per_page))
    
    # Get user's events (sample - replace with actual query)
    user_events = list(db.events.find({
        'attendees': ObjectId(session['user_id'])
    }))
    
    return render_template('events_lgbt.html',
                       events=events_list,
                       pagination={
                           'page': page,
                           'per_page': per_page,
                           'total': total_events,
                           'pages': total_pages,
                           'has_prev': page > 1,
                           'has_next': page < total_pages,
                           'prev_num': page - 1,
                           'next_num': page + 1
                       },
                       user_events=user_events,
                       category=category,
                       filter_type=request.args.get('filter', 'upcoming'))



@app.route('/events/create', methods=['GET', 'POST'])
@login_required
def create_event():
    if request.method == 'POST':
        # Process form data
        title = request.form.get('title')
        description = request.form.get('description')
        date = request.form.get('date')
        location = request.form.get('location')
        category = request.form.get('category')
        
        # Validate required fields
        if not all([title, description, date, location]):
            flash('Please fill in all required fields', 'error')
            return redirect(url_for('create_event'))
        
        # Create event document
        event = {
            'title': title,
            'description': description,
            'date': datetime.strptime(date, '%Y-%m-%d'),
            'location': location,
            'category': category,
            'organizer_id': ObjectId(session['user_id']),
            'attendees': [ObjectId(session['user_id'])],
            'created_at': datetime.utcnow()
        }
        
        # Insert into database (you'll need to create an events collection)
        db.events.insert_one(event)
        
        flash('Event created successfully!', 'success')
        return redirect(url_for('events', category=request.form.get('category', 'lgbt')))
    
    # GET request - show form
    return render_template('create_event.html')

@app.route('/feed/male')
@login_required
def male_feed():
    page = request.args.get('page', 1, type=int)
    skip = (page - 1) * app.config['POSTS_PER_PAGE']
    
    # Get all male users
    male_users = users_collection.find({'gender': 'male'})
    male_user_ids = [user['_id'] for user in male_users]
    
    # Get total count of posts for pagination
    total_posts = posts_collection.count_documents({'user_id': {'$in': male_user_ids}})
    
    # Calculate total pages needed
    total_pages = (total_posts + app.config['POSTS_PER_PAGE'] - 1) // app.config['POSTS_PER_PAGE']
    
    # Get paginated posts
    posts = posts_collection.find({'user_id': {'$in': male_user_ids}})\
                           .sort('created_at', -1)\
                           .skip(skip)\
                           .limit(app.config['POSTS_PER_PAGE'])
    
    posts = list(posts)
    
    # Add user and engagement data to each post
    for post in posts:
        post['user'] = users_collection.find_one({'_id': post['user_id']}, {'password': 0})
        post['like_count'] = likes_collection.count_documents({'post_id': post['_id']})
        post['is_liked'] = likes_collection.find_one({
            'post_id': post['_id'],
            'user_id': ObjectId(session['user_id'])
        }) is not None
        
        post['comments'] = list(comments_collection.find({'post_id': post['_id']}))
        for comment in post['comments']:
            comment['user'] = users_collection.find_one({'_id': comment['user_id']}, {'username': 1, 'avatar': 1})
    
    return render_template('male_feed.html',
                         posts=posts,
                         page=page,
                         total_pages=total_pages,
                         ObjectId=ObjectId)

@app.route('/feed/female')
@login_required
def female_feed():
    page = request.args.get('page', 1, type=int)
    skip = (page - 1) * app.config['POSTS_PER_PAGE']
    
    # Get all female users
    female_users = users_collection.find({'gender': 'female'})
    female_user_ids = [user['_id'] for user in female_users]
    
    # Get total count of posts for pagination
    total_posts = posts_collection.count_documents({'user_id': {'$in': female_user_ids}})
    
    # Calculate total pages needed
    total_pages = (total_posts + app.config['POSTS_PER_PAGE'] - 1) // app.config['POSTS_PER_PAGE']
    
    # Get posts from last 7 days for "new posts today" count
    posts_this_week = posts_collection.count_documents({
        'user_id': {'$in': female_user_ids},
        'created_at': {'$gte': datetime.now() - timedelta(days=7)}
    })
    
    # Get paginated posts
    posts = posts_collection.find({'user_id': {'$in': female_user_ids}})\
                           .sort('created_at', -1)\
                           .skip(skip)\
                           .limit(app.config['POSTS_PER_PAGE'])
    
    posts = list(posts)
    
    # Add user and engagement data to each post
    for post in posts:
        post['user'] = users_collection.find_one({'_id': post['user_id']}, {'password': 0})
        post['like_count'] = likes_collection.count_documents({'post_id': post['_id']})
        post['is_liked'] = likes_collection.find_one({
            'post_id': post['_id'],
            'user_id': ObjectId(session['user_id'])
        }) is not None
        
        post['comments'] = list(comments_collection.find({'post_id': post['_id']}))
        for comment in post['comments']:
            comment['user'] = users_collection.find_one({'_id': comment['user_id']}, {'username': 1, 'avatar': 1})
    
    # Get female users count
    female_users_count = users_collection.count_documents({'gender': 'female'})
    
    # Get active female users (logged in today)
    active_female_users = sessions_collection.count_documents({
        'user_id': {'$in': female_user_ids},
        'login_time': {'$gte': datetime.now() - timedelta(days=1)}
    })
    
    return render_template('female_feed.html',
                         posts=posts,
                         page=page,
                         total_pages=total_pages,
                         female_users_count=female_users_count,
                         active_female_users=active_female_users,
                         posts_this_week=posts_this_week,
                         new_posts_today=posts_this_week)  # You might want a separate query for just today's posts

# ... [rest of your existing routes remain the same]


@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("10 per hour")
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        email = request.form.get('email', '').strip()
        gender = request.form.get('gender', 'other')
        pronouns = request.form.get('pronouns', '').strip()
        
        # Basic validation
        if not username or not password:
            flash('Username and password are required.', 'error')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return redirect(url_for('register'))
        
        if email:
            email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
            if not re.match(email_regex, email):
                flash('Invalid email address.', 'error')
                return redirect(url_for('register'))
        
        # Check if username or email already exists
        if users_collection.find_one({'username': username}):
            flash('Username already exists.', 'error')
            return redirect(url_for('register'))
        
        if email and users_collection.find_one({'email': email}):
            flash('Email already registered.', 'error')
            return redirect(url_for('register'))
        
        # Hash the password
        hashed_pw = generate_password_hash(password)
        
        # Create user data
        user_data = {
            'username': username,
            'password': hashed_pw,
            'email': email,
            'role': 'user',
            'verified': False,
            'bio': '',
            'avatar': 'default.png',
            'gender': gender,
            'pronouns': pronouns,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Save user first
        users_collection.insert_one(user_data)

        # Prepare email verification
        if email:
            token = serializer.dumps(email, salt='email-confirm')
            verification_url = url_for('confirm_email', token=token, _external=True)
            
            # Send the verification email
            try:
                send_verification_email(email, verification_url)
            except Exception as e:
                app.logger.error(f"Failed to send verification email: {str(e)}")
                flash('Error sending verification email. Please contact support.', 'error')
                return redirect(url_for('login'))
        
        # Logging with IP address
        ip = request.remote_addr
        app.logger.info(f'New user registered: {username} from IP {ip}')
        
        flash('Registration successful! Please check your email to verify your account.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=3600)
    except:
        flash('The confirmation link is invalid or has expired.', 'error')
        return redirect(url_for('login'))
    
    user = users_collection.find_one({'email': email})
    if user and not user['verified']:
        users_collection.update_one(
            {'email': email},
            {'$set': {'verified': True}}
        )
        flash('Email successfully verified! You can now log in.', 'success')
    else:
        flash('Account already verified.', 'info')
    
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = users_collection.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            session.permanent = True
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            session['role'] = user.get('role', 'user')
            session['gender'] = user.get('gender', 'other')  # Store gender in session
            
            # Store session in DB
            sessions_collection.insert_one({
                'user_id': user['_id'],
                'ip': request.remote_addr,
                'user_agent': request.headers.get('User-Agent'),
                'login_time': datetime.utcnow()
            })
            
            flash('Login successful!', 'success')
            
            # Redirect based on gender
            gender = user.get('gender', 'other')
            if gender == 'male':
                return redirect(url_for('male_feed'))
            elif gender == 'female':
                return redirect(url_for('female_feed'))
            elif gender == 'lgbt':
                return redirect(url_for('lgbt_feed'))
            else:
                return redirect(url_for('feed'))  # Default feed for 'other' or unspecified
            
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    sessions_collection.update_one(
        {'user_id': ObjectId(session['user_id'])},
        {'$set': {'logout_time': datetime.utcnow()}}
    )
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Enhanced Profile Route with Privacy Settings
@app.route('/profile/<username>')
@login_required
def user_profile(username):
    viewer_id = ObjectId(session['user_id'])

    # Fetch user while excluding sensitive fields
    user = users_collection.find_one({'username': username}, {
        'password': 0,
        'email': 0,
        'verification_token': 0
    })

    if not user or user.get('status') == 'banned':
        app.logger.warning(f'Profile access denied for username="{username}" (not found or banned)')
        abort(404)

    # Check if viewer is blocked by the user
    if moderation_collection.find_one({
        'user_id': user['_id'],
        'blocked_user': viewer_id,
        'type': 'block'
    }):
        app.logger.info(f'Access denied: user {viewer_id} is blocked by {user["_id"]}')
        abort(403)

    # Privacy check for private accounts
    if user.get('private_account') and user['_id'] != viewer_id:
        is_following = followers_collection.find_one({
            'follower_id': viewer_id,
            'following_id': user['_id']
        })
        if not is_following:
            return render_template('private_profile.html', user=user)

    # Check if viewer is following the user
    is_following = followers_collection.find_one({
        'follower_id': viewer_id,
        'following_id': user['_id']
    }) is not None

    # Fetch user's latest posts (limit 10)
    posts = list(posts_collection.find({'user_id': user['_id']}).sort('created_at', -1).limit(10))
    post_ids = [post['_id'] for post in posts]

    # Bulk fetch like data to avoid N+1 queries
    liked_post_ids = set(
        like['post_id'] for like in likes_collection.find({
            'post_id': {'$in': post_ids},
            'user_id': viewer_id
        })
    )

    like_counts = {
        like['_id']: likes_collection.count_documents({'post_id': like['_id']})
        for like in posts
    }

    for post in posts:
        post['like_count'] = like_counts.get(post['_id'], 0)
        post['is_liked'] = post['_id'] in liked_post_ids

    # Fetch follower/following counts
    follower_count = followers_collection.count_documents({'following_id': user['_id']})
    following_count = followers_collection.count_documents({'follower_id': user['_id']})

    return render_template('profile.html',
                           user=user,
                           posts=posts,
                           is_following=is_following,
                           follower_count=follower_count,
                           following_count=following_count)


# Admin Moderation Routes
@app.route('/admin/moderation')
@admin_required
def admin_moderation():
    pending_reports = list(reports_collection.find({'status': 'pending'}))
    return render_template('admin/moderation.html', reports=pending_reports)


@app.route('/admin/action/report', methods=['POST'])
@admin_required
def handle_report():
    report_id = request.form.get('report_id')
    action = request.form.get('action')
    
    report = reports_collection.find_one({'_id': ObjectId(report_id)})
    if not report:
        abort(404)
    
    if action == 'dismiss':
        reports_collection.update_one(
            {'_id': ObjectId(report_id)},
            {'$set': {'status': 'dismissed'}}
        )
    elif action == 'ban':
        users_collection.update_one(
            {'_id': report['reported_user']},
            {'$set': {'status': 'banned'}}
        )
        reports_collection.update_one(
            {'_id': ObjectId(report_id)},
            {'$set': {'status': 'resolved'}}
        )
    
    flash('Action processed successfully', 'success')
    return redirect(url_for('admin_moderation'))

# Error Handlers
@app.errorhandler(413)
def request_entity_too_large(error):
    flash('File size exceeds maximum allowed limit (16MB)', 'error')
    return redirect(request.referrer or url_for('feed'))


@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = users_collection.find_one({'_id': ObjectId(session['user_id'])})
    
    if request.method == 'POST':
        update_data = {}
        
        if 'email' in request.form and request.form['email'] != user.get('email'):
            update_data['email'] = request.form['email']
            update_data['verified'] = False
        
        if 'bio' in request.form:
            update_data['bio'] = request.form['bio']
        
        if 'name' in request.form:
            update_data['name'] = request.form['name']
        
        if 'location' in request.form:
            update_data['location'] = request.form['location']
        
        if 'website' in request.form:
            update_data['website'] = request.form['website']
        
        if update_data:
            update_data['updated_at'] = datetime.utcnow()
            users_collection.update_one(
                {'_id': ObjectId(session['user_id'])},
                {'$set': update_data}
            )
            flash('Profile updated successfully!', 'success')
        
        return redirect(url_for('edit_profile'))
    
    return render_template('edit_profile.html', user=user)

@app.route('/upload_avatar', methods=['POST'])
@login_required
def upload_avatar():
    if 'avatar' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('edit_profile'))
    
    file = request.files['avatar']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('edit_profile'))
    
    if file and allowed_file(file.filename):
        # Get current user data
        user = users_collection.find_one({'_id': ObjectId(session['user_id'])})
        
        # Delete old avatar if it exists and isn't default
        if user.get('avatar') and user['avatar'] != 'default.png':
            try:
                old_filepath = os.path.join(app.config['PROFILE_IMAGES'], user['avatar'])
                if os.path.exists(old_filepath):
                    os.remove(old_filepath)
            except Exception as e:
                app.logger.error(f"Error deleting old avatar: {str(e)}")
        
        # Save new avatar
        filename = save_file(file, app.config['PROFILE_IMAGES'])
        
        # Update database
        result = users_collection.update_one(
            {'_id': ObjectId(session['user_id'])},
            {'$set': {
                'avatar': filename,
                'updated_at': datetime.utcnow()
            }}
        )
        
        if result.modified_count > 0:
            flash('Profile picture updated successfully!', 'success')
            # Clear session to force refresh (optional)
            session.modified = True
        else:
            flash('Failed to update profile picture', 'error')
    else:
        flash('Allowed file types are: png, jpg, jpeg, gif', 'error')
    
    return redirect(url_for('edit_profile'))

# Post routes
@app.route('/post/create', methods=['POST'])
@login_required
def create_post():
    content = request.form.get('content', '').strip()
    if not content:
        flash('Post content cannot be empty', 'error')
        return redirect(url_for('feed'))
    
    post_data = {
        'user_id': ObjectId(session['user_id']),
        'content': content,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    
    # Handle image upload if present
    if 'image' in request.files:
        file = request.files['image']
        if file.filename != '' and allowed_file(file.filename):
            filename = save_file(file, app.config['POST_IMAGES'])
            post_data['image'] = filename
    
    posts_collection.insert_one(post_data)
    flash('Post created successfully!', 'success')
    return redirect(url_for('feed'))
@app.route('/post/<post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    try:
        post = posts_collection.find_one({'_id': ObjectId(post_id)})
        
        if not post:
            flash('Post not found', 'error')
            return redirect(url_for('feed'))
        
        # Check if current user is the post owner or admin
        if str(post['user_id']) != session['user_id'] and session.get('role') != 'admin':
            flash('You are not authorized to delete this post', 'error')
            return redirect(url_for('feed'))
        
        # Delete associated comments
        comments_collection.delete_many({'post_id': ObjectId(post_id)})
        
        # Delete associated likes
        likes_collection.delete_many({'post_id': ObjectId(post_id)})
        
        # Delete associated notifications that reference this post
        notifications_collection.delete_many({'link': {'$regex': f'/post/{post_id}'}})
        
        # Delete post image if exists
        if post.get('image'):
            try:
                image_path = os.path.join(app.config['POST_IMAGES'], post['image'])
                if os.path.exists(image_path):
                    os.remove(image_path)
            except Exception as e:
                app.logger.error(f"Error deleting post image: {str(e)}")
                flash('Error deleting post image', 'error')
        
        # Delete the post
        result = posts_collection.delete_one({'_id': ObjectId(post_id)})
        
        if result.deleted_count > 0:
            flash('Post deleted successfully', 'success')
        else:
            flash('Failed to delete post', 'error')
            
    except Exception as e:
        app.logger.error(f"Error deleting post: {str(e)}")
        flash('An error occurred while deleting the post', 'error')
    
    return redirect(url_for('feed'))

# Comment routes
@app.route('/post/<post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    content = request.form.get('content', '').strip()
    if not content:
        flash('Comment cannot be empty', 'error')
        return redirect(url_for('feed'))
    
    post = posts_collection.find_one({'_id': ObjectId(post_id)})
    if not post:
        abort(404)
    
    comment_data = {
        'post_id': ObjectId(post_id),
        'user_id': ObjectId(session['user_id']),
        'content': content,
        'created_at': datetime.utcnow()
    }
    
    comments_collection.insert_one(comment_data)
    
    # Create notification for post owner if not commenting on own post
    if str(post['user_id']) != session['user_id']:
        post_owner = users_collection.find_one({'_id': post['user_id']})
        message = f"{session['username']} commented on your post"
        link = url_for('user_profile', username=session['username'])
        create_notification(post['user_id'], message, link)
    
    flash('Comment added successfully!', 'success')
    return redirect(url_for('feed'))

# Like routes
@app.route('/post/<post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    post = posts_collection.find_one({'_id': ObjectId(post_id)})
    if not post:
        abort(404)
    
    existing_like = likes_collection.find_one({
        'post_id': ObjectId(post_id),
        'user_id': ObjectId(session['user_id'])
    })
    
    if existing_like:
        likes_collection.delete_one({'_id': existing_like['_id']})
        liked = False
    else:
        like_data = {
            'post_id': ObjectId(post_id),
            'user_id': ObjectId(session['user_id']),
            'created_at': datetime.utcnow()
        }
        likes_collection.insert_one(like_data)
        liked = True
        
        # Create notification for post owner if not liking own post
        if str(post['user_id']) != session['user_id']:
            post_owner = users_collection.find_one({'_id': post['user_id']})
            message = f"{session['username']} liked your post"
            link = url_for('user_profile', username=session['username'])
            create_notification(post['user_id'], message, link)
    
    like_count = likes_collection.count_documents({'post_id': ObjectId(post_id)})
    return jsonify({'liked': liked, 'like_count': like_count})

# Follow routes
@app.route('/user/<user_id>/follow', methods=['POST'])
@login_required
def follow_user(user_id):
    if user_id == session['user_id']:
        return jsonify({'error': 'You cannot follow yourself'}), 400
    
    user_to_follow = users_collection.find_one({'_id': ObjectId(user_id)})
    if not user_to_follow:
        return jsonify({'error': 'User not found'}), 404
    
    existing_follow = followers_collection.find_one({
        'follower_id': ObjectId(session['user_id']),
        'following_id': ObjectId(user_id)
    })
    
    if existing_follow:
        followers_collection.delete_one({'_id': existing_follow['_id']})
        is_following = False
    else:
        follow_data = {
            'follower_id': ObjectId(session['user_id']),
            'following_id': ObjectId(user_id),
            'created_at': datetime.utcnow()
        }
        followers_collection.insert_one(follow_data)
        is_following = True
        
        # Create notification for the user being followed
        message = f"{session['username']} started following you"
        link = url_for('user_profile', username=session['username'])
        create_notification(user_id, message, link)
    
    follower_count = followers_collection.count_documents({'following_id': ObjectId(user_id)})
    return jsonify({
        'is_following': is_following,
        'follower_count': follower_count
    })

# Notifications
@app.route('/notifications')
@login_required
def notifications():
    # Mark all notifications as read
    notifications_collection.update_many(
        {'user_id': ObjectId(session['user_id']), 'read': False},
        {'$set': {'read': True}}
    )
    
    user_notifications = list(notifications_collection.find(
        {'user_id': ObjectId(session['user_id'])}
    ).sort('created_at', -1).limit(20))
    
    return render_template('notifications.html', notifications=user_notifications)

# Search
@app.route('/search')
@login_required
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return render_template('search.html', results=[], query=query)
    
    # Search users by username or name
    users = list(users_collection.find({
        '$or': [
            {'username': {'$regex': query, '$options': 'i'}},
            {'name': {'$regex': query, '$options': 'i'}}
        ]
    }, {'password': 0}).limit(20))
    
    # Search posts by content
    posts = list(posts_collection.find({
        'content': {'$regex': query, '$options': 'i'}
    }).sort('created_at', -1).limit(10))
    
    # Add user info to posts
    for post in posts:
        post['user'] = users_collection.find_one({'_id': post['user_id']}, {'username': 1, 'avatar': 1})
    
    return render_template('search.html', users=users, posts=posts, query=query)

# API endpoints
@app.route('/api/posts')
@login_required
def api_posts():
    page = request.args.get('page', 1, type=int)
    skip = (page - 1) * app.config['POSTS_PER_PAGE']
    
    posts = posts_collection.find().sort('created_at', -1).skip(skip).limit(app.config['POSTS_PER_PAGE'])
    posts = list(posts)
    
    for post in posts:
        post['user'] = users_collection.find_one({'_id': post['user_id']}, {'password': 0})
        post['like_count'] = likes_collection.count_documents({'post_id': post['_id']})
        post['comment_count'] = comments_collection.count_documents({'post_id': post['_id']})
    
    return jsonify(posts)

# Admin routes
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    stats = {
        'users': users_collection.count_documents({}),
        'posts': posts_collection.count_documents({}),
        'comments': comments_collection.count_documents({}),
        'active_sessions': sessions_collection.count_documents({'logout_time': {'$exists': False}})
    }
    return render_template('admin/dashboard.html', stats=stats)

@app.route('/admin/users')
@admin_required
def admin_users():
    users = list(users_collection.find({}, {'password': 0}).sort('created_at', -1))
    return render_template('admin/users.html', users=users)


# New Report Route
@app.route('/report/<content_type>/<content_id>', methods=['POST'])
@login_required
def report_content(content_type, content_id):
    valid_types = ['user', 'post', 'comment']
    if content_type not in valid_types:
        abort(400)
    
    reason = request.form.get('reason', '').strip()
    if not reason:
        flash('Please provide a reason for reporting', 'error')
        return redirect(request.referrer)
    
    report_data = {
        'reporter_id': ObjectId(session['user_id']),
        'content_type': content_type,
        'content_id': ObjectId(content_id),
        'reason': reason,
        'status': 'pending',
        'created_at': datetime.utcnow()
    }
    
    # Prevent duplicate reports
    existing_report = reports_collection.find_one({
        'reporter_id': ObjectId(session['user_id']),
        'content_type': content_type,
        'content_id': ObjectId(content_id)
    })
    
    if not existing_report:
        reports_collection.insert_one(report_data)
        flash('Thank you for your report. We will review it shortly.', 'success')
        
        # Check if user should be banned
        if content_type == 'user':
            check_report_threshold(ObjectId(content_id))
    else:
        flash('You have already reported this content', 'warning')
    
    return redirect(request.referrer)





# Error handlers
@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500


app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'a-strong-secret-key'

if __name__ == '__main__':
    # Create upload directories
    for folder in [app.config['UPLOAD_FOLDER'], 
                   app.config['PROFILE_IMAGES'], 
                   app.config['POST_IMAGES']]:
        os.makedirs(folder, exist_ok=True)
    
    app.run(host='0.0.0.0', port=5001, debug=True)