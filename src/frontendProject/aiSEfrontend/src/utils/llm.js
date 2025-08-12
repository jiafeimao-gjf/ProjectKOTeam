// 通用流式请求函数，返回最终内容
export async function fetchStreamAnswer(prompt, model, flushAnswer = () => {}, index = 0, isAnswer = true) {
  let buffer = ''
  await new Promise((resolve) => {
    fetch('/api/chat_start', {
      method: 'post',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt: encodeURIComponent(prompt),
        model: encodeURIComponent(model)
      })
    }).then(res => {
      if (!res.ok) throw new Error('接口请求失败')
      return res.text()
    }).then((streamUrl) => {
      const eventSource = new EventSource(streamUrl)
      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          if (event.data === '[DONE]') {
            loading.value = false
            eventSource.close()
            return
          }
          if (data.text) {
            buffer += data.text
            flushAnswer(index, buffer, isAnswer)
          }
        } catch (e) {
          buffer += event.data
        }
      }
      eventSource.onerror = () => {
        eventSource.close()
        resolve()
      }
      eventSource.addEventListener('end', () => {
        eventSource.close()
        resolve()
      })
    })
  })
  return buffer
}

