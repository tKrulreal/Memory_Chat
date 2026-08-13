# API.md — API Specification

## MemoryChat MVP v1.0

---

## 1. API Overview

### 1.1 Base Configuration

| Environment | Base URL |
|-------------|----------|
| Development | `http://localhost:8000` |
| Staging | `https://api.staging.memorychat.vn` |
| Production | `https://api.memorychat.vn` |

### 1.2 API Versioning

All APIs are versioned under `/api/v1/`.

```
/api/v1/auth/login
/api/v1/contacts
/api/v1/conversations
/api/v1/messages
/api/v1/search
/api/v1/recommendations
/api/v1/copilot
/api/v1/memory
/api/v1/tags
/api/v1/events
```

### 1.3 Authentication

| Method | Description |
|--------|-------------|
| JWT Bearer | Access token in `Authorization: Bearer <token>` header |
| Refresh Token | Used to obtain new access token |

### 1.4 Response Format

All responses follow this format:

```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "meta": {
    "request_id": "uuid",
    "timestamp": "2026-08-13T10:00:00Z"
  }
}
```

Error response:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Email is required",
    "details": { ... }
  },
  "meta": {
    "request_id": "uuid",
    "timestamp": "2026-08-13T10:00:00Z"
  }
}
```

---

## 2. Authentication API

### 2.1 Register

```
POST /api/v1/auth/register
```

**Request:**

```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "full_name": "Nguyen Van A"
}
```

**Response (201 Created):**

```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "full_name": "Nguyen Van A",
      "created_at": "2026-08-13T10:00:00Z"
    },
    "access_token": "eyJ...",
    "refresh_token": "eyJ..."
  }
}
```

### 2.2 Login

```
POST /api/v1/auth/login
```

**Request:**

```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "full_name": "Nguyen Van A",
      "avatar": null,
      "created_at": "2026-08-13T10:00:00Z"
    },
    "access_token": "eyJ...",
    "refresh_token": "eyJ..."
  }
}
```

### 2.3 Refresh Token

```
POST /api/v1/auth/refresh
```

**Request:**

```json
{
  "refresh_token": "eyJ..."
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ..."
  }
}
```

### 2.4 Logout

```
POST /api/v1/auth/logout
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "message": "Logged out successfully"
  }
}
```

---

## 3. Contact API

### 3.1 List Contacts

```
GET /api/v1/contacts
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | int | 1 | Page number |
| limit | int | 20 | Items per page |
| search | string | null | Search by name |
| sort_by | string | created_at | Sort field |
| order | string | desc | Sort order |

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "contacts": [
      {
        "id": "uuid",
        "display_name": "An Nguyen",
        "avatar": "https://...",
        "phone": "+84...",
        "email": "an@example.com",
        "relationship_score": 85,
        "has_memory": true,
        "created_at": "2026-08-10T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 100,
      "total_pages": 5
    }
  }
}
```

### 3.2 Get Contact

```
GET /api/v1/contacts/{contact_id}
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "display_name": "An Nguyen",
    "avatar": "https://...",
    "phone": "+84...",
    "email": "an@example.com",
    "created_at": "2026-08-10T10:00:00Z",
    "updated_at": "2026-08-13T10:00:00Z",
    "memory": {
      "id": "uuid",
      "summary": "AI Engineer at VinAI...",
      "profession": "AI Engineer",
      "company": "VinAI",
      "skills": ["Python", "Machine Learning", "LLM"],
      "interests": ["AI", "Startups", "Research"],
      "relationship_score": 85,
      "last_discussion": "Discussed the new AI project",
      "updated_at": "2026-08-13T09:00:00Z"
    },
    "tags": [
      {
        "id": "uuid",
        "name": "AI",
        "color": "#A1232A"
      }
    ]
  }
}
```

### 3.3 Create Contact

```
POST /api/v1/contacts
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request:**

```json
{
  "display_name": "An Nguyen",
  "phone": "+84...",
  "email": "an@example.com",
  "avatar": "https://..."
}
```

