import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import path from 'node:path'

const authForm = await readFile(path.resolve('src/components/auth/AuthForm.vue'), 'utf8')
const client = await readFile(path.resolve('src/api/client.ts'), 'utf8')

assert.match(client, /getWechatWebLoginUrl/)
assert.match(client, /\/api\/auth\/wechat\/web\/login-url/)
assert.match(client, /loginWithWechatWebCode/)
assert.match(client, /\/api\/auth\/wechat\/web-login/)

assert.match(authForm, /微信扫码登陆/)
assert.match(authForm, /startWechatWebLogin/)
assert.match(authForm, /handleWechatWebCallback/)
assert.match(authForm, /wechat_login_state/)
assert.match(authForm, /sessionStorage/)
