from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()

class Puzzle(Base):
    """海龟汤题库"""
    __tablename__ = "puzzles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    soup_surface = Column(Text, nullable=False)      # 汤面（题目描述）
    soup_base = Column(Text, nullable=False)         # 汤底（真相）
    key_details = Column(JSON, default=list)         # 关键细节清单（LLM生成）
    source = Column(String(20), default="preset")    # preset / ai_generated
    created_at = Column(DateTime, default=datetime.utcnow)
    play_count = Column(Integer, default=0)
    solve_count = Column(Integer, default=0)

class GameSession(Base):
    """对局记录"""
    __tablename__ = "game_sessions"

    id = Column(String(36), primary_key=True, index=True)
    puzzle_id = Column(Integer, nullable=False)
    mode = Column(String(20), nullable=False)        # ai / preset
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    total_rounds = Column(Integer, default=0)
    solved = Column(Boolean, default=False)
    status = Column(String(20), default="playing")   # playing / won / lost / revealed
    history = Column(JSON, default=list)             # 问答历史
    final_guess = Column(Text, nullable=True)
    duration_seconds = Column(Integer, nullable=True)

class GameState:
    """内存中的游戏状态（非持久化）"""
    def __init__(self, session_id: str, puzzle_id: int, soup_surface: str, soup_base: str, key_details: list, mode: str):
        self.session_id = session_id
        self.puzzle_id = puzzle_id
        self.soup_surface = soup_surface
        self.soup_base = soup_base
        self.key_details = key_details
        self.mode = mode
        self.round = 0
        self.max_rounds = 30
        self.history = []
        self.start_time = datetime.utcnow()
        self.status = "playing"  # playing / won / lost / revealed
        self.final_guess = None
