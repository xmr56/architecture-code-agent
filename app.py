"""Windows Tk GUI. API key remains only in process memory."""
import json
import queue
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from core import Agent, DeepSeek, preprocess


def asset_dir():
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))


class App:
    def __init__(self, root):
        self.root = root
        root.title("架构到代码 · Code Agent")
        root.geometry("940x730")
        root.minsize(760, 620)
        self.events = queue.Queue()
        self.cancel = threading.Event()
        self.running = False
        self.last_dir = None
        self.key = tk.StringVar()
        self.document = tk.StringVar(value=str(asset_dir() / "examples/Architecture_Documentation.md"))
        self.views = tk.StringVar(value=str(asset_dir() / "examples/Architecture_View.md"))
        base = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent
        self.output = tk.StringVar(value=str(base / "generated_runs"))
        self.rounds = tk.IntVar(value=50)
        self.execution = tk.BooleanVar(value=False)
        box = ttk.Frame(root, padding=18)
        box.pack(fill="both", expand=True)
        ttk.Label(box, text="从架构文档生成项目", font=("Microsoft YaHei UI", 18, "bold")).pack(anchor="w")
        ttk.Label(box, text="DeepSeek V4 Pro 官方API · 文件工具循环 · 静态检查与反馈修复").pack(anchor="w", pady=(3, 14))
        form = ttk.Frame(box)
        form.pack(fill="x")
        form.columnconfigure(1, weight=1)
        fields = [("API Key", self.key, None), ("架构文档", self.document, "file"),
                  ("架构视图", self.views, "file"), ("输出目录", self.output, "directory")]
        for i, (label, var, kind) in enumerate(fields):
            ttk.Label(form, text=label, width=12).grid(row=i, column=0, sticky="w", pady=5)
            ttk.Entry(form, textvariable=var, show="*" if i == 0 else "").grid(row=i, column=1, sticky="ew", padx=8)
            if kind:
                ttk.Button(form, text="选择", command=lambda v=var, k=kind: self.browse(v, k)).grid(row=i, column=2)
        row = ttk.Frame(box)
        row.pack(fill="x", pady=8)
        ttk.Label(row, text="最多模型调用轮数").pack(side="left")
        ttk.Spinbox(row, from_=1, to=60, textvariable=self.rounds, width=5).pack(side="left", padx=8)
        ttk.Label(row, text="密钥不保存；开始后会将选中的文档发送至DeepSeek，并产生API费用。").pack(side="left")
        ttk.Checkbutton(box, text="允许安装项目依赖、运行生成测试并反馈修复（会执行生成代码）", variable=self.execution).pack(anchor='w')
        ttk.Label(box, text="任务补充（可留空；若简化技术栈，请明确记录与原设计的差异）").pack(anchor="w")
        self.instructions = tk.Text(box, height=3, wrap="word")
        self.instructions.pack(fill="x", pady=5)
        buttons = ttk.Frame(box)
        buttons.pack(fill="x", pady=8)
        self.start_button = ttk.Button(buttons, text="开始生成", command=self.start)
        self.start_button.pack(side="left")
        ttk.Button(buttons, text="预览结构化输入", command=self.preview).pack(side="left", padx=8)
        self.stop_button = ttk.Button(buttons, text="停止", command=self.stop, state="disabled")
        self.stop_button.pack(side="left")
        ttk.Button(buttons, text="离线流程自检", command=self.demo).pack(side="left", padx=8)
        self.status = tk.StringVar(value="准备就绪。默认示例来自老师作业，可先预览输入或离线自检。")
        ttk.Label(box, textvariable=self.status, wraplength=860).pack(anchor="w", pady=6)
        self.log = ScrolledText(box, wrap="word", height=16, state="disabled")
        self.log.pack(fill="both", expand=True)
        ttk.Label(box, text="勾选后将实际执行生成测试。它以当前用户权限运行，并非隔离环境；运行测试结果会写入报告。", wraplength=860).pack(anchor="w", pady=(8, 0))
        root.protocol("WM_DELETE_WINDOW", self.close)
        root.after(100, self.poll)

    def browse(self, var, kind):
        value = filedialog.askdirectory() if kind == "directory" else filedialog.askopenfilename(filetypes=[("Markdown", "*.md"), ("All files", "*.*")])
        if value:
            var.set(value)

    def inputs(self):
        return preprocess(Path(self.document.get()).read_text(encoding="utf-8-sig"), Path(self.views.get()).read_text(encoding="utf-8-sig"))

    def preview(self):
        try:
            data = self.inputs()
            win = tk.Toplevel(self.root)
            win.title("结构化输入预览（保留原文）")
            text = ScrolledText(win, width=95, height=30)
            text.pack(fill="both", expand=True)
            text.insert("end", json.dumps(data, ensure_ascii=False, indent=2))
            text.configure(state="disabled")
        except Exception as exc:
            messagebox.showerror("无法读取", str(exc))

    def start(self):
        if self.running:
            return
        try:
            data = self.inputs()
            client = DeepSeek(self.key.get())
            rounds = self.rounds.get()
            if not 1 <= rounds <= 60:
                raise ValueError("调用轮数须为1到60")
            if not self.output.get().strip():
                raise ValueError("请选择输出目录")
            instruction = self.instructions.get("1.0", "end").strip()
            output = Path(self.output.get())
            execution = self.execution.get()
        except Exception as exc:
            messagebox.showerror("请检查输入", str(exc))
            return
        self.cancel.clear()
        self.set_busy(True)
        def work():
            try:
                agent = Agent(client, output, lambda s: self.events.put(("log", s)), self.cancel, rounds,
                              execution=execution, node=asset_dir() / 'runtime' / 'node.exe')
                self.events.put(("log", "输出：" + str(agent.run_dir)))
                report = agent.run(data, instruction)
                self.events.put(("done", report))
            except Exception as exc:
                self.events.put(("failure", str(exc)))
        threading.Thread(target=work, daemon=True).start()

    def demo(self):
        if self.running:
            return
        from selfcheck import run_check
        try:
            result = run_check()
            messagebox.showinfo("离线自检", result + "\n这不是DeepSeek生成测试，不消耗API费用。")
        except Exception as exc:
            messagebox.showerror("自检失败", str(exc))

    def set_busy(self, active):
        self.running = active
        self.start_button.configure(state="disabled" if active else "normal")
        self.stop_button.configure(state="normal" if active else "disabled")
        if active:
            self.status.set("正在生成；文件会逐步保存，可随时停止。")

    def stop(self):
        self.cancel.set()
        self.status.set("已请求停止；当前网络请求结束后停止，最长约120秒。")

    def poll(self):
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == "log":
                    self.log.configure(state="normal")
                    self.log.insert("end", value + "\n")
                    self.log.see("end")
                    self.log.configure(state="disabled")
                elif kind == "done":
                    self.set_busy(False)
                    self.last_dir = value["run_directory"]
                    label = {"artifacts_ready": "文件生成完成", "error": "生成遇到错误", "cancelled": "已停止", "limit_reached": "已达到轮数上限"}.get(value['status'], value['status'])
                    self.status.set(f"{label}。测试：{value['runtime_tests']}。产物位置：{self.last_dir}")
                elif kind == "failure":
                    self.set_busy(False)
                    self.status.set("未完成：" + value)
        except queue.Empty:
            pass
        self.root.after(100, self.poll)

    def close(self):
        if self.running:
            self.stop()
            messagebox.showinfo("正在停止", "等待当前请求结束、状态更新后再关闭，以保存报告。")
        else:
            self.root.destroy()


if __name__ == "__main__":
    if "--run-generated-tests" in sys.argv:
        from runner import python_child
        index = sys.argv.index('--run-generated-tests')
        sys.exit(python_child(sys.argv[index+1], sys.argv[index+2]))
    elif "--gui-check" in sys.argv:
        root = tk.Tk()
        root.withdraw()
        app = App(root)
        root.update()
        assert len(app.inputs()["plantuml_blocks"]) == 13
        app.set_busy(True)
        assert str(app.start_button['state']) == "disabled"
        app.set_busy(False)
        root.destroy()
        Path(sys.argv[sys.argv.index("--result") + 1]).write_text("PASS: packaged GUI, sample assets and state changes", encoding="utf-8")
    elif "--self-test" in sys.argv:
        from selfcheck import run_check
        result = run_check()
        if "--result" in sys.argv:
            Path(sys.argv[sys.argv.index("--result") + 1]).write_text(result, encoding="utf-8")
        else:
            print(result)
    else:
        root = tk.Tk()
        App(root)
        root.mainloop()
