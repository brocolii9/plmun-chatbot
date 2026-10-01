from app.database import SessionLocal
from app import nlp


TEST_CASES = [
    # Enrollment procedure
    ("enrollment_procedure", "Where do I start if I want to enroll?"),
    ("enrollment_procedure", "Ano ang unang step sa pag enroll?"),
    ("enrollment_procedure", "I want to register for the next semester"),

    # Enrollment requirements
    ("enrollment_requirements", "What papers should I prepare for enrollment?"),
    ("enrollment_requirements", "May documents ba na kailangan sa enrollment?"),
    ("enrollment_requirements", "What should continuing students bring when enrolling?"),

    # Add / drop / change subjects
    ("add_drop_change_subjects", "Can I remove a subject from my schedule?"),
    ("add_drop_change_subjects", "Gusto kong magpalit ng klase"),
    ("add_drop_change_subjects", "What should I do if I need to add another class?"),

    # LOA / shifting / withdrawal
    ("leave_of_absence_shifting", "Can I stop studying for one semester?"),
    ("leave_of_absence_shifting", "Gusto kong mag shift ng course"),
    ("leave_of_absence_shifting", "What do I do if I want to withdraw from school?"),

    # TOR
    ("tor_request", "Where do students get their transcript of records?"),
    ("tor_request", "Pwede ba akong kumuha ng transcript?"),
    ("tor_request", "I need a copy of my academic transcript"),

    # Certification
    ("certification_request", "Can I get a document proving that I am currently enrolled?"),
    ("certification_request", "Saan kukuha ng enrollment certificate?"),
    ("certification_request", "I need school certification for a requirement"),

    # Transfer credentials
    ("transfer_credentials", "What do I need if I move to another university?"),
    ("transfer_credentials", "Paano kumuha ng transfer credentials?"),
    ("transfer_credentials", "I'm planning to transfer to a different college"),

    # Fees / processing time
    ("document_fees_processing_time", "How long does it take to receive requested records?"),
    ("document_fees_processing_time", "May bayad ba ang pag request ng document?"),
    ("document_fees_processing_time", "When can I pick up my requested document?"),

    # Correction of records
    ("correction_of_records", "My middle name is incorrect in my student information"),
    ("correction_of_records", "Paano palitan ang maling birthday sa records?"),
    ("correction_of_records", "There is a spelling error in my name"),

    # Graduation
    ("graduation_requirements", "How do I know if I have completed everything for graduation?"),
    ("graduation_requirements", "Ano pa ang kulang ko para makagraduate?"),
    ("graduation_requirements", "What must graduating students complete?"),

    # Diploma / clearance
    ("diploma_and_clearance", "When can graduates receive their diploma?"),
    ("diploma_and_clearance", "Saan ipapasa ang clearance?"),
    ("diploma_and_clearance", "What is the process for completing school clearance?"),

    # Registrar information
    ("registrar_info", "How do I reach the Registrar's Office?"),
    ("registrar_info", "Bukas ba ang registrar ngayon?"),
    ("registrar_info", "What are the Registrar office hours?"),

    # Scholarship
    ("scholarship_concerns", "What financial aid is available for students?"),
    ("scholarship_concerns", "Ano ang kailangan para maging scholar?"),
    ("scholarship_concerns", "Where should I submit scholarship requirements?"),

    # Grade concern
    ("grade_concern", "One of my grades is not showing"),
    ("grade_concern", "Sino ang lalapitan kapag mali ang grade?"),
    ("grade_concern", "There is an issue with my final grade"),

    # COG
    ("cog_request", "Where can I request my Certificate of Grades?"),
    ("cog_request", "Kailangan ko ng copy ng COG"),
    ("cog_request", "What is the process for requesting a COG?"),

    # COM
    ("com_request", "Where can I get a Certificate of Matriculation?"),
    ("com_request", "Kailangan ko ng copy ng COM"),
    ("com_request", "How do students request their COM?"),

    # Out-of-scope
    (None, "What time is the basketball game?"),
    (None, "Can you write my programming assignment?"),
    (None, "Where is the nearest hospital?"),
    (None, "How do I renew my driver's license?"),
    (None, "What are the requirements for a passport?"),
    (None, "Tell me a joke"),
    (None, "How much does a laptop cost?"),
    (None, "Who is the president of the Philippines?"),
    (None, "What is the temperature outside?"),
    (None, "Can you solve this math equation?"),
]


db = SessionLocal()

try:
    sample_count = nlp.retrain_from_db(db)

    print("=" * 80)
    print(f"UNSEEN NLP TEST - {sample_count} training samples")
    print("=" * 80)

    passed = 0

    for expected, question in TEST_CASES:
        predicted, confidence, accepted = nlp.classify(question)

        if predicted == expected:
            status = "PASS"
            passed += 1
        else:
            status = "FAIL"

        expected_text = expected if expected else "FALLBACK"
        predicted_text = predicted if predicted else "FALLBACK"

        print(f"\n[{status}] {question}")
        print(f"Expected  : {expected_text}")
        print(f"Predicted : {predicted_text}")
        print(f"Confidence: {confidence:.2%}")

    total = len(TEST_CASES)

    print("\n" + "=" * 80)
    print(f"RESULT: {passed}/{total} passed")
    print(f"ACCURACY: {(passed / total) * 100:.2f}%")
    print("=" * 80)

finally:
    db.close()