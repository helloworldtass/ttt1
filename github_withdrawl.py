import requests
import time
import random
import hmac
import base64
import hashlib
import json
from typing import List
from datetime import datetime
from colorama import init,Fore

# OKX API credentials
API_KEY = '1a--a'
SECRET_KEY = '3'
PASSPHRASE = 'Z%'

# API endpoints
BASE_URL = 'https://www.okx.com'
WITHDRAWAL_ENDPOINT = '/api/v5/asset/withdrawal'

# Supported currencies and chains
CURRENCIES = ['BTC', 'USDT', 'ETH', 'USDC']
CHAINS = ['ETH-zkSync Era', 'ETH-Arbitrum One', 'ETH-Optimism'] 
#CHAINS = [ 'ETH-Arbitrum One', 'ETH-Optimism'] 

zkSync_addresses = []
arb_addresses = []
opt_addresses = []

def write_address_to_file(filename: str, address: str):
    with open(filename, 'a') as file:
        file.write(address + '\n')

def read_addresses_from_file(filename: str) -> List[str]:
    with open(filename, 'r') as file:
        addresses = [line.strip() for line in file]
    random.shuffle(addresses)
    return addresses

def generate_signature(timestamp: str, method: str, request_path: str, body: str, secret_key: str):
    message = timestamp + method + request_path + body
    mac = hmac.new(bytes(secret_key, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod=hashlib.sha256)
    d = mac.digest()
    return base64.b64encode(d)

def get_network_time():
    utc_time = datetime.utcnow()
    formatted_time = utc_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    return formatted_time

def create_withdrawal(currency: str, address: str, amount: float):
    chain = random.choice(CHAINS)
    #chain = 'ETH-zkSync Era'
    #chain = 'ETH-Arbitrum One'
    fee = 0.0004 if chain == 'ETH-zkSync Era' else 0.0001

    timestamp = get_network_time()
    method = 'POST'
    request_path = WITHDRAWAL_ENDPOINT
    body = json.dumps({
        'ccy': currency,
        'toAddr': address,
        'amt': amount,
        'fee': fee,
        'pwd': PASSPHRASE,
        'dest': '4',
        'chain': chain
    })

    headers = {
        'OK-ACCESS-KEY': API_KEY,
        'OK-ACCESS-SIGN': generate_signature(timestamp, method, request_path, body, SECRET_KEY),
        'OK-ACCESS-TIMESTAMP': timestamp,
        'OK-ACCESS-PASSPHRASE': PASSPHRASE,
        'Content-Type': 'application/json'
    }

    response = requests.post(BASE_URL + request_path, headers=headers, data=body)

    if response.status_code == 200:
        print(f'成功提现: {amount:.6f} {currency} 到地址: {address}')
        print(Fore.GREEN + f'提币链为: {chain}')
        print(Fore.GREEN + f'提币数量为: {amount:.6f}')
        print(f'提币时间为: {timestamp}')
        
        # 写入地址到相应的文件
        filename = f"{chain.replace(' ', '_').replace('-', '_')}_addresses.txt"
        write_address_to_file(filename, address)
        
    else:
        print(f'提现失败: {amount:.6f} {currency} 到地址: {address}. 原因: {response.text}')

    print("- - - -下一个...等待中...- - - - ")

def main():
    # 颜色自动重置
    init(autoreset=True)
    addresses = read_addresses_from_file('with_address.txt')
    random.shuffle(addresses)
    currency = input('输入提币币种 (BTC/USDT/ETH/USDC): ')
    min_amount, max_amount = map(float, input('请输入提币数量范围: ').split())

    for address in addresses:
        amount = round(random.uniform(min_amount, max_amount), random.randint(3, 7))
        create_withdrawal(currency, address, amount)
        # 100-200s提现一个地址
        time.sleep(random.randint(100, 300))

    
    print("所有地址提现完毕")

if __name__ == '__main__':
    main()
