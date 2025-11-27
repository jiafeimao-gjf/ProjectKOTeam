# model: gpt-oss:20b
# prompt: 
go 语言基础语法简述
# answer: 
 thinking:

The user writes: "go 语言基础语法简述" in Chinese, meaning "Briefly describe the basic syntax of Go language". They likely want a concise summary of Go's basic syntax. So answer in Chinese, covering package declaration, imports, main, variables, constants, types, control flow, functions, methods, interfaces, pointers, slices, maps, structs, packages, goroutines, channels? Basic syntax maybe only the fundamental features: package, imports, var, const, functions, if, for, switch, struct, array/slice, map, interface, pointers, packages, modules, comments, etc. Provide code snippets. Should be succinct but covering. Probably not go deep into advanced. Use Chinese.

Let's produce a concise cheat-sheet. Provide sections: 1. 结构 2. 变量 3. 函数 4. 控制流 5. 数组/切片/映射 6. 结构体 7. 接口 8. 并发基本语法: goroutine, channel 9. 包 10. 模块. Provide example code.

Let's answer.

thinking end 

## Go 语言基础语法简述

> **Tip**：下面的示例均可直接粘贴到 `*.go` 文件中，用 `go run` 运行，或加入到模块中 `go build`。

| 主题 | 关键词 / 关键字 | 说明 | 示例 |
|------|----------------|------|------|
| **1. 代码结构** | `package` <br>`import` | 每个文件属于一个包。`import` 用来引用其它包。 | ```go<br>package main<br><br>import "fmt"<br>``` |
| **2. 注释** | `//` <br>`/* … */` | 单行或多行注释。 | `// 单行注释` |
| **3. 变量** | `var` <br>`:=` | 声明变量。`:=` 为短变量声明，自动推导类型。 | ```go<br>var a int = 10<br>b := "hello"<br>``` |
| **4. 常量** | `const` | 编译期不可变。 | ```go<br>const Pi = 3.1415<br>``` |
| **5. 函数** | `func` | 返回值可多个，用逗号分隔。 | ```go<br>func add(x, y int) int { return x + y }\n``` |
| **6. 结构体** | `struct` | 组合数据。 | ```go<br>type Person struct { Name string; Age int }\n``` |
| **7. 数组 / 切片** | `[]T` | 切片更常用，动态长度。 | ```go<br>arr := [3]int{1,2,3}<br>slice := arr[:2] // {1,2}\n``` |
| **8. 映射 (Map)** | `map[Key]Value` | 键值对存储。 | ```go<br>m := map[string]int{"one":1, "two":2}\n``` |
| **9. 接口** | `interface{}` | 只定义方法签名。 | ```go<br>type Speaker interface { Speak() string }\n``` |
| **10. 控制流** | `if`, `for`, `switch`, `range` | `for` 既可以是传统循环，也可作为无限循环。 | ```go<br>for i:=0; i<5; i++ { fmt.Println(i) }\n``` |
| **11. 指针** | `*T` | 引用指针。 | ```go<br>p := &a // p 指向 a 的地址\n``` |
| **12. 并发（goroutine）** | `go` | 轻量级并发单元。 | ```go<br>go fmt.Println("异步打印")\n``` |
| **13. 通道（channel）** | `chan T` | 用于 goroutine 之间通信。 | ```go<br>c := make(chan int)\ngo func(){ c<-1 }()\nfmt.Println(<-c)\n``` |
| **14. 错误处理** | `error` | 常用的返回错误。 | ```go<br>func mayError() (int, error) { return 0, fmt.Errorf("oops") }\n``` |
| **15. 包与模块** | `go mod init` | Go 1.11+ 模块化。 | `go mod init myapp` |

---

### 代码实例：Hello World + 并发计数

```go
package main

import (
    "fmt"
    "time"
)

func main() {
    fmt.Println("Hello, 世界!")

    // 1. 使用 goroutine
    go countdown(5)

    // 2. 主线程睡眠，等待 goroutine 完成
    time.Sleep(6 * time.Second)
}

// countdown 函数演示 channel 通信
func countdown(n int) {
    c := make(chan int)

    // 子 goroutine 负责递减
    go func() {
        for i := n; i > 0; i-- {
            c <- i
            time.Sleep(1 * time.Second)
        }
        close(c)
    }()

    // 主 goroutine 接收
    for val := range c {
        fmt.Println(val)
    }
    fmt.Println("计数结束")
}
```

> **运行**：`go run main.go`

---

### 常见错误提示

| 错误 | 原因 | 解决 |
|------|------|------|
| `cannot use name (type *name) as type name in variable declaration` | 变量名与类型名冲突 | 改名或加前缀 |
| `expected type, found ...` | 语法不完整 | 检查逗号、括号 |
| `unused variable` | 变量未被使用 | 通过 `_` 或删除 |

---

## 小结

- Go 以 **包** 为单位，**变量**、**常量**、**结构体**、**接口** 为核心数据结构。
- **函数**是语言的基本构造块，**多返回值**是 Go 的特色。
- **for** 语句是唯一的循环控制结构；`range` 用于遍历数组、切片、映射、通道。
- **并发** 用 `goroutine` + `channel` 实现，语法简洁且轻量。
- **模块** (`go mod`) 让依赖管理变得简单。

> 以上是 Go 语言的核心语法骨架。掌握后，你可以快速上手更高级的特性（如 `select`、`defer`、`panic/recover` 等）。祝编码愉快 🚀!thinking:


