#!/usr/bin/env python3
# encoding: utf-8
import json
import threading
import requests
import neovim
import os
import time
import asyncio
import httpx
# from .rate_limiter import RateLimiter

#global_task = 0

@neovim.plugin
class MyPlugin:
    def __init__(self, nvim):
        self.nvim = nvim
        self.END_POINT = nvim.eval("g:deepseek_base_url") + "/completions"
        self.API_TOKEN = nvim.eval("g:deepseek_apikey")
        self.FILE_NAME = nvim.eval("expand('%:p')")
        self.nvim.command('echom "hello from DoItPython ' + self.API_TOKEN + '"')

    def safe_vim_eval(self, expression):
        try:
            return self.nvim.eval(expression)
        except self.nvim.error:
            return None


    async def post_request(self, client, url, headers, payload, timeout):
        try:
            # 发起POST请求
            response = await client.post(url, headers=headers, json=payload, timeout=timeout)
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

    async def response_handler(self, res):
        await self.async_eval("copilot#loading_stop()")
        await self.async_eval("copilot#callback('" + res + "')")
        # self.safe_vim_eval("copilot#loading_stop()")
        # self.nvim.eval("copilot#callback('" + res + "')")
        pass

    async def cache_response_pos(self, lnum, col):
        await self.async_eval("copilot#cache_response_pos(" + str(lnum) + "," + str(col) + ")")
        pass

    async def async_eval(self, expr):
        future = asyncio.get_event_loop().create_future()
        def callback():
            try:
                result = self.nvim.eval(expr)
                future.set_result(result)
            except Exception as e:
                future.set_exception(e)

        self.nvim.async_call(callback)
        return await future
    
    def log(self, astr):
        txt_t = str(astr)
        self.nvim.async_call(self.nvim.command, "echom '" + txt_t.replace("'", "''") + "'")

    async def completions_request_async(self):
        self.nvim.async_call(self.nvim.command, "echom 'Hello'")
        file_path = await self.async_eval("expand('%:p')")
        prompt = await self.async_eval("g:copilot_global_prompt")
        suffix = await self.async_eval("g:copilot_global_suffix")
        lnum = await self.async_eval("get(g:copilot_global_context,'lnum')")
        col = await self.async_eval("get(g:copilot_global_context,'col')")
        lang = await self.async_eval("copilot#lang()")
        # 记录 lnum 和 col，用以判断返回的 snippet 是否还是跟随原有光标位置，决定是否丢弃
        # fetch_thread = threading.Thread(target=get_completions, args=(file_path, prompt, suffix, lnum, col, lang))
        #fetch_thread = threading.Thread(target=asyncio.run, args=get_completions(file_path, prompt, suffix, lnum, col, lang))
        #fetch_thread.start()
        #asyncio.run(get_completions(file_path, prompt, suffix, lnum, col, lang))
        await self.get_completions(file_path, prompt, suffix, lnum, col, lang)
        pass

    async def get_completions(self, file_path, prompt, suffix, lnum, col, lang):
        # global global_task
        self.nvim.async_call(self.nvim.command, 'echom "iiiiiiiiiiiiii"')
        # prompt 就是 prefix
        timeout_setting = 10
        url = "https://www.baidu.com"

        post_json = {
            "model": "deepseek-coder",
            "request_id": int(time.time()),
            "stream": False,
            "temperature": 0.2,
            "top_p":0.1,
            "prompt": prompt,
            "suffix": suffix,
            "echo":False,
            "max_tokens": 1024
        }
        self.log(prompt)
        self.log(suffix)
        self.log(self.API_TOKEN)

        headers = {
            "accept": "application/json",
            'Authorization': "Bearer " + self.API_TOKEN,
            'Content-Type': 'application/json',
            'x-client-type': 'neovim'
        }


        self.log(3333)
        async with httpx.AsyncClient() as client:
            global_task = asyncio.create_task(self.post_request(client, self.END_POINT,
                                                                headers=headers,
                                                                payload=json.dumps(post_json),
                                                                timeout=timeout_setting))
            self.log(234)
            # post_init()
            # 模拟等待一段时间后取消任务（可选）
            # await asyncio.sleep(5)
            # if not task.done():
            #     print("Cancelling the request...")
            #     task.cancel()
            while not global_task.done():
                await asyncio.sleep(0.3)

            self.log(3444)

            res = await global_task  # 获取任务结果（不论是正常完成还是被取消）

            self.log("<<<<<<<<<<<<<<<<<<" + res["status"])

            if res["status"] == "success":
                self.log(res["body"] + ">>>")
                try:
                    result_obj = json.loads(res["body"])
                    result_str = result_obj["choices"][0]["text"]
                except KeyError:
                    self.log('response.choices 格式错误: ' + res["body"])
                    return
                result_str = result_str.replace("'", "''")
                self.log(345678)
                await self.cache_response_pos(lnum, col)
                await self.response_handler(result_str)
                # print("Request succeeded:")
                # print(f"Status Code: {res['status_code']}")
                # print(f"Response Body: {res['body']}")
            elif res["status"] == "cancelled":
                await self.response_handler('{cancelled}')
                return
            elif res["status"] == "error":
                # 包括超时
                await self.response_handler('{error}')
                return

    # 入口调用
    @neovim.function("DoCopilotComplete", sync=False)
    def do_complete(self, args):
        loop = asyncio.get_event_loop()
        loop.create_task(self.callback_task())
        self.nvim.async_call(self.nvim.eval, 'copilot#loading_start()')

    async def callback_task(self):
        await self.completions_request_async()








