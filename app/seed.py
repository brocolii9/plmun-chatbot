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
        "For enrollment, the process depends on your student status.\n\n"
        "For new undergraduate applicants:\n"
        "• Use the official PLMun Undergraduate Admission Portal.\n"
        "• Create or log in to your admission account.\n"
        "• Complete the required information in the online admission form.\n"
        "• Submit the required scanned admission documents.\n"
        "• Take the admission test according to the schedule provided by PLMun.\n"
        "• Check the official admission result and follow the enrollment instructions given to successful applicants.\n\n"
        "For continuing students, the PLMun Student Handbook describes the enrollment process as:\n"
        "• Proceed to your respective College for advising or pre-enrollment.\n"
        "• Have your subjects encoded through the College or Dean's Office.\n"
        "• Complete the applicable enrollment requirements for the semester.\n"
        "• Obtain your Certificate of Matriculation (COM) through the Office of the University Registrar.\n\n"
        "Enrollment schedules and procedures may be updated each semester, so always follow the latest official PLMun announcement and the instructions of your College and the Office of the University Registrar.",
        "Ang enrollment process ay depende sa student status.\n\n"
        "Para sa mga bagong undergraduate applicant:\n"
        "• Gamitin ang official PLMun Undergraduate Admission Portal.\n"
        "• Gumawa o mag-login sa inyong admission account.\n"
        "• Kumpletuhin ang kinakailangang impormasyon sa online admission form.\n"
        "• Isumite ang kinakailangang scanned admission documents.\n"
        "• Kumuha ng admission test ayon sa schedule na ibibigay ng PLMun.\n"
        "• Tingnan ang official admission result at sundin ang enrollment instructions para sa successful applicants.\n\n"
        "Para sa continuing students, inilalarawan sa PLMun Student Handbook ang enrollment process bilang:\n"
        "• Pumunta sa inyong College para sa advising o pre-enrollment.\n"
        "• Ipa-encode ang inyong subjects sa pamamagitan ng College o Dean's Office.\n"
        "• Kumpletuhin ang applicable enrollment requirements para sa semester.\n"
        "• Kunin ang Certificate of Matriculation (COM) sa pamamagitan ng Office of the University Registrar.\n\n"
        "Maaaring ma-update bawat semester ang enrollment schedule at procedure, kaya sundin palagi ang pinakabagong official PLMun announcement at instructions ng inyong College at Office of the University Registrar.",
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
        "For admission, the requirements may depend on your applicant status.\n\n"
        "Common documents identified by PLMun include:\n"
        "• 2x2 picture\n"
        "• PSA Birth Certificate\n"
        "• Previous school ID or another valid ID\n"
        "• Recent school card or copy of grades\n"
        "• Certificate of Good Moral Character\n"
        "• Form 138\n\n"
        "For transferees, the following may also be required:\n"
        "• Transcript of Records (TOR)\n"
        "• Honorable Dismissal\n\n"
        "Please check the current PLMun Admission Portal and official admission announcements because requirements may differ depending on applicant status.",

        "Para sa admission, maaaring magkaiba ang requirements depende sa applicant status.\n\n"
        "Karaniwang dokumentong tinutukoy ng PLMun ay:\n"
        "• 2x2 picture\n"
        "• PSA Birth Certificate\n"
        "• Previous school ID o ibang valid ID\n"
        "• Recent school card o copy of grades\n"
        "• Certificate of Good Moral Character\n"
        "• Form 138\n\n"
        "Para sa transferees, maaari ring kailanganin ang:\n"
        "• Transcript of Records (TOR)\n"
        "• Honorable Dismissal\n\n"
        "Tingnan ang kasalukuyang PLMun Admission Portal at opisyal na admission announcements dahil maaaring magkaiba ang requirements depende sa applicant status.",
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
        "According to the PLMun Student Handbook, students who need to add, drop, or change a subject should follow the official subject-adjustment process.\n\n"
        "Important guidelines include:\n"
        "• Adding or dropping a subject is allowed not later than two weeks after the start of classes.\n"
        "• A student may add or drop a maximum of two subjects for the current semester.\n"
        "• The request must receive the required approval from the instructor or College Dean and be submitted to the Registrar for official recording.\n"
        "• Dropping a subject without official approval may result in a failing grade.\n"
        "• Transfer to another class requires approval from the College Dean and must be recorded by the University Registrar.\n\n"
        "These rules are stated in the PLMun Student Handbook. Students should still check the current semester announcement or confirm with their College and the Registrar's Office in case the schedule or procedure has been updated.",
        "Ayon sa PLMun Student Handbook, ang mga estudyanteng kailangang mag-add, mag-drop, o magpalit ng subject ay dapat sumunod sa opisyal na subject-adjustment process.\n\n"
        "Mahahalagang guidelines:\n"
        "• Ang pag-add o pag-drop ng subject ay pinapayagan hanggang dalawang linggo pagkatapos magsimula ang klase.\n"
        "• Maaaring mag-add o mag-drop ng maximum na dalawang subjects sa kasalukuyang semester.\n"
        "• Kailangang makuha ang kinakailangang approval ng instructor o College Dean at maisumite sa Registrar para sa official recording.\n"
        "• Ang pag-drop ng subject nang walang official approval ay maaaring magresulta sa failing grade.\n"
        "• Ang paglipat sa ibang class section ay nangangailangan ng approval ng College Dean at dapat ma-record ng University Registrar.\n\n"
        "Ang mga patakarang ito ay nakasaad sa PLMun Student Handbook. Tingnan pa rin ang current semester announcement o kumpirmahin sa inyong College at Registrar's Office kung may bagong schedule o procedure.",
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
        "For Leave of Absence (LOA), the PLMun Student Handbook states:\n\n"
        "• The request must be made in writing.\n"
        "• The LOA must be approved by the College Dean.\n"
        "• An LOA may be granted for one academic year.\n"
        "• It may be extended for another year upon the student's request.\n"
        "• If the LOA exceeds two academic years, the student loses residency status.\n"
        "• A student who withdraws without a formal LOA must apply for readmission.\n\n"
        "For shifting to another program, the current step-by-step procedure is not stated in the verified source used by this chatbot. Please confirm the latest shifting requirements and procedure with your College or the Registrar's Office.",
        "Para sa Leave of Absence (LOA), nakasaad sa PLMun Student Handbook ang mga sumusunod:\n\n"
        "• Kailangang gawin ang request in writing.\n"
        "• Kailangang aprubahan ang LOA ng College Dean.\n"
        "• Maaaring payagan ang LOA nang isang academic year.\n"
        "• Maaari itong ma-extend ng isa pang taon kapag hiniling ng estudyante.\n"
        "• Kapag lumampas sa dalawang academic years ang LOA, mawawala ang residency status ng estudyante.\n"
        "• Ang estudyanteng mag-withdraw nang walang formal LOA ay kailangang mag-apply for readmission.\n\n"
        "Para naman sa shifting sa ibang program, walang verified step-by-step shifting procedure sa source na ginagamit ng chatbot. Kumpirmahin ang pinakabagong requirements at proseso sa inyong College o sa Registrar's Office.",
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
        "To request a Transcript of Records (TOR):\n\n"
        "• Coordinate with the PLMun Office of the University Registrar.\n"
        "• The Registrar is located at the 1st Floor, Student Center Building.\n"
        "• Contact number: 8659-2075 local 205.\n"
        "• The PLMun Student Handbook states that official documents, including the Transcript of Records, should be issued within thirty days from request.\n\n"
        "The current TOR request form, documentary requirements, fees, and exact release schedule are not specified in the verified sources used by this chatbot. Please confirm these details with the Registrar before submitting or paying for a request.",
        "Para humiling ng Transcript of Records (TOR):\n\n"
        "• Makipag-ugnayan sa PLMun Office of the University Registrar.\n"
        "• Ang Registrar ay matatagpuan sa 1st Floor, Student Center Building.\n"
        "• Contact number: 8659-2075 local 205.\n"
        "• Nakasaad sa PLMun Student Handbook na ang mga official documents, kabilang ang Transcript of Records, ay dapat ma-issue within thirty days mula sa request.\n\n"
        "Ang kasalukuyang TOR request form, documentary requirements, fees, at eksaktong release schedule ay hindi nakasaad sa verified sources na ginagamit ng chatbot. Kumpirmahin muna ang mga ito sa Registrar bago magsumite o magbayad para sa request.",
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
        "For certification requests:\n\n"
        "• Coordinate with the PLMun Office of the University Registrar.\n"
        "• The Registrar is located at the 1st Floor, Student Center Building.\n"
        "• Contact number: 8659-2075 local 205.\n"
        "• The PLMun Student Handbook states that official certificates and similar school documents should be issued within thirty days from request.\n\n"
        "The exact certification types currently available, request form, documentary requirements, fees, and release schedule are not specified in the verified sources used by this chatbot. Please confirm the specific certification you need with the Registrar before submitting a request.",
        "Para sa certification request:\n\n"
        "• Makipag-ugnayan sa PLMun Office of the University Registrar.\n"
        "• Ang Registrar ay matatagpuan sa 1st Floor, Student Center Building.\n"
        "• Contact number: 8659-2075 local 205.\n"
        "• Nakasaad sa PLMun Student Handbook na ang official certificates at iba pang similar school documents ay dapat ma-issue within thirty days mula sa request.\n\n"
        "Ang eksaktong certification types na kasalukuyang available, request form, documentary requirements, fees, at release schedule ay hindi nakasaad sa verified sources na ginagamit ng chatbot. Kumpirmahin muna sa Registrar kung anong certification ang kailangan bago magsumite ng request.",
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
        "For Honorable Dismissal or transfer credentials, the PLMun Student Handbook states:\n\n"
        "• A Certificate of Honorable Dismissal is issued by the University Registrar when a student voluntarily withdraws from PLMun to transfer to another school.\n"
        "• The student must be cleared of all accountabilities before the certificate can be issued.\n"
        "• A student who has already been issued a Certificate of Honorable Dismissal cannot be re-admitted to PLMun.\n\n"
        "The current request form, documentary requirements, fees, and exact processing procedure are not specified in the verified source used by this chatbot. Please confirm the latest requirements with the Office of the University Registrar before submitting your request.",
        "Para sa Honorable Dismissal o transfer credentials, nakasaad sa PLMun Student Handbook ang mga sumusunod:\n\n"
        "• Ang Certificate of Honorable Dismissal ay ini-issue ng University Registrar kapag boluntaryong nag-withdraw ang estudyante sa PLMun upang lumipat sa ibang paaralan.\n"
        "• Kailangang cleared ang estudyante sa lahat ng accountabilities bago ma-issue ang certificate.\n"
        "• Ang estudyanteng na-issue-han na ng Certificate of Honorable Dismissal ay hindi na maaaring ma-readmit sa PLMun.\n\n"
        "Ang kasalukuyang request form, documentary requirements, fees, at eksaktong processing procedure ay hindi nakasaad sa verified source na ginagamit ng chatbot. Kumpirmahin muna ang pinakabagong requirements sa Office of the University Registrar bago magsumite ng request.",
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
        "Document fees and processing times depend on the specific document requested.\n\n"
        "Verified information available to this chatbot:\n"
        "• The 2019 PLMun Student Handbook states that official certificates, diplomas, Transcript of Records (TOR), grades, transfer credentials, and similar documents should be issued within thirty days from request.\n"
        "• The Office of the University Registrar is located at the 1st Floor, Student Center Building.\n"
        "• Contact number: 8659-2075 local 205.\n\n"
        "Current fees and the exact processing time for each type of document are not specified in the verified current sources used by this chatbot. Please confirm the amount and release schedule with the Office of the University Registrar before making a payment.",
        "Ang document fees at processing time ay maaaring magkaiba depende sa uri ng dokumentong hinihingi.\n\n"
        "Verified information na available sa chatbot:\n"
        "• Nakasaad sa 2019 PLMun Student Handbook na ang official certificates, diploma, Transcript of Records (TOR), grades, transfer credentials, at iba pang similar documents ay dapat ma-issue within thirty days mula sa request.\n"
        "• Ang Office of the University Registrar ay matatagpuan sa 1st Floor, Student Center Building.\n"
        "• Contact number: 8659-2075 local 205.\n\n"
        "Ang kasalukuyang fee at eksaktong processing time ng bawat uri ng dokumento ay hindi nakasaad sa verified current sources na ginagamit ng chatbot. Kumpirmahin muna ang halaga at release schedule sa Office of the University Registrar bago magbayad.",
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
        "For grade corrections and incomplete grades (INC), the PLMun Student Handbook provides the following guidance:\n\n"
        "• A change of final grade may be allowed only when there is an error in the computation of the grade within the prevailing academic year.\n"
        "• A grade change must be supported by the necessary academic records and requires final approval of the VPAA.\n"
        "• An INC must be completed within one academic year; otherwise, it may result in a grade of 5.0.\n"
        "• For completion of an INC, the student should secure a Completion Form from the Registrar's Office and provide copies to the University Registrar, College Dean, and Instructor.\n"
        "• The instructor may require completion of missing requirements such as an examination or term paper before submitting the completed grade to the Registrar's Office.\n\n"
        "For corrections to personal student records such as name, birth date, or other personal information, the current step-by-step procedure and documentary requirements are not specified in the verified source used by this chatbot. Please confirm the latest requirements with the Office of the University Registrar.",
        "Para sa grade correction at incomplete grade (INC), nakasaad sa PLMun Student Handbook ang mga sumusunod:\n\n"
        "• Maaaring baguhin ang final grade kung may error sa computation ng grade sa loob ng kasalukuyang academic year.\n"
        "• Kailangang may supporting academic records ang grade change at nangangailangan ito ng final approval ng VPAA.\n"
        "• Kailangang makumpleto ang INC sa loob ng isang academic year; kung hindi, maaari itong maging grade na 5.0.\n"
        "• Para sa completion ng INC, kailangang kumuha ng Completion Form sa Registrar's Office at magbigay ng kopya sa University Registrar, College Dean, at Instructor.\n"
        "• Maaaring ipagawa ng instructor ang kulang na requirements tulad ng examination o term paper bago isumite ang completed grade sa Registrar's Office.\n\n"
        "Para sa correction ng personal student records gaya ng pangalan, birth date, o ibang personal information, walang verified step-by-step procedure at documentary requirements sa source na ginagamit ng chatbot. Kumpirmahin ang pinakabagong requirements sa Office of the University Registrar.",
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
        "For graduation preparation, the PLMun Student Handbook states:\n\n"
        "• During the First Semester of the School Year, senior students should fill out a form requesting evaluation of their subjects and grades from the Office of the Registrar.\n"
        "• Graduating students are also required to undergo an Exit Interview.\n"
        "• Students who may qualify for Latin honors undergo a separate evaluation and deliberation process involving the Office of the University Registrar, College Dean, and University Council.\n\n"
        "The complete current documentary requirements, clearance requirements, application deadlines, and graduation schedule are not fully specified in the verified source used by this chatbot. Please confirm the latest graduation instructions with the Office of the University Registrar and your College.",
        "Para sa paghahanda sa graduation, nakasaad sa PLMun Student Handbook ang mga sumusunod:\n\n"
        "• Sa First Semester ng School Year, ang senior students ay kailangang mag-fill out ng form para mag-request ng evaluation ng kanilang subjects at grades sa Office of the Registrar.\n"
        "• Kailangan ding sumailalim sa Exit Interview ang graduating students.\n"
        "• Ang mga estudyanteng maaaring maging qualified for Latin honors ay dumadaan sa hiwalay na evaluation at deliberation process na kinabibilangan ng Office of the University Registrar, College Dean, at University Council.\n\n"
        "Ang kumpletong kasalukuyang documentary requirements, clearance requirements, application deadlines, at graduation schedule ay hindi ganap na nakasaad sa verified source na ginagamit ng chatbot. Kumpirmahin ang pinakabagong graduation instructions sa Office of the University Registrar at sa inyong College.",
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
        "For diploma and clearance concerns:\n\n"
        "• The PLMun Student Handbook states that diplomas and other official school documents should be issued within thirty days from request.\n"
        "• Diploma-related requests should be coordinated with the Office of the University Registrar.\n\n"
        "The verified source used by this chatbot does not provide the current step-by-step graduation clearance procedure, required offices for clearance, clearance form requirements, diploma release schedule, or current fees. Please confirm these details with the Office of the University Registrar before processing your clearance or claiming your diploma.",
        "Para sa diploma at clearance concerns:\n\n"
        "• Nakasaad sa PLMun Student Handbook na ang diploma at iba pang official school documents ay dapat ma-issue within thirty days mula sa request.\n"
        "• Ang diploma-related requests ay dapat i-coordinate sa Office of the University Registrar.\n\n"
        "Ang verified source na ginagamit ng chatbot ay walang kasalukuyang step-by-step graduation clearance procedure, listahan ng offices na kailangang i-clear, clearance form requirements, diploma release schedule, o current fees. Kumpirmahin ang mga detalyeng ito sa Office of the University Registrar bago mag-process ng clearance o mag-claim ng diploma.",
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

        "The Office of the University Registrar:\n\n"
        "• Location: 1st Floor, Student Center Building\n"
        "• Address: PLMun, University Road, Poblacion, Muntinlupa City\n"
        "• Contact: 8659-2075 local 205\n\n"
        "For current schedules and service-specific requirements, please follow official PLMun announcements.",

        "Office of the University Registrar:\n\n"
        "• Lokasyon: 1st Floor, Student Center Building\n"
        "• Address: PLMun, University Road, Poblacion, Muntinlupa City\n"
        "• Contact: 8659-2075 local 205\n\n"
        "Para sa kasalukuyang schedule at requirements ng partikular na serbisyo, sundin ang opisyal na PLMun announcements.",
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
        "PLMun provides scholarship and financial assistance programs such as:\n"
        "• ACE\n"
        "• I-STEP\n"
        "• BOARD\n"
        "• CARRI\n"
        "• CREATE\n"
        "• SEAL\n"
        "• Masteral Degree Scholarship\n\n"
        "For local scholarship applications, the PLMun Citizen's Charter lists the following requirements:\n"
        "• Filled-out application form with 2x2 photo\n"
        "• Letter of Intent\n"
        "• Photocopy of Certificate of Matriculation (COM)\n"
        "• Original Certificate of Grades (COG) with previous GPA\n"
        "• Original Voter's Certificate\n"
        "• Certificate of Good Moral Character\n"
        "• Photocopy of School ID\n"
        "• Photocopy of parent's ID\n\n"
        "Submit the required documents to the Scholarship and Financial Assistance Division of the Office of Student Affairs. Eligibility and available programs may change, so check the latest official PLMun scholarship announcement.",

        "May scholarship at financial assistance programs ang PLMun tulad ng:\n"
        "• ACE\n"
        "• I-STEP\n"
        "• BOARD\n"
        "• CARRI\n"
        "• CREATE\n"
        "• SEAL\n"
        "• Masteral Degree Scholarship\n\n"
        "Para sa local scholarship application, nakalista sa PLMun Citizen's Charter ang mga sumusunod na requirements:\n"
        "• Filled-out application form na may 2x2 photo\n"
        "• Letter of Intent\n"
        "• Photocopy ng Certificate of Matriculation (COM)\n"
        "• Original Certificate of Grades (COG) na may previous GPA\n"
        "• Original Voter's Certificate\n"
        "• Certificate of Good Moral Character\n"
        "• Photocopy ng School ID\n"
        "• Photocopy ng ID ng magulang\n\n"
        "Isumite ang requirements sa Scholarship and Financial Assistance Division ng Office of Student Affairs. Maaaring magbago ang eligibility at available programs, kaya tingnan ang pinakabagong opisyal na PLMun scholarship announcement.",
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
        "For grade concerns, the PLMun Student Handbook provides the following guidance:\n\n"
        "• Grades are distributed every semester according to the schedule determined by the College Dean.\n"
        "• If there is a discrepancy between the grade given to the student and the grade recorded on the official grading sheet, the grade on the grading sheet is considered official and final.\n"
        "• A final grade may be changed only if there is an error in the computation of the grade within the prevailing academic year.\n"
        "• A grade change must be supported by necessary academic records, such as the class record, final examination paper, and other related documents.\n"
        "• Final approval of the VPAA is required for a grade change.\n\n"
        "The current online grade-viewing procedure or portal instructions are not specified in the verified source used by this chatbot. For a missing or incorrect grade, please coordinate with your College or the Office of the University Registrar.",
        "Para sa grade concerns, nakasaad sa PLMun Student Handbook ang mga sumusunod:\n\n"
        "• Ang grades ay ibinibigay bawat semester ayon sa schedule na itinakda ng College Dean.\n"
        "• Kapag may pagkakaiba sa grade na ibinigay sa estudyante at sa grade na nakalagay sa official grading sheet, ang grade sa grading sheet ang itinuturing na official at final.\n"
        "• Maaaring baguhin ang final grade kung may error sa computation ng grade sa loob ng kasalukuyang academic year.\n"
        "• Kailangang suportado ang grade change ng academic records tulad ng class record, final examination paper, at iba pang related documents.\n"
        "• Kailangan ang final approval ng VPAA para sa grade change.\n\n"
        "Ang kasalukuyang online grade-viewing procedure o portal instructions ay hindi nakasaad sa verified source na ginagamit ng chatbot. Para sa missing o incorrect na grade, makipag-ugnayan sa inyong College o sa Office of the University Registrar.",
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
        "For a Certificate of Grades (COG) request:\n\n"
        "• Coordinate with the PLMun Office of the University Registrar.\n"
        "• The Certificate of Grades is an official academic document used to show a student's grades.\n"
        "• The PLMun Student Handbook states that official certificates, grades, and similar school documents should be issued within thirty days from request.\n\n"
        "The current COG request form, documentary requirements, fees, and exact release schedule are not specified in the verified sources used by this chatbot. Please confirm the latest COG request procedure with the Office of the University Registrar.",
        "Para sa Certificate of Grades (COG) request:\n\n"
        "• Makipag-ugnayan sa PLMun Office of the University Registrar.\n"
        "• Ang Certificate of Grades ay isang official academic document na nagpapakita ng grades ng estudyante.\n"
        "• Nakasaad sa PLMun Student Handbook na ang official certificates, grades, at iba pang similar school documents ay dapat ma-issue within thirty days mula sa request.\n\n"
        "Ang kasalukuyang COG request form, documentary requirements, fees, at eksaktong release schedule ay hindi nakasaad sa verified sources na ginagamit ng chatbot. Kumpirmahin ang pinakabagong COG request procedure sa Office of the University Registrar.",
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
        "For a Certificate of Matriculation (COM):\n\n"
        "• The COM is an official enrollment document issued through the Office of the University Registrar.\n"
        "• The PLMun Student Handbook states that duly registered or officially enrolled students with a COM are included in the official Master List of Students and are allowed to attend classes.\n"
        "• The COM also reflects the subjects officially enrolled by the student.\n\n"
        "The current procedure for requesting a replacement or additional copy of the COM, including fees and documentary requirements, is not specified in the verified current sources used by this chatbot. Please confirm the latest procedure with the Office of the University Registrar.",
        "Para sa Certificate of Matriculation (COM):\n\n"
        "• Ang COM ay isang official enrollment document na ini-issue sa pamamagitan ng Office of the University Registrar.\n"
        "• Nakasaad sa PLMun Student Handbook na ang duly registered o officially enrolled students na may COM ay kasama sa official Master List of Students at pinapayagang pumasok sa classes.\n"
        "• Makikita rin sa COM ang mga subjects na officially enrolled ng estudyante.\n\n"
        "Ang kasalukuyang procedure para humiling ng replacement o additional copy ng COM, kabilang ang fees at documentary requirements, ay hindi nakasaad sa verified current sources na ginagamit ng chatbot. Kumpirmahin ang pinakabagong procedure sa Office of the University Registrar.",
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