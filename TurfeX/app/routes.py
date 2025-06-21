from app import app, db, csrf, session
from flask import render_template, redirect, url_for, flash, request, session, jsonify, abort
from werkzeug.utils import secure_filename
from app.models import User, Match, MatchParticipant, ChatMessage, TurfOwner, Turf, Booking, TurfPhoto
from app.forms import SignUpForm, SignInForm, MatchForm, TurfForm
from datetime import datetime
from sqlalchemy.orm import joinedload
from app.email_setup import send_email
from functools import wraps
from flask import session
import base64

ALLOWED_EXTENSIONS = {'png','jpg','jpeg','gif'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

def get_current_turfOwner():
    if 'turfOwner_id' in session:
        return TurfOwner.query.get(session['turfOwner_id'])
    return None

@app.context_processor
def inject_current_accounts():
    return {
        'current_user': get_current_user(),
        'current_turfOwner': get_current_turfOwner()
    }


def login_required_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            print("Please log in to access this page!!!")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def login_required_turfOwner(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'turfOwner_id' not in session:
            print("Please log in to access this page!!!")
            return redirect(url_for('turf_login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/home')
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/portal')
def portal():
    return render_template('portal.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form=SignUpForm()
    if form.validate_on_submit():
        #send_email(form.email_address.data, "OTP VERIFICATION", "Your One Time Password is 123456!!!")
        with app.app_context():
            user_data=User(username=form.username.data,
                           email=form.email_address.data,
                           password=form.password.data)
            
            db.session.add(user_data)
            db.session.commit()
            session['user_id']=user_data.id
            
        return redirect(url_for('dashboard'))
    
    if form.errors!={}:
        for err_msg in form.errors.values():
            print(f"There was an error with creating a user : {err_msg}")

    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form=SignInForm()
    if form.validate_on_submit():
        attempted_user=User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            session['user_id']=attempted_user.id
            return redirect(url_for('dashboard'))
        
        else:
            print(f"Username and Password do not match !!! Please try again")

    return render_template('signin.html', form=form)

@app.route('/dashboard')
@login_required_user
def dashboard():
    return render_template('dashboard.html')

@app.route('/turf-register', methods=['GET', 'POST'])
def turf_register():
    form=SignUpForm()
    if form.validate_on_submit():
        #send_email(form.email_address.data, "OTP VERIFICATION", "Your One Time Password is 123456!!!")
        with app.app_context():
            turfOwner_data=TurfOwner(username=form.username.data,
                           email=form.email_address.data,
                           password=form.password.data)
            
            db.session.add(turfOwner_data)
            db.session.commit()
            session['turfOwner_id']=turfOwner_data.id
            
        return redirect(url_for('profile_setup'))
    
    if form.errors!={}:
        for err_msg in form.errors.values():
            print(f"There was an error with creating a user : {err_msg}")

    return render_template('turf_signup.html', form=form)

@app.route('/turf-login', methods=['GET', 'POST'])
def turf_login():
    form=SignInForm()
    if form.validate_on_submit():
        attempted_user=TurfOwner.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            session['turfOwner_id']=attempted_user.id
            return redirect(url_for('turf_dashboard'))
        
        else:
            print(f"Username and Password do not match !!! Please try again")

    return render_template('turf_signin.html', form=form)

@app.route('/turf-dashboard')
@login_required_turfOwner
def turf_dashboard():
    owner=get_current_turfOwner()
    turfs=Turf.query.filter_by(owner_id=owner.id).all()

    dashboard_data = []
    for turf in turfs:
        primary = TurfPhoto.query.filter_by(
            turf_id=turf.id,
            profile_pic=True
        ).first()

        additional = TurfPhoto.query.filter_by(
            turf_id=turf.id,
            profile_pic=False
        ).all()

        # build data URIs
        primary_uri = None
        if primary:
            b64 = base64.b64encode(primary.data).decode('utf-8')
            primary_uri = f"data:{primary.mimetype};base64,{b64}"

        additional_uris = []
        for p in additional:
            b64 = base64.b64encode(p.data).decode('utf-8')
            additional_uris.append(f"data:{p.mimetype};base64,{b64}")

        dashboard_data.append({
            'turf': turf,
            'primary_uri': primary_uri,
            'additional_uris': additional_uris
        })

    return render_template('turf_dashboard.html',
                           turfOwner_data=owner,
                           dashboard_data=dashboard_data)
@app.route('/create_match', methods=['GET','POST'])
@login_required_user
def create_match():
    form=MatchForm()
    if form.validate_on_submit():
        scheduled=datetime.combine(form.date.data, form.time.data)
        with app.app_context():
            match_data=Match(creator_id=get_current_user().id,
                            teamName=form.teamName.data,
                            gameType=form.gameType.data,
                            turfName=form.turfName.data,
                            location=form.location.data,
                            scheduledFor=scheduled,
                            maxPlayers=form.players.data,
                            skill=form.skill.data
                            )
            db.session.add(match_data)
            db.session.commit()

        return redirect(url_for('create_match'))

    if form.errors!={}:
        for err_msg in form.errors.values():
            print(f"There was an error with creating a user : {err_msg}")


    return render_template('create.html', form=form)


@app.route('/live')
@login_required_user
def live_match():
    with app.app_context():
        match_objs=(
            Match.query.options(joinedload(Match.participants)).filter(Match.scheduledFor >= datetime.utcnow()).all()
        )

        joined_ids={
            mp.matchId
            for mp in MatchParticipant.query.filter_by(userId=get_current_user().id).all()
        }

        match_data=[]
        for m in match_objs:
            match_data.append({
                'obj':m,
                'joined':m.id in joined_ids
            })

    return render_template('live.html', match_data=match_data)

@app.route('/join_match', methods=['POST'])
@login_required_user
@csrf.exempt
def join_match():
    match_id=request.form.get('match_id', type=int)
    role=request.form.get('role')

    if not match_id or not role:
        print("Invalid join request!!!\n")
        return redirect(url_for('live_match'))
    
    match=Match.query.get_or_404(match_id)

    if match.status != 'open' or len(match.participants) >= match.maxPlayers:
        flash("Sorry, that match is already full or closed.", "warning")
        return redirect(url_for('live_match'))

    # 2) Check if user already joined
    already=MatchParticipant.query.filter_by(
        matchId=match.id, userId=get_current_user().id
    ).first()
    if already:
        flash("You’ve already joined this match.", "info")
        return redirect(url_for('live_match'))

    # 3) Create the participation entry
    participation=MatchParticipant(
        matchId=match.id,
        userId=get_current_user().id,
        role=role        # or whatever default you like
    )
    db.session.add(participation)

    # Optionally update match.status to “full” if it’s now at capacity
    if len(match.participants)+1>=match.maxPlayers:
        match.status='full'

    db.session.commit()
    flash(f"Joined match “{match.teamName}”!", "success")
    return redirect(url_for('live_match'))

@app.route('/match_room/<int:match_id>')
@login_required_user
def match_room(match_id):
   
    match = Match.query.get_or_404(match_id)

    # block access to anyone who hasn't joined
    is_participant = MatchParticipant.query.filter_by(
        matchId=match.id,
        userId=get_current_user().id
    ).first() is not None

    if not is_participant:
        print("You must join this match before viewing the room.")
        return redirect(url_for('live_match'))

    participants = MatchParticipant.query.filter_by(
        matchId=match.id
    ).order_by(MatchParticipant.id).all()

    return render_template(
        'match.html',
        match=match,
        participants=participants
    )

@app.route('/api/matches/<int:match_id>/messages', methods=['GET'])
@login_required_user
@csrf.exempt
def get_messages(match_id):
    if not MatchParticipant.query.filter_by(
        matchId=match_id,
        userId=get_current_user().id
    ).first():
        return jsonify({'error': 'Forbidden'}), 403
    
    msgs=(ChatMessage.query.filter_by(match_id=match_id).order_by(ChatMessage.timestamp.asc()).all())

    return jsonify([{
        'username': m.user.username,
        'text': m.text,
        'timestamp': m.timestamp.isoformat()
    } for m in msgs])

@app.route('/api/matches/<int:match_id>/messages', methods=['POST'])
@login_required_user
@csrf.exempt
def post_message(match_id):
    if not MatchParticipant.query.filter_by(
        matchId=match_id,
        userId=get_current_user.id()).first():

        return jsonify({'error': 'Forbidden'}), 403
    
    data=request.get_json() or {}
    text=(data.get('text') or '').strip()

    if not text:
        return jsonify({'error':'Empty mesage'}), 400
    
    with app.app_context():
        msg=ChatMessage(match_id=match_id,
                        user_id=get_current_user().id,
                        text=text)
        
        db.session.add(msg)
        db.session.flush()

        ts=msg.timestamp
        db.session.commit()
    
    return jsonify({
        'username': get_current_user().username,
        'text': text,
        'timestamp': ts.isoformat()
    }), 201

@app.route('/stats')
@login_required_user
def stats():
    return render_template('stats.html')

@app.route('/set-turf-profile', methods=['GET', 'POST'])
def profile_setup():
    form=TurfForm()
    if form.validate_on_submit():
        turf = Turf(
            owner_id=get_current_turfOwner().id,          # or however you identify the owner
            owner_name=form.owner_name.data,
            name=form.turf_name.data,
            contact_no=form.contact_no.data,
            address=form.address.data,
            city=form.city.data,
            pincode=form.pincode.data,
            cricket_price=float(form.cricket_price.data),
            football_price=float(form.football_price.data),
            tennis_price=float(form.tennis_price.data),
            turf_type=form.turf_type.data,
            max_capacity=form.capacity.data or 0,
            opening_time=datetime.combine(datetime.today(), form.opening_time.data) if form.opening_time.data else None,
            closing_time=datetime.combine(datetime.today(), form.closing_time.data) if form.closing_time.data else None,
            facilities=','.join(form.facilities.data),
            description=form.description.data,
            status='open'
        )
        db.session.add(turf)
        db.session.flush()  # so turf.id is available before commit
        
        main_file=form.main_image.data
        if main_file and allowed_file(main_file.filename):
            filename=secure_filename(main_file.filename)
            photo=TurfPhoto(
                turf_id=turf.id,
                filename=filename,
                data=main_file.read(),
                mimetype=main_file.mimetype,
                uploaded_at=datetime.utcnow(),
                profile_pic=True
            )
            db.session.add(photo)

        for img in form.additional_images.data:
            if img and allowed_file(img.filename):
                filename = secure_filename(img.filename)
                photo=TurfPhoto(
                    turf_id=turf.id,
                    filename=filename,
                    data=img.read(),
                    mimetype=img.mimetype,
                    uploaded_at=datetime.utcnow()
                )
                db.session.add(photo)

        db.session.commit()

        flash('Turf registered successfully!', 'success')
        return redirect(url_for('turf_dashboard'))

    return render_template('turfDoc.html', form=form)

@app.route('/api/turf/<int:turf_id>/price', methods=['POST'])
@login_required_turfOwner
@csrf.exempt
def update_turf_price(turf_id):
    owner = get_current_turfOwner()
    turf = Turf.query.filter_by(id=turf_id, owner_id=owner.id).first_or_404()

    data = request.get_json() or {}
    field = data.get('field')
    value = data.get('value')

    # whitelist your float fields
    valid_fields = {'cricket_price','football_price','tennis_price'}
    if field not in valid_fields:
        abort(400, 'Invalid price field')

    try:
        # allow strings like "1500.50" or numbers
        new_price = float(value)
    except (TypeError, ValueError):
        abort(400, 'Invalid value for price')

    setattr(turf, field, new_price)
    db.session.commit()

    return jsonify({ 'success': True, 'new': getattr(turf, field) })


@app.route('/logout')
@login_required_user
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/turf-logout')
@login_required_turfOwner
def turf_logout():
    session.pop('turfOwner_id', None)
    return redirect(url_for('home'))