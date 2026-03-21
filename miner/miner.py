import os
import re
import ast
import time
import json
import signal
import javalang
import requests
import tempfile
import threading
from git import Repo
import redis

STOP_FLAG = threading.Event()

def mine_repositories():
    r = get_redis_client()
    while not STOP_FLAG.is_set():
        try:
            for lang in ['Python', 'Java']:
                repos = fetch_repos(lang, per_page=15, pages=2)
                for repo in repos[:20]:
                    if STOP_FLAG.is_set():
                        break
                    repo_name = repo.get('full_name', '')
                    clone_url = repo.get('clone_url', '')
                    if clone_url:
                        words = process_repo(clone_url)
                        if words:
                            data = {'repo': repo_name,'language': lang,'words': words,'timestamp': time.time()}
                            print(data)
                            r.publish('function_names', json.dumps(data))
            if not STOP_FLAG.is_set():
                time.sleep(60)
        except Exception as e:
            time.sleep(10)

def fetch_repos(language, per_page=30, pages=3):
    repos = []
    for page in range(1, pages + 1):
        try:
            resp = requests.get('https://api.github.com/search/repositories', timeout=30, params={
                'q': f'language:{language} stars:>100',
                'sort': 'stars', 'order': 'desc', 'per_page': per_page, 'page': page
            })
            resp.raise_for_status()
            repos.extend(resp.json().get('items', []))
            time.sleep(1)
        except Exception:
            pass
    return repos

def process_repo(repo_url):
    words = []
    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp()
        Repo.clone_from(repo_url, temp_dir, depth=1, single_branch=True)
        for root, _, files in os.walk(temp_dir):
            for f in files:
                filepath = os.path.join(root, f)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
                        content = file.read()
                    file_words = extract_functions_from_file(filepath, content)
                    words.extend(file_words)
                except Exception:
                    pass
    except Exception as e:
        return []
    finally:
        if temp_dir and os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
    return words

def extract_functions_from_file(filepath, content):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == '.py':
        return extract_python_functions(content)
    elif ext == '.java':
        return extract_java_methods(content)
    return []

def extract_python_functions(content):
    words = []
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                words.extend(extract_words(node.name))
            elif isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if not item.name.startswith('_'):
                            words.extend(extract_words(item.name))
    except Exception:
        pass
    return words

def extract_java_methods(content):
    words = []
    try:
        tree = javalang.parse.parse(content)
        for path, node in tree:
            if isinstance(node, javalang.tree.Method):
                words.extend(extract_words(node.name))
    except Exception:
        pass
    return words

def get_redis_client():
    return redis.Redis(host="localhost", port=6379, decode_responses=True)

def extract_words(name):
    snake = [p.lower() for p in re.split(r'_', name) if p]
    camel = [p.lower() for p in re.split(r'(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])', name) if p]
    return snake if len(snake) > len(camel) else camel

def signal_handler(signum, frame):
    STOP_FLAG.set()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    mine_repositories()
