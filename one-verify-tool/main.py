"""
Gemini Verifier v12.0 (Enrollment Letter + Scan Effect)
Type: Official Registrar Letter (Highest Success Rate)
Features:
- "Scan Effect" to mimic real paper documents.
- Dynamic Dates (Matches Today).
- Full Verification Wording.
"""

import sys
import time
import random
import hashlib
import re
import datetime
from io import BytesIO
from typing import Dict, Optional, Tuple

try:
    import httpx
except ImportError:
    print("❌ Error: httpx missing.")
    sys.exit(1)

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
except ImportError:
    print("❌ Error: Pillow missing.")
    sys.exit(1)

# ============ CONFIG ============
SHEERID_API_URL = "https://services.sheerid.com/rest/v2"

UNIVERSITIES = [
    {"id": 3568, "name": "University of Michigan", "short": "U-MICH", "city": "Ann Arbor, MI"},
    {"id": 3499, "name": "Univ. of California, Los Angeles", "short": "UCLA", "city": "Los Angeles, CA"},
    {"id": 2565, "name": "Pennsylvania State University", "short": "PENN STATE", "city": "University Park, PA"},
    {"id": 1426, "name": "Harvard University", "short": "HARVARD", "city": "Cambridge, MA"},
    {"id": 378, "name": "Arizona State University", "short": "ASU", "city": "Tempe, AZ"}
]

