import json
import time
import re
from playwright.sync_api import sync_playwright

# ==================== 配置 ====================
BASE_URL = "http://192.168.66.123/#/Home"
FAST_SLEEP = 0.15


# ==================== 公式推算 ====================
def load_mapping_from_file():
    """从已有映射文件加载数据"""
    try:
        with open("db_to_percent_mapping_v2.json", "r") as f:
            return json.load(f)
    except:
        return None


def find_percent_by_db(db_value, mapping):
    """根据db值查找对应的percent（线性插值）"""
    if not mapping:
        return None

    # 转换为浮点数
    db_float = float(db_value)

    # 找到最接近的两个点
    for i, item in enumerate(mapping):
        current_db = float(item['db'])

        if current_db == db_float:
            return float(item['percent'])

        if current_db > db_float:
            if i == 0:
                return float(mapping[0]['percent'])

            prev_db = float(mapping[i - 1]['db'])
            prev_percent = float(mapping[i - 1]['percent'])
            current_percent = float(item['percent'])

            # 线性插值
            ratio = (db_float - prev_db) / (current_db - prev_db)
            return prev_percent + (current_percent - prev_percent) * ratio

    return float(mapping[-1]['percent'])


def calculate_percent_formula(db_value):
    """
    根据观察到的规律推算percent值（阶梯函数）

    观察规律：
    - 每0.6dB范围内percent值不变
    - 起始点：-80.0dB -> 0%
    - 结束点：-0.0dB -> 100%
    - 总范围：80dB对应100%的百分比

    公式：percent = ((db_value + 80) / 80) * 100
    但实际是阶梯函数，每0.6dB一个阶梯
    """
    # 限制范围
    if db_value <= -80:
        return 0.0
    if db_value >= 0:
        return 100.0

    # 线性公式计算理论值
    theoretical = ((db_value + 80) / 80) * 100

    # 应用阶梯量化（每0.6dB一个阶梯，与实际映射对齐）
    # 从数据观察，实际percent值是理论值的某种阶梯量化
    step_size = 0.6  # dB
    step_count = int((db_value + 80) / step_size)

    # 获取该阶梯对应的percent（通过实际数据拟合）
    # 这是简化版公式，精确值需要从映射表查询
    step_percent = (step_count / (80 / step_size)) * 100

    # 由于实际数据有微调，建议使用查表法
    return theoretical


def analyze_mapping_formula(mapping):
    """分析映射表的规律，给出不同区间的公式"""
    if not mapping or len(mapping) < 10:
        return None

    print("\n" + "=" * 60)
    print("映射表规律分析")
    print("=" * 60)

    # 检测阶梯规律
    last_percent = None
    step_count = 0
    step_info = []

    for item in mapping:
        current_percent = float(item['percent'])
        db = float(item['db'])

        if current_percent != last_percent:
            if last_percent is not None:
                step_info.append({
                    'db_start': prev_db,
                    'db_end': db,
                    'step_db_range': db - prev_db,
                    'percent': last_percent
                })
            last_percent = current_percent
            prev_db = db
            step_count += 1

    print(f"\n📊 总数据点: {len(mapping)}")
    print(f"📈 阶梯数: {step_count}")

    if step_info:
        avg_step = sum(s['step_db_range'] for s in step_info) / len(step_info)
        print(f"📐 平均阶梯宽度: {avg_step:.3f} dB")

        # 找出主要区间
        print("\n🔍 主要区间规律:")
        ranges = [
            (-80, -60, "低音量区"),
            (-60, -40, "较低音量区"),
            (-40, -20, "中音量区"),
            (-20, 0, "高音量区")
        ]

        for start, end, name in ranges:
            subset = [s for s in step_info if start <= s['db_start'] < end]
            if subset:
                avg_width = sum(s['step_db_range'] for s in subset) / len(subset)
                print(f"  {name} ({start}~{end}dB): 平均阶梯宽度 {avg_width:.3f}dB, 共{len(subset)}个阶梯")

    print("\n💡 推荐使用查表法，精确公式复杂（非线性+阶梯量化）")
    return step_info


# ==================== 扫描器 ====================
def db_to_percent_lookup(db_value, mapping):
    """查表法获取percent（精确）"""
    if not mapping:
        return None

    db_float = float(db_value)

    # 二分查找
    left, right = 0, len(mapping) - 1

    while left <= right:
        mid = (left + right) // 2
        current_db = float(mapping[mid]['db'])

        if current_db == db_float:
            return float(mapping[mid]['percent'])
        elif current_db < db_float:
            left = mid + 1
        else:
            right = mid - 1

    # 没找到精确值，进行插值
    if left >= len(mapping):
        return float(mapping[-1]['percent'])
    if right < 0:
        return float(mapping[0]['percent'])

    left_db = float(mapping[right]['db'])
    right_db = float(mapping[left]['db'])
    left_percent = float(mapping[right]['percent'])
    right_percent = float(mapping[left]['percent'])

    # 线性插值
    ratio = (db_float - left_db) / (right_db - left_db)
    return left_percent + (right_percent - left_percent) * ratio


