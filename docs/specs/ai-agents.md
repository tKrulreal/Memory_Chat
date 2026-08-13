# AI-AGENTS.md — AI Agent Architecture

## MemoryChat MVP v1.0

---

## 1. AI Agent Philosophy

### 1.1 Core Principles

MemoryChat's AI is not a chatbot — it's a **Personal Relationship Assistant**.

```
Chatbot:        "Hi! How can I help you?"
AI Assistant:   "I remember you're talking with An about the AI project at VinAI. 
                 Should I suggest a follow-up message?"
```

### 1.2 Key Design Principles

| Principle | Description |
|-----------|-------------|
| **Context-Aware** | AI always knows the current conversation, contact, and context |
| **Memory-First** | AI builds and uses persistent knowledge about contacts |
| **Human-in-the-Loop** | AI suggests, user decides |
| **Explainable** | Every recommendation has a reason |
| **Privacy-Preserving** | User data never shared between users |

### 1.3 AI vs. Traditional Chatbot

| Aspect | Chatbot | MemoryChat AI |
|--------|---------|--------------|
| Scope | General questions | Relationship context |
| Memory | Session only | Long-term |
| Actions | Direct execution | Suggestion + confirmation |
| Context | Manual input | Auto-detected |
| Output | Text | Text + structured data |

---

## 2. Agent System Overview

### 2.1 Agent Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER INTERFACE                               │
│                    AI Copilot (Bottom Sheet)                      │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ASSISTANT ORCHESTRATOR                          │
│                  (LangGraph StateGraph)                           │
│                                                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Intent Detection → Context Builder → Agent Selection       │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────┬───────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│    Memory     │     │    Search     │     │  Recommendation│
│    Agent      │     │    Agent      │     │    Agent       │
└───────┬───────┘     └───────┬───────┘     └───────┬───────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        LLM GATEWAY                                │
│              (OpenAI / Claude / Gemini / Local)                   │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Agent Responsibilities

| Agent | Responsibility | Input | Output |
|-------|---------------|-------|--------|
| **Memory Agent** | Build contact knowledge | Conversation | Contact Memory |
| **Search Agent** | Semantic search | Natural query | Matching contacts |
| **Recommendation Agent** | Proactive suggestions | Contact data | Recommendations |
| **Tagging Agent** | Entity extraction | Conversation | Suggested tags |
| **Connection Agent** | Relationship matching | Contact pairs | Connection suggestions |
| **Insight Agent** | Behavior analysis | Contact history | Insights |

---

## 3. Assistant Orchestrator

### 3.1 Architecture

```python
# src/agents/graph.py
class AssistantOrchestrator:
    """
    Main orchestrator using LangGraph StateGraph.
    Coordinates all AI agents based on user intent.
    """
    
    async def process(self, user_message: str, context: AgentContext) -> AgentResponse:
        # 1. Detect intent
        intent = await self.detect_intent(user_message)
        
        # 2. Build context
        full_context = await self.context_builder.build(context)
        
        # 3. Select agent(s)
        agents = self.select_agents(intent)
        
        # 4. Execute agents
        results = await self.execute_agents(agents, full_context)
        
        # 5. Merge results
        merged = self.merge_results(results)
        
        # 6. Generate response
        response = await self.generate_response(merged)
        
        # 7. Validate response
        validated = await self.validator.validate(response)
        
        return validated
```

### 3.2 LangGraph State

```python
# src/agents/state.py
from typing import TypedDict, Optional
from pydantic import BaseModel
from enum import Enum

class AgentIntent(str, Enum):
    MEMORY_QUERY = "memory_query"
    SEARCH = "search"
    RECOMMEND = "recommend"
    TAG = "tag"
    CONNECT = "connect"
    INSIGHT = "insight"
    GENERAL = "general"

class AgentState(TypedDict, total=False):
    # User info
    user_id: str
    conversation_id: str
    contact_id: str
    
    # Input
    user_message: str
    
    # Processing
    intent: Optional[AgentIntent]
    selected_agents: list[str]
    context: dict
    
    # Agent outputs
    memory: Optional[dict]
    search_results: Optional[list[dict]]
    recommendations: Optional[list[dict]]
    tags: Optional[list[dict]]
    connections: Optional[list[dict]]
    insights: Optional[list[dict]]
    
    # Final output
    response: Optional[str]
    error: Optional[str]
    
    # Metadata
    token_usage: dict
    latency_ms: int
```