FIRST_NAMES = ["James", "Robert", "Michael", "David", "William", "Richard", "Joseph"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller"]

# ============ UTILS ============
def generate_fingerprint() -> str:
    return hashlib.md5(str(time.time()).encode()).hexdigest()

def generate_name() -> Tuple[str, str]:
    return random.choice(FIRST_NAMES), random.choice(LAST_NAMES)

def generate_email(first: str, last: str, domain: str) -> str:
    domain = domain.replace("univ.", "u").replace("university", "u").replace(" ", "").lower() + ".edu"
    return f"{first[0].lower()}{last.lower()}{random.randint(10,99)}@{domain}"

def get_current_dates():
    """Returns today's date and term dates"""
    today = datetime.date.today()
    # Assuming Spring Semester logic
    term_start = f"January 05, {today.year}"
    term_end = f"May 15, {today.year}"
    today_str = today.strftime("%B %d, %Y")
    return today_str, term_start, term_end

def select_university() -> Dict:
    uni = random.choice(UNIVERSITIES)
    return {**uni, "idExtended": str(uni["id"]), "domain": uni["short"].lower() + ".edu"}

# ============ SCAN EFFECT GENERATOR ============
def apply_scan_effect(img):
    """Adds noise and blur to look like a scanned document"""
    # 1. Add subtle noise
    pixels = img.load()
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            r, g, b = pixels[i, j]
            noise = random.randint(-15, 15)
            pixels[i, j] = (
                max(0, min(255, r + noise)),
                max(0, min(255, g + noise)),
                max(0, min(255, b + noise))
            )
    
    # 2. Slight Blur
    img = img.filter(ImageFilter.GaussianBlur(radius=0.3))
    return img

# ============ DOCUMENT GENERATOR ============
def generate_enrollment_letter(first: str, last: str, school_data: Dict):
    W, H = 1000, 1300
    img = Image.new("RGB", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    try:
        font_header = ImageFont.truetype("/system/fonts/Roboto-Bold.ttf", 45)
        font_title = ImageFont.truetype("/system/fonts/Roboto-Bold.ttf", 28)
        font_body = ImageFont.truetype("/system/fonts/Roboto-Regular.ttf", 24)
        font_bold = ImageFont.truetype("/system/fonts/Roboto-Bold.ttf", 24)
    except:
        font_header = font_title = font_body = font_bold = ImageFont.load_default()

    # --- HEADER ---
    draw.text((50, 50), school_data["name"].upper(), fill=(0, 0, 0), font=font_header)
    draw.text((50, 110), "OFFICE OF THE REGISTRAR", fill=(80, 80, 80), font=font_title)
    draw.text((50, 150), school_data["city"], fill=(80, 80, 80), font=font_body)
    draw.line([(50, 190), (W-50, 190)], fill="black", width=3)

    # --- DATE & INFO ---
    today_str, start_str, end_str = get_current_dates()
    
    draw.text((50, 230), f"Date: {today_str}", fill="black", font=font_body)
    
    draw.text((50, 300), "RE: VERIFICATION OF ENROLLMENT", fill="black", font=font_bold)

    # --- BODY TEXT ---
    body_text = f"""To Whom It May Concern,

This letter certifies that {first} {last} (Student ID: {random.randint(90000000, 99999999)}) 
is officially enrolled as a full-time student at {school_data['name']} 
for the Spring {datetime.date.today().year} semester.

Term Information:
Start Date: {start_str}
End Date:   {end_str}

Academic Standing: Good Standing
Enrollment Status: Full-Time (12+ Credits)
Tuition Status:    PAID IN FULL

This document is provided at the student's request for verification 
purposes and serves as official proof of enrollment.
"""
    y = 360
    for line in body_text.split("\n"):
        draw.text((50, y), line, fill="black", font=font_body)
        y += 40

    # --- SIGNATURE ---
    y += 80
    draw.text((50, y), "Sincerely,", fill="black", font=font_body)
    y += 60
    
    # Fake Signature (Script style line)
    x_sig = 50
    y_sig = y + 10
    prev_x, prev_y = x_sig, y_sig
    for i in range(150):
        new_x = prev_x + 2
        new_y = y_sig + random.randint(-10, 10)
        draw.line([(prev_x, prev_y), (new_x, new_y)], fill="blue", width=2)
        prev_x, prev_y = new_x, new_y

    draw.text((50, y+50), "Sarah Jenkins", fill="black", font=font_bold)
    draw.text((50, y+85), "University Registrar", fill="black", font=font_body)

    # --- FOOTER ---
    draw.text((W//2, H-50), "Official Seal - Do Not Copy", fill="gray", font=font_body, anchor="mm")

    # === APPLY SCAN EFFECT ===
    # This makes the image look "dirty" and scanned, which passes filters better
    img = apply_scan_effect(img)

    return img

# ============ UPLOAD HELPER ============
def upload_file(file_bytes: bytes, filename: str) -> str:
    try:
        r = httpx.post("https://0x0.st", files={'file': (filename, file_bytes, 'image/png')}, timeout=30)
        if r.status_code == 200: return r.text.strip()
    except: pass
    try:
        r = httpx.put(f"https://transfer.sh/{filename}", content=file_bytes, timeout=30)
        if r.status_code == 200: return r.text.strip()
    except: pass
    return None

# ============ MAIN ============
class GeminiVerifier:
    def __init__(self, url: str):
        self.url = url
        self.vid = self._parse_id(url)
        self.client = httpx.Client(timeout=30)
    
    @staticmethod
    def _parse_id(url: str) -> Optional[str]:
        match = re.search(r"verificationId=([a-f0-9]+)", url, re.IGNORECASE)
        return match.group(1) if match else None
    
    def _request(self, method: str, endpoint: str, body: Dict = None) -> Tuple[Dict, int]:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        try:
            resp = self.client.request(method, f"{SHEERID_API_URL}{endpoint}", json=body, headers=headers)
            try: return resp.json(), resp.status_code
            except: return {}, resp.status_code
        except: return {}, 500

    def _upload_s3(self, url: str, data: bytes) -> bool:
        try:
            resp = self.client.put(url, content=data, headers={"Content-Type": "image/png"}, timeout=60)
            return 200 <= resp.status_code < 300
        except: return False

    def verify(self):
        if not self.vid:
            print("❌ Invalid Link")
            return
            
        print("\n   🚀 ভেরিফিকেশন শুরু হচ্ছে (Enrollment Letter Mode)...")
        
        # 1. Check
        data, status = self._request("GET", f"/verification/{self.vid}")
        current_step = data.get("currentStep", "UNKNOWN")
        
        if status != 200:
            print("   ❌ সার্ভার রেসপন্স করছে না।")
            return

        # 2. Identity
        first, last = generate_name()
        school_data = select_university()
        email = generate_email(first, last, school_data["domain"])
        # Consistent DOB
        dob = f"{datetime.date.today().year - 20}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        
        print(f"   👤 {first} {last}")
        print(f"   🏫 {school_data['name']}")
        print(f"   📄 ডক টাইপ: Registrar Verification Letter")

        # 3. Submit Info
        if current_step == "collectStudentPersonalInfo":
            print("   ▶ ধাপ ১: তথ্য জমা দেওয়া হচ্ছে...")
            body = {
                "firstName": first, "lastName": last, "birthDate": dob,
                "email": email,
                "organization": {"id": school_data["id"], "idExtended": school_data["idExtended"], "name": school_data["name"]},
                "deviceFingerprintHash": generate_fingerprint(),
                "metadata": {"verificationId": self.vid}
            }
            res, st = self._request("POST", f"/verification/{self.vid}/step/collectStudentPersonalInfo", body)
            if st == 200: current_step = res.get("currentStep", "")
            else: 
                print(f"   ❌ সাবমিট ফেইলড: {res}")
                return

        # 4. Generate & Upload
        if current_step in ["docUpload", "sso"]:
            if current_step == "sso":
                self._request("DELETE", f"/verification/{self.vid}/step/sso")
            
            print("   ▶ ধাপ ২: 'Scan Effect' সহ ডকুমেন্ট তৈরি হচ্ছে...")
            img = generate_enrollment_letter(first, last, school_data)
            
            buf = BytesIO()
            img.save(buf, format="PNG")
            doc_bytes = buf.getvalue()
            
            # Link for user
            link = upload_file(doc_bytes, "verification_letter.png")
            if link: print(f"   🔗 প্রিভিউ লিংক: {link}")
            
            # SheerID Upload
            print("   ... SheerID সার্ভারে আপলোড হচ্ছে ...")
            upload_body = {"files": [{"fileName": "letter.png", "mimeType": "image/png", "fileSize": len(doc_bytes)}]}
            res, st = self._request("POST", f"/verification/{self.vid}/step/docUpload", upload_body)
            
            if res.get("documents"):
                s3_url = res["documents"][0].get("uploadUrl")
                if self._upload_s3(s3_url, doc_bytes):
                    self._request("POST", f"/verification/{self.vid}/step/completeDocUpload")
                    print("   🎉 সফল! 'Enrollment Letter' জমা দেওয়া হয়েছে।")
                else: print("   ❌ আপলোড ফেইলড।")
            else: print("   ❌ আপলোড লিংক পাওয়া যায়নি।")

if __name__ == "__main__":
    url = input("🔗 SheerID Link: ").strip()
    if "sheerid" in url:
        v = GeminiVerifier(url)
        v.verify()
    else:
        print("❌ ভুল লিংক")
