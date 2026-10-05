# PLMun Accessible Conversational AI System

An Accessible Conversational AI System developed for student services at Pamantasan ng Lungsod ng Muntinlupa (PLMun).

The system uses Natural Language Processing (NLP) to identify student inquiries and retrieve responses from a structured knowledge base.

## Main Features

- NLP-based student inquiry processing
- Multinomial Naive Bayes intent classification
- Rule-based intent validation
- English, Filipino, and Taglish inquiry support
- Knowledge-base responses for 16 supported intent categories
- Student and guest access
- Conversation history
- Admin knowledge-base management
- Analytics dashboard
- Text-to-speech and speech-to-text support
- Web interface
- Planned Flutter mobile application

## NLP

The chatbot uses a hybrid intent-recognition process:

1. Preprocessing – clean and tokenize the text
2. Language detection – identify whether the inquiry is in English or Filipino/Taglish
3. Intent classification – use Multinomial Naive Bayes to predict the most likely intent
4. Intent-specific validation – check relevant words and phrases for the predicted intent
5. Confidence gate – determine whether the valid intent and confidence criteria are met
6. Knowledge base lookup – retrieve the corresponding stored response
7. Response output – return the matched response, or provide a referral/fallback response if the criteria are not met

The current training dataset contains 241 example sentences distributed across 16 intent categories.

## Technology Stack

- Backend: Python, FastAPI
- Frontend: HTML, CSS, JavaScript
- Database: MySQL for final implementation
- NLP: Multinomial Naive Bayes with rule-based intent validation
- Mobile Application: Flutter
- Admin Interface: AdminLTE
- Development Environment: Visual Studio Code

## Supported Intent Categories

1. Enrollment procedure
2. Enrollment requirements
3. Adding, dropping, and changing subjects
4. Leave of absence, shifting, and withdrawal
5. Transcript of Records (TOR) request
6. Certification request
7. Transfer credentials
8. Document fees and processing time
9. Correction of records
10. Graduation requirements
11. Diploma and clearance
12. Registrar information
13. Scholarship concerns
14. Grade concerns
15. Certificate of Grades (COG) request
16. Certificate of Matriculation (COM) request

## Development Status

The project is currently under development and testing.

Some features are still being completed, including:

- Service bottleneck analytics
- Extended usage-trend analytics
- Password reset
- Accessibility audit
- Flutter mobile application
- Formal ISO/IEC 25010 evaluation

## Important Note

The chatbot should only provide university information that has been verified for use in the knowledge base. For unsupported or uncertain inquiries, the system returns a fallback or referral response instead of guessing.
