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
        "For enrollment procedures, please follow the latest official enrollment instructions issued by PLMun. The exact sequence of steps may vary depending on the enrollment period and the student's status. Please check the current PLMun enrollment announcement or confirm the procedure with the Registrar's Office or your College/Department.",
        "Para sa enrollment procedure, sundin ang pinakabagong opisyal na enrollment instructions ng PLMun. Maaaring mag-iba ang eksaktong pagkakasunod-sunod ng mga hakbang depende sa enrollment period at status ng estudyante. Tingnan ang kasalukuyang PLMun enrollment announcement o kumpirmahin ang proseso sa Registrar's Office o sa inyong College/Department.",
        [
            "how do i enroll this semester",
            "paano mag-enroll ngayong semester",
            "what are the steps for enrollment",
            "ano ang proseso ng enrollment",
            "enrollment process for continuing students",
            "how do i enroll",
            "how to enroll",
            "how can i enroll",
            "i want to enroll",
            "paano mag enroll",
            "paano ako mag enroll",
            "gusto kong mag enroll",
            "ano ang enrollment process",
            "what is the first step of enrollment",
            "where should i begin the enrollment process",
            "ano ang unang gagawin sa enrollment",
        ],
    ),
    (
        "enrollment_requirements", "enrollment",
        "What are the requirements for enrollment?",
        "Enrollment requirements may vary depending on the student's status, such as freshman, continuing student, or transferee. Students should follow the current enrollment checklist and official instructions issued by PLMun. Additional documents may be required depending on the student's classification. For the latest and complete list of requirements, please check the official PLMun enrollment announcement or confirm with the Registrar's Office.",
        "Maaaring magkaiba ang enrollment requirements depende sa status ng estudyante, gaya ng freshman, continuing student, o transferee. Sundin ang kasalukuyang enrollment checklist at opisyal na instructions ng PLMun. Maaaring may karagdagang dokumentong kailangan depende sa classification ng estudyante. Para sa pinakabago at kumpletong listahan ng requirements, tingnan ang opisyal na PLMun enrollment announcement o kumpirmahin sa Registrar's Office.",
        [
            "what documents do i need to enroll",
            "ano ang mga requirements sa enrollment",
            "requirements for new freshmen",
            "mga kailangan ng transferee para mag-enroll",
            "what do transferees need to submit",
            "which documents are required for enrollment",
            "what should i submit when enrolling",
            "enrollment documents needed for continuing students",
            "ano ang dapat dalhin sa enrollment",
            "ano ang dapat ipasa sa pag enroll",
            "mga dokumento para makapag enroll",
            "list of enrollment requirements",
            "which papers are required when enrolling",
            "what should students prepare before enrollment",
            "what requirements should i bring for enrollment",
        ],
    ),
    (
        "add_drop_change_subjects", "enrollment",
        "How do I add, drop, or change a subject?",
        "To add, drop, or change a subject, follow the current procedure provided by your College/Department and the Registrar's Office. You may be required to submit the appropriate request form and obtain the necessary approval before the request can be processed. Requests must be completed within the official period announced by PLMun. For the exact form, approvals, and deadline, please check the latest university guidelines.",
        "Para mag-add, mag-drop, o magpalit ng subject, sundin ang kasalukuyang proseso ng inyong College/Department at ng Registrar's Office. Maaaring kailanganing magsumite ng tamang request form at kumuha ng kinakailangang approval bago ma-process ang request. Dapat maisagawa ito sa loob ng opisyal na panahon na itinakda ng PLMun. Para sa eksaktong form, approvals, at deadline, tingnan ang pinakabagong university guidelines.",
        [
            "how do i add a subject",
            "paano mag-drop ng subject",
            "can i change my subjects after enrollment",
            "pwede pa bang magpalit ng subject",
            "process for adding and dropping subjects",
            "how can i drop a class",
            "i want to remove one subject",
            "can i add another subject to my schedule",
            "i want to add one more subject",
            "how do students add an extra class",
            "how can i change one of my classes",
            "gusto kong mag drop ng class",
            "paano mag add ng bagong subject",
            "magpapalit ako ng isang subject",
        ],
    ),
    (
        "leave_of_absence_shifting", "policy",
        "How do I apply for a leave of absence, shift programs, or withdraw?",
        "For leave of absence, shifting, or withdrawal concerns, please follow the latest official PLMun procedure for your specific request. Requirements, approvals, and deadlines may differ depending on the type of request and the student's situation. Please confirm the current requirements and procedure with the Registrar's Office or the appropriate College/Department before submitting a request.",
        "Para sa leave of absence, shifting, o withdrawal, sundin ang pinakabagong opisyal na proseso ng PLMun para sa inyong request. Maaaring magkaiba ang requirements, approvals, at deadlines depende sa uri ng request at sitwasyon ng estudyante. Kumpirmahin muna ang kasalukuyang requirements at proseso sa Registrar's Office o sa inyong College/Department bago magsumite ng request.",
        [
            "how do i apply for a leave of absence",
            "paano mag-shift ng program",
            "i want to withdraw from the university",
            "paano mag-apply ng LOA",
            "requirements for shifting courses",
            "how do i file an loa",
            "i need to request leave of absence",
            "can students take a temporary leave",
            "what is the loa process",
            "paano mag file ng loa",
            "gusto kong mag leave of absence",
            "paano mag withdraw sa university",
            "can i pause my studies for a semester",
            "i need to temporarily stop studying",
            "how do i withdraw from the university",
            "i want to withdraw from my program",
            "pwede bang huminto muna ng isang semester",
            "paano mag withdraw sa school",
            "i want to shift to another course",
            "paano mag shift ng course",
            "gusto ko lumipat ng program",
        ],
    ),
    (
        "tor_request", "documents",
        "How do I request a Transcript of Records (TOR)?",
        "To request a Transcript of Records (TOR), please follow the current document-request procedure provided by the PLMun Registrar's Office. The required documents, fees, and processing time should be confirmed through the latest official PLMun information because these details may change. Contact or visit the Registrar's Office for the current TOR request instructions.",
        "Para humiling ng Transcript of Records (TOR), sundin ang kasalukuyang document-request procedure ng PLMun Registrar's Office. Ang kinakailangang dokumento, bayad, at processing time ay dapat kumpirmahin sa pinakabagong opisyal na impormasyon ng PLMun dahil maaaring magbago ang mga ito. Makipag-ugnayan o pumunta sa Registrar's Office para sa kasalukuyang TOR request instructions.",
        [
            "how do i request my transcript of records",
            "paano kumuha ng tor",
            "where can i get my tor",
            "gusto kong mag-request ng transcript of records",
            "steps to claim my tor",
            "can i request a transcript",
            "where can i get a transcript of records",
            "i want to request my tor",
            "how can i claim a transcript",
            "gusto ko ng tor",
            "saan mag request ng tor",
            "transcript request process",
            "i need an academic transcript",
            "how can i get a copy of my transcript",
            "where can i request my academic records transcript",
            "saan pinoprocess ang tor",
        ],
    ),
    (
        "certification_request", "documents",
        "How do I request a certification (Certificate of Enrollment, Grades, etc.)?",
        "For certification requests, please follow the current procedure of the PLMun Registrar's Office. The available types of certification, requirements, fees, and processing times are not yet verified in this knowledge base and may change. Please confirm the specific certification you need and the latest requirements with the Registrar's Office.",
        "Para sa certification requests, sundin ang kasalukuyang proseso ng PLMun Registrar's Office. Ang mga available na uri ng certification, requirements, bayad, at processing time ay hindi pa beripikado sa knowledge base na ito at maaaring magbago. Kumpirmahin sa Registrar's Office ang partikular na certification na kailangan ninyo at ang pinakabagong requirements.",
        [
            "how do i get a certificate of enrollment",
            "paano kumuha ng certificate of enrollment",
            "i need a certification from the registrar",
            "paano mag-request ng certification",
            "where do i request a certificate of registration",
            "how do i request a certification",
            "where can i get a certificate of enrollment",
            "i need an enrollment certification for a requirement",
            "can the registrar issue proof of enrollment",
            "paano mag request ng certification",
            "saan kukuha ng certificate of enrollment",
            "kailangan ko ng proof of enrollment",
            "how can i get proof of enrollment",
            "i need proof of my current enrollment",
            "what document proves that a student is enrolled",
        ],
    ),
    (
        "transfer_credentials", "documents",
        "How do I get Honorable Dismissal / Transfer Credentials?",
        "For transfer credential requests, including documents needed when transferring to another school, please follow the current procedure of the PLMun Registrar's Office. The exact requirements, forms, fees, and processing time are not verified in this knowledge base and may change. Please confirm the latest instructions directly with the Registrar's Office before submitting your request.",
        "Para sa transfer credential requests, kabilang ang mga dokumentong kailangan kapag lilipat sa ibang paaralan, sundin ang kasalukuyang proseso ng PLMun Registrar's Office. Ang eksaktong requirements, forms, bayad, at processing time ay hindi pa beripikado sa knowledge base na ito at maaaring magbago. Kumpirmahin muna ang pinakabagong instructions sa Registrar's Office bago magsumite ng request.",
        [
            "how do i get honorable dismissal",
            "paano kumuha ng transfer credentials",
            "i am transferring to another school, what do i need from the registrar",
            "lilipat ako ng school, ano ang kukunin ko sa registrar",
            "what are the requirements for transferring out",
            "what document do i need when moving to another university",
            "can i request transfer credentials",
            "where do i get honorable dismissal",
            "lilipat ako sa ibang university",
            "ano ang kailangan kapag lilipat ng school",
            "paano mag request ng honorable dismissal",
            "transfer out requirements",
            "i plan to transfer to another college",
            "how do i transfer to a different university",
            "lilipat ako sa ibang college",
            "i am moving to another school",
            "where can i request honorable dismissal",
            "how do i get my honorable dismissal",
            "i need honorable dismissal for transferring",
        ],
    ),
    (
        "document_fees_processing_time", "documents",
        "How much are document fees and how long is processing?",
        "Document fees and processing times may vary depending on the type of document requested and the current Registrar procedures. The exact amounts and processing periods are not verified in this knowledge base. Please check the latest official PLMun information or confirm directly with the Registrar's Office before making a request or payment.",
        "Maaaring mag-iba ang bayad at processing time depende sa uri ng dokumentong hinihingi at sa kasalukuyang proseso ng Registrar. Ang eksaktong halaga at processing period ay hindi pa beripikado sa knowledge base na ito. Tingnan ang pinakabagong opisyal na impormasyon ng PLMun o direktang kumpirmahin sa Registrar's Office bago mag-request o magbayad.",
        [
            "how much is the fee for documents",
            "magkano ang bayad sa mga dokumento",
            "how long before my request is released",
            "gaano katagal ang processing ng request",
            "when can i claim my requested document",
            "what is the price of requesting a document",
            "how many days does document processing take",
            "when will my document be ready",
            "what are the registrar document fees",
            "magkano ang document request",
            "ilang araw bago makuha ang document",
            "kailan mare-release ang requested document",
            "how long is the processing time for school records",
            "when will requested records be released",
            "how many days before records are ready",
            "gaano katagal bago makuha ang records",
        ],
    ),
    (
        "correction_of_records", "policy",
        "How do I correct my records or complete an INC grade?",
        "For corrections to student records, such as an incorrect name, birth date, or other personal information, please contact the PLMun Registrar's Office and follow the current correction procedure. The supporting documents and approval requirements depend on the type of correction and are not verified in this knowledge base. Please confirm the exact requirements with the Registrar's Office.",
        "Para sa pagwawasto ng student records, gaya ng maling pangalan, birth date, o ibang personal na impormasyon, makipag-ugnayan sa PLMun Registrar's Office at sundin ang kasalukuyang correction procedure. Ang supporting documents at approval requirements ay depende sa uri ng correction at hindi pa beripikado sa knowledge base na ito. Kumpirmahin ang eksaktong requirements sa Registrar's Office.",
        [
            "how do i correct my name in my records",
            "paano ipa-correct ang birthdate sa records ko",
            "there is an error in my grades",
            "paano mag-complete ng incomplete grade",
            "request for correction of student records",
            "how do i fix my birth date in my record",
            "my personal information in the school record is incorrect",
            "i need to correct my student information",
            "there is a mistake in my school records",
            "mali ang birthday sa student record ko",
            "paano ayusin ang maling information sa records",
            "may mali sa personal details ko",
        ],
    ),
    (
        "graduation_requirements", "graduation",
        "What are the graduation requirements?",
        "For graduation requirements, students should follow the latest official PLMun guidelines for graduating students. The specific academic, documentary, and clearance requirements are not verified in this knowledge base and may vary depending on the student's program and status. Please confirm the current graduation requirements with the Registrar's Office or the appropriate College/Department.",
        "Para sa graduation requirements, sundin ang pinakabagong opisyal na guidelines ng PLMun para sa graduating students. Ang partikular na academic, documentary, at clearance requirements ay hindi pa beripikado sa knowledge base na ito at maaaring mag-iba depende sa program at status ng estudyante. Kumpirmahin ang kasalukuyang graduation requirements sa Registrar's Office o sa inyong College/Department.",
        [
            "what are the requirements for graduation",
            "paano mag-apply para sa graduation",
            "what do i need to graduate",
            "ano ang kailangan para makapagtapos",
            "what should i complete before graduation",
            "what are the requirements for graduating students",
            "how do i know if i can graduate",
            "what is the graduation application process",
            "ano ang mga requirements bago grumaduate",
            "ano pa ang kailangan ko bago graduation",
            "paano malaman kung qualified na akong grumaduate",
            "proseso ng application for graduation",
        ],
    ),
    (
        "diploma_and_clearance", "graduation",
        "How do I claim my diploma and get my clearance?",
        "For diploma and clearance concerns, please follow the current PLMun procedure for completing clearance and claiming a diploma. The required clearances, release schedule, documents, and other conditions are not verified in this knowledge base and may change. Please confirm the latest procedure with the Registrar's Office and the appropriate university offices.",
        "Para sa diploma at clearance concerns, sundin ang kasalukuyang proseso ng PLMun para sa pag-complete ng clearance at pag-claim ng diploma. Ang kinakailangang clearances, release schedule, documents, at iba pang kondisyon ay hindi pa beripikado sa knowledge base na ito at maaaring magbago. Kumpirmahin ang pinakabagong proseso sa Registrar's Office at sa mga kaukulang university offices.",
        [
            "how do i claim my diploma",
            "paano kumuha ng clearance",
            "when can i get my diploma",
            "clearance requirements for graduating students",
            "how can i get my clearance form",
            "what are the steps for completing clearance",
            "when will diplomas be released",
"where do graduating students claim their diploma",
"paano mag process ng clearance",
"saan kukunin ang clearance form",
"kailan makukuha ang diploma",
"saan ko kukunin ang diploma ko",
"what is the school clearance process",
"how do students complete clearance",
"what are the steps for clearance",
"ano ang proseso ng clearance",
        "how do graduates claim their diploma",
        "where should i claim my diploma",
        "what is the diploma claiming process",
        ],
    ),
    (
        "registrar_info", "general",
         "Where is the Registrar's Office and what are its office hours?",

        "The Office of the University Registrar maintains student records and handles "
        "enrollment-related procedures. According to the PLMun Citizen's Charter, the "
        "Office of the University Registrar is located at the 1st Floor, Student Center "
        "Building, PLMun, University Road, Poblacion, Muntinlupa City. "
        "You may contact the office at 8659-2075 local 205. "
        "For service-specific requirements or updated schedules, please check the latest "
        "PLMun Citizen's Charter or official university announcements.",

        "Ang Office of the University Registrar ang nangangasiwa sa student records at "
        "mga enrollment-related procedures. Ayon sa PLMun Citizen's Charter, matatagpuan "
        "ang Office of the University Registrar sa 1st Floor, Student Center Building, "
        "PLMun, University Road, Poblacion, Muntinlupa City. "
        "Maaaring makipag-ugnayan sa opisina sa 8659-2075 local 205. "
        "Para sa partikular na requirements o updated na schedule, tingnan ang pinakabagong "
        "PLMun Citizen's Charter o opisyal na university announcements.",
        [
            "what are the registrar's office hours",
            "saan ang registrar's office",
            "where is the registrar located",
            "paano makontak ang registrar",
            "anong oras bukas ang registrar",
            "how can i contact the registrar",
            "what is the registrar contact information",
            "what time does the registrar close",
            "where can i find the registrar office",
            "ano ang contact number ng registrar",
            "anong oras nagsasara ang registrar",
            "saan makikita ang registrar office",
        ],
    ),
    (
        "scholarship_concerns", "scholarship",
        "What scholarships are available and how do I apply?",
        "For scholarship concerns, please refer to the latest official PLMun scholarship announcements and requirements. Available scholarship programs, qualifications, application periods, and documentary requirements are not verified in this knowledge base and may change. Please contact the appropriate PLMun office for the current scholarship information and application procedure.",
        "Para sa scholarship concerns, tingnan ang pinakabagong opisyal na scholarship announcements at requirements ng PLMun. Ang available na scholarship programs, qualifications, application periods, at documentary requirements ay hindi pa beripikado sa knowledge base na ito at maaaring magbago. Makipag-ugnayan sa kaukulang PLMun office para sa kasalukuyang scholarship information at application procedure.",
        [
            "what scholarships are available",
            "paano mag-apply ng scholarship",
            "requirements for scholarship",
            "may scholarship ba ang plmun",
            "ano ang mga kailangan para sa scholarship",
            "how do students apply for scholarships",
"what is the scholarship application process",
"what are the scholarship qualifications",
"are there financial assistance programs for students",
"paano mag submit ng scholarship application",
"ano ang qualifications para sa scholarship",
"may financial assistance ba para sa students",
"how can i apply for scholarship assistance",
"i want to apply for a scholarship program",
"where can students submit a scholarship application",
"scholarship application requirements",
        ],
    ),
    (
        "grade_concern", "policy",
        "Where can I check my grades and what if there is a problem?",
        "For concerns about a missing, incorrect, or disputed grade, please follow the current PLMun procedure for grade concerns. The appropriate office or personnel and the documents required may depend on the specific case and are not verified in this knowledge base. Please confirm the proper procedure with your College/Department or the Registrar's Office.",
        "Para sa concern tungkol sa nawawala, mali, o disputed na grade, sundin ang kasalukuyang proseso ng PLMun para sa grade concerns. Maaaring magdepende sa partikular na kaso ang tamang office o personnel na lalapitan at ang mga dokumentong kailangan, at hindi pa beripikado ang mga ito sa knowledge base na ito. Kumpirmahin ang tamang proseso sa inyong College/Department o sa Registrar's Office.",
        [
            "where can i check my grades",
            "paano makita ang grades ko",
            "my grade is missing",
            "wala pa ang grade ko sa portal",
            "who do i ask about my grade concern",
            "there is a problem with my grade",
"my grade looks incorrect",
"why is my grade missing",
"who should i contact about an incorrect grade",
"may problema sa grade ko",
"bakit wala ang grade ko",
"sino ang kakausapin tungkol sa maling grade",
        ],
    ),
    (
        "cog_request", "documents",
        "How do I get a Certificate of Grades (COG)?",
        "For a Certificate of Grades (COG) request, please follow the current document-request procedure of the PLMun Registrar's Office. The exact requirements, fees, and processing time are not verified in this knowledge base and may change. Please confirm the latest COG request instructions with the Registrar's Office.",
        "Para sa Certificate of Grades (COG) request, sundin ang kasalukuyang document-request procedure ng PLMun Registrar's Office. Ang eksaktong requirements, bayad, at processing time ay hindi pa beripikado sa knowledge base na ito at maaaring magbago. Kumpirmahin ang pinakabagong COG request instructions sa Registrar's Office.",
        [
            "how do i get my certificate of grades",
            "paano kumuha ng cog",
            "cog request process",
            "gusto kong mag-request ng cog",
            "how long does it take to get my cog",
            "i want to request a certificate of grades",
"where can i request a cog",
"certificate of grades request",
"what are the requirements for getting a cog",
"kailangan ko ng certificate of grades",
"saan mag request ng cog",
"ano ang requirements para sa cog",
        ],
    ),
    (
        "com_request", "documents",
        "How do I get a Certificate of Matriculation (COM)?",
        "For a Certificate of Matriculation (COM) request, please follow the current document-request procedure of the PLMun Registrar's Office. The exact requirements, fees, and processing time are not verified in this knowledge base and may change. Please confirm the latest COM request instructions with the Registrar's Office.",
        "Para sa Certificate of Matriculation (COM) request, sundin ang kasalukuyang document-request procedure ng PLMun Registrar's Office. Ang eksaktong requirements, bayad, at processing time ay hindi pa beripikado sa knowledge base na ito at maaaring magbago. Kumpirmahin ang pinakabagong COM request instructions sa Registrar's Office.",
        [
            "how do i get my certificate of matriculation",
            "paano kumuha ng com",
            "com request",
            "gusto kong mag-request ng certificate of matriculation",
            "magkano ang com",
            "i want to request a certificate of matriculation",
            "where can i request a com",
            "certificate of matriculation request",
            "what are the requirements for getting a com",
            "kailangan ko ng certificate of matriculation",
            "saan mag request ng com",
            "ano ang requirements para sa com",
            "where do i get my matriculation certificate",
            "how can i request matriculation certification",

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