from flask_lib import FlaskLib
import database


backend = FlaskLib()
db = database.Database(dbname='postgres', user="sonu", password="sonu")


@backend.api('/api/multi')
def multi(d):
	return d['x']*d['y']

########

@backend.api('/sign_up')
def sign_up_function(frontend_dict):
	query1="select * from users where email={email}"
	output={}
	if len(db.readQuery(query1, frontend_dict))==0:
		query2 = "insert into users (name, email, phone, password) values ({name}, {email}, {phone}, {password}) "
		new_id = db.writeQuery(query2, frontend_dict)
		output['id']=new_id
	else:
		output['error']="phle se email h"
	return output


@backend.api('/login')
def login_function(frontend_dict):
	if len(db.readQuery("select * from users where email={email} AND password={password}", frontend_dict)) != 0:
		return {}
	else:
		return {"error": "Email or password is incorrect."}

@backend.api('/all_users')
def all_users_function(frontend_dict):
	return db.readQuery("select * from users")

@backend.api('/add_product')
def save_products(frontend_dict):
	query = "insert into products (name, price, discount, image, description) values ({name}, {price}, {discount}, {image},{description}) "
	db.writeQuery(query, frontend_dict)
	return db.readQuery("select * from products order by id desc")

@backend.api('/all_products')
def all_products_function(frontend_dict):
	query="select products.*, COALESCE(cart.product_quantity, 0) as product_quantity from products left join cart  on products.id=cart.product_id order by products.id desc "
	return db.readQuery( query )

@backend.api('/product_update')
def update(frontend_dict):
	print(frontend_dict)
	query="update products set name = {name}, price  = {price}, discount={discount}, image={image}, description={description} where id={id}"
	db.writeQuery(query, frontend_dict)
	return db.readQuery("select * from products order by id desc")


@backend.api('/add_product_quantity')
def add_product_quantity(frontend_dict):
	db.writeQuery("delete from cart where  product_id={product_id}", frontend_dict)
	if frontend_dict["product_quantity"] > 0:
		query = "insert into cart (product_id ,product_quantity) values ({product_id}, {product_quantity}) "
		db.writeQuery(query, frontend_dict)

@backend.api('/products_in_cart')
def products_in_cart(frontend_dict):
	query1=" select products.id, products.name, products.price, products.discount,products.image, cart.product_quantity , cart.product_quantity * products.price as subtotal from cart inner join products on cart.product_id=products.id "
	query2="select sum(cart.product_quantity * products.price) as total_amount from cart inner join products on cart.product_id=products.id "
	query2_output = db.readQuery(query2)
	total_amount = query2_output[0]["total_amount"]
	return {
		"total_list": db.readQuery(query1),
		"total_amount": total_amount}

@backend.api('/add_product_quantity_in_cart')
def add_product_quantity_in_cart(frontend_dict):
	db.writeQuery("delete from cart where  product_id={product_id}", frontend_dict)
	if frontend_dict["product_quantity"] > 0:
		query = "insert into cart (product_id ,product_quantity) values ({product_id}, {product_quantity}) "
		db.writeQuery(query, frontend_dict)
	return products_in_cart(frontend_dict)


backend.run(port=5502)
