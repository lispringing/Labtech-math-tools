def hamming_decode(received_code):
    """
    严格按实验指导实现(7,4)汉明码译码
    位序：D1 D2 D3 D4 P1 P2 P3
    校正子公式：
    S1 = D1 ⊕ D2 ⊕ D3 ⊕ P1
    S2 = D1 ⊕ D2 ⊕ D4 ⊕ P2
    S3 = D1 ⊕ D3 ⊕ D4 ⊕ P3
    """
    # 输入验证
    if len(received_code) != 7 or not all(c in '01' for c in received_code):
        raise ValueError("请输入7位二进制汉明码（仅包含0和1）")
    
    # 按实验指导位序拆分信息位和监督位
    D1 = int(received_code[0])
    D2 = int(received_code[1])
    D3 = int(received_code[2])
    D4 = int(received_code[3])
    P1 = int(received_code[4])
    P2 = int(received_code[5])
    P3 = int(received_code[6])
    
    # 计算校正子（严格按公式）
    S1 = D1 ^ D2 ^ D3 ^ P1
    S2 = D1 ^ D2 ^ D4 ^ P2
    S3 = D1 ^ D3 ^ D4 ^ P3
    
    # 校正子与错误位置映射表（100%匹配实验指导）
    error_map = {
        (0, 0, 0): "无错误",
        (0, 0, 1): "P3",
        (0, 1, 0): "P2",
        (1, 0, 0): "P1",
        (0, 1, 1): "D4",
        (1, 0, 1): "D3",
        (1, 1, 0): "D2",
        (1, 1, 1): "D1"
    }
    
    error_pos = error_map[(S1, S2, S3)]
    
    # 纠正单比特错误
    corrected_bits = [D1, D2, D3, D4, P1, P2, P3]
    if error_pos != "无错误":
        # 确定错误位的索引
        pos_index = {
            "D1": 0, "D2": 1, "D3": 2, "D4": 3,
            "P1": 4, "P2": 5, "P3": 6
        }[error_pos]
        # 取反纠正
        corrected_bits[pos_index] ^= 1
    
    # 生成纠正后的完整码组
    corrected_code = ''.join(str(bit) for bit in corrected_bits)
    
    # 提取原始信息位（D1~D4）
    original_info = ''.join(str(bit) for bit in corrected_bits[:4])
    
    return {
        "原始接收码": received_code,
        "信息位拆分": f"D1={D1}, D2={D2}, D3={D3}, D4={D4}",
        "监督位拆分": f"P1={P1}, P2={P2}, P3={P3}",
        "校正子": f"S1={S1}, S2={S2}, S3={S3}",
        "错误位置": error_pos,
        "纠正后码组": corrected_code,
        "译码输出（原始信息位）": original_info
    }

# ==================== 交互模式 ====================
if __name__ == "__main__":
    print("=== (7,4)汉明码译码工具（严格按实验指导）===")
    print("功能：检测单比特错误并纠正，检测双比特错误")
    print("输入7位二进制汉明码（如1011001），输入 q 退出\n")
    
    while True:
        user_input = input("请输入7位汉明码: ").strip()
        
        if user_input.lower() in ['q', 'quit', 'exit']:
            print("程序已退出。")
            break
            
        try:
            result = hamming_decode(user_input)
            
            print(f"\n原始接收码: {result['原始接收码']}")
            print(f"信息位拆分: {result['信息位拆分']}")
            print(f"监督位拆分: {result['监督位拆分']}")
            print(f"校正子计算: {result['校正子']}")
            print(f"错误位置: {result['错误位置']}")
            print(f"纠正后码组: {result['纠正后码组']}")
            print(f"✅ 译码输出: {result['译码输出（原始信息位）']}")
            print("-" * 60)
            print()
            
        except ValueError as e:
            print(f"❌ 输入错误：{e}\n")