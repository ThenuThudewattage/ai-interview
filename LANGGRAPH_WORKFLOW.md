# LangGraph Workflow Design & Multi-Agent Orchestration

## Overview

This document details the LangGraph implementation for multi-agent orchestration, workflow compilation, and interview flow management.

---

## 1. LangGraph Architecture Overview

### 1.1 Graph Structure

```
┌─────────────────────────────────────────────────────────────┐
│                  Interview Workflow Graph                    │
│           (Compiled LangGraph State Machine)                 │
└─────────────────────────────────────────────────────────────┘

ENTRY
  │
  ▼
┌──────────────────────────────┐
│   Initialize Interview       │
│   • Load user context        │
│   • Load user skills         │
│   • Determine starting topic │
└──────────────┬───────────────┘
               │
      ┌────────┴────────┐
      │                 │
      ▼                 ▼
   [LOOP START]    [BRANCH: First Interview?]
   ┌────────────────────┐
   │  Orchestrator Node │
   │ (Decision Point)   │
   └────────┬───────────┘
            │
   ┌────────┴─────────────────────────┐
   │                                  │
   ▼                                  ▼
[Generate Question]            [Process Answer]
   │                                  │
   │                                  ▼
   │                          [Interview Agent Evaluates]
   │                                  │
   │                                  ▼
   │                          [Feedback Agent Evaluates]
   │                                  │
   │                                  ▼
   │                          [Update Metrics]
   │                                  │
   │                                  ▼
   │                          [Learning Agent Analyzes]
   │                                  │
   │                                  ▼
   │                          [Difficulty Adjustment]
   │                                  │
   └────────────┬─────────────────────┘
                │
    ┌───────────┴───────────────────┐
    │                               │
    ▼                               ▼
[Questions Remaining?]         [LOOP END]
    │                               │
 YES│                               │NO
    │                               ▼
    │                        [Generate Report]
    │                               │
    │                               ▼
    │                        [Complete Interview]
    │                               │
    └───────────────────┬───────────┘
                        │
                        ▼
                      EXIT
```

### 1.2 State Schema

```python
from typing import Annotated, TypedDict, Optional, List
from langgraph.graph.message import add_messages

class InterviewState(TypedDict):
    """Shared state across all agents"""
    
    # Session Info
    user_id: str
    interview_id: str
    session_id: str
    
    # Interview Config
    interview_type: str  # system_design, algorithms, behavioral
    difficulty_level: str  # easy, medium, hard, expert
    target_company: Optional[str]
    
    # Context
    user_context: dict  # User profile, preferences
    user_skills: dict  # Current skill levels
    interview_history: List[dict]  # Previous interviews
    
    # Current State
    messages: Annotated[list, add_messages]  # Message history
    current_question: Optional[dict]
    current_answer: Optional[str]
    current_evaluation: Optional[dict]
    
    # Metrics
    questions_asked: int
    current_score: float  # Running average
    technical_score: float
    communication_score: float
    
    # Decision Making
    next_action: str  # generate_question, process_answer, conclude
    should_increase_difficulty: bool
    should_decrease_difficulty: bool
    difficulty_adjustments: int
    
    # Metadata
    start_time: datetime
    elapsed_time: int  # seconds
    messages_count: int
    
    # Observability
    correlation_id: str
    tracing_id: str
    events: List[dict]  # Event log
```

---

## 2. Node Definitions

### 2.1 Initialize Node

```python
from langgraph.graph import StateGraph

async def initialize_interview_node(state: InterviewState) -> InterviewState:
    """
    Initialize interview session
    
    Tasks:
    1. Load user profile and skills
    2. Retrieve interview history
    3. Determine starting difficulty
    4. Initialize metrics
    """
    
    # Load user context
    user = await user_service.get_profile(state["user_id"])
    user_skills = await skill_service.get_user_skills(state["user_id"])
    
    # Load interview history for context
    interview_history = await interview_service.get_recent_interviews(
        user_id=state["user_id"],
        interview_type=state["interview_type"],
        limit=5
    )
    
    # Determine starting difficulty
    if interview_history:
        last_avg_score = interview_history[0].get("overall_score", 50)
        starting_difficulty = determine_difficulty(last_avg_score)
    else:
        starting_difficulty = state.get("difficulty_level", "medium")
    
    # Emit event
    emit_event("interview_initialized", {
        "user_id": state["user_id"],
        "starting_difficulty": starting_difficulty
    })
    
    return {
        **state,
        "user_context": user,
        "user_skills": user_skills,
        "interview_history": interview_history,
        "difficulty_level": starting_difficulty,
        "current_score": 70,
        "questions_asked": 0,
        "next_action": "generate_question"
    }
```

