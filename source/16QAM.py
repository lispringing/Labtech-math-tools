def qam16_modulate(binary_code):
    """
    严格按实验指导实现16QAM调制
    映射表100%匹配PPT中的所有参数
    """
    # 输入验证
    if len(binary_code) != 4 or not all(c in '01' for c in binary_code):
        raise ValueError("请输入4位二进制数据（仅包含0和1）")
    
    # ===================== 完全匹配PPT的16QAM映射表 =====================
    qam16_map = {
        '0000': {
            'gray_code': '0000',
            'iq_raw': '+1; +1',
            'i_raw': 1,
            'q_raw': 1,
            'i_norm': 0.316,
            'q_norm': 0.316,
            'quadrant': '第一象限'
        },
        '0001': {
            'gray_code': '0001',
            'iq_raw': '+1; +3',
            'i_raw': 1,
            'q_raw': 3,
            'i_norm': 0.316,
            'q_norm': 0.949,
            'quadrant': '第一象限'
        },
        '0010': {
            'gray_code': '0011',
            'iq_raw': '+3; +1',
            'i_raw': 3,
            'q_raw': 1,
            'i_norm': 0.949,
            'q_norm': 0.316,
            'quadrant': '第一象限'
        },
        '0011': {
            'gray_code': '0010',
            'iq_raw': '+3; +3',
            'i_raw': 3,
            'q_raw': 3,
            'i_norm': 0.949,
            'q_norm': 0.949,
            'quadrant': '第一象限'
        },
        '0100': {
            'gray_code': '0110',
            'iq_raw': '+1; -1',
            'i_raw': 1,
            'q_raw': -1,
            'i_norm': 0.316,
            'q_norm': -0.316,
            'quadrant': '第四象限'
        },
        '0101': {
            'gray_code': '0111',
            'iq_raw': '+1; -3',
            'i_raw': 1,
            'q_raw': -3,
            'i_norm': 0.316,
            'q_norm': -0.949,
            'quadrant': '第四象限'
        },
        '0110': {
            'gray_code': '0101',
            'iq_raw': '+3; -1',
            'i_raw': 3,
            'q_raw': -1,
            'i_norm': 0.949,
            'q_norm': -0.316,
            'quadrant': '第四象限'
        },
        '0111': {
            'gray_code': '0100',
            'iq_raw': '+3; -3',
            'i_raw': 3,
            'q_raw': -3,
            'i_norm': 0.949,
            'q_norm': -0.949,
            'quadrant': '第四象限'
        },
        '1000': {
            'gray_code': '1100',
            'iq_raw': '-1; +1',
            'i_raw': -1,
            'q_raw': 1,
            'i_norm': -0.316,
            'q_norm': 0.316,
            'quadrant': '第二象限'
        },
        '1001': {
            'gray_code': '1101',
            'iq_raw': '-1; +3',
            'i_raw': -1,
            'q_raw': 3,
            'i_norm': -0.316,
            'q_norm': 0.949,
            'quadrant': '第二象限'
        },
        '1010': {
            'gray_code': '1111',
            'iq_raw': '-3; +1',
            'i_raw': -3,
            'q_raw': 1,
            'i_norm': -0.949,
            'q_norm': 0.316,
            'quadrant': '第二象限'
        },
        '1011': {
            'gray_code': '1110',
            'iq_raw': '-3; +3',
            'i_raw': -3,
            'q_raw': 3,
            'i_norm': -0.949,
            'q_norm': 0.949,
            'quadrant': '第二象限'
        },
        '1100': {
            'gray_code': '1010',
            'iq_raw': '-1; -1',
            'i_raw': -1,
            'q_raw': -1,
            'i_norm': -0.316,
            'q_norm': -0.316,
            'quadrant': '第三象限'
        },
        '1101': {
            'gray_code': '1011',
            'iq_raw': '-1; -3',
            'i_raw': -1,
            'q_raw': -3,
            'i_norm': -0.316,
            'q_norm': -0.949,
            'quadrant': '第三象限'
        },
        '1110': {
            'gray_code': '1001',
            'iq_raw': '-3; -1',
            'i_raw': -3,
            'q_raw': -1,
            'i_norm': -0.949,
            'q_norm': -0.316,
            'quadrant': '第三象限'
        },
        '1111': {
            'gray_code': '1000',
            'iq_raw': '-3; -3',
            'i_raw': -3,
            'q_raw': -3,
            'i_norm': -0.949,
            'q_norm': -0.949,
            'quadrant': '第三象限'
        }
    }
    
    # 查询映射表
    info = qam16_map[binary_code]
    
    return {
        "原始4位分组": binary_code,
        "格雷编码": info['gray_code'],
        "IQ映射电平": info['iq_raw'],
        "归一化I分量": info['i_norm'],
        "归一化Q分量": info['q_norm'],
        "归一化IQ分组": f"[{info['i_norm']}, {info['q_norm']}]",
        "所在象限": info['quadrant']
    }

# ==================== 交互模式 ====================
if __name__ == "__main__":
    print("=== 16QAM调制计算工具（严格按实验指导映射表）===")
    print("输入4位二进制数据（如0110），输入 q 退出\n")
    
    while True:
        user_input = input("请输入4位二进制数据: ").strip()
        
        if user_input.lower() in ['q', 'quit', 'exit']:
            print("程序已退出。")
            break
            
        try:
            result = qam16_modulate(user_input)
            
            print(f"\n原始4位分组: {result['原始4位分组']}")
            print(f"格雷编码: {result['格雷编码']}")
            print(f"IQ映射电平: {result['IQ映射电平']}")
            print(f"归一化I分量: {result['归一化I分量']}")
            print(f"归一化Q分量: {result['归一化Q分量']}")
            print(f"归一化IQ分组: {result['归一化IQ分组']}")
            print(f"所在象限: {result['所在象限']}")
            print("-" * 50)
            print()
            
        except ValueError as e:
            print(f"❌ 输入错误：{e}\n")