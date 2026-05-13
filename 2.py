def hamming_encode_4bit(info_code):
    """
    严格按实验指导实现单块4位→7位汉明码编码
    位序：D1 D2 D3 D4 P1 P2 P3
    监督方程（偶校验）：
    P1 = D1 ⊕ D2 ⊕ D3
    P2 = D1 ⊕ D2 ⊕ D4
    P3 = D1 ⊕ D3 ⊕ D4
    """
    # 提取信息位 D1~D4
    D1 = int(info_code[0])
    D2 = int(info_code[1])
    D3 = int(info_code[2])
    D4 = int(info_code[3])
    
    # 按实验指导公式计算监督位
    P1 = D1 ^ D2 ^ D3
    P2 = D1 ^ D2 ^ D4
    P3 = D1 ^ D3 ^ D4
    
    # 组合完整7位编码
    full_code = f"{D1}{D2}{D3}{D4}{P1}{P2}{P3}"
    
    return {
        "信息位": f"D1={D1}, D2={D2}, D3={D3}, D4={D4}",
        "监督位": f"P1={P1}, P2={P2}, P3={P3}",
        "完整编码": full_code,
        "编码分组": f"[{D1} {D2} {D3} {D4} | {P1} {P2} {P3}]"
    }

def hamming_encode_8bit(info_code_8bit):
    """
    小春子大王开发
    """
    # 输入验证
    if len(info_code_8bit) != 8 or not all(c in '01' for c in info_code_8bit):
        raise ValueError("请输入8位二进制信息码（仅包含0和1）")
    
    # 拆分为高4位和低4位
    high_4bit = info_code_8bit[:4]
    low_4bit = info_code_8bit[4:]
    
    # 分别编码
    high_result = hamming_encode_4bit(high_4bit)
    low_result = hamming_encode_4bit(low_4bit)
    
    return {
        "原始8位信息": info_code_8bit,
        "高4位块": high_result,
        "低4位块": low_result,
        "总编码输出": f"{high_result['完整编码']} {low_result['完整编码']}"
    }

# ==================== 交互模式 ====================
if __name__ == "__main__":
    print("=== (7,4)汉明码编码工具（支持8位输入）===")
    print("说明：(7,4)汉明码每次编码4位信息，8位输入将拆分为两个4位块分别编码")
    print("输入8位二进制信息码（如10110101），输入 q 退出\n")
    
    while True:
        user_input = input("请输入8位信息码: ").strip()
        
        if user_input.lower() in ['q', 'quit', 'exit']:
            print("程序已退出。")
            break
            
        try:
            result = hamming_encode_8bit(user_input)
            
            print(f"\n原始8位信息: {result['原始8位信息']}")
            print("-" * 40)
            print(f"高4位块 (前4位): {user_input[:4]}")
            print(f"  编码分组: {result['高4位块']['编码分组']}")
            print(f"  信息位: {result['高4位块']['信息位']}")
            print(f"  监督位: {result['高4位块']['监督位']}")
            print(f"  7位编码: {result['高4位块']['完整编码']}")
            print("-" * 40)
            print(f"低4位块 (后4位): {user_input[4:]}")
            print(f"  编码分组: {result['低4位块']['编码分组']}")
            print(f"  信息位: {result['低4位块']['信息位']}")
            print(f"  监督位: {result['低4位块']['监督位']}")
            print(f"  7位编码: {result['低4位块']['完整编码']}")
            print("-" * 40)
            print(f"总编码输出: {result['总编码输出']}")
            print("-" * 50)
            print()
            
        except ValueError as e:
            print(f"❌ 输入错误：{e}\n")