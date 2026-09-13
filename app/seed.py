"""
Seeds the knowledge base + intents on first boot.
"""

import json
from datetime import datetime
from sqlalchemy.orm import Session
from .models import KnowledgeBase, Intent

SEED = [
    (
        "enrollment_steps", "enrollment",
        "What are the steps for enrollment?",
        "Enrollment steps:\n1. Log in to the PLMun Student Portal.\n2. Settle any outstanding balance at the Cashier.\n3. Proceed to your College/Department for advising and section assignment.\n4. Encode your subjects and confirm your schedule.\n5. Print and keep your Certificate of Registration (COR).",
        "Mga hakbang sa enrollment:\n1. Mag-log in sa PLMun Student Portal.\n2. Bayaran ang anumang natitirang balanse sa Cashier.\n3. Pumunta sa inyong College/Department para sa advising at section assignment.\n4. I-encode ang mga subjects at kumpirmahin ang schedule.\n5. I-print at itago ang Certificate of Registration (COR).",
        ["how do i enroll", "paano mag enroll", "enrollment steps", "paano mag-enroll ngayong semester", "steps for enrollment", "enrollment process", "how to enroll this semester"],
    ),
    (
        "enrollment_requirements", "enrollment",
        "What are the requirements for enrollment?",
        "Enrollment requirements:\n- Fully accomplished Enrollment Form\n- Current COR or TOR\n- Good Moral Certificate\n- 2x2 ID picture\n- Proof of payment\n- For freshmen: Form 138 and NCAE result",
        "Mga kailangan sa enrollment:\n- Kumpletong Enrollment Form\n- Kasalukuyang COR o TOR\n- Good Moral Certificate\n- 2x2 ID picture\n- Patunay ng bayad\n- Para sa freshmen: Form 138 at NCAE result",
        ["what are the requirements for enrollment", "ano requirements sa enrollment", "enrollment requirements", "requirements needed to enroll", "what do i need to enroll"],
    ),
    (
        "tor_request", "documents",
        "How do I request a Transcript of Records (TOR)?",
        "To request a TOR:\n1. Go to the Registrar's Office and accomplish the Request Form.\n2. Present a valid ID.\n3. Pay the fee at the Cashier.\n4. Return the receipt to the Registrar for your claim stub.\nProcessing time: 5-10 working days.",
        "Para humingi ng TOR:\n1. Pumunta sa Registrar's Office at sagutan ang Request Form.\n2. Magpakita ng valid ID.\n3. Magbayad ng kaukulang bayad sa Cashier.\n4. Ibalik ang resibo sa Registrar para sa claim stub.\nProcessing time: 5-10 working days.",
        ["how do i request tor", "paano kumuha ng tor", "tor request process", "transcript of records request", "i need my tor", "how to get my transcript"],
    ),
    (
        "cog_request", "documents",
        "How do I get a Certificate of Grades (COG)?",
        "To request a COG:\n1. File a request at the Registrar's Office.\n2. Present your student ID.\n3. Pay the fee at the Cashier and submit the receipt.\nProcessing time: 3-5 working days.",
        "Para kumuha ng COG:\n1. Mag-file ng request sa Registrar's Office.\n2. Magpakita ng student ID.\n3. Magbayad sa Cashier at isumite ang resibo.\nProcessing time: 3-5 working days.",
        ["how to get cog", "certificate of grades request", "paano kumuha ng cog", "cog request"],
    ),
    (
        "certificate_request", "documents",
        "How do I request a certificate or other document?",
        "For certificates (Good Moral, Enrollment, Graduation, etc.):\n1. Accomplish the Document Request Form.\n2. Present a valid ID.\n3. Pay the fee at the Cashier.\n4. Keep your claim stub.",
        "Para sa mga certificate:\n1. Sagutan ang Document Request Form.\n2. Magpakita ng valid ID.\n3. Magbayad sa Cashier.\n4. Itago ang claim stub.",
        ["how do i request a document", "paano kumuha ng certificate", "certificate request", "i need a certificate"],
    ),
    (
        "scholarship_list", "scholarship",
        "What scholarships are available?",
        "PLMun scholarship programs:\n- PLMun Academic Scholarship (Dean's Lister)\n- PLMun Grant-in-Aid\n- CHED, TESDA, DOST-SEI\n- LGU / City Government scholarships\nVisit the Scholarship Office for deadlines.",
        "Mga scholarship ng PLMun:\n- PLMun Academic Scholarship\n- PLMun Grant-in-Aid\n- CHED, TESDA, DOST-SEI\n- LGU scholarships\nBisitahin ang Scholarship Office.",
        ["what scholarships are available", "ano ang mga scholarship", "list of scholarships", "available scholarships", "scholarship programs"],
    ),
    (
        "scholarship_requirements", "scholarship",
        "How do I apply for a scholarship?",
        "General requirements:\n1. Scholarship Application Form\n2. Certified True Copy of Grades / TOR\n3. Certificate of Indigency (if applicable)\n4. Barangay Clearance and valid ID\n5. Proof of enrollment (COR)",
        "Mga kailangan:\n1. Scholarship Application Form\n2. Certified True Copy of Grades / TOR\n3. Certificate of Indigency\n4. Barangay Clearance at valid ID\n5. Proof of enrollment (COR)",
        ["scholarship requirements", "ano requirements sa scholarship", "how to apply for scholarship", "paano mag apply ng scholarship"],
    ),
    (
        "graduation_requirements", "graduation",
        "What are the graduation requirements?",
        "Graduation requirements:\n- Completed all academic units\n- Cleared of all financial obligations\n- Submitted TOR, Good Moral, Clearance Form\n- Applied for graduation within the prescribed period\n- Attended the graduation orientation",
        "Mga kailangan para makapagtapos:\n- Natapos ang lahat ng units\n- Malinis sa financial obligations\n- Naisumite ang TOR, Good Moral, Clearance Form\n- Nag-apply ng graduation sa panahon\n- Dumalo sa graduation orientation",
        ["graduation requirements", "ano requirements para mag graduate", "what do i need to graduate", "requirements for graduation"],
    ),
    (
        "class_schedule", "schedule",
        "Where can I see my class schedule?",
        "Your class schedule is in the PLMun Student Portal:\n1. Log in.\n2. Go to 'My Schedule' or 'Enrolled Subjects'.\n3. Print or save your schedule.\nFor conflicts, contact your College/Department.",
        "Nasa PLMun Student Portal ang class schedule:\n1. Mag-log in.\n2. Pumunta sa 'My Schedule'.\n3. I-print o i-save.\nPara sa conflict, makipag-ugnayan sa College/Department.",
        ["where can i see my class schedule", "paano makita ang schedule", "class schedule", "where to check schedule"],
    ),
    (
        "academic_calendar", "schedule",
        "What is the academic calendar?",
        "The PLMun academic calendar is posted on the official website and Student Portal. It includes enrollment periods, start/end of classes, exams, and graduation dates.",
        "Ang academic calendar ng PLMun ay nasa official website at Student Portal. Kasama ang enrollment periods, simula/katapusan ng klase, exams, at graduation.",
        ["academic calendar", "when is enrollment period", "ano ang academic calendar", "school calendar", "kelan ang enrollment"],
    ),
    (
        "grades_inquiry", "policy",
        "Where can I check my grades?",
        "Grades are in the PLMun Student Portal:\n1. Log in.\n2. Go to 'Grades' or 'Academic Records'.\n3. Select the semester.\nIf a grade is missing, file a Grade Inquiry at the Registrar.",
        "Nasa PLMun Student Portal ang grades:\n1. Mag-log in.\n2. Pumunta sa 'Grades'.\n3. Piliin ang semester.\nKung may kulang, mag-file ng Grade Inquiry.",
        ["where can i check my grades", "paano makita ang grades", "how to view grades", "grades online", "checking grades online"],
    ),
    (
        "shifting_course", "policy",
        "How do I shift to another course?",
        "To shift:\n1. Secure a Shift Form from your current College.\n2. Get recommendation from your Dean/Chair.\n3. Get acceptance from the receiving College.\n4. Submit the form to the Registrar.\nShifting is only allowed within the prescribed period.",
        "Para mag-shift:\n1. Kumuha ng Shift Form sa College.\n2. Kunin ang rekomendasyon ng Dean/Chair.\n3. Kunin ang pagtanggap ng lilipatang College.\n4. Isumite sa Registrar.\nPinapayagan lamang sa itinakdang panahon.",
        ["how to shift course", "paano mag shift ng course", "shifting requirements", "i want to change my course"],
    ),
]

def seed_admin_if_empty(db: Session) -> bool:
    """Create a default super_admin if no admin exists."""
    from .models import AdminUser
    from .auth import hash_password
    from .config import ADMIN_EMAIL, ADMIN_PASSWORD

    if db.query(AdminUser).count() > 0:
        return False

    admin = AdminUser(
        full_name="PLMun Super Admin",
        email=ADMIN_EMAIL.lower(),
        password_hash=hash_password(ADMIN_PASSWORD),
        role="super_admin",
    )
    db.add(admin)
    db.commit()
    print(f"[seed] Created default admin: {ADMIN_EMAIL}")
    return True


def seed_if_empty(db: Session) -> bool:
    existing = db.query(KnowledgeBase).count()
    if existing > 0:
        return False

    for name, category, question, ans_en, ans_fil, utterances in SEED:
        kb = KnowledgeBase(
            category=category,
            question=question,
            answer_en=ans_en,
            answer_fil=ans_fil,
            last_updated_at=datetime.utcnow(),
        )
        db.add(kb)
        db.flush()

        intent = Intent(
            name=name,
            sample_utterances=json.dumps(utterances),
            kb_entry_id=kb.id,
        )
        db.add(intent)

    db.commit()
    return True