**Response (201 Created):**

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "display_name": "An Nguyen",
    "phone": "+84...",
    "email": "an@example.com",
    "avatar": null,
    "created_at": "2026-08-13T10:00:00Z"
  }
}
```

### 3.4 Update Contact

```
PUT /api/v1/contacts/{contact_id}
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request:**

```json
{
  "display_name": "An Nguyen Updated",
  "phone": "+84...",
  "email": "new@example.com"
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "display_name": "An Nguyen Updated",
    "updated_at": "2026-08-13T10:00:00Z"
  }
}
```

### 3.5 Delete Contact

```
DELETE /api/v1/contacts/{contact_id}
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "message": "Contact deleted successfully"
  }
}
```

---

## 4. Conversation API

### 4.1 List Conversations

```
GET /api/v1/conversations
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | int | 1 | Page number |
| limit | int | 20 | Items per page |

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "conversations": [
      {
        "id": "uuid",
        "contact": {
          "id": "uuid",
          "display_name": "An Nguyen",
          "avatar": "https://..."
        },
        "last_message": "See you tomorrow!",
        "last_message_time": "2026-08-13T10:00:00Z",
        "unread_count": 2,
        "created_at": "2026-08-10T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 50,
      "total_pages": 3
    }
  }
}
```

### 4.2 Get Conversation

```
GET /api/v1/conversations/{conversation_id}
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "contact": {
      "id": "uuid",
      "display_name": "An Nguyen",
      "avatar": "https://...",
      "memory": {
        "summary": "AI Engineer at VinAI...",
        "relationship_score": 85
      }
    },
    "last_message": "See you tomorrow!",
    "last_message_time": "2026-08-13T10:00:00Z",
    "created_at": "2026-08-10T10:00:00Z"
  }
}
```

### 4.3 Create Conversation

```
POST /api/v1/conversations
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request:**

```json
{
  "contact_id": "uuid"
}
```

**Response (201 Created):**

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "contact_id": "uuid",
    "created_at": "2026-08-13T10:00:00Z"
  }
}
```

---

## 5. Message API

### 5.1 List Messages

```
GET /api/v1/conversations/{conversation_id}/messages
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | int | 1 | Page number |
| limit | int | 50 | Items per page |
| before | datetime | null | Get messages before this time |

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "messages": [
      {
        "id": "uuid",
        "sender_type": "USER",
        "content": "Hello! How are you?",
        "message_type": "TEXT",
        "created_at": "2026-08-13T09:00:00Z"
      },
      {
        "id": "uuid",
        "sender_type": "CONTACT",
        "content": "I'm doing great! Working on a new AI project.",
        "message_type": "TEXT",
        "created_at": "2026-08-13T09:05:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 50,
      "total": 150,
      "total_pages": 3
    }
  }
}
```

### 5.2 Send Message

```
POST /api/v1/conversations/{conversation_id}/messages
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request:**

```json
{
  "content": "That sounds interesting! Tell me more about it.",
  "message_type": "TEXT"
}
```

**Response (201 Created):**

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "sender_type": "USER",
    "content": "That sounds interesting! Tell me more about it.",
    "message_type": "TEXT",
    "created_at": "2026-08-13T10:00:00Z"
  }
}
```

### 5.3 Mark Messages as Read

```
POST /api/v1/conversations/{conversation_id}/read
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "message": "Messages marked as read"
  }
}
```

---

## 6. Search API

### 6.1 Semantic Search

