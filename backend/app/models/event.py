from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Date, Float, ForeignKey, func
)
from sqlalchemy.orm import relationship
from app.database import Base
from app.utils.id_gen import generate_id


class Event(Base):
    """拜访事件/活动 — 对应 Salesforce Event 对象"""
    __tablename__ = "events"

    id = Column(String(36), primary_key=True, default=lambda: generate_id("event_"))
    subject = Column(String(255), nullable=False, comment="拜访主题 (Subject)")
    type = Column(String(50), default="Visit", comment="拜访类型 (Type): Visit/Phone Call/Video Conference/Client Visit/Other")
    status = Column(String(50), default="planned", comment="状态: planned/in_progress/completed/cancelled")

    # 计划时间
    start_datetime = Column(DateTime, nullable=False, comment="计划开始时间 (StartDateTime)")
    end_datetime = Column(DateTime, comment="计划结束时间 (EndDateTime)")
    is_all_day_event = Column(Boolean, default=False, comment="是否全天事件 (IsAllDayEvent)")
    show_as = Column(String(20), default="busy", comment="忙/闲状态 (ShowAs): busy/free/out_of_office")

    # 实际执行（签到/签退）
    actual_start_time = Column(DateTime, comment="实际开始时间（签到）")
    actual_end_time = Column(DateTime, comment="实际结束时间（签退）")
    duration_minutes = Column(Integer, comment="实际时长分钟 (DurationInMinutes)")

    # 多态关联 (WhatId / WhoId)
    what_id = Column(String(36), comment="关联对象 ID (WhatId)")
    what_type = Column(String(50), comment="关联对象类型: account/opportunity")
    who_id = Column(String(36), ForeignKey("contacts.id", ondelete="SET NULL"), comment="关联联系人 ID (WhoId)")

    # 关联人
    owner_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), comment="负责人 (OwnerId)")

    # 拜访内容
    purpose = Column(Text, comment="拜访目的")
    preparation_notes = Column(Text, comment="拜访准备")
    description = Column(Text, comment="拜访纪要/备注 (Description)")
    outcome = Column(String(50), comment="拜访结果: success/neutral/failure/no_show")
    next_steps = Column(Text, comment="下一步计划")

    # 位置
    location = Column(String(255), comment="签到位置 (Location)")

    # 时间戳
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关系
    contact = relationship("Contact", backref="events")
    owner = relationship("User", backref="events")
    tasks = relationship("Task", back_populates="event", cascade="all, delete-orphan",
                         order_by="Task.sort_order")


class Task(Base):
    """任务 — 对应 Salesforce Task 对象"""
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, default=lambda: generate_id("task_"))
    event_id = Column(String(36), ForeignKey("events.id", ondelete="CASCADE"), comment="所属 Event ID")
    subject = Column(String(255), nullable=False, comment="任务主题 (Subject)")
    status = Column(String(50), default="not_started", comment="状态 (Status): not_started/in_progress/completed/deferred")
    priority = Column(String(20), default="normal", comment="优先级 (Priority): high/normal/low")
    activity_date = Column(Date, comment="截止日期 (ActivityDate)")

    # 多态关联
    what_id = Column(String(36), comment="关联对象 ID (WhatId)")
    what_type = Column(String(50), comment="关联对象类型")
    who_id = Column(String(36), comment="关联人 ID (WhoId)")

    assignee_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), comment="负责人 (OwnerId)")
    description = Column(Text, comment="任务描述 (Description)")
    sort_order = Column(Integer, default=0, comment="排序")

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关系
    event = relationship("Event", back_populates="tasks")
    assignee = relationship("User", backref="tasks")
