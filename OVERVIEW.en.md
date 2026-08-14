# ADK Multi-Agent Workshop: The Copywriting Crew

*A detailed English companion to the README — what this repo teaches, how it is structured, and why each design decision was made.*

## The Big Idea

This workshop teaches you to build a multi-agent system with Google's Agent Development Kit (ADK) 1.x, using a single running example throughout: a **marketing copywriting crew**. Instead of jumping between disconnected toy examples, you grow one system step by step — first a lone agent, then an agent with tools, then a coordinated team of specialists, and finally a guarded, production-minded version of that team.

The running product domain is a **health-supplement brand** (fish oil, probiotics, lutein…) — chosen because supplement advertising is heavily regulated, which makes the Lab 3 guardrails concrete rather than contrived. The crew mirrors how a real marketing agency works. A coordinator talks to the client. Two researchers gather market trends and audience insights. A copywriter drafts the campaign. A strict reviewer either approves the draft or sends it back for revision — up to three rounds. By the end, you will have watched agents hand work to each other, share findings through a common whiteboard, and loop until quality is reached.

The final session contrasts this 1.x architecture with ADK 2.0's graph-based workflows, so you leave understanding not just *how* to build with today's API, but *where the framework is heading and why*.

## Repository Layout

| Stage | Folder | What you do |
|---|---|---|
| Warm-up | `hello_agent/` + `lab1_tools/` | Verify the environment and see tool-calling once (10 min, not a graded exercise) |
| Lab 2 | `lab2_multi_agent/` | Assemble the full crew (the main event) |
| Lab 3 | `lab3_callbacks/` | Guardrails with callbacks **+ memory** (cross-session, via agent-level hooks) |
| Lab 4 | `lab4_mcp/` | **MCP**: consume a third-party server (Fetch) and build your own (compliance) |
| Lab 5 | `lab5_workflow_graph/` | Read/watch: all of Lab 1–4 re-expressed as an ADK 2.0 graph |
| Extras | `challenges.md` | Optional challenges, easy to hard |

Every lab is a fill-in-the-TODO exercise. If you get stuck, the `solutions/` folder contains complete answers — diff them against your attempt to see exactly where you diverged.

## Warm-up — Tools: Giving the Agent Hands

*(For a capable cohort this is a 10-minute read-and-run, not a graded lab — the live session starts at Lab 2.)*

A bare LLM agent can only talk. Tools give it the ability to *do* things — or in our case, to *look things up*. In ADK, a tool is just a Python function. The framework sends the function's name, its type hints, and its docstring to the model, so the docstring is effectively a user manual written for the LLM. Write it carelessly and the model will call your tool with the wrong arguments, or not at all.

You will implement two mock research tools — `get_market_trends` and `get_audience_profile` — and attach them to a research assistant agent. The data is hard-coded on purpose; the lesson here is the *mechanics* of tool calling, not data engineering.

The lab's most valuable moment is a deliberate before-and-after experiment: ask the agent about the Taiwanese fish-oil supplement market *before* attaching any tools, and watch it fabricate a confident answer. Attach the tools and ask again. The difference between hallucination and grounded response — visible in the Events panel of `adk web` — is the entire reason tools exist.

## Lab 2 — The Main Event: Assembling the Crew

This is where individual agents become a system. The target structure:

```
campaign_coordinator (root)
└── campaign_pipeline (SequentialAgent)
    ├── trend_researcher       → writes state["market_trends"]
    ├── audience_researcher    → writes state["audience_profile"]
    └── write_review_loop (LoopAgent, max 3 iterations)
        ├── writer             → reads research, writes state["campaign_copy"]
        └── reviewer           → approves, or writes revision feedback
```

Three coordination mechanisms carry all the weight, and each one is a TODO you complete yourself:

**Session state is the shared whiteboard.** An agent with `output_key="market_trends"` automatically writes its final answer into the session state under that key. A downstream agent reads it by embedding `{market_trends}` in its instruction — ADK substitutes the value at runtime. A trailing question mark, as in `{review_feedback?}`, marks the key as optional, which matters because no feedback exists during the first writing round.

**Workflow agents encode the process.** A `SequentialAgent` runs its children strictly in order — research first, then writing. A `LoopAgent` repeats its children up to `max_iterations` times. Note what these are: agents whose behavior is *deterministic orchestration*, not LLM reasoning. The LLM decides what to say; the workflow agents decide who speaks next.

**Escalation is the emergency exit.** How does the loop end early when the reviewer is satisfied? The reviewer calls an `approve_copy` tool, which sets `tool_context.actions.escalate = True`, telling the LoopAgent to stop. Sit with the uncomfortable part: loop termination depends on an LLM *remembering to call a tool*. The `max_iterations=3` is not the design — it is the fuse that keeps a forgetful model from looping forever. This exact pain point is what ADK 2.0 redesigns.

The lab closes with a deeper exercise, `record_revision`, where you write state from *inside a tool* using `tool_context.state`. Until now state was written for you by `output_key`; here you manipulate the whiteboard directly — read a counter, increment it, write it back — and watch it tick upward in the State panel across revision rounds. Ninety percent of multi-agent debugging is chasing state, so this small exercise builds the muscle you will use most in real projects.

