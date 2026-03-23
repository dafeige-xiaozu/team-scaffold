---
description: "前端状态管理规范 — 写操作刷新、持久化、防御性编程"
globs: "frontend/**"
---

# 前端状态管理规范

## 写操作后必须刷新关联数据

任何写操作（创建/编辑/删除/标记/推送）完成后，不能只更新当前组件的 state，必须：

1. **刷新当前列表**（重新 fetch）
2. **刷新关联组件**（如流程条、统计卡片、侧边栏状态）
3. **刷新父级摘要**（如有 summary 类接口）

❌ 错误做法：
```typescript
const handleSave = async () => {
  await updateItem(id, data)
  setLocalState(newData)  // 只改了本地 state，其他组件不知道
}
```

✅ 正确做法：
```typescript
const handleSave = async () => {
  await updateItem(id, data)
  await refreshList()      // 刷新列表
  await refreshSummary()   // 刷新关联组件
}
```

## 状态持久化规范

- 禁止只更新前端 state 不落库——刷新页面必须保持状态
- 操作后 F5 刷新页面，状态必须从 API 恢复，不能依赖 localStorage 或内存
- 跨页面跳转后，目标页面必须从 API 重新获取数据，不能假设 state 还在

## 数据取值防御

- 多数据源取值时用 fallback 链：`source1 ?? source2 ?? source3 ?? defaultValue`
- API 返回的字段名可能和前端定义不一致，对接时逐字段确认
- 所有数字显示做 null/NaN 兜底：`value != null ? value.toFixed(1) : '-'`

## WebSocket 回调必须用 useRef

WebSocket onmessage 回调中访问的 state 必须通过 useRef，不能直接用 useState 的值（闭包陷阱）：

❌ 错误：
```typescript
ws.onmessage = () => {
  console.log(count)  // 永远是初始值
}
```

✅ 正确：
```typescript
const countRef = useRef(count)
countRef.current = count
ws.onmessage = () => {
  console.log(countRef.current)  // 最新值
}
```

## React Hooks 规则

- 所有 useState/useEffect/useCallback 必须在组件顶层调用
- 禁止在条件 return 之后放 hooks（会导致 hooks 顺序不一致 → 白屏）

❌ 错误：
```typescript
function Component() {
  if (loading) return <Spinner />  // 提前 return
  const [data, setData] = useState()  // hooks 在条件之后 → 崩溃
}
```

✅ 正确：
```typescript
function Component() {
  const [data, setData] = useState()  // hooks 在最前面
  if (loading) return <Spinner />
}
```
