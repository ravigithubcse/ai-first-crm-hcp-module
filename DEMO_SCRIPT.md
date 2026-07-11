# Demo Video Script — AI-First CRM: HCP Interaction Module
**Presenter:** Ravikumar · **Target length:** 12–14 minutes · **Repo:** github.com/ravigithubcse/ai-first-crm-hcp-module

---

## Before you hit record

1. `docker compose up -d` (or your own Postgres), then start the backend
   (`uvicorn app.main:app --reload`) and frontend (`npm run dev`) — both
   running and visible in your browser at `localhost:5173`.
2. Make sure `backend/.env` has a **real** `GROQ_API_KEY`.
3. **Do one full silent dry-run of Part 3 before you record.** I built and
   tested every route, the database layer, and the agent's wiring, but I
   don't have a Groq key myself, so the live wording the AI replies with is
   something neither of us has actually seen yet. If a response looks
   slightly different from the script below, don't stop — just narrate what
   *did* happen naturally. It's the same tool either way.
4. Screen recorder: OBS Studio (free) or your OS's built-in recorder.
   Record browser + a small webcam corner if you can — it reads better than
   a flat screen capture.
5. Speak like you're explaining it to a teammate, not reading a script word
   for word. Pause a beat between sections — it's easy to trim in editing.

---

## Part 1 — Intro (0:00–0:45)

> "Hi, I'm Ravikumar. This is my submission for the AI-First CRM assignment
> — the Log HCP Interaction module for a pharma field rep CRM.
>
> The brief asked for a screen where a rep can log a visit with a doctor
> either by filling a structured form, or by just describing what happened
> in plain English to an AI assistant — with LangGraph and Groq doing the
> heavy lifting underneath. That's exactly what I built. Let me walk you
> through it."

---

## Part 2 — Architecture & tech stack (0:45–2:15)

Show the README or just talk over the running app.

> "Quick overview of the stack: React 19 with TypeScript and Redux Toolkit
> on the frontend, shadcn/ui components, Tailwind for styling. Backend is
> FastAPI with SQLAlchemy over PostgreSQL. The AI side is a LangGraph agent
> — five tools bound to Groq's `llama-3.3-70b-versatile` model, which
> decides which tool to call based on what the rep types. Each tool then
> makes its own call to Groq's `gemma2-9b-it` — the model this assignment
> specifically asked for — to actually pull the structured data out of the
> rep's sentence: HCP name, topics, sentiment, materials, samples.
>
> So there are really two layers of AI here: one model deciding *what to
> do*, and another doing the *language understanding* for each action."

*(Optional, if you want to show it: open `backend/app/langgraph_tools/agent.py`
for two seconds and point at the `ALL_TOOLS` list and the `agent → tools → agent`
graph — just enough to prove it's real, not a slide.)*

---

## Part 3 — Frontend walkthrough (2:15–3:45)

Click through the sidebar as you talk.

> "The app has five screens. Dashboard gives a quick overview. HCP
> Management is where profiles live. Interactions is the full log of
> everything recorded. Follow-ups tracks what's pending. And this one —
> Log Interaction — is the screen the assignment is really about, so
> that's where I'll spend most of this demo."

Land on `/log-interaction`.

> "Structured form on the left, AI Assistant on the right — both visible
> at the same time, both writing to the same record. That's deliberate:
> whichever way the rep logs something, it shows up in both places
> immediately, so nothing feels hidden or disconnected."

---

## Part 4 — Live demo: all five tools (3:45–11:30)

One continuous story — logging a visit to a single HCP, then editing,
reviewing, reporting on, and following up on that same visit. Type each
line into the chat box on the right and send it.

### Tool 1 — Log Interaction (3:45–5:30)

Type exactly:

```
Met Dr. Anjali Sharma today at Apollo Hospitals, discussed the OncoBoost Phase III efficacy data. She seemed very positive about the results and asked good questions. I left the OncoBoost Phase III brochure and two starter samples.
```

> "I haven't created Dr. Sharma anywhere — she doesn't exist in the system
> yet. Watch what happens."

After it responds:

> "The agent pulled out the HCP name, created her record since she was
> new, figured out the topic, picked up the positive sentiment, logged the
> brochure and samples — and look at the form on the left: it's filled in
> live from that one sentence. That's the auto-fill behavior tying the chat
> and the form together. If I wanted to tweak anything before saving, I
> still can — it's not locked."

Point at the **"Editing interaction #—"** badge above the form.

> "That number is the interaction ID — I'll use it in a second for editing,
> reporting, and follow-up, exactly like a rep would if they were doing
> this for real."

### Tool 2 — Edit Interaction (5:30–7:00)

Type (replace `[ID]` with the number from the badge):

```
For interaction [ID], add that she also requested the peer-reviewed publication list.
```

> "This is a correction after the fact — the kind of thing that happens
> constantly in real CRM use. I didn't have to open the record and hunt
> for a field; I just told it what changed."

### Tool 3 — View History (7:00–8:15)

```
Show me the interaction history for Dr. Sharma
```

> "This pulls every past interaction with her, plus the AI's own summary
> of the pattern — useful before walking into a follow-up visit so you're
> not starting from zero."

### Tool 4 — Generate Report (8:15–9:30)

```
Generate a call report for interaction [ID]
```

> "This turns the raw log into a structured report — the kind of writeup
> that'd go to a manager or into a compliance file, generated from a
> two-sentence chat message."

### Tool 5 — Schedule Follow-up (9:30–11:00)

```
Schedule a follow-up with Dr. Sharma in 2 weeks to share the peer-reviewed publications
```

> "And the last one — turning what we just talked about into an actual
> scheduled task, so it doesn't get forgotten." *(Optionally click over to
> the Follow-ups page to show it landed there.)*

