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

class RateLimiter:
    # limit: 次数, 比如 10
    # duration: 时间间隔，单位秒，比如 5
    def __init__(self, limit, duration):
        self.limit = limit
        self.duration = duration
        self.timestamps = []

    def is_allowed(self):
        current_time = time.time()
        self.timestamps = [t for t in self.timestamps if t > current_time - self.duration]
        if len(self.timestamps) < self.limit:
            self.timestamps.append(current_time)
            return True
        else:
            return False

@neovim.plugin
class MyPlugin:
    def __init__(self, nvim):
        self.nvim = nvim
        self.post_task = None
        self.BASE_URL = nvim.eval("g:copilot_base_url")
        self.END_POINT = self.BASE_URL + "/completions"
        self.API_TOKEN = nvim.eval("g:copilot_apikey")
        self.FILE_NAME = nvim.eval("expand('%:p')")
        self.TIME_OUT = nvim.eval("g:copilot_timeout")
        self.MODEL = nvim.eval("g:copilot_model")
        # deepseek, qwen
        self.LLM = nvim.eval("g:copilot_llm")
        self.reset_post_task()
        # 5 秒内少于 10 次请求
        self.rate_limiter = RateLimiter(9, 5)

    def reset_post_task(self):
        del self.post_task
        self.post_task = asyncio.create_task(asyncio.sleep(0))

    def nvim_call(self, expression):
        try:
            self.nvim.async_call(self.nvim.eval, expression)
        except self.nvim.error:
            return None

    async def post_request(self, client, url, headers, payload, timeout):
        try:
            # 发起POST请求
            # self.log('1' + url + str(headers) + str(payload) + str(timeout))
            response = await client.post(url, headers=headers, json=payload, timeout=timeout)
            # self.log('2' + response.text)
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
        except httpx.TimeoutException:
            return {
                "status": "timeout"
            }
        except Exception as e:
            # 捕获其他异常，网络错误等
            self.log('Error:' + str(e))
            return {
                "status": "error",
                "message": str(e)
            }

    async def response_handler(self, res):
        await self.async_eval("copilot#callback('" + res + "')")
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
        self.nvim.async_call(self.nvim.command,
                             "echom '[PY LOG] " + txt_t.replace("'", "''") + "'")

    async def completions_request_async(self):
        file_path = await self.async_eval("expand('%:p')")
        prompt = await self.async_eval("g:copilot_global_prompt")
        suffix = await self.async_eval("g:copilot_global_suffix")
        lnum = await self.async_eval("get(g:copilot_global_context,'lnum')")
        col = await self.async_eval("get(g:copilot_global_context,'col')")
        lang = await self.async_eval("copilot#lang()")
        await self.get_completions(file_path, prompt, suffix, lnum, col, lang)
        pass

    def get_deepseek_payload(self, prompt, suffix):
        post_json = {
            "model": self.MODEL,
            "request_id": int(time.time()),
            "echo":False,
            "stream": False,
            "temperature": 0.2,
            "top_p":0.1,
            "prompt": prompt,
            "suffix": suffix,
            "max_tokens": 128
        }
        return post_json

    def get_qwen_payload(self, prompt, suffix):
        prompt_esc = prompt # .replace('"', '\\"')
        suffix_esc = suffix # .replace('"', '\\"')
        post_json = {
            "model": self.MODEL,
            "prompt":f"<|fim_prefix|>{prompt_esc}<|fim_suffix|>{suffix_esc}<|fim_middle|>",
            "top_p":0.1
        }
        # "request_id": int(time.time()),
        # "stream": False,
        # "temperature": 0.1,
        # "top_p":0.1,
        return post_json
    
    def get_aone_layload(self, prompt, suffix):
        post_json = {
            "file_path": self.FILE_NAME,
            "gen_length": 0,
            "prompt": prompt,
            "return_nums": 1,
            "suffix": suffix,
            "temperature": 0.1,
            "top_p": 1
        }
        return post_json

    async def get_completions(self, file_path, prompt, suffix, lnum, col, lang):
        # prompt 就是 prefix
        timeout_setting = self.TIME_OUT
        url = "https://www.baidu.com"

        headers = {
            "Accept": "application/json",
            'Authorization': "Bearer " + self.API_TOKEN,
            'Content-Type': 'application/json'
        }

        if self.LLM == "deepseek":
            post_json = self.get_deepseek_payload(prompt, suffix)
        elif self.LLM == "qwen":
            post_json = self.get_qwen_payload(prompt, suffix)
        elif self.LLM == "aone":
            self.END_POINT = self.BASE_URL + "/completion"
            new_header = {
                'X-Plugin-Version': "999.999.999",
                'x-client-type': 'neovim',
                'x-client-version': "0.9.4"
            }
            merged_header = {**headers, **new_header}
            headers = merged_header
            post_json = self.get_aone_layload(prompt, suffix)
        else:
            self.nvim_call("copilot#loading_stop()")
            return

        async with httpx.AsyncClient() as client:
            self.post_task = asyncio.create_task(self.post_request(client, self.END_POINT,
                                                                headers=headers,
                                                                payload=post_json,
                                                                timeout=timeout_setting))

            # 一直等到 post_request 结束，这三种情况会 task.done()
            #   被 cancel 掉
            #   请求正常返回
            #   timeout 后终止
            while not self.post_task.done():
                await asyncio.sleep(0.3)

            res = await self.post_task  # 获取任务结果（不论是正常完成还是被取消）

            try:
                if res["status"] == "timeout":
                    await self.response_handler("{timeout}")
                    self.nvim_call("copilot#loading_stop()")
                    return
                elif res["status"] == "success":
                    try:
                        result_obj = json.loads(res["body"])
                        result_str = result_obj["choices"][0]["text"]
                    except KeyError:
                        self.log('response.choices Format error: ' + res["body"])
                        self.nvim_call("copilot#loading_stop()")
                        return
                    if self.LLM == "qwen":
                        result_str = result_str.lstrip('\n')
                        result_str = result_str.replace("\n", "\\n")
                    result_str = result_str.replace("'", "''")
                    await self.cache_response_pos(lnum, col)
                    await self.response_handler(result_str)
                    self.nvim_call("copilot#loading_stop()")
                elif res["status"] == "cancelled":
                    await self.response_handler("{cancelled}")
                    self.nvim_call("copilot#loading_stop()")
                    return
                elif res["status"] == "error":
                    # 包括超时
                    await self.response_handler("{error}")
                    self.nvim_call("copilot#loading_stop()")
                    return
            except Exception as e:
                self.log(str(e))

    # 入口调用，执行 DoComplete
    @neovim.function("DoCopilotComplete", sync=False)
    def do_complete(self, args):
        if self.rate_limiter.is_allowed():
            self.nvim_call("copilot#loading_start()")
            loop = asyncio.get_event_loop()
            loop.create_task(self.callback_task())
        else:
            self.nvim_call("copilot#loading_stop()")
        pass

    # cancel POST
    @neovim.function("CancelCopilotComplete", sync=True)
    def cancel_complete(self, args):
        if not self.post_task.done():
            self.post_task.cancel()


    async def callback_task(self):
        await self.completions_request_async()

