import json

from app.database import SessionLocal
from app.models import Intent
from app.seed import SEED


def main():
    db = SessionLocal()

    try:
        updated = 0
        total_samples = 0

        for name, category, question, ans_en, ans_fil, utterances in SEED:
            intent = db.query(Intent).filter(Intent.name == name).first()

            if not intent:
                print(f"[SKIP] Intent not found: {name}")
                continue

            intent.sample_utterances = json.dumps(
                utterances,
                ensure_ascii=False
            )

            updated += 1
            total_samples += len(utterances)

            print(
                f"[UPDATED] {name}: "
                f"{len(utterances)} samples"
            )

        db.commit()

        print("\n" + "=" * 60)
        print(f"Updated intents : {updated}")
        print(f"Training samples: {total_samples}")
        print("=" * 60)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()