from flask_login import current_user, login_user, logout_user, login_required
from app import app
from app.forms import LoginForm, RegistrationForm, TicketForm, ResponseForm, AddCategoryForm, EditCategoryForm, DeleteCategoryForm, MarkResolvedForm
from flask import render_template, flash, redirect, url_for, abort, request
from app import db
from app.models import User, Ticket, Category, Response
import sqlalchemy as sa
from datetime import timezone
from zoneinfo import ZoneInfo

@app.template_filter('to_gmt')
def to_gmt(value):
    if value is None:
        return ''
    return value.replace(tzinfo=timezone.utc).astimezone(ZoneInfo('Europe/London')).strftime('%Y-%m-%d %H:%M:%S')

@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    return render_template('index.html', title='Home')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.email == form.email.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('main'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(name=form.name.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/main')
@login_required
def main():
    categories = Category.query.all()
    page = request.args.get('page', 1, type=int)
    has_response = db.session.query(
        sa.exists().where(
            Response.ticket_id.in_(
                db.session.query(Ticket.id).filter(Ticket.user_id == current_user.id)
            )
        )
    ).scalar()
    ticket_query = Ticket.query.order_by(Ticket.date_created.desc()) 
    filter_category = request.args.get('category', type=int)
    date = request.args.get('date', 'desc')  
    priority = request.args.get('priority', 0, type=int)   

    if priority == 1:
        ticket_query = Ticket.query.order_by(Ticket.priority.asc())
    elif date == 'asc':
        ticket_query = Ticket.query.order_by(Ticket.date_created.asc())

    if filter_category: 
        ticket_query = ticket_query.filter(Ticket.category_id == filter_category)

    tickets = db.paginate(ticket_query, 
                        page=page,
                        per_page=app.config['POSTS_PER_PAGE'],
                        error_out=False)
    next_url = url_for('main', page=tickets.next_num) \
        if tickets.has_next else None
    prev_url = url_for('main', page=tickets.prev_num) \
        if tickets.has_prev else None

    return render_template('main.html', title='Home', user=current_user.name, num_pages = tickets.pages, tickets=tickets.items, next_url=next_url, date_direction=date, priority=priority, prev_url=prev_url, cur_page=tickets.page, categories=categories, has_response=has_response)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/ticket', methods=['GET', 'POST'])
@login_required
def ticket():
    
    form = TicketForm()
    categories = Category.query.all()
    form.category.choices = [(cat.id, cat.name) for cat in categories]
    if form.validate_on_submit():
        
        ticket = Ticket(title=form.title.data, description=form.description.data, user_id=current_user.id, category_id=form.category.data)
        db.session.add(ticket) 
        db.session.commit()
        flash('Your ticket has been submitted!')
        return redirect(url_for('main'))
    return render_template('ticket.html', title='Ticket', form=form)


@app.route('/thread/<int:id>', methods=['GET', 'POST'])
@login_required
def thread(id):
    form = ResponseForm()
    resolved_form = MarkResolvedForm()
    ticket = db.session.get(Ticket, id)
    responses = Response.query.filter_by(ticket_id=id).order_by(Response.date_created.asc()).all()
    owner = (ticket.user_id == current_user.id) if ticket else False
    if resolved_form.submit_resolved.data:
        if resolved_form.validate_on_submit() and ticket.status != 'resolved':
            ticket.status = 'resolved'
            db.session.commit()
            flash('Ticket marked as resolved.')
            return redirect(url_for('thread', id=ticket.id))
    if ticket is None:
        abort(404)
    if form.submit.data:
        if form.validate_on_submit():
            response = Response(content=form.content.data, ticket_id=ticket.id, user_id=current_user.id)
            db.session.add(response)
            db.session.commit()
            flash('Your response has been submitted!')
            return redirect(url_for('thread', id=ticket.id))
    category = db.session.get(Category, ticket.category_id)
    author = db.session.get(User, ticket.user_id)
    return render_template('thread.html', title='Thread', ticket=ticket, category=category, author=author, form=form, resolved_form=resolved_form, responses=responses, owner=owner)

@app.route('/thread/<int:id>/toggle_priority', methods=['POST'])
@login_required
def toggle_priority(id):
    if current_user.type != "admin":
        abort(403)  # Forbidden
    ticket = db.session.get(Ticket, id)
    if ticket is None:
        abort(404)
    priority = request.form.get('priority')
    ticket.priority = 1 if ticket.priority == 0 else 0
    db.session.commit()
    return redirect(url_for('thread', id=ticket.id))


@app.route('/admin', methods=['GET','POST'])
@login_required
def admin():
    if current_user.type != "admin":
        abort(403)  # Forbidden
    categories = Category.query.all()
    action = request.args.get('action', "", type=str)
    action_id = request.args.get('action_id', 0, type=int)
    
    add_cat_form = AddCategoryForm()
    if add_cat_form.submit_add.data:  
        if add_cat_form.validate_on_submit():
            new_category = Category(name=add_cat_form.name.data)
            db.session.add(new_category)
            db.session.commit()
            flash('Category added successfully!')
            return redirect(url_for('admin', action='add_cat'))
            
    edit_cat_form = EditCategoryForm()
    if edit_cat_form.submit_edit.data:
        if edit_cat_form.validate_on_submit():
            edit_category = Category.query.get_or_404(action_id)
            edit_category.name = edit_cat_form.name.data
            db.session.commit()
            flash('Category updated successfully!', 'success')
            return redirect(url_for('admin'))
    
    del_cat_form = DeleteCategoryForm()
    if del_cat_form.submit_del.data:
        if del_cat_form.validate_on_submit():
            category = db.session.get(Category, action_id)
            if category is None:
                abort(404)
            db.session.delete(category)
            db.session.commit()
            flash('Category deleted successfully!')
            return redirect(url_for('admin'))

    return render_template("admin.html",  title="Admin", categories=categories, action=action, action_id=action_id, add_cat_form=add_cat_form, edit_cat_form=edit_cat_form, del_cat_form=del_cat_form) 