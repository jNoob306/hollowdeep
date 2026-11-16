#!/usr/bin/env python3
"""Upload the playable game to the Hugging Face Space.

Sends index.html, README.md, the character models and the credits file. Nothing else
in the repository goes to the Space, and tokens never do.

  python3 tools/upload_space.py                 # to jNoob306/hollowdeep
  python3 tools/upload_space.py "what changed"  # with a commit message

Needs `pip install huggingface_hub` and a token with write access to the Space, in
HF_TOKEN or .env. In a Claude Code cloud session the token is injected by the network
proxy, so a placeholder is sent.
"""
import os, re, shutil, sys, tempfile
from huggingface_hub import HfApi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPACE = 'jNoob306/hollowdeep'


def token():
    tok = os.environ.get('HF_TOKEN', '')
    path = os.path.join(ROOT, '.env')
    if not tok and os.path.exists(path):
        for line in open(path, encoding='utf-8'):
            m = re.match(r'\s*HF_TOKEN\s*=\s*(.*)', line)
            if m:
                tok = m.group(1).strip().strip('"\'')
    return tok or 'hf_proxy_injected_placeholder'


def main():
    message = sys.argv[1] if len(sys.argv) > 1 else 'Update Hollowdeep'
    with tempfile.TemporaryDirectory() as stage:
        os.makedirs(os.path.join(stage, 'assets'))
        for name in ('index.html', 'README.md'):
            shutil.copy(os.path.join(ROOT, name), stage)
        for name in sorted(os.listdir(os.path.join(ROOT, 'assets'))):
            if name.endswith('.glb') or name == 'CREDITS.md':
                shutil.copy(os.path.join(ROOT, 'assets', name), os.path.join(stage, 'assets'))
        result = HfApi(token=token()).upload_folder(folder_path=stage, repo_id=SPACE, repo_type='space',
                                                    commit_message=message)
    print('uploaded:', result)


if __name__ == '__main__':
    main()
