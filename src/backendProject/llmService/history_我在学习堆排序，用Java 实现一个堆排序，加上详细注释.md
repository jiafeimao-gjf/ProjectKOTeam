# prompt: 我在学习堆排序，用Java 实现一个堆排序，加上详细注释
# answer: 
 下面给出一个 **完整、可直接运行** 的 Java 实现版本，并在代码中添加了大量中文注释，帮助你从每一行都能看懂堆排序的思路。  
为了便于理解，示例代码采用 **0‑based 索引** 的数组（Java 原生数组），实现的是 **升序** 排序。  
如果你想得到 **降序**，只需把 `maxHeapify` 换成 `minHeapify`，或者在 `heapSort` 里把 `swap(nums[i], nums[0])` 改成 `swap(nums[i], nums[0])` 并把 `i` 的起始位置改为 `nums.length - 1`。

---

## 1. 代码（Java 17+）

```java
/**
 * 经典堆排序（Max Heap）实现，升序排列。
 * 
 * 主要思路：
 * 1. 先把无序数组构建成一个 Max Heap（大顶堆）；
 * 2. 依次把堆顶（最大值）与数组末尾元素交换，随后把剩余的前 n-1 个元素重新调整为 Max Heap；
 * 3. 重复 2 步，直到堆的规模为 1。
 *
 * 复杂度：
 * - 时间复杂度：O(n log n)（建堆 O(n)，每次提取 O(log n)）
 * - 空间复杂度：O(1)（原地排序）
 *
 * 注意：
 * - 本实现使用 0‑based 索引；若改为 1‑based，父/子节点计算公式会略有不同。
 * - 代码注释使用中文，方便阅读和学习。
 */

public class HeapSort {

    /**
     * 主入口，示例使用
     */
    public static void main(String[] args) {
        int[] arr = { 5, 3, 17, 10, 84, 19, 6, 22, 9 };

        System.out.println("原始数组：");
        printArray(arr);

        heapSort(arr);

        System.out.println("\n堆排序后数组（升序）：");
        printArray(arr);
    }

    /**
     * 打印数组，方便观察排序过程
     */
    private static void printArray(int[] arr) {
        for (int v : arr) {
            System.out.print(v + " ");
        }
        System.out.println();
    }

    /* -------------------------------------------------------------
     * 1. 堆排序入口
     * ------------------------------------------------------------- */
    public static void heapSort(int[] arr) {
        int n = arr.length;

        /* --------------------
         * 1.1 构建 Max Heap
         * -------------------- */
        // 对于 0‑based 数组，最后一个非叶子节点的索引是 (n/2 - 1)
        for (int i = n / 2 - 1; i >= 0; i--) {
            maxHeapify(arr, n, i);
        }

        /* --------------------
         * 1.2 依次取出堆顶元素（最大值），并调整堆
         * -------------------- */
        for (int i = n - 1; i > 0; i--) {
            // 把堆顶元素（arr[0]）与当前最后一个元素交换
            swap(arr, 0, i);

            // 重新把前 i 个元素调整成 Max Heap
            // 注意：此时堆的大小减 1
            maxHeapify(arr, i, 0);
        }
    }

    /* -------------------------------------------------------------
     * 2. 维护 Max Heap 的“堆化”操作
     * ------------------------------------------------------------- */
    /**
     * 让以 index 为根的子树在给定范围 [0, heapSize) 内满足 Max Heap 性质
     *
     * @param arr      需要堆化的数组
     * @param heapSize 当前堆的规模
     * @param index   当前子树的根节点索引
     */
    private static void maxHeapify(int[] arr, int heapSize, int index) {
        int largest = index;           // 当前子树中最大值的索引
        int left = 2 * index + 1;      // 左子节点索引
        int right = 2 * index + 2;     // 右子节点索引

        // 若左子节点存在且大于根节点，则更新 largest
        if (left < heapSize && arr[left] > arr[largest]) {
            largest = left;
        }

        // 同理比较右子节点
        if (right < heapSize && arr[right] > arr[largest]) {
            largest = right;
        }

        // 如果最大值不是根节点，交换并递归继续堆化
        if (largest != index) {
            swap(arr, index, largest);

            // 递归调用，让下层子树继续满足堆性质
            maxHeapify(arr, heapSize, largest);
        }
    }

    /* -------------------------------------------------------------
     * 3. 辅助方法
     * ------------------------------------------------------------- */
    /**
     * 交换数组中的两个元素
     */
    private static void swap(int[] arr, int i, int j) {
        int tmp = arr[i];
        arr[i] = arr[j];
        arr[j] = tmp;
    }
}
```

---

## 2. 代码逐行说明

| 行号（或区块） | 说明 |
|---------------|------|
| `heapSort` 主入口 | 先构建堆，再依次把堆顶与末尾交换。 |
| `for (int i = n / 2 - 1; i >= 0; i--)` | **建堆**：从最后一个非叶子节点往前遍历，调用 `maxHeapify`。因为叶子节点本身就是堆。 |
| `maxHeapify(arr, n, i)` | 维护以 `i` 为根的子树满足 Max Heap。 |
| `for (int i = n - 1; i > 0; i--)` | **排序**：从末尾开始，将堆顶（最大值）放到数组末尾。 |
| `swap(arr, 0, i)` | 把堆顶与 `i` 位置交换。 |
| `maxHeapify(arr, i, 0)` | 重新调整前 `i` 个元素为堆（因为堆顶被交换到末尾）。 |
| `maxHeapify` 递归实现 | 通过比较父节点与左右子节点，决定是否需要交换，并递归向下调整。 |
| `swap` | 简单的交换方法。 |

---

## 3. 进一步的扩展

| 需求 | 如何实现 |
|------|----------|
| **降序排序** | 把 `maxHeapify` 换成 `minHeapify`（比较符号反转），或者在 `heapSort` 里把 `for (int i = n - 1; i > 0; i--)` 改成 `for (int i = 0; i < n - 1; i++)` 并在交换时使用 `swap(arr, i, 0)`。 |
| **自定义比较器** | 用 `Comparator<T>` 或 `Comparable<T>` 处理对象数组；把 `arr[left] > arr[largest]` 换成 `compare(arr[left], arr[largest]) > 0`。 |
| **优化建堆** | 迭代实现 `maxHeapify`（避免递归栈深度）。 |
| **可视化** | 在 `maxHeapify` 和交换前后打印数组，观察堆化过程。 |

---

## 4. 小结

- **堆排序** 是一种 **基于堆** 的 **原地排序**，不需要额外的存储空间。  
- 先构造 **Max Heap**，再把堆顶元素移到数组末尾，剩余元素重新堆化。  
- 代码中 `maxHeapify` 是核心维护堆性质的函数；如果你对递归不熟，可以把它改成循环版本。  

希望这份带有详尽中文注释的实现能帮你更好地理解堆排序的内部工作原理。如果还有疑问，欢迎继续交流！
