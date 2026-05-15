import tkinter as tk
from tkinter import ttk


def voltage_to_delta(voltage, full_scale=2048):
    voltage = max(min(voltage, 1.0), -1.0)
    return round(voltage * full_scale)


def get_quantization_info(linear_delta):
    abs_d = abs(linear_delta)
    sign = 1 if linear_delta >= 0 else -1

    if abs_d < 16:
        step, segment_num, segment_start = 1, 1, 0
    elif abs_d < 32:
        step, segment_num, segment_start = 1, 2, 16
    elif abs_d < 64:
        step, segment_num, segment_start = 2, 3, 32
    elif abs_d < 128:
        step, segment_num, segment_start = 4, 4, 64
    elif abs_d < 256:
        step, segment_num, segment_start = 8, 5, 128
    elif abs_d < 512:
        step, segment_num, segment_start = 16, 6, 256
    elif abs_d < 1024:
        step, segment_num, segment_start = 32, 7, 512
    else:
        step, segment_num, segment_start = 64, 8, 1024

    quant_abs = (abs_d // step) * step
    quant = sign * quant_abs
    inner_level = (abs_d - segment_start) // step

    return step, quant_abs, quant, segment_num, inner_level


def calculate_error(linear_delta):
    abs_d = abs(linear_delta)
    _, quant_abs, _, _, _ = get_quantization_info(linear_delta)
    return abs_d - quant_abs


def encode_pcm(linear_delta):
    _, _, _, segment_num, inner_level = get_quantization_info(linear_delta)

    polarity_code = "1" if linear_delta >= 0 else "0"
    segment_code_map = {
        1: "000",
        2: "001",
        3: "010",
        4: "011",
        5: "100",
        6: "101",
        7: "110",
        8: "111",
    }
    segment_code = segment_code_map[segment_num]
    inner_code = f"{inner_level:04b}"
    full_code = polarity_code + segment_code + inner_code

    return polarity_code, segment_code, inner_code, full_code


def pcm_decode(pcm_code):
    if len(pcm_code) != 8 or not all(c in "01" for c in pcm_code):
        raise ValueError("请输入8位二进制PCM编码（仅0和1）")

    polarity_bit = pcm_code[0]
    segment_code = pcm_code[1:4]
    inner_code = pcm_code[4:8]

    sign = 1 if polarity_bit == "1" else -1
    polarity = "正信号" if sign == 1 else "负信号"

    segment_map = {
        "111": (8, 1024, 64),
        "110": (7, 512, 32),
        "101": (6, 256, 16),
        "100": (5, 128, 8),
        "011": (4, 64, 4),
        "010": (3, 32, 2),
        "001": (2, 16, 1),
        "000": (1, 0, 1),
    }
    segment_num, segment_start, step = segment_map[segment_code]
    inner_level = int(inner_code, 2)

    quant_level_abs = segment_start + inner_level * step
    quant_level = sign * quant_level_abs

    voltage_raw = quant_level / 2048
    if voltage_raw >= 0:
        voltage = int(voltage_raw * 10000 + 0.5) / 10000
    else:
        voltage = -int(abs(voltage_raw) * 10000 + 0.5) / 10000

    return {
        "输入PCM编码": pcm_code,
        "信号极性": polarity,
        "所在段落": f"第{segment_num}段(Z{segment_num})",
        "段内量化级": f"第{inner_level}级",
        "段起始电平": f"{segment_start} Δ",
        "段内步长": f"{step} Δ",
        "还原量化电平": f"{quant_level} Δ",
        "还原采样电压": f"{voltage:.4f} V",
    }


def hamming_encode_4bit(info_code):
    d1, d2, d3, d4 = (int(info_code[0]), int(info_code[1]), int(info_code[2]), int(info_code[3]))
    p1 = d1 ^ d2 ^ d3
    p2 = d1 ^ d2 ^ d4
    p3 = d1 ^ d3 ^ d4
    full_code = f"{d1}{d2}{d3}{d4}{p1}{p2}{p3}"
    return {
        "info": f"D1={d1}, D2={d2}, D3={d3}, D4={d4}",
        "parity": f"P1={p1}, P2={p2}, P3={p3}",
        "full_code": full_code,
        "grouped": f"[{d1} {d2} {d3} {d4} | {p1} {p2} {p3}]",
    }


def hamming_encode_8bit(info_code_8bit):
    if len(info_code_8bit) != 8 or not all(c in "01" for c in info_code_8bit):
        raise ValueError("请输入8位二进制（仅0和1）")

    high_4bit = info_code_8bit[:4]
    low_4bit = info_code_8bit[4:]
    high_result = hamming_encode_4bit(high_4bit)
    low_result = hamming_encode_4bit(low_4bit)

    return {
        "source": info_code_8bit,
        "high": high_result,
        "low": low_result,
        "total": f"{high_result['full_code']}{low_result['full_code']}",
    }


def qpsk_modulate(binary_code):
    if len(binary_code) != 2 or not all(c in "01" for c in binary_code):
        raise ValueError("请输入2位二进制（仅0和1）")

    qpsk_map = {
        "00": {"gray_code": "00", "phase": 45, "i_raw": 1, "q_raw": 1, "constellation": "第一象限"},
        "01": {"gray_code": "01", "phase": 315, "i_raw": 1, "q_raw": -1, "constellation": "第四象限"},
        "10": {"gray_code": "11", "phase": 135, "i_raw": -1, "q_raw": 1, "constellation": "第二象限"},
        "11": {"gray_code": "10", "phase": 225, "i_raw": -1, "q_raw": -1, "constellation": "第三象限"},
    }

    info = qpsk_map[binary_code]
    i_norm = round(info["i_raw"] * 0.707, 3)
    q_norm = round(info["q_raw"] * 0.707, 3)

    return {
        "input": binary_code,
        "gray": info["gray_code"],
        "phase": info["phase"],
        "i_raw": info["i_raw"],
        "q_raw": info["q_raw"],
        "i_norm": i_norm,
        "q_norm": q_norm,
        "constellation": info["constellation"],
    }


def qpsk_demodulate_single(i, q):
    demap_table = {
        (1, 1): {"gray_code": "00", "original_code": "00", "phase": 45, "constellation": "第一象限"},
        (1, -1): {"gray_code": "01", "original_code": "01", "phase": 315, "constellation": "第四象限"},
        (-1, 1): {"gray_code": "11", "original_code": "10", "phase": 135, "constellation": "第二象限"},
        (-1, -1): {"gray_code": "10", "original_code": "11", "phase": 225, "constellation": "第三象限"},
    }
    if (i, q) not in demap_table:
        raise ValueError(f"无效的IQ分量：({i}, {q})，必须是±1的组合")
    return demap_table[(i, q)]


def qpsk_demodulate_batch(iq_data_str):
    iq_parts = iq_data_str.strip().split()
    if len(iq_parts) % 2 != 0:
        raise ValueError("IQ数据长度必须是偶数（每2个为一组：I Q）")

    try:
        iq_values = [int(part) for part in iq_parts]
    except ValueError:
        raise ValueError("输入必须是由空格分隔的数字，且只能是-1或1")

    groups = []
    full_original_stream = ""

    for idx in range(0, len(iq_values), 2):
        i_val = iq_values[idx]
        q_val = iq_values[idx + 1]
        result = qpsk_demodulate_single(i_val, q_val)
        groups.append(
            {
                "组号": idx // 2 + 1,
                "I分量": i_val,
                "Q分量": q_val,
                "格雷码": result["gray_code"],
                "原始二进制码": result["original_code"],
                "相位": result["phase"],
                "星座位置": result["constellation"],
            }
        )
        full_original_stream += result["original_code"]

    return groups, full_original_stream


def qam16_modulate(binary_code):
    if len(binary_code) != 4 or not all(c in "01" for c in binary_code):
        raise ValueError("请输入4位二进制（仅0和1）")

    qam16_map = {
        "0000": {"gray_code": "0000", "i_raw": 1, "q_raw": 1, "i_norm": 0.316, "q_norm": 0.316, "quadrant": "第一象限"},
        "0001": {"gray_code": "0001", "i_raw": 1, "q_raw": 3, "i_norm": 0.316, "q_norm": 0.949, "quadrant": "第一象限"},
        "0010": {"gray_code": "0011", "i_raw": 3, "q_raw": 1, "i_norm": 0.949, "q_norm": 0.316, "quadrant": "第一象限"},
        "0011": {"gray_code": "0010", "i_raw": 3, "q_raw": 3, "i_norm": 0.949, "q_norm": 0.949, "quadrant": "第一象限"},
        "0100": {"gray_code": "0110", "i_raw": 1, "q_raw": -1, "i_norm": 0.316, "q_norm": -0.316, "quadrant": "第四象限"},
        "0101": {"gray_code": "0111", "i_raw": 1, "q_raw": -3, "i_norm": 0.316, "q_norm": -0.949, "quadrant": "第四象限"},
        "0110": {"gray_code": "0101", "i_raw": 3, "q_raw": -1, "i_norm": 0.949, "q_norm": -0.316, "quadrant": "第四象限"},
        "0111": {"gray_code": "0100", "i_raw": 3, "q_raw": -3, "i_norm": 0.949, "q_norm": -0.949, "quadrant": "第四象限"},
        "1000": {"gray_code": "1100", "i_raw": -1, "q_raw": 1, "i_norm": -0.316, "q_norm": 0.316, "quadrant": "第二象限"},
        "1001": {"gray_code": "1101", "i_raw": -1, "q_raw": 3, "i_norm": -0.316, "q_norm": 0.949, "quadrant": "第二象限"},
        "1010": {"gray_code": "1111", "i_raw": -3, "q_raw": 1, "i_norm": -0.949, "q_norm": 0.316, "quadrant": "第二象限"},
        "1011": {"gray_code": "1110", "i_raw": -3, "q_raw": 3, "i_norm": -0.949, "q_norm": 0.949, "quadrant": "第二象限"},
        "1100": {"gray_code": "1010", "i_raw": -1, "q_raw": -1, "i_norm": -0.316, "q_norm": -0.316, "quadrant": "第三象限"},
        "1101": {"gray_code": "1011", "i_raw": -1, "q_raw": -3, "i_norm": -0.316, "q_norm": -0.949, "quadrant": "第三象限"},
        "1110": {"gray_code": "1001", "i_raw": -3, "q_raw": -1, "i_norm": -0.949, "q_norm": -0.316, "quadrant": "第三象限"},
        "1111": {"gray_code": "1000", "i_raw": -3, "q_raw": -3, "i_norm": -0.949, "q_norm": -0.949, "quadrant": "第三象限"},
    }
    info = qam16_map[binary_code]
    return {
        "input": binary_code,
        "gray": info["gray_code"],
        "i_raw": info["i_raw"],
        "q_raw": info["q_raw"],
        "i_norm": info["i_norm"],
        "q_norm": info["q_norm"],
        "quadrant": info["quadrant"],
    }


def qam16_demodulate(i_input, q_input):
    norm_to_raw = {0.316: 1, 0.949: 3, -0.316: -1, -0.949: -3}
    standard_norms = list(norm_to_raw.keys())

    def find_closest(value):
        return min(standard_norms, key=lambda x: abs(x - value))

    try:
        i_norm = float(i_input)
        q_norm = float(q_input)
    except ValueError:
        raise ValueError("请输入有效的数字作为IQ分量")

    i_closest = find_closest(i_norm)
    q_closest = find_closest(q_norm)
    i_raw = norm_to_raw[i_closest]
    q_raw = norm_to_raw[q_closest]

    demap_table = {
        (1, 1): {"gray_code": "0000", "original_code": "0000", "quadrant": "第一象限"},
        (1, 3): {"gray_code": "0001", "original_code": "0001", "quadrant": "第一象限"},
        (3, 1): {"gray_code": "0011", "original_code": "0010", "quadrant": "第一象限"},
        (3, 3): {"gray_code": "0010", "original_code": "0011", "quadrant": "第一象限"},
        (1, -1): {"gray_code": "0110", "original_code": "0100", "quadrant": "第四象限"},
        (1, -3): {"gray_code": "0111", "original_code": "0101", "quadrant": "第四象限"},
        (3, -1): {"gray_code": "0101", "original_code": "0110", "quadrant": "第四象限"},
        (3, -3): {"gray_code": "0100", "original_code": "0111", "quadrant": "第四象限"},
        (-1, 1): {"gray_code": "1100", "original_code": "1000", "quadrant": "第二象限"},
        (-1, 3): {"gray_code": "1101", "original_code": "1001", "quadrant": "第二象限"},
        (-3, 1): {"gray_code": "1111", "original_code": "1010", "quadrant": "第二象限"},
        (-3, 3): {"gray_code": "1110", "original_code": "1011", "quadrant": "第二象限"},
        (-1, -1): {"gray_code": "1010", "original_code": "1100", "quadrant": "第三象限"},
        (-1, -3): {"gray_code": "1011", "original_code": "1101", "quadrant": "第三象限"},
        (-3, -1): {"gray_code": "1001", "original_code": "1110", "quadrant": "第三象限"},
        (-3, -3): {"gray_code": "1000", "original_code": "1111", "quadrant": "第三象限"},
    }
    info = demap_table[(i_raw, q_raw)]
    return {
        "input_iq": f"[{i_norm}, {q_norm}]",
        "closest_iq": f"I: {i_closest}, Q: {q_closest}",
        "raw_iq": f"{i_raw:+d}; {q_raw:+d}",
        "gray": info["gray_code"],
        "original": info["original_code"],
        "quadrant": info["quadrant"],
    }


def hamming_decode(received_code):
    if len(received_code) != 7 or not all(c in "01" for c in received_code):
        raise ValueError("请输入7位二进制汉明码（仅0和1）")

    d1, d2, d3, d4, p1, p2, p3 = [int(x) for x in received_code]

    s1 = d1 ^ d2 ^ d3 ^ p1
    s2 = d1 ^ d2 ^ d4 ^ p2
    s3 = d1 ^ d3 ^ d4 ^ p3

    error_map = {
        (0, 0, 0): "无错误",
        (0, 0, 1): "P3",
        (0, 1, 0): "P2",
        (1, 0, 0): "P1",
        (0, 1, 1): "D4",
        (1, 0, 1): "D3",
        (1, 1, 0): "D2",
        (1, 1, 1): "D1",
    }

    error_pos = error_map[(s1, s2, s3)]
    corrected_bits = [d1, d2, d3, d4, p1, p2, p3]

    if error_pos != "无错误":
        pos_index = {"D1": 0, "D2": 1, "D3": 2, "D4": 3, "P1": 4, "P2": 5, "P3": 6}[error_pos]
        corrected_bits[pos_index] ^= 1

    corrected_code = "".join(str(bit) for bit in corrected_bits)
    original_info = "".join(str(bit) for bit in corrected_bits[:4])

    return {
        "received": received_code,
        "syndrome": f"S1={s1}, S2={s2}, S3={s3}",
        "error_pos": error_pos,
        "corrected": corrected_code,
        "decoded": original_info,
    }


class MiniSignalTool:
    MODES = [
        "PCM编码1",
        "汉明编码1",
        "QPSK调制映射1",
        "QPSK解映射1",
        "16QAM调制映射1",
        "16QAM解映射1",
        "汉明译码1",
        "PCM译码1",
    ]

    HINTS = {
        "PCM编码1": "输入采样电压，例如: 0.625",
        "PCM译码1": "输入8位PCM编码，例如: 11110001",
        "汉明编码1": "输入8位二进制，例如: 10110011",
        "QPSK调制映射1": "输入2位二进制，例如: 10",
        "QPSK解映射1": "注意IQ值要空格分开 例:1 -1",
        "16QAM调制映射1": "输入4位二进制，例如: 0110",
        "16QAM解映射1": "输入归一化IQ，空格分隔，例如: 0.316 -0.949",
        "汉明译码1": "输入7位汉明码，例如: 1011001",
    }

    def __init__(self, root):
        self.root = root
        self.root.title("春子大王の计算器")
        self.normal_geometry = "390x300"
        self.bar_geometry = "1280x62"
        self.transparent_key = "#111111"
        self.root.geometry(self.normal_geometry)
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)
        self.is_bar_mode = False
        self.default_bg = self.root.cget("bg")
        self.nav_fg = "#000000"
        self._drag_offset_x = None
        self._drag_offset_y = None
        self.root.bind("<Escape>", self._on_escape)

        self.main = ttk.Frame(root, padding=8)
        self.main.pack(fill="both", expand=True)

        self.mode_var = tk.StringVar(value=self.MODES[0])
        self.mode_box = ttk.Combobox(
            self.main, textvariable=self.mode_var, values=self.MODES, state="readonly", width=24
        )
        self.mode_box.pack(fill="x")
        self.mode_box.bind("<<ComboboxSelected>>", self._refresh_hint)

        self.hint_var = tk.StringVar(value=self.HINTS[self.MODES[0]])
        self.hint_label = ttk.Label(self.main, textvariable=self.hint_var, foreground="#666")
        self.hint_label.pack(anchor="w", pady=(6, 4))

        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(self.main, textvariable=self.input_var)
        self.input_entry.pack(fill="x")
        self.input_entry.bind("<Return>", lambda _e: self.run())

        self.btn_row = ttk.Frame(self.main)
        self.btn_row.pack(fill="x", pady=6)
        self.run_btn = ttk.Button(self.btn_row, text="执行", command=self.run)
        self.run_btn.pack(side="left", fill="x", expand=True)
        self.switch_btn = ttk.Button(self.btn_row, text="地址栏模式", command=self.enable_bar_mode)
        self.switch_btn.pack(side="left", padx=(6, 0))

        self.output = tk.Text(self.main, height=10, wrap="word")
        self.output.pack(fill="both", expand=True)
        self._set_output("Made By 春子大王 免责:本项目仅仅用于展示春子的代码技术，严禁用于其它用途！！")

        self.nav_var = tk.StringVar(value="在此输入数据")
        self.nav_frame = tk.Frame(self.root, bg=self.transparent_key)

        self.nav_prev_btn = tk.Button(
            self.nav_frame,
            text="<",
            command=self._mode_prev,
            bg=self.transparent_key,
            fg=self.nav_fg,
            activebackground=self.transparent_key,
            activeforeground=self.nav_fg,
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            width=4,
            font=("Segoe UI", 12, "normal"),
            padx=8,
            pady=2,
        )
        self.nav_prev_btn.pack(side="left", padx=(2, 6))

        self.nav_mode_label = tk.Label(
            self.nav_frame,
            textvariable=self.mode_var,
            bg=self.transparent_key,
            fg=self.nav_fg,
            font=("Segoe UI", 12, "normal"),
        )
        self.nav_mode_label.pack(side="left", padx=(0, 6))

        self.nav_next_btn = tk.Button(
            self.nav_frame,
            text=">",
            command=self._mode_next,
            bg=self.transparent_key,
            fg=self.nav_fg,
            activebackground=self.transparent_key,
            activeforeground=self.nav_fg,
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            width=4,
            font=("Segoe UI", 12, "normal"),
            padx=8,
            pady=2,
        )
        self.nav_next_btn.pack(side="left", padx=(0, 8))

        self.nav_entry = tk.Entry(
            self.nav_frame,
            textvariable=self.nav_var,
            bg=self.transparent_key,
            fg=self.nav_fg,
            insertbackground=self.nav_fg,
            relief="flat",
            bd=0,
            highlightthickness=0,
            font=("Segoe UI", 12, "normal"),
        )
        self.nav_entry.pack(side="left", fill="x", expand=True)
        self.nav_entry.bind("<Return>", lambda _e: self.run_bar())

        drag_widgets = [
            self.nav_frame,
            self.nav_mode_label,
            self.nav_prev_btn,
            self.nav_next_btn,
            self.nav_entry,
        ]
        for widget in drag_widgets:
            widget.bind("<Control-ButtonPress-1>", self._start_drag)
            widget.bind("<Control-B1-Motion>", self._on_drag)
            widget.bind("<Control-ButtonRelease-1>", self._stop_drag)

        self.input_entry.focus_set()

    def _refresh_hint(self, _event=None):
        self.hint_var.set(self.HINTS[self.mode_var.get()])

    def _set_output(self, text):
        self.output.delete("1.0", "end")
        self.output.insert("1.0", text)
        self._highlight_fill_lines()

    def _highlight_fill_lines(self):
        self.output.tag_remove("fill_red", "1.0", "end")
        self.output.tag_configure("fill_red", foreground="red")

        line_count = int(self.output.index("end-1c").split(".")[0])
        for line_no in range(1, line_count + 1):
            line_text = self.output.get(f"{line_no}.0", f"{line_no}.end")
            if "(填)" in line_text or "（填）" in line_text:
                self.output.tag_add("fill_red", f"{line_no}.0", f"{line_no}.end")

    def _mode_prev(self):
        idx = self.MODES.index(self.mode_var.get())
        idx = (idx - 1) % len(self.MODES)
        self.mode_var.set(self.MODES[idx])
        self._refresh_hint()

    def _mode_next(self):
        idx = self.MODES.index(self.mode_var.get())
        idx = (idx + 1) % len(self.MODES)
        self.mode_var.set(self.MODES[idx])
        self._refresh_hint()

    def _on_escape(self, _event=None):
        if self.is_bar_mode:
            self.disable_bar_mode()

    def _start_drag(self, event):
        if not self.is_bar_mode:
            return
        self._drag_offset_x = event.x_root - self.root.winfo_x()
        self._drag_offset_y = event.y_root - self.root.winfo_y()

    def _on_drag(self, event):
        if not self.is_bar_mode or self._drag_offset_x is None or self._drag_offset_y is None:
            return
        new_x = event.x_root - self._drag_offset_x
        new_y = event.y_root - self._drag_offset_y
        self.root.geometry(f"+{new_x}+{new_y}")

    def _stop_drag(self, _event=None):
        self._drag_offset_x = None
        self._drag_offset_y = None

    def _calc_text(self, mode, raw):
        if mode == "PCM编码1":
            value = float(raw)
            linear = voltage_to_delta(value)
            step, _, quant, segment_num, inner_level = get_quantization_info(linear)
            error = calculate_error(linear)
            p, s, inner, full = encode_pcm(linear)
            return (
                f"采样电压: {value:.6f} V\n"
                f"转化量化单位(填): {linear}\n"
                f"量化误差(填): {error}\n"
                f"13折线段落(填):{segment_num}\n"
                f"13折线段内(填): {inner_level}\n"
                f"编码输出(填): {full}\n"
                f"段内步长: {step}\n"
                f"量化电平: {quant}\n"
                f"B7/B6-B4/B3-B0: {p} / {s} / {inner}"
            )
        if mode == "PCM译码1":
            result = pcm_decode(raw)
            return (
                f"输入PCM编码: {result['输入PCM编码']}\n"
                f"段起始电平: {result['段起始电平']}\n"
                f"段内步长: {result['段内步长']}\n"
                f"极性(填): {result['信号极性']}\n"
                f"段落（填）: {result['所在段落']}\n"
                f"段内(填): {result['段内量化级']}\n"
                f"还原量化电平(填): {result['还原量化电平']}\n"
                f"还原采样电压(填): {result['还原采样电压']}"
            )
        if mode == "汉明编码1":
            result = hamming_encode_8bit(raw)
            return (
                f"原始8位: {result['source']}\n"
                f"信息位|监督位(上): {result['high']['grouped']} -> {result['high']['full_code']}\n"
                f"信息位|监督位(下): {result['low']['grouped']} -> {result['low']['full_code']}\n"
                f"编码输出(注意不要空格): {result['total']}"
            )
        if mode == "QPSK调制映射1":
            result = qpsk_modulate(raw)
            return (
                f"输入原码: {result['input']}\n"
                f"格雷编码(填): {result['gray']}\n"
                f"IQ映射(填): {result['i_raw']} / {result['q_raw']}\n"
                f"相位: {result['phase']}°\n"
                f"I/Q归一化: {result['i_norm']} / {result['q_norm']}\n"
                f"星座: {result['constellation']}\n"
                f"IQ分组:最前面的I，后面的是Q"
            )
        if mode == "QPSK解映射1":
            groups, full_stream = qpsk_demodulate_batch(raw)
            lines = [f"\n共 {len(groups)} 个符号组"]
            for group in groups:
                lines.append(f"第{group['组号']} 组")
                lines.append(f"  I分量: {group['I分量']}, Q分量: {group['Q分量']}")
                lines.append(f"  原始二进制码: {group['原始二进制码']}")
                lines.append(f"  对应相位: {group['相位']}°")
                lines.append(f"  星座位置: {group['星座位置']}")
            last_gray = groups[-1]["格雷码"] if groups else "无"
            lines.append(f"IQ解映射(填): {last_gray}")
            lines.append(f"格雷译码(填): {full_stream}")
            lines.append("")
            return "\n".join(lines)
        if mode == "16QAM调制映射1":
            result = qam16_modulate(raw)
            return (
                f"输入原码: {result['input']}\n"
                f"格雷编码(填): {result['gray']}\n"
                f"IQ映射(填): {result['i_raw']} / {result['q_raw']}\n"
                f"I归一化(填): {result['i_norm']}\n"
                f"Q归一化(填): {result['q_norm']}\n"
                f"IQ分组(填): [{result['i_norm']}, {result['q_norm']}]\n"
                f"星座象限: {result['quadrant']}"
            )
        if mode == "16QAM解映射1":
            parts = raw.split()
            if len(parts) != 2:
                raise ValueError("请输入两个由空格分隔的IQ值")
            result = qam16_demodulate(parts[0], parts[1])
            return (
                f"输入IQ分组: {result['input_iq']}\n"
                f"识别到标准电平: {result['closest_iq']}\n"
                f"逆映射原始IQ电平: {result['raw_iq']}\n"
                f"IQ解映射(填): {result['gray']}\n"
                f"格雷译码(填): {result['original']}\n"
                f"星座象限: {result['quadrant']}"
            )

        result = hamming_decode(raw)
        return (
            f"接收码: {result['received']}\n"
            f"校正子: {result['syndrome']}\n"
            f"错误位置: {result['error_pos']}\n"
            f"前4位信息位，后3位监督位(填): {result['corrected']}\n"
            f"译码输出中的四位(填): {result['decoded']}"
        )

    def run(self):
        mode = self.mode_var.get()
        raw = self.input_var.get().strip()
        try:
            text = self._calc_text(mode, raw)
        except Exception as exc:
            text = f"输入错误: {exc}"
        self._set_output(text)

    def run_bar(self):
        mode = self.mode_var.get()
        raw = self.nav_var.get().strip()
        try:
            text = self._calc_text(mode, raw)
            one_line = " | ".join(part.strip() for part in text.splitlines() if part.strip())
            self.nav_var.set(one_line)
        except Exception as exc:
            self.nav_var.set(f"输入错误: {exc}")
        self.nav_entry.focus_set()
        self.nav_entry.selection_range(0, "end")

    def enable_bar_mode(self):
        if self.is_bar_mode:
            return
        self.is_bar_mode = True
        self.root.overrideredirect(True)
        self.root.configure(bg=self.transparent_key)
        try:
            self.root.wm_attributes("-transparentcolor", self.transparent_key)
        except tk.TclError:
            pass
        self.root.geometry(self.bar_geometry)

        self.main.pack_forget()

        self.nav_var.set("在此输入数据")
        self.nav_frame.pack(fill="both", expand=True, padx=8, pady=16)
        self.nav_entry.focus_set()
        self.nav_entry.selection_range(0, "end")

    def disable_bar_mode(self):
        if not self.is_bar_mode:
            return
        self.is_bar_mode = False
        self.root.overrideredirect(False)
        try:
            self.root.wm_attributes("-transparentcolor", "")
        except tk.TclError:
            pass
        self.root.configure(bg=self.default_bg)
        self.root.geometry(self.normal_geometry)

        self.nav_frame.pack_forget()
        self.main.pack(fill="both", expand=True)
        self.input_entry.focus_set()


def main():
    root = tk.Tk()
    MiniSignalTool(root)
    root.mainloop()


if __name__ == "__main__":
    main()
