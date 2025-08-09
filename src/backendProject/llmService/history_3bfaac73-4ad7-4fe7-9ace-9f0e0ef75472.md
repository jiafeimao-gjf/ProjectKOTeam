# prompt: 用c++写一个代码，针对输入自然数n，输出0-n里面的质数
# answer: 
 下面给出一个最简洁的 **C++** 程序，读取一个自然数 `n`，并把 `0 … n` 之间（含 `n`）的所有质数逐个输出。  
程序采用“试除法”来判断质数，复杂度为 `O(n√n)`，对于普通练习题足够用；如果你想处理非常大的 `n`（比如 `10⁶` 以上），可以把试除法换成 **埃拉托斯特尼筛**，但这里我们保持代码简洁易懂。

```cpp
/*
   程序功能：输入一个自然数 n，输出 0 ~ n 之间的所有质数
   编译方式（g++）: g++ -std=c++17 -O2 -Wall -o primes primes.cpp
   运行方式: ./primes
*/
#include <bits/stdc++.h>
using namespace std;

// 判断 x 是否为质数（只检查 2 ~ sqrt(x)）
bool isPrime(int x) {
    if (x < 2) return false;          // 0、1 不是质数
    if (x == 2) return true;           // 2 是质数
    if (x % 2 == 0) return false;      // 2 以外的偶数不是质数
    int r = static_cast<int>(sqrt(x));
    for (int i = 3; i <= r; i += 2) { // 只需检查奇数即可
        if (x % i == 0) return false;
    }
    return true;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    long long n;
    if (!(cin >> n)) return 0;  // 读取失败直接退出

    if (n < 2) {
        // n 小于 2 时，没有质数可输出
        return 0;
    }

    bool first = true; // 用于控制输出格式（逗号分隔或换行）
    for (long long i = 2; i <= n; ++i) {
        if (isPrime(static_cast<int>(i))) {
            if (!first) cout << ' ';
            cout << i;
            first = false;
        }
    }
    cout << '\n';
    return 0;
}
```

### 说明

1. **输入**  
   程序从标准输入读取一个整数 `n`。  
   - 如果输入为空或非整数，程序直接退出。  
   - `n` 可以是 `int` 甚至更大（`long long`），但 `isPrime` 只对 `int` 进行检查，适合 `n` 在 `2³¹-1` 以内。

2. **输出**  
   - 质数之间用空格分隔，最后换行。  
   - 例如输入 `20`，输出：  
     ```
     2 3 5 7 11 13 17 19
     ```

3. **复杂度**  
   - 对每个 `i` 进行 `O(√i)` 的试除，整体时间复杂度 `O(n√n)`。  
   - 对于 `n ≤ 10⁶` 或 `10⁷` 仍可在毫秒级完成；若 `n` 较大，可考虑使用埃拉托斯特尼筛（`O(n log log n)`）。

4. **可扩展**  
   - 如需按行输出，可将 `cout << ' ';` 换成 `cout << '\n';`。  
   - 若要把输出写入文件，只需改 `cin`/`cout` 为对应文件流。

祝你玩得开心，Happy coding!
