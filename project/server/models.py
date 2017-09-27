from datetime import *
from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy_utils import aggregated
import json

import jwt
import datetime

from project.server import app, db, bcrypt

class BaseModel():
    def serialize(self, relation_levels=1):
        ret_data = {}
        
        columns = self.__table__.columns.keys()
        relationships = self.__mapper__.relationships.keys()
        column_attrs = dict(self.__mapper__.column_attrs)

        if hasattr(self, 'hide'):
            hide = self.hide
        else:
            hide = []
        
        for c in columns:
            if c not in hide:
                
                attr_type = type(column_attrs[c].columns[0].type).__name__
                if attr_type == "String":
                    s = str(column_attrs[c].columns[0].type)
                    attr_len = s[s.find("(")+1:s.find(")")]
                    ret_data[c] = {
                        'value': getattr(self, c), 
                        'type': attr_type, 
                        'len': attr_len
                    }
                else:
                    ret_data[c] = {
                        'value': getattr(self, c), 
                        'type': attr_type
                    }
        
        if relation_levels > 0:
            for r in relationships:
                if r not in hide:
                    if self.__mapper__.relationships[r].uselist:
                        ret_data[r] = []
                        for item in getattr(self, r):
                            if item:
                                ret_data[r].append(item.serialize(relation_levels-1))
                            else:
                                ret_data[r].append({})
                    else:
                        if getattr(self,r):
                            ret_data[r] = getattr(self, r).serialize(0)

        return ret_data

    

class Todo(db.Model, BaseModel):
    __tablename__ = 'todo'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    done = db.Column(db.Boolean)
    date = db.Column(db.DateTime)
    description = db.Column(db.String(100))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    shopping_list_id = db.Column(db.Integer, db.ForeignKey('shopping_list.id'))

    hide = ['shopping_list_id', 'user_id', 'account_id']

    
    def __init__(self, 
            user_id,
            account_id, 
            data
        ):
        self.account_id = account_id
        self.user_id = user_id
        self.title = data.get('title','')
        self.description = data.get('description','')
        self.done = data.get('done',False)
        self.date = data.get('date', datetime.datetime.now())
    
class ShoppingList(db.Model, BaseModel):
    __tablename__ = 'shopping_list'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    done = db.Column(db.Boolean)
    value = db.Column(db.Numeric)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    shopping_list_items = db.relationship('ShoppingListItem', backref='shopping_list')
    todos = db.relationship('Todo', backref='shopping_list')

    hide = ['category_id' , 'user_id', 'account_id']

    def __init__(self, 
            user_id,
            account_id, 
            data
        ):
        self.account_id = account_id
        self.user_id = user_id
        self.name = data.get('name','')
        self.done = data.get('done',False)
        self.value = data.get('date', 0)
        self.category_id = data.get('category').get('id')
    

class ShoppingListItem(db.Model, BaseModel):
    __tablename__ = 'shopping_list_item'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    value = db.Column(db.Numeric)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    shopping_list_id = db.Column(db.Integer, db.ForeignKey('shopping_list.id'))
    
    hide = ['category_id' , 'shopping_list_id']

    def __init__(self, 
            data,
            shopping_list_id,
            category_id
        ):
        self.name = data.get('name','')
        self.value = data.get('value', 0)
        self.shopping_list_id = shopping_list_id
        if category_id:
            self.category_id = category_id
        else:
            self.category_id = ShoppingList.query.get(shopping_list_id).category_id

class Budget(db.Model, BaseModel):
    __tablename__ = 'budget'
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    month = db.Column(db.Integer)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    budget_items = db.relationship('BudgetItem', backref='budget')

    hide = ['user_id', 'account_id']

    def __init__(self, account_id, user_id, data):
        self.account_id = account_id
        self.user_id = user_id
        self.year = data.get('year', datetime.datetime.now().year)
        self.month = data.get('year', datetime.datetime.now().month)

class BudgetItem(db.Model, BaseModel):
    __tablename__ = 'budget_item'
    id = db.Column(db.Integer, primary_key=True)
    budget_value = db.Column(db.Numeric)
    year = db.Column(db.Integer)
    month = db.Column(db.Integer)
    budget_id = db.Column(db.Integer, db.ForeignKey('budget.id'))
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    @aggregated('expenses', db.Column(db.Numeric))
    def sum_expenses(self):
        return func.sum(Expense.value)

    @aggregated('revenues', db.Column(db.Numeric))
    def sum_revenues(self):
        return func.sum(Revenue.value)


    expenses = db.relationship('Expense')
    revenues = db.relationship('Revenue')

    hide = ['category_id' , 'budget_item_id']

    def __init__(self, 
            account_id,
            data
        ):
        print(data.get('date', None))
        self.budget_value = data.get('budget_value','')
        self.category_id = data.get('category').get('id')
        self.year = data.get('year', datetime.datetime.now().year)
        self.month = data.get('year', datetime.datetime.now().month)
        self.account_id = account_id