### Wrap the live section (11:00–11:30)

> "That's all five tools — log, edit, view history, generate report,
> schedule follow-up — each one a real LangGraph tool the agent chose on
> its own based on what I typed, not a hardcoded menu."

---

## Part 5 — Code structure, briefly (11:30–13:15)

Have the repo open in your editor, scroll rather than read line by line.

> "On the backend, `app/langgraph_tools` is the agent — one file per tool,
> plus `agent.py`, which wires them all together: it binds the five tools
> to the Groq model, and lets that model decide which one to call. That
> decision-making is genuinely the LLM's, not a keyword check — the model
> reasons over the conversation and picks.
>
> `app/api` has the FastAPI routes — separate files for HCPs, interactions,
> follow-ups, and the agent chat endpoint. `app/models` and `app/schemas`
> are the SQLAlchemy tables and the Pydantic request/response shapes.
>
> On the frontend, `src/pages` holds the five screens, `src/store` is the
> Redux Toolkit slices — one for chat, one for interactions, one for HCPs.
> `LogInteraction.tsx` is the one doing the interesting work: it watches
> the chat's messages, and whenever the AI successfully logs or edits an
> interaction, an effect reads the structured result straight out of that
> message and fills in the form state — that's the mechanism behind the
> auto-fill you just saw.
>
> Everything's covered by a small pytest suite too — CRUD routes and the
> agent graph's structure — so the plumbing is checked independent of
> whether a live Groq key is configured."

---

## Part 6 — What I understood from the task (13:15–14:00)

> "The core idea, as I understood it, was: field reps are busy, and asking
> them to fill out a long form after every single visit is friction that
> gets skipped in real life. So the goal wasn't just 'add a chatbot' — it
> was making the structured, compliance-grade record and the natural,
> conversational way of capturing it be *the same thing*, not two separate
> systems that drift apart. That's why I made sure the two panels stay in
> sync live, instead of just having a chatbot that quietly writes to the
> database somewhere the rep can't see.
>
> And using LangGraph properly meant the agent should genuinely *decide*
> which action to take from the conversation — so I made sure that
> decision is made by the LLM reasoning over the five tools, not a fixed
> if/else behind the scenes."

---

## Part 7 — Closing (14:00–14:20)

> "That's the full walkthrough — structured form and AI chat writing to
> one record, five working LangGraph tools backed by Groq, and the code's
> up on GitHub with a full README for anyone who wants to run it locally.
> Thanks for watching."

---

## Quick reference — all five prompts in order

```
1. Met Dr. Anjali Sharma today at Apollo Hospitals, discussed the OncoBoost Phase III efficacy data. She seemed very positive about the results and asked good questions. I left the OncoBoost Phase III brochure and two starter samples.

2. For interaction [ID], add that she also requested the peer-reviewed publication list.

3. Show me the interaction history for Dr. Sharma

4. Generate a call report for interaction [ID]

5. Schedule a follow-up with Dr. Sharma in 2 weeks to share the peer-reviewed publications
```

Replace `[ID]` both times with the number shown in the blue "Editing
interaction #—" badge after step 1 runs.
