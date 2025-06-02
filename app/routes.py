from flask import render_template, redirect, url_for, request, flash
from app import app, db
from app.model.user import User
from app.model.package import Package
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
import uuid
from app.model.office import Office
from app.utils.jarak import calculate_distance
from app.utils.dijkstra import get_optimal_route

@app.route('/')
@app.route('/home')
def index():
    return render_template('home.html', title='Home')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('index'))
        flash('Username atau password salah')
    return render_template('login.html', title='Login')

@app.route('/add-package', methods=['GET', 'POST'])
@login_required
def add_package():
    if request.method == 'POST':
        package = Package(
            tracking_number=str(uuid.uuid4())[:8].upper(),
            sender_name=request.form['sender_name'],
            receiver_name=request.form['receiver_name'],
            receiver_address=request.form['receiver_address'],
            receiver_phone=request.form['receiver_phone'],
            lat=float(request.form['lat']),
            lng=float(request.form['lng']),
            courier_id=current_user.id
        )
        db.session.add(package)
        db.session.commit()
        flash('Paket berhasil ditambahkan')
        return redirect(url_for('find_route'))
    return render_template('add_package.html', title='Tambah Paket')

@app.route('/find-route')
@login_required
def find_route():
    office = Office.query.filter_by(is_main=True).first()
    if not office:
        office = Office(
            name="Kantor Unesa Express",
            address="jl barat-maospati, Kabupaten magetan",
            lat=-7.5879252,
            lng=111.4375723,
            is_main=True
        )
        db.session.add(office)
        db.session.commit()

    packages = Package.query.filter_by(
        courier_id=current_user.id,
        status='pending'
    ).all()

    if packages:
        
        optimized_packages, total_distance = get_optimal_route(office, packages)
        
        
        for i, package in enumerate(optimized_packages):
            if not hasattr(package, 'distance'):
                package.distance = 0
                
        
        avg_speed = 30  
        stop_time = 10  
        total_time = (total_distance / avg_speed) + (len(optimized_packages) * stop_time / 60)
        estimated_time = str(timedelta(hours=total_time)).split('.')[0]
    else:
        optimized_packages = []
        total_distance = 0
        estimated_time = "0:00:00"

    return render_template(
        'find_route.html',
        title='Cari Rute',
        office=office,
        packages=optimized_packages,  
        total_distance=total_distance,
        estimated_time=estimated_time
    )

@app.route('/history')
@login_required
def history():
    
    delivered_packages = Package.query.filter_by(
        status='delivered',
        courier_id=current_user.id
    ).order_by(Package.delivered_at.desc()).all()
    
    packages_by_date = {}
    total_packages = 0
    total_distance = 0.0  
    
    for package in delivered_packages:
        date = package.delivered_at.strftime('%Y-%m-%d')
        if date not in packages_by_date:
            packages_by_date[date] = []
        packages_by_date[date].append(package)
        total_packages += 1
        
        if package.distance:
            total_distance += float(package.distance)
    
    return render_template('history.html', 
                         packages_by_date=packages_by_date,
                         total_packages=total_packages,
                         total_distance=round(total_distance, 1)) 

@app.route('/about')
def about():
    
    developers = [
        {
            'name': 'Restu Mahardika',
            'nim': '24111814034',
            'image': 'Anggota1.jpg',
            'instagram': 'instagram_username1',
            'github': 'github_username1'
        },
        {
            'name': 'Hafiyyan Lintang Arizaki',
            'nim': '24111814048',
            'image': 'Anggota2.jpg',
            'instagram': 'instagram_username2',
            'github': 'github_username2'
        },
         {
            'name': 'Mia Audina Ika Aprilani',
            'nim': '24111814107',
            'image': 'Anggota3.png',
            'instagram': 'instagram_username2',
            'github': 'github_username2'
        },
         {
            'name': 'Bagus Candra Priyatna',
            'nim': '24111814129',
            'image': 'Anggota4.jpg',
            'instagram': 'instagram_username2',
            'github': 'github_username2'
        },
         {
            'name': 'Rifkia Zaqli Yaumulalam',
            'nim': '24111814132',
            'image': 'Anggota5.jpg',
            'instagram': 'instagram_username2',
            'github': 'github_username2'
        }
        
    ]
    
    return render_template('about.html', title='Tentang Kami', developers=developers)

@app.route('/mark-delivered/<tracking_number>', methods=['POST'])
@login_required
def mark_delivered(tracking_number):
    
    package = Package.query.filter_by(tracking_number=tracking_number).first_or_404()
    
    
    if package.courier_id != current_user.id:
        flash('Anda tidak memiliki akses ke paket ini', 'danger')
        return redirect(url_for('find_route'))
    
    office = Office.query.filter_by(is_main=True).first()
    
    
    if not package.distance:
        package.distance = calculate_distance(
            office.lat, 
            office.lng, 
            package.lat, 
            package.lng
        )
    
    package.status = 'delivered'
    package.delivered_at = datetime.now()
    
    try:
        db.session.commit()
        flash('Paket berhasil ditandai terkirim', 'success')
    except:
        db.session.rollback()
        flash('Terjadi kesalahan saat memperbarui status paket', 'danger')
    
    return redirect(url_for('history'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        
        if User.query.filter_by(username=username).first():
            flash('Username sudah digunakan')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email sudah terdaftar')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Password tidak cocok')
            return redirect(url_for('register'))
        
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registrasi berhasil! Silahkan login')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Register')
