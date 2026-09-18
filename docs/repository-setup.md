# Repository Setup

The release ZIP omits Git internals and build caches. After extracting it, initialize the empty hakcTEL remote and restore the two pinned Meshtastic submodules:

```bash
./scripts/init_repo.sh https://github.com/haKC-ai/hakctel.git
git status
git commit -m "Initial hakcTEL firmware"
git push -u origin main
```

The script stages files but deliberately does not commit or push. This gives you a final review point before changing the remote repository.

GitHub Actions includes the hakcTEL firmware and Cloudflare Pages workflows. The inherited upstream Meshtastic workflows are also present, so review which ones you want enabled in the repository Actions settings.