### 2.2 Generate Question Node

```python
async def generate_question_node(state: InterviewState) -> InterviewState:
    """
    Generate next interview question using Interview Agent
    
    Tasks:
    1. Search knowledge base for candidate questions
    2. Filter by skill area, difficulty, exclusions
    3. Use Interview Agent to select best question
    4. Add follow-up hints
    """
    
    with tracer.start_as_current_span("generate_question"):
        # Get context
        user_skills = state["user_skills"]
        current_difficulty = state["difficulty_level"]
        questions_asked = state["questions_asked"]
        
        # Determine next skill area to focus on
        focus_skill = determine_next_skill_focus(
            user_skills=user_skills,
            interview_type=state["interview_type"]
        )
        
        # Search knowledge base
        candidate_questions = await rag_service.search_questions(
            skill_area=focus_skill,
            difficulty=current_difficulty,
            exclude_ids=[q["id"] for q in state.get("interview_history", [])],
            limit=5
        )
        
        # Use Interview Agent to select question
        interview_agent_response = await interview_agent.invoke({
            "candidates": candidate_questions,
            "user_context": state["user_context"],
            "previous_scores": state.get("messages", [])[-3:],
            "next_skill_area": focus_skill
        })
        
        selected_question = interview_agent_response["selected_question"]
        
        # Log cost
        log_llm_cost(
            agent="interview_agent",
            model=interview_agent_response["model"],
            tokens=interview_agent_response["tokens_used"],
            cost=interview_agent_response["cost_usd"]
        )
        
        # Add to messages
        new_messages = state["messages"] + [
            {
                "role": "assistant",
                "content": selected_question["content"],
                "type": "question",
                "question_id": selected_question["id"]
            }
        ]
        
        return {
            **state,
            "current_question": selected_question,
            "messages": new_messages,
            "questions_asked": questions_asked + 1,
            "next_action": "process_answer"
        }
```

### 2.3 Process Answer Node

```python
async def process_answer_node(state: InterviewState) -> InterviewState:
    """
    Process user's answer
    
    Tasks:
    1. Receive answer from user
    2. Store in database
    3. Prepare for evaluation
    """
    
    # For this node, the answer comes from external input
    # In a real system, this would be triggered by API call
    
    current_answer = state["current_answer"]
    current_question = state["current_question"]
    
    # Store answer
    answer = await answer_service.create_answer(
        interview_id=state["interview_id"],
        question_id=current_question["id"],
        answer_text=current_answer
    )
    
    # Add to messages
    new_messages = state["messages"] + [
        {
            "role": "user",
            "content": current_answer,
            "type": "answer",
            "answer_id": answer.id
        }
    ]
    
    return {
        **state,
        "messages": new_messages,
        "next_action": "evaluate_answer"
    }
```

### 2.4 Evaluate Answer Node (Feedback Agent)

```python
async def evaluate_answer_node(state: InterviewState) -> InterviewState:
    """
    Evaluate answer using Feedback Agent
    
    Tasks:
    1. Call Feedback Agent for structured evaluation
    2. Calculate scores
    3. Generate feedback
    4. Identify gaps
    """
    
    with tracer.start_as_current_span("evaluate_answer"):
        current_question = state["current_question"]
        current_answer = state["current_answer"]
        
        # Get expected answer context from RAG
        expected_context = await rag_service.get_expected_answer_context(
            question_id=current_question["id"]
        )
        
        # Call Feedback Agent
        evaluation = await feedback_agent.invoke({
            "question": current_question,
            "answer": current_answer,
            "expected_context": expected_context,
            "rubric_type": state["interview_type"]
        })
        
        # Extract scores
        scores = {
            "technical_accuracy": evaluation["technical_accuracy"],
            "completeness": evaluation["completeness"],
            "communication": evaluation["communication"],
            "problem_solving": evaluation["problem_solving"],
            "confidence": evaluation["confidence"],
            "overall": evaluation["overall_score"]
        }
        
        # Update running average
        prev_score = state["current_score"]
        new_score = (prev_score * (state["questions_asked"] - 1) + scores["overall"]) / state["questions_asked"]
        
        # Store evaluation
        eval_record = await evaluation_service.create_evaluation(
            answer_id=state["current_answer"],  # Would need to track this
            scores=scores,
            feedback=evaluation["feedback"],
            gaps=evaluation["gaps_identified"]
        )
        
        # Log cost
        log_llm_cost(
            agent="feedback_agent",
            model=evaluation["model"],
            tokens=evaluation["tokens_used"],
            cost=evaluation["cost_usd"]
        )
        
        return {
            **state,
            "current_evaluation": evaluation,
            "current_score": new_score,
            "technical_score": scores["technical_accuracy"],
            "communication_score": scores["communication"],
            "next_action": "analyze_and_adjust"
        }
```

