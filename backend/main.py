import os
import uuid
import json
from datetime import datetime, timedelta
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import init_db, get_db, SessionLocal
from models import Puzzle, GameSession, GameState
from llm_service import llm_service
from puzzles_data import PRESET_PUZZLES

# ========== 内存游戏状态存储 ==========
game_states: dict[str, GameState] = {}

# ========== 启动时初始化 ==========
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    db = SessionLocal()
    try:
        count = db.query(Puzzle).count()
        if count == 0:
            for p in PRESET_PUZZLES:
                db.add(Puzzle(
                    title=p["title"],
                    soup_surface=p["soup_surface"],
                    soup_base=p["soup_base"],
                    key_details=p["key_details"],
                    source="preset"
                ))
            db.commit()
            print(f"✅ 已导入 {len(PRESET_PUZZLES)} 个预置题目")
    finally:
        db.close()
    yield
    game_states.clear()

app = FastAPI(
    title="AI海龟汤",
    description="AI驱动的海龟汤解谜游戏",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== Pydantic 模型 ==========
class LLMConfig(BaseModel):
    api_key: str
    base_url: str = "https://api.moonshot.cn/v1"
    model: str = "moonshot-v1-8k"

class StartGameRequest(BaseModel):
    mode: str  # "ai" | "preset"
    puzzle_id: Optional[int] = None
    llm_config: LLMConfig

class AskRequest(BaseModel):
    question: str
    llm_config: LLMConfig

class GuessRequest(BaseModel):
    guess: str
    llm_config: LLMConfig

class GeneratePuzzleRequest(BaseModel):
    llm_config: LLMConfig

class PuzzleOut(BaseModel):
    id: int
    title: str
    soup_surface: str
    source: str
    play_count: int
    solve_count: int

    class Config:
        from_attributes = True

# ========== 全局异常处理 ==========
import traceback

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    stack = traceback.format_exc()
    print(f"[ERROR] {request.url.path}: {exc}\n{stack}")
    return {"detail": f"服务器内部错误: {str(exc)}\n{stack}"}

# ========== API 路由 ==========

@app.get("/puzzles", response_model=list[PuzzleOut])
def list_puzzles(db: Session = Depends(get_db)):
    """获取所有预置题库"""
    puzzles = db.query(Puzzle).filter(Puzzle.source == "preset").all()
    return puzzles

@app.post("/puzzle/generate")
async def generate_puzzle(req: GeneratePuzzleRequest, db: Session = Depends(get_db)):
    """AI生成新题目并存入题库"""
    try:
        puzzle_data = await llm_service.generate_puzzle(req.llm_config.model_dump())
        puzzle = Puzzle(
            title=puzzle_data["title"],
            soup_surface=puzzle_data["soup_surface"],
            soup_base=puzzle_data["soup_base"],
            key_details=puzzle_data.get("key_details", []),
            source="ai_generated"
        )
        db.add(puzzle)
        db.commit()
        db.refresh(puzzle)
        return {
            "id": puzzle.id,
            "title": puzzle.title,
            "soup_surface": puzzle.soup_surface,
            "source": "ai_generated"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成题目失败: {str(e)}")

@app.post("/game/start")
async def start_game(req: StartGameRequest, db: Session = Depends(get_db)):
    """开始新游戏"""
    session_id = str(uuid.uuid4())

    if req.mode == "ai":
        # AI生成新题
        try:
            puzzle_data = await llm_service.generate_puzzle(req.llm_config.model_dump())
            puzzle = Puzzle(
                title=puzzle_data["title"],
                soup_surface=puzzle_data["soup_surface"],
                soup_base=puzzle_data["soup_base"],
                key_details=puzzle_data.get("key_details", []),
                source="ai_generated"
            )
            db.add(puzzle)
            db.commit()
            db.refresh(puzzle)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AI生成题目失败: {str(e)}")
    else:
        # 从题库选题
        if req.puzzle_id:
            puzzle = db.query(Puzzle).filter(Puzzle.id == req.puzzle_id).first()
            if not puzzle:
                raise HTTPException(status_code=404, detail="题目不存在")
        else:
            import random
            puzzles = db.query(Puzzle).all()
            if not puzzles:
                raise HTTPException(status_code=404, detail="题库为空")
            puzzle = random.choice(puzzles)

    # 创建游戏状态
    state = GameState(
        session_id=session_id,
        puzzle_id=puzzle.id,
        soup_surface=puzzle.soup_surface,
        soup_base=puzzle.soup_base,
        key_details=puzzle.key_details or [],
        mode=req.mode
    )
    game_states[session_id] = state

    # 创建对局记录
    db.add(GameSession(
        id=session_id,
        puzzle_id=puzzle.id,
        mode=req.mode
    ))
    db.commit()

    # 增加游玩次数
    puzzle.play_count += 1
    db.commit()

    return {
        "session_id": session_id,
        "soup_surface": puzzle.soup_surface,
        "round": 0,
        "max_rounds": 30,
        "status": "playing",
        "mode": req.mode
    }

@app.post("/game/{session_id}/ask")
async def ask_question(session_id: str, req: AskRequest, db: Session = Depends(get_db)):
    """玩家提问"""
    state = game_states.get(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="游戏不存在或已过期")

    if state.status != "playing":
        raise HTTPException(status_code=400, detail=f"游戏已结束，状态: {state.status}")

    if state.round >= state.max_rounds:
        state.status = "lost"
        await _save_game_end(db, state)
        return {
            "round": state.round,
            "max_rounds": state.max_rounds,
            "status": "lost",
            "message": "已达到最大回合数！",
            "answer": "",
            "type": "",
            "hint": ""
        }

    state.round += 1

    try:
        result = await llm_service.judge_question(
            soup_surface=state.soup_surface,
            soup_base=state.soup_base,
            key_details=state.key_details,
            history=state.history,
            question=req.question,
            llm_config=req.llm_config.model_dump()
        )
    except Exception as e:
        state.round -= 1
        raise HTTPException(status_code=500, detail=f"LLM判定失败: {str(e)}")

    # 记录历史
    state.history.append({
        "round": state.round,
        "question": req.question,
        "answer": result.get("answer", ""),
        "type": result.get("type", "无关"),
        "reasoning": result.get("reasoning", "")
    })

    # 检查是否达到最大回合
    if state.round >= state.max_rounds:
        state.status = "lost"
        await _save_game_end(db, state)

    return {
        "round": state.round,
        "max_rounds": state.max_rounds,
        "status": state.status,
        "answer": result.get("answer", ""),
        "type": result.get("type", "无关"),
        "hint": result.get("reasoning", "")[:50],
        "history": state.history
    }

@app.post("/game/{session_id}/guess")
async def guess_truth(session_id: str, req: GuessRequest, db: Session = Depends(get_db)):
    """玩家猜真相"""
    state = game_states.get(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="游戏不存在或已过期")

    if state.status != "playing":
        raise HTTPException(status_code=400, detail=f"游戏已结束，状态: {state.status}")

    state.round += 1
    state.final_guess = req.guess

    try:
        result = await llm_service.judge_guess(
            soup_surface=state.soup_surface,
            soup_base=state.soup_base,
            guess=req.guess,
            llm_config=req.llm_config.model_dump()
        )
    except Exception as e:
        state.round -= 1
        raise HTTPException(status_code=500, detail=f"LLM判定失败: {str(e)}")

    is_correct = result.get("correct", False)
    if is_correct:
        state.status = "won"
        # 增加解题次数
        puzzle = db.query(Puzzle).filter(Puzzle.id == state.puzzle_id).first()
        if puzzle:
            puzzle.solve_count += 1
            db.commit()
    else:
        state.status = "lost"

    await _save_game_end(db, state)

    return {
        "correct": is_correct,
        "feedback": result.get("feedback", ""),
        "round": state.round,
        "status": state.status,
        "soup_base": state.soup_base if is_correct else None
    }

@app.post("/game/{session_id}/reveal")
async def reveal_answer(session_id: str, db: Session = Depends(get_db)):
    """揭晓汤底"""
    state = game_states.get(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="游戏不存在或已过期")

    if state.status == "playing":
        state.status = "revealed"
        await _save_game_end(db, state)

    return {
        "soup_base": state.soup_base,
        "key_details": state.key_details,
        "round": state.round,
        "status": state.status
    }

@app.get("/game/{session_id}")
def get_game_state(session_id: str):
    """获取游戏状态"""
    state = game_states.get(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="游戏不存在或已过期")

    return {
        "session_id": state.session_id,
        "soup_surface": state.soup_surface,
        "round": state.round,
        "max_rounds": state.max_rounds,
        "status": state.status,
        "history": state.history,
        "mode": state.mode
    }

@app.get("/game/{session_id}/history")
def get_game_history(session_id: str):
    """获取游戏历史"""
    state = game_states.get(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="游戏不存在或已过期")

    return {
        "history": state.history,
        "round": state.round,
        "max_rounds": state.max_rounds
    }

# ========== 调试端点 ==========
class DebugLLMRequest(BaseModel):
    llm_config: LLMConfig

@app.post("/debug/llm")
async def debug_llm(req: DebugLLMRequest):
    """调试用：验证 LLM 配置是否正确传递"""
    cfg = req.llm_config.model_dump()
    api_key = cfg.get("api_key", "").strip()
    
    # 安全地返回 key 的部分信息（不暴露完整 key）
    return {
        "base_url": cfg.get("base_url"),
        "model": cfg.get("model"),
        "api_key_length": len(api_key),
        "api_key_prefix": api_key[:10] + "..." if len(api_key) > 10 else "(empty)",
        "api_key_suffix": "..." + api_key[-4:] if len(api_key) > 4 else "(empty)",
        "has_space": " " in api_key,
        "has_newline": "\n" in api_key,
        "starts_with_sk": api_key.startswith("sk-"),
    }

# ========== 调试端点 ==========
class DebugLLMRequest(BaseModel):
    llm_config: LLMConfig

@app.post("/debug/llm")
async def debug_llm(req: DebugLLMRequest):
    """调试用：验证 LLM 配置是否正确传递"""
    cfg = req.llm_config.model_dump()
    api_key = cfg.get("api_key", "").strip()
    
    # 安全地返回 key 的部分信息（不暴露完整 key）
    return {
        "base_url": cfg.get("base_url"),
        "model": cfg.get("model"),
        "api_key_length": len(api_key),
        "api_key_prefix": api_key[:10] + "..." if len(api_key) > 10 else "(empty)",
        "api_key_suffix": "..." + api_key[-4:] if len(api_key) > 4 else "(empty)",
        "has_space": " " in api_key,
        "has_newline": "\n" in api_key,
        "starts_with_sk": api_key.startswith("sk-"),
    }

# ========== 辅助函数 ==========

async def _save_game_end(db: Session, state: GameState):
    """保存游戏结束状态到数据库"""
    session = db.query(GameSession).filter(GameSession.id == state.session_id).first()
    if session:
        session.end_time = datetime.utcnow()
        session.total_rounds = state.round
        session.solved = (state.status == "won")
        session.status = state.status
        session.history = state.history
        session.final_guess = state.final_guess
        if state.start_time:
            duration = (datetime.utcnow() - state.start_time).total_seconds()
            session.duration_seconds = int(duration)
        db.commit()

# ========== 启动 ==========
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
