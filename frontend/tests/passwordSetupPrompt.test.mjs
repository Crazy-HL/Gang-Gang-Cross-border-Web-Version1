import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import path from 'node:path'

const authForm = await readFile(path.resolve('src/components/auth/AuthForm.vue'), 'utf8')
const client = await readFile(path.resolve('src/api/client.ts'), 'utf8')

assert.match(client, /needsPasswordSetup/)
assert.match(client, /setPassword/)
assert.match(client, /\/api\/auth\/password/)

assert.match(authForm, /showPasswordSetup/)
assert.match(authForm, /setupPassword/)
assert.match(authForm, /showSetupPassword/)
assert.match(authForm, /setPassword/)
assert.match(authForm, /设置新密码/)
assert.match(authForm, /:type="showSetupPassword \? 'text' : 'password'"/)
assert.match(authForm, /该手机号已注册/)
assert.match(authForm, /验证码登录后设置密码/)
