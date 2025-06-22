from app import app, db, csrf, session
from flask import render_template, redirect, url_for, flash, request, session, jsonify, abort, Response
from werkzeug.utils import secure_filename
from app.models import User, Match, MatchParticipant, ChatMessage, TurfOwner, Turf, Booking, TurfPhoto, BattingRecord, BowlingRecord, Team
from app.forms import SignUpForm, SignInForm, MatchForm, TurfForm
from datetime import datetime, date, timedelta, time
from datetime import timezone as dt_timezone
from sqlalchemy.orm import joinedload
from app.email_setup import send_email
from functools import wraps
from flask import session
from app.turf_map import render_turf_map
import base64
import pytz
import random
from sqlalchemy.exc import IntegrityError
from collections import defaultdict
from app.mvp_prediction import get_mvp
import warnings
from dotenv import load_dotenv
load_dotenv()

from pydantic.json_schema import PydanticJsonSchemaWarning
warnings.filterwarnings("ignore", category=PydanticJsonSchemaWarning)
IST = pytz.timezone('Asia/Kolkata')

def to_ist(dt_utc: datetime) -> datetime:
    # if naive, explicitly mark UTC
    if dt_utc.tzinfo is None:
        dt_utc = dt_utc.replace(tzinfo=dt_timezone.utc)
    return dt_utc.astimezone(IST)

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

def get_scorecard_string(match_id):
    # Fetch all batting and bowling records for this match
    bats = BattingRecord.query.filter_by(match_id=match_id).all()
    bowls = BowlingRecord.query.filter_by(match_id=match_id).all()

    # Group batting & bowling by team_id
    batting_by_team = defaultdict(list)
    for br in bats:
        batting_by_team[br.team_id].append(br)

    bowling_by_team = defaultdict(list)
    for br in bowls:
        bowling_by_team[br.team_id].append(br)

    lines = []

    # Iterate over each team that has either batting or bowling records
    team_ids = set(batting_by_team) | set(bowling_by_team)
    for team_id in team_ids:
        team = Team.query.get(team_id)
        bat_list = batting_by_team.get(team_id, [])
        bowl_list = bowling_by_team.get(team_id, [])

        # Calculate total runs and wickets from batting records
        total_runs = sum(br.runs for br in bat_list)
        total_wickets = sum(1 for br in bat_list if br.is_out)
        total_balls = sum(br.balls for br in bat_list)
        overs_full = total_balls // 6
        overs_rem  = total_balls % 6

        # Header
        lines.append(f"{team.name}: {total_runs}/{total_wickets} ({overs_full}.{overs_rem} overs)")
        lines.append("Batting History :")

        # Player list
        if bat_list:
            player_names = [br.player.username for br in bat_list]
            lines.append("Players : " + ", ".join(player_names))
        else:
            lines.append("Players : (none)")

        # Detailed batting lines
        for idx, br in enumerate(bat_list, start=1):
            status = br.desc or ("out" if br.is_out else "not out")
            lines.append(
                f"{idx}) {br.player.username}: "
                f"{br.runs} runs off {br.balls} balls, "
                f"{br.fours} fours, {br.sixes} sixes, {status}"
            )

        lines.append("")  # blank line before bowling

        # Bowling section
        lines.append("Bowling History :")
        if bowl_list:
            for idx, br in enumerate(bowl_list, start=1):
                lines.append(
                    f"{idx}) {br.player.username}: "
                    f"{br.overs} overs, {br.runs} runs, {br.wickets} wicket"
                    + ("s" if br.wickets != 1 else "")
                )
        else:
            lines.append("(no bowling records)")

        lines.append("\n")  # separate teams

    # Join all lines into one string
    return "\n".join(lines)


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
@csrf.exempt
def dashboard():
    
    turfs=(Turf.query.join(TurfPhoto).filter(TurfPhoto.profile_pic==True).options(db.contains_eager(Turf.photos)).all())
    lat = float(request.args.get("lat", 22.5726))
    lon = float(request.args.get("lon", 88.3639))

    # 2) Check if a turf was clicked (to_lat,to_lon)
    to_lat = request.args.get("to_lat")
    to_lon = request.args.get("to_lon")
    route_to = None
    if to_lat and to_lon:
        route_to = {"lat": float(to_lat), "lon": float(to_lon)}

    print(to_lat, to_lon, route_to)

    # 3) Render map HTML
    turf_map_html = render_turf_map(lat, lon, radius=5000, route_to=route_to)

    return render_template('dashboard.html', turfs=turfs,  turf_map_html=turf_map_html)


@app.route('/turf_photo/<int:photo_id>')
def turf_photo(photo_id):
    photo=TurfPhoto.query.get(photo_id)
    if not photo:
        abort(404)
    return Response(photo.data, mimetype=photo.mimetype)