### 2.5 Analyze & Adjust Difficulty Node

```python
async def analyze_and_adjust_node(state: InterviewState) -> InterviewState:
    """
    Analyze evaluation and adjust difficulty for next question
    
    Tasks:
    1. Analyze current score
    2. Determine difficulty adjustment
    3. Update Interview Agent state
    """
    
    evaluation = state["current_evaluation"]
    overall_score = evaluation["overall_score"]
    current_difficulty = state["difficulty_level"]
    adjustments_count = state["difficulty_adjustments"]
    
    # Difficulty adjustment logic
    should_increase = False
    should_decrease = False
    new_difficulty = current_difficulty
    
    if overall_score >= 85 and adjustments_count < 3:
        should_increase = True
        new_difficulty = increase_difficulty(current_difficulty)
        adjustments_count += 1
    elif overall_score < 60 and adjustments_count > -3:
        should_decrease = True
        new_difficulty = decrease_difficulty(current_difficulty)
        adjustments_count -= 1
    
    # Emit difficulty adjustment event
    if should_increase or should_decrease:
        emit_event("difficulty_adjusted", {
            "from": current_difficulty,
            "to": new_difficulty,
            "reason": "Score: " + str(overall_score)
        })
    
    # Check if interview should end
    total_questions = state.get("total_questions_planned", 5)
    should_conclude = state["questions_asked"] >= total_questions
    
    next_action = "conclude" if should_conclude else "generate_question"
    
    return {
        **state,
        "difficulty_level": new_difficulty,
        "should_increase_difficulty": should_increase,
        "should_decrease_difficulty": should_decrease,
        "difficulty_adjustments": adjustments_count,
        "next_action": next_action
    }
```

### 2.6 Learning Agent Analysis Node

```python
async def learning_agent_analysis_node(state: InterviewState) -> InterviewState:
    """
    Learning Agent analyzes performance and identifies gaps
    
    Tasks:
    1. Analyze evaluation results
    2. Identify skill gaps
    3. Prepare learning recommendations
    """
    
    with tracer.start_as_current_span("learning_agent_analysis"):
        current_evaluation = state["current_evaluation"]
        user_skills = state["user_skills"]
        
        # Call Learning Agent
        analysis = await learning_agent.invoke({
            "evaluation": current_evaluation,
            "user_skills": user_skills,
            "interview_type": state["interview_type"]
        })
        
        # Store gap analysis
        for gap in analysis.get("gaps_identified", []):
            await skill_gap_service.create_gap(
                user_id=state["user_id"],
                skill_area=gap["skill"],
                severity=gap["severity"],
                related_interview_id=state["interview_id"]
            )
        
        # Log cost
        log_llm_cost(
            agent="learning_agent",
            model=analysis["model"],
            tokens=analysis["tokens_used"],
            cost=analysis["cost_usd"]
        )
        
        # Emit event
        emit_event("gaps_analyzed", {
            "gaps": analysis.get("gaps_identified", [])
        })
        
        return {
            **state,
            "events": state["events"] + [
                {
                    "type": "gaps_analyzed",
                    "data": analysis
                }
            ]
        }
```

### 2.7 Conclude Interview Node

```python
async def conclude_interview_node(state: InterviewState) -> InterviewState:
    """
    Generate interview report and complete session
    
    Tasks:
    1. Calculate final scores
    2. Generate feedback report
    3. Create learning recommendations
    4. Update user profiles
    """
    
    with tracer.start_as_current_span("conclude_interview"):
        # Calculate final metrics
        final_metrics = {
            "overall_score": state["current_score"],
            "technical_score": state["technical_score"],
            "communication_score": state["communication_score"],
            "total_questions": state["questions_asked"],
            "difficulty_adjustments": state["difficulty_adjustments"]
        }
        
        # Update user skills based on performance
        for skill_area, proficiency in state["user_skills"].items():
            # Adjust based on interview performance
            adjustment = calculate_skill_adjustment(
                current_proficiency=proficiency,
                interview_score=final_metrics["overall_score"],
                skill_area=skill_area
            )
            
            new_proficiency = proficiency + adjustment
            await skill_service.update_skill(
                user_id=state["user_id"],
                skill_area=skill_area,
                proficiency=new_proficiency
            )
        
        # Complete interview in database
        await interview_service.complete_interview(
            interview_id=state["interview_id"],
            metrics=final_metrics
        )
        
        # Emit completion event
        emit_event("interview_completed", {
            "interview_id": state["interview_id"],
            "final_score": final_metrics["overall_score"]
        })
        
        return {
            **state,
            "next_action": "exit"
        }
```

