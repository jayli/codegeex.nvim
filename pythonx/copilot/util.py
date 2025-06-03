#!/usr/bin/env python3
# encoding: utf-8
import json
import threading
import requests
import vim
import os
import time
import asyncio
import httpx
from .rate_limiter import RateLimiter

# https://api-docs.deepseek.com/zh-cn/api/create-completion
END_POINT = vim.eval("g:deepseek_base_url") + "/completions"
API_TOKEN = vim.eval("g:deepseek_apikey")
FILE_NAME = vim.eval("expand('%:p')")
# 5 秒内少于 10 次请求
rate_limiter = RateLimiter(9, 5)
# 判断请求是否正在进行的标志位，如果是 1 则等待返回，如果是 0 则立即终止
http_requesting_flag = 0

def post_cancel():
    global http_requesting_flag
    http_requesting_flag = 0

def post_init():
    global http_requesting_flag
    http_requesting_flag = 1

def safe_vim_eval(expression):
    try:
        return vim.eval(expression)
    except vim.error:
        return None

async def post_request(client, url, payload, timeout):
    try:
        # 发起POST请求
        response = await client.post(url, json=payload, timeout=timeout)
        #print(f"Response status: {response.status_code}")
        #print(f"Response body: {response.text}")
        return {
            "status": "success",
            "status_code": response.status_code,
            "body": response.text
        }
    except asyncio.CancelledError:
        # print("Request was cancelled.")
        return {
            "status": "cancelled"
        }
    except Exception as e:
        # 捕获其他异常，例如超时、网络错误等
        return {
            "status": "error",
            "message": str(e)
        }

async def completions_request_async():
    file_path = safe_vim_eval("expand('%:p')")
    prompt = safe_vim_eval("g:copilot_global_prompt")
    suffix = safe_vim_eval("g:copilot_global_suffix")
    lnum = safe_vim_eval("get(g:copilot_global_context,'lnum')")
    col = safe_vim_eval("get(g:copilot_global_context,'col')")
    lang = safe_vim_eval("copilot#lang()")
    # 记录 lnum 和 col，用以判断返回的 snippet 是否还是跟随原有光标位置，决定是否丢弃
    # fetch_thread = threading.Thread(target=get_completions, args=(file_path, prompt, suffix, lnum, col, lang))
    #fetch_thread = threading.Thread(target=asyncio.run, args=get_completions(file_path, prompt, suffix, lnum, col, lang))
    #fetch_thread.start()
    #asyncio.run(get_completions(file_path, prompt, suffix, lnum, col, lang))
    await get_completions(file_path, prompt, suffix, lnum, col, lang)
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


async def get_completions(file_path, prompt, suffix, lnum, col, lang):
    # prompt 就是 prefix
    timeout_setting = 13
    url = "https://www.baidu.com"
    vim.async_call(print, 'iiiiiiiiiiiiii')

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


    async with httpx.AsyncClient() as client:
        task = asyncio.create_task(post_request(client, END_POINT,
                                                payload=json.dumps(post_json),
                                                timeout=timeout_setting))

        post_init()
        # 模拟等待一段时间后取消任务（可选）
        # await asyncio.sleep(5)
        # if not task.done():
        #     print("Cancelling the request...")
        #     task.cancel()
        while not task.done():
            print("Monitoring: Task is still running...")
            # 判断 task 是否已经被取消了
            await asyncio.sleep(0.3)

        res = await task  # 获取任务结果（不论是正常完成还是被取消）

        if res["status"] == "success":
            result_obj = json.loads(response.body)
            try:
                result_str = result_obj["choices"][0]["text"]
            except KeyError:
                vim.async_call(print, 'response.choices 格式错误')
                return
            result_str = result_str.replace("'", "''")
            vim.async_call(cache_response_pos, lnum, col)
            vim.async_call(response_handler, result_str)
            # print("Request succeeded:")
            # print(f"Status Code: {res['status_code']}")
            # print(f"Response Body: {res['body']}")
        elif res["status"] == "cancelled":
            vim.async_call(response_handler, '{cancelled}')
            return
        elif res["status"] == "error":
            # 包括超时
            vim.async_call(response_handler, '{error}')
            return


    # try:
    #     response = requests.request("POST", END_POINT, data=json.dumps(post_json),
    #                                 headers=headers, timeout=timeout_setting)
    #     response.raise_for_status()
    # except requests.exceptions.HTTPError as err:
    #     vim.async_call(response_handler, '{error}')
    #     return
    # except requests.exceptions.Timeout as e:
    #     # vim.command("echom '调用超时'")
    #     vim.async_call(response_handler, '{timeout}')
    #     return
    # except requests.exceptions.RequestException as err:
    #     vim.async_call(response_handler, '{error}')
    #     return

    # TODO 如果字符串内有"\n"的情况下的处理
    # aaa = "all_list = all_list.concat(content.trim().split('\n'));\n\n"
    # bbb = aaa.replace("'", "''")
    # vim.async_call(cache_response_pos, lnum, col)
    # vim.async_call(response_handler, bbb)
    # return

def do_complete():
    if rate_limiter.is_allowed():
        completions_request_async()
        safe_vim_eval("copilot#loading_start()")
    else:
        safe_vim_eval("copilot#loading_stop()")
        pass

if __name__ == "__main__":
    completions_request_async()

