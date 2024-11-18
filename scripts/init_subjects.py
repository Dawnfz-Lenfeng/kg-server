from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.subject import Subject
from app.schemas.subject import SubjectType

SUBJECTS = [
    {"name": "金融", "type": SubjectType.FINANCE, "description": "包含金融理论、金融市场、投资学等相关文献"},
    {
        "name": "经济",
        "type": SubjectType.ECONOMICS,
        "description": "包含宏观经济、微观经济、政治经济学等相关文献",
    },
    {
        "name": "统计",
        "type": SubjectType.STATISTICS,
        "description": "包含统计理论、统计方法、数理统计等相关文献",
    },
    {
        "name": "数据科学",
        "type": SubjectType.DATA_SCIENCE,
        "description": "包含机器学习、数据挖掘、人工智能等相关文献",
    },
]


def init_subjects():
    """初始化学科数据"""
    db = SessionLocal()
    try:
        # 检查是否已存在
        existing = {subject.type: subject for subject in db.query(Subject).all()}

        for subject_data in SUBJECTS:
            if subject_data["type"] not in existing:
                subject = Subject(**subject_data)
                db.add(subject)

        db.commit()
        print("学科初始化完成！")
    except Exception as e:
        print(f"初始化失败: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_subjects()