@app.route('/api/turfs')
@login_required_user
def api_turfs():
    turfs=(
        Turf.query
            .join(TurfPhoto)
            .filter(TurfPhoto.profile_pic==True)
            .options(db.contains_eager(Turf.photos))
            .all()
    )
    result=[]
    for turf in turfs:
        photo = turf.photos[0]
        result.append({
            "id":       turf.id,
            "name":     turf.name,
            "address":  turf.address,
            "city":     turf.city,
            "pincode":  turf.pincode,
            "status":   turf.status,
            "image":    url_for('turf_photo', photo_id=photo.id),
        })
    return jsonify(result)

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

@app.route('/turf/<int:turf_id>')
@login_required_user
def turf_details(turf_id):
    turf = (
        Turf.query
            .options(
                joinedload(Turf.photos),    
                joinedload(Turf.owner)     
            )
            .get_or_404(turf_id)
    )
    return render_template('turf.html', turf=turf)

@app.route('/book/<int:turf_id>', methods=['GET','POST'])
@login_required_user
@csrf.exempt
def booking(turf_id):
    turf = Turf.query.get_or_404(turf_id)

    # 1) Compute globals for both GET and POST
    today       = date.today()
    max_date    = today + timedelta(days=30)
    today_str   = today.strftime('%Y-%m-%d')

    ist      = pytz.timezone('Asia/Kolkata')
    now_ist  = datetime.now(ist)
    now_hour = now_ist.hour

    # 2) Determine selected date from GET args or POST form
    sel_date = request.values.get('date', today_str)
    try:
        sel_date_obj = datetime.strptime(sel_date, '%Y-%m-%d').date()
    except ValueError:
        sel_date_obj = today
        sel_date     = today_str

    # 3) Pre‑compute opening/closing hours
    opening_hour = turf.opening_time.hour
    closing_hour = turf.closing_time.hour

    # 4) Fetch already‑booked slots for this date
    booked = (
        Booking.query
               .filter_by(turf_id=turf_id, date=sel_date_obj)
               .with_entities(Booking.slot_index)
               .all()
    )
    booked_indices = {b.slot_index for b in booked}

    summary = None

    if request.method == 'POST':
        # 5) Pull fresh form fields
        slots     = sorted(int(i) for i in request.form.getlist('slots'))
        game_type = request.form['game_type']
        payment   = request.form['payment']
        # date_str = request.form['date']  # same as sel_date

        # 6) Re‑fetch booked_indices in case user just loaded GET with old values
        booked_indices = {b.slot_index for b in
            Booking.query.filter_by(turf_id=turf_id, date=sel_date_obj)
                   .with_entities(Booking.slot_index).all()
        }

        # 7) Validate selection
        errors = []
        if not slots:
            errors.append("Select at least one slot.")
        if any(slots[i+1] - slots[i] != 1 for i in range(len(slots)-1)):
            errors.append("Slots must be consecutive.")
        if any(idx in booked_indices for idx in slots):
            errors.append("One or more of those slots is already booked.")

        if errors:
            for msg in errors:
                flash(msg, "error")
        else:
            # 8) Persist bookings
            for idx in slots:
                db.session.add(Booking(
                    turf_id    = turf_id,
                    user_id    = get_current_user().id,
                    date       = sel_date_obj,
                    slot_index = idx,
                    created_at = datetime.utcnow()
                ))
            db.session.commit()
            flash("Booking confirmed!", "success")
            booked_indices |= set(slots)

            # 9) Build summary
            start = f"{slots[0]:02d}:00"
            end   = f"{(slots[-1]+1)%24:02d}:00"
            hours = len(slots)
            price = getattr(turf, f"{game_type.lower()}_price") * hours
            summary = {
                'start': start,
                'end': end,
                'hours': hours,
                'game_type': game_type,
                'payment': payment,
                'total_price': price
            }

    # 10) Single render_template with every var defined
    return render_template('bookingForm.html',
        turf            = turf,
        current_date    = today_str,
        max_date        = max_date.strftime('%Y-%m-%d'),
        sel_date        = sel_date,
        booked_indices  = booked_indices,
        opening_hour    = opening_hour,
        closing_hour    = closing_hour,
        now_hour        = now_hour,
        today_str       = today_str,
        summary         = summary
    )


