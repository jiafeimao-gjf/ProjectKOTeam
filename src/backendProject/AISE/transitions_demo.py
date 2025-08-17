# -*- coding: utf-8 -*-
from transitions import Machine


# 定义 Bug 类
class Bug:
    # 定义所有可能的状态
    states = ['new', 'assigned', 'fixed', 'verified', 'closed']

    def __init__(self, name):
        self.name = name
        # 初始化状态机，将 self (Bug 实例) 与状态和转换关联起来
        # initial='new' 设置初始状态为 'new'
        # 注意：这里直接使用类属性 Bug.states
        self.machine = Machine(model=self, states=Bug.states, initial='new')

        # --- 定义状态转换 (transitions) ---
        # 每个转换是一个字典，包含 'trigger' (触发事件), 'source' (源状态), 'dest' (目标状态)
        # 可以添加 'before' 和 'after' 回调函数，在转换前后执行

        # 从 'new' 状态，可以通过 'assign' 事件转换到 'assigned'
        self.machine.add_transition(trigger='assign', source='new', dest='assigned')

        # 从 'assigned' 状态，可以通过 'fix' 事件转换到 'fixed'
        self.machine.add_transition(trigger='fix', source='assigned', dest='fixed')

        # 从 'fixed' 状态，可以通过 'verify' 事件转换到 'verified'
        self.machine.add_transition(trigger='verify', source='fixed', dest='verified')

        # 从 'verified' 状态，可以通过 'close' 事件转换到 'closed'
        self.machine.add_transition(trigger='close', source='verified', dest='closed')

        # 从 'new' 或 'assigned' 状态，可以通过 'reject' 事件转换到 'closed'
        # source 可以是一个列表，表示多个源状态
        self.machine.add_transition(trigger='reject', source=['new', 'assigned'], dest='closed')

        # --- 定义回调函数 (Callbacks) ---
        # 在状态转换时自动调用

        # 当进入 'assigned' 状态时调用
        self.machine.on_enter_assigned('on_assigned')

        # 当进入 'fixed' 状态时调用
        self.machine.on_enter_fixed('on_fixed')

        # 当进入 'closed' 状态时调用
        self.machine.on_enter_closed('on_closed')

    # --- 回调函数定义 ---
    def on_assigned(self):
        print(f"  -> Bug '{self.name}' has been assigned to a developer.")

    def on_fixed(self):
        print(f"  -> Bug '{self.name}' has been marked as fixed by the developer.")

    def on_closed(self):
        print(f"  -> Bug '{self.name}' has been closed.")


# --- 运行演示 ---

if __name__ == "__main__":
    # 创建一个 Bug 实例
    my_bug = Bug("Login Button Not Working")

    print("--- Bug Lifecycle Demo with transitions library ---")
    print(f"Initial state of bug '{my_bug.name}': {my_bug.state}")
    print("-" * 20)

    # 尝试有效转换
    print("1. Assigning the bug...")
    my_bug.assign()  # 触发 assign 事件
    print(f"   Current state: {my_bug.state}")
    print("-" * 20)

    print("2. Fixing the bug...")
    my_bug.fix()  # 触发 fix 事件
    print(f"   Current state: {my_bug.state}")
    print("-" * 20)

    print("3. Verifying the fix...")
    my_bug.verify()  # 触发 verify 事件
    print(f"   Current state: {my_bug.state}")
    print("-" * 20)

    print("4. Closing the bug...")
    my_bug.close()  # 触发 close 事件
    print(f"   Final state: {my_bug.state}")
    print("-" * 20)

    print("\n--- Demo with Rejection ---")
    # 创建另一个 Bug 实例来演示拒绝
    rejected_bug = Bug("Minor UI Typo")
    print(f"Initial state of bug '{rejected_bug.name}': {rejected_bug.state}")
    print("-" * 20)

    print("1. Rejecting the bug report (as invalid)...")
    rejected_bug.reject()  # 触发 reject 事件，从 'new' 直接到 'closed'
    print(f"   Final state: {rejected_bug.state}")
    print("-" * 20)

    print("\n--- Attempting Invalid Transition ---")
    # 演示无效转换
    another_bug = Bug("Another Bug")
    print(f"Initial state of bug '{another_bug.name}': {another_bug.state}")
    print("Attempting to 'verify' a 'new' bug (invalid transition)...")
    try:
        # 尝试从 'new' 状态直接 'verify'，这是不允许的
        another_bug.verify()
    except AttributeError as e:
        # transitions 库通常通过动态添加方法实现，无效转换会引发 AttributeError
        print(f"   Error: {type(e).__name__} - This transition is not allowed.")
        print(f"   State remains: {another_bug.state}")

    print("-" * 20)
    print("Demo completed.")