---

## 3. Conditional Edges (Router Logic)

```python
def orchestrator_router(state: InterviewState) -> str:
    """
    Route to next node based on current state
    
    Returns: str (next node name)
    """
    
    next_action = state.get("next_action")
    
    routing_map = {
        "generate_question": "generate_question",
        "process_answer": "process_answer",
        "evaluate_answer": "evaluate_answer",
        "analyze_and_adjust": "analyze_and_adjust",
        "conclude": "conclude_interview",
        "exit": "__end__"
    }
    
    return routing_map.get(next_action, "generate_question")
```

---

## 4. Graph Compilation

```python
from langgraph.graph import StateGraph, END

def create_interview_workflow() -> CompiledGraph:
    """
    Create and compile the interview workflow graph
    """
    
    # Initialize graph
    workflow = StateGraph(InterviewState)
    
    # Add nodes
    workflow.add_node("initialize", initialize_interview_node)
    workflow.add_node("generate_question", generate_question_node)
    workflow.add_node("process_answer", process_answer_node)
    workflow.add_node("evaluate_answer", evaluate_answer_node)
    workflow.add_node("analyze_and_adjust", analyze_and_adjust_node)
    workflow.add_node("learning_analysis", learning_agent_analysis_node)
    workflow.add_node("conclude_interview", conclude_interview_node)
    
    # Set entry point
    workflow.set_entry_point("initialize")
    
    # Add edges
    workflow.add_edge("initialize", "generate_question")
    
    # Conditional edges
    workflow.add_conditional_edges(
        "generate_question",
        orchestrator_router
    )
    
    workflow.add_edge("process_answer", "evaluate_answer")
    workflow.add_edge("evaluate_answer", "learning_analysis")
    workflow.add_edge("learning_analysis", "analyze_and_adjust")
    
    workflow.add_conditional_edges(
        "analyze_and_adjust",
        orchestrator_router
    )
    
    workflow.add_edge("conclude_interview", END)
    
    # Compile
    compiled = workflow.compile()
    
    return compiled
```

---

## 5. Agent Prompts (System)

### 5.1 Interview Agent System Prompt

```
You are an experienced interview conductor for technical interviews. Your role is to:

1. **Guide the Interview Flow**: Present questions that match the candidate's current skill level,
   starting from the selected difficulty and adjusting as needed.

2. **Question Selection**: From the provided candidate questions, select the most appropriate
   based on:
   - Candidate's current performance
   - Skill gaps identified so far
   - Interview flow and variety
   - Avoiding repetition of topics

3. **Adapt Dynamically**: Be responsive to the candidate's performance:
   - If performing well: increase complexity and depth
   - If struggling: ask clarifying follow-ups or suggest hints
   - Maintain engagement throughout

4. **Professional Conduct**: 
   - Be encouraging and supportive
   - Provide constructive follow-ups
   - Note interesting responses for feedback

Context:
- Candidate Profile: {{user_context}}
- Current Performance: {{current_score}}/100
- Interview Type: {{interview_type}}
- Next Skill Focus: {{next_skill_area}}

Your job is to select from the provided questions and explain why it's the best choice.
```

### 5.2 Feedback Agent System Prompt

```
You are an expert technical interviewer trained in evaluation and feedback. Your role is to:

1. **Evaluate Answers**: Assess the candidate's answer using the provided rubric with:
   - Technical Accuracy: Is the answer correct and technically sound?
   - Completeness: Does it cover important aspects?
   - Communication: Is the explanation clear and well-structured?
   - Problem-Solving Approach: Did they demonstrate good methodology?
   - Confidence: How confident did they seem?

2. **Provide Scores**: Rate each dimension from 0-100 with justification.

3. **Identify Gaps**: Highlight missing knowledge or skills compared to expected answer.

4. **Constructive Feedback**: Provide actionable feedback that helps learning.

Rubric for {{rubric_type}} questions:
{{rubric}}

Expected Answer Context:
{{expected_context}}

Candidate's Answer:
{{answer}}

Your task is to provide structured evaluation with scores, feedback, and identified gaps.
```

### 5.3 Learning Agent System Prompt

