from flask_lib import FlaskLib
import database
import time
import os
import urllib.request
import math
import csv
import io


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
# sign_up ki api h

@backend.api('/sign_up')
def sign_up(frontend_dict, session):
	time.sleep(2)
	query1="select * from users where email={email}"
	output={}
	if('role' not in frontend_dict):
		frontend_dict['role']='USER'
	if len(db.readQuery(query1, frontend_dict))==0:	
		query2 = "insert into users (name, email, phone, password,role) values ({name}, {email}, {phone}, {password} ,{role}) "
		db.writeQuery(query2, frontend_dict)
		new_id = db.readQuery("select max(id) as new_id from users")[0]["new_id"]
		session['login_key'] = {"id": new_id,"role":frontend_dict["role"], "name": frontend_dict["name"]}
	else:
		output['error']="phle se email h"
	return output

# login_page ki api h
@backend.api('/login')
def login(frontend_dict, session):
	time.sleep(2)
	query_output = db.readQuery("select * from users where email={email} AND password={password}", frontend_dict)
	if len(query_output) != 0:
		session['login_key'] = {"id": query_output[0]['id'],"role":query_output[0]['role'], "name": query_output[0]['name']}
		return {}
	else:
		return {"error": "Email or password is incorrect."}

# admin.html ki api h.
@backend.api('/all_users')
def all_users(frontend_dict):
	return db.readQuery("select * from users where role={role} order by id desc", frontend_dict)

# admin1.html ki api h

#  jo bi details frontend se ayi h usko products table me insert krna h or usi table ko read krke return krna h
@backend.api('/add_product')
def add_product(frontend_dict,session):
	time.sleep(2)
	frontend_dict['farmer_id']=login_id(session)
	query = "insert into products (name, price, image, description,farmer_id) values ({name}, {price}, {image},{description},{farmer_id}) "
	db.writeQuery(query, frontend_dict)

	# return db.readQuery("select * from products order by id desc")


@backend.api('/load_farmer_all_products')
def load_farmer_all_products(frontend_dict,session):
	frontend_dict['farmer_id']=login_id(session)
	l=db.readQuery("select * from users where id={farmer_id}",frontend_dict)
	print(l)
	if l[0]["account_status"]=='ACTIVE':
		return {"farmer_products_list":db.readQuery("select * from products where farmer_id= {farmer_id} order by id desc",frontend_dict)}
	else:
		return {"error":"Your account is not verified yet.."}
	

# yha jo item h usko edit(update)kiya gya h fir jo update table h usko read krke return kiya gya h.
@backend.api('/product_update')
def product_update(frontend_dict):
	time.sleep(2)
	print(frontend_dict)
	query="update products set name = {name}, price  = {price}, image={image}, description={description} where id={id}"
	db.writeQuery(query, frontend_dict)
	return db.readQuery("select * from products order by id desc")

@backend.api('/api_c')
def api_c(frontend_dict, session):
	time.sleep(3)
	return ["11", 33, 55]


# poducts_page.html ki api h
# product and admin1ki commen api h jisme products table ko or cart table ko join kiya hua h jisme products ki full details h or cart me se products quantities kia table bnai h jisko yha read kiya gya h
@backend.api('/all_products')
def all_products(frontend_dict, session):
	time.sleep(2)
	print(frontend_dict)
	one_page_num_products = 8
	frontend_dict["user_id"] = login_id(session)
	frontend_dict["search_key"] = '%' + frontend_dict["search_key"] + '%'
	frontend_dict["offset"] = (int(frontend_dict['page']) - 1)*one_page_num_products
	query="select products.*, COALESCE(cart.product_quantity, 0) as product_quantity from products left join cart  on products.id=cart.product_id AND cart.user_id={user_id} WHERE name like {search_key}"
	if frontend_dict['sort_price'] == 'Price: High to Low':
		query += " order by products.price desc"
	elif frontend_dict['sort_price'] == 'Price: Low to High':
		query += " order by products.price asc"
	else:
		query += " order by products.id desc"
	query += " offset {offset} limit " + str(one_page_num_products)

	num_page =math.ceil((db.readQuery("SELECT COUNT(id) As num_products FROM products WHERE name like {search_key}", frontend_dict)[0]["num_products"])/one_page_num_products)
	# total_page=db.readQuery("SELECT COUNT(")
	return {"products_list":db.readQuery(query, frontend_dict), "num_page":num_page} 


