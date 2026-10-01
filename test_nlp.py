from app.database import SessionLocal
from app import nlp


TEST_CASES = [
    # 1. Enrollment procedure
    ("enrollment_procedure", "Can I enroll now?"),
    ("enrollment_procedure", "Paano ako mag-enroll?"),

    # 2. Enrollment requirements
    ("enrollment_requirements", "What do I need for enrollment?"),
    ("enrollment_requirements", "Ano kailangan ko para mag-enroll?"),

    # 3. Add / drop / change subjects
    ("add_drop_change_subjects", "I need to drop one class"),
    ("add_drop_change_subjects", "Pwede ba akong magpalit ng subject?"),

    # 4. Leave of absence / shifting / withdrawal
    ("leave_of_absence_shifting", "I want to take a leave from school"),
    ("leave_of_absence_shifting", "Paano ako mag LOA?"),

    # 5. TOR
    ("tor_request", "I need my transcript"),
    ("tor_request", "Kailangan ko ng TOR"),

    # 6. Certification
    ("certification_request", "I need proof that I am enrolled"),
    ("certification_request", "Kailangan ko ng certificate of enrollment"),

    # 7. Transfer credentials
    ("transfer_credentials", "I am transferring schools"),
    ("transfer_credentials", "Kailangan ko ng honorable dismissal"),

    # 8. Document fees / processing
    ("document_fees_processing_time", "How much will my document cost?"),
    ("document_fees_processing_time", "Magkano at gaano katagal ang document?"),

    # 9. Correction of records
    ("correction_of_records", "My name is wrong in my school record"),
    ("correction_of_records", "Mali ang birthdate ko sa record"),

    # 10. Graduation
    ("graduation_requirements", "What do I need before I can graduate?"),
    ("graduation_requirements", "Ano requirements ko para grumaduate?"),

    # 11. Diploma / clearance
    ("diploma_and_clearance", "Where can I claim my diploma?"),
    ("diploma_and_clearance", "Paano ko kukunin clearance ko?"),

    # 12. Registrar information
    ("registrar_info", "When does the registrar open?"),
    ("registrar_info", "Saan po ang registrar?"),

    # 13. Scholarship
    ("scholarship_concerns", "Can I apply for a scholarship?"),
    ("scholarship_concerns", "Paano ako makakakuha ng scholarship?"),

    # 14. Grade concern
    ("grade_concern", "I have a problem with my grade"),
    ("grade_concern", "Mali ang grade ko"),

    # 15. COG
    ("cog_request", "I need a COG"),
    ("cog_request", "Saan kukuha ng COG?"),

    # 16. COM
    ("com_request", "I need a COM"),
    ("com_request", "Saan kukuha ng COM?"),

    # Out-of-scope: these should go to fallback
    (None, "What is the weather today?"),
    (None, "Who won the NBA game?"),
    (None, "Write me a poem"),
    (None, "Magkano ang iPhone?"),
]


db = SessionLocal()

try:
    sample_count = nlp.retrain_from_db(db)

    print("=" * 80)
    print(f"NLP TEST - {sample_count} training samples")
    print("=" * 80)

    passed_count = 0

    for expected, question in TEST_CASES:
        predicted, confidence, accepted = nlp.classify(question)

        if predicted == expected:
            status = "PASS"
            passed_count += 1
        else:
            status = "FAIL"

        expected_text = expected if expected else "FALLBACK"
        predicted_text = predicted if predicted else "FALLBACK"

        print(f"\n[{status}] {question}")
        print(f"Expected  : {expected_text}")
        print(f"Predicted : {predicted_text}")
        print(f"Confidence: {confidence:.2%}")

    print("\n" + "=" * 80)
    print(f"RESULT: {passed_count}/{len(TEST_CASES)} passed")
    print("=" * 80)

finally:
    db.close()