@app.route('/create_match', methods=['GET','POST'])
@login_required_user
def create_match():
    form=MatchForm()
    if form.validate_on_submit():
        code=random.randint(100000, 999999)
        print(code)   
        send_email(get_current_user().email, "Match Room Code", f"Your Match Room Code is {code} !!!")
        scheduled=datetime.combine(form.date.data, form.time.data)
        with app.app_context():
            match_data=Match(creator_id=get_current_user().id,
                            teamName=form.teamName.data,
                            gameType=form.gameType.data,
                            turfName=form.turfName.data,
                            location=form.location.data,
                            scheduledFor=scheduled,
                            maxPlayers=form.players.data,
                            skill=form.skill.data,
                            room_type=form.room_type.data,
                            room_code=code
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

@app.route('/match/<int:match_id>/toggle_room', methods=['POST'])
@login_required_user
def toggle_room(match_id):
    m = Match.query.get_or_404(match_id)
    # Only the creator may change this
    if m.creator_id != get_current_user().id:
        abort(403)

    new_rt = request.form.get('room_type')
    if new_rt not in ('Public','Private'):
        flash('Invalid room type', 'error')
    else:
        m.room_type = new_rt
        db.session.commit()
        flash(f'Room set to {new_rt}', 'success')

    return redirect(url_for('live_match'))

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
    
    if match.room_type == 'Private':
        submitted = request.form.get('room_code', '').strip()
        # your model uses integer; cast carefully
        try:
            submitted_code = int(submitted)
        except ValueError:
            flash("Invalid room code format.", "error")
            return redirect(url_for('live_match'))

        if submitted_code != match.room_code:
            flash("Wrong room code. Cannot join private match.", "error")
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
        'timestamp': to_ist(m.timestamp).strftime('%Y-%m-%d %H:%M:%S')
    } for m in msgs])

@app.route('/api/matches/<int:match_id>/messages', methods=['POST'])
@login_required_user
@csrf.exempt
def post_message(match_id):
    # 1) Must have joined
    user_id = get_current_user().id
    is_participant = MatchParticipant.query.filter_by(
        matchId=match_id,
        userId=user_id
    ).first()
    if not is_participant:
        return jsonify({'error': 'Forbidden'}), 403

    # 2) Parse payload
    data = request.get_json() or {}
    text = (data.get('text') or '').strip()
    if not text:
        return jsonify({'error': 'Empty message'}), 400

    # 3) Create & save the message
    msg = ChatMessage(
        match_id=match_id,
        user_id=user_id,
        text=text
    )
    db.session.add(msg)
    db.session.commit()
    local_ts = to_ist(msg.timestamp)

    # 4) Return the newly created message
    return jsonify({
        'username': get_current_user().username,
        'text': msg.text,
        'timestamp': local_ts.strftime('%Y-%m-%d %H:%M:%S')
    }), 201

@app.route('/turfs/<int:turf_id>/photos', methods=['POST'])
@login_required_turfOwner
@csrf.exempt
def upload_turf_photos(turf_id):
    files = request.files.getlist('images')
    if not files:
        return jsonify({"error": "No files uploaded"}), 400

    saved = []
    for file in files:
        if file and file.mimetype.startswith('image/'):
            photo = TurfPhoto(
                turf_id   = turf_id,
                filename  = file.filename,
                data      = file.read(),
                mimetype  = file.mimetype,
                uploaded_at = datetime.utcnow()
            )
            db.session.add(photo)
            saved.append(file.filename)
    db.session.commit()

    return jsonify({
        "message": f"Uploaded {len(saved)} images.",
        "filenames": saved
    }), 200



@app.route('/stats')
@login_required_user
def stats():
    return render_template('stats.html')

