from app.database import SessionLocal
from app import nlp


TEST_CASES = [
    # =========================================================
    # IN-SCOPE QUESTIONS
    # 3 new questions for each of the 16 intents = 48
    # =========================================================

    # 1. Enrollment procedure
    ("enrollment_procedure", "How does a student begin the registration process?"),
    ("enrollment_procedure", "Saan ako magsisimula para makapag enroll?"),
    ("enrollment_procedure", "What comes first when enrolling for a new term?"),

    # 2. Enrollment requirements
    ("enrollment_requirements", "Which papers must I prepare before registration?"),
    ("enrollment_requirements", "Ano ang mga dapat kong dalhin kapag mag-eenroll?"),
    ("enrollment_requirements", "What documents are required from students during enrollment?"),

    # 3. Add / drop / change subjects
    ("add_drop_change_subjects", "Can I replace one subject with another?"),
    ("add_drop_change_subjects", "Gusto kong alisin ang isang subject sa load ko"),
    ("add_drop_change_subjects", "How do I add an extra subject to my current schedule?"),

    # 4. LOA / shifting / withdrawal
    ("leave_of_absence_shifting", "I want to take a break from school for one term"),
    ("leave_of_absence_shifting", "Pwede ba akong lumipat sa ibang course?"),
    ("leave_of_absence_shifting", "How can I officially withdraw from my program?"),

    # 5. TOR
    ("tor_request", "How can I obtain my official academic transcript?"),
    ("tor_request", "Saan pinoprocess ang TOR?"),
    ("tor_request", "Can I request another copy of my transcript?"),

    # 6. Certification
    ("certification_request", "I need a letter confirming that I am currently a student"),
    ("certification_request", "Paano kumuha ng certification na enrolled ako?"),
    ("certification_request", "Where do I request an enrollment certification?"),

    # 7. Transfer credentials
    ("transfer_credentials", "What papers do I need when leaving for another school?"),
    ("transfer_credentials", "Ano ang kailangan ko kapag lilipat sa ibang university?"),
    ("transfer_credentials", "I need credentials so I can continue studying at another college"),

    # 8. Document fees / processing time
    ("document_fees_processing_time", "How many working days does a document request take?"),
    ("document_fees_processing_time", "May fee ba sa pagkuha ng registrar documents?"),
    ("document_fees_processing_time", "How soon can I collect a requested school document?"),

    # 9. Correction of records
    ("correction_of_records", "My surname is misspelled in the university record"),
    ("correction_of_records", "Mali ang date of birth na nakalagay sa student information ko"),
    ("correction_of_records", "How can I correct an error in my personal details?"),

    # 10. Graduation requirements
    ("graduation_requirements", "What must seniors finish before they are allowed to graduate?"),
    ("graduation_requirements", "Paano ko malalaman kung kumpleto na requirements ko sa graduation?"),
    ("graduation_requirements", "What should I complete as a graduating student?"),

    # 11. Diploma / clearance
    ("diploma_and_clearance", "How do I complete my university clearance?"),
    ("diploma_and_clearance", "Kailan maaaring kunin ng graduate ang diploma?"),
    ("diploma_and_clearance", "Where should I go to process my clearance?"),

    # 12. Registrar information
    ("registrar_info", "What days is the Registrar Office available?"),
    ("registrar_info", "Paano ko makokontak ang Registrar?"),
    ("registrar_info", "Where exactly is the Registrar Office located?"),

    # 13. Scholarship
    ("scholarship_concerns", "Where can I inquire about financial assistance for students?"),
    ("scholarship_concerns", "Ano ang dapat kong gawin para mag-apply bilang scholar?"),
    ("scholarship_concerns", "What qualifications are needed for student scholarships?"),

    # 14. Grade concern
    ("grade_concern", "My subject grade has not appeared yet"),
    ("grade_concern", "Kanino ako lalapit kung may problema sa grades ko?"),
    ("grade_concern", "Who handles discrepancies in student grades?"),

    # 15. COG
    ("cog_request", "How can I obtain an official Certificate of Grades?"),
    ("cog_request", "Pwede ba akong mag request ng COG?"),
    ("cog_request", "Where is a Certificate of Grades processed?"),

    # 16. COM
    ("com_request", "I need an official Certificate of Matriculation"),
    ("com_request", "Pwede ba akong kumuha ng COM sa Registrar?"),
    ("com_request", "What is the procedure for getting a matriculation certificate?"),

    # =========================================================
    # OUT-OF-SCOPE QUESTIONS
    # 16 questions
    # =========================================================

    # University-related but outside the 16 supported intents
    (None, "What time does the university library close?"),
    (None, "Where is the school canteen?"),
    (None, "When will the intramurals begin?"),
    (None, "How can I join the university basketball team?"),
    (None, "What subjects are offered next semester?"),
    (None, "How much is the tuition fee?"),
    (None, "Who is my professor for programming?"),
    (None, "What events are happening on campus this week?"),

    # Completely unrelated
    (None, "Can you teach me how Python loops work?"),
    (None, "What will the weather be tomorrow?"),
    (None, "Where is Muntinlupa City Hall?"),
    (None, "How do I apply for a driver's license?"),
    (None, "Tell me something funny"),
    (None, "What is 25 multiplied by 16?"),
    (None, "Who won the basketball championship?"),
    (None, "Which smartphone should I buy?"),
]


db = SessionLocal()

try:
    sample_count = nlp.retrain_from_db(db)

    print("=" * 80)
    print(f"FINAL HOLDOUT TEST - {sample_count} training samples")
    print("=" * 80)

    total_correct = 0

    in_scope_total = 0
    in_scope_correct = 0

    out_scope_total = 0
    out_scope_correct = 0

    for expected, question in TEST_CASES:
        predicted, confidence, accepted = nlp.classify(question)

        correct = predicted == expected

        if correct:
            total_correct += 1
            status = "PASS"
        else:
            status = "FAIL"

        if expected is None:
            out_scope_total += 1

            if correct:
                out_scope_correct += 1
        else:
            in_scope_total += 1

            if correct:
                in_scope_correct += 1

        expected_text = expected if expected else "FALLBACK"
        predicted_text = predicted if predicted else "FALLBACK"

        print(f"\n[{status}] {question}")
        print(f"Expected  : {expected_text}")
        print(f"Predicted : {predicted_text}")
        print(f"Confidence: {confidence:.2%}")

    total = len(TEST_CASES)

    overall_accuracy = (
        total_correct / total * 100
        if total else 0
    )

    intent_accuracy = (
        in_scope_correct / in_scope_total * 100
        if in_scope_total else 0
    )

    rejection_accuracy = (
        out_scope_correct / out_scope_total * 100
        if out_scope_total else 0
    )

    print("\n" + "=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)

    print(
        f"In-scope intent classification : "
        f"{in_scope_correct}/{in_scope_total} "
        f"({intent_accuracy:.2f}%)"
    )

    print(
        f"Out-of-scope rejection        : "
        f"{out_scope_correct}/{out_scope_total} "
        f"({rejection_accuracy:.2f}%)"
    )

    print(
        f"Overall                       : "
        f"{total_correct}/{total} "
        f"({overall_accuracy:.2f}%)"
    )

    print("=" * 80)

finally:
    db.close()