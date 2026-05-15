def qpsk_modulate(binary_code):
    """
    严格按实验指导实现QPSK调制
    流程：2位原码 → 格雷编码 → IQ映射 → 归一化 → 星座定位
    """
    # 输入验证
    if len(binary_code) != 2 or not all(c in '01' for c in binary_code):
        raise ValueError("请输入2位二进制原码（仅包含0和1）")
    
    # 严格按实验指导映射表定义
    qpsk_map = {
        '00': {
            'gray_code': '00',
            'phase': 45,
            'i_raw': 1,
            'q_raw': 1,
            'constellation': '第一象限'
        },
        '01': {
            'gray_code': '01',
            'phase': 315,
            'i_raw': 1,
            'q_raw': -1,
            'constellation': '第四象限'
        },
        '10': {
            'gray_code': '11',
            'phase': 135,
            'i_raw': -1,
            'q_raw': 1,
            'constellation': '第二象限'
        },
        '11': {
            'gray_code': '10',
            'phase': 225,
            'i_raw': -1,
            'q_raw': -1,
            'constellation': '第三象限'
        }
    }
    
    # 查询映射表
    info = qpsk_map[binary_code]
    
    # 归一化处理（×0.707，实验指导标准值）
    i_norm = round(info['i_raw'] * 0.707, 3)
    q_norm = round(info['q_raw'] * 0.707, 3)
    
    return {
        "输入原码": binary_code,
        "格雷编码": info['gray_code'],
        "调制相位": f"{info['phase']}°",
        "原始I分量": info['i_raw'],
        "原始Q分量": info['q_raw'],
        "归一化I分量": i_norm,
        "归一化Q分量": q_norm,
        "星座位置": info['constellation'],
        "IQ分组": f"[{i_norm}, {q_norm}]"
    }

# ==================== 交互模式 ====================
if __name__ == "__main__":
    print("=== QPSK调制计算工具（严格按实验指导）===")
    print("输入2位二进制原码（如00、10），输入 q 退出\n")
    
    while True:
        user_input = input("请输入2位二进制原码: ").strip()
        
        if user_input.lower() in ['q', 'quit', 'exit']:
            print("程序已退出。")
            break
            
        try:
            result = qpsk_modulate(user_input)
            
            print(f"\n输入原码   : {result['输入原码']}")
            print(f"格雷编码   : {result['格雷编码']}")
            print(f"调制相位   : {result['调制相位']}")
            print(f"原始I分量  : {result['原始I分量']}")
            print(f"原始Q分量  : {result['原始Q分量']}")
            print(f"归一化I分量: {result['归一化I分量']}")
            print(f"归一化Q分量: {result['归一化Q分量']}")
            print(f"IQ分组     : {result['IQ分组']}")
            print(f"星座位置   : {result['星座位置']}")
            print("-" * 50)
            print()
            
        except ValueError as e:
            print(f"❌ 输入错误：{e}\n")