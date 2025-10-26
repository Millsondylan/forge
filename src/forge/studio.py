from __future__ import annotations
import asyncio
from typing import List
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout, HSplit
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.styles import Style
from . import storage


async def _fetch_tasks_text(limit: int = 20) -> str:
    rows = await storage.list_tasks(limit)
    lines = ["ID  STATUS        PAYLOAD"]
    for r in rows:
        rid, payload, status, created, updated = r
        lines.append(f"{rid:<3} {status:<12} {payload}")
    return "\n".join(lines)


def launch_studio(concurrency: int, runner_coro_factory, enqueue_fn):
    kb = KeyBindings()

    output_control = FormattedTextControl(text="Loading...")
    output_window = Window(content=output_control, wrap_lines=False, height=20)

    input_area = TextArea(height=3, prompt="Task> ", multiline=False)

    @input_area.accept_handler
    def accept(buff):
        text = buff.text.strip()
        if text:
            asyncio.get_event_loop().create_task(enqueue_fn(text))
        buff.text = ""

    @kb.add("c-c")
    @kb.add("c-q")
    def _(event):
        event.app.exit()

    root = HSplit([
        Window(height=1, content=FormattedTextControl("AgentForge Studio (Ctrl+C to exit)")),
        output_window,
        input_area,
    ])

    style = Style.from_dict({"window.border": "#666666"})

    app = Application(layout=Layout(root), key_bindings=kb, full_screen=True, style=style)

    async def updater():
        while True:
            txt = await _fetch_tasks_text()
            output_control.text = txt
            app.invalidate()
            await asyncio.sleep(1.0)

    async def enqueue_task(payload: str):
        await storage.enqueue_task(payload)

    loop = asyncio.get_event_loop()

    async def main_async():
        await storage.init_db()
        # Start continuous runner
        loop.create_task(runner_coro_factory())
        loop.create_task(updater())
        await app.run_async()

    asyncio.run(main_async())
