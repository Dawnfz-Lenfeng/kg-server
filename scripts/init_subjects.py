from app.database import SessionLocal
from app.models import *

SUBJECTS = [
    {
        "id": 1,
        "name": "金融",
        "description": "包含金融理论、金融市场、投资学等相关文献",
    },
    {
        "id": 2,
        "name": "经济",
        "description": "包含宏观经济、微观经济、政治经济学等相关文献",
    },
    {
        "id": 3,
        "name": "统计",
        "description": "包含统计理论、统计方法、数理统计等相关文献",
    },
    {
        "id": 4,
        "name": "数据科学",
        "description": "包含机器学习、数据挖掘、人工智能等相关文献",
    },
]


def init_subjects():
    """初始化学科数据"""
    with SessionLocal() as db:
        added_subjects = []
        try:
            # 检查是否已存在
            existing = {subject.id: subject for subject in db.query(Subject).all()}

            for subject_data in SUBJECTS:
                if subject_data["id"] not in existing:
                    subject = Subject(**subject_data)
                    db.add(subject)
                    added_subjects.append(subject_data["name"])

            db.commit()
            print("Subject Init Success")
        except Exception as e:
            print(f"Subject Init Failed: {e}")
            db.rollback()

        if added_subjects:
            print(f"✓ Added subjects: {', '.join(added_subjects)}")
        else:
            print("✗ No new subjects added")


if __name__ == "__main__":
    init_subjects()
