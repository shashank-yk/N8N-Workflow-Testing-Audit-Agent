from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship

from .config import settings
from .models import QaReport, ScenarioResult


class Base(DeclarativeBase):
    pass


class TestRunRecord(Base):
    __tablename__ = "test_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    workflow_id: Mapped[str] = mapped_column(String, nullable=False)
    workflow_name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    report_markdown: Mapped[str] = mapped_column(String, nullable=False)
    report_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    scenarios: Mapped[list["ScenarioRecord"]] = relationship(back_populates="run", cascade="all, delete-orphan")


class ScenarioRecord(Base):
    __tablename__ = "scenario_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("test_runs.id"), nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    run: Mapped[TestRunRecord] = relationship(back_populates="scenarios")


engine = create_engine(settings.database_url)


def init_db() -> None:
    Base.metadata.create_all(engine)


def save_report(report: QaReport) -> None:
    payload = report.model_dump(mode="json")
    record = TestRunRecord(
        id=report.run_id,
        workflow_id=report.workflow.id,
        workflow_name=report.workflow.name,
        created_at=report.created_at,
        report_markdown=report.to_markdown(),
        report_payload=payload,
    )
    for item in [*report.passed, *report.failed]:
        record.scenarios.append(
            ScenarioRecord(
                role=item.scenario.role.value,
                title=item.scenario.title,
                status=item.status.value,
                payload=item.model_dump(mode="json"),
            )
        )
    with Session(engine) as session:
        session.add(record)
        session.commit()


def get_latest_report() -> TestRunRecord | None:
    with Session(engine) as session:
        stmt = select(TestRunRecord).order_by(TestRunRecord.created_at.desc()).limit(1)
        return session.scalar(stmt)


def get_report(run_id: str) -> TestRunRecord | None:
    with Session(engine) as session:
        return session.get(TestRunRecord, run_id)


if __name__ == "__main__":
    init_db()
