import requests
import sys
import time
import os
import re
from datetime import datetime, timedelta

# Dependency Check
try:
    import ascii_magic
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    print("\033[91m[!] Missing dependencies: 'ascii-magic' or 'colorama'.\033[0m")
    print("\033[93mRun: pip install ascii-magic colorama requests\033[0m")
    sys.exit(1)

class UI:
    # Silly Retro "Bricky" Palette
    BRICK_RED = '\033[38;5;160m'
    BRIGHT_BLUE = '\033[38;5;39m'
    SLIME_GREEN = '\033[38;5;118m'
    SUNNY_YELLOW = '\033[38;5;226m'
    PLASTIC_GREY = '\033[38;5;248m'
    NEON_PINK = '\033[38;5;201m'
    WHITE = '\033[38;5;255m'
    BOLD = '\033[1m'
    END = '\033[0m'

class OpenBloxAPI:
    @staticmethod
    def request(method, url, **kwargs):
        retries = 5
        for i in range(retries):
            try:
                headers = kwargs.get('headers', {})
                headers['User-Agent'] = 'OpenBlox/Silly-Edition'
                kwargs['headers'] = headers
                response = requests.request(method, url, timeout=10, **kwargs)
                if response.status_code == 429:
                    time.sleep(2**i)
                    continue
                return response
            except Exception:
                if i == retries - 1: return None
                time.sleep(2**i)
        return None

def bricky_loading(text):
    """Silly retro bouncy loading animation."""
    frames = ["■□□□", "■■□□", "□■■□", "□□■■", "□□□■", "□□□□"]
    for _ in range(2):
        for frame in frames:
            sys.stdout.write(f"\r {UI.SUNNY_YELLOW}[{frame}] {UI.WHITE}{text}...{UI.END}")
            sys.stdout.flush()
            time.sleep(0.1)
    sys.stdout.write("\r" + " " * 60 + "\r")

def get_avatar_ascii(user_id, columns=50):
    try:
        thumb_url = f"https://thumbnails.roblox.com/v1/users/avatar?userIds={user_id}&size=420x420&format=Png&isCircular=false"
        res = OpenBloxAPI.request("GET", thumb_url)
        if res and res.status_code == 200:
            img_url = res.json()['data'][0]['imageUrl']
            my_art = ascii_magic.from_url(img_url)
            return my_art.to_ascii(columns=columns, monochrome=False, back=None).splitlines()
        return [f"{UI.PLASTIC_GREY}[NO BLOCKS FOUND]{UI.END}"]
    except:
        return [f"{UI.BRICK_RED}[OOF! AVATAR ERROR]{UI.END}"]

def get_strict_tags(user_id, username, friends, followers, badges, created_str, is_banned):
    tags = []
    join_date = datetime.strptime(created_str[:10], '%Y-%m-%d')
    now = datetime.now()

    if is_banned:
        tags.append(f"{UI.BRICK_RED}{UI.BOLD}[BANNED BRICK]{UI.END}")
    
    if badges > 2000 and followers < 10:
        tags.append(f"{UI.NEON_PINK}[HACKER MAN]{UI.END}")

    if followers >= 1000000 and friends >= 20:
        tags.append(f"{UI.SUNNY_YELLOW}[ULTRA FAMOUS]{UI.END}")
    elif followers >= 10000 and friends < 20:
        tags.append(f"{UI.BRICK_RED}{UI.BOLD}[PREDATOR ALERT]{UI.END}")

    if 2006 <= join_date.year <= 2016:
        tags.append(f"{UI.SUNNY_YELLOW}[CLASSIC OG]{UI.END}")

    half_year_ago = now - timedelta(days=182)
    if join_date > half_year_ago:
        tags.append(f"{UI.PLASTIC_GREY}[NEWBIE/ALT]{UI.END}")

    if not is_banned:
        tags.append(f"{UI.SLIME_GREEN}[STILL BLOXIN']{UI.END}")

    return " ".join(tags)