### 3.3 Orchestrator Graph

```python
# src/agents/graph.py
from langgraph.graph import StateGraph, END

def create_orchestrator_graph():
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("intent_detection", detect_intent_node)
    graph.add_node("context_builder", build_context_node)
    graph.add_node("memory_agent", memory_agent_node)
    graph.add_node("search_agent", search_agent_node)
    graph.add_node("recommendation_agent", recommendation_agent_node)
    graph.add_node("tagging_agent", tagging_agent_node)
    graph.add_node("merge_results", merge_results_node)
    graph.add_node("generate_response", generate_response_node)
    graph.add_node("validate_response", validate_response_node)
    
    # Define edges
    graph.add_edge("__start__", "intent_detection")
    graph.add_edge("intent_detection", "context_builder")
    graph.add_edge("context_builder", "memory_agent")
    graph.add_edge("context_builder", "search_agent")
    graph.add_edge("context_builder", "recommendation_agent")
    graph.add_edge("context_builder", "tagging_agent")
    graph.add_edge("memory_agent", "merge_results")
    graph.add_edge("search_agent", "merge_results")
    graph.add_edge("recommendation_agent", "merge_results")
    graph.add_edge("tagging_agent", "merge_results")
    graph.add_edge("merge_results", "generate_response")
    graph.add_edge("generate_response", "validate_response")
    graph.add_edge("validate_response", END)
    
    return graph.compile()
```

---

## 4. Memory Agent

### 4.1 Purpose

The Memory Agent transforms raw conversation data into structured, persistent knowledge about contacts.

### 4.2 Input → Output

```
Input                          Output
─────────────────────────────────────────────────────────────
Conversation              →    Contact Memory
  - Messages                   - Summary
  - Timeline                   - Company
  - Topics                     - Profession
                               - Skills (JSON)
                               - Interests (JSON)
                               - Timeline (JSON)
                               - Relationship Score (0-100)
                               - Last Discussion
```

### 4.3 Workflow

```python
async def memory_agent_workflow(conversation_id: str) -> ContactMemory:
    # 1. Load conversation
    messages = await message_repo.get_recent(conversation_id, limit=100)
    
    # 2. Chunk messages
    chunks = chunk_messages(messages, chunk_size=2000)
    
    # 3. Generate summary
    summary = await llm.generate_summary(chunks)
    
    # 4. Extract entities
    entities = await llm.extract_entities(chunks)
    
    # 5. Analyze relationship
    relationship_score = await calculate_relationship_score(
        message_frequency=len(messages),
        topic_diversity=entities.topics,
        recency=messages[-1].created_at
    )
    
    # 6. Build timeline
    timeline = extract_timeline(events)
    
    # 7. Update memory
    memory = await memory_repo.upsert(contact_id, {
        "summary": summary,
        "profession": entities.profession,
        "company": entities.company,
        "skills": entities.skills,
        "interests": entities.interests,
        "timeline": timeline,
        "relationship_score": relationship_score,
        "last_discussion": entities.last_topic
    })
    
    # 8. Generate embedding
    embedding = await embedding_model.encode(summary)
    
    # 9. Upsert to vector DB
    await vector_db.upsert("contact_memory", {
        "id": memory.id,
        "embedding": embedding,
        "metadata": {"contact_id": contact_id, "summary": summary}
    })
    
    return memory
```

### 4.4 Trigger Conditions

```python
# When to update memory
MEMORY_UPDATE_TRIGGERS = {
    "conversation_idle": timedelta(minutes=5),  # 5 min no activity
    "message_count": 20,                         # 20 new messages
    "user_request": True,                        # User clicks "Refresh"
    "batch_job": "0 2 * * *",                   # 2 AM daily
    "conversation_closed": True                   # User closes chat
}
```

### 4.5 Memory Schema

```python
class ContactMemory(BaseModel):
    id: UUID
    contact_id: UUID
    summary: str
    profession: Optional[str]
    company: Optional[str]
    skills: list[str]
    interests: list[str]
    timeline: list[TimelineEvent]
    relationship_score: int  # 0-100
    last_discussion: Optional[str]
    updated_at: datetime

class TimelineEvent(BaseModel):
    date: date
    event: str  # "Discussed AI project"
    type: str   # "topic", "action", "meeting", "decision"
```

---

## 5. Search Agent

### 5.1 Purpose

The Search Agent enables natural language semantic search across contacts and conversations.

### 5.2 Example Queries

| User Query | AI Understanding | Result |
|------------|-----------------|--------|
| "Find people working on AI" | Semantic: skills ∝ "AI" | Contacts with AI skill |
| "Who did I meet at the startup event?" | Semantic: context ∝ "startup event" | Relevant contacts |
| "People interested in hiring" | Semantic: interest ∝ "hiring" | Contacts hiring |
| "Last month conversations" | Time filter: created_at > 30 days | Recent contacts |

### 5.3 Workflow

```python
async def search_agent_workflow(query: str, user_id: str) -> SearchResponse:
    # 1. Embed query
    query_embedding = await embedding_model.encode(query)
    
    # 2. Semantic search in vector DB
    candidates = await vector_db.search(
        collection="contact_memory_embeddings",
        query_embedding=query_embedding,
        n_results=20,
        filter={"user_id": user_id}
    )
    
    # 3. Get contact details
    contact_ids = [c.metadata["contact_id"] for c in candidates]
    contacts = await contact_repo.get_many(contact_ids)
    
    # 4. LLM re-ranking
    reranked = await llm.rerank_search_results(
        query=query,
        candidates=contacts,
        top_k=10
    )
    
    # 5. Generate explanation
    explanation = await llm.explain_search_results(
        query=query,
        results=reranked
    )
    
    # 6. Log search
    await search_history_repo.create(
        user_id=user_id,
        query=query,
        result_count=len(reranked)
    )
    
    return SearchResponse(
        query=query,
        results=reranked,
        explanation=explanation,
        total=len(reranked)
    )
```

### 5.4 Search Response Format

```python
class SearchResponse(BaseModel):
    query: str
    results: list[ContactSearchResult]
    explanation: str
    total: int

class ContactSearchResult(BaseModel):
    contact: Contact
    memory: Optional[ContactMemory]
    score: float  # 0-1 relevance
    match_reason: str  # "Shared interest in AI projects"
```

---

## 6. Recommendation Agent

### 6.1 Purpose

The Recommendation Agent proactively suggests actions to help users maintain relationships.

### 6.2 Recommendation Types

| Type | Description | Example |
|------|-------------|---------|
| **Follow-up** | Contacts to reach out to | "You haven't talked to An in 30 days" |
| **Reply** | Suggested responses | "Draft: 'Thanks for the update on the project...'" |
| **Tag** | Suggested tags | "Based on conversation, suggest adding 'AI project'" |
| **Connection** | Introduction suggestions | "An and Binh both work in AI, they might know each other" |
| **Priority** | High-value contacts | "This contact has high engagement, prioritize" |
| **Merge** | Duplicate detection | "These two contacts might be the same person" |

### 6.3 Workflow

```python
async def recommendation_agent_workflow(user_id: str) -> list[Recommendation]:
    # 1. Get all contacts with memory
    contacts = await contact_repo.get_all_with_memory(user_id)
    
    # 2. Generate candidates
    candidates = []
    
    # Follow-up candidates
    for contact in contacts:
        days_since_contact = (now() - contact.last_message_time).days
        if days_since_contact > 14:
            candidates.append(RecommendationCandidate(
                type="FOLLOWUP",
                contact_id=contact.id,
                priority=calculate_followup_priority(days_since_contact, contact.relationship_score)
            ))
    
    # Connection candidates
    similar_pairs = await find_similar_contacts(contacts)
    for pair in similar_pairs:
        candidates.append(RecommendationCandidate(
            type="CONNECTION",
            contact_ids=[pair.contact1_id, pair.contact2_id],
            reason=f"Both interested in {pair.shared_interest}"
        ))
    
    # 3. Filter with rules
    filtered = apply_recommendation_rules(candidates)
    
    # 4. Generate explanations
    recommendations = []
    for candidate in filtered:
        reason = await llm.generate_recommendation_reason(candidate)
        recommendations.append(Recommendation(
            **candidate.dict(),
            reason=reason
        ))
    
    # 5. Save recommendations
    for rec in recommendations:
        await recommendation_repo.create(rec)
    
    return recommendations
```

### 6.4 Recommendation Schema

```python
class Recommendation(BaseModel):
    id: UUID
    contact_id: Optional[UUID]  # For single-contact recommendations
    contact_ids: Optional[list[UUID]]  # For connection recommendations
    type: RecommendationType
    reason: str
    priority: Priority
    status: RecommendationStatus = RecommendationStatus.PENDING
    created_at: datetime
    acted_at: Optional[datetime]
    
    def explain(self) -> str:
        return f"[{self.priority.value}] {self.type.value}: {self.reason}"
```

---

## 7. Tagging Agent

### 7.1 Purpose

The Tagging Agent extracts structured information from conversations and suggests tags.

### 7.2 Extractable Entities

```python
class ExtractedEntities(BaseModel):
    companies: list[str]      # "VinAI", "FPT", "Google"
    professions: list[str]    # "AI Engineer", "Product Manager"
    skills: list[str]          # "Python", "Machine Learning", "Leadership"
    interests: list[str]       # "Startup", "AI", "Travel"
    topics: list[str]          # "AI project", "Hiring", "Partnership"
    organizations: list[str]   # "VinUni", "VNExpress"
    locations: list[str]       # "Hanoi", "Ho Chi Minh City"
    dates: list[date]         # "Next Monday", "August 15"
    actions: list[str]         # "Call back", "Send email"
```

### 7.3 Workflow

```python
async def tagging_agent_workflow(conversation_id: str) -> list[TagSuggestion]:
    # 1. Get recent messages
    messages = await message_repo.get_recent(conversation_id, limit=50)
    
    # 2. Extract entities
    entities = await llm.extract_entities(messages)
    
    # 3. Get existing tags
    existing_tags = await tag_repo.get_for_contact(contact_id)
    
    # 4. Generate suggestions
    suggestions = []
    for entity_type, values in entities.dict().items():
        for value in values:
            # Check if tag already exists
            existing = [t for t in existing_tags if t.name == value]
            if not existing:
                suggestions.append(TagSuggestion(
                    entity_type=entity_type,
                    value=value,
                    confidence=entities.confidence.get(value, 0.8),
                    conversation_context=extract_context_snippet(messages, value)
                ))
    
    # 5. Remove low-confidence suggestions
    high_confidence = [s for s in suggestions if s.confidence > 0.7]
    
    return high_confidence
```

### 7.4 Tag Suggestion Schema

```python
class TagSuggestion(BaseModel):
    entity_type: str  # "company", "skill", "interest", etc.
    value: str
    confidence: float  # 0-1
    conversation_context: str
    suggested_by: str  # "AI extracted from conversation"
    
    def to_user_friendly(self) -> str:
        return f"📌 {self.value} ({self.entity_type})"
```

---

## 8. Connection Agent

### 8.1 Purpose

The Connection Agent identifies opportunities to introduce contacts to each other.

### 8.2 Example Connections