```
You are an expert in learning design and skill development. Your role is to:

1. **Analyze Performance**: Review the candidate's evaluation and identify:
   - Which skills are strong
   - Which skills need development
   - Patterns in responses

2. **Identify Gaps**: From the evaluation, extract specific knowledge or skill gaps:
   - Be specific (not just "system design" but "database consistency models")
   - Estimate gap severity (0-1 scale)
   - Connect to interview performance

3. **Recommend Resources**: Suggest learning materials that address gaps:
   - Type: courses, books, articles, practice problems
   - Difficulty level
   - Estimated time to complete

4. **Create Roadmap**: If appropriate, suggest next interview topics to focus on.

Evaluation to analyze:
{{evaluation}}

User's current skills:
{{user_skills}}

Your task is to identify gaps, suggest resources, and recommend next steps.
```

---

## 6. Integration with FastAPI

```python
from fastapi import WebSocket
from langgraph.graph import CompiledGraph

class InterviewService:
    """Service to manage interview workflow execution"""
    
    def __init__(self):
        self.workflow: CompiledGraph = create_interview_workflow()
        self.active_sessions: Dict[str, InterviewState] = {}
    
    async def start_interview(
        self,
        user_id: str,
        interview_type: str,
        difficulty_level: str,
        websocket: WebSocket
    ) -> str:
        """Start new interview session"""
        
        session_id = generate_uuid()
        interview_id = await self._create_interview(user_id, interview_type, difficulty_level)
        
        # Initialize state
        initial_state = InterviewState(
            user_id=user_id,
            interview_id=interview_id,
            session_id=session_id,
            interview_type=interview_type,
            difficulty_level=difficulty_level,
            current_answer=None,
            messages=[],
            questions_asked=0,
            current_score=70,
            next_action="initialize",
            correlation_id=generate_uuid(),
            tracing_id=generate_uuid(),
            events=[]
        )
        
        # Store session
        self.active_sessions[session_id] = initial_state
        
        # Execute workflow (non-blocking)
        asyncio.create_task(
            self._execute_interview_workflow(session_id, websocket)
        )
        
        return session_id
    
    async def _execute_interview_workflow(
        self,
        session_id: str,
        websocket: WebSocket
    ):
        """Execute interview workflow and stream updates"""
        
        state = self.active_sessions[session_id]
        
        try:
            # Initialize workflow
            for output in self.workflow.stream(state):
                state = output
                
                # Send updates to client via WebSocket
                await self._send_state_update(websocket, state, output)
                
                # Store updated state
                self.active_sessions[session_id] = state
                
                # Check if completed
                if state.get("next_action") == "exit":
                    break
        
        except Exception as e:
            logger.error(f"Interview workflow error: {e}")
            await websocket.send_json({
                "type": "error",
                "error_code": "WORKFLOW_ERROR",
                "message": str(e)
            })
        
        finally:
            del self.active_sessions[session_id]
    
    async def submit_answer(self, session_id: str, answer: str):
        """Submit user answer to active interview"""
        
        state = self.active_sessions.get(session_id)
        if not state:
            raise ValueError("Invalid session")
        
        # Update state with answer
        state["current_answer"] = answer
        state["next_action"] = "process_answer"
```

---

## 7. Message Streaming to Frontend

```python
async def _send_state_update(
    websocket: WebSocket,
    state: InterviewState,
    workflow_output: Dict
):
    """Stream state updates to WebSocket client"""
    
    # Determine what changed
    node_name = list(workflow_output.keys())[0]
    
    if node_name == "generate_question":
        await websocket.send_json({
            "type": "question",
            "data": {
                "question_id": state["current_question"]["id"],
                "content": state["current_question"]["content"],
                "difficulty": state["difficulty_level"],
                "hints": state["current_question"].get("followup_hints", [])
            }
        })
    
    elif node_name == "evaluate_answer":
        await websocket.send_json({
            "type": "evaluation",
            "data": {
                "scores": {
                    "technical": state["current_evaluation"]["technical_accuracy"],
                    "communication": state["current_evaluation"]["communication"],
                    "overall": state["current_evaluation"]["overall_score"]
                },
                "feedback": state["current_evaluation"]["feedback"],
                "gaps": state["current_evaluation"]["gaps_identified"]
            }
        })
    
    elif node_name == "conclude_interview":
        await websocket.send_json({
            "type": "interview_complete",
            "data": {
                "final_score": state["current_score"],
                "technical_score": state["technical_score"],
                "communication_score": state["communication_score"],
                "questions_answered": state["questions_asked"]
            }
        })
```

This LangGraph design provides:
- ✅ Clear state management
- ✅ Explicit node responsibilities
- ✅ Conditional routing logic
- ✅ Seamless integration with FastAPI WebSocket
- ✅ Observability hooks at each step
- ✅ Error handling and recovery
- ✅ Extensibility for new nodes/agents