@backend.api('/admin_all_products')
def admin_all_products(frontend_dict):
	query="select * from products order by products.id desc"
	return db.readQuery(query)

# ye api products page me use ki gyi h jisme jo quantites hm add krte h cart me dalne ke liye vo inset hoti h cart table me but use phle hme cart me se us produts ki jo phle ki quantity h usko htana hota h taki new insert kr ske isliye phle delete ki query fir insert ki query NOTE: yha se koyi bi output ni jayega kyuki yha cart ki jo table h vo hi update hogi is api ka kam h only auantiyt jo ab dali h usko inset krna.
@backend.api('/add_product_quantity')
def add_product_quantity(frontend_dict, session):
	print(session)
	frontend_dict["user_id"] = login_id(session)
	db.writeQuery("delete from cart where product_id={product_id} AND user_id = {user_id}",frontend_dict)
	l1=db.readQuery("select products.farmer_id from cart left join products on cart.product_id=products.id WHERE cart.user_id = {user_id}",frontend_dict)
	l2=db.readQuery("select * from products where id={product_id}", frontend_dict)

	print(l1)
	print(l2)
	print(frontend_dict)

	for i in l1:
		if i['farmer_id'] != l2[0]['farmer_id']:
			return {"error":"same farmer products ni h."}

	if frontend_dict["product_quantity"] > 0:
		query = "insert into cart (product_id ,product_quantity,user_id) values ({product_id}, {product_quantity},{user_id})"
		db.writeQuery(query, frontend_dict)
	return {}

# cart.html ki api h

@backend.api('/products_in_cart')
def products_in_cart(frontend_dict, session):
	frontend_dict["user_id"] = login_id(session)
	query1=" select products.id, products.name, products.price, products.discount,products.image, products.farmer_id, cart.product_quantity , cart.product_quantity * products.price as subtotal from cart inner join products on cart.product_id=products.id where cart.user_id = {user_id}"
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

def checkout_now(frontend_dict, session, paid):
	cart_info=products_in_cart({}, session)
	if len(cart_info['total_list']) == 0:
		return {"error": "Cart empty"}
	query1="insert into orders(store_name , total_amount, ordered_at, expected_delivery_at, status, user_id, address_id, paid, farmer_id) values ('sonu store', {total_amount}, {ordered_at}, {expected_delivery_at}, 'ORDERED', {user_id}, {address_id},{paid}, {farmer_id})"
	frontend_dict['paid'] = paid
	frontend_dict['total_amount'] = cart_info["total_amount"]
	frontend_dict['farmer_id'] = cart_info['total_list'][0]["farmer_id"]
	frontend_dict['ordered_at'] = int(time.time())
	frontend_dict['expected_delivery_at'] = frontend_dict['ordered_at'] + 48*3600
	frontend_dict["user_id"] = session["login_key"]["id"]
	frontend_dict["address_id"] = frontend_dict.get("address_id", 0)
	db.writeQuery(query1, frontend_dict)

	A="select max(id) As order_id from orders"
	B=db.readQuery(A)[0]['order_id']
	print(B)

	for i in cart_info['total_list']:
		p = {"x" : B, "y": i["id"], "z": i["product_quantity"]}
		db.writeQuery("insert into order_items (order_id , product_id, product_quantity) values({x}, {y}, {z})", p)
	db.writeQuery("delete from cart")
	return {}


@backend.api('/pay_later_and_order')
def pay_later_and_order(frontend_dict, session):
	return checkout_now(frontend_dict, session, 0)


@backend.api('/products_according_to_id')
def products_according_to_id(frontend_dict):
	query="select products.*, COALESCE(cart.product_quantity, 0) as product_quantity from products left join cart on products.id=cart.product_id where id={product_id}"
	output=db.readQuery(query, frontend_dict)
	if len(output)==0:
		return {"error":"item not available"}
	else:
		return output[0]