| Contacts | Common Factor | Suggestion |
|----------|---------------|------------|
| An (Founder) + Binh (AI Dev) | Both in AI | "Introduce them to discuss AI collaboration" |
| Chi (Hiring) + Dung (Engineer) | Chi hiring + Dung looking | "Dung might be a good fit for Chi's opening" |
| Emma (Investor) + Frank (Founder) | Both in startup ecosystem | "Frank might benefit from Emma's investment focus" |

### 8.3 Workflow

```python
async def connection_agent_workflow(user_id: str) -> list[ConnectionSuggestion]:
    # 1. Get all contacts with memory
    contacts = await contact_repo.get_all_with_memory(user_id)
    
    # 2. Find potential connections
    candidates = []
    for i, c1 in enumerate(contacts):
        for c2 in contacts[i+1:]:
            score = calculate_connection_score(c1, c2)
            if score > 0.6:  # Threshold
                candidates.append(ConnectionCandidate(
                    contact1=c1,
                    contact2=c2,
                    score=score,
                    factors=find_common_factors(c1, c2)
                ))
    
    # 3. Generate explanations
    suggestions = []
    for candidate in candidates:
        explanation = await llm.explain_connection(candidate)
        suggestions.append(ConnectionSuggestion(
            contact1_id=candidate.contact1.id,
            contact2_id=candidate.contact2.id,
            shared_interests=candidate.factors.interests,
            shared_skills=candidate.factors.skills,
            reason=explanation,
            confidence=candidate.score
        ))
    
    return suggestions
```

---

## 9. Insight Agent

### 9.1 Purpose

The Insight Agent generates behavioral insights about contacts.

### 9.2 Insight Types

```python
class InsightType(str, Enum):
    BEHAVIOR = "behavior"           # "Responds quickly in mornings"
    PATTERN = "pattern"             # "Discusses AI every week"
    PREFERENCE = "preference"       # "Prefers concise messages"
    OPPORTUNITY = "opportunity"     # "Might be interested in X"
    RISK = "risk"                  # "Less engaged recently"
    FACT = "fact"                  # "Works at VinAI as AI Engineer"
```

### 9.3 Example Insights

| Contact | Insight | Type | Confidence |
|---------|---------|------|------------|
| An | "Prefers morning meetings" | preference | 85% |
| An | "Has mentioned AI 15 times" | pattern | 95% |
| An | "May be open to new opportunities" | opportunity | 70% |
| An | "Engagement dropped 40% this month" | risk | 80% |

---

## 10. Tool Registry

### 10.1 Available Tools

```python
class ToolRegistry:
    """
    Central registry for all tools available to agents.
    Tools provide the interface between agents and data layer.
    """
    
    def __init__(self):
        self._tools: dict[str, Tool] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        # Memory tools
        self.register(GetContactMemory())
        self.register(UpdateContactMemory())
        self.register(GetConversationSummary())
        self.register(GetTimeline())
        
        # Search tools
        self.register(SemanticSearch())
        self.register(GetContactDetails())
        self.register(GetSearchHistory())
        
        # Recommendation tools
        self.register(GetRecommendations())
        self.register(AcceptRecommendation())
        self.register(RejectRecommendation())
        
        # Contact tools
        self.register(GetContact())
        self.register(GetContacts())
        self.register(GetConversation())
        self.register(GetMessages())
        
        # Tag tools
        self.register(GetTags())
        self.register(SuggestTags())
        self.register(AddTag())
        
    def get_tool(self, name: str) -> Tool:
        return self._tools.get(name)
    
    def list_tools(self) -> list[str]:
        return list(self._tools.keys())
```

### 10.2 Tool Definitions

```python
# Memory Tools
class GetContactMemory(BaseTool):
    name = "get_contact_memory"
    description = "Get the memory/knowledge about a contact"
    args_schema = GetContactMemoryInput
    
    async def _run(self, contact_id: str) -> ContactMemory:
        return await memory_repo.get_by_contact(contact_id)

class SemanticSearch(BaseTool):
    name = "semantic_search"
    description = "Search contacts using natural language"
    args_schema = SemanticSearchInput
    
    async def _run(self, query: str, user_id: str) -> SearchResponse:
        return await search_agent.search(query, user_id)

class GetRecommendations(BaseTool):
    name = "get_recommendations"
    description = "Get AI recommendations for contacts"
    args_schema = GetRecommendationsInput
    
    async def _run(self, contact_id: str, limit: int = 10) -> list[Recommendation]:
        return await recommendation_repo.get_pending(contact_id, limit)
```

