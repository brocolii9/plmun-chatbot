from datetime import datetime, timezone

from app.database import SessionLocal
from app.models import Intent
from app.seed import SEED


def main():
    db = SessionLocal()

    updated = 0
    missing = 0

    try:
        for (
            name,
            category,
            question,
            answer_en,
            answer_fil,
            utterances,
        ) in SEED:

            intent = (
                db.query(Intent)
                .filter(Intent.name == name)
                .first()
            )

            if not intent:
                print(f"[MISSING INTENT] {name}")
                missing += 1
                continue

            kb = intent.kb_entry

            if not kb:
                print(f"[MISSING KB] {name}")
                missing += 1
                continue

            # Update knowledge-base content only.
            # Do NOT change the NLP training samples here.
            kb.category = category
            kb.question = question
            kb.answer_en = answer_en
            kb.answer_fil = answer_fil
            kb.last_updated_at = datetime.utcnow()

            updated += 1

            print(f"[UPDATED] {name}")

        db.commit()

        print("\n" + "=" * 60)
        print(f"Knowledge entries updated: {updated}")
        print(f"Missing entries          : {missing}")
        print("=" * 60)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()