def run_fast_scanner():
    """运行快速扫描器"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        print(f"🚀 正在连接并初始化极速扫描...")
        page.goto(BASE_URL)

        # 定位选择器
        card_xpath = "//div[contains(@class, 'Card-module_Card')][descendant::span[text()='OUTPUT 1']]"
        page.wait_for_selector(card_xpath)

        display_selector = f"{card_xpath}//div[contains(@class, 'ScaleSteper-module_display-message')]"
        handle_selector = f"{card_xpath}//div[contains(@class, 'ant-slider-handle')]"
        input_selector = "input.ant-input-number-input"

        results = []
        # 准备分贝点列表（-80.0 到 0.0，步进0.1）
        db_points = [round(x * 0.1, 1) for x in range(-800, 1)]

        start_time = time.time()

        for db in db_points:
            db_str = f"{db:.1f}"
            try:
                # 快速触发输入
                page.click(display_selector, force=True)
                page.fill(input_selector, db_str)
                page.keyboard.press("Enter")

                # 等待UI渲染
                time.sleep(FAST_SLEEP)

                # 获取滑块位置
                style = page.get_attribute(handle_selector, "style")
                match = re.search(r"left:\s*([\d\.]+)%", style)

                if match:
                    percent_value = float(match.group(1))
                    results.append({
                        "db": db_str,
                        "percent": str(round(percent_value, 6))
                    })

                    if len(results) % 50 == 0:
                        print(f"已完成: {db_str} dB ({len(results)}/801)")

            except Exception as e:
                print(f"⚠️ 误差 at {db_str}: {e}")
                page.keyboard.press("Escape")

        # 写入文件
        with open("db_to_percent_mapping_v2.json", "w") as f:
            json.dump(results, f, indent=4)

        end_time = time.time()
        print(f"\n✨ 扫描结束！总耗时: {int(end_time - start_time)} 秒")
        browser.close()

        return results


def test_formula_accuracy(mapping):
    """测试公式精度"""
    if not mapping:
        return

    print("\n" + "=" * 60)
    print("公式精度测试（与映射表对比）")
    print("=" * 60)

    test_points = [-80, -75, -70, -65, -60, -55, -50, -45, -40,
                   -35, -30, -25, -20, -15, -10, -5, 0]

    errors = []
    for db in test_points:
        actual = find_percent_by_db(db, mapping)
        formula = calculate_percent_formula(db)

        if actual is not None:
            error = abs(actual - formula)
            errors.append(error)
            print(f"dB={db:5.1f} | 实际:{actual:7.3f}% | 公式:{formula:7.3f}% | 误差:{error:6.3f}%")

    if errors:
        print(f"\n📊 平均误差: {sum(errors) / len(errors):.3f}%")
        print(f"📊 最大误差: {max(errors):.3f}%")
        print("\n💡 注: 由于实际映射是非线性的阶梯函数，简单线性公式会有误差")
        print("   建议使用 db_to_percent_lookup() 查表法获得精确值")


# ==================== 主程序 ====================
if __name__ == "__main__":
    import sys

    # 检查是否已有映射文件
    existing_mapping = load_mapping_from_file()

    if existing_mapping:
        print(f"✅ 找到现有映射文件，共 {len(existing_mapping)} 条记录")

        # 分析规律
        analyze_mapping_formula(existing_mapping)

        # 测试精度
        test_formula_accuracy(existing_mapping)

        # 提供使用示例
        print("\n" + "=" * 60)
        print("使用示例")
        print("=" * 60)
        print("\n# 精确查表法（推荐）")
        print("percent = db_to_percent_lookup(-45.3, mapping)")
        print(f"示例: dB=-45.3 -> {db_to_percent_lookup(-45.3, existing_mapping):.3f}%")

        print("\n# 线性插值法")
        print("percent = find_percent_by_db(-45.3, mapping)")
        print(f"示例: dB=-45.3 -> {find_percent_by_db(-45.3, existing_mapping):.3f}%")

        # 询问是否重新扫描
        response = input("\n🔍 是否重新扫描？(y/N): ")
        if response.lower() != 'y':
            sys.exit(0)

    # 运行扫描
    new_mapping = run_fast_scanner()

    # 分析新数据
    if new_mapping:
        analyze_mapping_formula(new_mapping)
        test_formula_accuracy(new_mapping)