#!/usr/bin/env python3
# encoding: utf-8

import json
import threading
import requests
import vim
import os
from .rate_limiter import RateLimiter

END_POINT = "http://open.bigmodel.cn/api/paas/v4/chat/completions"
API_TOKEN = vim.eval("g:codegeex_apikey")
FILE_NAME = vim.eval("expand('%:p')")
# 5 秒内少于 10 次请求
rate_limiter = RateLimiter(9, 5)

def safe_vim_eval(expression):
    try:
        return vim.eval(expression)
    except vim.error:
        return None

def completions_request_async():
    file_path = safe_vim_eval("expand('%:p')")
    prompt = safe_vim_eval("g:copilot_global_prompt")
    suffix = safe_vim_eval("g:copilot_global_suffix")
    lnum = safe_vim_eval("get(g:copilot_global_context,'lnum')")
    col = safe_vim_eval("get(g:copilot_global_context,'col')")
    lang = safe_vim_eval("copilot#lang()")
    # 记录 lnum 和 col，用以判断返回的 snippet 是否还是跟随原有光标位置，决定是否丢弃
    fetch_thread = threading.Thread(target=get_completions, args=(file_path, prompt, suffix, lnum, col, lang))
    # fetch_thread.daemon = True
    fetch_thread.start()
    pass

def log(msg):
    print(msg)

def response_handler(res):
    safe_vim_eval("copilot#loading_stop()")
    vim.eval("copilot#callback('" + res + "')")
    pass

def cache_response_pos(lnum, col):
    vim.eval("copilot#cache_response_pos(" + str(lnum) + "," + str(col) + ")")
    pass

def get_completions(file_path, prompt, suffix, lnum, col, lang):
    # prompt 就是 prefix
    timeout_setting = 13
    url = "https://www.baidu.com"
    post_json = {
        "model": "codegeex-4",
        "extra":{
            "target": {
                "path": FILE_NAME,
                "language": lang,
                "code_prefix": prompt,
                "code_suffix": suffix
            },
            "contexts": []
        }
    }

    headers = {
        "accept": "application/json",
        'Authorization': "Bearer " + API_TOKEN,
        'Content-Type': 'application/json',
        'x-client-type': 'neovim'
    }

    try:
        response = requests.request("POST", END_POINT, data=json.dumps(post_json),
                                    headers=headers, timeout=timeout_setting)
    except requests.exceptions.Timeout as e:
        # vim.command("echom '调用超时'")
        vim.async_call(response_handler, '{timeout}')
        return

    if response.status_code == 429:
        # 次数太频繁被限流
        vim.async_call(response_handler, "{429}")
        return

    result = json.loads(response.text)
    result_str = result["choices"][0]["message"]["content"]
    result_str = result_str.replace("'", "''")
    vim.async_call(cache_response_pos, lnum, col)
    vim.async_call(response_handler, result_str)

def do_complete():
    if rate_limiter.is_allowed():
        completions_request_async()
        safe_vim_eval("copilot#loading_start()")
    else:
        safe_vim_eval("copilot#loading_stop()")
        pass

if __name__ == "__main__":
    completions_request_async()

