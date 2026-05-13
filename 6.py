def pcm_decode(pcm_code):
    """
    严格按实验指导实现A律13折线8位PCM译码
    修正：使用标准四舍五入（非银行家舍入）保留4位小数
    """
    # 输入验证
    if len(pcm_code) != 8 or not all(c in '01' for c in pcm_code):
        raise ValueError("请输入8位二进制PCM编码（仅包含0和1）")
    
    # 1. 拆分编码各部分
    polarity_bit = pcm_code[0]       # B7 极性码
    segment_code = pcm_code[1:4]     # B6-B4 段落码
    inner_code = pcm_code[4:8]       # B3-B0 段内码
    
    # 2. 极性判断
    sign = 1 if polarity_bit == '1' else -1
    polarity = "正信号" if sign == 1 else "负信号"
    
    # 3. 段落码逆映射
    segment_map = {
        '111': (8, 1024, 64),
        '110': (7, 512, 32),
        '101': (6, 256, 16),
        '100': (5, 128, 8),
        '011': (4, 64, 4),
        '010': (3, 32, 2),
        '001': (2, 16, 1),
        '000': (1, 0, 1)
    }
    
    segment_num, segment_start, step = segment_map[segment_code]
    
    # 4. 段内码转量化级序号
    inner_level = int(inner_code, 2)
    
    # 5. 计算量化电平
    quant_level_abs = segment_start + inner_level * step
    quant_level = sign * quant_level_abs
    
    # 6. 标准四舍五入保留4位小数（解决银行家舍入问题）
    voltage_raw = quant_level / 2048
    voltage = int(voltage_raw * 10000 + 0.5) / 10000  # 标准四舍五入算法
    
    return {
        "输入PCM编码": pcm_code,
        "极性": polarity,
        "段落序号": f"第{segment_num}段 (Z{segment_num})",
        "段内量化级": f"第{inner_level}级",
        "段起始电平": f"{segment_start} Δ",
        "段内步长": f"{step} Δ",
        "还原量化电平": f"{quant_level} Δ",
        "还原采样电压": f"{voltage:.4f} V"
    }

# ==================== 交互模式 ====================
if __name__ == "__main__":
    print("=== A律13折线 PCM 译码工具（标准四舍五入版）===")
    print("输入8位二进制PCM编码（如11110001），输入 q 退出\n")
    
    while True:
        user_input = input("请输入8位PCM编码: ").strip()
        
        if user_input.lower() in ['q', 'quit', 'exit']:
            print("程序已退出。")
            break
            
        try:
            result = pcm_decode(user_input)
            
            print(f"\n输入PCM编码: {result['输入PCM编码']}")
            print(f"信号极性: {result['极性']}")
            print(f"所在段落: {result['段落序号']}")
            print(f"段内量化级: {result['段内量化级']}")
            print(f"段起始电平: {result['段起始电平']}")
            print(f"段内步长: {result['段内步长']}")
            print(f"还原量化电平: {result['还原量化电平']}")
            print(f"✅ 还原采样电压: {result['还原采样电压']}")
            print("-" * 60)
            print()
            
        except ValueError as e:
            print(f"❌ 输入错误：{e}\n")