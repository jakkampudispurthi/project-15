#!/usr/bin/env bash
echo "=== Test 1: destructive, no token (expect BLOCK, exit 2) ==="
echo '{"tool_input":{"command":"kubectl delete pvc data-var"}}' | bash approval_gate.sh
echo "exit=$?"
echo ""
echo "=== Test 2: read-only (expect ALLOW, exit 0) ==="
echo '{"tool_input":{"command":"du -x -d1 /var"}}' | bash approval_gate.sh
echo "exit=$?"
echo ""
echo "=== Test 3: destructive, WITH token (expect ALLOW, exit 0) ==="
export HUMAN_APPROVAL_TOKEN=I-APPROVE
echo '{"tool_input":{"command":"kubectl delete pvc data-var"}}' | bash approval_gate.sh
echo "exit=$?"
