# prompt: 写一个简单的鸡尾酒排序
# answer: 
 **鸡尾酒排序（Cocktail Shaker Sort）**  
也叫双向冒泡排序，基本思路是：先正向从左往右把最大元素“推”到右端，再反向从右往左把最小元素“推”到左端。这样每一次完整的“往返”都能把最远端的元素放到正确的位置，从而减少一次冒泡循环的范围。

---

## 1. 算法思路

```
1. 设 left = 0, right = n-1
2. while left < right
       # 正向冒泡
       for i from left to right-1
           if a[i] > a[i+1]: swap
       right--            # 右端已确定最大值
       # 反向冒泡
       for i from right down to left+1
           if a[i] < a[i-1]: swap
       left++             # 左端已确定最小值
```

*如果在某一次正向或反向遍历中没有发生任何交换，则说明已经排好序，直接结束。*

---

## 2. 代码实现（Python）

```python
def cocktail_shaker_sort(arr):
    """
    鸡尾酒排序（双向冒泡排序）
    arr: 可变列表，按升序排序
    """
    left = 0
    right = len(arr) - 1
    while left < right:
        swapped = False

        # 正向冒泡，把最大的元素移到 right
        for i in range(left, right):
            if arr[i] > arr[i + 1]:
                arr[i], arr[i + 1] = arr[i + 1], arr[i]
                swapped = True
        right -= 1
        if not swapped:          # 没有交换，已经排好序
            break

        swapped = False
        # 反向冒泡，把最小的元素移到 left
        for i in range(right, left, -1):
            if arr[i] < arr[i - 1]:
                arr[i], arr[i - 1] = arr[i - 1], arr[i]
                swapped = True
        left += 1
        if not swapped:
            break
    return arr

# 示例
if __name__ == "__main__":
    data = [3, 6, 2, 10, 1, 5]
    print("原始:", data)
    sorted_data = cocktail_shaker_sort(data)
    print("排好序:", sorted_data)
```

**输出**

```
原始: [3, 6, 2, 10, 1, 5]
排好序: [1, 2, 3, 5, 6, 10]
```

---

## 3. 复杂度分析

| 复杂度 | 说明 |
|--------|------|
| 最佳情况 | `O(n)`（当数组已排序时，第一次遍历即可判定） |
| 平均/最坏情况 | `O(n^2)`（与标准冒泡排序相当） |
| 空间复杂度 | `O(1)`（原地排序） |

---

## 4. 小技巧

- **提前终止**：在每次正向/反向遍历结束后检查是否有交换，若没有则说明已排好序，直接退出循环，可节省时间。
- **优化方向**：如果需要对大数据集排序，建议使用更高效的算法（如快速排序、堆排序或 Timsort）。鸡尾酒排序仅适合教学或对空间占用极其敏感且对时间要求不高的场景。

---

**总结**：鸡尾酒排序通过双向冒泡，每一轮往返可把最远端的元素放到正确位置，代码简洁、易于理解，是学习冒泡变体的好例子。祝你玩得愉快 🚀!