```
POST /api/v1/search
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request:**

```json
{
  "query": "Find people working on AI projects in Hanoi"
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "query": "Find people working on AI projects in Hanoi",
    "results": [
      {
        "contact": {
          "id": "uuid",
          "display_name": "An Nguyen",
          "avatar": "https://..."
        },
        "memory": {
          "summary": "AI Engineer at VinAI...",
          "skills": ["Python", "Machine Learning"]
        },
        "score": 0.95,
        "match_reason": "Works on AI projects at VinAI in Hanoi"
      },
      {
        "contact": {
          "id": "uuid",
          "display_name": "Minh Tran",
          "avatar": "https://..."
        },
        "memory": {
          "summary": "ML Engineer interested in AI...",
          "skills": ["Deep Learning", "Computer Vision"]
        },
        "score": 0.88,
        "match_reason": "Interested in AI and works in Hanoi"
      }
    ],
    "total": 2,
    "explanation": "Found 2 contacts working on AI projects. An is an AI Engineer at VinAI, and Minh is an ML Engineer interested in AI research."
  }
}
```

### 6.2 Search History

```
GET /api/v1/search/history
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | int | 1 | Page number |
| limit | int | 20 | Items per page |

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "history": [
      {
        "id": "uuid",
        "query": "Find people working on AI",
        "result_count": 5,
        "created_at": "2026-08-13T10:00:00Z"
      }
    ]
  }
}
```

---

## 7. Recommendation API

### 7.1 Get Recommendations

```
GET /api/v1/recommendations
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| type | string | null | Filter by type |
| status | string | PENDING | Filter by status |
| priority | string | null | Filter by priority |
| page | int | 1 | Page number |
| limit | int | 20 | Items per page |

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "recommendations": [
      {
        "id": "uuid",
        "type": "FOLLOWUP",
        "contact": {
          "id": "uuid",
          "display_name": "An Nguyen",
          "avatar": "https://..."
        },
        "reason": "You haven't talked to An in 30 days. Last conversation was about the AI project at VinAI.",
        "priority": "HIGH",
        "status": "PENDING",
        "created_at": "2026-08-13T08:00:00Z"
      },
      {
        "id": "uuid",
        "type": "CONNECTION",
        "contacts": [
          {
            "id": "uuid",
            "display_name": "An Nguyen"
          },
          {
            "id": "uuid",
            "display_name": "Minh Tran"
          }
        ],
        "reason": "Both An and Minh are working on AI projects and might benefit from connecting.",
        "priority": "MEDIUM",
        "status": "PENDING",
        "created_at": "2026-08-13T08:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 10,
      "total_pages": 1
    }
  }
}
```

### 7.2 Accept Recommendation

```
POST /api/v1/recommendations/{recommendation_id}/accept
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "status": "ACCEPTED",
    "action_taken": "Follow-up message drafted",
    "updated_at": "2026-08-13T10:00:00Z"
  }
}
```

### 7.3 Reject Recommendation

```
POST /api/v1/recommendations/{recommendation_id}/reject
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request:**

```json
{
  "reason": "Already contacted them yesterday"
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "status": "REJECTED",
    "rejection_reason": "Already contacted them yesterday",
    "updated_at": "2026-08-13T10:00:00Z"
  }
}
```

---

## 8. Memory API

### 8.1 Get Contact Memory

```
GET /api/v1/contacts/{contact_id}/memory
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "contact_id": "uuid",
    "summary": "An is an AI Engineer at VinAI with 3 years of experience in machine learning and LLM research.",
    "profession": "AI Engineer",
    "company": "VinAI",
    "skills": ["Python", "Machine Learning", "LLM", "PyTorch", "LangChain"],
    "interests": ["AI Research", "Startups", "Technology", "Research Papers"],
    "timeline": [
      {
        "date": "2026-08-10",
        "event": "Discussed AI project at VinAI",
        "type": "topic"
      },
      {
        "date": "2026-08-05",
        "event": "Shared interest in LLM research",
        "type": "interest"
      }
    ],
    "relationship_score": 85,
    "last_discussion": "Discussed the new AI project at VinAI",
    "updated_at": "2026-08-13T09:00:00Z"
  }
}
```

### 8.2 Update Contact Memory