---

## 11. LLM Gateway

### 11.1 Purpose

The LLM Gateway provides a unified interface to LLM providers.

### 11.2 Architecture

```python
# src/llm/gateway.py
class LLMGateway:
    """
    Unified interface for LLM providers.
    Supports OpenAI, Anthropic, Google, and local models.
    """
    
    def __init__(self, provider: str = "openai", model: str = "gpt-4o-mini"):
        self.provider = provider
        self.model = model
        self._client = self._init_client()
    
    async def chat(self, messages: list[ChatMessage], **kwargs) -> ChatResponse:
        # Route to appropriate provider
        if self.provider == "openai":
            return await self._openai_chat(messages, **kwargs)
        elif self.provider == "anthropic":
            return await self._anthropic_chat(messages, **kwargs)
        elif self.provider == "google":
            return await self._google_chat(messages, **kwargs)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    async def embed(self, texts: list[str]) -> list[list[float]]:
        return await self._openai_embed(texts)
```

### 11.3 Provider Support

| Provider | Model | Use Case | Cost |
|----------|-------|----------|------|
| OpenAI | gpt-4o-mini | General tasks | Low |
| OpenAI | gpt-4o | Complex reasoning | High |
| Anthropic | claude-3.5-sonnet | Complex tasks | Medium |
| Google | gemini-1.5-pro | Multimodal | Medium |
| Local | llama3.1 8B | Privacy, offline | Free |

---

## 12. Prompt Templates

### 12.1 Memory Agent Prompts

```python
# System prompt for memory extraction
MEMORY_EXTRACTION_SYSTEM = """
You are a helpful assistant that extracts structured information from conversations.

Given a conversation, extract:
1. **Summary**: A brief summary of what this conversation was about
2. **Companies mentioned**: Company names
3. **Professions**: Job titles or roles
4. **Skills**: Technical or professional skills mentioned
5. **Interests**: Topics the person seems interested in
6. **Key facts**: Important facts about this person

Be concise and only extract information that was explicitly mentioned or strongly implied.
"""

# User prompt template
MEMORY_EXTRACTION_USER = """
Extract information from this conversation:

---
{conversation_text}
---

Contact name: {contact_name}

{format_instructions}
"""
```

### 12.2 Search Agent Prompts

```python
SEARCH_RERANK_SYSTEM = """
You are helping rerank search results for a query about contacts.
Given a user's natural language query and a list of contacts with their memories,
rank the contacts by relevance to the query and explain why each is relevant.
"""

RECOMMENDATION_REASON_SYSTEM = """
You are a helpful assistant that explains why you recommend a specific action.
Given the context, generate a clear, concise reason for the recommendation.
The reason should help the user understand the value of taking action.
"""
```

---

## 13. Response Validation

### 13.1 Validation Rules

```python
class ResponseValidator:
    """
    Validates AI responses before returning to user.
    """
    
    async def validate(self, response: str, context: AgentContext) -> ValidationResult:
        issues = []
        
        # Check for data leakage
        if self._contains_other_user_data(response, context.user_id):
            issues.append(ValidationIssue(
                type="data_leakage",
                severity="high",
                message="Response may contain data from other users"
            ))
        
        # Check for prompt injection
        if self._contains_injection_patterns(response):
            issues.append(ValidationIssue(
                type="prompt_injection",
                severity="high",
                message="Response may contain injected content"
            ))
        
        # Check for PII (future)
        if self._contains_pii(response):
            issues.append(ValidationIssue(
                type="pii",
                severity="medium",
                message="Response may contain personal information"
            ))
        
        # Check for off-topic content
        if not self._is_topical(response, context.user_message):
            issues.append(ValidationIssue(
                type="off_topic",
                severity="low",
                message="Response may not fully address the query"
            ))
        
        return ValidationResult(
            is_valid=len([i for i in issues if i.severity == "high"]) == 0,
            issues=issues,
            sanitized_response=self._sanitize(response) if issues else response
        )
```

