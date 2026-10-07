import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./plmun.db")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-do-not-use-in-prod")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.20"))

REGISTRAR_REFERRAL_EN = (
    "I'm sorry, I don't have a verified answer for that in my knowledge base, "
    "so I won't guess. Please contact the PLMun Office of the University Registrar:\n"
    "1st Floor, Student Center Building, PLMun, University Road, Poblacion, Muntinlupa City\n"
    "8659-2075 local 205\n"
    "For current schedules and service-specific requirements, please check official PLMun announcements."
)

REGISTRAR_REFERRAL_FIL = (
    "Paumanhin, wala akong beripikadong sagot diyan sa aking knowledge base, "
    "kaya hindi ako manghuhula. Makipag-ugnayan sa PLMun Office of the University Registrar:\n"
    "1st Floor, Student Center Building, PLMun, University Road, Poblacion, Muntinlupa City\n"
    "8659-2075 local 205\n"
    "Para sa kasalukuyang schedule at service-specific requirements, tingnan ang official PLMun announcements."
)

# --- Admin seed credentials (change in production) ---
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@plmun.edu.ph")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")