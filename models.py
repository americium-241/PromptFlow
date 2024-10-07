# models.py
from sqlalchemy import (
    create_engine, Column, String, DateTime, Enum, JSON, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum
import uuid
from datetime import datetime

Base = declarative_base()


class LogLevel(enum.Enum):
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'


class ActionStatus(enum.Enum):
    STARTED = 'STARTED'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'


class ExecutionSession(Base):
    __tablename__ = 'execution_sessions'

    execution_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)

    action_traces = relationship('ActionTrace', back_populates='execution_session')
    log_entries = relationship('LogEntry', back_populates='execution_session')


class ActionTrace(Base):
    __tablename__ = 'action_traces'

    trace_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id = Column(String, ForeignKey('execution_sessions.execution_id'))
    parent_trace_id = Column(String, ForeignKey('action_traces.trace_id'), nullable=True)
    action_name = Column(String)
    component = Column(String)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    status = Column(Enum(ActionStatus))
    input_data = Column(JSON)
    output_data = Column(JSON)

    execution_session = relationship('ExecutionSession', back_populates='action_traces')
    parent_trace = relationship('ActionTrace', remote_side=[trace_id], backref='child_traces')


class LogEntry(Base):
    __tablename__ = 'log_entries'

    log_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id = Column(String, ForeignKey('execution_sessions.execution_id'))
    action_trace_id = Column(String, ForeignKey('action_traces.trace_id'), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    component = Column(String)
    action = Column(String)
    parent_log_id = Column(String, ForeignKey('log_entries.log_id'), nullable=True)
    level = Column(Enum(LogLevel))
    message = Column(String)
    data = Column(JSON)

    execution_session = relationship('ExecutionSession', back_populates='log_entries')
    parent_log = relationship('LogEntry', remote_side=[log_id], backref='child_logs')