## Lab 3 — Callbacks: One Concept, Three Interception Points

A demo agent can be naive; a deployed one cannot. Callbacks are ADK's hook points around every agent, model, and tool invocation. This lab enforces real **health-supplement advertising rules** — no medical-efficacy claims, no exaggerated/absolute superlatives, no marketing of restricted ingredients or to restricted audiences — placing a different rule at each of three layers to reveal how differently each behaves.

**`before_model_callback` — block at the gate.** Runs before every LLM call. Return `None` to let the request through; return an `LlmResponse` to short-circuit — your response is used and the model is never invoked. You will block requests that ask for **medical-efficacy claims** (治療／療效／降血壓…), which supplements legally cannot make. The proof lives in the Events panel: a blocked turn shows *no LLM call at all*, which also means no token cost.

**`after_model_callback` — sanitize on the way out.** Runs after the model responds, before anyone sees it. You cannot "block" here — the text already exists — so instead you rewrite it, masking **illegal superlatives** ("全球銷量第一", "立即見效", "無副作用") with ○○○. Blocking versus sanitizing are two distinct guardrail philosophies: input filters prevent, output filters redact. Production systems usually need both.

**`before_tool_callback` — validate the arguments.** Runs before a tool executes, with access to the tool's name and its arguments. You will intercept tool calls whose LLM-chosen arguments are restricted: a **controlled ingredient** (e.g., 褪黑激素/melatonin, a drug in Taiwan, not a supplement) passed as `product_category`, or a **protected audience** (孕婦/嬰幼兒) passed as `audience_group`. Here is the question worth pausing on: why can't the input filter handle this? Because these values are *chosen by the LLM*, not copied from the user's message — a user asks for "something to help sleep" and the model fills in "褪黑激素". The only place you can see the actual value is the tool layer.

One placement rule ties it together: a `before_tool_callback` must be attached to the agent that *owns* the tool — hang it on the root agent and it will never fire for a sub-agent's tools. Because this lab guards *two* tools, the same callback hangs on *both* owners (`trend_researcher` for the ingredient, `audience_researcher` for the audience).

**Then memory, through the one hook level the guardrails skipped.** The three guardrails live at the model and tool levels; memory enters at the *agent* level (`before_agent_callback` / `after_agent_callback`), which rounds out all three. A `before_agent` hook calls `search_memory` to load this brand's past campaigns into state so the writer stays on-voice; an `after_agent` hook on the pipeline calls `add_session_to_memory` so the finished campaign is remembered next time. This also nails a common confusion: **session state (Lab 2) is the short-term whiteboard for *this* conversation; memory is long-term and persists *across* sessions.** The workshop uses `InMemoryMemoryService` (zero setup); the same interface swaps to a Vertex AI service for production.

## Lab 4 — MCP: Tools You Didn't Write, and One You Did

MCP (Model Context Protocol) is "USB-C for AI tools" — a standard way for an agent to plug into tools served by external servers, instead of hand-writing every integration. This lab works both ends. **As a client (Part A),** `audience_researcher` drops its mock and uses a third-party **Fetch MCP server** to pull real web content and build the audience profile — a tool you didn't write, discovered automatically by `MCPToolset`. **As a server (Part B),** you build your own **compliance MCP server** that wraps Lab 3's rules into a reusable `check_ad_compliance` tool, and the reviewer calls it before approving. The payoff is the contrast: Lab 3's rules were a callback *baked into this app*; here the same rules become a *standalone service* any MCP client can consume. The Fetch server needs no API key (it just fetches public web pages), so the lab stays zero-auth.

## Lab 5 — The 2.0 Contrast

The finale revisits every awkward moment of Labs 2–4 through ADK 2.0's lens. The revision loop that depended on prompt-level pleading becomes a conditional edge in an explicit graph. Handoffs that relied on the LLM "remembering to transfer" become edges that either exist or do not. The mental shift: 1.x lets the LLM improvise the control flow; 2.0 draws the control flow and lets the LLM fill in the nodes. This session is instructor-led — read along rather than code along.

## Beyond the Labs

The challenges in `challenges.md` extend the crew in production directions, roughly in ascending difficulty: swap mock data for live Google Search grounding (and hit a deliberate constraint about mixing built-in and custom tools); force structured JSON output with Pydantic schemas; persist the final copy as a versioned Artifact; replace mocks with real BigQuery queries via the MCP Toolbox; and add a brand-new media-planning agent to the pipeline end-to-end — the truest test that the concepts stuck.

Deployment is intentionally out of scope — the previous session covered it, and this same crew ships to Agent Engine with a single `adk deploy` command. When you are ready for the full production path (MCP, A2A, Cloud Run, automated grading), the capstone Campaign Challenge Lab on Google Skills is the recommended next step.

## How to Get the Most Out of This

Run everything through `adk web`, and treat the Events panel as your microscope: every tool call, every agent transfer, every state write is visible there. After each TODO, resist the urge to move on — re-run the system and *predict* what will change before you look. The gap between your prediction and the actual event stream is where the learning happens.