def preprocessOrderRow(row):
	row['ordered_at_str'] = time.strftime('%Y-%m-%d %I:%M:%S %p', time.localtime(row['ordered_at']))
	row['delivery_at_str'] = time.strftime('%Y-%m-%d %I:%M:%S %p', time.localtime(row['delivery_at']))
	row['expected_delivery_at_str'] = time.strftime('%Y-%m-%d %I:%M:%S %p', time.localtime(row['expected_delivery_at']))
	row['order_at_date_str']= time.strftime('%Y-%m-%d', time.localtime(row['ordered_at']))
	row['status_display']=row['status'].title()
	return row

@backend.api('/orders')
def orders(frontend_dict,session):
	frontend_dict["user_id"] = session["login_key"]["id"]
	query1="select orders.*, addresses.address from orders left join addresses on orders.address_id=addresses.id where orders.user_id = {user_id} order by id desc"
	l=db.readQuery( query1, frontend_dict)
	for i in l:
		preprocessOrderRow(i)
	return  l

@backend.api('/order_item')
def order_item(frontend_dict):
	query1="select order_items.*,products.id, products.image, products.price,products.name, product_quantity*products.price As subtotal from order_items left join products on order_items.product_id=products.id where order_items.order_id={order_id}"
	query2="select total_amount from orders where id={order_id}"
	l2 = db.readQuery(query2, frontend_dict)
	if len(l2) == 0:
		return {"error": "Invalid order id"}
	l1 = db.readQuery( query1, frontend_dict)
	return {"order_item_list": l1,
			"total_amount": l2[0]["total_amount"]}


@backend.api('/admin_all_orders')
def admin_all_orders(frontend_dict):
	query1="select orders.*,addresses.address,users.name AS farmer_name from orders left join addresses on orders.address_id=addresses.id left join users on  orders.farmer_id=users.id order by id desc"
	l=db.readQuery( query1, frontend_dict)
	query2="select id, name from users where users.role='DELIVERY_PERSON' AND account_status='ACTIVE' "
	
	for i in l:
		preprocessOrderRow(i)
	return {"orders_details":l,"delivery_person_list": db.readQuery(query2)}

@backend.api('/Status_save')
def Status_save(frontend_dict):
	time.sleep(2)
	db.writeQuery("UPDATE orders SET status = {status} WHERE id={order_id}", frontend_dict)
	# return admin_all_orders({})

@backend.api('/get_user_detail')
def get_user_detail(frontend_dict, session):
	# frontend_dict["user_id"] = login_id(session)
	l=db.readQuery("select id, name, phone, email, role,address from users where id ={user_ki_id}", frontend_dict)
	if len(l)!=0:
		l1=db.readQuery("select id, address from addresses where user_id={user_ki_id}", frontend_dict)
		d = l[0]
		d["address_list"] = l1
		return d
	else:
		return {"error":"id not correct"}


@backend.api('/update_user_details')
def update_user_details(frontend_dict, session):
	frontend_dict["user_id"] = login_id(session)
	query="update users set name = {name}, phone  = {phone},address={address} where id={user_id}"
	db.writeQuery(query, frontend_dict)
	session["login_key"]["name"] = frontend_dict["name"]

@backend.api('/add_address')
def new_address(frontend_dict, session):
	print(frontend_dict)
	frontend_dict["user_id"] = login_id(session)
	db.writeQuery("insert into addresses(user_id,address,label) values({user_id},{address},'')",frontend_dict)
	return db.readQuery("select id, address from addresses where user_id={user_id}", frontend_dict)

@backend.api('/update_address')
def update_address(frontend_dict, session):
	print(frontend_dict)
	frontend_dict["user_id"] = login_id(session)
	db.writeQuery("update addresses set address = {address} where id={address_id} AND user_id={user_id}" , frontend_dict)

@backend.api('/delete_address')
def delete_address(frontend_dict, session):
	print(frontend_dict)
	frontend_dict["user_id"] = login_id(session)
	db.writeQuery("DELETE FROM addresses where id={address_id} AND user_id={user_id}",frontend_dict )
	return db.readQuery("select id, address from addresses where user_id={user_id}", frontend_dict)