---

## 14. Cost Optimization

### 14.1 Strategies

| Strategy | Implementation | Savings |
|----------|---------------|---------|
| **Batch Processing** | Group messages before calling LLM | 60-80% |
| **Caching** | Cache LLM responses | 30-50% |
| **Incremental Embedding** | Only embed new/changed data | 40-60% |
| **Model Selection** | Use gpt-4o-mini for simple tasks | 80-90% |
| **Context Compression** | Summarize old messages | 30-50% |
| **Rule-based Pre-filtering** | Filter before LLM call | 20-40% |

### 14.2 Batch Processing Example

```python
# Instead of calling LLM for each message
async def process_messages_individually(messages: list[Message]):
    results = []
    for msg in messages:
        result = await llm.extract_entity(msg)  # Expensive!
        results.append(result)
    return results

# Batch processing is much cheaper
async def process_messages_batch(messages: list[Message]):
    combined = "\n".join([f"{m.sender}: {m.content}" for m in messages])
    results = await llm.extract_entities_batch(combined)  # One call
    return results
```

---

## 15. Agent Collaboration

### 15.1 Multi-Agent Requests

```python
# Example: "Who is An and should I follow up?"
async def handle_complex_request(message: str, context: AgentContext):
    # Step 1: Memory Agent - Who is An?
    memory = await memory_agent.get_contact_memory(context.contact_id)
    
    # Step 2: Recommendation Agent - Should I follow up?
    recs = await recommendation_agent.get_recommendations(context.contact_id)
    followup_rec = next((r for r in recs if r.type == "FOLLOWUP"), None)
    
    # Step 3: Merge results
    response = f"""
    Based on your conversations:
    
    **{memory.summary}**
    
    - Works at: {memory.company}
    - Role: {memory.profession}
    - Relationship score: {memory.relationship_score}/100
    
    **Follow-up suggestion:**
    {followup_rec.reason if followup_rec else "No specific follow-up needed right now."}
    """
    
    return response
```

---

## 16. MCP Integration (Future)

### 16.1 Model Context Protocol

The architecture is designed to be MCP-compatible for future integrations:

```python
# Future MCP Server integration
class MCPToolAdapter:
    """
    Adapter to expose MemoryChat tools via MCP protocol.
    """
    
    async def get_mcp_tools(self) -> list[MCPTool]:
        return [
            MCPTool(
                name="memorychat.get_contact_memory",
                description="Get memory about a contact",
                input_schema=GetContactMemorySchema,
                handler=self.get_contact_memory_handler
            ),
            MCPTool(
                name="memorychat.search_contacts",
                description="Search contacts semantically",
                input_schema=SearchContactsSchema,
                handler=self.search_contacts_handler
            ),
            # ... more tools
        ]
```

---

## 17. Error Handling

### 17.1 Error Types

```python
class AgentError(str, Enum):
    LLM_ERROR = "llm_error"           # LLM API failure
    TIMEOUT = "timeout"                # Request timeout
    VALIDATION_ERROR = "validation"   # Output validation failed
    CONTEXT_ERROR = "context"         # Missing/invalid context
    TOOL_ERROR = "tool_error"        # Tool execution failed

class AgentException(Exception):
    def __init__(self, error_type: AgentError, message: str, details: dict = None):
        self.error_type = error_type
        self.message = message
        self.details = details or {}
```

### 17.2 Recovery Strategies

```python
async def execute_with_retry(agent_func, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            return await agent_func()
        except LLMError as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                continue
            raise AgentException(
                error_type=AgentError.LLM_ERROR,
                message="LLM request failed after retries",
                details={"attempts": max_retries}
            )
```

---

*Document Version: 1.0*  
*Last Updated: 2026-08-13*