def fetch_user_data(user_id):
    bricky_loading("Building Blocks")
    bricky_loading("Finding Noobs")
    
    u_res = OpenBloxAPI.request("GET", f"https://users.roblox.com/v1/users/{user_id}")
    if not u_res or u_res.status_code != 200:
        print(f"\n {UI.BRICK_RED}{UI.BOLD}[OOF!] THAT USER DOESN'T EXIST!{UI.END}")
        return

    data = u_res.json()
    created = data.get('created', '2006-01-01')
    is_banned = data.get('isBanned', False)
    display_name = data.get('displayName', 'Noob')
    
    # Detailed Data Gathering
    f_count = OpenBloxAPI.request("GET", f"https://friends.roblox.com/v1/users/{user_id}/friends/count").json().get('count', 0)
    fol_count = OpenBloxAPI.request("GET", f"https://friends.roblox.com/v1/users/{user_id}/followers/count").json().get('count', 0)
    following_count = OpenBloxAPI.request("GET", f"https://friends.roblox.com/v1/users/{user_id}/followings/count").json().get('count', 0)
    b_count = OpenBloxAPI.request("GET", f"https://badges.roblox.com/v1/users/{user_id}/badges?limit=1").json().get('total', 0)
    
    # Extra Info: Membership
    premium_res = OpenBloxAPI.request("GET", f"https://premiumfeatures.roblox.com/v1/users/{user_id}/validate-membership")
    has_premium = premium_res.json() if premium_res else False

    tags = get_strict_tags(user_id, data['name'], f_count, fol_count, b_count, created, is_banned)
    ascii_art = get_avatar_ascii(user_id)
    
    bio = (data.get('description') or "I'm too shy to write a bio!").replace('\n', ' ')[:55] + "..."

    # Bricky Side Panel
    info_panel = [
        f"{UI.BOLD}{UI.SUNNY_YELLOW}WHO DAT?{UI.END}     : {UI.BOLD}{UI.WHITE}{data['name']}{UI.END}",
        f"{UI.BOLD}{UI.SUNNY_YELLOW}NICKNAME{UI.END}     : {UI.PLASTIC_GREY}{display_name}{UI.END}",
        f"{UI.BOLD}{UI.SUNNY_YELLOW}BRICK ID{UI.END}     : {UI.BRIGHT_BLUE}{user_id}{UI.END}",
        f"{UI.PLASTIC_GREY}--------------------------------------------------{UI.END}",
        f"{UI.BOLD}{UI.WHITE}REPUTATION{UI.END}   : {tags}",
        f"{UI.BOLD}{UI.WHITE}SPAWN DATE{UI.END}   : {UI.SLIME_GREEN}{created[:10]}{UI.END}",
        f"{UI.BOLD}{UI.WHITE}PREMIUM?{UI.END}     : {UI.SUNNY_YELLOW + 'YES! (Rich Guy)' if has_premium else UI.PLASTIC_GREY + 'Nope.'}{UI.END}",
        f"",
        f"{UI.BRIGHT_BLUE}╔══ BRICKY STATS ══╗{UI.END}",
        f"{UI.BRIGHT_BLUE}║{UI.END} {UI.WHITE}Friends    : {f_count}{UI.END}",
        f"{UI.BRIGHT_BLUE}║{UI.END} {UI.WHITE}Followers  : {fol_count}{UI.END}",
        f"{UI.BRIGHT_BLUE}║{UI.END} {UI.WHITE}Following  : {following_count}{UI.END}",
        f"{UI.BRIGHT_BLUE}║{UI.END} {UI.WHITE}Shiny Badges: {b_count}{UI.END}",
        f"{UI.BRIGHT_BLUE}╚══════════════════╝{UI.END}",
        f"",
        f"{UI.BOLD}{UI.NEON_PINK}WHAT THEY SAID:{UI.END}",
        f" {UI.WHITE}“{bio}”{UI.END}",
        f"",
        f"{UI.BRICK_RED}■ {UI.BRIGHT_BLUE}■ {UI.SLIME_GREEN}■ {UI.SUNNY_YELLOW}■ {UI.END} {UI.BOLD}BYE BYE!{UI.END}"
    ]

    # Render Interface
    print(f"\n{UI.SUNNY_YELLOW}╔{'═'*120}╗{UI.END}")
    max_h = max(len(ascii_art), len(info_panel))
    for i in range(max_h):
        l_img = ascii_art[i] if i < len(ascii_art) else " " * 50
        r_txt = info_panel[i] if i < len(info_panel) else ""
        print(f"{UI.SUNNY_YELLOW}║{UI.END} {l_img}  {r_txt}")
    print(f"{UI.SUNNY_YELLOW}╚{'═'*120}╝{UI.END}\n")

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Silly Retro Header
    header = f"""{UI.BOLD}{UI.BRIGHT_BLUE}
     _______________________________________________________
    /                                                       \\
    |   {UI.SUNNY_YELLOW}█▀█ █▀█ █▀▀ █▄░█ █▄▄ █░░ █▀█ ▀▄▀{UI.BRIGHT_BLUE}                    |
    |   {UI.SUNNY_YELLOW}█▄█ █▀▀ ██▄ █░▀█ █▄█ █▄▄ █▄█ █░█{UI.BRIGHT_BLUE}                    |
    |                                                       |
    |      {UI.WHITE}Beta V0.4 - POWERED BY BRICKS{UI.BRIGHT_BLUE}           |
    \\_______________________________________________________/
    """
    print(header)
    
    while True:
        try:
            print(f" {UI.SLIME_GREEN}* {UI.WHITE}WHO DO YOU WANT TO SPY ON?{UI.END}")
            target = input(f" {UI.SLIME_GREEN}> {UI.SUNNY_YELLOW}ROBLOX_ID:{UI.END} ").strip()
            
            if not target:
                continue
                
            if target.lower() in ['exit', 'quit', 'stop', 'bye']:
                print(f"\n {UI.BRICK_RED}SEE YOU LATER, BRICK-HEAD!{UI.END}")
                break

            if target.isdigit():
                fetch_user_data(target)
            else:
                print(f"\n {UI.BRICK_RED}[!] HEY! USE NUMBERS! (Roblox IDs are numbers silly){UI.END}\n")
                
        except KeyboardInterrupt:
            print(f"\n\n {UI.BRICK_RED}OOF! EMERGENCY SHUTDOWN!{UI.END}")
            sys.exit(0)

if __name__ == "__main__":
    main()
