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
#   - 本地 daily-brief 克隆与仓库同级（../tianxin-daily-brief/，脚本自动克隆若不存在）
#   - 只镜像 skill 代码：SKILL.md / references / templates / assets / examples
#   - 绝不碰 daily-brief 仓里的根级游离文件（tianxin-dashboard.html、日报-*.md）
#     与 daily/ 每日产出（那些由日报生成流程另写，避免覆盖某天归档）
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"            # 本 skill 目录
ROOT="$(cd "$SRC/../.." && pwd)"               # 天信本身/
DST="$ROOT/../tianxin-daily-brief"             # 与仓库同级
REMOTE="git@github.com:cyhzzz/tianxin-daily-brief.git"

# 0) 前置守卫：镜像的必须是「已提交的 skill 内容」，不是主仓工作区快照。
#    被镜像范围内（SKILL.md / references / templates / assets / examples）存在
#    未提交/未跟踪改动时直接拒绝——否则改动会绕过 PR 审查被顺带写进镜像仓。
#    范围只查被镜像的五项（与下方镜像清单一致）：daily/ 产出在主仓被 gitignore、
#    仓库根级文件不在镜像范围，都不卡同步；本脚本自身不参与镜像，也不卡。
cd "$ROOT"
MIRROR_DIRTY="$(git status --porcelain -- "$SRC/SKILL.md" "$SRC/references" "$SRC/templates" "$SRC/assets" "$SRC/examples")"
if [ -n "$MIRROR_DIRTY" ]; then
  echo "[ABORT] uncommitted changes found under mirrored paths:"
  echo "$MIRROR_DIRTY"
  echo "        Commit them (PR + merge) first, then re-run sync. Nothing was copied."
  exit 1
fi

# 1) 确保本地克隆存在（首次或换机器时自动建）
if [ ! -d "$DST/.git" ]; then
  echo "[clone] $REMOTE -> $DST"
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
#    注意：rm -rf + cp -r 重写文件会刷新 mtime，git status --porcelain 因 stat
#    变脏报假阳性 M；先 add -A 刷新 index，再以 git diff --cached --quiet 为准
#    （内容相同则无 staged 变更，跳过提交），否则空提交会触发 set -e 退出 1。
cd "$DST"
git add -A
if ! git diff --cached --quiet; then
  git commit -q -m "sync: $(date +%F) 天信日报 skill 子树镜像（结构固化 + .tt-item 修复）"
  GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=no" git push origin master
  echo "[OK] pushed to tianxin-daily-brief ($(date +%F))"
else
  echo "[OK] no changes, skip push"
fi
