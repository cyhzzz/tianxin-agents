#!/usr/bin/env bash
# sync-daily-brief.sh — 把「天信每日日报」skill 子树镜像到 cyhzzz/tianxin-daily-brief 并推送
#
# 背景：天信日报 skill 随 tianxin-agents 走，同时镜像发布到独立仓 tianxin-daily-brief
#       （线上发布仓 / 每日产出归档）。改了 skill 后双仓都要更新，本脚本负责后者。
#
# 用法：在 天信本身/运营/天信日报skill/ 目录下执行
#        ./sync-daily-brief.sh
#
# 约定：
#   - 本地 daily-brief 克隆位于 爸爸/tianxin-daily-brief/（脚本自动克隆若不存在）
#   - 只镜像 skill 代码：SKILL.md / references / templates / assets / examples
#   - 绝不碰 daily-brief 仓里的根级游离文件（tianxin-dashboard.html、日报-*.md）
#     与 daily/ 每日产出（那些由日报生成流程另写，避免覆盖某天归档）
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"            # 本 skill 目录
ROOT="$(cd "$SRC/../.." && pwd)"               # 天信本身/
DST="$ROOT/../tianxin-daily-brief"             # 爸爸/tianxin-daily-brief
REMOTE="git@github.com:cyhzzz/tianxin-daily-brief.git"

# 1) 确保本地克隆存在（首次或换机器时自动建）
if [ ! -d "$DST/.git" ]; then
  echo "▸ 克隆 $REMOTE → $DST"
  git clone "$REMOTE" "$DST"
fi

# 2) 镜像 skill 代码（先清后拷，保证与源完全一致）
for item in SKILL.md references templates assets examples; do
  if [ -e "$SRC/$item" ]; then
    rm -rf "$DST/$item"
    cp -r "$SRC/$item" "$DST/$item"
  fi
done

# 3) 提交并推送（仅在确有变更时）
cd "$DST"
if [ -n "$(git status --porcelain)" ]; then
  git add -A
  git commit -q -m "sync: $(date +%F) 天信日报 skill 子树镜像（结构固化 + .tt-item 修复）"
  GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=no" git push origin master
  echo "✓ 已推送到 tianxin-daily-brief ($(date +%F))"
else
  echo "✓ 无变更，跳过推送"
fi