@app.route('/set-turf-profile', methods=['GET', 'POST'])
def profile_setup():
    form=TurfForm()
    if form.validate_on_submit():
        turf = Turf(
            owner_id=get_current_turfOwner().id,        
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

@app.route('/api/matches/<int:match_id>/set_team', methods=['PATCH'])
@login_required_user
@csrf.exempt
def set_team(match_id):
    match = Match.query.get_or_404(match_id)
    data = request.get_json()

    # Update whichever side was sent
    if 'team1_id' in data:
        match.team1_id = data['team1_id']
    if 'team2_id' in data:
        match.team2_id = data['team2_id']

    db.session.commit()
    return jsonify({'success': True}), 200


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

@app.route('/api/teams', methods=['POST'])
@login_required_user
@csrf.exempt
def create_team():
    data = request.get_json()
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Name required'}), 400

    # If a team with that name already exists, just return it
    existing = Team.query.filter_by(name=name).first()
    if existing:
        return jsonify({'id': existing.id, 'name': existing.name}), 200

    team = Team(name=name)
    db.session.add(team)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        # In the unlikely race that someone created it between our query and commit,
        # fetch it again and return that.
        team = Team.query.filter_by(name=name).first()
        return jsonify({'id': team.id, 'name': team.name}), 200

    return jsonify({'id': team.id, 'name': team.name}), 201

@app.route('/api/teams/<int:team_id>', methods=['PATCH'])
@login_required_user
@csrf.exempt
def update_team(team_id):
    team = Team.query.get_or_404(team_id)
    data = request.get_json()
    if 'name' in data:
        team.name = data['name']
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/users', methods=['POST'])
@login_required_user
@csrf.exempt
def create_user():
    data = request.get_json()
    username = data.get('username')
    if not username:
        return jsonify({'error': 'Username required'}), 400
    user = User(username=username, email=f'{username}@example.com', password_hash='dummy')
    db.session.add(user)
    db.session.commit()
    return jsonify({'id': user.id, 'username': user.username})

@app.route('/api/users', methods=['GET'])
@login_required_user
@csrf.exempt
def get_user_by_name():
    username = request.args.get('username')
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({'id': user.id, 'username': user.username})
    return jsonify({})

@app.route('/api/scorecard/batting_records', methods=['POST'])
@login_required_user
@csrf.exempt
def create_batting_record():
    data = request.get_json()
    br = BattingRecord(
        match_id=data['match_id'],
        team_id=data['team_id'],
        player_id=data['player_id'],
        runs=0, balls=0, fours=0, sixes=0, is_out=False
    )
    db.session.add(br)
    db.session.commit()
    return jsonify({'id': br.id})

@app.route('/api/scorecard/batting_records/<int:rec_id>', methods=['PATCH'])
@login_required_user
@csrf.exempt
def update_batting_record(rec_id):
    br = BattingRecord.query.get_or_404(rec_id)
    data = request.get_json()
    for field in ['runs', 'balls', 'fours', 'sixes', 'player_id', 'is_out', 'desc']:
        if field in data:
            setattr(br, field, data[field])
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/scorecard/bowling_records', methods=['POST'])
@login_required_user
@csrf.exempt
def create_bowling_record():
    data = request.get_json()
    br = BowlingRecord(
        match_id=data['match_id'],
        team_id=data['team_id'],
        player_id=data['player_id'],
        overs=0, maidens=0, runs=0, wickets=0
    )
    db.session.add(br)
    db.session.commit()
    return jsonify({'id': br.id})

@app.route('/api/scorecard/bowling_records/<int:rec_id>', methods=['PATCH'])
@login_required_user
@csrf.exempt
def update_bowling_record(rec_id):
    br = BowlingRecord.query.get_or_404(rec_id)
    data = request.get_json()
    for field in ['overs', 'maidens', 'runs', 'wickets', 'player_id']:
        if field in data:
            setattr(br, field, data[field])
    db.session.commit()
    return jsonify({'success': True})

@app.route('/match/<int:match_id>/scorecard')
@login_required_user
@csrf.exempt
def match_scorecard(match_id):
    match = Match.query.get_or_404(match_id)
    txt = get_scorecard_string(match_id)
    top_players = get_mvp(txt)
    # Get teams
    team1 = Team.query.get(match.team1_id) if match.team1_id else None
    team2 = Team.query.get(match.team2_id) if match.team2_id else None
    # Get batting and bowling records for each team
    team1_batting = BattingRecord.query.filter_by(match_id=match.id, team_id=team1.id).all() if team1 else []
    team2_batting = BattingRecord.query.filter_by(match_id=match.id, team_id=team2.id).all() if team2 else []
    team1_bowling = BowlingRecord.query.filter_by(match_id=match.id, team_id=team1.id).all() if team1 else []
    team2_bowling = BowlingRecord.query.filter_by(match_id=match.id, team_id=team2.id).all() if team2 else []
    # Extras (if you store them separately, otherwise set to 0)
    team1_extras = 0
    team2_extras = 0
    participants = (
        MatchParticipant.query
        .filter_by(matchId=match.id)
        .join(User, MatchParticipant.userId == User.id)
        .add_columns(User.id.label('user_id'),
                     User.username.label('username'))
        .all()
    )
    # Pass is_creator if needed
    is_creator = (get_current_user().id == match.creator_id)
    return render_template(
        'cricket2.html',
        match=match,
        team1=team1,
        team2=team2,
        team1_batting=team1_batting,
        team2_batting=team2_batting,
        team1_bowling=team1_bowling,
        team2_bowling=team2_bowling,
        team1_extras=team1_extras,
        team2_extras=team2_extras,
        is_creator=is_creator,
        participants=participants,
        top_players=top_players 
    )

@app.route('/match/<int:match_id>/mvp')
@login_required_user
def match_mvp(match_id):
    txt = get_scorecard_string(match_id)
    top_players = get_mvp(txt)
    print(type(top_players))
    if not isinstance(top_players, dict):
        return jsonify(error="MVP generation failed"), 500
    return render_template('mvp_view.html', mvp=top_players)

@app.route('/match/<int:match_id>/mvp-view')
@login_required_user
def match_mvp_view(match_id):
    # fetch exactly the same data
    txt = get_scorecard_string(match_id)
    top_players = get_mvp(txt)
    if not isinstance(top_players, dict):
        # you could flash an error, or just show an empty page
        top_players = {}
    # render an HTML page, injecting the dict
    return render_template('mvp_view.html', mvp=top_players)

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