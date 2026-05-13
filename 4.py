def qpsk_demodulate_single(i, q):
    """
    严格按实验指导实现单个IQ对的解映射
    返回：格雷码, 原始二进制码, 相位, 星座位置
    """
    # 严格按实验指导映射表定义（逆映射）
    demap_table = {
        (1, 1): {
            'gray_code': '00',
            'original_code': '00',
            'phase': 45,
            'constellation': '第一象限'
        },
        (1, -1): {
            'gray_code': '01',
            'original_code': '01',
            'phase': 315,
            'constellation': '第四象限'
        },
        (-1, 1): {
            'gray_code': '11',
            'original_code': '10',
            'phase': 135,
            'constellation': '第二象限'
        },
        (-1, -1): {
            'gray_code': '10',
            'original_code': '11',
            'phase': 225,
            'constellation': '第三象限'
        }
    }
    
    # 验证输入合法性
    if (i, q) not in demap_table:
        raise ValueError(f"无效的IQ分量：({i}, {q})，必须是±1的组合")
    
    return demap_table[(i, q)]

def qpsk_demodulate_batch(iq_data_str):
    """
    批量处理一串IQ数据
    输入格式：用空格分隔的±1序列，如"1 1 -1 1 1 -1 -1 -1"
    """
    # 处理输入字符串
    iq_parts = iq_data_str.strip().split()
    
    # 输入验证
    if len(iq_parts) % 2 != 0:
        raise ValueError("IQ数据长度必须是偶数（每2个为一组：I Q）")
    
    try:
        iq_values = [int(part) for part in iq_parts]
    except ValueError:
        raise ValueError("输入必须是由空格分隔的数字，且只能是-1或1")
    
    # 按I Q分组
    groups = []
    full_original_stream = ""
    
    for i in range(0, len(iq_values), 2):
        i_val = iq_values[i]
        q_val = iq_values[i+1]
        result = qpsk_demodulate_single(i_val, q_val)
        groups.append({
            '组号': i//2 + 1,
            'I分量': i_val,
            'Q分量': q_val,
            '格雷码': result['gray_code'],
            '原始二进制码': result['original_code'],
            '相位': result['phase'],
            '星座位置': result['constellation']
        })
        full_original_stream += result['original_code']
    
    return groups, full_original_stream

# ==================== 交互模式 ====================
if __name__ == "__main__":
    print("=== QPSK解映射与格雷译码工具（严格按实验指导）===")
    print("输入格式：用空格分隔的±1序列，如：1 1 -1 1")
    print("每2个为一组（I Q），输入 q 退出\n")
    
    while True:
        user_input = input("请输入IQ数据序列: ").strip()
        
        if user_input.lower() in ['q', 'quit', 'exit']:
            print("程序已退出。")
            break
            
        try:
            groups, full_stream = qpsk_demodulate_batch(user_input)
            
            print(f"\n共 {len(groups)} 个符号组")
            print("-" * 70)
            
            for group in groups:
                print(f"第 {group['组号']} 组:")
                print(f"  I分量: {group['I分量']}, Q分量: {group['Q分量']}")
                print(f"  IQ解映射: {group['格雷码']}")
                print(f"  原始二进制码: {group['原始二进制码']}")
                print(f"  对应相位: {group['相位']}°")
                print(f"  星座位置: {group['星座位置']}")
                print("-" * 70)
            
            print(f"\n✅ 格雷译码: {full_stream}")
            print("=" * 70)
            print()
            
        except ValueError as e:
            print(f"❌ 输入错误：{e}\n")