```
PUT /api/v1/contacts/{contact_id}/memory
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request:**

```json
{
  "summary": "An is an AI Engineer at VinAI...",
  "profession": "AI Engineer",
  "company": "VinAI Research",
  "skills": ["Python", "Machine Learning", "LLM"],
  "interests": ["AI", "Startups"]
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "updated_at": "2026-08-13T10:00:00Z"
  }
}
```

### 8.3 Refresh Memory

```
POST /api/v1/contacts/{contact_id}/memory/refresh
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "message": "Memory refresh initiated",
    "status": "PROCESSING"
  }
}
```

### 8.4 Get Context Card

```
GET /api/v1/conversations/{conversation_id}/context
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "contact": {
      "id": "uuid",
      "display_name": "An Nguyen",
      "avatar": "https://..."
    },
    "memory": {
      "summary": "AI Engineer at VinAI with 3 years of experience...",
      "profession": "AI Engineer",
      "company": "VinAI",
      "relationship_score": 85
    },
    "last_discussion": "Discussed the new AI project",
    "timeline": [
      {
        "date": "2026-08-10",
        "event": "Discussed AI project"
      }
    ],
    "recent_recommendations": [
      {
        "type": "FOLLOWUP",
        "reason": "30 days since last contact"
      }
    ],
    "tags": [
      {
        "id": "uuid",
        "name": "AI",
        "color": "#A1232A"
      }
    ]
  }
}
```

---

## 9. Copilot API

### 9.1 Chat with Copilot

```
POST /api/v1/copilot
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request:**

```json
{
  "conversation_id": "uuid",
  "message": "Who is An and should I follow up with them?",
  "stream": false
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "response": "Based on your conversations with An:\n\n**Who is An?**\nAn is an AI Engineer at VinAI with 3 years of experience in machine learning. You've discussed AI projects and LLM research multiple times.\n\n**Relationship Score:** 85/100 (High)\n\n**Should you follow up?**\nYes! It's been 30 days since your last conversation about the AI project. You might want to check on the project's progress or share any relevant resources you come across.\n\n**Suggested follow-up:**\n\"Hey An! How's the AI project going? Found some interesting papers on LLMs that might be relevant.\"",
    "suggestions": [
      {
        "type": "SHARE_TO_CONVERSATION",
        "content": "Hey An! How's the AI project going?",
        "action": "Copy to input"
      }
    ],
    "context_used": {
      "memory": true,
      "timeline": true,
      "recommendations": true
    }
  }
}
```

### 9.2 Copilot with Streaming

```
POST /api/v1/copilot
```

**Request:**

```json
{
  "conversation_id": "uuid",
  "message": "Summarize our recent conversations",
  "stream": true
}
```

**Response (200 OK) - Server-Sent Events:**

```
data: {"type": "start", "data": {}}

data: {"type": "token", "data": {"content": "Based"}}

data: {"type": "token", "data": {"content": " on"}}

data: {"type": "token", "data": {"content": " your"}}

...

data: {"type": "done", "data": {"usage": {"prompt_tokens": 100, "completion_tokens": 50}}}
```

### 9.3 Copilot Actions

```
POST /api/v1/copilot/actions
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request:**

```json
{
  "action": "get_summary",
  "conversation_id": "uuid"
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "type": "SUMMARY",
    "content": "Your recent conversations with An have been about AI projects and research. Key topics: LLM development, VinAI work, and potential collaboration opportunities.",
    "shareable": true
  }
}
```

---

## 10. Tag API

### 10.1 List Tags

```
GET /api/v1/tags
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "tags": [
      {
        "id": "uuid",
        "name": "AI",
        "color": "#A1232A",
        "usage_count": 15
      },
      {
        "id": "uuid",
        "name": "Startup",
        "color": "#FFD700",
        "usage_count": 8
      }
    ]
  }
}
```

### 10.2 Get Suggested Tags

```
GET /api/v1/contacts/{contact_id}/tags/suggestions
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "suggestions": [
      {
        "entity_type": "company",
        "value": "VinAI",
        "confidence": 0.95,
        "context": "I work at VinAI as an AI Engineer"
      },
      {
        "entity_type": "skill",
        "value": "Machine Learning",
        "confidence": 0.90,
        "context": "I have experience in Machine Learning"
      }
    ]
  }
}
```

### 10.3 Add Tag to Contact

```
POST /api/v1/contacts/{contact_id}/tags
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request:**

```json
{
  "tag_id": "uuid"
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "contact_id": "uuid",
    "tag": {
      "id": "uuid",
      "name": "AI",
      "color": "#A1232A"
    }
  }
}
```

### 10.4 Remove Tag from Contact

```
DELETE /api/v1/contacts/{contact_id}/tags/{tag_id}
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "message": "Tag removed successfully"
  }
}
```

