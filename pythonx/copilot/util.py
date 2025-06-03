#!/usr/bin/env python3
# encoding: utf-8

import json
import threading
import requests
import vim
import os
import time
from .rate_limiter import RateLimiter

# https://api-docs.deepseek.com/zh-cn/api/create-completion
END_POINT = "https://api.deepseek.com/beta/completions"
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
        "model": "deepseek-coder",
        "request_id": int(time.time()),
        "stream": False,
        "temperature": 0.2,
        "stop":["<|endoftext|>", "<|user|>", "<|assistant|>", "<|observation|>"],
        "prompt": prompt,
        "suffix": suffix,
        "echo":False,
        "max_tokens": 1024
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
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        vim.async_call(response_handler, '{error}')
        return
    except requests.exceptions.Timeout as e:
        # vim.command("echom '调用超时'")
        vim.async_call(response_handler, '{timeout}')
        return
    except requests.exceptions.RequestException as err:
        vim.async_call(response_handler, '{error}')
        return

    # aaa = "all_list = all_list.concat(content.trim().split('\n'));\n\n"
    # bbb = aaa.replace("'", "''")
    # vim.async_call(cache_response_pos, lnum, col)
    # vim.async_call(response_handler, bbb)
    # return

    if response.status_code == 429:
        # 次数太频繁被限流
        vim.async_call(response_handler, "{429}")
        return

    result = json.loads(response.text)
    try:
        result_str = result["choices"][0]["text"]
    except KeyError:
        vim.async_call(print, 'response.choices 格式错误')
        return
    # vim.async_call(print, '-----------------')
    # vim.async_call(print, col)
    # vim.async_call(print, '-----------------')
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

