def qam16_demodulate(i_input, q_input):
    """
    严格按实验指导实现16QAM解调
    支持输入归一化IQ分量（±0.316, ±0.949），自动识别最接近的电平
    """
    # 标准归一化电平与原始电平的对应关系
    norm_to_raw = {
        0.316: 1,
        0.949: 3,
        -0.316: -1,
        -0.949: -3
    }
    standard_norms = list(norm_to_raw.keys())
    
    # 找到输入值最接近的标准归一化电平（解决微小误差问题）
    def find_closest(value):
        return min(standard_norms, key=lambda x: abs(x - value))
    
    # 转换输入为浮点数并找到对应原始电平
    try:
        i_norm = float(i_input)
        q_norm = float(q_input)
    except ValueError:
        raise ValueError("请输入有效的数字作为IQ分量")
    
    i_closest = find_closest(i_norm)
    q_closest = find_closest(q_norm)
    
    i_raw = norm_to_raw[i_closest]
    q_raw = norm_to_raw[q_closest]
    
    # ===================== 完全匹配PPT的逆映射表 =====================
    demap_table = {
        (1, 1): {
            'gray_code': '0000',
            'original_code': '0000',
            'quadrant': '第一象限'
        },
        (1, 3): {
            'gray_code': '0001',
            'original_code': '0001',
            'quadrant': '第一象限'
        },
        (3, 1): {
            'gray_code': '0011',
            'original_code': '0010',
            'quadrant': '第一象限'
        },
        (3, 3): {
            'gray_code': '0010',
            'original_code': '0011',
            'quadrant': '第一象限'
        },
        (1, -1): {
            'gray_code': '0110',
            'original_code': '0100',
            'quadrant': '第四象限'
        },
        (1, -3): {
            'gray_code': '0111',
            'original_code': '0101',
            'quadrant': '第四象限'
        },
        (3, -1): {
            'gray_code': '0101',
            'original_code': '0110',
            'quadrant': '第四象限'
        },
        (3, -3): {
            'gray_code': '0100',
            'original_code': '0111',
            'quadrant': '第四象限'
        },
        (-1, 1): {
            'gray_code': '1100',
            'original_code': '1000',
            'quadrant': '第二象限'
        },
        (-1, 3): {
            'gray_code': '1101',
            'original_code': '1001',
            'quadrant': '第二象限'
        },
        (-3, 1): {
            'gray_code': '1111',
            'original_code': '1010',
            'quadrant': '第二象限'
        },
        (-3, 3): {
            'gray_code': '1110',
            'original_code': '1011',
            'quadrant': '第二象限'
        },
        (-1, -1): {
            'gray_code': '1010',
            'original_code': '1100',
            'quadrant': '第三象限'
        },
        (-1, -3): {
            'gray_code': '1011',
            'original_code': '1101',
            'quadrant': '第三象限'
        },
        (-3, -1): {
            'gray_code': '1001',
            'original_code': '1110',
            'quadrant': '第三象限'
        },
        (-3, -3): {
            'gray_code': '1000',
            'original_code': '1111',
            'quadrant': '第三象限'
        }
    }
    
    # 查询逆映射表
    info = demap_table[(i_raw, q_raw)]
    
    return {
        "输入IQ分组": f"[{i_norm}, {q_norm}]",
        "识别到的标准归一化电平": f"I: {i_closest}, Q: {q_closest}",
        "逆映射原始IQ电平": f"{i_raw:+d}; {q_raw:+d}",
        "格雷码": info['gray_code'],
        "✅ 原始4位二进制分组": info['original_code'],
        "所在象限": info['quadrant']
    }

# ==================== 交互模式 ====================
if __name__ == "__main__":
    print("=== 16QAM解调与格雷译码工具（严格按实验指导）===")
    print("输入格式：两个用空格分隔的归一化IQ分量，如：0.316 -0.316")
    print("输入 q 退出\n")
    
    while True:
        user_input = input("请输入IQ分组: ").strip()
        
        if user_input.lower() in ['q', 'quit', 'exit']:
            print("程序已退出。")
            break
        
        # 拆分输入
        parts = user_input.split()
        if len(parts) != 2:
            print("❌ 输入错误！请输入两个用空格分隔的数字\n")
            continue
            
        try:
            result = qam16_demodulate(parts[0], parts[1])
            
            print(f"\n输入IQ分组: {result['输入IQ分组']}")
            print(f"识别到的标准电平: {result['识别到的标准归一化电平']}")
            print(f"逆映射原始IQ电平: {result['逆映射原始IQ电平']}")
            print(f"格雷码: {result['格雷码']}")
            print(f"✅ 原始4位分组: {result['✅ 原始4位二进制分组']}")
            print(f"所在象限: {result['所在象限']}")
            print("-" * 60)
            print()
            
        except ValueError as e:
            print(f"❌ 输入错误：{e}\n")