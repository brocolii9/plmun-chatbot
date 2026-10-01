"""
Seeds the knowledge base + intents on first boot.

16 registrar intents, 77 sample utterances in total.
COG = Certificate of Grades, COM = Certificate of Matriculation.
Answers marked [TODO: ...] are placeholders: confirm them with the
PLMun Registrar's Office (or the Citizen's Charter) and replace the
text BEFORE demo/defense.
"""

import json
from datetime import datetime
from sqlalchemy.orm import Session
from .models import KnowledgeBase, Intent

SEED = [
    (
        "enrollment_procedure", "enrollment",
        "What are the steps for enrollment?",
        "Enrollment steps (continuing students):\n1. Log in to the PLMun Student Portal.\n2. Settle any outstanding balance at the Cashier.\n3. Proceed to your College/Department for advising and section assignment.\n4. Encode your subjects and confirm your schedule.\n5. Print and keep your Certificate of Registration (COR).",
        "Mga hakbang sa enrollment (continuing students):\n1. Mag-log in sa PLMun Student Portal.\n2. Bayaran ang anumang natitirang balanse sa Cashier.\n3. Pumunta sa inyong College/Department para sa advising at section assignment.\n4. I-encode ang mga subjects at kumpirmahin ang schedule.\n5. I-print at itago ang Certificate of Registration (COR).",
        [
            "how do i enroll this semester",
            "paano mag-enroll ngayong semester",
            "what are the steps for enrollment",
            "ano ang proseso ng enrollment",
            "enrollment process for continuing students",
        ],
    ),
    (
        "enrollment_requirements", "enrollment",
        "What are the requirements for enrollment?",
        "Enrollment requirements:\n- Fully accomplished Enrollment Form\n- Current COR or TOR\n- Good Moral Certificate\n- 2x2 ID picture\n- Proof of payment\n- For freshmen: Form 138 and NCAE result\n- For transferees: Transfer Credentials / Honorable Dismissal and TOR from your previous school\n[TODO: confirm the full list for freshmen and transferees with the Registrar]",
        "Mga kailangan sa enrollment:\n- Kumpletong Enrollment Form\n- Kasalukuyang COR o TOR\n- Good Moral Certificate\n- 2x2 ID picture\n- Patunay ng bayad\n- Para sa freshmen: Form 138 at NCAE result\n- Para sa transferees: Transfer Credentials / Honorable Dismissal at TOR mula sa dating paaralan\n[TODO: kumpirmahin ang buong listahan sa Registrar]",
        [
            "what documents do i need to enroll",
            "ano ang mga requirements sa enrollment",
            "requirements for new freshmen",
            "mga kailangan ng transferee para mag-enroll",
            "what do transferees need to submit",
        ],
    ),
    (
        "add_drop_change_subjects", "enrollment",
        "How do I add, drop, or change a subject?",
        "To add, drop, or change a subject:\n1. Get the Adding/Dropping/Changing of Subjects form from your College/Department.\n2. Have it approved by your Dean/Adviser.\n3. Submit the approved form to the Registrar's Office within the prescribed period.\n[TODO: confirm form name, approvals, fees, and deadline]",
        "Para mag-add, mag-drop, o magpalit ng subject:\n1. Kumuha ng form para sa Adding/Dropping/Changing of Subjects sa inyong College/Department.\n2. Ipa-approve sa Dean/Adviser.\n3. Isumite ang approved form sa Registrar's Office sa loob ng itinakdang panahon.\n[TODO: kumpirmahin ang pangalan ng form, approvals, bayad, at deadline]",
        [
            "how do i add a subject",
            "paano mag-drop ng subject",
            "can i change my subjects after enrollment",
            "pwede pa bang magpalit ng subject",
            "process for adding and dropping subjects",
        ],
    ),
    (
        "leave_of_absence_shifting", "policy",
        "How do I apply for a leave of absence, shift programs, or withdraw?",
        "Shifting:\n1. Secure a Shift Form from your current College.\n2. Get recommendation from your Dean/Chair.\n3. Get acceptance from the receiving College.\n4. Submit the form to the Registrar.\nShifting is only allowed within the prescribed period.\nLeave of absence / withdrawal: file a written request at the Registrar's Office. [TODO: confirm LOA and withdrawal requirements and deadlines]",
        "Shifting:\n1. Kumuha ng Shift Form sa kasalukuyang College.\n2. Kunin ang rekomendasyon ng Dean/Chair.\n3. Kunin ang pagtanggap ng lilipatang College.\n4. Isumite sa Registrar.\nPinapayagan lamang sa itinakdang panahon.\nLeave of absence / pag-withdraw: mag-file ng written request sa Registrar's Office. [TODO: kumpirmahin ang requirements at deadline ng LOA at withdrawal]",
        [
            "how do i apply for a leave of absence",
            "paano mag-shift ng program",
            "i want to withdraw from the university",
            "paano mag-apply ng LOA",
            "requirements for shifting courses",
        ],
    ),
    (
        "tor_request", "documents",
        "How do I request a Transcript of Records (TOR)?",
        "To request a TOR:\n1. Go to the Registrar's Office and accomplish the Request Form.\n2. Present a valid ID.\n3. Pay the fee at the Cashier.\n4. Return the receipt to the Registrar for your claim stub.\nProcessing time: 5-10 working days.\n[TODO: confirm steps and processing time]",
        "Para humingi ng TOR:\n1. Pumunta sa Registrar's Office at sagutan ang Request Form.\n2. Magpakita ng valid ID.\n3. Magbayad ng kaukulang bayad sa Cashier.\n4. Ibalik ang resibo sa Registrar para sa claim stub.\nProcessing time: 5-10 working days.\n[TODO: kumpirmahin ang mga hakbang at processing time]",
        [
            "how do i request my transcript of records",
            "paano kumuha ng tor",
            "where can i get my tor",
            "gusto kong mag-request ng transcript of records",
            "steps to claim my tor",
        ],
    ),
    (
        "certification_request", "documents",
        "How do I request a certification (Certificate of Enrollment, Grades, etc.)?",
        "For certifications (Certificate of Enrollment, Certificate of Grades, Certificate of Registration, etc.):\n1. Accomplish the Document Request Form at the Registrar's Office.\n2. Present a valid ID.\n3. Pay the fee at the Cashier.\n4. Keep your claim stub.\n[TODO: confirm the list of available certifications]",
        "Para sa mga certification (Certificate of Enrollment, Certificate of Grades, Certificate of Registration, atbp.):\n1. Sagutan ang Document Request Form sa Registrar's Office.\n2. Magpakita ng valid ID.\n3. Magbayad sa Cashier.\n4. Itago ang claim stub.\n[TODO: kumpirmahin ang listahan ng mga available na certification]",
        [
            "how do i get a certificate of enrollment",
            "paano kumuha ng certificate of enrollment",
            "i need a certification from the registrar",
            "paano mag-request ng certification",
            "where do i request a certificate of registration",
        ],
    ),
    (
        "transfer_credentials", "documents",
        "How do I get Honorable Dismissal / Transfer Credentials?",
        "To get Transfer Credentials (Honorable Dismissal):\n1. File a request at the Registrar's Office.\n2. Submit your clearance.\n3. Pay the fee at the Cashier and present the receipt.\n4. Claim your documents on the release date.\n[TODO: confirm requirements, fee, and release time]",
        "Para kumuha ng Transfer Credentials (Honorable Dismissal):\n1. Mag-file ng request sa Registrar's Office.\n2. Isumite ang inyong clearance.\n3. Magbayad sa Cashier at ipakita ang resibo.\n4. Kunin ang mga dokumento sa petsa ng release.\n[TODO: kumpirmahin ang requirements, bayad, at oras ng release]",
        [
            "how do i get honorable dismissal",
            "paano kumuha ng transfer credentials",
            "i am transferring to another school, what do i need from the registrar",
            "lilipat ako ng school, ano ang kukunin ko sa registrar",
        ],
    ),
    (
        "document_fees_processing_time", "documents",
        "How much are document fees and how long is processing?",
        "Fees and processing time depend on the document. For example, a TOR usually takes 5-10 working days. Fees are paid at the Cashier, and the release date is written on your claim stub.\n[TODO: add the official fee and processing time per document]",
        "Nag-iiba ang bayad at processing time depende sa dokumento. Halimbawa, ang TOR ay karaniwang 5-10 working days. Ang bayad ay sa Cashier, at nakasulat sa claim stub ang petsa ng release.\n[TODO: ilagay ang opisyal na bayad at processing time kada dokumento]",
        [
            "how much is the fee for documents",
            "magkano ang bayad sa mga dokumento",
            "how long before my request is released",
            "gaano katagal ang processing ng request",
            "when can i claim my requested document",
        ],
    ),
    (
        "correction_of_records", "policy",
        "How do I correct my records or complete an INC grade?",
        "To correct your student records (name, birthdate, grades):\n1. File a written request at the Registrar's Office.\n2. Attach supporting documents (e.g., PSA Birth Certificate for name or birthdate corrections).\n3. For grade errors or INC completion, get the instructor's and Dean's approval.\nIf a grade is missing, file a Grade Inquiry at the Registrar.\n[TODO: confirm requirements and deadlines]",
        "Para ipa-correct ang student records (pangalan, birthdate, grades):\n1. Mag-file ng written request sa Registrar's Office.\n2. Ilakip ang supporting documents (hal. PSA Birth Certificate para sa pangalan o birthdate).\n3. Para sa error sa grades o pag-complete ng INC, kailangan ang approval ng instructor at Dean.\nKung may kulang na grade, mag-file ng Grade Inquiry sa Registrar.\n[TODO: kumpirmahin ang requirements at deadline]",
        [
            "how do i correct my name in my records",
            "paano ipa-correct ang birthdate sa records ko",
            "there is an error in my grades",
            "paano mag-complete ng incomplete grade",
            "request for correction of student records",
        ],
    ),
    (
        "graduation_requirements", "graduation",
        "What are the graduation requirements?",
        "Graduation requirements:\n- Completed all academic units\n- Cleared of all financial obligations\n- Submitted TOR, Good Moral, Clearance Form\n- Applied for graduation within the prescribed period\n- Attended the graduation orientation",
        "Mga kailangan para makapagtapos:\n- Natapos ang lahat ng units\n- Malinis sa financial obligations\n- Naisumite ang TOR, Good Moral, Clearance Form\n- Nag-apply ng graduation sa panahon\n- Dumalo sa graduation orientation",
        [
            "what are the requirements for graduation",
            "paano mag-apply para sa graduation",
            "what do i need to graduate",
            "ano ang kailangan para makapagtapos",
        ],
    ),
    (
        "diploma_and_clearance", "graduation",
        "How do I claim my diploma and get my clearance?",
        "Clearance and diploma:\n1. Secure your Clearance Form and have it signed by all required offices.\n2. Submit the completed clearance to the Registrar's Office.\n3. Claim your diploma on the release date announced by the Registrar.\n[TODO: confirm clearance signatories and diploma release schedule]",
        "Clearance at diploma:\n1. Kumuha ng Clearance Form at ipapirma sa lahat ng kailangang opisina.\n2. Isumite ang kumpletong clearance sa Registrar's Office.\n3. Kunin ang diploma sa petsa ng release na iaanunsyo ng Registrar.\n[TODO: kumpirmahin ang mga pipirma sa clearance at schedule ng diploma release]",
        [
            "how do i claim my diploma",
            "paano kumuha ng clearance",
            "when can i get my diploma",
            "clearance requirements for graduating students",
        ],
    ),
    (
        "registrar_info", "general",
        "Where is the Registrar's Office and what are its office hours?",
        "[TODO: add the Registrar's Office location, office hours, and contact details (phone/email)]",
        "[TODO: ilagay ang lokasyon, office hours, at contact details (phone/email) ng Registrar's Office]",
        [
            "what are the registrar's office hours",
            "saan ang registrar's office",
            "where is the registrar located",
            "paano makontak ang registrar",
            "anong oras bukas ang registrar",
        ],
    ),
    (
        "scholarship_concerns", "scholarship",
        "What scholarships are available and how do I apply?",
        "PLMun scholarship programs:\n- PLMun Academic Scholarship (Dean's Lister)\n- PLMun Grant-in-Aid\n- CHED, TESDA, DOST-SEI\n- LGU / City Government scholarships\nGeneral requirements:\n1. Scholarship Application Form\n2. Certified True Copy of Grades / TOR\n3. Certificate of Indigency (if applicable)\n4. Barangay Clearance and valid ID\n5. Proof of enrollment (COR)\nVisit the Scholarship Office for deadlines.\n[TODO: confirm scholarship list, requirements, and deadlines]",
        "Mga scholarship ng PLMun:\n- PLMun Academic Scholarship (Dean's Lister)\n- PLMun Grant-in-Aid\n- CHED, TESDA, DOST-SEI\n- LGU / City Government scholarships\nMga kailangan:\n1. Scholarship Application Form\n2. Certified True Copy of Grades / TOR\n3. Certificate of Indigency (kung applicable)\n4. Barangay Clearance at valid ID\n5. Proof of enrollment (COR)\nBisitahin ang Scholarship Office para sa deadlines.\n[TODO: kumpirmahin ang listahan, requirements, at deadlines]",
        [
            "what scholarships are available",
            "paano mag-apply ng scholarship",
            "requirements for scholarship",
            "may scholarship ba ang plmun",
            "ano ang mga kailangan para sa scholarship",
        ],
    ),
    (
        "grade_concern", "policy",
        "Where can I check my grades and what if there is a problem?",
        "Grades are in the PLMun Student Portal:\n1. Log in.\n2. Go to 'Grades' or 'Academic Records'.\n3. Select the semester.\nIf a grade is missing or you have a concern, file a Grade Inquiry at the Registrar's Office.\n[TODO: confirm Grade Inquiry process]",
        "Nasa PLMun Student Portal ang grades:\n1. Mag-log in.\n2. Pumunta sa 'Grades' o 'Academic Records'.\n3. Piliin ang semester.\nKung may kulang na grade o may concern, mag-file ng Grade Inquiry sa Registrar's Office.\n[TODO: kumpirmahin ang proseso ng Grade Inquiry]",
        [
            "where can i check my grades",
            "paano makita ang grades ko",
            "my grade is missing",
            "wala pa ang grade ko sa portal",
            "who do i ask about my grade concern",
        ],
    ),
    (
        "cog_request", "documents",
        "How do I get a Certificate of Grades (COG)?",
        "To request a Certificate of Grades (COG):\n1. File a request at the Registrar's Office.\n2. Present your student ID.\n3. Pay the fee at the Cashier and submit the receipt.\nProcessing time: 3-5 working days.\n[TODO: confirm steps, fee, and processing time]",
        "Para kumuha ng Certificate of Grades (COG):\n1. Mag-file ng request sa Registrar's Office.\n2. Magpakita ng student ID.\n3. Magbayad sa Cashier at isumite ang resibo.\nProcessing time: 3-5 working days.\n[TODO: kumpirmahin ang mga hakbang, bayad, at processing time]",
        [
            "how do i get my certificate of grades",
            "paano kumuha ng cog",
            "cog request process",
            "gusto kong mag-request ng cog",
            "how long does it take to get my cog",
        ],
    ),
    (
        "com_request", "documents",
        "How do I get a Certificate of Matriculation (COM)?",
        "To request a Certificate of Matriculation (COM), go to the Registrar's Office.\n[TODO: add the steps, requirements, fee, and processing time for requesting a COM]",
        "Para kumuha ng Certificate of Matriculation (COM), pumunta sa Registrar's Office.\n[TODO: ilagay ang mga hakbang, requirements, bayad, at processing time sa pagkuha ng COM]",
        [
            "how do i get my certificate of matriculation",
            "paano kumuha ng com",
            "com request",
            "gusto kong mag-request ng certificate of matriculation",
            "magkano ang com",
        ],
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