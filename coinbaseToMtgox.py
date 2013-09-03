import json,requests,csv,time,smtplib,string,os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from xvfbwrapper import Xvfb

state_file='/home/ian/Documents/arbiter/trader_state.csv'
headers = {'content-type': 'application/json','User-Agent':'Firefox/5.0'}


def req_and_ret(url,req_input,header,url_type='GET'):
	if url_type=='GET':
			r=requests.get(url,data=json.dumps(req_input),headers=header)
	else:
			r=requests.post(url,data=json.dumps(req_input),headers=header)
	list_response=r.json()
	json_response = json.dumps(list_response)
	return list_response,json_response

def get_coinbase_info(input_vars):
	buy_price_url = "https://coinbase.com/api/v1/prices/buy"
	price_payload={'qty':1.0}

	#Get Current Bitcoin Prices for buy

	buy_price_response,throwaway = req_and_ret(buy_price_url,price_payload,headers)
	input_vars['last_coinbase_price']=float(buy_price_response['subtotal']['amount'])

# def l

def coinbase_buy(amount_to_trade,input_vars):
	buy_url = "https://coinbase.com/api/v1/buys"
	transaction_payload = {'api_key':input_vars['coinbase_api_key'],'qty':amount_to_trade}
	transaction_response,trans_resp_string=req_and_ret(buy_url,transaction_payload,'POST')
	success=transaction_response['success']
	errors=''
	amount_per_btc=0
	total_amount=0
	trans_code=''
	if not success:
		errors=transaction_response['errors']
	else:
		total_amount=float(transaction_response['transfer']['total']['amount'])
		amount_per_btc=total_amount/amount_to_trade
		trans_code=transaction_response['transfer']['code']
	subject=''
	text=''
	if not success:
		subject="Got Problems With Your Bitcoin Arbiter"
		text="Hello Sir \n\n I just had trouble making an api based buy bitcoin transaction on coinbase. Coinbase gave the following error: \r\n "+str(errors)+"\r\n You have 1 day from the time these email was sent to fix the problem. \n\n Yours Truly, \n\n RPI BitTrader \r\n PS This is the whole response: \r\n" +str(trans_resp_string)
	else:
		subject="Successful Buy On the Part of Your Bitcoin Arbiter"
		text="Hello Sir \n\n I just made a Buy order successfully on coinbase. \r\n The price was "+str(total_amount)+" for "+str(amount_to_trade)+"BTC \n\n Yours Truly, \n\n RPI BitTrader"

	send_email(input_vars['gmailUser'],input_vars['gmailUser'],subject,text,input_vars)

	return success,errors,trans_code

# def coinbase_transfer(to_addr):

	
def read_state(return_vars):
#Reading in current state
	with open(state_file,'r') as trader_state:
		trader_state_csv=csv.reader(trader_state,delimiter=',')
		for line in trader_state_csv:
			if not line[0].isdigit():
				return_vars[line[0]]=line[1]
			else:
				return_vars[line[0]]=float(line[1])
		trader_state.close()

	return return_vars

def send_email(to_addr,from_addr,subject,text,vars_in):
	mailServer = smtplib.SMTP('smtp.gmail.com', 587)
	mailServer.ehlo()
	mailServer.starttls()
	mailServer.ehlo()
	mailServer.login(vars_in['gmailUser'],vars_in['gmailPassword'])
	body=string.join(("From: %s" % from_addr,"To: %s" % to_addr,"Subject: %s" % subject ,"",text), "\r\n")
	mailServer.sendmail(from_addr, [to_addr], body)
	mailServer.close()

def save_state(input_vars):

	# record the state

	assembled_message=''
	with open(state_file,'r') as trader_state_read:
		trader_state_csv=csv.reader(trader_state_read,delimiter=',')
		for line in trader_state_csv:
			assembled_message=assembled_message+line[0]+','+str(input_vars[line[0]])+'\n'
			

	with open(state_file,'w') as trader_state:
		trader_state.write(assembled_message)
		trader_state.close()

def get_mtgox_info(input_vars):
	vdisplay = Xvfb()
	vdisplay.start()

	driver = webdriver.Firefox()

	driver.get("http://www.mtgox.com")

	uelem = driver.find_element_by_name("username")
	pelem = driver.find_element_by_name("password")
	lelem = driver.find_element_by_name("LOGIN")

	uelem.send_keys(input_vars['mtgoxId'])
	time.sleep(0.25)
	pelem.send_keys(input_vars['mtgoxPassword'])
	time.sleep(0.25)
	lelem.click()
	time.sleep(0.25)

	driver.get("https://www.mtgox.com/trade/funding-options")
	time.sleep(0.25)

	logout_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "logout")))

	address_elem = driver.find_elements_by_xpath("/html/body/div[2]/div[2]/div[3]/div[3]/section/div/div[4]/div[2]/div/p/strong")

	print address_elem
	new_address=address_elem.text

	# input_vars['mtgoxBTCAddress']=''
	# if len(str(new_address))>10:
	# 	input_vars['mtgoxBTCAddress']=new_address

	# driver.get("https://www.mtgox.com/trade")

	# time.sleep(0.25)
	
	# logout_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "logout")))
	# sell_button = driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[3]/section/ul/li[2]/a')
	# sell_button.click()
	# time.sleep(0.25)
	# price_elem = driver.find_element_by_id('sellP')

	# input_vars['last_mtgox_price']=float(price_elem.text[1:])

	# logout_button.click()

	# time.sleep(0.25)

	# driver.quit()

	# vdisplay.stop()

def withdraw_usd(input_vars):
	driver = webdriver.Firefox()

	driver.get("http://www.mtgox.com")

	uelem = driver.find_element_by_name("username")
	pelem = driver.find_element_by_name("password")
	lelem = driver.find_element_by_name("LOGIN")

	uelem.send_keys(input_vars['mtgoxId'])
	time.sleep(0.25)
	pelem.send_keys(input_vars['mtgoxPassword'])
	time.sleep(0.25)
	lelem.click()
	time.sleep(0.25)

	driver.get("https://www.mtgox.com/trade")

	time.sleep(0.25)
	
	logout_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "logout")))
	dollars_field = driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[3]/section/form[2]/table/tbody/tr/td/p/span')

	dollars=float(dollars_field.text[1:])
	print dollars

	driver.get("https://www.mtgox.com/trade/funding-options")
	time.sleep(0.25)

	logout_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "logout")))

	withdraw_button = driver.find_element_by_xpath('//*[@id="withdrawFundsBtn"]')
	withdraw_button.click()
	time.sleep(0.25)
	dropdown_elem = driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[3]/div[3]/section[2]/form/div/div/div[3]/div/a')
	dropdown_elem.click()
	time.sleep(0.1)
	dropdown_elem.send_keys(Keys.ARROW_DOWN)
	time.sleep(0.1)
	dropdown_elem.send_keys(Keys.ARROW_DOWN)
	time.sleep(0.1)
	dropdown_elem.send_keys(Keys.ARROW_DOWN)
	time.sleep(0.1)
	dropdown_elem.send_keys(Keys.ARROW_DOWN)
	time.sleep(0.1)
	dropdown_elem.send_keys(Keys.ENTER)
	time.sleep(0.25)
	amount_field=driver.find_element_by_xpath('//*[@id="amount"]')
	submit_field=driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[3]/div[3]/section[2]/form/div/p/a/span')
	amount_field.send_keys(str(dollars*0.1))
	#submit_field.click()


	input_vars['dollars_in_bank'] = dollars+float(input_vars['dollars_in_bank'])

	logout_button.click()

	time.sleep(0.25)

	driver.quit()