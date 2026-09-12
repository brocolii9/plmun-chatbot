import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./plmun.db")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-do-not-use-in-prod")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.30"))

REGISTRAR_REFERRAL_EN = (
    "I'm sorry, I don't have a verified answer for that in my knowledge base, "
    "so I won't guess. Please contact the PLMun Registrar's Office directly:\n"
    " 2nd Floor, Admin Building, Pamantasan ng Lungsod ng Muntinlupa\n"
    " (02) 8809-0000 loc. 123\n"
    " registrar@plmun.edu.ph\n"
    " Mon-Fri, 8:00 AM - 5:00 PM"
)

REGISTRAR_REFERRAL_FIL = (
    "Paumanhin, wala akong beripikadong sagot diyan sa aking knowledge base, "
    "kaya hindi ako manghuhula. Mangyaring makipag-ugnayan nang direkta sa "
    "Registrar's Office ng PLMun:\n"
    " 2nd Floor, Admin Building, Pamantasan ng Lungsod ng Muntinlupa\n"
    " (02) 8809-0000 loc. 123\n"
    " registrar@plmun.edu.ph\n"
    " Lunes-Biyernes, 8:00 AM - 5:00 PM"
)