from flask_lib import FlaskLib
import database
import time
import os


backend = FlaskLib()

if os.environ.get('FRESHMART_SONU_ENV') == 'mohit':
	db = database.Database(dbname='postgres', user="mohit.saini", password="")
else:
	db = database.Database(dbname='postgres', user="sonu", password="sonu")


@backend.api('/api/multi')
def multi(d):
	return d['x']*d['y']

########
def Is_login(session):
  if "login_key" in session and "id" in session["login_key"]:
    return True
  else:
    return False


def login_id(session):
	if Is_login(session):
		return session["login_key"]["id"]
	else:
		return 0

@backend.api('/sign_up')
def sign_up_function(frontend_dict, session):
	query1="select * from users where email={email}"
	output={}
	if len(db.readQuery(query1, frontend_dict))==0:
		query2 = "insert into users (name, email, phone, password) values ({name}, {email}, {phone}, {password}) "
		db.writeQuery(query2, frontend_dict)
		new_id = db.readQuery("select max(id) as new_id from users")[0]["new_id"]
		session['login_key'] = {"id": new_id, "name": frontend_dict["name"]}
	else:
		output['error']="phle se email h"
	return output


@backend.api('/login')
def login_function(frontend_dict, session):
	query_output = db.readQuery("select * from users where email={email} AND password={password}", frontend_dict)
	if len(query_output) != 0:
		session['login_key'] = {"id": query_output[0]['id'], "name": query_output[0]['name']}
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
def all_products_function(frontend_dict,session):
	frontend_dict["user_id"] = login_id(session)
	query="select products.*, COALESCE(cart.product_quantity, 0) as product_quantity from products left join cart  on products.id=cart.product_id AND cart.user_id={user_id} order by products.id desc "
	return db.readQuery( query,frontend_dict)

@backend.api('/product_update')
def update(frontend_dict):
	print(frontend_dict)
	query="update products set name = {name}, price  = {price}, discount={discount}, image={image}, description={description} where id={id}"
	db.writeQuery(query, frontend_dict)
	return db.readQuery("select * from products order by id desc")


@backend.api('/add_product_quantity')
def add_product_quantity(frontend_dict, session):
	print(session)
	frontend_dict["user_id"] = session["login_key"]["id"]
	db.writeQuery("delete from cart where product_id={product_id} AND user_id = {user_id}",frontend_dict)
	if frontend_dict["product_quantity"] > 0:
		query = "insert into cart (product_id ,product_quantity,user_id) values ({product_id}, {product_quantity},{user_id})"
		db.writeQuery(query, frontend_dict)

@backend.api('/products_in_cart')
def products_in_cart(frontend_dict, session):
	frontend_dict["user_id"] = session["login_key"]["id"]
	query1=" select products.id, products.name, products.price, products.discount,products.image, cart.product_quantity , cart.product_quantity * products.price as subtotal from cart inner join products on cart.product_id=products.id where cart.user_id = {user_id}"
	query2="select sum(cart.product_quantity * products.price) as total_amount from cart inner join products on cart.product_id=products.id where cart.user_id = {user_id}"
	query2_output = db.readQuery(query2 , frontend_dict)
	total_amount = query2_output[0]["total_amount"]
	p = {
		"total_list": db.readQuery(query1, frontend_dict),
		"total_amount": total_amount}
	return p

@backend.api('/add_product_quantity_in_cart')
def add_product_quantity_in_cart(frontend_dict,session):
	add_product_quantity(frontend_dict,session)
	return products_in_cart(frontend_dict, session)


@backend.api('/products_according_to_id')
def products_according_to_id(frontend_dict):
	query="select products.*, COALESCE(cart.product_quantity, 0) as product_quantity from products left join cart on products.id=cart.product_id where id={product_id}"
	output=db.readQuery(query, frontend_dict)
	if len(output)==0:
		return {"error":"item not available"}
	else:
		return output[0]

@backend.api('/checkout')
def checkout(frontend_dict, session):
	cart_info=products_in_cart({}, session);
	query1="insert into orders(store_name , total_amount, ordered_at, expected_delivery_at, status, user_id) values ('sonu store', {total_amount}, {ordered_at}, {expected_delivery_at}, 'ORDERED', {user_id})"
	frontend_dict['total_amount'] = cart_info['total_amount']
	frontend_dict['ordered_at'] = int(time.time())
	frontend_dict['expected_delivery_at'] = frontend_dict['ordered_at'] + 48*3600
	frontend_dict["user_id"] = session["login_key"]["id"]
	db.writeQuery(query1, frontend_dict)

	A="select max(id) As order_id from orders"
	B=db.readQuery(A)[0]['order_id']
	print(B)

	for i in cart_info['total_list']:
		p = {"x" : B, "y": i["id"], "z": i["product_quantity"]}
		db.writeQuery("insert into order_items (order_id , product_id, product_quantity) values({x}, {y}, {z})", p)
	db.writeQuery("delete from cart")

@backend.api('/orders')
def orders(frontend_dict,session):
	frontend_dict["user_id"] = session["login_key"]["id"]
	query1="select * from orders where orders.user_id = {user_id} order by id desc"
	l=db.readQuery( query1, frontend_dict)
	for i in l:
		i['ordered_at_str'] = time.strftime('%Y-%m-%d %I:%M:%S %p', time.localtime(i['ordered_at']))
		i['delivery_at_str'] = time.strftime('%Y-%m-%d %I:%M:%S %p', time.localtime(i['delivery_at']))
		i['expected_delivery_at_str'] = time.strftime('%Y-%m-%d %I:%M:%S %p', time.localtime(i['expected_delivery_at']))
		i['status_display']=i['status'].title()
	return  l

@backend.api('/order_item')
def order_item(frontend_dict):
	query1="select order_items.*,products.id, products.image, products.price,products.name, product_quantity*products.price As subtotal from order_items left join products on order_items.product_id=products.id where order_items.order_id={order_id}"

	return db.readQuery( query1, frontend_dict)


@backend.api('/orders_details')
def orders_details(frontend_dict):
	return orders(frontend_dict)


@backend.api('/Status_save')
def Status_save(frontend_dict):
	db.writeQuery("UPDATE orders SET status = {status} WHERE id={order_id}", frontend_dict)
	return db.readQuery("select * from orders order by id desc")



  


backend.run(port=5502)
