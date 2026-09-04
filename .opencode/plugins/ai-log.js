import { appendFile, mkdir } from "node:fs/promises"
import { execFile } from "node:child_process"
import { join } from "node:path"
import { promisify } from "node:util"

const VN_OFFSET = "+07:00"
const exec = promisify(execFile)

function localTimestamp() {
  const now = new Date()
  const shifted = new Date(now.getTime() + 7 * 60 * 60 * 1000)
  return shifted.toISOString().replace("Z", VN_OFFSET)
}

function props(event) {
  return event.properties || {}
}

function sessionId(event) {
  const value = props(event)
  return value.sessionID || value.info?.sessionID || value.part?.sessionID || "unknown"
}

function messageId(event) {
  const value = props(event)
  return value.info?.id || value.part?.messageID || value.messageID || "unknown"
}

function textFor(message, parts) {
  const content = message?.content
  if (typeof content === "string") return content.trim()
  return (parts.get(message?.id) || "").trim()
}

async function gitValue(worktree, ...args) {
  try {
    const result = await exec("git", ["-C", worktree, ...args])
    return result.stdout.trim()
  } catch {
    return ""
  }
}

export const AILogPlugin = async ({ directory, worktree }) => {
  const messages = new Map()
  const parts = new Map()
  const logged = new Set()
  const root = worktree || directory || process.cwd()
  const logDir = process.env.AI_LOG_DIR || join(root, ".ai-log")
  const logFile = join(logDir, "session.jsonl")
  const origin = await gitValue(root, "remote", "get-url", "origin")
  const repo = (origin || root).replace(/\.git$/, "").split(/[\\/]/).pop()
  const branch = await gitValue(root, "rev-parse", "--abbrev-ref", "HEAD")
  const commit = await gitValue(root, "rev-parse", "--short", "HEAD")
  const student = (await gitValue(root, "config", "user.email")) || process.env.USER || "unknown"

  async function writeEntry(sessionID, prompt, response, responseID) {
    const entryID = `opencode-${sessionID}-${responseID}`
    if (logged.has(entryID) || (!prompt && !response)) return
    logged.add(entryID)
    const entry = {
      ts: localTimestamp(),
      tool: "opencode",
      event: "ChatComplete",
      entry_id: entryID,
      session_id: sessionID,
      model: "",
      repo,
      branch,
      commit,
      student,
      prompt: prompt.slice(0, 1000),
      response_summary: response.slice(0, 500),
    }
    await mkdir(logDir, { recursive: true })
    await appendFile(logFile, `${JSON.stringify(entry)}\n`, "utf8")
  }

  return {
    event: async ({ event }) => {
      const value = props(event)
      const id = messageId(event)

      if (event.type === "message.part.updated") {
        const part = value.part || {}
        if (part.type === "text" && typeof part.text === "string") {
          parts.set(part.messageID, part.text)
        }
        return
      }

      if (event.type === "message.updated") {
        const info = value.info || {}
        messages.set(info.id || id, info)
        return
      }

      if (event.type !== "session.idle") return

      const sid = sessionId(event)
      const sessionMessages = [...messages.values()]
        .filter((message) => message.sessionID === sid)
        .sort((a, b) => (a.time?.created || 0) - (b.time?.created || 0))
      const assistant = [...sessionMessages].reverse().find((message) => message.role === "assistant")
      const user = [...sessionMessages].reverse().find(
        (message) => message.role === "user" && (!assistant || (message.time?.created || 0) <= (assistant.time?.created || 0)),
      )
      await writeEntry(sid, textFor(user, parts), textFor(assistant, parts), assistant?.id || "turn")
    },
  }
}

export default AILogPlugin
