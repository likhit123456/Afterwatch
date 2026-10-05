# GitLab Duo Agent Platform: Flow Registry v1 schema notes

Reference for writing flows in this repo. Only facts confirmed for the v1 spec are
listed here; if a field is not in this doc, check the official spec before using it.

## Top-level structure

```yaml
version: "v1"
environment: ambient      # ambient | chat | chat-partial
components: []
routers: []
flow:
  entry_point: <component name>
```

- `environment`: `ambient`, `chat` or `chat-partial`. Use `ambient` for hands-off flows.
- `flow.entry_point` names the first component to run.

## Component types

- `AgentComponent`
- `OneOffComponent`
- `DeterministicStepComponent`
- `HumanInputComponent`
- `EndComponent` / `AbortComponent` (`end` and `abort` are built in)

## Termination

Every flow must terminate at `end` (success) or `abort` (error).

## Rules that cause most failures

### 1. Project ID for GitLab API tools

Any component that calls a GitLab API tool MUST:

- list this in its inputs:

  ```yaml
  - from: "context:project_id"
    as: "project_id"
  ```

- include `Project ID: {{ project_id }}` in the prompt `user:` block.

Omitting this is the #1 failure cause.

### 2. Inline prompts

Inline prompts MUST include `unit_primitives: []` and `placeholder: history`.

### 3. Stop instruction

Every `system:` prompt MUST end with an explicit stop instruction, for example
"When X, your final answer is Y. No further steps are needed." Without one, the
agent loops.

### 4. No literal Jinja in prompt text

The platform runs the system prompt through Jinja2 first. In prompt TEXT, never
write double curly braces as literal documentation. Use `<<var>>` in explanatory
text instead. Real template variables (like `project_id` above) are fine where a
substitution is intended.

### 5. Branch/MR flows need standard context

Flows that create branches or MRs need `flow.inputs` with the
`agent_platform_standard_context` schema, providing:

- `primary_branch`
- `workload_branch`
- `session_owner_id`

## Supervisor mode

An `AgentComponent` with `subagents:` automatically gets `delegate_task` and
`final_response_tool`. Every sub-agent needs a `description`.

## Common tools

`read_file`, `edit_file`, `create_file_with_contents`, `run_command`,
`create_branch`, `create_merge_request`, `get_issue`, `create_issue_note`,
`create_merge_request_note`, `get_merge_request`.
