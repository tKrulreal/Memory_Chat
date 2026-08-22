--
-- PostgreSQL database dump
--

\restrict Wm8DwarlRcZosvcR3ZchImLnak66SoBVMQvc3NS3ylMH78ZYwrM5JcivfQCjeo7

-- Dumped from database version 15.18
-- Dumped by pg_dump version 15.18

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY public.user_tags DROP CONSTRAINT IF EXISTS user_tags_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.user_tags DROP CONSTRAINT IF EXISTS user_tags_tag_id_fkey;
ALTER TABLE IF EXISTS ONLY public.user_profiles DROP CONSTRAINT IF EXISTS user_profiles_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.tags DROP CONSTRAINT IF EXISTS tags_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.settings DROP CONSTRAINT IF EXISTS settings_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.search_history DROP CONSTRAINT IF EXISTS search_history_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.recommendations DROP CONSTRAINT IF EXISTS recommendations_target_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.recommendations DROP CONSTRAINT IF EXISTS recommendations_target_contact_id_fkey;
ALTER TABLE IF EXISTS ONLY public.recommendations DROP CONSTRAINT IF EXISTS recommendations_owner_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.recommendations DROP CONSTRAINT IF EXISTS recommendations_contact_id_fkey;
ALTER TABLE IF EXISTS ONLY public.notifications DROP CONSTRAINT IF EXISTS notifications_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.messages DROP CONSTRAINT IF EXISTS messages_sender_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.messages DROP CONSTRAINT IF EXISTS messages_reply_to_message_id_fkey;
ALTER TABLE IF EXISTS ONLY public.messages DROP CONSTRAINT IF EXISTS messages_conversation_id_fkey;
ALTER TABLE IF EXISTS ONLY public.message_reactions DROP CONSTRAINT IF EXISTS message_reactions_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.message_reactions DROP CONSTRAINT IF EXISTS message_reactions_message_id_fkey;
ALTER TABLE IF EXISTS ONLY public.event_logs DROP CONSTRAINT IF EXISTS event_logs_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.event_logs DROP CONSTRAINT IF EXISTS event_logs_conversation_id_fkey;
ALTER TABLE IF EXISTS ONLY public.direct_conversations DROP CONSTRAINT IF EXISTS direct_conversations_user_b_id_fkey;
ALTER TABLE IF EXISTS ONLY public.direct_conversations DROP CONSTRAINT IF EXISTS direct_conversations_user_a_id_fkey;
ALTER TABLE IF EXISTS ONLY public.conversation_user_state DROP CONSTRAINT IF EXISTS conversation_user_state_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.conversation_user_state DROP CONSTRAINT IF EXISTS conversation_user_state_conversation_id_fkey;
ALTER TABLE IF EXISTS ONLY public.contacts DROP CONSTRAINT IF EXISTS contacts_owner_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.contacts DROP CONSTRAINT IF EXISTS contacts_conversation_id_fkey;
ALTER TABLE IF EXISTS ONLY public.contact_memories DROP CONSTRAINT IF EXISTS contact_memories_contact_id_fkey;
ALTER TABLE IF EXISTS ONLY public.connection_requests DROP CONSTRAINT IF EXISTS connection_requests_sender_id_fkey;
ALTER TABLE IF EXISTS ONLY public.connection_requests DROP CONSTRAINT IF EXISTS connection_requests_receiver_id_fkey;
ALTER TABLE IF EXISTS ONLY public.assistant_memories DROP CONSTRAINT IF EXISTS assistant_memories_owner_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.assistant_memories DROP CONSTRAINT IF EXISTS assistant_memories_conversation_id_fkey;
ALTER TABLE IF EXISTS ONLY public.ai_system_config DROP CONSTRAINT IF EXISTS ai_system_config_user_id_fkey;
DROP INDEX IF EXISTS public.ix_users_phone;
DROP INDEX IF EXISTS public.ix_users_email;
DROP INDEX IF EXISTS public.ix_user_tags_user_id;
DROP INDEX IF EXISTS public.ix_user_tags_tag_id;
DROP INDEX IF EXISTS public.ix_tags_user_id;
DROP INDEX IF EXISTS public.ix_tags_name;
DROP INDEX IF EXISTS public.ix_search_history_user_id;
DROP INDEX IF EXISTS public.ix_recommendations_target_user_id;
DROP INDEX IF EXISTS public.ix_recommendations_target_contact_id;
DROP INDEX IF EXISTS public.ix_recommendations_owner_user_id;
DROP INDEX IF EXISTS public.ix_recommendations_contact_id;
DROP INDEX IF EXISTS public.ix_outbox_events_status;
DROP INDEX IF EXISTS public.ix_outbox_events_event_type;
DROP INDEX IF EXISTS public.ix_notifications_user_id;
DROP INDEX IF EXISTS public.ix_messages_sender_user_id;
DROP INDEX IF EXISTS public.ix_messages_conversation_id;
DROP INDEX IF EXISTS public.ix_messages_conv_created_id;
DROP INDEX IF EXISTS public.ix_messages_client_message_id;
DROP INDEX IF EXISTS public.ix_message_reactions_user_id;
DROP INDEX IF EXISTS public.ix_message_reactions_message_id;
DROP INDEX IF EXISTS public.ix_event_logs_user_id;
DROP INDEX IF EXISTS public.ix_event_logs_conversation_id;
DROP INDEX IF EXISTS public.ix_direct_conversations_user_b_id;
DROP INDEX IF EXISTS public.ix_direct_conversations_user_a_id;
DROP INDEX IF EXISTS public.ix_conversation_user_state_user_id;
DROP INDEX IF EXISTS public.ix_conversation_user_state_conversation_id;
DROP INDEX IF EXISTS public.ix_contacts_owner_user_id;
DROP INDEX IF EXISTS public.ix_contacts_conversation_id;
DROP INDEX IF EXISTS public.ix_contact_memories_contact_id;
DROP INDEX IF EXISTS public.ix_connection_requests_status;
DROP INDEX IF EXISTS public.ix_connection_requests_sender_id;
DROP INDEX IF EXISTS public.ix_connection_requests_receiver_id;
DROP INDEX IF EXISTS public.ix_assistant_memories_owner_user_id;
DROP INDEX IF EXISTS public.ix_assistant_memories_conversation_id;
DROP INDEX IF EXISTS public.ix_ai_system_config_user_id;
DROP INDEX IF EXISTS public.ix_ai_system_config_key;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_pkey;
ALTER TABLE IF EXISTS ONLY public.user_tags DROP CONSTRAINT IF EXISTS user_tags_pkey;
ALTER TABLE IF EXISTS ONLY public.user_profiles DROP CONSTRAINT IF EXISTS user_profiles_pkey;
ALTER TABLE IF EXISTS ONLY public.tags DROP CONSTRAINT IF EXISTS uq_user_tag_name;
ALTER TABLE IF EXISTS ONLY public.user_tags DROP CONSTRAINT IF EXISTS uq_user_tag;
ALTER TABLE IF EXISTS ONLY public.ai_system_config DROP CONSTRAINT IF EXISTS uq_user_ai_config;
ALTER TABLE IF EXISTS ONLY public.message_reactions DROP CONSTRAINT IF EXISTS uq_message_user_emoji;
ALTER TABLE IF EXISTS ONLY public.direct_conversations DROP CONSTRAINT IF EXISTS uq_direct_conversation;
ALTER TABLE IF EXISTS ONLY public.connection_requests DROP CONSTRAINT IF EXISTS uq_connection_request;
ALTER TABLE IF EXISTS ONLY public.messages DROP CONSTRAINT IF EXISTS uq_client_message_id;
ALTER TABLE IF EXISTS ONLY public.tags DROP CONSTRAINT IF EXISTS tags_pkey;
ALTER TABLE IF EXISTS ONLY public.settings DROP CONSTRAINT IF EXISTS settings_pkey;
ALTER TABLE IF EXISTS ONLY public.search_history DROP CONSTRAINT IF EXISTS search_history_pkey;
ALTER TABLE IF EXISTS ONLY public.recommendations DROP CONSTRAINT IF EXISTS recommendations_pkey;
ALTER TABLE IF EXISTS ONLY public.outbox_events DROP CONSTRAINT IF EXISTS outbox_events_pkey;
ALTER TABLE IF EXISTS ONLY public.notifications DROP CONSTRAINT IF EXISTS notifications_pkey;
ALTER TABLE IF EXISTS ONLY public.messages DROP CONSTRAINT IF EXISTS messages_pkey;
ALTER TABLE IF EXISTS ONLY public.message_reactions DROP CONSTRAINT IF EXISTS message_reactions_pkey;
ALTER TABLE IF EXISTS ONLY public.event_logs DROP CONSTRAINT IF EXISTS event_logs_pkey;
ALTER TABLE IF EXISTS ONLY public.direct_conversations DROP CONSTRAINT IF EXISTS direct_conversations_pkey;
ALTER TABLE IF EXISTS ONLY public.conversation_user_state DROP CONSTRAINT IF EXISTS conversation_user_state_pkey;
ALTER TABLE IF EXISTS ONLY public.contacts DROP CONSTRAINT IF EXISTS contacts_pkey;
ALTER TABLE IF EXISTS ONLY public.contact_memories DROP CONSTRAINT IF EXISTS contact_memories_pkey;
ALTER TABLE IF EXISTS ONLY public.connection_requests DROP CONSTRAINT IF EXISTS connection_requests_pkey;
ALTER TABLE IF EXISTS ONLY public.assistant_memories DROP CONSTRAINT IF EXISTS assistant_memories_pkey;
ALTER TABLE IF EXISTS ONLY public.alembic_version DROP CONSTRAINT IF EXISTS alembic_version_pkc;
ALTER TABLE IF EXISTS ONLY public.ai_system_config DROP CONSTRAINT IF EXISTS ai_system_config_pkey;
DROP TABLE IF EXISTS public.users;
DROP TABLE IF EXISTS public.user_tags;
DROP TABLE IF EXISTS public.user_profiles;
DROP TABLE IF EXISTS public.tags;
DROP TABLE IF EXISTS public.settings;
DROP TABLE IF EXISTS public.search_history;
DROP TABLE IF EXISTS public.recommendations;
DROP TABLE IF EXISTS public.outbox_events;
DROP TABLE IF EXISTS public.notifications;
DROP TABLE IF EXISTS public.messages;
DROP TABLE IF EXISTS public.message_reactions;
DROP TABLE IF EXISTS public.event_logs;
DROP TABLE IF EXISTS public.direct_conversations;
DROP TABLE IF EXISTS public.conversation_user_state;
DROP TABLE IF EXISTS public.contacts;
DROP TABLE IF EXISTS public.contact_memories;
DROP TABLE IF EXISTS public.connection_requests;
DROP TABLE IF EXISTS public.assistant_memories;
DROP TABLE IF EXISTS public.alembic_version;
DROP TABLE IF EXISTS public.ai_system_config;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: ai_system_config; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ai_system_config (
    id uuid NOT NULL,
    key character varying(255) NOT NULL,
    value json NOT NULL,
    description character varying(1024),
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    user_id uuid NOT NULL
);