@backend.api('/update_password')
def update_password(frontend_dict, session):
	print(frontend_dict)
	frontend_dict["user_id"] = login_id(session)
	if frontend_dict["new_password"] != frontend_dict["repeat_password"]:
		return {"error": "youe password is different from repeat password"}
	l=db.readQuery("select id from users where password = {old_password} AND id={user_id}", frontend_dict)
	if len(l)==0:
		return {"error":"old password is not correct"}
	db.writeQuery("update users set password = {new_password} where id={user_id}",frontend_dict)
	return {}
@backend.api('/checkout_info')
def checkout_info(frontend_dict, session):
	print(frontend_dict)
	frontend_dict["user_id"] = login_id(session)
	l1=db.readQuery("select phone from users where id={user_id} ",frontend_dict)
	if len(l1) > 0:
		l2=db.readQuery("select id, address from addresses where user_id={user_id}", frontend_dict)
		return {
			"cart_items": products_in_cart(frontend_dict, session),
			"phone_number":l1[0]["phone"],
			"delivery_address_list":l2 
		}

@backend.api('/pay_online_and_order')
def pay_later_and_order(frontend_dict, session):
	cart_info=products_in_cart({}, session)
	return checkout_now(frontend_dict, session, cart_info['total_amount'])

@backend.api('/update_account_status')
def update_account_status(frontend_dict, session):
	db.writeQuery("update users set account_status = {account_status} where id={user_id}",frontend_dict)
	print(frontend_dict)


@backend.api('/farmer_all_orders')
def farmer_all_orders(frontend_dict, session):
	frontend_dict['farmer_id']=login_id(session)
	l=db.readQuery("select orders.*,addresses.address from orders  left join addresses on orders.address_id=addresses.id where farmer_id={farmer_id} order by orders.id desc",frontend_dict)
	for i in l:
		preprocessOrderRow(i)
	return  l

@backend.api('/assign_delivery_person')
def assign_delivery_person(frontend_dict, session):
	db.writeQuery("update orders set delivery_person_id={delivery_person_id} where id={order_id}",frontend_dict)

@backend.api('/assign_delivery_person_now')
def assign_delivery_person_now(frontend_dict, session):
	frontend_dict["delivery_person_id"] = login_id(session)
	db.writeQuery("update orders set delivery_person_id={delivery_person_id} where id={order_id}",frontend_dict)
	return unallocated_orders(frontend_dict, session)

def date_of_list(list_of_dic):
	l1={}
	for i in list_of_dic:
		if i["order_at_date_str"] not in l1:
			l1[i["order_at_date_str"]]=[]
		l1[i["order_at_date_str"]].append(i)
	return l1

@backend.api('/delivery_person_all_orders')
def delivery_person_all_orders(frontend_dict, session):	
	frontend_dict['delivery_person_id']=login_id(session)

	query1="select orders.* ,users.name,farmers.name as farmers_name,farmers.address as farmer_address, addresses.address from orders left join users on orders.user_id = users.id left join addresses on orders.address_id=addresses.id left join users as farmers on orders.farmer_id= farmers.id where delivery_person_id={delivery_person_id} "

	l=db.readQuery(query1, frontend_dict)
	for i in l:
		preprocessOrderRow(i)
	return date_of_list(l)
	
@backend.api('/delivery_person_status')
def delivery_person_status(frontend_dict, session):
	time.sleep(2)
	if frontend_dict["status"]=="DELIVERED":
		frontend_dict["x"]=time.time()
	else:
		frontend_dict["x"]=0
		
	db.writeQuery("UPDATE orders SET status = {status},delivery_at={x} WHERE id={order_id}", frontend_dict)

