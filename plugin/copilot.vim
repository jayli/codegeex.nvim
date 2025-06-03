" finish
if !has('nvim')
  finish
endif

if !has('python3')
  finish
endif

if !exists("g:deepseek_apikey")
  let g:deepseek_apikey = ""
endif

if !exists("g:deepseek_base_url")
  let g:deepseek_base_url = ""
endif

if empty(g:deepseek_base_url)
  let g:deepseek_base_url = "https://api.deepseek.com/beta"
endif

if empty(g:deepseek_apikey)
  finish
endif


let s:plugin_root = fnamemodify(expand('<sfile>:p'), ':h:h')
if &runtimepath =~ 'deepseek-coder.nvim'
else
  exec "set runtimepath+=" . s:plugin_root
endif

call timer_start(10, { -> system('UpdateRemotePlugins')})

let g:copilot_ready = v:true
if has('vim_starting')
  augroup deepseek_copilot
    autocmd!
    autocmd BufReadPost,BufNewFile * call copilot#init()
    autocmd TextChangedI * call copilot#text_changed_i()
    autocmd CursorHoldI * call copilot#cursor_hold_i()
    autocmd InsertLeave * call copilot#insert_leave()
    autocmd CompleteChanged * call copilot#complete_changed()
    autocmd CursorMovedI * call copilot#cursor_moved_i()
  augroup END
else
  call copilot#init()
endif


" vim:ts=2:sw=2:sts=2