class Expense(db.Model, BaseModel):
    __tablename__ = 'expense'
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Numeric)
    year = db.Column(db.Integer)
    month = db.Column(db.Integer)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    budget_item_id = db.Column(db.Integer, db.ForeignKey('budget_item.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))

    hide = ['category_id' , 'budget_item_id', 'user_id', 'account_id']


    def __init__(self, 
            data
        ):
        self.value = data.get('value','')
        self.year = data.get('year', datetime.datetime.now().year)
        self.month = data.get('year', datetime.datetime.now().month)
        self.category_id = data.get('category').get('id')

    def add_to_budget_item(self):
        budget_item = BudgetItem.query.filter(
                BudgetItem.year==self.year
            ).filter(
                BudgetItem.year==self.year
            ).filter(BudgetItem.category_id == self.category_id).first()
        
        budget_item.expenses.append(self)
    

class Revenue(db.Model, BaseModel):
    __tablename__ = 'revenue'
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    month = db.Column(db.Integer)
    value = db.Column(db.Numeric)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    budget_item_id = db.Column(db.Integer, db.ForeignKey('budget_item.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))

    hide = ['category_id' , 'budget_item_id', 'user_id', 'account_id']

    def __init__(self, 
            data
        ):
        self.value = data.get('value','')
        self.year = data.get('year', datetime.datetime.now().year)
        self.month = data.get('year', datetime.datetime.now().month)
        self.category_id = data.get('category').get('id')

    def add_to_budget_item(self):
        budget_item = BudgetItem.query.filter(
                BudgetItem.year==self.year
            ).filter(
                BudgetItem.year==self.year
            ).filter(BudgetItem.category_id == self.category_id).first()
        
        budget_item.expenses.append(self)


class Category(db.Model, BaseModel):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    
    shopping_lists = db.relationship('ShoppingList', backref='category')
    budget_items = db.relationship('BudgetItem', backref='category')
    expenses = db.relationship('Expense', backref='category')
    revenues = db.relationship('Revenue', backref='category')

    def __init__(self, account_id, data):
        self.account_id = account_id
        self.name = data.get('name')

class Account(db.Model, BaseModel):
    __tablename__ = 'account'
    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(50))
    level = db.Column(db.String(50))

    users = db.relationship('User', backref="account")
    todos = db.relationship('Todo', backref='account')
    shopping_lists = db.relationship('ShoppingList', backref='account')
    budgets = db.relationship('Budget', backref='account')
    categories = db.relationship('Category', backref='account')
    expenses = db.relationship('Expense', backref='account')
    revenues = db.relationship('Revenue', backref='account')
    
    def __init__(self, account_name, level='basic'):
        self.account_name = account_name
        self.level = level

class User(db.Model, BaseModel):
    """ User Model for storing user related details """
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))

    #rel_account = db.relationship('Account')

    todos = db.relationship('Todo', backref='user')
    shopping_lists = db.relationship('ShoppingList', backref='user')
    budgets = db.relationship('Budget', backref='user')
    expenses = db.relationship('Expense', backref='user')
    revenues = db.relationship('Revenue', backref='user')

    hide = ['password' ,'account_id']

    def __init__(self, email, password, account_id, admin=False):
        self.email = email
        print(app.config.get('SECRET_KEY'))
        self.password = bcrypt.generate_password_hash(
            password, app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()
        self.registered_on = datetime.datetime.now()
        self.admin = admin
        self.account_id = account_id

    def encode_auth_token(self, user_id, account_id):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id,
                'account': account_id
            }
            print(jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            ))
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Validates the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
            is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
            if is_blacklisted_token:
                return 'Token blacklisted. Please log in again.'
            else:
                return payload
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'


class BlacklistToken(db.Model, BaseModel):
    """
    Token Model for storing JWT tokens
    """
    __tablename__ = 'blacklist_tokens'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def __repr__(self):
        return '<id: token: {}'.format(self.token)

    @staticmethod
    def check_blacklist(auth_token):
        # check whether auth token has been blacklisted
        res = BlacklistToken.query.filter_by(token=str(auth_token)).first()
        if res:
            return True
        else:
            return False
