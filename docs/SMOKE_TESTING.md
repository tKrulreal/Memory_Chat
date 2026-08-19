# Smoke Testing Checklist

This document serves as the mandatory manual testing checklist to be executed on **Staging** (before release) and **Production** (immediately after release). 

> **Important**: Staging should resemble production as closely as practical. Do not skip staging tests unless it's a critical hotfix.

## 1. Authentication & Security
- [ ] **Register**: Can create a new user account successfully.
- [ ] **Login**: Can login with the newly created account.
- [ ] **JWT Expiration**: Wait for the JWT token to expire (or artificially reduce expiry time in staging) and verify the user is logged out or prompted to re-authenticate gracefully.
- [ ] **Logout**: Clicking logout immediately invalidates the session on the client side.

## 2. Peer-to-Peer Connections
*Requires two separate accounts (User A and User B).*
- [ ] **Send Request**: User A sends a connection request to User B. User B receives the request in real-time.
- [ ] **Reject**: User B rejects the request. User A is notified.
- [ ] **Accept**: User A sends a new request, User B accepts. Both users see each other in their friend list.
- [ ] **Cancel/Remove**: User A removes User B from connections. Both users can no longer send messages to each other.

## 3. Real-time Messaging (Chat)
- [ ] **Send & Receive**: User A sends a message. User B receives it instantly via WebSocket.
- [ ] **Idempotency**: Send the exact same message payload twice (using an interceptor/curl). Verify it only appears once in the database and UI.
- [ ] **Pagination**: Open a chat with >50 messages. Scroll up to trigger cursor pagination. Verify older messages load smoothly without duplicates.
- [ ] **WebSocket Reconnect**: 
  - Turn off Wi-Fi or throttle network to offline.
  - Send a message (should go to offline queue/retry state).
  - Turn Wi-Fi back on.
  - Verify WebSocket reconnects automatically and the queued message is successfully delivered.

## 4. Message Recall
- [ ] **Recall Own Message**: User A recalls a message they sent. It disappears/shows as recalled for both User A and User B in real-time.
- [ ] **Persistence**: Refresh the page. The recalled message should remain in the "recalled" state (not revert to original text).
- [ ] **Unauthorized Recall**: Attempt to recall User B's message using User A's token via cURL/Postman. Verify the API returns `403 Forbidden` or `404 Not Found`.

## 5. AI Features (If enabled)
*Only test AI features that are enabled in the current release.*
- [ ] **AI Search (RAG)**: Search for a specific detail mentioned in a past chat. Verify the AI retrieves the correct context and cites the conversation.
- [ ] **Data Isolation**: User A asks the AI about a secret User B told User C. Ensure User A's AI cannot access User B/C's chats.
- [ ] **AI Recommendation/Copilot**: (If applicable) Verify AI correctly suggests responses based on the chat context.

---
**Sign-off:**
If any of these tests fail on Staging, **DO NOT DEPLOY TO PRODUCTION**. 
If any fail on Production, initiate the **Rollback Plan** immediately.
