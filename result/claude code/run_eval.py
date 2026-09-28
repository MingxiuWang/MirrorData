"""Judge each MirrorData task in isolation.

One stateless API call per task. Each request carries only that task's own
description.txt and candidate.py - no other task, no shared conversation, no
tools (so no web search, no file access). Nothing is retained between tasks.
"""
import anthropic, json, os, sys, time, threading
from concurrent.futures import ThreadPoolExecutor

BASE = os.path.dirname(os.path.abspath(__file__))
ENV, OUT = f"{BASE}/env", f"{BASE}/out"
MODEL = "claude-sonnet-5"
WORKERS = int(os.environ.get("WORKERS", "12"))

SCHEMA = {"type": "object",
          "properties": {"verdict": {"type": "string", "enum": ["correct", "incorrect"]}},
          "required": ["verdict"], "additionalProperties": False}

SYSTEM = (
    "You judge whether a Python program is a correct solution to a programming task.\n"
    "Judge it as a competitive-programming submission: it must give right answers for all inputs "
    "allowed by the stated constraints (not just the example in the statement), print output in the "
    "required format, run fast enough for the stated limits, and not crash. If the statement says any "
    "valid answer is accepted, any valid answer counts.\n"
    "This is a quick judgement - do not deliberate at length."
)

client = anthropic.Anthropic(max_retries=5)
lock = threading.Lock()
done = 0

def judge(idx):
    global done
    outp = f"{OUT}/task_{idx:04d}.json"
    if os.path.exists(outp):
        return
    d = f"{ENV}/task_{idx:04d}"
    desc = open(f"{d}/description.txt").read()
    code = open(f"{d}/candidate.py").read()
    msg = (f"TASK DESCRIPTION:\n{desc}\n\nCANDIDATE PROGRAM:\n{code}\n\n"
           f"Is this program a correct solution to the task?")
    last = None
    for attempt in range(6):
        try:
            r = client.messages.create(
                model=MODEL, max_tokens=64,
                thinking={"type": "disabled"},
                output_config={"effort": "low",
                               "format": {"type": "json_schema", "schema": SCHEMA}},
                system=SYSTEM,
                messages=[{"role": "user", "content": msg}],
            )
            txt = "".join(b.text for b in r.content if b.type == "text").strip()
            verdict = json.loads(txt)["verdict"]
            json.dump({"index": idx, "task_id": idx + 1, "verdict": verdict,
                       "input_tokens": r.usage.input_tokens,
                       "output_tokens": r.usage.output_tokens},
                      open(outp, "w"))
            with lock:
                done += 1
                if done % 25 == 0:
                    print(f"  {done} judged", flush=True)
            return
        except Exception as e:
            last = e
            time.sleep(min(2 ** attempt, 30))
    with lock:
        print(f"  task {idx} FAILED: {str(last)[:120]}", flush=True)

todo = [i for i in range(645) if not os.path.exists(f"{OUT}/task_{i:04d}.json")]
print(f"tasks to judge: {len(todo)} (workers={WORKERS}, model={MODEL}, effort=low, thinking=disabled)")
t0 = time.time()
with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    list(ex.map(judge, todo))
n = len(os.listdir(OUT))
print(f"complete: {n}/645 in {time.time()-t0:.0f}s")