---

## 11. WebSocket API

### 11.1 Connection

```
WS /ws/chat
```

**Connection URL:**

```
ws://localhost:8000/ws/chat?token=<access_token>
```

### 11.2 Send Message (via WebSocket)

**Client → Server:**

```json
{
  "type": "message",
  "conversation_id": "uuid",
  "content": "Hello!",
  "message_type": "TEXT"
}
```

**Server → Client:**

```json
{
  "type": "message",
  "data": {
    "id": "uuid",
    "conversation_id": "uuid",
    "sender_type": "USER",
    "content": "Hello!",
    "created_at": "2026-08-13T10:00:00Z"
  }
}
```

### 11.3 Typing Indicator

**Client → Server:**

```json
{
  "type": "typing",
  "conversation_id": "uuid",
  "is_typing": true
}
```

### 11.4 Online Status

**Server → Client:**

```json
{
  "type": "online_status",
  "data": {
    "contact_id": "uuid",
    "is_online": true
  }
}
```

### 11.5 Notification

**Server → Client:**

```json
{
  "type": "notification",
  "data": {
    "id": "uuid",
    "title": "New Recommendation",
    "content": "You haven't talked to An in 30 days",
    "type": "FOLLOWUP"
  }
}
```

---

## 12. Event Log API

### 12.1 Log Event

```
POST /api/v1/events
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request:**

```json
{
  "event_type": "OPEN_CHAT",
  "conversation_id": "uuid",
  "payload": {
    "duration_seconds": 120
  }
}
```

**Response (201 Created):**

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "event_type": "OPEN_CHAT",
    "created_at": "2026-08-13T10:00:00Z"
  }
}
```

---

## 13. Settings API

### 13.1 Get Settings

```
GET /api/v1/settings
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "auto_tag": false,
    "auto_memory": true,
    "theme": "light",
    "language": "vi",
    "notification": true
  }
}
```

### 13.2 Update Settings

```
PUT /api/v1/settings
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request:**

```json
{
  "auto_tag": true,
  "notification": false
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "auto_tag": true,
    "auto_memory": true,
    "theme": "light",
    "language": "vi",
    "notification": false
  }
}
```

---

## 14. Error Codes

### 14.1 HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Validation error |
| 401 | Unauthorized | Invalid/missing token |
| 403 | Forbidden | Access denied |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limited |
| 500 | Internal Server Error | Server error |

### 14.2 Application Error Codes

| Code | Meaning |
|------|---------|
| `VALIDATION_ERROR` | Request validation failed |
| `AUTH_INVALID_CREDENTIALS` | Wrong email/password |
| `AUTH_TOKEN_EXPIRED` | JWT token expired |
| `AUTH_TOKEN_INVALID` | Invalid JWT token |
| `RESOURCE_NOT_FOUND` | Resource doesn't exist |
| `RESOURCE_FORBIDDEN` | Not allowed to access resource |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `INTERNAL_ERROR` | Server error |

---

## 15. Rate Limiting

### 15.1 Limits by Endpoint

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/api/v1/auth/*` | 10 | per minute |
| `/api/v1/copilot` | 30 | per minute |
| `/api/v1/search` | 20 | per minute |
| `/api/v1/*` (other) | 100 | per minute |

### 15.2 Rate Limit Headers

```
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 25
X-RateLimit-Reset: 1691928000
```

---

## 16. Pagination

### 16.1 Cursor-based Pagination (Recommended for Messages)

```
GET /api/v1/conversations/{id}/messages?before=2026-08-13T10:00:00Z&limit=50
```

### 16.2 Offset-based Pagination (Default)

```
GET /api/v1/contacts?page=1&limit=20
```

---

## 17. OpenAPI/Swagger

API documentation is automatically generated and available at:

| Environment | URL |
|-------------|-----|
| Development | `http://localhost:8000/docs` |
| Staging | `https://api.staging.memorychat.vn/docs` |
| Production | `https://api.memorychat.vn/docs` |

Alternative documentation: `http://localhost:8000/redoc`

---

*Document Version: 1.0*  
*Last Updated: 2026-08-13*