ALTER TABLE public.ai_system_config OWNER TO postgres;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: assistant_memories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.assistant_memories (
    id uuid NOT NULL,
    owner_user_id uuid NOT NULL,
    conversation_id uuid NOT NULL,
    through_message_id character varying(255),
    summary character varying,
    facts json,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    scope character varying(50) DEFAULT 'CONVERSATION'::character varying NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.assistant_memories OWNER TO postgres;

--
-- Name: connection_requests; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.connection_requests (
    id uuid NOT NULL,
    sender_id uuid NOT NULL,
    receiver_id uuid NOT NULL,
    status character varying(50) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.connection_requests OWNER TO postgres;

--
-- Name: contact_memories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.contact_memories (
    id uuid NOT NULL,
    contact_id uuid NOT NULL,
    summary character varying,
    skills json,
    interests json,
    current_needs json,
    current_offers json,
    relationship_score integer DEFAULT 50 NOT NULL,
    last_interaction timestamp without time zone,
    timeline json,
    follow_up character varying(512),
    last_met character varying(512),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.contact_memories OWNER TO postgres;

--
-- Name: contacts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.contacts (
    id uuid NOT NULL,
    owner_user_id uuid NOT NULL,
    conversation_id uuid,
    display_name character varying(255) NOT NULL,
    email character varying(255),
    phone character varying(50),
    avatar_url character varying(1024),
    profession character varying(255),
    company character varying(255),
    location character varying(255),
    notes character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.contacts OWNER TO postgres;

--
-- Name: conversation_user_state; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.conversation_user_state (
    id uuid NOT NULL,
    conversation_id uuid NOT NULL,
    user_id uuid NOT NULL,
    last_read_message_id character varying(255),
    is_archived boolean NOT NULL,
    is_muted boolean NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    role character varying(50) DEFAULT 'MEMBER'::character varying NOT NULL,
    joined_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.conversation_user_state OWNER TO postgres;

--
-- Name: direct_conversations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.direct_conversations (
    id uuid NOT NULL,
    user_a_id uuid NOT NULL,
    user_b_id uuid NOT NULL,
    last_message_id character varying(255),
    last_message_time timestamp with time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_message_content character varying(1024),
    type character varying(50) DEFAULT 'P2P'::character varying NOT NULL,
    title character varying(255),
    CONSTRAINT chk_user_order CHECK ((user_a_id < user_b_id))
);


ALTER TABLE public.direct_conversations OWNER TO postgres;

--
-- Name: event_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.event_logs (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    conversation_id uuid,
    event_type character varying(50) NOT NULL,
    payload json,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.event_logs OWNER TO postgres;

--
-- Name: message_reactions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.message_reactions (
    id uuid NOT NULL,
    message_id uuid NOT NULL,
    user_id uuid NOT NULL,
    emoji character varying(50) NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.message_reactions OWNER TO postgres;

--
-- Name: messages; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.messages (
    id uuid NOT NULL,
    conversation_id uuid NOT NULL,
    sender_user_id uuid NOT NULL,
    client_message_id character varying(255),
    content character varying NOT NULL,
    message_type character varying(50) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    edited_at timestamp with time zone,
    deleted_at timestamp with time zone,
    reply_to_message_id uuid
);


ALTER TABLE public.messages OWNER TO postgres;

--
-- Name: notifications; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notifications (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    type character varying(50) NOT NULL,
    title character varying(255) NOT NULL,
    content character varying(2048) NOT NULL,
    status character varying(50) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.notifications OWNER TO postgres;

--
-- Name: outbox_events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.outbox_events (
    id uuid NOT NULL,
    event_type character varying(50) NOT NULL,
    payload json,
    status character varying(50) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.outbox_events OWNER TO postgres;

--
-- Name: recommendations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.recommendations (
    id uuid NOT NULL,
    owner_user_id uuid NOT NULL,
    target_user_id uuid,
    contact_id uuid,
    target_contact_id uuid,
    type character varying(50) NOT NULL,
    reason character varying NOT NULL,
    priority character varying(20) DEFAULT 'MEDIUM'::character varying NOT NULL,
    confidence double precision DEFAULT '0.5'::double precision NOT NULL,
    status character varying(20) DEFAULT 'PENDING'::character varying NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    expires_at timestamp with time zone
);


ALTER TABLE public.recommendations OWNER TO postgres;

--
-- Name: search_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.search_history (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    query character varying(1024) NOT NULL,
    results json,
    result_count integer NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.search_history OWNER TO postgres;

--
-- Name: settings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.settings (
    user_id uuid NOT NULL,
    auto_tag boolean NOT NULL,
    auto_memory boolean NOT NULL,
    theme character varying(50) NOT NULL,
    language character varying(50) NOT NULL,
    notification boolean NOT NULL,
    ai_enabled boolean DEFAULT true NOT NULL,
    ai_memory_window character varying(50) DEFAULT 'unlimited'::character varying NOT NULL,
    ai_read_profile boolean DEFAULT true NOT NULL,
    ai_memory_refresh_interval character varying(50) DEFAULT 'realtime'::character varying NOT NULL
);


ALTER TABLE public.settings OWNER TO postgres;

--
-- Name: tags; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tags (
    id uuid NOT NULL,
    name character varying(100) NOT NULL,
    category character varying(100),
    is_active boolean NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    user_id uuid NOT NULL
);


ALTER TABLE public.tags OWNER TO postgres;

--
-- Name: user_profiles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_profiles (
    user_id uuid NOT NULL,
    profession character varying(255),
    company character varying(255),
    location character varying(255),
    skills json,
    interests json,
    looking_for json,
    offering json,
    bio character varying(1024),
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.user_profiles OWNER TO postgres;

--
-- Name: user_tags; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_tags (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    tag_id uuid NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.user_tags OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id uuid NOT NULL,
    email character varying(255) NOT NULL,
    password_hash character varying(255) NOT NULL,
    full_name character varying(255),
    avatar character varying(1024),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    is_ai boolean DEFAULT false NOT NULL,
    deleted_at timestamp with time zone,
    gender character varying(50),
    phone character varying(50)
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Data for Name: ai_system_config; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ai_system_config (id, key, value, description, created_at, updated_at, user_id) FROM stdin;
ead46449-5fc8-495d-9b5a-e8443bc014c4	system_prompt	{"role": "system", "content": "You are a helpful AI Matchmaker agent. Analyze user chats to find common interests and propose connections."}	System rules for AI Matchmaker	2026-08-21 13:20:32.964777	2026-08-21 13:20:32.964777	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59
7f9f4768-c416-4ee8-ab3c-f2be4ed4779f	system_prompt	{"role": "system", "content": "You are a helpful AI Matchmaker agent. Analyze user chats to find common interests and propose connections."}	System rules for AI Matchmaker	2026-08-22 14:43:26.517654	2026-08-22 14:43:26.517654	cfc3c138-db1a-4b67-ace1-0e1b21d42938
39156b9d-db4f-4101-bace-aae9486d1529	ai_settings	{"features": {"copilot": true, "recommendation": true, "memory": true, "tagging": true}, "tag_limit": 3, "memory_timeframe": "1 month"}	Global AI Settings	2026-08-22 14:44:05.35389	2026-08-22 14:44:12.159544	cfc3c138-db1a-4b67-ace1-0e1b21d42938
b3960897-05c7-4f9b-8b0c-566a4c86bd83	system_prompt	{"role": "system", "content": "You are a helpful AI Matchmaker agent. Analyze user chats to find common interests and propose connections."}	System rules for AI Matchmaker	2026-08-22 14:44:34.848821	2026-08-22 14:44:34.848821	33a2cf07-6177-420e-bfd7-99cdae79b549
2b070ca4-8f15-4ca6-b298-69cb83677f49	ai_settings	{"features": {"copilot": true, "recommendation": true, "memory": true, "tagging": true}, "tag_limit": 6, "min_matching_score": 90, "memory_timeframe": "1 month"}	Global AI Settings	2026-08-21 14:58:54.649975	2026-08-22 17:36:01.228378	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
132d211943b2
\.


--
-- Data for Name: assistant_memories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.assistant_memories (id, owner_user_id, conversation_id, through_message_id, summary, facts, updated_at, scope, created_at) FROM stdin;
310277c6-4ec6-4bcb-8013-9ca5e774bf45	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	4a34d8c5-9dec-46f7-afb3-bb4371bfc0b8	\N		{"tags": ["\\u0110\\u1ed1i T\\u00e1c", "Tr\\u00ed Tu\\u1ec7 Nh\\u00e2n T\\u1ea1o", "Product Manager", "C\\u00f4ng Ngh\\u1ec7", "H\\u00e0 N\\u1ed9i"]}	2026-08-21 13:19:49.507044	CONVERSATION	2026-08-21 13:19:49.491446
fc8e01ed-cd54-42d0-a4ad-15bb73736bb3	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	98a24b83-c339-40b8-95cc-13433ae8130a	\N		{"tags": ["B\\u1ea1n B\\u00e8", "Tr\\u00ed Tu\\u1ec7 Nh\\u00e2n T\\u1ea1o", "Mobile Developer", "H\\u00e0 N\\u1ed9i"]}	2026-08-21 13:19:49.020166	CONVERSATION	2026-08-21 13:19:48.994861
b1702214-0835-4ebb-8f23-89283c2c6e20	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	15940406-00d7-4c70-aa78-110988b19fa0	\N	Đối tác đang nghiên cứu AI và phát triển Backend, đồng thời thể hiện sự quan tâm đến việc trao đổi và hợp tác trong lĩnh vực Machine Learning và tối ưu hóa hệ thống.	{"tags": ["\\u0110\\u1ed1i T\\u00e1c", "Tr\\u00ed Tu\\u1ec7 Nh\\u00e2n T\\u1ea1o", "Devops Engineer", "C\\u00f4ng Ngh\\u1ec7", "H\\u00e0 N\\u1ed9i"], "last_met": null, "interested_in": ["Ai", "Backend", "Machine Learning"], "follow_up": "Trao \\u0111\\u1ed5i th\\u00eam v\\u1ec1 d\\u1ef1 \\u00e1n", "relationship_score": 44, "timeline": [{"date": "2026-08-14", "message_count": 5, "last_message_preview": "Tuy\\u1ec7t v\\u1eddi, cu\\u1ed1i tu\\u1ea7n n\\u00e0y m\\u00ecnh r\\u1ea3nh. S\\u1ebd nh\\u1eafn l\\u1ea1i th\\u1eddi gian c\\u1ee5 th\\u1ec3 nh\\u00e9.", "participants": [null]}]}	2026-08-21 13:20:20.445805	CONVERSATION	2026-08-21 13:19:50.530787
195de529-55de-4d48-b9c2-63b0920ee522	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	a78023ce-b676-4477-8292-3391ab5bfaca	\N	Đối tác đang tập trung nghiên cứu về trí tuệ nhân tạo (AI) và phát triển Backend. Họ cũng bày tỏ mong muốn trao đổi thêm về Machine Learning và tối ưu hóa hệ thống.	{"tags": ["B\\u1ea1n B\\u00e8", "Tr\\u00ed Tu\\u1ec7 Nh\\u00e2n T\\u1ea1o", "Data Scientist", "C\\u00f4ng Ngh\\u1ec7", "H\\u00e0 N\\u1ed9i"], "last_met": null, "interested_in": ["Ai", "Backend", "Machine Learning"], "follow_up": "Trao \\u0111\\u1ed5i th\\u00eam v\\u1ec1 d\\u1ef1 \\u00e1n", "relationship_score": 44, "timeline": [{"date": "2026-08-11", "message_count": 5, "last_message_preview": "Tuy\\u1ec7t v\\u1eddi, cu\\u1ed1i tu\\u1ea7n n\\u00e0y m\\u00ecnh r\\u1ea3nh. S\\u1ebd nh\\u1eafn l\\u1ea1i th\\u1eddi gian c\\u1ee5 th\\u1ec3 nh\\u00e9.", "participants": [null]}], "pending_tags": ["B\\u1ea1n B\\u00e8", "Tr\\u00ed Tu\\u1ec7 Nh\\u00e2n T\\u1ea1o", "Data Scientist", "C\\u00f4ng Ngh\\u1ec7", "H\\u00e0 N\\u1ed9i"]}	2026-08-22 12:42:44.074141	CONVERSATION	2026-08-21 13:19:49.919257
4e33d425-95f1-4eaa-acc6-51578336ae22	cfc3c138-db1a-4b67-ace1-0e1b21d42938	3e156f9e-511c-4a79-bdb6-ec91b1312d44	\N		{"pending_tags": ["\\u0110\\u1ed1i T\\u00e1c", "Tr\\u00ed Tu\\u1ec7 Nh\\u00e2n T\\u1ea1o", "Product Manager"]}	2026-08-22 14:43:31.236238	CONVERSATION	2026-08-22 14:43:31.20821
cc4e923e-f97a-4eb7-8985-6fd4b81eb7f7	cfc3c138-db1a-4b67-ace1-0e1b21d42938	d8027034-474b-4b41-8cd5-8dcabcaedb6c	\N		{"pending_tags": ["B\\u1ea1n B\\u00e8", "C\\u00f4ng Ngh\\u1ec7", "Tr\\u00ed Tu\\u1ec7 Nh\\u00e2n T\\u1ea1o"]}	2026-08-22 14:43:35.087082	CONVERSATION	2026-08-22 14:43:35.075703
e5110448-137e-4000-9543-168801b1c87d	cfc3c138-db1a-4b67-ace1-0e1b21d42938	559340ef-80f9-41cd-825c-5d58440e5eeb	\N		{"pending_tags": ["B\\u1ea1n B\\u00e8", "C\\u00f4ng Ngh\\u1ec7", "Tr\\u00ed Tu\\u1ec7 Nh\\u00e2n T\\u1ea1o"]}	2026-08-22 14:43:35.565353	CONVERSATION	2026-08-22 14:43:35.536168
d79de206-c2ef-46c4-a248-f7191e3ed971	cfc3c138-db1a-4b67-ace1-0e1b21d42938	db39ac3b-1ddb-4b1e-b359-d6867eaf1f70	\N		{"pending_tags": ["B\\u1ea1n B\\u00e8", "C\\u00f4ng Ngh\\u1ec7", "Tr\\u00ed Tu\\u1ec7 Nh\\u00e2n T\\u1ea1o"]}	2026-08-22 14:43:36.159734	CONVERSATION	2026-08-22 14:43:36.148032
2915a453-2002-44c1-9b01-7b9c48dbddfd	cfc3c138-db1a-4b67-ace1-0e1b21d42938	fb44203d-ced3-471f-bde0-9b20fa4af31d	\N		{"pending_tags": ["B\\u1ea1n B\\u00e8", "C\\u00f4ng Ngh\\u1ec7", "Tr\\u00ed Tu\\u1ec7 Nh\\u00e2n T\\u1ea1o"]}	2026-08-22 14:43:36.888782	CONVERSATION	2026-08-22 14:43:36.878491
6992da4f-e7f3-4bd4-8ac3-a205252fe477	cfc3c138-db1a-4b67-ace1-0e1b21d42938	a86e8fab-273c-4640-8612-5083d856b56d	\N		{"pending_tags": ["B\\u1ea1n B\\u00e8", "Devops Engineer", "Machine Learning"]}	2026-08-22 14:43:36.512537	CONVERSATION	2026-08-22 14:43:36.501425
abaf8bfa-a8e1-4667-85de-8ad828d280a3	cfc3c138-db1a-4b67-ace1-0e1b21d42938	a78023ce-b676-4477-8292-3391ab5bfaca	\N		{"pending_tags": ["B\\u1ea1n B\\u00e8", "Ui/ux Designer", "C\\u00f4ng Ngh\\u1ec7"]}	2026-08-22 14:43:37.28589	CONVERSATION	2026-08-22 14:43:37.26401
c184f861-181b-4c37-9bb8-921bf16aacd8	33a2cf07-6177-420e-bfd7-99cdae79b549	211e7ab3-1d05-4227-bb01-cd27cd655691	\N		{"pending_tags": ["B\\u1ea1n B\\u00e8", "C\\u00f4ng Ngh\\u1ec7", "Tr\\u00ed Tu\\u1ec7 Nh\\u00e2n T\\u1ea1o (ai)"]}	2026-08-22 14:46:28.274271	CONVERSATION	2026-08-22 14:46:28.256576
16f0d700-1484-4bda-aa75-10ac8e9a72b7	33a2cf07-6177-420e-bfd7-99cdae79b549	a6af6560-fac5-4016-a8e0-48e521636bd2	\N		{"pending_tags": ["\\u0110\\u1ed1i T\\u00e1c", "Product Manager", "Tr\\u00ed Tu\\u1ec7 Nh\\u00e2n T\\u1ea1o"], "summary": ""}	2026-08-22 14:49:15.890625	CONVERSATION	2026-08-22 14:46:28.688068
1fdf026d-e21e-4d7e-9082-e810bbf32035	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	b2a4cf94-be68-4f29-ba2f-18127d1b6059	\N	Đối tác đang nghiên cứu về trí tuệ nhân tạo (AI) và phát triển Backend. Họ thể hiện sự quan tâm đến việc hợp tác và trao đổi thêm về các dự án liên quan đến Machine Learning.	{"tags": [], "last_met": "Caf\\u00e9 trao \\u0111\\u1ed5i v\\u1ec1 d\\u1ef1 \\u00e1n", "interested_in": ["Ai", "Backend", "Machine Learning"], "follow_up": "Th\\u1ea3o lu\\u1eadn v\\u1ec1 d\\u1ef1 \\u00e1n c\\u1ee5 th\\u1ec3", "relationship_score": 44, "timeline": [{"date": "2026-08-20", "message_count": 5, "last_message_preview": "Tuy\\u1ec7t v\\u1eddi, cu\\u1ed1i tu\\u1ea7n n\\u00e0y m\\u00ecnh r\\u1ea3nh. S\\u1ebd nh\\u1eafn l\\u1ea1i th\\u1eddi gian c\\u1ee5 th\\u1ec3 nh\\u00e9.", "participants": [null]}], "pending_tags": ["B\\u1ea1n B\\u00e8", "C\\u00f4ng Ngh\\u1ec7", "Tr\\u00ed Tu\\u1ec7 Nh\\u00e2n T\\u1ea1o", "Frontend Developer"], "summary": "\\u0110\\u1ed1i t\\u00e1c \\u0111ang nghi\\u00ean c\\u1ee9u v\\u1ec1 tr\\u00ed tu\\u1ec7 nh\\u00e2n t\\u1ea1o (AI) v\\u00e0 ph\\u00e1t tri\\u1ec3n Backend. H\\u1ecd th\\u1ec3 hi\\u1ec7n s\\u1ef1 quan t\\u00e2m \\u0111\\u1ebfn vi\\u1ec7c h\\u1ee3p t\\u00e1c v\\u00e0 trao \\u0111\\u1ed5i th\\u00eam v\\u1ec1 c\\u00e1c d\\u1ef1 \\u00e1n li\\u00ean quan \\u0111\\u1ebfn Machine Learning."}	2026-08-22 17:21:41.472989	CONVERSATION	2026-08-21 13:19:47.670308
\.


--
-- Data for Name: connection_requests; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.connection_requests (id, sender_id, receiver_id, status, created_at, updated_at) FROM stdin;
5e1b5001-167a-4861-8b28-467ac2a5a4c5	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	fa63627e-ae02-4b51-bea6-8c7af20501ad	ACCEPTED	2026-08-21 11:43:52.90033	2026-08-21 11:43:52.90033
72e9e5c2-a487-4971-ba69-7016df93d714	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	cfc3c138-db1a-4b67-ace1-0e1b21d42938	ACCEPTED	2026-08-21 11:43:52.916613	2026-08-21 11:43:52.916613
ab12a0d8-cdf9-442a-8642-f797302f436a	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	8fcd1ec3-980c-422e-9956-aa675289b2b5	ACCEPTED	2026-08-21 11:43:52.925125	2026-08-21 11:43:52.925125
96f15546-a0f5-4604-a514-a440ddf08738	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	ACCEPTED	2026-08-21 11:43:52.934305	2026-08-21 11:43:52.934305
92b1589c-9ba1-48de-bf83-9273c58d7df2	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	b70fe0df-4f87-4275-8dec-6160f139ffea	ACCEPTED	2026-08-21 11:43:52.942945	2026-08-21 11:43:52.942945
711199c4-61c6-4625-8c59-dfbd58251c51	fa63627e-ae02-4b51-bea6-8c7af20501ad	cfc3c138-db1a-4b67-ace1-0e1b21d42938	ACCEPTED	2026-08-21 11:43:52.953654	2026-08-21 11:43:52.953654
b9ba6992-c864-4ed4-b9be-f1e023d250a2	fa63627e-ae02-4b51-bea6-8c7af20501ad	8fcd1ec3-980c-422e-9956-aa675289b2b5	ACCEPTED	2026-08-21 11:43:52.962313	2026-08-21 11:43:52.962313
94541cf3-662e-498b-a4c7-056151a8fbe0	fa63627e-ae02-4b51-bea6-8c7af20501ad	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	ACCEPTED	2026-08-21 11:43:52.975888	2026-08-21 11:43:52.975888
d6c238a2-b4cd-475d-a090-c543bad84c7b	fa63627e-ae02-4b51-bea6-8c7af20501ad	b70fe0df-4f87-4275-8dec-6160f139ffea	ACCEPTED	2026-08-21 11:43:52.988328	2026-08-21 11:43:52.988328
1c267b32-5867-404d-9ae7-256b8a7373ec	fa63627e-ae02-4b51-bea6-8c7af20501ad	d896dfec-6d5f-4708-9d8b-ac7d97174165	ACCEPTED	2026-08-21 11:43:52.998978	2026-08-21 11:43:52.998978
1df9a8d8-c1b5-4074-afbd-641809df3224	cfc3c138-db1a-4b67-ace1-0e1b21d42938	8fcd1ec3-980c-422e-9956-aa675289b2b5	ACCEPTED	2026-08-21 11:43:53.00946	2026-08-21 11:43:53.00946
b9a7f6b9-20ff-4ce5-b85f-0718fe612d0f	cfc3c138-db1a-4b67-ace1-0e1b21d42938	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	ACCEPTED	2026-08-21 11:43:53.020375	2026-08-21 11:43:53.020375
3762c5a0-a0e6-4280-ad27-3a82fb9de18f	cfc3c138-db1a-4b67-ace1-0e1b21d42938	b70fe0df-4f87-4275-8dec-6160f139ffea	ACCEPTED	2026-08-21 11:43:53.029418	2026-08-21 11:43:53.029418
06419ad7-fcf7-46f6-84fe-2834c5e2c4c7	cfc3c138-db1a-4b67-ace1-0e1b21d42938	d896dfec-6d5f-4708-9d8b-ac7d97174165	ACCEPTED	2026-08-21 11:43:53.040104	2026-08-21 11:43:53.040104
0b447920-ce68-4697-9ca7-ac27fabb40c9	cfc3c138-db1a-4b67-ace1-0e1b21d42938	d367d79b-6cb8-4215-856d-bd6832604eac	ACCEPTED	2026-08-21 11:43:53.050361	2026-08-21 11:43:53.050361
19fa51a0-1c40-44e3-8396-30581fe9f332	8fcd1ec3-980c-422e-9956-aa675289b2b5	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	ACCEPTED	2026-08-21 11:43:53.060569	2026-08-21 11:43:53.060569
eb72fc94-641f-4f6d-9afc-59733699b01b	8fcd1ec3-980c-422e-9956-aa675289b2b5	b70fe0df-4f87-4275-8dec-6160f139ffea	ACCEPTED	2026-08-21 11:43:53.070824	2026-08-21 11:43:53.070824
72b953df-7e97-47be-b577-992805c088f9	8fcd1ec3-980c-422e-9956-aa675289b2b5	d896dfec-6d5f-4708-9d8b-ac7d97174165	ACCEPTED	2026-08-21 11:43:53.081102	2026-08-21 11:43:53.081102
2a984137-358a-43b8-bd72-7a8733ebac52	8fcd1ec3-980c-422e-9956-aa675289b2b5	d367d79b-6cb8-4215-856d-bd6832604eac	ACCEPTED	2026-08-21 11:43:53.090684	2026-08-21 11:43:53.090684
599dada7-619e-417e-b902-a50adc4179d0	8fcd1ec3-980c-422e-9956-aa675289b2b5	33a2cf07-6177-420e-bfd7-99cdae79b549	ACCEPTED	2026-08-21 11:43:53.101496	2026-08-21 11:43:53.101496
0d5fc7ed-3e78-4b49-9d37-16b9d0396115	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	b70fe0df-4f87-4275-8dec-6160f139ffea	ACCEPTED	2026-08-21 11:43:53.110668	2026-08-21 11:43:53.110668
a51e8325-e6be-4b1e-a929-848aecc661a0	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	d896dfec-6d5f-4708-9d8b-ac7d97174165	ACCEPTED	2026-08-21 11:43:53.12119	2026-08-21 11:43:53.12119
958907b0-a489-4e75-a43a-271470f1cb9c	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	d367d79b-6cb8-4215-856d-bd6832604eac	ACCEPTED	2026-08-21 11:43:53.130694	2026-08-21 11:43:53.130694
2ee22352-2d2e-4ea5-9d38-7b210c0d34bc	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	33a2cf07-6177-420e-bfd7-99cdae79b549	ACCEPTED	2026-08-21 11:43:53.14664	2026-08-21 11:43:53.14664
43b05223-57ae-4650-81b6-ceda67cf0968	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	720e462f-449a-4ec5-85c5-7452c94823ce	ACCEPTED	2026-08-21 11:43:53.160673	2026-08-21 11:43:53.160673
a03fd65a-1ce3-4757-bebd-3231a8387870	b70fe0df-4f87-4275-8dec-6160f139ffea	d896dfec-6d5f-4708-9d8b-ac7d97174165	ACCEPTED	2026-08-21 11:43:53.171854	2026-08-21 11:43:53.171854
6b661ea9-dac6-4f02-884f-9801350faa65	b70fe0df-4f87-4275-8dec-6160f139ffea	d367d79b-6cb8-4215-856d-bd6832604eac	ACCEPTED	2026-08-21 11:43:53.181667	2026-08-21 11:43:53.181667
46c42f32-2886-4210-bc84-f4371899d92a	b70fe0df-4f87-4275-8dec-6160f139ffea	33a2cf07-6177-420e-bfd7-99cdae79b549	ACCEPTED	2026-08-21 11:43:53.200921	2026-08-21 11:43:53.200921
fde3da2b-a020-486b-9aba-7ace0a564c10	b70fe0df-4f87-4275-8dec-6160f139ffea	720e462f-449a-4ec5-85c5-7452c94823ce	ACCEPTED	2026-08-21 11:43:53.229471	2026-08-21 11:43:53.229471
9b79ce30-a34f-4e36-a73a-698717c10f2a	d896dfec-6d5f-4708-9d8b-ac7d97174165	d367d79b-6cb8-4215-856d-bd6832604eac	ACCEPTED	2026-08-21 11:43:53.254549	2026-08-21 11:43:53.254549
9ed83498-c0fd-4227-b046-000639d9e6e4	d896dfec-6d5f-4708-9d8b-ac7d97174165	33a2cf07-6177-420e-bfd7-99cdae79b549	ACCEPTED	2026-08-21 11:43:53.268629	2026-08-21 11:43:53.268629
a1467b9f-639c-49fb-809d-56de5f97857f	d896dfec-6d5f-4708-9d8b-ac7d97174165	720e462f-449a-4ec5-85c5-7452c94823ce	ACCEPTED	2026-08-21 11:43:53.278851	2026-08-21 11:43:53.278851
f2655930-cd96-43ce-81bd-6c9fbed57e33	d367d79b-6cb8-4215-856d-bd6832604eac	33a2cf07-6177-420e-bfd7-99cdae79b549	ACCEPTED	2026-08-21 11:43:53.290279	2026-08-21 11:43:53.290279
17f39374-2bd0-4d3d-b36f-4038d88379f9	d367d79b-6cb8-4215-856d-bd6832604eac	720e462f-449a-4ec5-85c5-7452c94823ce	ACCEPTED	2026-08-21 11:43:53.302146	2026-08-21 11:43:53.302146
2d841755-9634-4bb2-b55c-c5ce85ba3bf9	33a2cf07-6177-420e-bfd7-99cdae79b549	720e462f-449a-4ec5-85c5-7452c94823ce	ACCEPTED	2026-08-21 11:43:53.312079	2026-08-21 11:43:53.312079
\.


--
-- Data for Name: contact_memories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.contact_memories (id, contact_id, summary, skills, interests, current_needs, current_offers, relationship_score, last_interaction, timeline, follow_up, last_met, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: contacts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.contacts (id, owner_user_id, conversation_id, display_name, email, phone, avatar_url, profession, company, location, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: conversation_user_state; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.conversation_user_state (id, conversation_id, user_id, last_read_message_id, is_archived, is_muted, updated_at, role, joined_at) FROM stdin;
5f5c2c68-0563-4247-aa59-099a4a8329d6	15940406-00d7-4c70-aa78-110988b19fa0	fa63627e-ae02-4b51-bea6-8c7af20501ad	\N	f	f	2026-08-21 11:43:52.90033	MEMBER	2026-08-21 11:43:52.90033
e3d68eb9-4fb3-4248-87c2-56bca34271a2	4a34d8c5-9dec-46f7-afb3-bb4371bfc0b8	8fcd1ec3-980c-422e-9956-aa675289b2b5	\N	f	f	2026-08-21 11:43:52.925125	MEMBER	2026-08-21 11:43:52.925125
5876ef93-67e3-4de0-a849-dc836eab0c7f	98a24b83-c339-40b8-95cc-13433ae8130a	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	\N	f	f	2026-08-21 11:43:52.934305	MEMBER	2026-08-21 11:43:52.934305
24cd7d64-7f00-4dde-9348-12a834299bca	b2a4cf94-be68-4f29-ba2f-18127d1b6059	b70fe0df-4f87-4275-8dec-6160f139ffea	\N	f	f	2026-08-21 11:43:52.942945	MEMBER	2026-08-21 11:43:52.942945
ad0c425d-90ba-4176-bfc2-4f00493138b0	a86e8fab-273c-4640-8612-5083d856b56d	fa63627e-ae02-4b51-bea6-8c7af20501ad	\N	f	f	2026-08-21 11:43:52.953654	MEMBER	2026-08-21 11:43:52.953654
4838a251-c7cd-421b-9efb-b38340cc0862	7130fefd-5219-42f4-acf2-fd6787a1c862	fa63627e-ae02-4b51-bea6-8c7af20501ad	\N	f	f	2026-08-21 11:43:52.962313	MEMBER	2026-08-21 11:43:52.962313
c2d2c070-8372-4380-aefe-80712ce121c0	7130fefd-5219-42f4-acf2-fd6787a1c862	8fcd1ec3-980c-422e-9956-aa675289b2b5	\N	f	f	2026-08-21 11:43:52.962313	MEMBER	2026-08-21 11:43:52.962313
a3c651eb-3e5b-4af8-9948-d25a9574c3f9	2ac06044-877a-40a1-a58b-978cbcb9f28a	fa63627e-ae02-4b51-bea6-8c7af20501ad	\N	f	f	2026-08-21 11:43:52.975888	MEMBER	2026-08-21 11:43:52.975888
da455890-7675-483a-b167-ea34262a921d	2ac06044-877a-40a1-a58b-978cbcb9f28a	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	\N	f	f	2026-08-21 11:43:52.975888	MEMBER	2026-08-21 11:43:52.975888
2b1d58c8-1229-4ed2-802f-3cd3caff87f0	407b3cc9-1764-42c1-96a0-29b596339451	fa63627e-ae02-4b51-bea6-8c7af20501ad	\N	f	f	2026-08-21 11:43:52.988328	MEMBER	2026-08-21 11:43:52.988328
92881136-07e0-4c3b-92e0-c53ce146500e	407b3cc9-1764-42c1-96a0-29b596339451	b70fe0df-4f87-4275-8dec-6160f139ffea	\N	f	f	2026-08-21 11:43:52.988328	MEMBER	2026-08-21 11:43:52.988328
d0b48e19-e4cf-4c27-9c82-d23048fa6deb	c7d95fcd-7f41-4520-9139-f665ce545727	fa63627e-ae02-4b51-bea6-8c7af20501ad	\N	f	f	2026-08-21 11:43:52.998978	MEMBER	2026-08-21 11:43:52.998978
26680f4a-5dd5-468a-bbd3-e324ed1f7650	c7d95fcd-7f41-4520-9139-f665ce545727	d896dfec-6d5f-4708-9d8b-ac7d97174165	\N	f	f	2026-08-21 11:43:52.998978	MEMBER	2026-08-21 11:43:52.998978
aa6c33f3-62b3-462b-8b57-34136be100f9	3e156f9e-511c-4a79-bdb6-ec91b1312d44	8fcd1ec3-980c-422e-9956-aa675289b2b5	\N	f	f	2026-08-21 11:43:53.00946	MEMBER	2026-08-21 11:43:53.00946
af801f06-381f-46be-933c-1d905e0611eb	559340ef-80f9-41cd-825c-5d58440e5eeb	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	\N	f	f	2026-08-21 11:43:53.020375	MEMBER	2026-08-21 11:43:53.020375
8202ed87-4489-4a6d-a4b7-04dcf66b64f4	fb44203d-ced3-471f-bde0-9b20fa4af31d	b70fe0df-4f87-4275-8dec-6160f139ffea	\N	f	f	2026-08-21 11:43:53.029418	MEMBER	2026-08-21 11:43:53.029418
d6b520a6-a11d-4932-9c2c-1f9cd8fd2d9e	db39ac3b-1ddb-4b1e-b359-d6867eaf1f70	d896dfec-6d5f-4708-9d8b-ac7d97174165	\N	f	f	2026-08-21 11:43:53.040104	MEMBER	2026-08-21 11:43:53.040104
8043fac1-5668-413b-8a1c-b6ed4f528775	d8027034-474b-4b41-8cd5-8dcabcaedb6c	d367d79b-6cb8-4215-856d-bd6832604eac	\N	f	f	2026-08-21 11:43:53.050361	MEMBER	2026-08-21 11:43:53.050361
6478b50e-c844-485d-ad77-ac11529a9d36	ca2a8210-b708-4702-a822-08146ba55319	8fcd1ec3-980c-422e-9956-aa675289b2b5	\N	f	f	2026-08-21 11:43:53.060569	MEMBER	2026-08-21 11:43:53.060569
5d2be619-b016-4fc3-9b0f-339f1fb57843	ca2a8210-b708-4702-a822-08146ba55319	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	\N	f	f	2026-08-21 11:43:53.060569	MEMBER	2026-08-21 11:43:53.060569
5345553f-a2fd-450a-9436-72222cb43922	aae65b59-7660-44b5-b925-a5c8b556324c	8fcd1ec3-980c-422e-9956-aa675289b2b5	\N	f	f	2026-08-21 11:43:53.070824	MEMBER	2026-08-21 11:43:53.070824
f4b53c14-10c5-4980-8a4e-cf7f0b62f009	aae65b59-7660-44b5-b925-a5c8b556324c	b70fe0df-4f87-4275-8dec-6160f139ffea	\N	f	f	2026-08-21 11:43:53.070824	MEMBER	2026-08-21 11:43:53.070824
574a5515-bc6b-444f-93bf-e63ea6e47f30	737f6edd-d78a-4ba6-bc76-838708df1c3d	8fcd1ec3-980c-422e-9956-aa675289b2b5	\N	f	f	2026-08-21 11:43:53.081102	MEMBER	2026-08-21 11:43:53.081102
da126e53-5082-40e9-ad0d-260ea972bc16	737f6edd-d78a-4ba6-bc76-838708df1c3d	d896dfec-6d5f-4708-9d8b-ac7d97174165	\N	f	f	2026-08-21 11:43:53.081102	MEMBER	2026-08-21 11:43:53.081102
9d2402ca-10e8-48d0-8421-7baeb916e94a	7cedae6b-bca8-43af-9686-c3253f325842	8fcd1ec3-980c-422e-9956-aa675289b2b5	\N	f	f	2026-08-21 11:43:53.090684	MEMBER	2026-08-21 11:43:53.090684
e135c51f-63ab-445e-91f6-d162f267d128	7cedae6b-bca8-43af-9686-c3253f325842	d367d79b-6cb8-4215-856d-bd6832604eac	\N	f	f	2026-08-21 11:43:53.090684	MEMBER	2026-08-21 11:43:53.090684
c3dc0966-ce79-4746-89a0-8839cd107ced	a6af6560-fac5-4016-a8e0-48e521636bd2	8fcd1ec3-980c-422e-9956-aa675289b2b5	\N	f	f	2026-08-21 11:43:53.101496	MEMBER	2026-08-21 11:43:53.101496
f18dced7-e54f-4ffc-97ee-88b6f2493efc	9e8f9ead-a2dd-40ef-8ea0-50ad90ab956f	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	\N	f	f	2026-08-21 11:43:53.110668	MEMBER	2026-08-21 11:43:53.110668
2325afab-7df2-4184-942b-ddfa7f8f491a	9e8f9ead-a2dd-40ef-8ea0-50ad90ab956f	b70fe0df-4f87-4275-8dec-6160f139ffea	\N	f	f	2026-08-21 11:43:53.110668	MEMBER	2026-08-21 11:43:53.110668
67b127c7-c35e-45e8-b29e-e9860d95b531	9eacdc06-eeb1-41ee-a9ee-13c1738114e1	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	\N	f	f	2026-08-21 11:43:53.12119	MEMBER	2026-08-21 11:43:53.12119
3b394666-4c56-4565-8a79-06dbc9978904	9eacdc06-eeb1-41ee-a9ee-13c1738114e1	d896dfec-6d5f-4708-9d8b-ac7d97174165	\N	f	f	2026-08-21 11:43:53.12119	MEMBER	2026-08-21 11:43:53.12119
20b824b1-a080-41c7-afdf-975fb3405427	d0a7dddc-75f0-4593-86e5-bd3fe9d870e8	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	\N	f	f	2026-08-21 11:43:53.130694	MEMBER	2026-08-21 11:43:53.130694
7496b95c-77d5-498e-9eaf-95cbfbc0a17a	d0a7dddc-75f0-4593-86e5-bd3fe9d870e8	d367d79b-6cb8-4215-856d-bd6832604eac	\N	f	f	2026-08-21 11:43:53.130694	MEMBER	2026-08-21 11:43:53.130694
84b74391-c940-4181-a5f6-353fa7ecd1ea	7536e586-efc6-47fa-b53a-2ae05b8fe67c	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	\N	f	f	2026-08-21 11:43:53.14664	MEMBER	2026-08-21 11:43:53.14664
4ce13bbc-5c9e-49b2-837d-9a46c28b47ac	7536e586-efc6-47fa-b53a-2ae05b8fe67c	33a2cf07-6177-420e-bfd7-99cdae79b549	\N	f	f	2026-08-21 11:43:53.14664	MEMBER	2026-08-21 11:43:53.14664
77cbebc7-15eb-44d6-bece-6e03299f0a38	5b26daff-27a7-49d7-bff6-5345e48c1d30	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	\N	f	f	2026-08-21 11:43:53.160673	MEMBER	2026-08-21 11:43:53.160673
2a21c6c9-f0ee-4c53-b4c6-679d2c03c83a	5b26daff-27a7-49d7-bff6-5345e48c1d30	720e462f-449a-4ec5-85c5-7452c94823ce	\N	f	f	2026-08-21 11:43:53.160673	MEMBER	2026-08-21 11:43:53.160673
e0f4e734-e48b-4169-b9d1-a3e0ad785ef1	2bb46ccc-0450-452b-9286-8d46fbaa0aae	b70fe0df-4f87-4275-8dec-6160f139ffea	\N	f	f	2026-08-21 11:43:53.171854	MEMBER	2026-08-21 11:43:53.171854
0f54e58b-4f22-47d5-b4b4-20203472e800	2bb46ccc-0450-452b-9286-8d46fbaa0aae	d896dfec-6d5f-4708-9d8b-ac7d97174165	\N	f	f	2026-08-21 11:43:53.171854	MEMBER	2026-08-21 11:43:53.171854
32504e50-3876-4c8f-9f45-0fac07573351	102a807d-7da1-42de-8802-9fcd154ac23f	b70fe0df-4f87-4275-8dec-6160f139ffea	\N	f	f	2026-08-21 11:43:53.181667	MEMBER	2026-08-21 11:43:53.181667
3a8dc8ac-d3bc-4dad-a1dd-b7933fc0e874	102a807d-7da1-42de-8802-9fcd154ac23f	d367d79b-6cb8-4215-856d-bd6832604eac	\N	f	f	2026-08-21 11:43:53.181667	MEMBER	2026-08-21 11:43:53.181667
5f02188e-c8e4-448a-9a65-70e8f16d8561	fa826862-22db-4973-a42e-47fb4a03c604	b70fe0df-4f87-4275-8dec-6160f139ffea	\N	f	f	2026-08-21 11:43:53.200921	MEMBER	2026-08-21 11:43:53.200921
091c2a8f-a07e-4c4b-8b25-34b131e5e24e	fa826862-22db-4973-a42e-47fb4a03c604	33a2cf07-6177-420e-bfd7-99cdae79b549	\N	f	f	2026-08-21 11:43:53.200921	MEMBER	2026-08-21 11:43:53.200921
74d2b7d6-3893-41d1-bce0-74728be515ae	8992e301-301b-4565-bdcb-31efef059d12	b70fe0df-4f87-4275-8dec-6160f139ffea	\N	f	f	2026-08-21 11:43:53.229471	MEMBER	2026-08-21 11:43:53.229471
0e1e358a-6196-42cc-8e5f-b59e2bdd5e8c	8992e301-301b-4565-bdcb-31efef059d12	720e462f-449a-4ec5-85c5-7452c94823ce	\N	f	f	2026-08-21 11:43:53.229471	MEMBER	2026-08-21 11:43:53.229471
8bf9a889-7930-4b07-8e1d-d31960d9fb80	381c7079-39d6-41fa-844f-f68c4f280012	d896dfec-6d5f-4708-9d8b-ac7d97174165	\N	f	f	2026-08-21 11:43:53.254549	MEMBER	2026-08-21 11:43:53.254549
247ba1ae-61dc-4b82-80a1-37025fdd6eb4	381c7079-39d6-41fa-844f-f68c4f280012	d367d79b-6cb8-4215-856d-bd6832604eac	\N	f	f	2026-08-21 11:43:53.254549	MEMBER	2026-08-21 11:43:53.254549
db8d24f1-6014-494a-8129-5a7384206ff2	cebf275a-4846-4d7b-9d83-9de5d4f4b367	d896dfec-6d5f-4708-9d8b-ac7d97174165	\N	f	f	2026-08-21 11:43:53.268629	MEMBER	2026-08-21 11:43:53.268629
ba5b3825-c03e-4a35-b3a9-dfb91ecbcede	cebf275a-4846-4d7b-9d83-9de5d4f4b367	33a2cf07-6177-420e-bfd7-99cdae79b549	\N	f	f	2026-08-21 11:43:53.268629	MEMBER	2026-08-21 11:43:53.268629
a66fa349-4e4f-42db-a734-ba3c6c2c6d3e	6bb8b995-f8eb-4919-8cb4-20904f19e9db	d896dfec-6d5f-4708-9d8b-ac7d97174165	\N	f	f	2026-08-21 11:43:53.278851	MEMBER	2026-08-21 11:43:53.278851
e479a881-f8f4-4c44-80f9-838e4d0c913b	6bb8b995-f8eb-4919-8cb4-20904f19e9db	720e462f-449a-4ec5-85c5-7452c94823ce	\N	f	f	2026-08-21 11:43:53.278851	MEMBER	2026-08-21 11:43:53.278851
fe273d0f-bd93-4e65-97be-c1171f52adbf	4c4dde50-7579-4216-b174-f3fec9ecc8b8	d367d79b-6cb8-4215-856d-bd6832604eac	\N	f	f	2026-08-21 11:43:53.290279	MEMBER	2026-08-21 11:43:53.290279
1959f348-22d5-4ab9-b2c1-f7d8a6769e96	4c4dde50-7579-4216-b174-f3fec9ecc8b8	33a2cf07-6177-420e-bfd7-99cdae79b549	\N	f	f	2026-08-21 11:43:53.290279	MEMBER	2026-08-21 11:43:53.290279
63f1b536-f5c8-4c3b-a5b3-2635db52fd8f	79882a03-770f-49f8-8ec6-11d00b9b34b5	d367d79b-6cb8-4215-856d-bd6832604eac	\N	f	f	2026-08-21 11:43:53.302146	MEMBER	2026-08-21 11:43:53.302146
437a6f6a-ade7-4860-aa04-872179df2042	79882a03-770f-49f8-8ec6-11d00b9b34b5	720e462f-449a-4ec5-85c5-7452c94823ce	\N	f	f	2026-08-21 11:43:53.302146	MEMBER	2026-08-21 11:43:53.302146
b2f2eb99-8818-40e6-a798-f4aea8670992	b2a4cf94-be68-4f29-ba2f-18127d1b6059	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	caaa0382-408e-4a07-b19b-509d275bdd2c	f	f	2026-08-21 13:19:47.700517	MEMBER	2026-08-21 11:43:52.942945
9a9882d4-ad02-4ce8-a574-57ebf024f94d	4a34d8c5-9dec-46f7-afb3-bb4371bfc0b8	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	df9fd5b8-fc9e-415f-9f41-bf5e3942894f	f	f	2026-08-21 13:19:49.518235	MEMBER	2026-08-21 11:43:52.925125
e627923b-6787-4c57-a05c-9445e8984ef0	a78023ce-b676-4477-8292-3391ab5bfaca	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	ec888b6e-857c-4186-96d0-5853252b8f2e	f	f	2026-08-21 13:19:49.94217	MEMBER	2026-08-21 11:43:52.916613
9d18deb2-ec22-4ba0-862b-ee9a3fa47c78	15940406-00d7-4c70-aa78-110988b19fa0	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	cc9cd2f2-23bb-4ec7-98ad-4df3fd28ec78	f	f	2026-08-21 13:19:50.558566	MEMBER	2026-08-21 11:43:52.90033
6831de93-cb9e-4bb7-a3f3-ebd5472523d5	3e156f9e-511c-4a79-bdb6-ec91b1312d44	cfc3c138-db1a-4b67-ace1-0e1b21d42938	7758742a-ea12-4c4e-8339-d0abfa8deea8	f	f	2026-08-22 14:43:31.254886	MEMBER	2026-08-21 11:43:53.00946
6bd53beb-1d71-40cc-ba71-631568cda65f	559340ef-80f9-41cd-825c-5d58440e5eeb	cfc3c138-db1a-4b67-ace1-0e1b21d42938	adc052b5-2db1-497d-99a6-5a51e3f869e2	f	f	2026-08-22 14:43:35.570575	MEMBER	2026-08-21 11:43:53.020375
b495ccda-6a63-4dae-942c-6cf4b616fc58	db39ac3b-1ddb-4b1e-b359-d6867eaf1f70	cfc3c138-db1a-4b67-ace1-0e1b21d42938	45f7a9ee-abea-4018-b4c6-625873774521	f	f	2026-08-22 14:43:36.17529	MEMBER	2026-08-21 11:43:53.040104
2319dfa7-ddee-4247-ba85-6ce5bca79858	a86e8fab-273c-4640-8612-5083d856b56d	cfc3c138-db1a-4b67-ace1-0e1b21d42938	0d85a061-321c-4c06-b657-3a12521e15be	f	f	2026-08-22 14:43:36.509268	MEMBER	2026-08-21 11:43:52.953654
3fd35bea-27b7-424d-aaa1-ff4856b25b82	fb44203d-ced3-471f-bde0-9b20fa4af31d	cfc3c138-db1a-4b67-ace1-0e1b21d42938	090f359c-6e44-49ad-a61e-20a8cde092c2	f	f	2026-08-22 14:43:36.899065	MEMBER	2026-08-21 11:43:53.029418
9b2ebb75-7079-4cac-a7f7-0d34d5d640fa	211e7ab3-1d05-4227-bb01-cd27cd655691	33a2cf07-6177-420e-bfd7-99cdae79b549	b1b38390-3176-4c92-aa4c-79474268a771	f	f	2026-08-22 14:46:28.270766	MEMBER	2026-08-21 11:43:53.312079
ec3089ac-bc2b-4cce-b39a-bb6371cf1c43	a6af6560-fac5-4016-a8e0-48e521636bd2	33a2cf07-6177-420e-bfd7-99cdae79b549	a7c17fc3-c818-447c-b89e-641ce2529040	f	f	2026-08-22 14:46:28.701398	MEMBER	2026-08-21 11:43:53.101496
afee5f7f-59ff-4988-ae9c-5f9ba1af0e79	211e7ab3-1d05-4227-bb01-cd27cd655691	720e462f-449a-4ec5-85c5-7452c94823ce	\N	f	f	2026-08-21 11:43:53.312079	MEMBER	2026-08-21 11:43:53.312079
d4aa20dc-cea1-417a-9b12-359ecb3daab9	98a24b83-c339-40b8-95cc-13433ae8130a	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	a75f24aa-a68e-48bb-98cd-93f16ad6dcc0	f	f	2026-08-21 13:19:49.033033	MEMBER	2026-08-21 11:43:52.934305
0425d51f-e153-4740-a583-5b87a1512f3e	d8027034-474b-4b41-8cd5-8dcabcaedb6c	cfc3c138-db1a-4b67-ace1-0e1b21d42938	d65a2741-de68-45df-b4ef-5411c91bd230	f	f	2026-08-22 14:43:35.086075	MEMBER	2026-08-21 11:43:53.050361
2d7d2e1f-4167-4507-81f7-a843cdbe27dd	a78023ce-b676-4477-8292-3391ab5bfaca	cfc3c138-db1a-4b67-ace1-0e1b21d42938	ec888b6e-857c-4186-96d0-5853252b8f2e	f	f	2026-08-22 14:43:37.283537	MEMBER	2026-08-21 11:43:52.916613
\.


--
-- Data for Name: direct_conversations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.direct_conversations (id, user_a_id, user_b_id, last_message_id, last_message_time, created_at, updated_at, last_message_content, type, title) FROM stdin;
102a807d-7da1-42de-8802-9fcd154ac23f	b70fe0df-4f87-4275-8dec-6160f139ffea	d367d79b-6cb8-4215-856d-bd6832604eac	\N	2026-08-17 12:03:53.189792+00	2026-08-21 11:43:53.181667	2026-08-21 11:43:53.181667	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	P2P	\N
15940406-00d7-4c70-aa78-110988b19fa0	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	fa63627e-ae02-4b51-bea6-8c7af20501ad	\N	2026-08-14 12:03:52.908866+00	2026-08-21 11:43:52.90033	2026-08-21 11:43:52.90033	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	P2P	\N
211e7ab3-1d05-4227-bb01-cd27cd655691	33a2cf07-6177-420e-bfd7-99cdae79b549	720e462f-449a-4ec5-85c5-7452c94823ce	\N	2026-08-19 12:03:53.319124+00	2026-08-21 11:43:53.312079	2026-08-21 11:43:53.312079	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	P2P	\N
2ac06044-877a-40a1-a58b-978cbcb9f28a	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	fa63627e-ae02-4b51-bea6-8c7af20501ad	\N	2026-08-14 12:03:52.982211+00	2026-08-21 11:43:52.975888	2026-08-21 11:43:52.975888	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	P2P	\N
2bb46ccc-0450-452b-9286-8d46fbaa0aae	b70fe0df-4f87-4275-8dec-6160f139ffea	d896dfec-6d5f-4708-9d8b-ac7d97174165	\N	2026-08-12 12:03:53.176294+00	2026-08-21 11:43:53.171854	2026-08-21 11:43:53.171854	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	P2P	\N
381c7079-39d6-41fa-844f-f68c4f280012	d367d79b-6cb8-4215-856d-bd6832604eac	d896dfec-6d5f-4708-9d8b-ac7d97174165	\N	2026-08-11 12:03:53.261495+00	2026-08-21 11:43:53.254549	2026-08-21 11:43:53.254549	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	P2P	\N
3e156f9e-511c-4a79-bdb6-ec91b1312d44	8fcd1ec3-980c-422e-9956-aa675289b2b5	cfc3c138-db1a-4b67-ace1-0e1b21d42938	\N	2026-08-20 12:03:53.014495+00	2026-08-21 11:43:53.00946	2026-08-21 11:43:53.00946	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	P2P	\N
407b3cc9-1764-42c1-96a0-29b596339451	b70fe0df-4f87-4275-8dec-6160f139ffea	fa63627e-ae02-4b51-bea6-8c7af20501ad	\N	2026-08-12 12:03:52.993314+00	2026-08-21 11:43:52.988328	2026-08-21 11:43:52.988328	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	P2P	\N
4a34d8c5-9dec-46f7-afb3-bb4371bfc0b8	8fcd1ec3-980c-422e-9956-aa675289b2b5	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	\N	2026-08-16 12:03:52.928828+00	2026-08-21 11:43:52.925125	2026-08-21 11:43:52.925125	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	P2P	\N
4c4dde50-7579-4216-b174-f3fec9ecc8b8	33a2cf07-6177-420e-bfd7-99cdae79b549	d367d79b-6cb8-4215-856d-bd6832604eac	\N	2026-08-19 12:03:53.295356+00	2026-08-21 11:43:53.290279	2026-08-21 11:43:53.290279	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	P2P	\N
559340ef-80f9-41cd-825c-5d58440e5eeb	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	cfc3c138-db1a-4b67-ace1-0e1b21d42938	\N	2026-08-18 12:03:53.024307+00	2026-08-21 11:43:53.020375	2026-08-21 11:43:53.020375	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	P2P	\N
5b26daff-27a7-49d7-bff6-5345e48c1d30	720e462f-449a-4ec5-85c5-7452c94823ce	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	\N	2026-08-11 12:03:53.16637+00	2026-08-21 11:43:53.160673	2026-08-21 11:43:53.160673	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	P2P	\N
6bb8b995-f8eb-4919-8cb4-20904f19e9db	720e462f-449a-4ec5-85c5-7452c94823ce	d896dfec-6d5f-4708-9d8b-ac7d97174165	\N	2026-08-16 12:03:53.284881+00	2026-08-21 11:43:53.278851	2026-08-21 11:43:53.278851	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	P2P	\N
7130fefd-5219-42f4-acf2-fd6787a1c862	8fcd1ec3-980c-422e-9956-aa675289b2b5	fa63627e-ae02-4b51-bea6-8c7af20501ad	\N	2026-08-14 12:03:52.967695+00	2026-08-21 11:43:52.962313	2026-08-21 11:43:52.962313	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	P2P	\N
737f6edd-d78a-4ba6-bc76-838708df1c3d	8fcd1ec3-980c-422e-9956-aa675289b2b5	d896dfec-6d5f-4708-9d8b-ac7d97174165	\N	2026-08-14 12:03:53.085864+00	2026-08-21 11:43:53.081102	2026-08-21 11:43:53.081102	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	P2P	\N
7536e586-efc6-47fa-b53a-2ae05b8fe67c	33a2cf07-6177-420e-bfd7-99cdae79b549	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	\N	2026-08-11 12:03:53.154639+00	2026-08-21 11:43:53.14664	2026-08-21 11:43:53.14664	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	P2P	\N
79882a03-770f-49f8-8ec6-11d00b9b34b5	720e462f-449a-4ec5-85c5-7452c94823ce	d367d79b-6cb8-4215-856d-bd6832604eac	\N	2026-08-20 12:03:53.307045+00	2026-08-21 11:43:53.302146	2026-08-21 11:43:53.302146	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	P2P	\N
7cedae6b-bca8-43af-9686-c3253f325842	8fcd1ec3-980c-422e-9956-aa675289b2b5	d367d79b-6cb8-4215-856d-bd6832604eac	\N	2026-08-14 12:03:53.095305+00	2026-08-21 11:43:53.090684	2026-08-21 11:43:53.090684	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	P2P	\N
8992e301-301b-4565-bdcb-31efef059d12	720e462f-449a-4ec5-85c5-7452c94823ce	b70fe0df-4f87-4275-8dec-6160f139ffea	\N	2026-08-20 12:03:53.246782+00	2026-08-21 11:43:53.229471	2026-08-21 11:43:53.229471	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	P2P	\N
98a24b83-c339-40b8-95cc-13433ae8130a	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	\N	2026-08-13 12:03:52.93896+00	2026-08-21 11:43:52.934305	2026-08-21 11:43:52.934305	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	P2P	\N
9e8f9ead-a2dd-40ef-8ea0-50ad90ab956f	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	b70fe0df-4f87-4275-8dec-6160f139ffea	\N	2026-08-12 12:03:53.115679+00	2026-08-21 11:43:53.110668	2026-08-21 11:43:53.110668	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	P2P	\N
9eacdc06-eeb1-41ee-a9ee-13c1738114e1	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	d896dfec-6d5f-4708-9d8b-ac7d97174165	\N	2026-08-18 12:03:53.125248+00	2026-08-21 11:43:53.12119	2026-08-21 11:43:53.12119	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	P2P	\N
a6af6560-fac5-4016-a8e0-48e521636bd2	33a2cf07-6177-420e-bfd7-99cdae79b549	8fcd1ec3-980c-422e-9956-aa675289b2b5	\N	2026-08-20 12:03:53.105892+00	2026-08-21 11:43:53.101496	2026-08-21 11:43:53.101496	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	P2P	\N
a78023ce-b676-4477-8292-3391ab5bfaca	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	cfc3c138-db1a-4b67-ace1-0e1b21d42938	\N	2026-08-11 12:03:52.920889+00	2026-08-21 11:43:52.916613	2026-08-21 11:43:52.916613	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	P2P	\N
a86e8fab-273c-4640-8612-5083d856b56d	cfc3c138-db1a-4b67-ace1-0e1b21d42938	fa63627e-ae02-4b51-bea6-8c7af20501ad	\N	2026-08-13 12:03:52.957904+00	2026-08-21 11:43:52.953654	2026-08-21 11:43:52.953654	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	P2P	\N
aae65b59-7660-44b5-b925-a5c8b556324c	8fcd1ec3-980c-422e-9956-aa675289b2b5	b70fe0df-4f87-4275-8dec-6160f139ffea	\N	2026-08-15 12:03:53.075147+00	2026-08-21 11:43:53.070824	2026-08-21 11:43:53.070824	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	P2P	\N
b2a4cf94-be68-4f29-ba2f-18127d1b6059	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	b70fe0df-4f87-4275-8dec-6160f139ffea	\N	2026-08-20 12:03:52.947823+00	2026-08-21 11:43:52.942945	2026-08-21 11:43:52.942945	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	P2P	\N
c7d95fcd-7f41-4520-9139-f665ce545727	d896dfec-6d5f-4708-9d8b-ac7d97174165	fa63627e-ae02-4b51-bea6-8c7af20501ad	\N	2026-08-11 12:03:53.004267+00	2026-08-21 11:43:52.998978	2026-08-21 11:43:52.998978	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	P2P	\N
ca2a8210-b708-4702-a822-08146ba55319	8fcd1ec3-980c-422e-9956-aa675289b2b5	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	\N	2026-08-19 12:03:53.066069+00	2026-08-21 11:43:53.060569	2026-08-21 11:43:53.060569	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	P2P	\N
cebf275a-4846-4d7b-9d83-9de5d4f4b367	33a2cf07-6177-420e-bfd7-99cdae79b549	d896dfec-6d5f-4708-9d8b-ac7d97174165	\N	2026-08-19 12:03:53.273512+00	2026-08-21 11:43:53.268629	2026-08-21 11:43:53.268629	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	P2P	\N
d0a7dddc-75f0-4593-86e5-bd3fe9d870e8	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	d367d79b-6cb8-4215-856d-bd6832604eac	\N	2026-08-15 12:03:53.135629+00	2026-08-21 11:43:53.130694	2026-08-21 11:43:53.130694	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	P2P	\N
d8027034-474b-4b41-8cd5-8dcabcaedb6c	cfc3c138-db1a-4b67-ace1-0e1b21d42938	d367d79b-6cb8-4215-856d-bd6832604eac	\N	2026-08-19 12:03:53.055385+00	2026-08-21 11:43:53.050361	2026-08-21 11:43:53.050361	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	P2P	\N
db39ac3b-1ddb-4b1e-b359-d6867eaf1f70	cfc3c138-db1a-4b67-ace1-0e1b21d42938	d896dfec-6d5f-4708-9d8b-ac7d97174165	\N	2026-08-14 12:03:53.044583+00	2026-08-21 11:43:53.040104	2026-08-21 11:43:53.040104	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	P2P	\N
fa826862-22db-4973-a42e-47fb4a03c604	33a2cf07-6177-420e-bfd7-99cdae79b549	b70fe0df-4f87-4275-8dec-6160f139ffea	\N	2026-08-19 12:03:53.206727+00	2026-08-21 11:43:53.200921	2026-08-21 11:43:53.200921	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	P2P	\N
fb44203d-ced3-471f-bde0-9b20fa4af31d	b70fe0df-4f87-4275-8dec-6160f139ffea	cfc3c138-db1a-4b67-ace1-0e1b21d42938	\N	2026-08-12 12:03:53.035059+00	2026-08-21 11:43:53.029418	2026-08-21 11:43:53.029418	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	P2P	\N
\.


--
-- Data for Name: event_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.event_logs (id, user_id, conversation_id, event_type, payload, created_at) FROM stdin;
\.


--
-- Data for Name: message_reactions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.message_reactions (id, message_id, user_id, emoji, created_at) FROM stdin;
\.


--
-- Data for Name: messages; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.messages (id, conversation_id, sender_user_id, client_message_id, content, message_type, created_at, edited_at, deleted_at, reply_to_message_id) FROM stdin;
1478e862-c8fc-474d-8ae8-26d2a05b6c67	15940406-00d7-4c70-aa78-110988b19fa0	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	\N	Chào bạn, dạo này bạn có đang tìm hiểu gì mới không?	TEXT	2026-08-14 11:43:52.908866	\N	\N	\N
06e2259d-a006-43db-b600-2a2d3a1ecd50	15940406-00d7-4c70-aa78-110988b19fa0	fa63627e-ae02-4b51-bea6-8c7af20501ad	\N	Mình đang tập trung nghiên cứu AI và phát triển Backend.	TEXT	2026-08-14 11:48:52.908866	\N	\N	\N
757c7f6e-2e48-49d9-8462-0daafdd7d532	15940406-00d7-4c70-aa78-110988b19fa0	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	\N	Hay quá, mình cũng đang làm dự án liên quan đến Machine Learning và tối ưu hóa hệ thống.	TEXT	2026-08-14 11:53:52.908866	\N	\N	\N
a37c8d07-24d4-421e-aa34-a7f9d7725a1e	15940406-00d7-4c70-aa78-110988b19fa0	fa63627e-ae02-4b51-bea6-8c7af20501ad	\N	Thế hôm nào chúng ta có thể cafe trao đổi thêm nhé. Chắc sẽ hợp tác được nhiều đấy!	TEXT	2026-08-14 11:58:52.908866	\N	\N	\N
cc9cd2f2-23bb-4ec7-98ad-4df3fd28ec78	15940406-00d7-4c70-aa78-110988b19fa0	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	\N	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	TEXT	2026-08-14 12:03:52.908866	\N	\N	\N
85630f0c-0ec4-4e74-b6eb-14c3c1a0d004	a78023ce-b676-4477-8292-3391ab5bfaca	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	\N	Chào bạn, dạo này bạn có đang tìm hiểu gì mới không?	TEXT	2026-08-11 11:43:52.920889	\N	\N	\N
636b85a6-be5b-4258-b343-3c75d5ce9dc1	a78023ce-b676-4477-8292-3391ab5bfaca	cfc3c138-db1a-4b67-ace1-0e1b21d42938	\N	Mình đang tập trung nghiên cứu AI và phát triển Backend.	TEXT	2026-08-11 11:48:52.920889	\N	\N	\N
594fadc1-94b1-4ccf-acf2-31703a21cc21	a78023ce-b676-4477-8292-3391ab5bfaca	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	\N	Hay quá, mình cũng đang làm dự án liên quan đến Machine Learning và tối ưu hóa hệ thống.	TEXT	2026-08-11 11:53:52.920889	\N	\N	\N
3be09e39-875f-4ff8-8670-064a19839c67	a78023ce-b676-4477-8292-3391ab5bfaca	cfc3c138-db1a-4b67-ace1-0e1b21d42938	\N	Thế hôm nào chúng ta có thể cafe trao đổi thêm nhé. Chắc sẽ hợp tác được nhiều đấy!	TEXT	2026-08-11 11:58:52.920889	\N	\N	\N
ec888b6e-857c-4186-96d0-5853252b8f2e	a78023ce-b676-4477-8292-3391ab5bfaca	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	\N	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	TEXT	2026-08-11 12:03:52.920889	\N	\N	\N
2a6380ae-227b-430e-9e8d-8231b026f2c2	4a34d8c5-9dec-46f7-afb3-bb4371bfc0b8	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	\N	Chào bạn, dạo này bạn có đang tìm hiểu gì mới không?	TEXT	2026-08-16 11:43:52.928828	\N	\N	\N
841e9125-d1d6-4cf3-bfb4-162132b31161	4a34d8c5-9dec-46f7-afb3-bb4371bfc0b8	8fcd1ec3-980c-422e-9956-aa675289b2b5	\N	Mình đang tập trung nghiên cứu AI và phát triển Backend.	TEXT	2026-08-16 11:48:52.928828	\N	\N	\N
913449c6-8467-47d9-b918-d822cec97404	4a34d8c5-9dec-46f7-afb3-bb4371bfc0b8	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	\N	Hay quá, mình cũng đang làm dự án liên quan đến Machine Learning và tối ưu hóa hệ thống.	TEXT	2026-08-16 11:53:52.928828	\N	\N	\N
0fd3aa97-dcec-41cc-b1bd-ad38e00a1865	4a34d8c5-9dec-46f7-afb3-bb4371bfc0b8	8fcd1ec3-980c-422e-9956-aa675289b2b5	\N	Thế hôm nào chúng ta có thể cafe trao đổi thêm nhé. Chắc sẽ hợp tác được nhiều đấy!	TEXT	2026-08-16 11:58:52.928828	\N	\N	\N
df9fd5b8-fc9e-415f-9f41-bf5e3942894f	4a34d8c5-9dec-46f7-afb3-bb4371bfc0b8	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	\N	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	TEXT	2026-08-16 12:03:52.928828	\N	\N	\N
13d05342-2762-4cfd-80da-7946cf78a0a7	98a24b83-c339-40b8-95cc-13433ae8130a	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	\N	Chào bạn, dạo này bạn có đang tìm hiểu gì mới không?	TEXT	2026-08-13 11:43:52.93896	\N	\N	\N
2d9c3d27-4403-46d2-a123-7b6e70ef5d78	98a24b83-c339-40b8-95cc-13433ae8130a	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	\N	Mình đang tập trung nghiên cứu AI và phát triển Backend.	TEXT	2026-08-13 11:48:52.93896	\N	\N	\N
42ef397c-247b-4c87-9e0f-8d43c97210b0	98a24b83-c339-40b8-95cc-13433ae8130a	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	\N	Hay quá, mình cũng đang làm dự án liên quan đến Machine Learning và tối ưu hóa hệ thống.	TEXT	2026-08-13 11:53:52.93896	\N	\N	\N
775b4779-4f0f-42ff-aba3-31b6c1066b70	98a24b83-c339-40b8-95cc-13433ae8130a	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	\N	Thế hôm nào chúng ta có thể cafe trao đổi thêm nhé. Chắc sẽ hợp tác được nhiều đấy!	TEXT	2026-08-13 11:58:52.93896	\N	\N	\N
a75f24aa-a68e-48bb-98cd-93f16ad6dcc0	98a24b83-c339-40b8-95cc-13433ae8130a	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	\N	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	TEXT	2026-08-13 12:03:52.93896	\N	\N	\N
26eb398c-b2d8-48e4-b39e-85a6b9a8bdeb	b2a4cf94-be68-4f29-ba2f-18127d1b6059	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	\N	Chào bạn, dạo này bạn có đang tìm hiểu gì mới không?	TEXT	2026-08-20 11:43:52.947823	\N	\N	\N
01d2d215-513b-4e0f-bc23-8942f16df6ce	b2a4cf94-be68-4f29-ba2f-18127d1b6059	b70fe0df-4f87-4275-8dec-6160f139ffea	\N	Mình đang tập trung nghiên cứu AI và phát triển Backend.	TEXT	2026-08-20 11:48:52.947823	\N	\N	\N
d08aac6b-42b1-4571-a395-feb15f5b6fa0	b2a4cf94-be68-4f29-ba2f-18127d1b6059	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	\N	Hay quá, mình cũng đang làm dự án liên quan đến Machine Learning và tối ưu hóa hệ thống.	TEXT	2026-08-20 11:53:52.947823	\N	\N	\N
af64120f-01b0-4b6a-8429-4b8dac8921e4	b2a4cf94-be68-4f29-ba2f-18127d1b6059	b70fe0df-4f87-4275-8dec-6160f139ffea	\N	Thế hôm nào chúng ta có thể cafe trao đổi thêm nhé. Chắc sẽ hợp tác được nhiều đấy!	TEXT	2026-08-20 11:58:52.947823	\N	\N	\N
caaa0382-408e-4a07-b19b-509d275bdd2c	b2a4cf94-be68-4f29-ba2f-18127d1b6059	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	\N	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	TEXT	2026-08-20 12:03:52.947823	\N	\N	\N
1cab5a5a-26c5-4474-9bac-c1c96033cdb3	a86e8fab-273c-4640-8612-5083d856b56d	fa63627e-ae02-4b51-bea6-8c7af20501ad	\N	Chào bạn, dạo này bạn có đang tìm hiểu gì mới không?	TEXT	2026-08-13 11:43:52.957904	\N	\N	\N
b5274fc2-1679-4f64-9c27-373dca8768bb	a86e8fab-273c-4640-8612-5083d856b56d	cfc3c138-db1a-4b67-ace1-0e1b21d42938	\N	Mình đang tập trung nghiên cứu AI và phát triển Backend.	TEXT	2026-08-13 11:48:52.957904	\N	\N	\N
293b0783-5c97-4626-b56d-7e6b5bc95c00	a86e8fab-273c-4640-8612-5083d856b56d	fa63627e-ae02-4b51-bea6-8c7af20501ad	\N	Hay quá, mình cũng đang làm dự án liên quan đến Machine Learning và tối ưu hóa hệ thống.	TEXT	2026-08-13 11:53:52.957904	\N	\N	\N
9837d783-e811-4ffd-ac99-d7e7cdb45a8f	a86e8fab-273c-4640-8612-5083d856b56d	cfc3c138-db1a-4b67-ace1-0e1b21d42938	\N	Thế hôm nào chúng ta có thể cafe trao đổi thêm nhé. Chắc sẽ hợp tác được nhiều đấy!	TEXT	2026-08-13 11:58:52.957904	\N	\N	\N
0d85a061-321c-4c06-b657-3a12521e15be	a86e8fab-273c-4640-8612-5083d856b56d	fa63627e-ae02-4b51-bea6-8c7af20501ad	\N	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	TEXT	2026-08-13 12:03:52.957904	\N	\N	\N
ae2be6af-5ac4-4b3d-98a1-2c59e359a627	7130fefd-5219-42f4-acf2-fd6787a1c862	fa63627e-ae02-4b51-bea6-8c7af20501ad	\N	Chào bạn, dạo này bạn có đang tìm hiểu gì mới không?	TEXT	2026-08-14 11:43:52.967695	\N	\N	\N
1096af2f-ff2d-474c-9e62-8bec5b9a99d4	7130fefd-5219-42f4-acf2-fd6787a1c862	8fcd1ec3-980c-422e-9956-aa675289b2b5	\N	Mình đang tập trung nghiên cứu AI và phát triển Backend.	TEXT	2026-08-14 11:48:52.967695	\N	\N	\N
416c2fb5-aa1e-4bc6-af25-0ba5582f2112	7130fefd-5219-42f4-acf2-fd6787a1c862	fa63627e-ae02-4b51-bea6-8c7af20501ad	\N	Hay quá, mình cũng đang làm dự án liên quan đến Machine Learning và tối ưu hóa hệ thống.	TEXT	2026-08-14 11:53:52.967695	\N	\N	\N
c0418711-2968-441c-a935-2706cbd26d6e	7130fefd-5219-42f4-acf2-fd6787a1c862	8fcd1ec3-980c-422e-9956-aa675289b2b5	\N	Thế hôm nào chúng ta có thể cafe trao đổi thêm nhé. Chắc sẽ hợp tác được nhiều đấy!	TEXT	2026-08-14 11:58:52.967695	\N	\N	\N
eb7f0581-ad7c-4338-8111-1b3e9b1ad494	7130fefd-5219-42f4-acf2-fd6787a1c862	fa63627e-ae02-4b51-bea6-8c7af20501ad	\N	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	TEXT	2026-08-14 12:03:52.967695	\N	\N	\N
2eff1907-e217-425c-9804-a4f416207f1b	2ac06044-877a-40a1-a58b-978cbcb9f28a	fa63627e-ae02-4b51-bea6-8c7af20501ad	\N	Chào bạn, dạo này bạn có đang tìm hiểu gì mới không?	TEXT	2026-08-14 11:43:52.982211	\N	\N	\N
d91e1164-7055-495b-95b2-cf46dd4ec8f6	2ac06044-877a-40a1-a58b-978cbcb9f28a	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	\N	Mình đang tập trung nghiên cứu AI và phát triển Backend.	TEXT	2026-08-14 11:48:52.982211	\N	\N	\N
53694593-f6c8-4ec0-9113-22ece26f4750	2ac06044-877a-40a1-a58b-978cbcb9f28a	fa63627e-ae02-4b51-bea6-8c7af20501ad	\N	Hay quá, mình cũng đang làm dự án liên quan đến Machine Learning và tối ưu hóa hệ thống.	TEXT	2026-08-14 11:53:52.982211	\N	\N	\N
caf91b21-95a0-4712-ac71-0543e02c8ee9	2ac06044-877a-40a1-a58b-978cbcb9f28a	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	\N	Thế hôm nào chúng ta có thể cafe trao đổi thêm nhé. Chắc sẽ hợp tác được nhiều đấy!	TEXT	2026-08-14 11:58:52.982211	\N	\N	\N
d74038f7-32ce-485a-9d4e-704f7fd3d74b	2ac06044-877a-40a1-a58b-978cbcb9f28a	fa63627e-ae02-4b51-bea6-8c7af20501ad	\N	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	TEXT	2026-08-14 12:03:52.982211	\N	\N	\N
d740e019-2111-40a6-bc48-311446550140	407b3cc9-1764-42c1-96a0-29b596339451	fa63627e-ae02-4b51-bea6-8c7af20501ad	\N	Chào bạn, dạo này bạn có đang tìm hiểu gì mới không?	TEXT	2026-08-12 11:43:52.993314	\N	\N	\N
4126d317-0994-4e3d-af7f-4275f20dc2ad	407b3cc9-1764-42c1-96a0-29b596339451	b70fe0df-4f87-4275-8dec-6160f139ffea	\N	Mình đang tập trung nghiên cứu AI và phát triển Backend.	TEXT	2026-08-12 11:48:52.993314	\N	\N	\N
ce80afd5-9d11-4abb-bcdb-6868da2c8ad7	407b3cc9-1764-42c1-96a0-29b596339451	fa63627e-ae02-4b51-bea6-8c7af20501ad	\N	Hay quá, mình cũng đang làm dự án liên quan đến Machine Learning và tối ưu hóa hệ thống.	TEXT	2026-08-12 11:53:52.993314	\N	\N	\N
f128d469-5f84-4212-bfa0-ec92f0560485	407b3cc9-1764-42c1-96a0-29b596339451	b70fe0df-4f87-4275-8dec-6160f139ffea	\N	Thế hôm nào chúng ta có thể cafe trao đổi thêm nhé. Chắc sẽ hợp tác được nhiều đấy!	TEXT	2026-08-12 11:58:52.993314	\N	\N	\N
69d0106e-f817-4549-877c-d8af341f27ca	407b3cc9-1764-42c1-96a0-29b596339451	fa63627e-ae02-4b51-bea6-8c7af20501ad	\N	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	TEXT	2026-08-12 12:03:52.993314	\N	\N	\N
43e95683-ae00-455b-a31e-2c5ee66b69da	c7d95fcd-7f41-4520-9139-f665ce545727	fa63627e-ae02-4b51-bea6-8c7af20501ad	\N	Chào bạn, dạo này bạn có đang tìm hiểu gì mới không?	TEXT	2026-08-11 11:43:53.004267	\N	\N	\N
f32cf373-a710-46bf-80e1-b45814d2c0c2	c7d95fcd-7f41-4520-9139-f665ce545727	d896dfec-6d5f-4708-9d8b-ac7d97174165	\N	Mình đang tập trung nghiên cứu AI và phát triển Backend.	TEXT	2026-08-11 11:48:53.004267	\N	\N	\N
289f0acb-33af-4c0e-a5f4-c5d67bc4d954	c7d95fcd-7f41-4520-9139-f665ce545727	fa63627e-ae02-4b51-bea6-8c7af20501ad	\N	Hay quá, mình cũng đang làm dự án liên quan đến Machine Learning và tối ưu hóa hệ thống.	TEXT	2026-08-11 11:53:53.004267	\N	\N	\N
d404a23a-5821-4cc7-90e7-cd30b7c29bc0	c7d95fcd-7f41-4520-9139-f665ce545727	d896dfec-6d5f-4708-9d8b-ac7d97174165	\N	Thế hôm nào chúng ta có thể cafe trao đổi thêm nhé. Chắc sẽ hợp tác được nhiều đấy!	TEXT	2026-08-11 11:58:53.004267	\N	\N	\N
caa8faaa-1c81-4791-a3ce-b6951db24023	c7d95fcd-7f41-4520-9139-f665ce545727	fa63627e-ae02-4b51-bea6-8c7af20501ad	\N	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	TEXT	2026-08-11 12:03:53.004267	\N	\N	\N
9a996c2a-3b14-4e99-a013-d2df69878fe6	3e156f9e-511c-4a79-bdb6-ec91b1312d44	cfc3c138-db1a-4b67-ace1-0e1b21d42938	\N	Chào bạn, dạo này bạn có đang tìm hiểu gì mới không?	TEXT	2026-08-20 11:43:53.014495	\N	\N	\N
736d1495-7ea5-42b9-a7be-907c1335bdd1	3e156f9e-511c-4a79-bdb6-ec91b1312d44	8fcd1ec3-980c-422e-9956-aa675289b2b5	\N	Mình đang tập trung nghiên cứu AI và phát triển Backend.	TEXT	2026-08-20 11:48:53.014495	\N	\N	\N
4896b8aa-5ebc-4ebd-bc57-e84f12df563a	3e156f9e-511c-4a79-bdb6-ec91b1312d44	cfc3c138-db1a-4b67-ace1-0e1b21d42938	\N	Hay quá, mình cũng đang làm dự án liên quan đến Machine Learning và tối ưu hóa hệ thống.	TEXT	2026-08-20 11:53:53.014495	\N	\N	\N
6b9496c0-4112-4e02-9b8d-ec88ee0260d5	3e156f9e-511c-4a79-bdb6-ec91b1312d44	8fcd1ec3-980c-422e-9956-aa675289b2b5	\N	Thế hôm nào chúng ta có thể cafe trao đổi thêm nhé. Chắc sẽ hợp tác được nhiều đấy!	TEXT	2026-08-20 11:58:53.014495	\N	\N	\N
7758742a-ea12-4c4e-8339-d0abfa8deea8	3e156f9e-511c-4a79-bdb6-ec91b1312d44	cfc3c138-db1a-4b67-ace1-0e1b21d42938	\N	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	TEXT	2026-08-20 12:03:53.014495	\N	\N	\N
aee7b680-5a86-400e-a6fc-4f9fb4b9d36c	559340ef-80f9-41cd-825c-5d58440e5eeb	cfc3c138-db1a-4b67-ace1-0e1b21d42938	\N	Chào bạn, dạo này bạn có đang tìm hiểu gì mới không?	TEXT	2026-08-18 11:43:53.024307	\N	\N	\N
2c3778ef-2a1e-4eef-a1d2-8e2aed946cdf	559340ef-80f9-41cd-825c-5d58440e5eeb	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	\N	Mình đang tập trung nghiên cứu AI và phát triển Backend.	TEXT	2026-08-18 11:48:53.024307	\N	\N	\N
df613479-f9d7-4360-b256-c6607522963d	559340ef-80f9-41cd-825c-5d58440e5eeb	cfc3c138-db1a-4b67-ace1-0e1b21d42938	\N	Hay quá, mình cũng đang làm dự án liên quan đến Machine Learning và tối ưu hóa hệ thống.	TEXT	2026-08-18 11:53:53.024307	\N	\N	\N
d6853d21-dae5-4afd-957e-80a00ff35a4e	559340ef-80f9-41cd-825c-5d58440e5eeb	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	\N	Thế hôm nào chúng ta có thể cafe trao đổi thêm nhé. Chắc sẽ hợp tác được nhiều đấy!	TEXT	2026-08-18 11:58:53.024307	\N	\N	\N
adc052b5-2db1-497d-99a6-5a51e3f869e2	559340ef-80f9-41cd-825c-5d58440e5eeb	cfc3c138-db1a-4b67-ace1-0e1b21d42938	\N	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	TEXT	2026-08-18 12:03:53.024307	\N	\N	\N
7fb0125c-cb41-46c9-9e89-14c678e17e6d	fb44203d-ced3-471f-bde0-9b20fa4af31d	cfc3c138-db1a-4b67-ace1-0e1b21d42938	\N	Chào bạn, dạo này bạn có đang tìm hiểu gì mới không?	TEXT	2026-08-12 11:43:53.035059	\N	\N	\N
cf8a7bc9-bf4b-496b-affd-6d44079dfbc9	fb44203d-ced3-471f-bde0-9b20fa4af31d	b70fe0df-4f87-4275-8dec-6160f139ffea	\N	Mình đang tập trung nghiên cứu AI và phát triển Backend.	TEXT	2026-08-12 11:48:53.035059	\N	\N	\N
3af00675-8940-4b67-a779-831421bbff13	fb44203d-ced3-471f-bde0-9b20fa4af31d	cfc3c138-db1a-4b67-ace1-0e1b21d42938	\N	Hay quá, mình cũng đang làm dự án liên quan đến Machine Learning và tối ưu hóa hệ thống.	TEXT	2026-08-12 11:53:53.035059	\N	\N	\N
1af3bf99-9d42-490e-920d-e886aa68823a	fb44203d-ced3-471f-bde0-9b20fa4af31d	b70fe0df-4f87-4275-8dec-6160f139ffea	\N	Thế hôm nào chúng ta có thể cafe trao đổi thêm nhé. Chắc sẽ hợp tác được nhiều đấy!	TEXT	2026-08-12 11:58:53.035059	\N	\N	\N
090f359c-6e44-49ad-a61e-20a8cde092c2	fb44203d-ced3-471f-bde0-9b20fa4af31d	cfc3c138-db1a-4b67-ace1-0e1b21d42938	\N	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	TEXT	2026-08-12 12:03:53.035059	\N	\N	\N
b26303e7-983c-4b66-b7a2-6b281e9fb318	db39ac3b-1ddb-4b1e-b359-d6867eaf1f70	cfc3c138-db1a-4b67-ace1-0e1b21d42938	\N	Chào bạn, dạo này bạn có đang tìm hiểu gì mới không?	TEXT	2026-08-14 11:43:53.044583	\N	\N	\N
5b407c60-6c6b-4d54-adbc-b73b3f352001	db39ac3b-1ddb-4b1e-b359-d6867eaf1f70	d896dfec-6d5f-4708-9d8b-ac7d97174165	\N	Mình đang tập trung nghiên cứu AI và phát triển Backend.	TEXT	2026-08-14 11:48:53.044583	\N	\N	\N
8a5a36f7-8190-4163-82f0-c7f548cb8b8e	db39ac3b-1ddb-4b1e-b359-d6867eaf1f70	cfc3c138-db1a-4b67-ace1-0e1b21d42938	\N	Hay quá, mình cũng đang làm dự án liên quan đến Machine Learning và tối ưu hóa hệ thống.	TEXT	2026-08-14 11:53:53.044583	\N	\N	\N
dcc4f010-257a-4504-82d1-838c1641b2ee	db39ac3b-1ddb-4b1e-b359-d6867eaf1f70	d896dfec-6d5f-4708-9d8b-ac7d97174165	\N	Thế hôm nào chúng ta có thể cafe trao đổi thêm nhé. Chắc sẽ hợp tác được nhiều đấy!	TEXT	2026-08-14 11:58:53.044583	\N	\N	\N
45f7a9ee-abea-4018-b4c6-625873774521	db39ac3b-1ddb-4b1e-b359-d6867eaf1f70	cfc3c138-db1a-4b67-ace1-0e1b21d42938	\N	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	TEXT	2026-08-14 12:03:53.044583	\N	\N	\N
0c98156f-dc6c-486a-8b09-05c9fda20f2c	d8027034-474b-4b41-8cd5-8dcabcaedb6c	cfc3c138-db1a-4b67-ace1-0e1b21d42938	\N	Chào bạn, dạo này bạn có đang tìm hiểu gì mới không?	TEXT	2026-08-19 11:43:53.055385	\N	\N	\N
bba07246-f0e8-4b5d-80ce-dffac2e1b179	d8027034-474b-4b41-8cd5-8dcabcaedb6c	d367d79b-6cb8-4215-856d-bd6832604eac	\N	Mình đang tập trung nghiên cứu AI và phát triển Backend.	TEXT	2026-08-19 11:48:53.055385	\N	\N	\N
38add85b-3a11-4b69-8477-2a7dd635e436	d8027034-474b-4b41-8cd5-8dcabcaedb6c	cfc3c138-db1a-4b67-ace1-0e1b21d42938	\N	Hay quá, mình cũng đang làm dự án liên quan đến Machine Learning và tối ưu hóa hệ thống.	TEXT	2026-08-19 11:53:53.055385	\N	\N	\N
1ea3035d-3841-4374-bd75-7b6a8a2f88f1	d8027034-474b-4b41-8cd5-8dcabcaedb6c	d367d79b-6cb8-4215-856d-bd6832604eac	\N	Thế hôm nào chúng ta có thể cafe trao đổi thêm nhé. Chắc sẽ hợp tác được nhiều đấy!	TEXT	2026-08-19 11:58:53.055385	\N	\N	\N
d65a2741-de68-45df-b4ef-5411c91bd230	d8027034-474b-4b41-8cd5-8dcabcaedb6c	cfc3c138-db1a-4b67-ace1-0e1b21d42938	\N	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	TEXT	2026-08-19 12:03:53.055385	\N	\N	\N
076c53d3-d64f-4358-ac7e-9028ed0424dc	ca2a8210-b708-4702-a822-08146ba55319	8fcd1ec3-980c-422e-9956-aa675289b2b5	\N	Chào bạn, dạo này bạn có đang tìm hiểu gì mới không?	TEXT	2026-08-19 11:43:53.066069	\N	\N	\N
2fd70dbf-6ebe-4903-943c-e123736d21d2	ca2a8210-b708-4702-a822-08146ba55319	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	\N	Mình đang tập trung nghiên cứu AI và phát triển Backend.	TEXT	2026-08-19 11:48:53.066069	\N	\N	\N
910118fd-d6e3-4ca6-8c77-870c4341fa11	ca2a8210-b708-4702-a822-08146ba55319	8fcd1ec3-980c-422e-9956-aa675289b2b5	\N	Hay quá, mình cũng đang làm dự án liên quan đến Machine Learning và tối ưu hóa hệ thống.	TEXT	2026-08-19 11:53:53.066069	\N	\N	\N
a94abd3a-a40a-412a-8d30-701ded6858b0	ca2a8210-b708-4702-a822-08146ba55319	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	\N	Thế hôm nào chúng ta có thể cafe trao đổi thêm nhé. Chắc sẽ hợp tác được nhiều đấy!	TEXT	2026-08-19 11:58:53.066069	\N	\N	\N
1fc0d143-ab74-4fa2-9c26-b3be91ee5e45	ca2a8210-b708-4702-a822-08146ba55319	8fcd1ec3-980c-422e-9956-aa675289b2b5	\N	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	TEXT	2026-08-19 12:03:53.066069	\N	\N	\N
1d72550f-da54-493e-9a4d-05822898b208	aae65b59-7660-44b5-b925-a5c8b556324c	8fcd1ec3-980c-422e-9956-aa675289b2b5	\N	Chào bạn, dạo này bạn có đang tìm hiểu gì mới không?	TEXT	2026-08-15 11:43:53.075147	\N	\N	\N
167b43c4-970c-4c85-947e-fd6345bfafe9	aae65b59-7660-44b5-b925-a5c8b556324c	b70fe0df-4f87-4275-8dec-6160f139ffea	\N	Mình đang tập trung nghiên cứu AI và phát triển Backend.	TEXT	2026-08-15 11:48:53.075147	\N	\N	\N
b82258af-4762-4343-b1f5-996801fa84c5	aae65b59-7660-44b5-b925-a5c8b556324c	8fcd1ec3-980c-422e-9956-aa675289b2b5	\N	Hay quá, mình cũng đang làm dự án liên quan đến Machine Learning và tối ưu hóa hệ thống.	TEXT	2026-08-15 11:53:53.075147	\N	\N	\N
d070b0a2-d664-4596-8017-45f5054032d4	aae65b59-7660-44b5-b925-a5c8b556324c	b70fe0df-4f87-4275-8dec-6160f139ffea	\N	Thế hôm nào chúng ta có thể cafe trao đổi thêm nhé. Chắc sẽ hợp tác được nhiều đấy!	TEXT	2026-08-15 11:58:53.075147	\N	\N	\N
19a58e3e-55f8-467e-b450-a501a0e9f267	aae65b59-7660-44b5-b925-a5c8b556324c	8fcd1ec3-980c-422e-9956-aa675289b2b5	\N	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	TEXT	2026-08-15 12:03:53.075147	\N	\N	\N
9eeaac2a-4cfa-4c90-bae9-c36b2922bb56	737f6edd-d78a-4ba6-bc76-838708df1c3d	8fcd1ec3-980c-422e-9956-aa675289b2b5	\N	Chào bạn, dạo này bạn có đang tìm hiểu gì mới không?	TEXT	2026-08-14 11:43:53.085864	\N	\N	\N
5ae9fad9-d9dc-4843-8b41-930c160926ff	737f6edd-d78a-4ba6-bc76-838708df1c3d	d896dfec-6d5f-4708-9d8b-ac7d97174165	\N	Mình đang tập trung nghiên cứu AI và phát triển Backend.	TEXT	2026-08-14 11:48:53.085864	\N	\N	\N
1692885e-2136-44f8-81c8-266d11fdec97	737f6edd-d78a-4ba6-bc76-838708df1c3d	8fcd1ec3-980c-422e-9956-aa675289b2b5	\N	Hay quá, mình cũng đang làm dự án liên quan đến Machine Learning và tối ưu hóa hệ thống.	TEXT	2026-08-14 11:53:53.085864	\N	\N	\N
a69a3e81-fc98-4c7c-b6f3-91fe0d55d435	737f6edd-d78a-4ba6-bc76-838708df1c3d	d896dfec-6d5f-4708-9d8b-ac7d97174165	\N	Thế hôm nào chúng ta có thể cafe trao đổi thêm nhé. Chắc sẽ hợp tác được nhiều đấy!	TEXT	2026-08-14 11:58:53.085864	\N	\N	\N
4b97da00-05bc-413e-9838-705750a472a6	737f6edd-d78a-4ba6-bc76-838708df1c3d	8fcd1ec3-980c-422e-9956-aa675289b2b5	\N	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	TEXT	2026-08-14 12:03:53.085864	\N	\N	\N
813f62df-52ec-4021-b0cd-bb009e4908cb	7cedae6b-bca8-43af-9686-c3253f325842	8fcd1ec3-980c-422e-9956-aa675289b2b5	\N	Chào bạn, dạo này bạn có đang tìm hiểu gì mới không?	TEXT	2026-08-14 11:43:53.095305	\N	\N	\N
65783357-92b0-4575-b0a9-5f3c402bdbca	7cedae6b-bca8-43af-9686-c3253f325842	d367d79b-6cb8-4215-856d-bd6832604eac	\N	Mình đang tập trung nghiên cứu AI và phát triển Backend.	TEXT	2026-08-14 11:48:53.095305	\N	\N	\N
50538e4e-f40b-4f3a-b5b0-124c0b4bc37c	7cedae6b-bca8-43af-9686-c3253f325842	8fcd1ec3-980c-422e-9956-aa675289b2b5	\N	Hay quá, mình cũng đang làm dự án liên quan đến Machine Learning và tối ưu hóa hệ thống.	TEXT	2026-08-14 11:53:53.095305	\N	\N	\N
e08363c9-eccc-4387-be81-b8aaa0ef72b4	7cedae6b-bca8-43af-9686-c3253f325842	d367d79b-6cb8-4215-856d-bd6832604eac	\N	Thế hôm nào chúng ta có thể cafe trao đổi thêm nhé. Chắc sẽ hợp tác được nhiều đấy!	TEXT	2026-08-14 11:58:53.095305	\N	\N	\N
f06225d1-203d-4df7-9ac8-2e9fad2eef4e	7cedae6b-bca8-43af-9686-c3253f325842	8fcd1ec3-980c-422e-9956-aa675289b2b5	\N	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	TEXT	2026-08-14 12:03:53.095305	\N	\N	\N
5f164160-1885-4480-980f-0cd811365bf9	a6af6560-fac5-4016-a8e0-48e521636bd2	8fcd1ec3-980c-422e-9956-aa675289b2b5	\N	Chào bạn, dạo này bạn có đang tìm hiểu gì mới không?	TEXT	2026-08-20 11:43:53.105892	\N	\N	\N
5b9d26b2-e3bc-48a5-bad4-66067b3a1255	a6af6560-fac5-4016-a8e0-48e521636bd2	33a2cf07-6177-420e-bfd7-99cdae79b549	\N	Mình đang tập trung nghiên cứu AI và phát triển Backend.	TEXT	2026-08-20 11:48:53.105892	\N	\N	\N
f914b8ef-9b85-4c62-9e97-60a7450c1d90	a6af6560-fac5-4016-a8e0-48e521636bd2	8fcd1ec3-980c-422e-9956-aa675289b2b5	\N	Hay quá, mình cũng đang làm dự án liên quan đến Machine Learning và tối ưu hóa hệ thống.	TEXT	2026-08-20 11:53:53.105892	\N	\N	\N
9193802d-babf-4744-872e-c558366aea84	a6af6560-fac5-4016-a8e0-48e521636bd2	33a2cf07-6177-420e-bfd7-99cdae79b549	\N	Thế hôm nào chúng ta có thể cafe trao đổi thêm nhé. Chắc sẽ hợp tác được nhiều đấy!	TEXT	2026-08-20 11:58:53.105892	\N	\N	\N
a7c17fc3-c818-447c-b89e-641ce2529040	a6af6560-fac5-4016-a8e0-48e521636bd2	8fcd1ec3-980c-422e-9956-aa675289b2b5	\N	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	TEXT	2026-08-20 12:03:53.105892	\N	\N	\N
a66a50e8-ae77-47da-82f9-45b150bb14d6	9e8f9ead-a2dd-40ef-8ea0-50ad90ab956f	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	\N	Chào bạn, dạo này bạn có đang tìm hiểu gì mới không?	TEXT	2026-08-12 11:43:53.115679	\N	\N	\N
7dc5e072-84dc-45a1-9083-17d22e72286a	9e8f9ead-a2dd-40ef-8ea0-50ad90ab956f	b70fe0df-4f87-4275-8dec-6160f139ffea	\N	Mình đang tập trung nghiên cứu AI và phát triển Backend.	TEXT	2026-08-12 11:48:53.115679	\N	\N	\N
0f250cff-5ed2-4b44-8ba8-70061ad97a39	9e8f9ead-a2dd-40ef-8ea0-50ad90ab956f	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	\N	Hay quá, mình cũng đang làm dự án liên quan đến Machine Learning và tối ưu hóa hệ thống.	TEXT	2026-08-12 11:53:53.115679	\N	\N	\N
28cd0f86-55f5-436c-b515-2d9f364d366d	9e8f9ead-a2dd-40ef-8ea0-50ad90ab956f	b70fe0df-4f87-4275-8dec-6160f139ffea	\N	Thế hôm nào chúng ta có thể cafe trao đổi thêm nhé. Chắc sẽ hợp tác được nhiều đấy!	TEXT	2026-08-12 11:58:53.115679	\N	\N	\N
610a1656-c71b-49ec-8125-52150361fe12	9e8f9ead-a2dd-40ef-8ea0-50ad90ab956f	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	\N	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	TEXT	2026-08-12 12:03:53.115679	\N	\N	\N
6f165bdf-e9a7-4858-8d50-a034ad3042e3	9eacdc06-eeb1-41ee-a9ee-13c1738114e1	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	\N	Chào bạn, dạo này bạn có đang tìm hiểu gì mới không?	TEXT	2026-08-18 11:43:53.125248	\N	\N	\N
40b768de-3fa8-4a21-9677-7be38280727d	9eacdc06-eeb1-41ee-a9ee-13c1738114e1	d896dfec-6d5f-4708-9d8b-ac7d97174165	\N	Mình đang tập trung nghiên cứu AI và phát triển Backend.	TEXT	2026-08-18 11:48:53.125248	\N	\N	\N
f30425ba-fd1e-4324-a50d-03b63d16f220	9eacdc06-eeb1-41ee-a9ee-13c1738114e1	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	\N	Hay quá, mình cũng đang làm dự án liên quan đến Machine Learning và tối ưu hóa hệ thống.	TEXT	2026-08-18 11:53:53.125248	\N	\N	\N
7258bebb-61fb-48fc-b259-6567a10d59a4	9eacdc06-eeb1-41ee-a9ee-13c1738114e1	d896dfec-6d5f-4708-9d8b-ac7d97174165	\N	Thế hôm nào chúng ta có thể cafe trao đổi thêm nhé. Chắc sẽ hợp tác được nhiều đấy!	TEXT	2026-08-18 11:58:53.125248	\N	\N	\N
a6bee7c8-cb6b-44f7-9914-572eb0780a84	9eacdc06-eeb1-41ee-a9ee-13c1738114e1	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	\N	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	TEXT	2026-08-18 12:03:53.125248	\N	\N	\N
f8142f28-03f1-45bd-bb92-f019072f1f86	d0a7dddc-75f0-4593-86e5-bd3fe9d870e8	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	\N	Chào bạn, dạo này bạn có đang tìm hiểu gì mới không?	TEXT	2026-08-15 11:43:53.135629	\N	\N	\N
95b6a9fb-0612-4ccb-a061-27d2a8b1b854	d0a7dddc-75f0-4593-86e5-bd3fe9d870e8	d367d79b-6cb8-4215-856d-bd6832604eac	\N	Mình đang tập trung nghiên cứu AI và phát triển Backend.	TEXT	2026-08-15 11:48:53.135629	\N	\N	\N
00e155d2-33e2-40af-bfa5-b716cde29c12	d0a7dddc-75f0-4593-86e5-bd3fe9d870e8	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	\N	Hay quá, mình cũng đang làm dự án liên quan đến Machine Learning và tối ưu hóa hệ thống.	TEXT	2026-08-15 11:53:53.135629	\N	\N	\N
dfbb9b5c-ecd9-462c-b998-8fae5a815c0f	d0a7dddc-75f0-4593-86e5-bd3fe9d870e8	d367d79b-6cb8-4215-856d-bd6832604eac	\N	Thế hôm nào chúng ta có thể cafe trao đổi thêm nhé. Chắc sẽ hợp tác được nhiều đấy!	TEXT	2026-08-15 11:58:53.135629	\N	\N	\N
8498ba0b-9097-4a48-975b-c1ea6b81a805	d0a7dddc-75f0-4593-86e5-bd3fe9d870e8	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	\N	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	TEXT	2026-08-15 12:03:53.135629	\N	\N	\N
4c9d1601-3994-4f1a-8caf-a6973b58cf15	7536e586-efc6-47fa-b53a-2ae05b8fe67c	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	\N	Chào bạn, dạo này bạn có đang tìm hiểu gì mới không?	TEXT	2026-08-11 11:43:53.154639	\N	\N	\N
5fa7f635-99d9-4979-9789-d9fa0758a285	7536e586-efc6-47fa-b53a-2ae05b8fe67c	33a2cf07-6177-420e-bfd7-99cdae79b549	\N	Mình đang tập trung nghiên cứu AI và phát triển Backend.	TEXT	2026-08-11 11:48:53.154639	\N	\N	\N
f3eec493-17d5-4137-895e-3bd5d6e3e94f	7536e586-efc6-47fa-b53a-2ae05b8fe67c	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	\N	Hay quá, mình cũng đang làm dự án liên quan đến Machine Learning và tối ưu hóa hệ thống.	TEXT	2026-08-11 11:53:53.154639	\N	\N	\N
690e9953-b607-44ae-b7d9-896b76fe6659	7536e586-efc6-47fa-b53a-2ae05b8fe67c	33a2cf07-6177-420e-bfd7-99cdae79b549	\N	Thế hôm nào chúng ta có thể cafe trao đổi thêm nhé. Chắc sẽ hợp tác được nhiều đấy!	TEXT	2026-08-11 11:58:53.154639	\N	\N	\N
389f9952-21f5-400b-8016-d149f61453da	7536e586-efc6-47fa-b53a-2ae05b8fe67c	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	\N	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	TEXT	2026-08-11 12:03:53.154639	\N	\N	\N
9abd014e-25c6-4aea-b427-4539cb17c273	5b26daff-27a7-49d7-bff6-5345e48c1d30	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	\N	Chào bạn, dạo này bạn có đang tìm hiểu gì mới không?	TEXT	2026-08-11 11:43:53.16637	\N	\N	\N
581a96a8-951f-4232-be0b-6e0d58763865	5b26daff-27a7-49d7-bff6-5345e48c1d30	720e462f-449a-4ec5-85c5-7452c94823ce	\N	Mình đang tập trung nghiên cứu AI và phát triển Backend.	TEXT	2026-08-11 11:48:53.16637	\N	\N	\N
0c7767e4-5f56-484c-a1a5-4eec05393ed5	5b26daff-27a7-49d7-bff6-5345e48c1d30	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	\N	Hay quá, mình cũng đang làm dự án liên quan đến Machine Learning và tối ưu hóa hệ thống.	TEXT	2026-08-11 11:53:53.16637	\N	\N	\N
f2d98705-9d19-4a6e-9cbd-7a9532ec88f6	5b26daff-27a7-49d7-bff6-5345e48c1d30	720e462f-449a-4ec5-85c5-7452c94823ce	\N	Thế hôm nào chúng ta có thể cafe trao đổi thêm nhé. Chắc sẽ hợp tác được nhiều đấy!	TEXT	2026-08-11 11:58:53.16637	\N	\N	\N
e475cc42-fd02-4d9b-b8bf-8b7b53ad3231	5b26daff-27a7-49d7-bff6-5345e48c1d30	a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	\N	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	TEXT	2026-08-11 12:03:53.16637	\N	\N	\N
f4b44374-7027-4449-8a58-8cd4bbda4a18	2bb46ccc-0450-452b-9286-8d46fbaa0aae	b70fe0df-4f87-4275-8dec-6160f139ffea	\N	Chào bạn, dạo này bạn có đang tìm hiểu gì mới không?	TEXT	2026-08-12 11:43:53.176294	\N	\N	\N
24111743-82bb-4364-8b77-43239b7cdadf	2bb46ccc-0450-452b-9286-8d46fbaa0aae	d896dfec-6d5f-4708-9d8b-ac7d97174165	\N	Mình đang tập trung nghiên cứu AI và phát triển Backend.	TEXT	2026-08-12 11:48:53.176294	\N	\N	\N
3d059e7f-ae25-469c-aeea-945f62427820	2bb46ccc-0450-452b-9286-8d46fbaa0aae	b70fe0df-4f87-4275-8dec-6160f139ffea	\N	Hay quá, mình cũng đang làm dự án liên quan đến Machine Learning và tối ưu hóa hệ thống.	TEXT	2026-08-12 11:53:53.176294	\N	\N	\N
c883a277-7ee3-4ebb-9eed-c5f5542668e0	2bb46ccc-0450-452b-9286-8d46fbaa0aae	d896dfec-6d5f-4708-9d8b-ac7d97174165	\N	Thế hôm nào chúng ta có thể cafe trao đổi thêm nhé. Chắc sẽ hợp tác được nhiều đấy!	TEXT	2026-08-12 11:58:53.176294	\N	\N	\N
cd670364-71e8-4cc4-b9ba-23bfe2f382bb	2bb46ccc-0450-452b-9286-8d46fbaa0aae	b70fe0df-4f87-4275-8dec-6160f139ffea	\N	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	TEXT	2026-08-12 12:03:53.176294	\N	\N	\N
837b6c16-7511-4de3-a853-cd9880530585	102a807d-7da1-42de-8802-9fcd154ac23f	b70fe0df-4f87-4275-8dec-6160f139ffea	\N	Chào bạn, dạo này bạn có đang tìm hiểu gì mới không?	TEXT	2026-08-17 11:43:53.189792	\N	\N	\N
b2ba0a32-bf28-4737-b72d-7788da9bc4b9	102a807d-7da1-42de-8802-9fcd154ac23f	d367d79b-6cb8-4215-856d-bd6832604eac	\N	Mình đang tập trung nghiên cứu AI và phát triển Backend.	TEXT	2026-08-17 11:48:53.189792	\N	\N	\N
1b774360-bd42-4121-a67f-7d53be1aef28	102a807d-7da1-42de-8802-9fcd154ac23f	b70fe0df-4f87-4275-8dec-6160f139ffea	\N	Hay quá, mình cũng đang làm dự án liên quan đến Machine Learning và tối ưu hóa hệ thống.	TEXT	2026-08-17 11:53:53.189792	\N	\N	\N
21df11c8-c3b7-4011-b543-a58a39ef8a29	102a807d-7da1-42de-8802-9fcd154ac23f	d367d79b-6cb8-4215-856d-bd6832604eac	\N	Thế hôm nào chúng ta có thể cafe trao đổi thêm nhé. Chắc sẽ hợp tác được nhiều đấy!	TEXT	2026-08-17 11:58:53.189792	\N	\N	\N
ed624a59-be1d-4543-8931-c13dbea33ca0	102a807d-7da1-42de-8802-9fcd154ac23f	b70fe0df-4f87-4275-8dec-6160f139ffea	\N	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	TEXT	2026-08-17 12:03:53.189792	\N	\N	\N
b0d4cf54-cec2-4bba-8612-b3ec11e29439	fa826862-22db-4973-a42e-47fb4a03c604	b70fe0df-4f87-4275-8dec-6160f139ffea	\N	Chào bạn, dạo này bạn có đang tìm hiểu gì mới không?	TEXT	2026-08-19 11:43:53.206727	\N	\N	\N
b571f297-f6b6-400f-8938-520c34995289	fa826862-22db-4973-a42e-47fb4a03c604	33a2cf07-6177-420e-bfd7-99cdae79b549	\N	Mình đang tập trung nghiên cứu AI và phát triển Backend.	TEXT	2026-08-19 11:48:53.206727	\N	\N	\N
c2e32669-4234-4014-b6dc-0a3a7271e7fb	fa826862-22db-4973-a42e-47fb4a03c604	b70fe0df-4f87-4275-8dec-6160f139ffea	\N	Hay quá, mình cũng đang làm dự án liên quan đến Machine Learning và tối ưu hóa hệ thống.	TEXT	2026-08-19 11:53:53.206727	\N	\N	\N
15f25855-d5d8-4ea6-ad03-e05f096593a8	fa826862-22db-4973-a42e-47fb4a03c604	33a2cf07-6177-420e-bfd7-99cdae79b549	\N	Thế hôm nào chúng ta có thể cafe trao đổi thêm nhé. Chắc sẽ hợp tác được nhiều đấy!	TEXT	2026-08-19 11:58:53.206727	\N	\N	\N
042d5e64-31ea-4bbf-a380-643ada1218a4	fa826862-22db-4973-a42e-47fb4a03c604	b70fe0df-4f87-4275-8dec-6160f139ffea	\N	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	TEXT	2026-08-19 12:03:53.206727	\N	\N	\N
a44a4121-b210-4375-a1fd-7247bb887c43	8992e301-301b-4565-bdcb-31efef059d12	b70fe0df-4f87-4275-8dec-6160f139ffea	\N	Chào bạn, dạo này bạn có đang tìm hiểu gì mới không?	TEXT	2026-08-20 11:43:53.246782	\N	\N	\N
dd071e72-3c9b-45b0-9201-c85ac64e201a	8992e301-301b-4565-bdcb-31efef059d12	720e462f-449a-4ec5-85c5-7452c94823ce	\N	Mình đang tập trung nghiên cứu AI và phát triển Backend.	TEXT	2026-08-20 11:48:53.246782	\N	\N	\N
0e5b053d-54f1-42b3-8d38-c1639b6cc846	8992e301-301b-4565-bdcb-31efef059d12	b70fe0df-4f87-4275-8dec-6160f139ffea	\N	Hay quá, mình cũng đang làm dự án liên quan đến Machine Learning và tối ưu hóa hệ thống.	TEXT	2026-08-20 11:53:53.246782	\N	\N	\N
1f047efe-bae3-4e56-a910-51b3fc9b7ede	8992e301-301b-4565-bdcb-31efef059d12	720e462f-449a-4ec5-85c5-7452c94823ce	\N	Thế hôm nào chúng ta có thể cafe trao đổi thêm nhé. Chắc sẽ hợp tác được nhiều đấy!	TEXT	2026-08-20 11:58:53.246782	\N	\N	\N
0b0ea90e-3458-40d5-bd77-264bf1e31964	8992e301-301b-4565-bdcb-31efef059d12	b70fe0df-4f87-4275-8dec-6160f139ffea	\N	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	TEXT	2026-08-20 12:03:53.246782	\N	\N	\N
fda021eb-e7f6-4d28-8b23-f2338798d5dc	381c7079-39d6-41fa-844f-f68c4f280012	d896dfec-6d5f-4708-9d8b-ac7d97174165	\N	Chào bạn, dạo này bạn có đang tìm hiểu gì mới không?	TEXT	2026-08-11 11:43:53.261495	\N	\N	\N
8f2fad43-a890-4920-bd96-52ba7b8c176a	381c7079-39d6-41fa-844f-f68c4f280012	d367d79b-6cb8-4215-856d-bd6832604eac	\N	Mình đang tập trung nghiên cứu AI và phát triển Backend.	TEXT	2026-08-11 11:48:53.261495	\N	\N	\N
abcf55d6-a467-4a79-8622-7aed958edf3a	381c7079-39d6-41fa-844f-f68c4f280012	d896dfec-6d5f-4708-9d8b-ac7d97174165	\N	Hay quá, mình cũng đang làm dự án liên quan đến Machine Learning và tối ưu hóa hệ thống.	TEXT	2026-08-11 11:53:53.261495	\N	\N	\N
09756894-0cfd-4e77-bcb0-81d25b14fafd	381c7079-39d6-41fa-844f-f68c4f280012	d367d79b-6cb8-4215-856d-bd6832604eac	\N	Thế hôm nào chúng ta có thể cafe trao đổi thêm nhé. Chắc sẽ hợp tác được nhiều đấy!	TEXT	2026-08-11 11:58:53.261495	\N	\N	\N
f82fe06b-a1f5-41fd-924d-f3d0da4c57af	381c7079-39d6-41fa-844f-f68c4f280012	d896dfec-6d5f-4708-9d8b-ac7d97174165	\N	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	TEXT	2026-08-11 12:03:53.261495	\N	\N	\N
4eb7d301-ac60-4919-b369-84c5d2fbb4f3	cebf275a-4846-4d7b-9d83-9de5d4f4b367	d896dfec-6d5f-4708-9d8b-ac7d97174165	\N	Chào bạn, dạo này bạn có đang tìm hiểu gì mới không?	TEXT	2026-08-19 11:43:53.273512	\N	\N	\N
5907d4c8-49db-477f-838f-ae74fbad28c2	cebf275a-4846-4d7b-9d83-9de5d4f4b367	33a2cf07-6177-420e-bfd7-99cdae79b549	\N	Mình đang tập trung nghiên cứu AI và phát triển Backend.	TEXT	2026-08-19 11:48:53.273512	\N	\N	\N
d4093781-e51f-4956-92b2-cb74d9a12946	cebf275a-4846-4d7b-9d83-9de5d4f4b367	d896dfec-6d5f-4708-9d8b-ac7d97174165	\N	Hay quá, mình cũng đang làm dự án liên quan đến Machine Learning và tối ưu hóa hệ thống.	TEXT	2026-08-19 11:53:53.273512	\N	\N	\N
78779c1c-4dfb-4ee8-85bd-6c4b38f4d2c4	cebf275a-4846-4d7b-9d83-9de5d4f4b367	33a2cf07-6177-420e-bfd7-99cdae79b549	\N	Thế hôm nào chúng ta có thể cafe trao đổi thêm nhé. Chắc sẽ hợp tác được nhiều đấy!	TEXT	2026-08-19 11:58:53.273512	\N	\N	\N
b954cdd9-4d1e-4897-8879-81cf67a41e48	cebf275a-4846-4d7b-9d83-9de5d4f4b367	d896dfec-6d5f-4708-9d8b-ac7d97174165	\N	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	TEXT	2026-08-19 12:03:53.273512	\N	\N	\N
efe6e6b6-a8f2-4304-aacb-d50479454f15	6bb8b995-f8eb-4919-8cb4-20904f19e9db	d896dfec-6d5f-4708-9d8b-ac7d97174165	\N	Chào bạn, dạo này bạn có đang tìm hiểu gì mới không?	TEXT	2026-08-16 11:43:53.284881	\N	\N	\N
4a56223f-ce40-46d0-bc03-e0ba32906cae	6bb8b995-f8eb-4919-8cb4-20904f19e9db	720e462f-449a-4ec5-85c5-7452c94823ce	\N	Mình đang tập trung nghiên cứu AI và phát triển Backend.	TEXT	2026-08-16 11:48:53.284881	\N	\N	\N
8148efe8-b280-4eba-9610-ad1357710223	6bb8b995-f8eb-4919-8cb4-20904f19e9db	d896dfec-6d5f-4708-9d8b-ac7d97174165	\N	Hay quá, mình cũng đang làm dự án liên quan đến Machine Learning và tối ưu hóa hệ thống.	TEXT	2026-08-16 11:53:53.284881	\N	\N	\N
0de6c288-8c6e-468b-b8e5-265f1a17dae5	6bb8b995-f8eb-4919-8cb4-20904f19e9db	720e462f-449a-4ec5-85c5-7452c94823ce	\N	Thế hôm nào chúng ta có thể cafe trao đổi thêm nhé. Chắc sẽ hợp tác được nhiều đấy!	TEXT	2026-08-16 11:58:53.284881	\N	\N	\N
35d2eb5e-c0c1-4ca1-908d-405472ada139	6bb8b995-f8eb-4919-8cb4-20904f19e9db	d896dfec-6d5f-4708-9d8b-ac7d97174165	\N	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	TEXT	2026-08-16 12:03:53.284881	\N	\N	\N
cc4baeed-d118-4653-b58f-517a82e261f3	4c4dde50-7579-4216-b174-f3fec9ecc8b8	d367d79b-6cb8-4215-856d-bd6832604eac	\N	Chào bạn, dạo này bạn có đang tìm hiểu gì mới không?	TEXT	2026-08-19 11:43:53.295356	\N	\N	\N
b7c78888-60d0-47a2-987a-1a2d9c63f5c2	4c4dde50-7579-4216-b174-f3fec9ecc8b8	33a2cf07-6177-420e-bfd7-99cdae79b549	\N	Mình đang tập trung nghiên cứu AI và phát triển Backend.	TEXT	2026-08-19 11:48:53.295356	\N	\N	\N
06dfb865-7187-4197-8c1c-cbd75970c49e	4c4dde50-7579-4216-b174-f3fec9ecc8b8	d367d79b-6cb8-4215-856d-bd6832604eac	\N	Hay quá, mình cũng đang làm dự án liên quan đến Machine Learning và tối ưu hóa hệ thống.	TEXT	2026-08-19 11:53:53.295356	\N	\N	\N
4c970745-dddc-4083-965c-e550234ce43b	4c4dde50-7579-4216-b174-f3fec9ecc8b8	33a2cf07-6177-420e-bfd7-99cdae79b549	\N	Thế hôm nào chúng ta có thể cafe trao đổi thêm nhé. Chắc sẽ hợp tác được nhiều đấy!	TEXT	2026-08-19 11:58:53.295356	\N	\N	\N
447c8bfa-2463-4a45-8179-9fd570c087ba	4c4dde50-7579-4216-b174-f3fec9ecc8b8	d367d79b-6cb8-4215-856d-bd6832604eac	\N	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	TEXT	2026-08-19 12:03:53.295356	\N	\N	\N
0838994a-3be2-4e15-a5a0-12b66839714a	79882a03-770f-49f8-8ec6-11d00b9b34b5	d367d79b-6cb8-4215-856d-bd6832604eac	\N	Chào bạn, dạo này bạn có đang tìm hiểu gì mới không?	TEXT	2026-08-20 11:43:53.307045	\N	\N	\N
dac87871-bf00-4478-9955-76a97039f987	79882a03-770f-49f8-8ec6-11d00b9b34b5	720e462f-449a-4ec5-85c5-7452c94823ce	\N	Mình đang tập trung nghiên cứu AI và phát triển Backend.	TEXT	2026-08-20 11:48:53.307045	\N	\N	\N
030ab506-23a6-4515-be2c-c7be4e9b7b84	79882a03-770f-49f8-8ec6-11d00b9b34b5	d367d79b-6cb8-4215-856d-bd6832604eac	\N	Hay quá, mình cũng đang làm dự án liên quan đến Machine Learning và tối ưu hóa hệ thống.	TEXT	2026-08-20 11:53:53.307045	\N	\N	\N
986c2620-6ba3-424e-a335-5176dc258c77	79882a03-770f-49f8-8ec6-11d00b9b34b5	720e462f-449a-4ec5-85c5-7452c94823ce	\N	Thế hôm nào chúng ta có thể cafe trao đổi thêm nhé. Chắc sẽ hợp tác được nhiều đấy!	TEXT	2026-08-20 11:58:53.307045	\N	\N	\N
a233638d-7b63-4ec0-ab7b-c9ad899f6169	79882a03-770f-49f8-8ec6-11d00b9b34b5	d367d79b-6cb8-4215-856d-bd6832604eac	\N	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	TEXT	2026-08-20 12:03:53.307045	\N	\N	\N
49d14e8f-a181-4644-8341-544cb3d99dfe	211e7ab3-1d05-4227-bb01-cd27cd655691	33a2cf07-6177-420e-bfd7-99cdae79b549	\N	Chào bạn, dạo này bạn có đang tìm hiểu gì mới không?	TEXT	2026-08-19 11:43:53.319124	\N	\N	\N
809ea3d9-6051-4b62-9fbf-da9ed502344d	211e7ab3-1d05-4227-bb01-cd27cd655691	720e462f-449a-4ec5-85c5-7452c94823ce	\N	Mình đang tập trung nghiên cứu AI và phát triển Backend.	TEXT	2026-08-19 11:48:53.319124	\N	\N	\N
ba64f59c-ec57-4103-b806-a2304efb1c4b	211e7ab3-1d05-4227-bb01-cd27cd655691	33a2cf07-6177-420e-bfd7-99cdae79b549	\N	Hay quá, mình cũng đang làm dự án liên quan đến Machine Learning và tối ưu hóa hệ thống.	TEXT	2026-08-19 11:53:53.319124	\N	\N	\N
9aba32a8-bc9b-42b3-8bf5-b0ee7dba8fb2	211e7ab3-1d05-4227-bb01-cd27cd655691	720e462f-449a-4ec5-85c5-7452c94823ce	\N	Thế hôm nào chúng ta có thể cafe trao đổi thêm nhé. Chắc sẽ hợp tác được nhiều đấy!	TEXT	2026-08-19 11:58:53.319124	\N	\N	\N
b1b38390-3176-4c92-aa4c-79474268a771	211e7ab3-1d05-4227-bb01-cd27cd655691	33a2cf07-6177-420e-bfd7-99cdae79b549	\N	Tuyệt vời, cuối tuần này mình rảnh. Sẽ nhắn lại thời gian cụ thể nhé.	TEXT	2026-08-19 12:03:53.319124	\N	\N	\N
\.


--
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.notifications (id, user_id, type, title, content, status, created_at) FROM stdin;
1bc9925d-0135-4242-a46d-ed134bea6918	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	CONNECTION_RECOMMENDATION	Có gợi ý kết nối mới	Hệ thống đã tìm thấy 4 cơ hội kết nối tiềm năng cho bạn. Nhấn để xem chi tiết.	UNREAD	2026-08-21 13:21:26.882522
\.


--
-- Data for Name: outbox_events; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.outbox_events (id, event_type, payload, status, created_at) FROM stdin;
220e0e8d-4c8a-4837-88a5-70a7509ecf88	OPEN_CHAT	{"user_id": "fcc16f65-7ff2-4320-ac57-c16a11c162a2", "conversation_id": "cc6ab180-c6cf-4d9d-b0d1-d7f6c15e8b6f"}	PROCESSED	2026-08-20 17:14:00.568261
f5e47125-04cd-4c54-a97b-168724a0dd4b	NEW_MESSAGE	{"user_id": "fcc16f65-7ff2-4320-ac57-c16a11c162a2", "conversation_id": "cc6ab180-c6cf-4d9d-b0d1-d7f6c15e8b6f", "message_id": "7ab86c6f-bd19-41cc-bf13-858e394c005e", "content": "Hello b\\u1ea1n, b\\u00ean m\\u00ecnh \\u0111ang tri\\u1ec3n khai v\\u1ec1 ch\\u01b0\\u01a1ng tr\\u00ecnh AI th\\u1ef1c chi\\u1ebfn \\u1ea5y kh\\u00f4ng bi\\u1ebft b\\u1ea1n c\\u00f3 nhu c\\u1ea7u t\\u01b0 v\\u1ea5n v\\u1ec1 kh\\u00f3a h\\u1ecdc AI th\\u1ef1c chi\\u1ebfn c\\u1ee7a Vin kh\\u00f4ng \\u1ea1 !"}	PROCESSED	2026-08-20 17:39:37.67092
a5df340b-8dd4-48f8-be99-c9c0734d447f	MEMORY_UPDATED	{"user_id": "fcc16f65-7ff2-4320-ac57-c16a11c162a2", "conversation_id": "cc6ab180-c6cf-4d9d-b0d1-d7f6c15e8b6f"}	PROCESSED	2026-08-20 17:39:49.595926
c164a9ff-99f9-432f-98fc-83a808a058f7	MEMORY_UPDATED	{"user_id": "adea9584-28f8-409c-82e5-cedc07e7d6cd", "conversation_id": "cc6ab180-c6cf-4d9d-b0d1-d7f6c15e8b6f"}	PROCESSED	2026-08-20 17:39:38.273605
8a91945a-0fe5-4d48-9c6c-9cc80905fb87	NEW_MESSAGE	{"user_id": "adea9584-28f8-409c-82e5-cedc07e7d6cd", "conversation_id": "cc6ab180-c6cf-4d9d-b0d1-d7f6c15e8b6f", "message_id": "9c06062d-1781-49e7-b2b4-3b45d4ce06a7", "content": "Minh c\\u1ea3m \\u01a1n, b\\u00ean b\\u1ea1n \\u0111ang tri\\u1ec3n khai ch\\u01b0\\u01a1ng tr\\u00ecnh nh\\u01b0 n\\u00e0o nh\\u1ec9 !"}	PROCESSED	2026-08-20 17:41:40.983104
dc8f790e-2b5c-4f1e-8430-a12db39bca77	NEW_MESSAGE	{"user_id": "adea9584-28f8-409c-82e5-cedc07e7d6cd", "conversation_id": "cc6ab180-c6cf-4d9d-b0d1-d7f6c15e8b6f", "message_id": "d34145fa-92dd-4281-afb1-498333768d8c", "content": "Hi\\u1ec7n t\\u1ea1i m\\u00ecnh l\\u00e0 fullstack v\\u1ec1 m\\u1ea3ng web, c\\u00f3 kinh nghi\\u1ec7m l\\u00e0m nhi\\u1ec1u trong c\\u00e1c t\\u1eadp \\u0111o\\u00e0n l\\u1edbn, kh\\u00f4ng bi\\u1ebft l\\u00e0 tham gia ch\\u01b0\\u01a1ng tr\\u00ecnh c\\u00f3 \\u1ed5n kh\\u00f4ng"}	PROCESSED	2026-08-20 17:41:40.983754
c9ec177d-5a65-4797-8335-05af915e1cc6	NEW_MESSAGE	{"user_id": "adea9584-28f8-409c-82e5-cedc07e7d6cd", "conversation_id": "cc6ab180-c6cf-4d9d-b0d1-d7f6c15e8b6f", "message_id": "78968d18-221e-4095-a62f-5888fedf967b", "content": "C\\u1ea3m \\u01a1n Minh Anh \\u0111\\u00e3 chia s\\u1ebb th\\u00f4ng tin. M\\u00ecnh r\\u1ea5t quan t\\u00e2m \\u0111\\u1ebfn kh\\u00f3a h\\u1ecdc AI th\\u1ef1c chi\\u1ebfn c\\u1ee7a Vin, b\\u1ea1n c\\u00f3 th\\u1ec3 cung c\\u1ea5p th\\u00eam chi ti\\u1ebft v\\u1ec1 n\\u1ed9i dung v\\u00e0 th\\u1eddi gian kh\\u00f3a h\\u1ecdc \\u0111\\u01b0\\u1ee3c kh\\u00f4ng?"}	PROCESSED	2026-08-20 17:41:53.52567
ee613e7d-177a-4be3-9825-0e3666c961fd	MEMORY_UPDATED	{"user_id": "fcc16f65-7ff2-4320-ac57-c16a11c162a2", "conversation_id": "cc6ab180-c6cf-4d9d-b0d1-d7f6c15e8b6f"}	PROCESSED	2026-08-20 17:42:23.723595
0156ca67-2c3f-4ba2-a169-ef6958571f65	MEMORY_UPDATED	{"user_id": "adea9584-28f8-409c-82e5-cedc07e7d6cd", "conversation_id": "cc6ab180-c6cf-4d9d-b0d1-d7f6c15e8b6f"}	PROCESSED	2026-08-20 17:43:20.27077
ddaf3d5c-b606-4870-b3eb-74cc081ae417	NEW_MESSAGE	{"user_id": "fcc16f65-7ff2-4320-ac57-c16a11c162a2", "conversation_id": "cc6ab180-c6cf-4d9d-b0d1-d7f6c15e8b6f", "message_id": "f0a99220-0489-4282-bd7f-16ec1ba98c6c", "content": "Kh\\u00f3a h\\u1ecdc AI th\\u1ef1c chi\\u1ebfn c\\u1ee7a Vin s\\u1ebd bao g\\u1ed3m c\\u00e1c n\\u1ed9i dung nh\\u01b0 l\\u1eadp tr\\u00ecnh AI, x\\u1eed l\\u00fd d\\u1eef li\\u1ec7u v\\u00e0 \\u1ee9ng d\\u1ee5ng th\\u1ef1c ti\\u1ec5n trong doanh nghi\\u1ec7p. Th\\u1eddi gian h\\u1ecdc k\\u00e9o d\\u00e0i kho\\u1ea3ng 8 tu\\u1ea7n v\\u1edbi c\\u00e1c bu\\u1ed5i h\\u1ecdc v\\u00e0o cu\\u1ed1i tu\\u1ea7n. M\\u00ecnh s\\u1ebd g\\u1eedi th\\u00eam th\\u00f4ng tin chi ti\\u1ebft qua email nh\\u00e9!"}	PROCESSED	2026-08-21 06:09:15.485594
016818f5-d75d-4d70-8ab5-ca46ae1f0589	MEMORY_UPDATED	{"user_id": "adea9584-28f8-409c-82e5-cedc07e7d6cd", "conversation_id": "cc6ab180-c6cf-4d9d-b0d1-d7f6c15e8b6f"}	PROCESSED	2026-08-21 06:09:15.78098
a797185b-908f-46d5-a4fa-b5770c8796b8	MEMORY_UPDATED	{"user_id": "fcc16f65-7ff2-4320-ac57-c16a11c162a2", "conversation_id": "cc6ab180-c6cf-4d9d-b0d1-d7f6c15e8b6f"}	PROCESSED	2026-08-21 06:09:26.64252
8ed46b46-5d66-4d97-b4fa-6c930a2a7931	MEMORY_UPDATED	{"user_id": "a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59", "conversation_id": "a78023ce-b676-4477-8292-3391ab5bfaca"}	PROCESSED	2026-08-21 13:20:04.151158
3f88fd61-bce8-4517-949b-3c39fb56fbf3	MEMORY_UPDATED	{"user_id": "a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59", "conversation_id": "15940406-00d7-4c70-aa78-110988b19fa0"}	PROCESSED	2026-08-21 13:20:23.774892
cfdcd1d5-0c73-4476-8625-d6db04ea7f53	MEMORY_UPDATED	{"user_id": "a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59", "conversation_id": "b2a4cf94-be68-4f29-ba2f-18127d1b6059"}	PROCESSED	2026-08-21 13:56:15.454679
ecc97e1a-0bec-40fa-a744-c7d52e90069d	MEMORY_UPDATED	{"user_id": "a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59", "conversation_id": "b2a4cf94-be68-4f29-ba2f-18127d1b6059"}	PROCESSED	2026-08-21 13:56:29.262076
7519300e-62b9-4bad-ad68-bd8a4abb3fbc	MEMORY_UPDATED	{"user_id": "a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59", "conversation_id": "b2a4cf94-be68-4f29-ba2f-18127d1b6059"}	PROCESSED	2026-08-22 15:52:58.691436
65206634-4bb8-49f0-a887-bd40d3553381	MEMORY_UPDATED	{"user_id": "a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59", "conversation_id": "b2a4cf94-be68-4f29-ba2f-18127d1b6059"}	PROCESSED	2026-08-22 16:52:05.724074
90297cfe-9168-455b-90d1-39b17744c15d	MEMORY_UPDATED	{"user_id": "a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59", "conversation_id": "b2a4cf94-be68-4f29-ba2f-18127d1b6059"}	PROCESSED	2026-08-22 17:19:10.079293
\.


--
-- Data for Name: recommendations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.recommendations (id, owner_user_id, target_user_id, contact_id, target_contact_id, type, reason, priority, confidence, status, created_at, expires_at) FROM stdin;
bb8b70d5-adcb-4476-8c45-5b95c8c1d92e	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	d896dfec-6d5f-4708-9d8b-ac7d97174165	\N	\N	CONNECTION	Bạn nên kết nối với Bùi Khánh Linh (Frontend Developer tại Tech Innovators VN, TP. HCM, Việt Nam) vì cả hai bạn đều đang tìm kiếm cơ hội Networking, Mentorship và Collaboration, trong khi Bùi Khánh Linh có kinh nghiệm sâu về Docker và AWS mà có thể bổ trợ cho kỹ năng Python của bạn. Cả hai bạn đều quan tâm đến AI, điều này tạo cơ hội thảo luận và hợp tác trong các dự án liên quan.	HIGH	0.88	PENDING	2026-08-21 13:21:11.983523	\N
e9cf1f2c-78b2-460d-9f33-ac5cbbf16695	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	720e462f-449a-4ec5-85c5-7452c94823ce	\N	\N	CONNECTION	Bạn nên kết nối với Nguyễn Hà Phương (Frontend Developer tại Tech Innovators VN, TP. HCM, Việt Nam) vì cả hai bạn đều đang tìm kiếm cơ hội networking và mentorship. Nguyễn Hà Phương có kinh nghiệm về Machine Learning và AWS, điều này có thể bổ sung cho kiến thức và kỹ năng của bạn trong thiết kế UX/UI với các giải pháp thực tiễn. Cả hai bạn đều có chung sự quan tâm đến công nghệ mới và đổi mới sáng tạo.	HIGH	0.85	PENDING	2026-08-21 13:21:26.866378	\N
d31524e8-faf9-494b-9550-25d817f1c4b0	cfc3c138-db1a-4b67-ace1-0e1b21d42938	720e462f-449a-4ec5-85c5-7452c94823ce	\N	\N	CONNECTION	Bạn nên kết nối với Nguyễn Hà Phương (Frontend Developer tại Tech Innovators VN, TP. HCM, Việt Nam) vì cả hai bạn đều đang tìm kiếm cơ hội kết nối và hợp tác, trong khi Nguyễn Hà Phương có kinh nghiệm về Machine Learning, có thể bổ sung cho việc phát triển dự án AI của bạn. Cả hai bạn đều quan tâm đến việc mở rộng mạng lưới nghề nghiệp.	HIGH	0.85	PENDING	2026-08-22 14:43:50.721705	\N
7c34dc5d-1db9-40d0-81b8-5d59ebfcd94a	cfc3c138-db1a-4b67-ace1-0e1b21d42938	33a2cf07-6177-420e-bfd7-99cdae79b549	\N	\N	CONNECTION	Bạn nên kết nối với Đỗ Tuấn Kiệt (Frontend Developer tại Tech Innovators VN, TP. HCM, Việt Nam) vì bạn đang tìm kiếm cơ hội hợp tác và mentoring trong khi Đỗ Tuấn Kiệt có thể chia sẻ kinh nghiệm phát triển frontend, điều này có thể bổ sung cho các dự án AI mà bạn quan tâm. Cả hai bạn đều quan tâm đến việc mở rộng mạng lưới chuyên môn.	HIGH	0.8	PENDING	2026-08-22 14:43:56.520478	\N
4bf9eb63-3b8f-48c2-8178-78c865b878c9	33a2cf07-6177-420e-bfd7-99cdae79b549	fa63627e-ae02-4b51-bea6-8c7af20501ad	\N	\N	CONNECTION	Bạn nên kết nối với Trần Quốc Huy (DevOps Engineer tại Tech Innovators VN, Hà Nội, Việt Nam) vì bạn đang tìm kiếm cơ hội hợp tác và mentorship trong khi Trần Quốc Huy có kinh nghiệm sâu về AWS và React, có thể hỗ trợ bạn trong các dự án phát triển ứng dụng. Cả hai bạn đều quan tâm đến gaming, điều này có thể tạo ra nền tảng tốt để kết nối.	HIGH	0.88	PENDING	2026-08-22 14:44:37.427717	\N
8c96fee1-6cf8-4a0e-a9c3-5ab550f39d8a	33a2cf07-6177-420e-bfd7-99cdae79b549	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	\N	\N	CONNECTION	Bạn nên kết nối với Nguyễn Minh Anh (UI/UX Designer tại Tech Innovators VN, TP. HCM, Việt Nam) vì bạn đang tìm kiếm cơ hội hợp tác và mentorship trong khi Nguyễn Minh Anh có kinh nghiệm sâu về thiết kế UI/UX và cũng tìm kiếm sự kết nối tương tự. Cả hai bạn đều quan tâm đến việc đọc sách.	HIGH	0.88	PENDING	2026-08-22 14:44:47.255094	\N
ab7c4ea2-1f0d-434a-b042-b090f547aa57	33a2cf07-6177-420e-bfd7-99cdae79b549	cfc3c138-db1a-4b67-ace1-0e1b21d42938	\N	\N	CONNECTION	Bạn nên kết nối với Lê Hoàng Nam (Data Scientist tại Tech Innovators VN, Hà Nội, Việt Nam) vì bạn đang tìm kiếm cơ hội hợp tác và mentorship trong khi Lê Hoàng Nam có kinh nghiệm sâu về AWS và AI, điều này có thể bổ trợ cho công việc của bạn. Cả hai bạn đều quan tâm đến Networking.	MEDIUM	0.75	PENDING	2026-08-22 14:44:47.261528	\N
3ccb57c8-1d8c-4982-9f45-d7ea0bfa2441	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	33a2cf07-6177-420e-bfd7-99cdae79b549	\N	\N	CONNECTION	Bạn nên kết nối với Đỗ Tuấn Kiệt (Frontend Developer tại Tech Innovators VN, TP. HCM, Việt Nam) vì bạn đang tìm kiếm cơ hội hợp tác và mentorship trong khi Đỗ Tuấn Kiệt có kinh nghiệm sâu về Frontend Development và sẵn sàng chia sẻ kinh nghiệm. Cả hai bạn đều quan tâm đến việc đọc sách và có chung môi trường làm việc tại Tech Innovators VN.	HIGH	0.88	REJECTED	2026-08-21 13:21:26.860459	\N
48bce8b7-b0ae-4e12-8ff6-45037e10bba2	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	d367d79b-6cb8-4215-856d-bd6832604eac	\N	\N	CONNECTION	Bạn nên kết nối với Hoàng Minh Quân (Mobile Developer tại Tech Innovators VN, TP. HCM, Việt Nam) vì bạn đang tìm kiếm cơ hội kết nối và hợp tác trong khi Hoàng Minh Quân có kinh nghiệm sâu về Machine Learning, điều này có thể bổ sung cho các dự án bạn đang làm. Cả hai bạn đều quan tâm đến AI.	HIGH	0.88	REJECTED	2026-08-21 13:21:26.852313	\N
4e6da833-6b12-4963-84c6-344212ec4bb3	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	33a2cf07-6177-420e-bfd7-99cdae79b549	\N	\N	CONNECTION	Bạn nên kết nối với Đỗ Tuấn Kiệt (Frontend Developer tại Tech Innovators VN, TP. HCM, Việt Nam) vì bạn đang tìm kiếm cơ hội hợp tác và mentorship trong khi Đỗ Tuấn Kiệt có kinh nghiệm sâu về React và Go. Cả hai bạn đều quan tâm đến việc đọc sách, điều này có thể tạo cơ hội để trao đổi ý tưởng và kiến thức.	HIGH	0.88	PENDING	2026-08-22 17:05:26.869572	\N
8dd25a01-a4cc-4b32-a000-93d6a643ad2d	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	d367d79b-6cb8-4215-856d-bd6832604eac	\N	\N	CONNECTION	Bạn nên kết nối với Hoàng Minh Quân (Mobile Developer tại Tech Innovators VN, TP. HCM, Việt Nam) vì bạn đang tìm kiếm cơ hội hợp tác và mentorship trong khi Hoàng Minh Quân có kinh nghiệm sâu về Machine Learning và Go. Cả hai bạn đều quan tâm đến AI, điều này sẽ tạo cơ hội cho việc trao đổi ý tưởng và phát triển kỹ năng lẫn nhau.	HIGH	0.88	PENDING	2026-08-22 17:05:33.372629	\N
\.


--
-- Data for Name: search_history; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.search_history (id, user_id, query, results, result_count, created_at) FROM stdin;
\.


--
-- Data for Name: settings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.settings (user_id, auto_tag, auto_memory, theme, language, notification, ai_enabled, ai_memory_window, ai_read_profile, ai_memory_refresh_interval) FROM stdin;
33a2cf07-6177-420e-bfd7-99cdae79b549	t	t	light	vi	t	t	7 days	t	daily
a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	t	t	system	vi	t	t	unlimited	t	daily
\.


--
-- Data for Name: tags; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tags (id, name, category, is_active, created_at, updated_at, user_id) FROM stdin;
10a54bc5-76cd-4d8a-840e-71a6b4f06aa1	Frontend Developer	\N	f	2026-08-22 17:20:17.713528	2026-08-22 17:20:28.782505	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59
6e97ee6a-88cf-4d5b-85ee-82ca0b9ce27a	Công Nghệ	\N	f	2026-08-22 17:20:15.168724	2026-08-22 17:34:56.385126	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59
63c03445-9bce-4609-a03f-227ca0f769be	Trí Tuệ Nhân Tạo	\N	f	2026-08-22 17:20:37.162401	2026-08-22 17:34:57.203174	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59
fd014a93-c69f-45ff-ba1b-fd7151f18b46	Đối Tác	\N	f	2026-08-22 17:20:42.064122	2026-08-22 17:34:57.998833	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59
79c3bf0f-a6d3-4ad3-8e12-9641c8066a03	Bạn Bè	\N	t	2026-08-22 17:20:37.150564	2026-08-22 17:35:15.268173	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59
e95bcbf7-0260-43c5-90be-00a787c69717	Gia Đình		t	2026-08-22 17:35:19.457811	2026-08-22 17:35:19.457811	a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59
\.


--
-- Data for Name: user_profiles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_profiles (user_id, profession, company, location, skills, interests, looking_for, offering, bio, created_at, updated_at) FROM stdin;
fa63627e-ae02-4b51-bea6-8c7af20501ad	DevOps Engineer	Tech Innovators VN	Hà Nội, Việt Nam	["AWS", "React", "Figma"]	["Gaming", "AI", "Traveling"]	["Networking", "Mentorship", "Collaboration"]	["Experience", "Code Review"]	Xin chào, tôi là Trần Quốc Huy. Rất vui được kết nối!	2026-08-21 11:43:52.769394	2026-08-21 11:43:52.769394
cfc3c138-db1a-4b67-ace1-0e1b21d42938	Data Scientist	Tech Innovators VN	Hà Nội, Việt Nam	["AWS", "Node.js", "Docker", "Java"]	["Traveling", "AI"]	["Networking", "Mentorship", "Collaboration"]	["Experience", "Code Review"]	Xin chào, tôi là Lê Hoàng Nam. Rất vui được kết nối!	2026-08-21 11:43:52.769394	2026-08-21 11:43:52.769394
8fcd1ec3-980c-422e-9956-aa675289b2b5	Product Manager	Tech Innovators VN	Hà Nội, Việt Nam	["Node.js", "Figma", "SQL", "Machine Learning"]	["Music", "Startups", "Blockchain"]	["Networking", "Mentorship", "Collaboration"]	["Experience", "Code Review"]	Xin chào, tôi là Phạm Đức Anh. Rất vui được kết nối!	2026-08-21 11:43:52.769394	2026-08-21 11:43:52.769394
a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	Mobile Developer	Tech Innovators VN	Hà Nội, Việt Nam	["Docker", "Go"]	["Gaming", "Blockchain"]	["Networking", "Mentorship", "Collaboration"]	["Experience", "Code Review"]	Xin chào, tôi là Vũ Thành Đạt. Rất vui được kết nối!	2026-08-21 11:43:52.769394	2026-08-21 11:43:52.769394
b70fe0df-4f87-4275-8dec-6160f139ffea	Frontend Developer	Tech Innovators VN	TP. HCM, Việt Nam	["Machine Learning", "Docker", "AWS", "Figma"]	["Startups", "Blockchain"]	["Networking", "Mentorship", "Collaboration"]	["Experience", "Code Review"]	Xin chào, tôi là Đặng Ngọc Mai. Rất vui được kết nối!	2026-08-21 11:43:52.769394	2026-08-21 11:43:52.769394
d896dfec-6d5f-4708-9d8b-ac7d97174165	Frontend Developer	Tech Innovators VN	TP. HCM, Việt Nam	["Docker", "Python", "AWS"]	["Blockchain", "Photography"]	["Networking", "Mentorship", "Collaboration"]	["Experience", "Code Review"]	Xin chào, tôi là Bùi Khánh Linh. Rất vui được kết nối!	2026-08-21 11:43:52.769394	2026-08-21 11:43:52.769394
d367d79b-6cb8-4215-856d-bd6832604eac	Mobile Developer	Tech Innovators VN	TP. HCM, Việt Nam	["SQL", "C++", "Machine Learning", "Go"]	["Traveling", "AI", "Gaming"]	["Networking", "Mentorship", "Collaboration"]	["Experience", "Code Review"]	Xin chào, tôi là Hoàng Minh Quân. Rất vui được kết nối!	2026-08-21 11:43:52.769394	2026-08-21 11:43:52.769394
33a2cf07-6177-420e-bfd7-99cdae79b549	Frontend Developer	Tech Innovators VN	TP. HCM, Việt Nam	["Go", "React"]	["Reading", "Gaming", "Blockchain"]	["Networking", "Mentorship", "Collaboration"]	["Experience", "Code Review"]	Xin chào, tôi là Đỗ Tuấn Kiệt. Rất vui được kết nối!	2026-08-21 11:43:52.769394	2026-08-21 11:43:52.769394
720e462f-449a-4ec5-85c5-7452c94823ce	Frontend Developer	Tech Innovators VN	TP. HCM, Việt Nam	["Machine Learning", "AWS", "Node.js"]	["Blockchain", "Startups"]	["Networking", "Mentorship", "Collaboration"]	["Experience", "Code Review"]	Xin chào, tôi là Nguyễn Hà Phương. Rất vui được kết nối!	2026-08-21 11:43:52.769394	2026-08-21 11:43:52.769394
a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	UI/UX Designer	Tech Innovators VN	TP. HCM, Việt Nam	["Python", "Figma", "Go", "C++", "Java"]	["Reading", "Investing", "Music", "AI", "#Sleeping"]	["Networking", "Mentorship", "Collaboration", "Teacher"]	["Experience", "Code Review", "PM"]	Xin chào, tôi là Nguyễn Minh Anh. Rất vui được kết nối!	2026-08-21 11:43:52.769394	2026-08-22 13:05:35.872416
\.


--
-- Data for Name: user_tags; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_tags (id, user_id, tag_id, created_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, email, password_hash, full_name, avatar, created_at, updated_at, is_ai, deleted_at, gender, phone) FROM stdin;
fa63627e-ae02-4b51-bea6-8c7af20501ad	tranquochuy@gmail.com	$2b$12$B2Nr.4fUhnSFiA/1Kr3jM.8UukSjJkqW6uwNgpoMa7Xm7EK.R5IRi	Trần Quốc Huy	\N	2026-08-21 11:43:50.567106	2026-08-21 11:43:50.567106	f	\N	Male	0963671649
cfc3c138-db1a-4b67-ace1-0e1b21d42938	lehoangnam@gmail.com	$2b$12$y5VC0rg4X0K5nCeEkkzrLeWRCc81R5MQ8Q0DosxeuTWmSbk5kTrBa	Lê Hoàng Nam	\N	2026-08-21 11:43:50.567106	2026-08-21 11:43:50.567106	f	\N	Female	0999343145
8fcd1ec3-980c-422e-9956-aa675289b2b5	phamducanh@gmail.com	$2b$12$HyBw6dN/gXBzVGz9iECDb.tlx0rZfRFcU4CLNC9CdaGb2AaVo0/da	Phạm Đức Anh	\N	2026-08-21 11:43:50.567106	2026-08-21 11:43:50.567106	f	\N	Male	0946204347
a2a3d7a8-e0a6-4bf8-9183-3c0ee0d2070b	vuthanhdat@gmail.com	$2b$12$P5cOKgadUrAmTGgFYcuJJe9VdRLAmYaenVn/JgSO.E0Rnhn1k01Nu	Vũ Thành Đạt	\N	2026-08-21 11:43:50.567106	2026-08-21 11:43:50.567106	f	\N	Female	0977103957
b70fe0df-4f87-4275-8dec-6160f139ffea	dangngocmai@gmail.com	$2b$12$6vqRYhbi43215wnnNi2gT.JU1Vi4Esu0/mQ/YgcJH0Vtkaenro1a.	Đặng Ngọc Mai	\N	2026-08-21 11:43:50.567106	2026-08-21 11:43:50.567106	f	\N	Female	0916585234
d896dfec-6d5f-4708-9d8b-ac7d97174165	buikhanhlinh@gmail.com	$2b$12$J4KWz.GU.kofk7oAUYisR.ZAh2k4t9LcBqHM/u9NPMTPeyflgkGHG	Bùi Khánh Linh	\N	2026-08-21 11:43:50.567106	2026-08-21 11:43:50.567106	f	\N	Male	0952510885
d367d79b-6cb8-4215-856d-bd6832604eac	hoangminhquan@gmail.com	$2b$12$LpqsJG5MgJbUpf4VO0FDweaVdwT5hj71lPPZTRbp7qm/zSUthcVNC	Hoàng Minh Quân	\N	2026-08-21 11:43:50.567106	2026-08-21 11:43:50.567106	f	\N	Male	0942296353
33a2cf07-6177-420e-bfd7-99cdae79b549	dotuankiet@gmail.com	$2b$12$CPKFNYyh6s6NO535VCME6uYp35nf8XIvmwxb.Zpj3CDjTEfPyyYoi	Đỗ Tuấn Kiệt	\N	2026-08-21 11:43:50.567106	2026-08-21 11:43:50.567106	f	\N	Female	0994021472
720e462f-449a-4ec5-85c5-7452c94823ce	nguyenhaphuong@gmail.com	$2b$12$q5cxohOPquGUsfvUg7LPC.J6U0QWRtwcNiYY37zpy5NbOoBuFdW9i	Nguyễn Hà Phương	\N	2026-08-21 11:43:50.567106	2026-08-21 11:43:50.567106	f	\N	Female	0960009343
a26ed1fb-e5f3-42e8-9c27-89ef5ea47a59	nguyenminhanh@gmail.com	$2b$12$Il50mUobjuUuS9TcRuHyoOsFGm/EtfLjTBfpZAJ0P03tSRsHp86me	Nguyễn Minh Anh	\N	2026-08-21 11:43:50.567106	2026-08-21 13:58:20.935188	f	\N	female	0956961719
\.


--
-- Name: ai_system_config ai_system_config_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ai_system_config
    ADD CONSTRAINT ai_system_config_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: assistant_memories assistant_memories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.assistant_memories
    ADD CONSTRAINT assistant_memories_pkey PRIMARY KEY (id);


--
-- Name: connection_requests connection_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.connection_requests
    ADD CONSTRAINT connection_requests_pkey PRIMARY KEY (id);


--
-- Name: contact_memories contact_memories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contact_memories
    ADD CONSTRAINT contact_memories_pkey PRIMARY KEY (id);


--
-- Name: contacts contacts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contacts
    ADD CONSTRAINT contacts_pkey PRIMARY KEY (id);


--
-- Name: conversation_user_state conversation_user_state_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.conversation_user_state
    ADD CONSTRAINT conversation_user_state_pkey PRIMARY KEY (id);


--
-- Name: direct_conversations direct_conversations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.direct_conversations
    ADD CONSTRAINT direct_conversations_pkey PRIMARY KEY (id);


--
-- Name: event_logs event_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_logs
    ADD CONSTRAINT event_logs_pkey PRIMARY KEY (id);


--
-- Name: message_reactions message_reactions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.message_reactions
    ADD CONSTRAINT message_reactions_pkey PRIMARY KEY (id);


--
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- Name: outbox_events outbox_events_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.outbox_events
    ADD CONSTRAINT outbox_events_pkey PRIMARY KEY (id);


--
-- Name: recommendations recommendations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recommendations
    ADD CONSTRAINT recommendations_pkey PRIMARY KEY (id);


--
-- Name: search_history search_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.search_history
    ADD CONSTRAINT search_history_pkey PRIMARY KEY (id);


--
-- Name: settings settings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.settings
    ADD CONSTRAINT settings_pkey PRIMARY KEY (user_id);


--
-- Name: tags tags_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT tags_pkey PRIMARY KEY (id);


--
-- Name: messages uq_client_message_id; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT uq_client_message_id UNIQUE (sender_user_id, client_message_id);


--
-- Name: connection_requests uq_connection_request; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.connection_requests
    ADD CONSTRAINT uq_connection_request UNIQUE (sender_id, receiver_id);


--
-- Name: direct_conversations uq_direct_conversation; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.direct_conversations
    ADD CONSTRAINT uq_direct_conversation UNIQUE (user_a_id, user_b_id);


--
-- Name: message_reactions uq_message_user_emoji; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.message_reactions
    ADD CONSTRAINT uq_message_user_emoji UNIQUE (message_id, user_id, emoji);


--
-- Name: ai_system_config uq_user_ai_config; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ai_system_config
    ADD CONSTRAINT uq_user_ai_config UNIQUE (user_id, key);


--
-- Name: user_tags uq_user_tag; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_tags
    ADD CONSTRAINT uq_user_tag UNIQUE (user_id, tag_id);


--
-- Name: tags uq_user_tag_name; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT uq_user_tag_name UNIQUE (user_id, name);


--
-- Name: user_profiles user_profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_profiles
    ADD CONSTRAINT user_profiles_pkey PRIMARY KEY (user_id);


--
-- Name: user_tags user_tags_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_tags
    ADD CONSTRAINT user_tags_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_ai_system_config_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_ai_system_config_key ON public.ai_system_config USING btree (key);


--
-- Name: ix_ai_system_config_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_ai_system_config_user_id ON public.ai_system_config USING btree (user_id);


--
-- Name: ix_assistant_memories_conversation_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_assistant_memories_conversation_id ON public.assistant_memories USING btree (conversation_id);


--
-- Name: ix_assistant_memories_owner_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_assistant_memories_owner_user_id ON public.assistant_memories USING btree (owner_user_id);


--
-- Name: ix_connection_requests_receiver_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_connection_requests_receiver_id ON public.connection_requests USING btree (receiver_id);


--
-- Name: ix_connection_requests_sender_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_connection_requests_sender_id ON public.connection_requests USING btree (sender_id);


--
-- Name: ix_connection_requests_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_connection_requests_status ON public.connection_requests USING btree (status);


--
-- Name: ix_contact_memories_contact_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_contact_memories_contact_id ON public.contact_memories USING btree (contact_id);


--
-- Name: ix_contacts_conversation_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_contacts_conversation_id ON public.contacts USING btree (conversation_id);


--
-- Name: ix_contacts_owner_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_contacts_owner_user_id ON public.contacts USING btree (owner_user_id);


--
-- Name: ix_conversation_user_state_conversation_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_conversation_user_state_conversation_id ON public.conversation_user_state USING btree (conversation_id);


--
-- Name: ix_conversation_user_state_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_conversation_user_state_user_id ON public.conversation_user_state USING btree (user_id);


--
-- Name: ix_direct_conversations_user_a_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_direct_conversations_user_a_id ON public.direct_conversations USING btree (user_a_id);


--
-- Name: ix_direct_conversations_user_b_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_direct_conversations_user_b_id ON public.direct_conversations USING btree (user_b_id);


--
-- Name: ix_event_logs_conversation_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_event_logs_conversation_id ON public.event_logs USING btree (conversation_id);


--
-- Name: ix_event_logs_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_event_logs_user_id ON public.event_logs USING btree (user_id);


--
-- Name: ix_message_reactions_message_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_message_reactions_message_id ON public.message_reactions USING btree (message_id);


--
-- Name: ix_message_reactions_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_message_reactions_user_id ON public.message_reactions USING btree (user_id);


--
-- Name: ix_messages_client_message_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_messages_client_message_id ON public.messages USING btree (client_message_id);


--
-- Name: ix_messages_conv_created_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_messages_conv_created_id ON public.messages USING btree (conversation_id, created_at, id);


--
-- Name: ix_messages_conversation_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_messages_conversation_id ON public.messages USING btree (conversation_id);


--
-- Name: ix_messages_sender_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_messages_sender_user_id ON public.messages USING btree (sender_user_id);


--
-- Name: ix_notifications_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notifications_user_id ON public.notifications USING btree (user_id);


--
-- Name: ix_outbox_events_event_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_outbox_events_event_type ON public.outbox_events USING btree (event_type);


--
-- Name: ix_outbox_events_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_outbox_events_status ON public.outbox_events USING btree (status);


--
-- Name: ix_recommendations_contact_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_recommendations_contact_id ON public.recommendations USING btree (contact_id);


--
-- Name: ix_recommendations_owner_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_recommendations_owner_user_id ON public.recommendations USING btree (owner_user_id);


--
-- Name: ix_recommendations_target_contact_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_recommendations_target_contact_id ON public.recommendations USING btree (target_contact_id);


--
-- Name: ix_recommendations_target_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_recommendations_target_user_id ON public.recommendations USING btree (target_user_id);


--
-- Name: ix_search_history_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_search_history_user_id ON public.search_history USING btree (user_id);


--
-- Name: ix_tags_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tags_name ON public.tags USING btree (name);


--
-- Name: ix_tags_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tags_user_id ON public.tags USING btree (user_id);


--
-- Name: ix_user_tags_tag_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_tags_tag_id ON public.user_tags USING btree (tag_id);


--
-- Name: ix_user_tags_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_tags_user_id ON public.user_tags USING btree (user_id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_phone; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_phone ON public.users USING btree (phone);


--
-- Name: ai_system_config ai_system_config_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ai_system_config
    ADD CONSTRAINT ai_system_config_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: assistant_memories assistant_memories_conversation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.assistant_memories
    ADD CONSTRAINT assistant_memories_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.direct_conversations(id) ON DELETE CASCADE;


--
-- Name: assistant_memories assistant_memories_owner_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.assistant_memories
    ADD CONSTRAINT assistant_memories_owner_user_id_fkey FOREIGN KEY (owner_user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: connection_requests connection_requests_receiver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.connection_requests
    ADD CONSTRAINT connection_requests_receiver_id_fkey FOREIGN KEY (receiver_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: connection_requests connection_requests_sender_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.connection_requests
    ADD CONSTRAINT connection_requests_sender_id_fkey FOREIGN KEY (sender_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: contact_memories contact_memories_contact_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contact_memories
    ADD CONSTRAINT contact_memories_contact_id_fkey FOREIGN KEY (contact_id) REFERENCES public.contacts(id) ON DELETE CASCADE;


--
-- Name: contacts contacts_conversation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contacts
    ADD CONSTRAINT contacts_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.direct_conversations(id) ON DELETE SET NULL;


--
-- Name: contacts contacts_owner_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contacts
    ADD CONSTRAINT contacts_owner_user_id_fkey FOREIGN KEY (owner_user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: conversation_user_state conversation_user_state_conversation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.conversation_user_state
    ADD CONSTRAINT conversation_user_state_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.direct_conversations(id) ON DELETE CASCADE;


--
-- Name: conversation_user_state conversation_user_state_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.conversation_user_state
    ADD CONSTRAINT conversation_user_state_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: direct_conversations direct_conversations_user_a_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.direct_conversations
    ADD CONSTRAINT direct_conversations_user_a_id_fkey FOREIGN KEY (user_a_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: direct_conversations direct_conversations_user_b_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.direct_conversations
    ADD CONSTRAINT direct_conversations_user_b_id_fkey FOREIGN KEY (user_b_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: event_logs event_logs_conversation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_logs
    ADD CONSTRAINT event_logs_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.direct_conversations(id) ON DELETE SET NULL;


--
-- Name: event_logs event_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_logs
    ADD CONSTRAINT event_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: message_reactions message_reactions_message_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.message_reactions
    ADD CONSTRAINT message_reactions_message_id_fkey FOREIGN KEY (message_id) REFERENCES public.messages(id) ON DELETE CASCADE;


--
-- Name: message_reactions message_reactions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.message_reactions
    ADD CONSTRAINT message_reactions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: messages messages_conversation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.direct_conversations(id) ON DELETE CASCADE;


--
-- Name: messages messages_reply_to_message_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_reply_to_message_id_fkey FOREIGN KEY (reply_to_message_id) REFERENCES public.messages(id) ON DELETE SET NULL;


--
-- Name: messages messages_sender_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_sender_user_id_fkey FOREIGN KEY (sender_user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: notifications notifications_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: recommendations recommendations_contact_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recommendations
    ADD CONSTRAINT recommendations_contact_id_fkey FOREIGN KEY (contact_id) REFERENCES public.contacts(id) ON DELETE CASCADE;


--
-- Name: recommendations recommendations_owner_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recommendations
    ADD CONSTRAINT recommendations_owner_user_id_fkey FOREIGN KEY (owner_user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: recommendations recommendations_target_contact_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recommendations
    ADD CONSTRAINT recommendations_target_contact_id_fkey FOREIGN KEY (target_contact_id) REFERENCES public.contacts(id) ON DELETE CASCADE;


--
-- Name: recommendations recommendations_target_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recommendations
    ADD CONSTRAINT recommendations_target_user_id_fkey FOREIGN KEY (target_user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: search_history search_history_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.search_history
    ADD CONSTRAINT search_history_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: settings settings_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.settings
    ADD CONSTRAINT settings_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: tags tags_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT tags_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_profiles user_profiles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_profiles
    ADD CONSTRAINT user_profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_tags user_tags_tag_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_tags
    ADD CONSTRAINT user_tags_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES public.tags(id) ON DELETE CASCADE;


--
-- Name: user_tags user_tags_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_tags
    ADD CONSTRAINT user_tags_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict Wm8DwarlRcZosvcR3ZchImLnak66SoBVMQvc3NS3ylMH78ZYwrM5JcivfQCjeo7

