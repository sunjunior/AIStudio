#!/bin/bash
# AIStudio 前后端集成测试脚本
# 测试后端 API 和前端代理是否正常工作

PASS=0
FAIL=0

pass() { echo "  ✅ $1"; ((PASS++)); }
fail() { echo "  ❌ $1"; ((FAIL++)); }

echo "╔══════════════════════════════════════════╗"
echo "║     AIStudio 集成测试                    ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# -------------------------------------------------
echo "── [1] 后端健康检查 ──"
HEALTH=$(curl -sf http://127.0.0.1:8000/api/health 2>&1)
if echo "$HEALTH" | grep -q '"status":"ok"'; then
  pass "后端运行正常（http://127.0.0.1:8000）"
else
  fail "后端未运行！请先启动：cd AIStudio && python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000"
  echo ""
  echo "❌ 无法继续测试，请先启动后端"
  exit 1
fi

# -------------------------------------------------
echo ""
echo "── [2] 前端服务检查 ──"
FRONTEND=$(curl -sf http://localhost:5173 2>&1 | head -1)
if echo "$FRONTEND" | grep -q "DOCTYPE html"; then
  pass "前端运行正常（http://localhost:5173）"
else
  fail "前端未运行！请先启动：cd AIStudio/frontend && npm run dev"
fi

# -------------------------------------------------
echo ""
echo "── [3] 前端代理测试 ──"
echo "   测试: 通过前端端口 (/api/models) 请求后端"
MODELS=$(curl -sf http://localhost:5173/api/models 2>&1)
if echo "$MODELS" | grep -q '"total"'; then
  TOTAL=$(echo "$MODELS" | python3 -c "import sys,json;print(json.load(sys.stdin)['total'])")
  pass "前端 → 后端代理正常（可通过 http://localhost:5173/api/* 访问后端，返回 $TOTAL 个模型）"
else
  fail "代理未正常工作"
fi

# -------------------------------------------------
echo ""
echo "── [4] 模型 CRUD 测试 ──"

echo "   4a. 创建模型..."
CREATE=$(curl -sf -X POST http://127.0.0.1:8000/api/models \
  -H "Content-Type: application/json" \
  -d '{"name":"e2e-test","source":"local","source_path":"/tmp/e2e","model_type":"llm","description":"集成测试"}' 2>&1)
MODEL_ID=$(echo "$CREATE" | python3 -c "import sys,json;print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "")
if [ -n "$MODEL_ID" ]; then
  pass "创建模型成功 (ID: $MODEL_ID)"
else
  fail "创建模型失败"
fi

echo "   4b. 获取模型详情..."
curl -sf "http://127.0.0.1:8000/api/models/$MODEL_ID" > /dev/null 2>&1 && pass "获取详情成功" || fail "获取详情失败"

echo "   4c. 列出所有模型..."
curl -sf http://127.0.0.1:8000/api/models > /dev/null 2>&1 && pass "列表查询成功" || fail "列表查询失败"

echo "   4d. 删除模型..."
curl -sf -X DELETE "http://127.0.0.1:8000/api/models/$MODEL_ID" > /dev/null 2>&1 && pass "删除模型成功" || fail "删除模型失败"

# -------------------------------------------------
echo ""
echo "── [5] 训练 API 测试 ──"

echo "   5a. 创建模型用于训练..."
M2=$(curl -sf -X POST http://127.0.0.1:8000/api/models \
  -H "Content-Type: application/json" \
  -d '{"name":"train-test","source":"local","source_path":"/tmp/train","model_type":"llm"}' 2>&1)
M2_ID=$(echo "$M2" | python3 -c "import sys,json;print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "")

echo "   5b. 创建训练任务..."
TRAIN=$(curl -sf -X POST http://127.0.0.1:8000/api/training \
  -H "Content-Type: application/json" \
  -d "{\"model_id\":$M2_ID,\"config\":{\"method\":\"lora\",\"learning_rate\":2e-4,\"num_epochs\":1,\"batch_size\":2,\"lora_r\":8,\"lora_alpha\":32,\"max_length\":256,\"dataset_path\":\"\",\"output_name\":\"test-lora\"}}" 2>&1)
TASK_ID=$(echo "$TRAIN" | python3 -c "import sys,json;print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "")
CONFIG_TYPE=$(echo "$TRAIN" | python3 -c "import sys,json;print(type(json.load(sys.stdin)['config']).__name__)" 2>/dev/null || echo "")
if [ -n "$TASK_ID" ]; then
  pass "创建训练任务成功 (ID: $TASK_ID)"
  if [ "$CONFIG_TYPE" = "dict" ]; then
    pass "  config 字段类型正确 (dict)"
  else
    fail "  config 字段类型错误 (应为 dict, 实际为 $CONFIG_TYPE)"
  fi
else
  fail "创建训练任务失败"
fi

echo "   5c. 查询训练日志..."
curl -sf "http://127.0.0.1:8000/api/training/$TASK_ID/logs" > /dev/null 2>&1 && pass "查询日志成功" || fail "查询日志失败"

# -------------------------------------------------
echo ""
echo "── [6] 评估 API 测试 ──"
EVAL=$(curl -sf -X POST http://127.0.0.1:8000/api/evaluation \
  -H "Content-Type: application/json" \
  -d "{\"model_id\":$M2_ID,\"eval_type\":\"perplexity\",\"dataset\":\"\"}" 2>&1)
EVAL_ID=$(echo "$EVAL" | python3 -c "import sys,json;print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "")
if [ -n "$EVAL_ID" ]; then
  pass "创建评估任务成功 (ID: $EVAL_ID)"
else
  fail "创建评估任务失败"
fi

# -------------------------------------------------
echo ""
echo "── [7] 发布 API 测试 ──"
PUB=$(curl -sf -X POST http://127.0.0.1:8000/api/publishing \
  -H "Content-Type: application/json" \
  -d "{\"model_id\":$M2_ID,\"service_type\":\"export\",\"config\":{\"export_path\":\"/tmp/aistudio-export\"}}" 2>&1)
PUB_ID=$(echo "$PUB" | python3 -c "import sys,json;print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "")
CONFIG_TYPE2=$(echo "$PUB" | python3 -c "import sys,json;print(type(json.load(sys.stdin)['config']).__name__)" 2>/dev/null || echo "")
if [ -n "$PUB_ID" ]; then
  pass "创建发布成功 (ID: $PUB_ID)"
  if [ "$CONFIG_TYPE2" = "dict" ]; then
    pass "  config 字段类型正确 (dict)"
  else
    fail "  config 字段类型错误"
  fi
else
  fail "创建发布失败"
fi

# -------------------------------------------------
echo ""
echo "── [8] 清理测试数据 ──"
curl -sf -X DELETE "http://127.0.0.1:8000/api/models/$M2_ID" > /dev/null 2>&1 && pass "清理测试数据成功" || fail "清理失败"

# -------------------------------------------------
echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  测试结果                                ║"
echo "║  通过: $PASS   失败: $FAIL                  ║"
echo "╚══════════════════════════════════════════╝"
echo ""

if [ $FAIL -eq 0 ]; then
  echo "🎉 全部测试通过！前后端集成正常。"
else
  echo "⚠️  $FAIL 个测试失败，请检查输出。"
fi
echo ""
echo "💡 如果前端页面仍不显示功能，请检查浏览器控制台 (F12)："
echo "   1. 确认没有 404/500 的 API 请求"
echo "   2. 确认没有 JavaScript 运行时错误"
echo "   3. 检查浏览器是否禁用了 JavaScript"
echo "   4. 尝试清空浏览器缓存后重新加载 (Cmd+Shift+R)"