@backend.api('/unallocated_orders')
def unallocated_orders(frontend_dict, session):
	frontend_dict["delivery_person_id"] = login_id(session)
	# query1="select orders.*,addresses.address,users.name AS farmer_name from orders left join addresses on orders.address_id=addresses.id left join users on  orders.farmer_id=users.id order by id desc"

	query1="select orders.*,users.address AS farmer_address,addresses.address AS user_address,users.name AS farmer_name from orders left join addresses on orders.address_id=addresses.id left join users on  orders.farmer_id=users.id where (orders.status='CONFIRMED' or orders.status='ORDERED') AND (delivery_person_id is null ) "

	query2="select orders.*,users.address AS farmer_address,addresses.address AS user_address,users.name AS farmer_name from orders left join addresses on orders.address_id=addresses.id   left join users on  orders.farmer_id=users.id  where (orders.status='CONFIRMED' or orders.status='ORDERED') AND (delivery_person_id = {delivery_person_id}  ) "
	l1=db.readQuery(query1)
	l2=db.readQuery(query2, frontend_dict)

	for i in l1:
		preprocessOrderRow(i)
	for i in l2:
		preprocessOrderRow(i)

	return {"unassigned_orders":l1,
	       "my_assigned_orders":l2}


@backend.api('/upload_image')
def upload_image(frontend_dict, session):
	v="data/image_"+str(int(time.time()))+"." + frontend_dict["filename"].split(".")[-1]
	f = open(v , "wb")
	print(len(frontend_dict["image_file_content"]))
	r = urllib.request.urlopen(frontend_dict["image_file_content"])
	f.write(r.file.read())
	f.close()
	return v

#l=[["name","price","quantity"],["sonu",100,1000],["mohit",10,100],["soniya",20,402]]
# l1=["name","price","quantity"]
# l2=[["sonu",100,1000],["mohit",10,100],["soniya",20,402]]
# result=[{"name":"sonu","price":100,"quantity":1000},
# {"name":"mohit","price":10,"quantity":100},{"name":"soniya","price":20,"quantity":402}

REQUIRED_FIELDS = ["name", "price", "image","description" ]

def transform_csv_products(l):
    l1=l[0]
    l2=l[1:]
    list3=[]
    if REQUIRED_FIELDS != l1:
        return {"error": "Invalid columns. Should be " + str(REQUIRED_FIELDS)}
    for k in range(len(l2)):
        i = l2[k]
        if len(i) == 0:
        	continue
        if len(REQUIRED_FIELDS) != len(i):
            return {"error": "Invalid row " + str(k+1) + ". Should match header columns. " + str(REQUIRED_FIELDS)}
        d={}
        for j in range(len(i)):
            d[l1[j]]=i[j]
        list3.append (d)            
    return {"list": list3}

@backend.api('/import_products')
def import_products(frontend_dict, session):
	r = urllib.request.urlopen(frontend_dict["file_content"])
	x = list(csv.reader(r.file.read().decode('UTF-8').split("\n")))
	print(x)
	output = transform_csv_products(x)
	if "error" in output:
		return output
	for i in output["list"]:
		i['farmer_id']=login_id(session)
		db.writeQuery("insert into products(name, price, image,description,farmer_id) values({name}, {price}, {image},{description},{farmer_id})",i)
	return {}


# output = [ ["name","price","quantity"],["sonu",100,1000],["mohit",10,100],["soniya",20,402]
# input = [ {'name': 'sonu', 'price': 100, 'quantity': 1000}, {'name': 'mohit', 'price': 10, 'quantity': 100},
# {'name': 'soniya', 'price': 20, 'quantity': 402} ]

def transform_back_to_csv(l):
    l1 = [REQUIRED_FIELDS]
    for d in l:
        l2 = []
        for j in REQUIRED_FIELDS:
            l2.append(d[j])
        l1.append(l2)
    return l1

@backend.api('/export_products')
def export_products(frontend_dict, session):
	frontend_dict['farmer_id']=login_id(session)
	l = db.readQuery("select * from products where farmer_id={farmer_id}",frontend_dict)
	output = transform_back_to_csv(l)
	file = io.StringIO()
	writer = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC)
	writer.writerows(output)
	return {"csv_content": file.getvalue()}


@backend.api('/order_tracking_info')
def order_tracking_info(frontend_dict, session):
	frontend_dict['delivery_person_id']=login_id(session)

	query="select orders.*, users.name AS farmer_name from orders left join users on users.id= farmer_id where orders.id={order_id}"

	output= db.readQuery(query,frontend_dict)

	print(output)
	if len(output)==0:
		return {"error":"order invalid"}
	
	else:
		preprocessOrderRow(output[0])
		return output[0]

backend.run(port=5502)

