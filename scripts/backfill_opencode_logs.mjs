#!/usr/bin/env node

import { appendFile, mkdir, mkdtemp, readFile, readdir, rm } from "node:fs/promises"
import { execFile } from "node:child_process"
import { join } from "node:path"
import { tmpdir } from "node:os"
import { promisify } from "node:util"

const exec = promisify(execFile)
const args = process.argv.slice(2)
const allSessions = args.includes("--all")
const dryRun = args.includes("--dry-run")
const sessionIDs = args.filter((arg) => !arg.startsWith("--"))

if (!allSessions && (!sessionIDs.length || sessionIDs.some((id) => !/^ses_[A-Za-z0-9]+$/.test(id)))) {
  console.error("Usage: node scripts/backfill_opencode_logs.mjs <session-id> [...] [--dry-run]")
  console.error("       node scripts/backfill_opencode_logs.mjs --all [--dry-run]")
  process.exit(1)
}

const root = process.cwd()
const logDir = process.env.AI_LOG_DIR || join(root, ".ai-log")
const logFile = join(logDir, "session.jsonl")
const existingIDs = await loadEntryIDs(logDir)
const metadata = await gitMetadata(root)
const sessions = allSessions ? await listSessions() : sessionIDs
const entries = []

for (const sessionID of sessions) {
  const exported = await exportSession(sessionID)
  for (const entry of entriesFromSession(exported.messages ?? [], sessionID, metadata)) {
    if (!existingIDs.has(entry.entry_id)) {
      existingIDs.add(entry.entry_id)
      entries.push(entry)
    }
  }
}

if (!entries.length) {
  console.log("[ai-log] No new OpenCode turns to import.")
  process.exit(0)
}

if (dryRun) {
  console.log(`[ai-log] Would import ${entries.length} OpenCode turn(s) from ${sessions.length} session(s).`)
  process.exit(0)
}

await mkdir(logDir, { recursive: true })
await appendFile(logFile, `${entries.map((entry) => JSON.stringify(entry)).join("\n")}\n`, "utf8")
console.log(`[ai-log] Imported ${entries.length} OpenCode turn(s) from ${sessions.length} session(s).`)

function entriesFromSession(messages, expectedSessionID, metadata) {
  const entries = []
  for (let index = 0; index < messages.length; index += 1) {
    const userMessage = messages[index]
    if (userMessage.info?.role !== "user") continue

    const nextUserIndex = messages.findIndex(
      (message, candidateIndex) => candidateIndex > index && message.info?.role === "user",
    )
    const turnEnd = nextUserIndex === -1 ? messages.length : nextUserIndex
    const assistantMessage = findFinalAssistantMessage(messages.slice(index + 1, turnEnd))
    const prompt = textFromMessage(userMessage)
    const response = assistantMessage ? textFromMessage(assistantMessage) : ""

    if (!prompt || !response || userMessage.info?.sessionID !== expectedSessionID) continue

    const model = userMessage.info?.model
    entries.push({
      ts: vietnamTimestamp(assistantMessage.info?.time?.created ?? userMessage.info?.time?.created),
      tool: "opencode",
      event: "ChatComplete",
      entry_id: `opencode-${expectedSessionID}-${assistantMessage.info.id}`,
      session_id: expectedSessionID,
      model: model ? `${model.providerID}/${model.modelID}` : "",
      repo: metadata.repo,
      branch: metadata.branch,
      commit: metadata.commit,
      student: metadata.student,
      prompt: prompt.slice(0, 1000),
      response_summary: response.slice(0, 500),
      source: "backfill",
    })
  }
  return entries
}

function findFinalAssistantMessage(messages) {
  return messages
    .filter((message) => message.info?.role === "assistant" && textFromMessage(message))
    .at(-1)
}

function textFromMessage(message) {
  return (message.parts ?? [])
    .filter((part) => part.type === "text" && typeof part.text === "string")
    .map((part) => part.text)
    .join("\n")
    .trim()
}

async function loadEntryIDs(directory) {
  const files = [logFile]
  try {
    const archiveFiles = (await readdir(join(directory, "archive")))
      .filter((file) => file.endsWith(".jsonl"))
      .map((file) => join(directory, "archive", file))
    files.push(...archiveFiles)
  } catch {
    // The archive directory is optional.
  }

  const IDs = new Set()
  for (const file of files) {
    try {
      const content = await readFile(file, "utf8")
      for (const line of content.split("\n")) {
        try {
          const entryID = JSON.parse(line).entry_id
          if (entryID) IDs.add(entryID)
        } catch {
          // Ignore malformed historical lines.
        }
      }
    } catch {
      // A missing log file is equivalent to an empty one.
    }
  }
  return IDs
}

async function listSessions() {
  const { stdout } = await exec(process.env.OPENCODE_BIN || "opencode", ["session", "list"])
  return [...stdout.matchAll(/^(ses_[A-Za-z0-9]+)\s/gm)].map((match) => match[1])
}

async function gitMetadata(worktree) {
  const [origin, branch, commit, student] = await Promise.all([
    gitValue(worktree, "remote", "get-url", "origin"),
    gitValue(worktree, "rev-parse", "--abbrev-ref", "HEAD"),
    gitValue(worktree, "rev-parse", "--short", "HEAD"),
    gitValue(worktree, "config", "user.email"),
  ])
  return {
    repo: (origin || worktree).replace(/\.git$/, "").split(/[\\/]/).at(-1),
    branch,
    commit,
    student: student || process.env.USER || "unknown",
  }
}

async function gitValue(worktree, ...args) {
  try {
    const { stdout } = await exec("git", ["-C", worktree, ...args])
    return stdout.trim()
  } catch {
    return ""
  }
}

function vietnamTimestamp(milliseconds) {
  return new Date(Number(milliseconds) + 7 * 60 * 60 * 1000).toISOString().replace("Z", "+07:00")
}

async function exportSession(id) {
  const directory = await mkdtemp(join(tmpdir(), "opencode-log-"))
  const exportFile = join(directory, "session.json")
  try {
    const binary = process.env.OPENCODE_BIN || "opencode"
    await exec("bash", ["-lc", '"$1" export "$2" > "$3"', "bash", binary, id, exportFile])
    return JSON.parse(await readFile(exportFile, "utf8"))
  } finally {
    await rm(directory, { force: true, recursive: true })
  }
}
