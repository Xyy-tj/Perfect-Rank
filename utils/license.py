
import sys
import os

# from networkx import desargues_graph
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(project_root)

from utils.logger import Ranker_Logger
logger = Ranker_Logger.get_logger()


from Crypto.Cipher import AES
from binascii import b2a_hex

import re
import datetime
import subprocess
from binascii import a2b_hex
import uuid

def encrypt(content):
    # content length must be a multiple of 16.
    while len(content) % 16:
        content += ' '
    content = content.encode('utf-8')
    # Encrypt content.
    aes = AES.new(b'2021052020210520', AES.MODE_CBC, b'2021052020210520')
    encrypted_content = aes.encrypt(content)
    return(b2a_hex(encrypted_content))


# 生成license文件的函数
def gen_license_file(valid_days):
    license_file = './license.lic'
    current_date = datetime.datetime.now()
    expiry_date = current_date + datetime.timedelta(days=valid_days)
    # 获取本机MAC地址
    mac = uuid.getnode()
    # 将MAC地址格式化为标准格式
    mac_address = ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2))
    issue_date = current_date.strftime("%Y%m%d")
    expiry_date_str = expiry_date.strftime("%Y%m%d")
    
    with open(license_file, 'w') as LF:
        LF.write(f'MAC : {mac_address}\n')
        LF.write(f'Issue Date : {issue_date}\n')
        LF.write(f'Expiry Date : {expiry_date_str}\n')
        
        sign = encrypt('%s#%s' % (mac_address, expiry_date_str))
        LF.write('Sign : ' + str(sign.decode('utf-8')) + '\n')

    print(f"License file '{license_file}' generated successfully.")


## License check
def license_check():
    license_dic = parse_license_file()
    sign = decrypt(license_dic['Sign'])
    sign_list = sign.split('#')
    mac = sign_list[0].strip()
    date = sign_list[1].strip()
    # Check license file is modified or not.
    if (mac != license_dic['MAC']) or (date != license_dic['Expiry Date']):
        logger.error('License file is modified!')
        sys.exit(1)
    return True
    # Check MAC and effective date invalid or not.
    if len(sign_list) == 2:
        mac = get_mac()
        current_date = datetime.datetime.now().strftime('%Y%m%d')
        # 请注意修改此处的MAC地址为指定授权的MAC地址
        if sign_list[0] != uuid.getnode():
            logger.error('MAC Address Unauthorized.')
            pass
            # return False
        if sign_list[1] < current_date:
            logger.error('License is expired!')
            return False
    else:
        logger.error('License check failed.')
        return False
    logger.debug('License check passed.')
    return True


def parse_license_file():
    license_dic = {}
    license_file = './license.lic'
    with open(license_file, 'r') as LF:
        for line in LF.readlines():
            # 使用正则表达式匹配键值对
            match = re.match(r'^\s*(.+?)\s*:\s*(.+?)\s*$', line)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                license_dic[key] = value
    return license_dic


def decrypt(content):
    aes = AES.new(b'2021052020210520', AES.MODE_CBC, b'2021052020210520')
    decrypted_content = aes.decrypt(a2b_hex(content.encode('utf-8')))
    return(decrypted_content.decode('utf-8'))


def get_mac():
    mac = ''
    SP = subprocess.Popen('/sbin/ifconfig', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = SP.communicate()
    for line in str(stdout, 'utf-8').split('\n'):
        if re.match('^\s*ether\s+(\S+)\s+.*$', line):
            my_match = re.match('^\s*ether\s+(\S+)\s+.*$', line)
            mac = my_match.group(1)
            break
    return(mac)



if __name__ == '__main__':
    gen_license_file(valid_days=30)
    lic_check = license_check()
    print("Check Result: %s" % lic_check)